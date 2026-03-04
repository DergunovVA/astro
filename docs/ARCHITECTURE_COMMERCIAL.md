# ARCHITECTURE_COMMERCIAL.md

## Core Principle

Calculation Engine is server-controlled intellectual property.

---

## Layers

1. astro_engine (Python core library)
2. API layer (FastAPI)
3. Auth + Subscription control
4. Mobile / Web client

---

## Data Handling

- No PII stored by default
- Cache optional
- Structured logging only
- Explicit consent for chart storage

---

## Licensing

- Swiss Ephemeris documented
- Dependencies pinned
- License file maintained