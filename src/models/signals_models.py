from pydantic import BaseModel
from typing import List, Optional

class Signal(BaseModel):
    id: str
    intensity: str  # 'low', 'medium', 'high'
    domain: str
    period: str
    sources: List[str]
    weight: Optional[float] = None
