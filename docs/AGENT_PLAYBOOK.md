# Agent Playbook: Code Review + Hardening (Astro Engine)

Use this as a **prompt/guide for an autonomous agent** (or yourself) to run consistent review passes.

---

## 0) Ground rules
- Never use `eval/exec` for DSL execution.
- No user PII in logs by default.
- No network calls by default (geocoding must be opt-in).

---

## 1) Repo health checks (must pass)
### Commands
```bash
python -m pip install -r requirements.txt
pytest -q
```

### Add (recommended) tooling
```bash
python -m pip install ruff mypy pip-audit
ruff check .
mypy src
pip-audit
```

---

## 2) Security checklist (Red Team)
- [ ] Inputs have max length limits (date/time/place, DSL)
- [ ] DSL has max token + nesting depth limits
- [ ] No filesystem writes unless explicitly enabled (`--cache`)
- [ ] No secrets in repo (`.env`, tokens, user charts)

### Tests to add
- fuzz: lexer/parser token storms
- fuzz: date parsing ambiguity
- fuzz: city resolver unicode + long strings

---

## 3) Reliability checklist (SRE)
- [ ] structured logs (JSON) with stable keys
- [ ] retry budget + timeout for geocoder
- [ ] metrics list documented:
  - normalize_input latency
  - cache hit rate
  - geocode failures
  - tz resolve failures

---

## 4) Architecture checklist (Principal)
- [ ] single import style (`astro_engine.*`)
- [ ] no sys.path mutations
- [ ] clear boundaries:
  - core math
  - adapters (swe, geocoder)
  - features (horary/synastry/graph)
  - IO/CLI

---

## 5) “Astrology correctness” checklist
- [ ] enforce `mode=traditional|modern|hybrid`
- [ ] golden charts fixtures per mode
- [ ] doctrine notes: what you implement and what you do NOT

---

## 6) Output artifacts (what the agent should produce)
- `reports/code_review.md`
- `reports/security_findings.md`
- `reports/performance.md`
- `reports/privacy_contract.md`
- `backlog/sprints.md`

