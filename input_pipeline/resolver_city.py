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
        _logger = logging.getLogger("astro.input_pipeline.resolver_city")
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
    "st. petersburg": (
        "Saint Petersburg",
        "RU",
        59.9311,
        30.3609,
        "Europe/Moscow",
        0.95,
        "alias",
    ),
    "saint petersburg": (
        "Saint Petersburg",
        "RU",
        59.9311,
        30.3609,
        "Europe/Moscow",
        0.95,
        "alias",
    ),
    "спб": ("Saint Petersburg", "RU", 59.9311, 30.3609, "Europe/Moscow", 0.9, "alias"),
    "питер": (
        "Saint Petersburg",
        "RU",
        59.9311,
        30.3609,
        "Europe/Moscow",
        0.85,
        "alias",
    ),
    "kazan": ("Kazan", "RU", 55.7887, 49.1221, "Europe/Moscow", 0.95, "alias"),
    "казань": ("Kazan", "RU", 55.7887, 49.1221, "Europe/Moscow", 0.95, "alias"),
    "novosibirsk": (
        "Novosibirsk",
        "RU",
        55.0415,
        82.9346,
        "Asia/Novosibirsk",
        0.95,
        "alias",
    ),
    "новосибирск": (
        "Novosibirsk",
        "RU",
        55.0415,
        82.9346,
        "Asia/Novosibirsk",
        0.95,
        "alias",
    ),
    "ekaterinburg": (
        "Ekaterinburg",
        "RU",
        56.8389,
        60.6057,
        "Asia/Yekaterinburg",
        0.95,
        "alias",
    ),
    "yekaterinburg": (
        "Ekaterinburg",
        "RU",
        56.8389,
        60.6057,
        "Asia/Yekaterinburg",
        0.95,
        "alias",
    ),
    "екатеринбург": (
        "Ekaterinburg",
        "RU",
        56.8389,
        60.6057,
        "Asia/Yekaterinburg",
        0.95,
        "alias",
    ),
    "nizhny novgorod": (
        "Nizhny Novgorod",
        "RU",
        56.2965,
        43.9361,
        "Europe/Moscow",
        0.95,
        "alias",
    ),
    "нижний новгород": (
        "Nizhny Novgorod",
        "RU",
        56.2965,
        43.9361,
        "Europe/Moscow",
        0.95,
        "alias",
    ),
    "samara": ("Samara", "RU", 53.1959, 50.1004, "Europe/Samara", 0.95, "alias"),
    "самара": ("Samara", "RU", 53.1959, 50.1004, "Europe/Samara", 0.95, "alias"),
    "omsk": ("Omsk", "RU", 54.9885, 73.3242, "Asia/Omsk", 0.95, "alias"),
    "омск": ("Omsk", "RU", 54.9885, 73.3242, "Asia/Omsk", 0.95, "alias"),
    "rostov-on-don": (
        "Rostov-on-Don",
        "RU",
        47.2357,
        39.7015,
        "Europe/Moscow",
        0.95,
        "alias",
    ),
    "rostov": ("Rostov-on-Don", "RU", 47.2357, 39.7015, "Europe/Moscow", 0.9, "alias"),
    "ростов": ("Rostov-on-Don", "RU", 47.2357, 39.7015, "Europe/Moscow", 0.9, "alias"),
    "ростов-на-дону": (
        "Rostov-on-Don",
        "RU",
        47.2357,
        39.7015,
        "Europe/Moscow",
        0.95,
        "alias",
    ),
    "ufa": ("Ufa", "RU", 54.7388, 55.9721, "Asia/Yekaterinburg", 0.95, "alias"),
    "уфа": ("Ufa", "RU", 54.7388, 55.9721, "Asia/Yekaterinburg", 0.95, "alias"),
    "krasnoyarsk": (
        "Krasnoyarsk",
        "RU",
        56.0153,
        92.8932,
        "Asia/Krasnoyarsk",
        0.95,
        "alias",
    ),
    "красноярск": (
        "Krasnoyarsk",
        "RU",
        56.0153,
        92.8932,
        "Asia/Krasnoyarsk",
        0.95,
        "alias",
    ),
    "perm": ("Perm", "RU", 58.0296, 56.2667, "Asia/Yekaterinburg", 0.95, "alias"),
    "пермь": ("Perm", "RU", 58.0296, 56.2667, "Asia/Yekaterinburg", 0.95, "alias"),
    "voronezh": ("Voronezh", "RU", 51.6754, 39.2089, "Europe/Moscow", 0.95, "alias"),
    "воронеж": ("Voronezh", "RU", 51.6754, 39.2089, "Europe/Moscow", 0.95, "alias"),
    "volgograd": (
        "Volgograd",
        "RU",
        48.7080,
        44.5133,
        "Europe/Volgograd",
        0.95,
        "alias",
    ),
    "волгоград": (
        "Volgograd",
        "RU",
        48.7080,
        44.5133,
        "Europe/Volgograd",
        0.95,
        "alias",
    ),
    "krasnodar": ("Krasnodar", "RU", 45.0355, 38.9753, "Europe/Moscow", 0.95, "alias"),
    "краснодар": ("Krasnodar", "RU", 45.0355, 38.9753, "Europe/Moscow", 0.95, "alias"),
    "sochi": ("Sochi", "RU", 43.6028, 39.7342, "Europe/Moscow", 0.95, "alias"),
    "сочи": ("Sochi", "RU", 43.6028, 39.7342, "Europe/Moscow", 0.95, "alias"),
    "chelyabinsk": (
        "Chelyabinsk",
        "RU",
        55.1644,
        61.4368,
        "Asia/Yekaterinburg",
        0.95,
        "alias",
    ),
    "челябинск": (
        "Chelyabinsk",
        "RU",
        55.1644,
        61.4368,
        "Asia/Yekaterinburg",
        0.95,
        "alias",
    ),
    "vladivostok": (
        "Vladivostok",
        "RU",
        43.1332,
        131.9113,
        "Asia/Vladivostok",
        0.95,
        "alias",
    ),
    "владивосток": (
        "Vladivostok",
        "RU",
        43.1332,
        131.9113,
        "Asia/Vladivostok",
        0.95,
        "alias",
    ),
    "irkutsk": ("Irkutsk", "RU", 52.2978, 104.2964, "Asia/Irkutsk", 0.95, "alias"),
    "иркутск": ("Irkutsk", "RU", 52.2978, 104.2964, "Asia/Irkutsk", 0.95, "alias"),
    # Europe
    "london": ("London", "GB", 51.5074, -0.1278, "Europe/London", 0.95, "alias"),
    "paris": ("Paris", "FR", 48.8566, 2.3522, "Europe/Paris", 0.95, "alias"),
    "berlin": ("Berlin", "DE", 52.5200, 13.4050, "Europe/Berlin", 0.95, "alias"),
    "prague": ("Prague", "CZ", 50.0755, 14.4378, "Europe/Prague", 0.95, "alias"),
    "praha": ("Prague", "CZ", 50.0755, 14.4378, "Europe/Prague", 0.9, "alias"),
    "madrid": ("Madrid", "ES", 40.4168, -3.7038, "Europe/Madrid", 0.95, "alias"),
    "rome": ("Rome", "IT", 41.9028, 12.4964, "Europe/Rome", 0.95, "alias"),
    "roma": ("Rome", "IT", 41.9028, 12.4964, "Europe/Rome", 0.9, "alias"),
    "amsterdam": (
        "Amsterdam",
        "NL",
        52.3676,
        4.9041,
        "Europe/Amsterdam",
        0.95,
        "alias",
    ),
    "vienna": ("Vienna", "AT", 48.2082, 16.3738, "Europe/Vienna", 0.95, "alias"),
    "wien": ("Vienna", "AT", 48.2082, 16.3738, "Europe/Vienna", 0.9, "alias"),
    "warsaw": ("Warsaw", "PL", 52.2297, 21.0122, "Europe/Warsaw", 0.95, "alias"),
    "warszawa": ("Warsaw", "PL", 52.2297, 21.0122, "Europe/Warsaw", 0.9, "alias"),
    "варшава": ("Warsaw", "PL", 52.2297, 21.0122, "Europe/Warsaw", 0.9, "alias"),
    "budapest": ("Budapest", "HU", 47.4979, 19.0402, "Europe/Budapest", 0.95, "alias"),
    "будапешт": ("Budapest", "HU", 47.4979, 19.0402, "Europe/Budapest", 0.9, "alias"),
    "athens": ("Athens", "GR", 37.9838, 23.7275, "Europe/Athens", 0.95, "alias"),
    "афины": ("Athens", "GR", 37.9838, 23.7275, "Europe/Athens", 0.9, "alias"),
    "copenhagen": (
        "Copenhagen",
        "DK",
        55.6761,
        12.5683,
        "Europe/Copenhagen",
        0.95,
        "alias",
    ),
    "københavn": (
        "Copenhagen",
        "DK",
        55.6761,
        12.5683,
        "Europe/Copenhagen",
        0.9,
        "alias",
    ),
    "stockholm": (
        "Stockholm",
        "SE",
        59.3293,
        18.0686,
        "Europe/Stockholm",
        0.95,
        "alias",
    ),
    "стокгольм": (
        "Stockholm",
        "SE",
        59.3293,
        18.0686,
        "Europe/Stockholm",
        0.9,
        "alias",
    ),
    "oslo": ("Oslo", "NO", 59.9139, 10.7522, "Europe/Oslo", 0.95, "alias"),
    "осло": ("Oslo", "NO", 59.9139, 10.7522, "Europe/Oslo", 0.9, "alias"),
    "helsinki": ("Helsinki", "FI", 60.1699, 24.9384, "Europe/Helsinki", 0.95, "alias"),
    "хельсинки": ("Helsinki", "FI", 60.1699, 24.9384, "Europe/Helsinki", 0.9, "alias"),
    "brussels": ("Brussels", "BE", 50.8503, 4.3517, "Europe/Brussels", 0.95, "alias"),
    "bruxelles": ("Brussels", "BE", 50.8503, 4.3517, "Europe/Brussels", 0.9, "alias"),
    "lisbon": ("Lisbon", "PT", 38.7223, -9.1393, "Europe/Lisbon", 0.95, "alias"),
    "lisboa": ("Lisbon", "PT", 38.7223, -9.1393, "Europe/Lisbon", 0.9, "alias"),
    "dublin": ("Dublin", "IE", 53.3498, -6.2603, "Europe/Dublin", 0.95, "alias"),
    "bucharest": (
        "Bucharest",
        "RO",
        44.4268,
        26.1025,
        "Europe/Bucharest",
        0.95,
        "alias",
    ),
    "bucuresti": (
        "Bucharest",
        "RO",
        44.4268,
        26.1025,
        "Europe/Bucharest",
        0.9,
        "alias",
    ),
    "sofia": ("Sofia", "BG", 42.6977, 23.3219, "Europe/Sofia", 0.95, "alias"),
    "софия": ("Sofia", "BG", 42.6977, 23.3219, "Europe/Sofia", 0.9, "alias"),
    "zagreb": ("Zagreb", "HR", 45.8150, 15.9819, "Europe/Zagreb", 0.95, "alias"),
    "belgrade": ("Belgrade", "RS", 44.7866, 20.4489, "Europe/Belgrade", 0.95, "alias"),
    "beograd": ("Belgrade", "RS", 44.7866, 20.4489, "Europe/Belgrade", 0.9, "alias"),
    "минск": ("Minsk", "BY", 53.9045, 27.5615, "Europe/Minsk", 0.95, "alias"),
    "minsk": ("Minsk", "BY", 53.9045, 27.5615, "Europe/Minsk", 0.95, "alias"),
    "kiev": ("Kyiv", "UA", 50.4501, 30.5234, "Europe/Kiev", 0.95, "alias"),
    "kyiv": ("Kyiv", "UA", 50.4501, 30.5234, "Europe/Kiev", 0.95, "alias"),
    "киев": ("Kyiv", "UA", 50.4501, 30.5234, "Europe/Kiev", 0.95, "alias"),
    # Asia
    "tokyo": ("Tokyo", "JP", 35.6762, 139.6503, "Asia/Tokyo", 0.95, "alias"),
    "токио": ("Tokyo", "JP", 35.6762, 139.6503, "Asia/Tokyo", 0.9, "alias"),
    "beijing": ("Beijing", "CN", 39.9042, 116.4074, "Asia/Shanghai", 0.95, "alias"),
    "bangkok": ("Bangkok", "TH", 13.7563, 100.5018, "Asia/Bangkok", 0.95, "alias"),
    "delhi": ("Delhi", "IN", 28.7041, 77.1025, "Asia/Kolkata", 0.95, "alias"),
    "dubai": ("Dubai", "AE", 25.2048, 55.2708, "Asia/Dubai", 0.95, "alias"),
    "hong kong": (
        "Hong Kong",
        "HK",
        22.3193,
        114.1694,
        "Asia/Hong_Kong",
        0.95,
        "alias",
    ),
    "singapore": ("Singapore", "SG", 1.3521, 103.8198, "Asia/Singapore", 0.95, "alias"),
    "shanghai": ("Shanghai", "CN", 31.2304, 121.4737, "Asia/Shanghai", 0.95, "alias"),
    "seoul": ("Seoul", "KR", 37.5665, 126.9780, "Asia/Seoul", 0.95, "alias"),
    "сеул": ("Seoul", "KR", 37.5665, 126.9780, "Asia/Seoul", 0.9, "alias"),
    "mumbai": ("Mumbai", "IN", 19.0760, 72.8777, "Asia/Kolkata", 0.95, "alias"),
    "bangalore": ("Bangalore", "IN", 12.9716, 77.5946, "Asia/Kolkata", 0.95, "alias"),
    "bengaluru": ("Bangalore", "IN", 12.9716, 77.5946, "Asia/Kolkata", 0.95, "alias"),
    "kuala lumpur": (
        "Kuala Lumpur",
        "MY",
        3.1390,
        101.6869,
        "Asia/Kuala_Lumpur",
        0.95,
        "alias",
    ),
    "ho chi minh": (
        "Ho Chi Minh City",
        "VN",
        10.8231,
        106.6297,
        "Asia/Ho_Chi_Minh",
        0.95,
        "alias",
    ),
    "saigon": (
        "Ho Chi Minh City",
        "VN",
        10.8231,
        106.6297,
        "Asia/Ho_Chi_Minh",
        0.9,
        "alias",
    ),
    "taipei": ("Taipei", "TW", 25.0330, 121.5654, "Asia/Taipei", 0.95, "alias"),
    "manila": ("Manila", "PH", 14.5995, 120.9842, "Asia/Manila", 0.95, "alias"),
    "jakarta": ("Jakarta", "ID", -6.2088, 106.8456, "Asia/Jakarta", 0.95, "alias"),
    "hanoi": ("Hanoi", "VN", 21.0285, 105.8542, "Asia/Ho_Chi_Minh", 0.95, "alias"),
    "karachi": ("Karachi", "PK", 24.8607, 67.0011, "Asia/Karachi", 0.95, "alias"),
    "colombo": ("Colombo", "LK", 6.9271, 79.8612, "Asia/Colombo", 0.95, "alias"),
    "tashkent": ("Tashkent", "UZ", 41.2995, 69.2401, "Asia/Tashkent", 0.95, "alias"),
    "ташкент": ("Tashkent", "UZ", 41.2995, 69.2401, "Asia/Tashkent", 0.95, "alias"),
    "almaty": ("Almaty", "KZ", 43.2220, 76.8512, "Asia/Almaty", 0.95, "alias"),
    "алматы": ("Almaty", "KZ", 43.2220, 76.8512, "Asia/Almaty", 0.95, "alias"),
    "tbilisi": ("Tbilisi", "GE", 41.7151, 44.8271, "Asia/Tbilisi", 0.95, "alias"),
    "тбилиси": ("Tbilisi", "GE", 41.7151, 44.8271, "Asia/Tbilisi", 0.95, "alias"),
    "yerevan": ("Yerevan", "AM", 40.1792, 44.4991, "Asia/Yerevan", 0.95, "alias"),
    "ереван": ("Yerevan", "AM", 40.1792, 44.4991, "Asia/Yerevan", 0.95, "alias"),
    "baku": ("Baku", "AZ", 40.4093, 49.8671, "Asia/Baku", 0.95, "alias"),
    "баку": ("Baku", "AZ", 40.4093, 49.8671, "Asia/Baku", 0.95, "alias"),
    # Americas
    "new york": (
        "New York",
        "US",
        40.7128,
        -74.0060,
        "America/New_York",
        0.95,
        "alias",
    ),
    "new york city": (
        "New York",
        "US",
        40.7128,
        -74.0060,
        "America/New_York",
        0.95,
        "alias",
    ),
    "los angeles": (
        "Los Angeles",
        "US",
        34.0522,
        -118.2437,
        "America/Los_Angeles",
        0.95,
        "alias",
    ),
    "chicago": ("Chicago", "US", 41.8781, -87.6298, "America/Chicago", 0.95, "alias"),
    "toronto": ("Toronto", "CA", 43.6532, -79.3832, "America/Toronto", 0.95, "alias"),
    "mexico city": (
        "Mexico City",
        "MX",
        19.4326,
        -99.1332,
        "America/Mexico_City",
        0.95,
        "alias",
    ),
    "sao paulo": (
        "São Paulo",
        "BR",
        -23.5505,
        -46.6333,
        "America/Sao_Paulo",
        0.95,
        "alias",
    ),
    "são paulo": (
        "São Paulo",
        "BR",
        -23.5505,
        -46.6333,
        "America/Sao_Paulo",
        0.95,
        "alias",
    ),
    "buenos aires": (
        "Buenos Aires",
        "AR",
        -34.6037,
        -58.3816,
        "America/Argentina/Buenos_Aires",
        0.95,
        "alias",
    ),
    "san francisco": (
        "San Francisco",
        "US",
        37.7749,
        -122.4194,
        "America/Los_Angeles",
        0.95,
        "alias",
    ),
    "boston": ("Boston", "US", 42.3601, -71.0589, "America/New_York", 0.95, "alias"),
    "washington": (
        "Washington D.C.",
        "US",
        38.9072,
        -77.0369,
        "America/New_York",
        0.95,
        "alias",
    ),
    "washington dc": (
        "Washington D.C.",
        "US",
        38.9072,
        -77.0369,
        "America/New_York",
        0.95,
        "alias",
    ),
    "miami": ("Miami", "US", 25.7617, -80.1918, "America/New_York", 0.95, "alias"),
    "seattle": (
        "Seattle",
        "US",
        47.6062,
        -122.3321,
        "America/Los_Angeles",
        0.95,
        "alias",
    ),
    "las vegas": (
        "Las Vegas",
        "US",
        36.1699,
        -115.1398,
        "America/Los_Angeles",
        0.95,
        "alias",
    ),
    "denver": ("Denver", "US", 39.7392, -104.9903, "America/Denver", 0.95, "alias"),
    "philadelphia": (
        "Philadelphia",
        "US",
        39.9526,
        -75.1652,
        "America/New_York",
        0.95,
        "alias",
    ),
    "phoenix": ("Phoenix", "US", 33.4484, -112.0740, "America/Phoenix", 0.95, "alias"),
    "houston": ("Houston", "US", 29.7604, -95.3698, "America/Chicago", 0.95, "alias"),
    "atlanta": ("Atlanta", "US", 33.7490, -84.3880, "America/New_York", 0.95, "alias"),
    "vancouver": (
        "Vancouver",
        "CA",
        49.2827,
        -123.1207,
        "America/Vancouver",
        0.95,
        "alias",
    ),
    "montreal": ("Montreal", "CA", 45.5017, -73.5673, "America/Toronto", 0.95, "alias"),
    "montréal": ("Montreal", "CA", 45.5017, -73.5673, "America/Toronto", 0.95, "alias"),
    "rio de janeiro": (
        "Rio de Janeiro",
        "BR",
        -22.9068,
        -43.1729,
        "America/Sao_Paulo",
        0.95,
        "alias",
    ),
    "santiago": (
        "Santiago",
        "CL",
        -33.4489,
        -70.6693,
        "America/Santiago",
        0.95,
        "alias",
    ),
    "lima": ("Lima", "PE", -12.0464, -77.0428, "America/Lima", 0.95, "alias"),
    "bogota": ("Bogota", "CO", 4.7110, -74.0721, "America/Bogota", 0.95, "alias"),
    "bogotá": ("Bogota", "CO", 4.7110, -74.0721, "America/Bogota", 0.95, "alias"),
    "havana": ("Havana", "CU", 23.1136, -82.3666, "America/Havana", 0.95, "alias"),
    "la habana": ("Havana", "CU", 23.1136, -82.3666, "America/Havana", 0.9, "alias"),
    # Africa & Middle East
    "cairo": ("Cairo", "EG", 30.0444, 31.2357, "Africa/Cairo", 0.95, "alias"),
    "istanbul": ("Istanbul", "TR", 41.0082, 28.9784, "Europe/Istanbul", 0.95, "alias"),
    "стамбул": ("Istanbul", "TR", 41.0082, 28.9784, "Europe/Istanbul", 0.9, "alias"),
    "johannesburg": (
        "Johannesburg",
        "ZA",
        -26.2023,
        28.0436,
        "Africa/Johannesburg",
        0.95,
        "alias",
    ),
    "tel aviv": ("Tel Aviv", "IL", 32.0853, 34.7818, "Asia/Jerusalem", 0.95, "alias"),
    "jerusalem": ("Jerusalem", "IL", 31.7683, 35.2137, "Asia/Jerusalem", 0.95, "alias"),
    "riyadh": ("Riyadh", "SA", 24.7136, 46.6753, "Asia/Riyadh", 0.95, "alias"),
    "doha": ("Doha", "QA", 25.2854, 51.5310, "Asia/Qatar", 0.95, "alias"),
    "abu dhabi": ("Abu Dhabi", "AE", 24.4539, 54.3773, "Asia/Dubai", 0.95, "alias"),
    "nairobi": ("Nairobi", "KE", -1.2921, 36.8219, "Africa/Nairobi", 0.95, "alias"),
    "lagos": ("Lagos", "NG", 6.5244, 3.3792, "Africa/Lagos", 0.95, "alias"),
    "casablanca": (
        "Casablanca",
        "MA",
        33.5731,
        -7.5898,
        "Africa/Casablanca",
        0.95,
        "alias",
    ),
    "tunis": ("Tunis", "TN", 36.8065, 10.1815, "Africa/Tunis", 0.95, "alias"),
    "algiers": ("Algiers", "DZ", 36.7538, 3.0588, "Africa/Algiers", 0.95, "alias"),
    "tehran": ("Tehran", "IR", 35.6892, 51.3890, "Asia/Tehran", 0.95, "alias"),
    "тегеран": ("Tehran", "IR", 35.6892, 51.3890, "Asia/Tehran", 0.9, "alias"),
    "damascus": ("Damascus", "SY", 33.5138, 36.2765, "Asia/Damascus", 0.95, "alias"),
    "beirut": ("Beirut", "LB", 33.8886, 35.4955, "Asia/Beirut", 0.95, "alias"),
    "amman": ("Amman", "JO", 31.9454, 35.9284, "Asia/Amman", 0.95, "alias"),
    # Oceania
    "sydney": ("Sydney", "AU", -33.8688, 151.2093, "Australia/Sydney", 0.95, "alias"),
    "melbourne": (
        "Melbourne",
        "AU",
        -37.8136,
        144.9631,
        "Australia/Melbourne",
        0.95,
        "alias",
    ),
    "auckland": (
        "Auckland",
        "NZ",
        -37.7870,
        174.7869,
        "Pacific/Auckland",
        0.95,
        "alias",
    ),
    "brisbane": (
        "Brisbane",
        "AU",
        -27.4698,
        153.0251,
        "Australia/Brisbane",
        0.95,
        "alias",
    ),
    "perth": ("Perth", "AU", -31.9505, 115.8605, "Australia/Perth", 0.95, "alias"),
    "adelaide": (
        "Adelaide",
        "AU",
        -34.9285,
        138.6007,
        "Australia/Adelaide",
        0.95,
        "alias",
    ),
    "wellington": (
        "Wellington",
        "NZ",
        -41.2865,
        174.7762,
        "Pacific/Auckland",
        0.95,
        "alias",
    ),
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
            _log_operation("resolve_city", "success", source="cache", confidence=0.95)
            return ResolvedPlace(**cached)

    # 2) check aliases (fast path)
    if key in ALIASES:
        name, country, lat, lon, tz, conf, source = ALIASES[key]
        _log_operation("resolve_city", "success", source="alias", confidence=conf)
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
        warnings.append(
            ParseWarning(
                code="GEOPY_MISSING",
                message="geopy not installed; falling back to aliases",
            )
        )

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

                _log_operation(
                    "resolve_city", "success", source="geopy", confidence=0.8
                )
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
            warnings.append(
                ParseWarning(
                    code="GEOCODER_FAILED",
                    message=f"Geocoding failed ({type(e).__name__}); checking aliases",
                )
            )

    # 4) check for typos as last resort
    typo_match = _check_typos(q)
    if typo_match:
        alias_key, confidence = typo_match
        name, country, lat, lon, tz, conf, source = ALIASES[alias_key]
        _log_operation(
            "resolve_city", "fallback", source="typo_correction", confidence=confidence
        )
        warnings.append(
            ParseWarning(
                code="TYPO_DETECTED",
                message=f"City '{q}' not found. Did you mean '{name}'? (match: {confidence * 100:.0f}%)",
            )
        )
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
    raise ValueError(
        f"City not found: '{q}' (no alias match, geocoding unavailable or failed)"
    )
