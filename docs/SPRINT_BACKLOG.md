# Sprint Backlog (Hardening → Product)

This backlog is organized as **epics → sprints → tasks** with acceptance criteria.

---

## Epic A — Installable, clean package
### Sprint A0 (Packaging)
- [ ] Add `pyproject.toml` (build-system + deps + scripts)
- [ ] Move code to `src/astro_engine/`
- [ ] Replace `modules.*` imports with `astro_engine.*`
- [ ] CLI entrypoint: `astro` (Typer)
- [ ] Remove `sys.path` hacks

**Acceptance:** `pip install -e .` works; `python -m astro_engine` works; tests pass in clean venv.

---

## Epic B — Privacy & security contract
### Sprint B0 (PII hardening)
- [ ] Replace regex redaction with field-based redaction
- [ ] Add tests proving logs never contain:
  - raw coordinates
  - full birth datetime
  - full place string
- [ ] Default `--no-cache`; caching opt-in
- [ ] CI guard: block commits of `user_*.json`, `*_chart.json`, `*.cache*`

**Acceptance:** `pytest -q` includes PII regression tests; running CLI produces no PII files by default.

### Sprint B1 (Supply chain)
- [ ] Pin dependencies or add lock (uv/poetry/pip-tools)
- [ ] Add `pip-audit` in CI
- [ ] Generate SBOM (optional)

---

## Epic C — Correctness modes (Traditional/Modern/Vedic-ready)
### Sprint C0 (Mode plumbing)
- [ ] Single `Mode` enum propagated through:
  - dignities, rulers, house systems, aspects, horary rules
- [ ] Validate tables per mode
- [ ] Document doctrine differences

**Acceptance:** same input produces deterministic outputs; mode changes outputs in documented ways.

### Sprint C1 (Golden tests)
- [ ] Add fixtures:
  - 5 natal charts
  - 3 horary charts
  - 2 sidereal charts with ayanamsa
- [ ] Compare against expected key positions & aspects

---

## Epic D — SRE readiness
### Sprint D0 (Observability)
- [ ] Structured logs across layers (stable keys)
- [ ] Error code taxonomy
- [ ] Metrics hooks (even if just counters)

### Sprint D1 (Resilience)
- [ ] Retry budget + backoff for geocoder
- [ ] Offline mode default
- [ ] Timeouts everywhere network touches happen

---

## Epic E — Performance & scale
### Sprint E0 (Bench discipline)
- [ ] Benchmark gates in CI (thresholds)
- [ ] Cache correctness tests (TTL, eviction)

---

## Epic F — Product polish
### Sprint F0 (Docs)
- [ ] “Getting started” in 5 minutes
- [ ] “Professional usage”
- [ ] “Astrology doctrine” page (what’s implemented)

