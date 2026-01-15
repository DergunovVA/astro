# Relocation calculation (basic stub)
def relocate_coords(place: str) -> dict:
    # TODO: geocode place to lat/lon
    # For demo: Moscow
    if place.lower() == "moscow":
        return {"lat": 55.7558, "lon": 37.6173}
    # Add more cities or use geocoding API
    return {"lat": 0.0, "lon": 0.0}
