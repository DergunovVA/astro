from pydantic import BaseModel
from typing import List, Optional

class Decision(BaseModel):
    id: str
    summary: str
    signals: List[str]
    recommendation: Optional[str] = None
    fatal: bool = False
