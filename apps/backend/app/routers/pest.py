from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import base64
import io

router = APIRouter()

# Disease database with treatments
DISEASE_TREATMENTS = {
    "wheat_brown_rust": {
        "name": "Wheat Brown Rust",
        "name_hi": "गेहूं का भूरा रतुआ",
        "name_pa": "ਕਣਕ ਦਾ ਭੂਰਾ ਰਤੂਆ",
        "treatment": "Spray Propiconazole 25% EC @ 0.1% or Tebuconazole 250 EC @ 0.1%. Apply in morning.",
        "treatment_hi": "प्रोपिकोनाज़ोल 25% EC @ 0.1% छिड़काव करें। सुबह लगाएं।",
        "treatment_pa": "ਪ੍ਰੋਪੀਕੋਨਾਜ਼ੋਲ 25% EC @ 0.1% ਸਪਰੇਅ ਕਰੋ।",
        "severity": "high",
        "prevention": "Use resistant varieties PBW-723, HD-3086. Avoid excess nitrogen.",
    },
    "rice_brown_spot": {
        "name": "Rice Brown Spot",
        "name_hi": "चावल का भूरा धब्बा",
        "name_pa": "ਚੌਲ ਦਾ ਭੂਰਾ ਧੱਬਾ",
        "treatment": "Spray Mancozeb 75 WP @ 2.5 g/L. Ensure proper drainage.",
        "treatment_hi": "मैनकोज़ेब 75 WP @ 2.5 ग्राम/लीटर छिड़काव करें।",
        "treatment_pa": "ਮੈਨਕੋਜ਼ੇਬ 75 WP @ 2.5 g/L ਸਪਰੇਅ ਕਰੋ।",
        "severity": "medium",
        "prevention": "Balanced potassium fertilization. Avoid water stress.",
    },
    "maize_leaf_blight": {
        "name": "Maize Northern Leaf Blight",
        "name_hi": "मक्का का पत्ती झुलसा",
        "name_pa": "ਮੱਕੀ ਦਾ ਪੱਤਾ ਝੁਲਸਣਾ",
        "treatment": "Spray Mancozeb 75 WP + Carbendazim 50 WP @ 2 g/L. Improve air circulation.",
        "treatment_hi": "मैनकोज़ेब + कार्बेन्डाज़िम @ 2 ग्राम/लीटर छिड़काव करें।",
        "treatment_pa": "ਮੈਨਕੋਜ਼ੇਬ + ਕਾਰਬੇਂਡਾਜ਼ਿਮ @ 2 g/L ਸਪਰੇਅ ਕਰੋ।",
        "severity": "medium",
        "prevention": "Use resistant hybrids. Crop rotation with non-host crops.",
    },
    "cotton_bollworm": {
        "name": "Cotton Pink Bollworm",
        "name_hi": "कपास का गुलाबी सुंडी",
        "name_pa": "ਕਪਾਹ ਦਾ ਗੁਲਾਬੀ ਸੁੰਡੀ",
        "treatment": "Spray Chlorpyriphos 20 EC @ 2 mL/L or Emamectin benzoate 5 SG @ 0.4 g/L.",
        "treatment_hi": "क्लोरपाइरिफोस 20 EC @ 2 मिली/लीटर या एमामेक्टिन बेंज़ोएट 5 SG @ 0.4 ग्राम/लीटर।",
        "treatment_pa": "ਕਲੋਰਪਾਈਰੀਫੋਸ 20 EC @ 2 mL/L ਸਪਰੇਅ ਕਰੋ।",
        "severity": "high",
        "prevention": "Install pheromone traps @ 5/acre. Monitor from August.",
    },
    "healthy": {
        "name": "Healthy Plant",
        "name_hi": "स्वस्थ पौधा",
        "name_pa": "ਤੰਦਰੁਸਤ ਪੌਦਾ",
        "treatment": "No treatment needed. Continue regular care.",
        "treatment_hi": "कोई उपचार नहीं चाहिए। सामान्य देखभाल जारी रखें।",
        "treatment_pa": "ਕੋਈ ਇਲਾਜ ਦੀ ਲੋੜ ਨਹੀਂ।",
        "severity": "none",
        "prevention": "Maintain soil health and balanced nutrition.",
    },
}


class DetectResponse(BaseModel):
    disease_key: str
    disease_name: str
    disease_name_hi: str
    disease_name_pa: str
    confidence: float
    treatment: str
    treatment_hi: str
    treatment_pa: str
    severity: str
    prevention: str
    model_source: str  # "on_device" | "server"


@router.post("/detect", response_model=DetectResponse)
async def detect_disease(
    file: UploadFile = File(..., description="Leaf/plant image"),
):
    """
    Server-side disease detection fallback.
    Primary detection happens on-device via TFLite.
    This endpoint is called when on-device confidence < 60% or no model available.
    """
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Only JPEG/PNG/WEBP images supported.")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=413, detail="Image too large. Max 10MB.")

    # TODO: Load actual TFLite/ONNX model for server-side inference
    # For demo: return mock result based on file size heuristic
    result_key = _mock_inference(len(contents))
    data = DISEASE_TREATMENTS[result_key]

    return DetectResponse(
        disease_key=result_key,
        disease_name=data["name"],
        disease_name_hi=data["name_hi"],
        disease_name_pa=data["name_pa"],
        confidence=0.87,
        treatment=data["treatment"],
        treatment_hi=data["treatment_hi"],
        treatment_pa=data["treatment_pa"],
        severity=data["severity"],
        prevention=data["prevention"],
        model_source="server",
    )


@router.get("/diseases")
async def list_diseases():
    """List all detectable diseases with descriptions."""
    return {
        "total": len(DISEASE_TREATMENTS),
        "diseases": [
            {"key": k, "name": v["name"], "name_pa": v["name_pa"], "severity": v["severity"]}
            for k, v in DISEASE_TREATMENTS.items()
        ],
    }


def _mock_inference(file_size: int) -> str:
    """Demo mock: cycle through diseases based on file size."""
    keys = list(DISEASE_TREATMENTS.keys())
    return keys[file_size % len(keys)]
