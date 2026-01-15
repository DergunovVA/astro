from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass(frozen=True)
class ParseWarning:
    code: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResolvedPlace:
    query: str
    name: str
    country: Optional[str]
    lat: float
    lon: float
    tz_name: Optional[str]
    source: str
    confidence: float
    warnings: List[ParseWarning] = field(default_factory=list)


@dataclass(frozen=True)
class NormalizedInput:
    raw_date: str
    raw_time: str
    raw_place: str

    local_dt: datetime          # timezone-aware
    utc_dt: datetime            # timezone-aware (UTC)
    tz_name: str

    lat: float
    lon: float

    place_name: str
    country: Optional[str]

    confidence: float
    warnings: List[ParseWarning] = field(default_factory=list)
