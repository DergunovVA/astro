from pydantic import BaseModel
from typing import Optional, Dict, Literal

# Known fact types — extend as new fact categories are added
FactType = Literal[
    "planet_in_sign",
    "aspect",
    "aspect_to_angle",
    "aspect_to_cusp",
    "house_position",
    "house_cusp",
    "dignity",
    "essential_dignity",
    "accidental_dignity",
    "total_dignity",
    "dispositor",
    "mutual_reception",
    "retrograde",
    "solar_condition",
    "arabic_lot",
    "special_point",
    "pattern",
    "profection",
    "progression",
]


class Fact(BaseModel):
    id: str
    type: FactType  # discriminated union of known fact categories
    object: str
    value: str
    details: Optional[Dict] = None
    source: Optional[str] = None
    timestamp: Optional[str] = None
