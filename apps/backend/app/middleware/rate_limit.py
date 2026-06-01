"""
Rate Limiting Middleware for Kisaan Saathi API
================================================
Implements a sliding-window rate limiter using Redis (when available)
with an in-memory fallback for development / offline mode.

Limits:
  - /auth/login    : 10 req / 60 s  per IP  (brute-force protection)
  - /pest/detect   : 20 req / 60 s  per IP  (image upload, expensive)
  - /* (global)    : 200 req / 60 s per IP  (general API protection)

Headers added to every response:
  X-RateLimit-Limit     – max requests allowed in the window
  X-RateLimit-Remaining – requests left in this window
  X-RateLimit-Reset     – Unix timestamp when the window resets
"""

from __future__ import annotations

import os
import time
import collections
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


# ---------------------------------------------------------------------------
# Route-specific limits  (path_prefix → (max_requests, window_seconds))
# ---------------------------------------------------------------------------
ROUTE_LIMITS: dict[str, tuple[int, int]] = {
    "/auth/login":   (10,  60),   # 10 logins/min — brute-force guard
    "/auth/refresh": (20,  60),   # 20 refresh/min
    "/pest/detect":  (20,  60),   # 20 image uploads/min — costly inference
}
DEFAULT_LIMIT = (200, 60)         # 200 req/min for everything else


# ---------------------------------------------------------------------------
# In-memory store  (fallback when Redis is unavailable)
# ---------------------------------------------------------------------------
# Structure: { "ip:path_prefix": deque([timestamp, ...]) }
_in_memory_store: dict[str, collections.deque] = collections.defaultdict(
    lambda: collections.deque()
)


def _get_limit_for_path(path: str) -> tuple[int, int]:
    """Return (max_requests, window_seconds) for the given request path."""
    for prefix, limit in ROUTE_LIMITS.items():
        if path.startswith(prefix):
            return limit
    return DEFAULT_LIMIT


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window rate limiter.

    Uses Redis sorted sets when REDIS_URL is configured and reachable,
    falling back transparently to an in-process deque store so the app
    always starts — even without a Redis instance (dev / offline mode).
    """

    def __init__(self, app, redis_url: Optional[str] = None):
        super().__init__(app)
        self._redis = None
        self._redis_ok = False

        redis_url = redis_url or os.getenv("REDIS_URL", "")
        if redis_url:
            try:
                import redis as _redis_lib
                client = _redis_lib.from_url(redis_url, socket_connect_timeout=1)
                client.ping()
                self._redis = client
                self._redis_ok = True
            except Exception:
                # Redis not available — silently use in-memory fallback
                self._redis_ok = False

    # ------------------------------------------------------------------
    # Core sliding-window check
    # ------------------------------------------------------------------

    def _check_redis(self, key: str, max_req: int, window: int) -> tuple[bool, int, int, int]:
        """
        Sliding-window check via Redis sorted set.
        Returns (allowed, remaining, limit, reset_ts).
        """
        now = time.time()
        window_start = now - window
        pipe = self._redis.pipeline()
        pipe.zremrangebyscore(key, "-inf", window_start)   # drop old entries
        pipe.zadd(key, {str(now): now})                    # add current request
        pipe.zcard(key)                                    # count in window
        pipe.expire(key, window + 1)
        _, _, count, _ = pipe.execute()

        allowed = count <= max_req
        remaining = max(0, max_req - count)
        reset_ts = int(now) + window
        return allowed, remaining, max_req, reset_ts

    def _check_memory(self, key: str, max_req: int, window: int) -> tuple[bool, int, int, int]:
        """
        Sliding-window check using in-process deque.
        Returns (allowed, remaining, limit, reset_ts).
        """
        now = time.time()
        window_start = now - window
        dq = _in_memory_store[key]

        # Remove expired timestamps
        while dq and dq[0] < window_start:
            dq.popleft()

        count = len(dq)
        allowed = count < max_req
        if allowed:
            dq.append(now)
            count += 1

        remaining = max(0, max_req - count)
        reset_ts = int(now) + window
        return allowed, remaining, max_req, reset_ts

    # ------------------------------------------------------------------
    # Middleware dispatch
    # ------------------------------------------------------------------

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate-limiting for docs / health endpoints
        path = request.url.path
        if path in ("/docs", "/redoc", "/openapi.json", "/health", "/"):
            return await call_next(request)

        # Identify client by real IP (respects X-Forwarded-For from proxies)
        client_ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown")
        )

        max_req, window = _get_limit_for_path(path)
        # Bucket key: ip + route prefix for specific limits, ip only for global
        bucket = f"rl:{client_ip}:{path.split('/')[1]}"  # e.g. rl:1.2.3.4:auth

        # Choose backend
        if self._redis_ok:
            try:
                allowed, remaining, limit, reset_ts = self._check_redis(
                    bucket, max_req, window
                )
            except Exception:
                # Redis went down mid-flight — fall back to memory
                allowed, remaining, limit, reset_ts = self._check_memory(
                    bucket, max_req, window
                )
        else:
            allowed, remaining, limit, reset_ts = self._check_memory(
                bucket, max_req, window
            )

        # Rate-limit headers (RFC 6585 + common convention)
        rl_headers = {
            "X-RateLimit-Limit":     str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset":     str(reset_ts),
        }

        if not allowed:
            retry_after = str(window)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        f"Rate limit exceeded. Maximum {limit} requests per "
                        f"{window} seconds. Please try again shortly."
                    ),
                    "detail_pa": (
                        f"\u0a30\u0a47\u0a1f \u0a38\u0a40\u0a2e\u0a3e \u0a9f\u0a41\u0a71\u0a1f \u0a17\u0a08\u0964 "
                        f"\u0a39\u0a30 {window} \u0a38\u0a15\u0a3f\u0a70\u0a1f \u0a35\u0a3f\u0a71\u0a1a "
                        f"\u0a35\u0a71\u0a27\u0a4b\u0a02 {limit} \u0a2c\u0a47\u0a28\u0a24\u0a40\u0a06\u0a02 "
                        "\u0a28\u0a39\u0a40\u0a02 \u0a15\u0a40\u0a24\u0a40\u0a06\u0a02 \u0a1c\u0a3e \u0a38\u0a15\u0a26\u0a40\u0a06\u0a02\u0964"
                    ),
                    "retry_after_seconds": window,
                },
                headers={**rl_headers, "Retry-After": retry_after},
            )

        response = await call_next(request)

        # Inject rate-limit headers into successful responses
        for header, value in rl_headers.items():
            response.headers[header] = value

        return response
