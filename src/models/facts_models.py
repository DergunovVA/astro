from pydantic import BaseModel
from typing import Optional, Dict

class Fact(BaseModel):
    id: str
    type: str  # 'planet_in_sign', 'aspect', etc.
    object: str
    value: str
    details: Optional[Dict] = None
    source: Optional[str] = None
    timestamp: Optional[str] = None
