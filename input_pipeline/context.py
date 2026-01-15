"""InputContext: Bridge class connecting normalized input to calculation results."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List

from .models import NormalizedInput, ParseWarning


@dataclass(frozen=True)
class InputContext:
    """
    Bridge class that wraps NormalizedInput and provides convenient access
    to both input data and metadata.
    
    This class serves as a bridge between:
    - Input normalization layer (normalize_input)
    - Calculation layer (natal_calculation, transit_calculation, etc.)
    - Result serialization (JSON output)
    
    Immutable (frozen=True) to prevent accidental modifications during calculation.
    """
    
    # Original input
    raw_date: str
    raw_time: str
    raw_place: str
    
    # Normalized datetime
    local_dt: datetime  # timezone-aware (local)
    utc_dt: datetime    # timezone-aware (UTC)
    tz_name: str
    
    # Geocoded coordinates
    lat: float
    lon: float
    
    # Place information
    place_name: str
    country: Optional[str]
    
    # Quality indicators
    confidence: float  # 0.0-1.0
    warnings: List[ParseWarning] = field(default_factory=list)
    
    @classmethod
    def from_normalized(cls, ni: NormalizedInput) -> InputContext:
        """
        Factory method: Create InputContext from NormalizedInput.
        
        Args:
            ni: NormalizedInput dataclass from normalize_input()
            
        Returns:
            InputContext with same data
        """
        return cls(
            raw_date=ni.raw_date,
            raw_time=ni.raw_time,
            raw_place=ni.raw_place,
            local_dt=ni.local_dt,
            utc_dt=ni.utc_dt,
            tz_name=ni.tz_name,
            lat=ni.lat,
            lon=ni.lon,
            place_name=ni.place_name,
            country=ni.country,
            confidence=ni.confidence,
            warnings=ni.warnings
        )
    
    def to_metadata_dict(self) -> Dict[str, Any]:
        """
        Convert to metadata dict suitable for JSON output.
        
        Returns:
            Dict with: confidence, timezone, local_datetime, utc_datetime,
                      coordinates, warnings
        """
        return {
            "confidence": self.confidence,
            "timezone": self.tz_name,
            "local_datetime": self.local_dt.isoformat(),
            "utc_datetime": self.utc_dt.isoformat(),
            "coordinates": {
                "lat": self.lat,
                "lon": self.lon
            },
            "place": {
                "name": self.place_name,
                "country": self.country
            },
            "warnings": [
                {"code": w.code, "message": w.message}
                for w in self.warnings
            ] if self.warnings else []
        }
    
    def to_metadata_dict_minimal(self) -> Dict[str, Any]:
        """
        Minimal metadata dict (coordinates only).
        
        Returns:
            Dict with: confidence, timezone, coordinates
        """
        return {
            "confidence": self.confidence,
            "timezone": self.tz_name,
            "coordinates": {
                "lat": self.lat,
                "lon": self.lon
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entire context to dict (for debugging/logging).
        
        Returns:
            Complete dict representation of all fields
        """
        return {
            "raw_input": {
                "date": self.raw_date,
                "time": self.raw_time,
                "place": self.raw_place
            },
            "normalized": {
                "local_dt": self.local_dt.isoformat(),
                "utc_dt": self.utc_dt.isoformat(),
                "timezone": self.tz_name
            },
            "geocoding": {
                "place": self.place_name,
                "country": self.country,
                "lat": self.lat,
                "lon": self.lon,
                "confidence": self.confidence
            },
            "warnings": [
                {"code": w.code, "message": w.message, "details": w.details}
                for w in self.warnings
            ] if self.warnings else []
        }
    
    def has_warnings(self) -> bool:
        """Check if input had any parsing warnings."""
        return len(self.warnings) > 0
    
    def get_coordinates(self) -> tuple[float, float]:
        """Get (lat, lon) tuple."""
        return (self.lat, self.lon)
    
    def get_utc_datetime(self) -> datetime:
        """Get UTC aware datetime for calculation."""
        return self.utc_dt
    
    def get_local_datetime(self) -> datetime:
        """Get local aware datetime for display."""
        return self.local_dt
