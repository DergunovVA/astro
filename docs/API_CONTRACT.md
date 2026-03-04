# API_CONTRACT.md

## Endpoint: POST /v1/calc

### Request JSON
{
  "datetime": "YYYY-MM-DDTHH:MM:SS",
  "latitude": float,
  "longitude": float,
  "mode": "traditional|modern|sidereal",
  "house_system": "placidus|whole_sign"
}

### Response JSON
{
  "planets": [...],
  "houses": [...],
  "aspects": [...],
  "metadata": {...}
}

---

## Versioning

Breaking changes require version bump.