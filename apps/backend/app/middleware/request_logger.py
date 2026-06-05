"""
Request Logging Middleware for Kisaan Saathi API
=================================================
Logs every incoming HTTP request and its response status/time.

Log format (structured JSON-lines):
  {
    "ts":      "2025-11-15T10:30:00.123Z",   # ISO-8601 UTC timestamp
    "method":  "POST",
    "path":    "/crop/recommend",
    "status":  200,
    "ms":      42,                            # response time in milliseconds
    "ip":      "1.2.3.4",
    "ua":      "KisaanSaathiApp/2.0",
    "req_id":  "f47ac10b-58cc-4372-a567"     # unique per-request UUID prefix
  }

Sensitive paths (/auth/login, /auth/refresh) have their payloads
suppressed — only the method/path/status/ms are logged.

Usage:
  app.add_middleware(RequestLoggingMiddleware)
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# ---------------------------------------------------------------------------
# Logger setup — writes to stdout; configure handlers in production as needed
# ---------------------------------------------------------------------------
logger = logging.getLogger("kisaan.access")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))  # raw JSON lines
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Paths whose response bodies should never be echoed in logs
_SENSITIVE_PATHS = {"/auth/login", "/auth/refresh", "/auth/profile"}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Structured access-log middleware.

    Adds ``X-Request-ID`` header to every response so mobile clients and
    support teams can correlate logs with specific API calls.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate a short request ID (first 12 chars of a UUID4)
        req_id = str(uuid.uuid4())[:12]

        # Resolve real client IP (proxy-aware)
        client_ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown")
        )

        t_start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - t_start) * 1000)

        path = request.url.path
        is_sensitive = any(path.startswith(s) for s in _SENSITIVE_PATHS)

        log_entry = {
            "ts":     time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "req_id": req_id,
            "method": request.method,
            "path":   path if not is_sensitive else _mask_path(path),
            "status": response.status_code,
            "ms":     elapsed_ms,
            "ip":     client_ip,
            "ua":     request.headers.get("User-Agent", "")[:120],
        }

        # Log level: ERROR for 5xx, WARNING for 4xx, INFO for the rest
        if response.status_code >= 500:
            logger.error(json.dumps(log_entry, ensure_ascii=False))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_entry, ensure_ascii=False))
        else:
            logger.info(json.dumps(log_entry, ensure_ascii=False))

        # Inject request ID header so clients can reference it in bug reports
        response.headers["X-Request-ID"] = req_id
        return response


def _mask_path(path: str) -> str:
    """Replace sensitive path segments with a placeholder."""
    return path.split("?")[0] + "?[redacted]"
