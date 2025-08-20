from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.normalizer import normalize

router = APIRouter()

class NormalizeRequest(BaseModel):
    text: str
    with_nikud: bool = False
    spellcheck: bool = False
    customization: dict | None = None

@router.post("/normalize")
def normalize_endpoint(req: NormalizeRequest):
    return {"input": req.text, "output": normalize(
        req.text, req.with_nikud, req.spellcheck, req.customization
    )}
