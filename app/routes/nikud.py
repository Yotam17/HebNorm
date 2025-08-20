from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.utils.nikud import add_nikud

router = APIRouter()

class TextRequest(BaseModel):
    text: str = Field(..., description="Hebrew text to add nikud to")
    keep_vowels: bool = Field(
        default=False, 
        description="Whether to keep matres lectionis (אימות קריאה) in the output. "
                   "When True, vowel letters (א, ה, ו, י) are preserved with '*' marker. "
                   "When False, they are automatically removed by the model."
    )

@router.post("/add_nikud")
def add_nikud_endpoint(req: TextRequest):
    """
    Add nikud (diacritics) to Hebrew text using DictaBERT model.
    
    This endpoint processes Hebrew text and adds appropriate diacritical marks.
    The keep_vowels parameter controls whether matres lectionis are preserved.
    
    Args:
        req: TextRequest containing the text and keep_vowels option
        
    Returns:
        JSON response with input text and processed output
        
    Example:
        POST /api/v1/add_nikud
        {
            "text": "שלום עולם",
            "keep_vowels": true
        }
    """
    return {
        "input": req.text, 
        "output": add_nikud(req.text, req.keep_vowels),
        "keep_vowels": req.keep_vowels
    }
