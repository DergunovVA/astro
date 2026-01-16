# Privacy & Data Policy

## Disclaimer

This is an **astrology calculation library**, not a data collection service. It:

- ✅ Does NOT store user birth data
- ✅ Does NOT transmit data to external servers (optional geopy only with user permission)
- ✅ Does NOT track or identify users
- ✅ Does NOT use cookies or analytics

## Data Handling

### What Data We Process

- **Input**: Date, time, location strings (provided by user at runtime)
- **Processing**: Converted to UTC datetime and coordinates for calculation
- **Output**: Planetary positions and aspects
- **Storage**: Only local cache of city coordinates (no personal data)

### What We DON'T Store

- ❌ Birth records of real people
- ❌ User identification data
- ❌ IP addresses or access logs
- ❌ Calculation results

### Cache File (`.cache_places.json`)

- **What it contains**: City names → coordinates mapping
- **Why**: Avoid repeated geocoding API calls (performance + cost)
- **Who can access**: Only local machine (not uploaded)
- **Data sensitivity**: Low (public geographic data)
- **How to clear**: Delete `.cache_places.json` or call `reset_global_cache()`

## GDPR Compliance

### Article 4 (Definitions)

- No "processing of personal data" occurs if input contains only date/time/location
- Birth data is PII only when combined with identity → we don't store that

### Article 5 (Principles)

- **Lawfulness**: Calculation as stated purpose ✓
- **Data minimization**: No unnecessary data collection ✓
- **Storage limitation**: No data retention ✓
- **Integrity & confidentiality**: Code reviewed, no known vulnerabilities ✓

### Article 6 (Legal basis)

- Users provide input willingly for astrological calculation
- Legitimate interest in planetary mechanics

### Right to be Forgotten (Article 17)

- Delete local cache: `reset_global_cache()`
- No personal data is retained server-side

## California Consumer Privacy Act (CCPA)

Not applicable - this library:

- Doesn't sell personal information
- Doesn't collect personal information
- Doesn't have a privacy policy requirement (no collection)

## US State Laws (NYSDPA, CPA, etc.)

No state-specific concerns:

- No data broker activity
- No sensitive data categories (SSN, financial, health beyond astrology)
- No secondary marketing

## Recommendations for Users

### Self-hosting

```python
from input_pipeline import normalize_input, reset_global_cache

# Process birth data
ni = normalize_input("1990-01-15", "14:30", "Moscow")

# If concerned about local cache:
reset_global_cache()  # Clears .cache_places.json
```

### Batch Processing

```python
# Avoid storing results locally
results = []
for date, time, place in data:
    ni = normalize_input(date, time, place)
    result = natal_calculation(ni.utc_dt, ni.lat, ni.lon)
    # Process and discard immediately
    # Don't save to disk
```

### Production Deployment

- Run on private infrastructure (not cloud)
- Set `--strict` mode for validation
- No logging of coordinates/dates
- Clear cache regularly: `cache.clear()`

## Third-party Dependencies

### geopy (Nominatim)

- **Purpose**: Map city names to coordinates
- **Optional**: Can use alias database without it
- **Data sharing**: City strings sent to OpenStreetMap API
- **User control**: `--tz` parameter bypasses geolocation

### timezonefinder

- **Purpose**: Map coordinates to IANA timezone
- **Data sharing**: None (offline library)
- **User control**: `--tz` parameter bypasses it

### Swiss Ephemeris

- **Purpose**: Calculate planetary positions
- **Data sharing**: None (local calculations)
- **User control**: None needed

## Contact & Questions

This is an open-source library. For privacy concerns:

- Review the code (github.com/...)
- Use in audit mode with `--devils` flag for transparency
- Submit issues for security review

## Version History

| Version | Date       | Changes                |
| ------- | ---------- | ---------------------- |
| 1.0     | 2026-01-15 | Initial privacy policy |

---

**Last Updated**: January 15, 2026  
**Status**: Compliant with GDPR (safe harbor: no personal data retention)
