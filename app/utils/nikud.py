import torch
from transformers import AutoModel, AutoTokenizer
from app.config import settings

device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(settings.nikud_model)
model = AutoModel.from_pretrained(settings.nikud_model, trust_remote_code=True)
model.to(device).eval()

def add_nikud(text: str, keep_vowels: bool = False) -> str:
    """
    Add nikud (diacritics) to Hebrew text using DictaBERT model.
    
    Args:
        text: Hebrew text to add nikud to
        keep_vowels: Whether to keep matres lectionis (אימות קריאה) in the output
        
    Returns:
        Hebrew text with nikud added
    """
    # Use mark_matres_lectionis parameter to control vowel preservation
    mark_matres_lectionis = '*' if keep_vowels else None
    
    return model.predict([text], tokenizer, mark_matres_lectionis=mark_matres_lectionis)[0]
