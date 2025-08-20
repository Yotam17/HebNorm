from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.spellcheck import spellcheck

router = APIRouter()

class SpellRequest(BaseModel):
    text: str

@router.post("/spellcheck")
def spellcheck_endpoint(req: SpellRequest):
    return {"input": req.text, "output": spellcheck(req.text)}
