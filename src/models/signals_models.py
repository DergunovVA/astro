from pydantic import BaseModel
from typing import List, Optional, Literal

# Signal intensity levels — ordered low < medium < high
SignalIntensity = Literal["low", "medium", "high"]


class Signal(BaseModel):
    id: str
    intensity: SignalIntensity  # strength of the astrological signal
    domain: str
    period: str
    sources: List[str]
    weight: Optional[float] = None
