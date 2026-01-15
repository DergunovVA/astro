from __future__ import annotations

from typing import Optional
import logging

from .cache import JsonCache
from .models import ResolvedPlace, ParseWarning

# Module logger (lazy init to avoid circular imports)
_logger = None

def _get_logger():
    global _logger
    if _logger is None:
        _logger = logging.getLogger('astro.input_pipeline.resolver_city')
        # Only configure if not already configured
        if not _logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            _logger.addHandler(handler)
            _logger.setLevel(logging.DEBUG)
            _logger.propagate = False
    return _logger

def _log_operation(operation: str, status: str, **kwargs) -> None:
    """Log operation with optional context."""
    logger = _get_logger()
    msg_parts = [f"{operation}: {status}"]
    if kwargs:
        msg_parts.append(str(kwargs))
    logger.debug(" | ".join(msg_parts))


# MVP: local aliases. Later load from json.
ALIASES = {
    # Russia
    "moscow": ("Moscow", "RU", 55.7558, 37.6173, "Europe/Moscow", 0.95, "alias"),
    "москва": ("Moscow", "RU", 55.7558, 37.6173, "Europe/Moscow", 0.95, "alias"),
    "moskva": ("Moscow", "RU", 55.7558, 37.6173, "Europe/Moscow", 0.9, "alias"),
    "saratov": ("Saratov", "RU", 51.5339, 46.0021, "Europe/Saratov", 0.95, "alias"),
    "саратов": ("Saratov", "RU", 51.5339, 46.0021, "Europe/Saratov", 0.95, "alias"),
    "lipetsk": ("Lipetsk", "RU", 52.6086, 39.5726, "Europe/Moscow", 0.95, "alias"),
    "липецк": ("Lipetsk", "RU", 52.6086, 39.5726, "Europe/Moscow", 0.95, "alias"),
    "st. petersburg": ("Saint Petersburg", "RU", 59.9311, 30.3609, "Europe/Moscow", 0.95, "alias"),
    "saint petersburg": ("Saint Petersburg", "RU", 59.9311, 30.3609, "Europe/Moscow", 0.95, "alias"),
    "спб": ("Saint Petersburg", "RU", 59.9311, 30.3609, "Europe/Moscow", 0.9, "alias"),
    "питер": ("Saint Petersburg", "RU", 59.9311, 30.3609, "Europe/Moscow", 0.85, "alias"),
    "kazan": ("Kazan", "RU", 55.7887, 49.1221, "Europe/Moscow", 0.95, "alias"),
    "казань": ("Kazan", "RU", 55.7887, 49.1221, "Europe/Moscow", 0.95, "alias"),
    "novosibirsk": ("Novosibirsk", "RU", 55.0415, 82.9346, "Asia/Novosibirsk", 0.95, "alias"),
    "новосибирск": ("Novosibirsk", "RU", 55.0415, 82.9346, "Asia/Novosibirsk", 0.95, "alias"),
    
    # Europe
    "london": ("London", "GB", 51.5074, -0.1278, "Europe/London", 0.95, "alias"),
    "paris": ("Paris", "FR", 48.8566, 2.3522, "Europe/Paris", 0.95, "alias"),
    "berlin": ("Berlin", "DE", 52.5200, 13.4050, "Europe/Berlin", 0.95, "alias"),
    "prague": ("Prague", "CZ", 50.0755, 14.4378, "Europe/Prague", 0.95, "alias"),
    "praha": ("Prague", "CZ", 50.0755, 14.4378, "Europe/Prague", 0.9, "alias"),
    "madrid": ("Madrid", "ES", 40.4168, -3.7038, "Europe/Madrid", 0.95, "alias"),
    "rome": ("Rome", "IT", 41.9028, 12.4964, "Europe/Rome", 0.95, "alias"),
    "roma": ("Rome", "IT", 41.9028, 12.4964, "Europe/Rome", 0.9, "alias"),
    "amsterdam": ("Amsterdam", "NL", 52.3676, 4.9041, "Europe/Amsterdam", 0.95, "alias"),
    "vienna": ("Vienna", "AT", 48.2082, 16.3738, "Europe/Vienna", 0.95, "alias"),
    "wien": ("Vienna", "AT", 48.2082, 16.3738, "Europe/Vienna", 0.9, "alias"),
    
    # Asia
    "tokyo": ("Tokyo", "JP", 35.6762, 139.6503, "Asia/Tokyo", 0.95, "alias"),
    "токио": ("Tokyo", "JP", 35.6762, 139.6503, "Asia/Tokyo", 0.9, "alias"),
    "beijing": ("Beijing", "CN", 39.9042, 116.4074, "Asia/Shanghai", 0.95, "alias"),
    "beijing": ("Beijing", "CN", 39.9042, 116.4074, "Asia/Shanghai", 0.95, "alias"),
    "bangkok": ("Bangkok", "TH", 13.7563, 100.5018, "Asia/Bangkok", 0.95, "alias"),
    "delhi": ("Delhi", "IN", 28.7041, 77.1025, "Asia/Kolkata", 0.95, "alias"),
    "dubai": ("Dubai", "AE", 25.2048, 55.2708, "Asia/Dubai", 0.95, "alias"),
    "hong kong": ("Hong Kong", "HK", 22.3193, 114.1694, "Asia/Hong_Kong", 0.95, "alias"),
    "singapore": ("Singapore", "SG", 1.3521, 103.8198, "Asia/Singapore", 0.95, "alias"),
    "shanghai": ("Shanghai", "CN", 31.2304, 121.4737, "Asia/Shanghai", 0.95, "alias"),
    
    # Americas
    "new york": ("New York", "US", 40.7128, -74.0060, "America/New_York", 0.95, "alias"),
    "new york city": ("New York", "US", 40.7128, -74.0060, "America/New_York", 0.95, "alias"),
    "los angeles": ("Los Angeles", "US", 34.0522, -118.2437, "America/Los_Angeles", 0.95, "alias"),
    "chicago": ("Chicago", "US", 41.8781, -87.6298, "America/Chicago", 0.95, "alias"),
    "toronto": ("Toronto", "CA", 43.6532, -79.3832, "America/Toronto", 0.95, "alias"),
    "mexico city": ("Mexico City", "MX", 19.4326, -99.1332, "America/Mexico_City", 0.95, "alias"),
    "sao paulo": ("São Paulo", "BR", -23.5505, -46.6333, "America/Sao_Paulo", 0.95, "alias"),
    "buenos aires": ("Buenos Aires", "AR", -34.6037, -58.3816, "America/Argentina/Buenos_Aires", 0.95, "alias"),
    
    # Africa & Middle East
    "cairo": ("Cairo", "EG", 30.0444, 31.2357, "Africa/Cairo", 0.95, "alias"),
    "istanbul": ("Istanbul", "TR", 41.0082, 28.9784, "Europe/Istanbul", 0.95, "alias"),
    "johannesburg": ("Johannesburg", "ZA", -26.2023, 28.0436, "Africa/Johannesburg", 0.95, "alias"),
    
    # Oceania
    "sydney": ("Sydney", "AU", -33.8688, 151.2093, "Australia/Sydney", 0.95, "alias"),
    "melbourne": ("Melbourne", "AU", -37.8136, 144.9631, "Australia/Melbourne", 0.95, "alias"),
    "auckland": ("Auckland", "NZ", -37.7870, 174.7869, "Pacific/Auckland", 0.95, "alias"),
}


def _check_typos(place: str) -> Optional[tuple[str, float]]:
    """
    Check for typos in city name using fuzzy matching.
    Returns: (suggested_alias_key, match_confidence) or None if no close match.
    """
    try:
        from difflib import SequenceMatcher
        place_lower = place.lower()
        best_match = None
        best_ratio = 0.0
        
        for alias_key in ALIASES.keys():
            ratio = SequenceMatcher(None, place_lower, alias_key).ratio()
            # Only suggest if match is > 70% to avoid false positives
            if ratio > 0.7 and ratio > best_ratio:
                best_ratio = ratio
                best_match = alias_key
        
        return (best_match, best_ratio) if best_match else None
    except Exception:
        return None


def resolve_city(place: str, cache: Optional[JsonCache] = None) -> ResolvedPlace:
    q = place.strip()
    key = q.lower()
    warnings = []

    # 1) cache-first
    if cache:
        cached = cache.get(key)
        if cached:
            _log_operation('resolve_city', 'success', source='cache', confidence=0.95)
            return ResolvedPlace(**cached)

    # 2) check aliases (fast path)
    if key in ALIASES:
        name, country, lat, lon, tz, conf, source = ALIASES[key]
        _log_operation('resolve_city', 'success', source='alias', confidence=conf)
        rp = ResolvedPlace(
            query=q,
            name=name,
            country=country,
            lat=lat,
            lon=lon,
            tz_name=tz,
            source=source,
            confidence=conf,
            warnings=[],
        )
        if cache:
            cache.set(key, rp.__dict__)
        return rp

    # 3) try geopy geocoder for any city in the world
    geopy_available = False
    try:
        from geopy.geocoders import Nominatim  # type: ignore
        geopy_available = True
    except ImportError:
        warnings.append(ParseWarning(
            code="GEOPY_MISSING",
            message="geopy not installed; falling back to aliases"
        ))
    
    if geopy_available:
        try:
            from geopy.geocoders import Nominatim  # type: ignore
            
            geolocator = Nominatim(user_agent="astroprocessor", timeout=10)
            
            # Try to geocode the city
            loc = geolocator.geocode(q, addressdetails=True, language="en")
            
            if loc:
                # Extract country code from address details
                country = None
                if getattr(loc, "raw", None):
                    country = loc.raw.get("address", {}).get("country_code")
                    if country:
                        country = country.upper()
                
                # Use first part of address as city name
                city_name = loc.address.split(",")[0].strip()
                
                _log_operation('resolve_city', 'success', source='geopy', confidence=0.8)
                rp = ResolvedPlace(
                    query=q,
                    name=city_name,
                    country=country,
                    lat=float(loc.latitude),
                    lon=float(loc.longitude),
                    tz_name=None,  # Will be resolved by resolver_timezone
                    source="geocoder",
                    confidence=0.8,  # Higher confidence for successful geocode
                    warnings=warnings,
                )
                if cache:
                    cache.set(key, rp.__dict__)
                return rp
        
        except Exception as e:
            # Geocoding failed (timeout, network, etc.) - continue to typo check
            warnings.append(ParseWarning(
                code="GEOCODER_FAILED",
                message=f"Geocoding failed ({type(e).__name__}); checking aliases"
            ))
    
    # 4) check for typos as last resort
    typo_match = _check_typos(q)
    if typo_match:
        alias_key, confidence = typo_match
        name, country, lat, lon, tz, conf, source = ALIASES[alias_key]
        _log_operation('resolve_city', 'fallback', source='typo_correction', confidence=confidence)
        warnings.append(ParseWarning(
            code="TYPO_DETECTED",
            message=f"City '{q}' not found. Did you mean '{name}'? (match: {confidence*100:.0f}%)"
        ))
        rp = ResolvedPlace(
            query=q,
            name=name,
            country=country,
            lat=lat,
            lon=lon,
            tz_name=tz,
            source="alias",
            confidence=min(conf, confidence),
            warnings=warnings,
        )
        if cache:
            cache.set(key, rp.__dict__)
        return rp
    
    # 5) complete failure
    raise ValueError(f"City not found: '{q}' (no alias match, geocoding unavailable or failed)")
