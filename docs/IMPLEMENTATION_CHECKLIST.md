# IMPLEMENTATION CHECKLIST

## PHASE 1: CRITICAL FIXES (Week 1 - ~2.5 hours)

### 1. Update astro_adapter.py signatures ☐

- [ ] Update `julian_day(str, str)` → `julian_day(datetime)`
- [ ] Add UTC validation in julian_day()
- [ ] Update `natal_calculation(str, str, str)` → `natal_calculation(datetime, float, float)`
- [ ] Remove relocation_coords call from natal_calculation
- [ ] Update return dict structure (remove "datetime", "place")
- [ ] Update docstrings with new signatures
- [ ] **Test**: `python -c "from astro_adapter import natal_calculation; ..."`
- **Effort**: 20 min

### 2. Update main.py natal command ☐

- [ ] Import `InputContext` (or just use ni directly)
- [ ] Pass `ni.utc_dt, ni.lat, ni.lon` to natal_calculation
- [ ] Remove string formatting of dates
- [ ] Add `input_metadata` to result dict
- [ ] Fix Pydantic deprecation: `.dict()` → `.model_dump()`
- [ ] Update error handling for datetime validation errors
- [ ] Add `--tz` parameter with help text
- [ ] **Test**: `python -m main natal 1990-01-01 12:00 Moscow`
- **Effort**: 15 min

### 3. Update relocation_math.py integration ☐

- [ ] Import `resolve_city` and `JsonCache` from input_pipeline
- [ ] Create `get_global_cache()` function
- [ ] Update `relocate_coords()` to use `resolve_city()`
- [ ] Remove direct Nominatim usage
- [ ] Add docstring with explanation
- [ ] **Test**: `python -m main relocate Lipetsk`
- [ ] **Test**: `python -m main relocate tokyo` (new city)
- **Effort**: 10 min

### 4. Update transit command ☐

- [ ] Add `normalize_input()` before calculation
- [ ] Update signature: add `tz: str | None = None` parameter
- [ ] Update calculation call with `ni.utc_dt, ni.lat, ni.lon`
- [ ] Add `input_metadata` to result
- [ ] Fix Pydantic deprecation
- [ ] **Test**: `python -m main transit 2025-01-15 12:00 Moscow`
- **Effort**: 10 min

### 5. Update solar command ☐

- [ ] Add `normalize_input()` before calculation
- [ ] Update signature: add `tz: str | None = None` parameter
- [ ] Update calculation call with `ni.utc_dt, ni.lat, ni.lon`
- [ ] Add `input_metadata` to result
- [ ] Fix Pydantic deprecation
- [ ] **Test**: `python -m main solar 2025-01-01 12:00 Moscow`
- **Effort**: 10 min

### 6. Update rectify command ☐

- [ ] Add `normalize_input()` before calculation
- [ ] Update signature: add `tz: str | None = None` parameter
- [ ] Add `input_metadata` to result
- [ ] Fix Pydantic deprecation
- [ ] **Test**: `python -m main rectify 1990-01-01 12:00 Moscow "event_date"`
- **Effort**: 10 min

### 7. Update devils command ☐

- [ ] Add `normalize_input()` before calculation
- [ ] Update signature: add `tz: str | None = None` parameter
- [ ] Add `input_metadata` to result
- [ ] Fix Pydantic deprecation
- [ ] **Test**: `python -m main devils 1990-01-01 12:00 Moscow`
- **Effort**: 10 min

### 8. Update and expand ALIASES ☐

- [ ] Add Lipetsk (already done)
- [ ] Add other Russian cities (St. Petersburg, etc.)
- [ ] Add major world cities (20-30 cities)
- [ ] Verify timezone names (all are valid IANA zones)
- [ ] Add both English and Cyrillic variants where applicable
- [ ] **Test**: `python -c "from input_pipeline.resolver_city import ALIASES; print(len(ALIASES))"`
- **Effort**: 15 min

---

## PHASE 2: TESTING & VALIDATION (Week 1 - ~1.5 hours)

### 9. Update test_input_pipeline.py ☐

- [ ] Add tests for new aliases
- [ ] Add test for UTC datetime validation in julian_day()
- [ ] Add test for direct coordinate passing to natal_calculation()
- [ ] Add integration test: normalize_input → natal_calculation
- [ ] **Run**: `python -m pytest test_input_pipeline.py -v`
- [ ] Verify all 15+ tests pass
- **Effort**: 30 min

### 10. Create test_main_commands.py ☐

- [ ] Test natal with basic input
- [ ] Test natal with European date format
- [ ] Test natal with Cyrillic place name
- [ ] Test natal with typo (fuzzy matching)
- [ ] Test natal with `--tz` override
- [ ] Test transit command
- [ ] Test solar command
- [ ] Test rectify command
- [ ] Test devils command
- [ ] Test relocate command with new cities
- [ ] **Run**: `python -m pytest test_main_commands.py -v`
- **Effort**: 45 min

### 11. Performance benchmarks ☐

- [ ] Measure natal_calculation() time for moscow (alias)
- [ ] Measure natal_calculation() time for london (geopy)
- [ ] Measure 2nd call to moscow (should be faster - cache)
- [ ] Record baseline vs optimized
- [ ] Document results in OPTIMIZATION_EXAMPLES.md
- **Effort**: 15 min

### 12. End-to-end smoke tests ☐

```bash
# Test all 6 commands work
python -m main natal 1990-01-01 12:00 Moscow
python -m main natal 01.01.1990 12:00 Moscow  # European format
python -m main transit 2025-01-15 12:00 Moscow
python -m main solar 2025-01-01 12:00 Moscow
python -m main rectify "1990-01-01" "12:00" "Moscow" "event"
python -m main devils 1990-01-01 12:00 Moscow
python -m main relocate Lipetsk
python -m main relocate London  # Geopy fallback
python -m main relocate Tokyo   # Geopy fallback
```

- [ ] All commands execute without error
- [ ] JSON output is valid
- [ ] Warnings are included where appropriate
- **Effort**: 10 min

---

## PHASE 3: DOCUMENTATION & CLEANUP (Week 1 - ~1 hour)

### 13. Update documentation ☐

- [ ] Update ARCHITECTURE.md with new signatures
- [ ] Update INPUT_PIPELINE.md with integration examples
- [ ] Create CLI_USAGE.md with examples for each command
- [ ] Add docstring examples to main.py
- [ ] Update README.md with new features (--tz, typo correction, etc.)
- **Effort**: 30 min

### 14. Update help text ☐

- [ ] Add help text to all commands in main.py
- [ ] Add examples to help
- [ ] Document --tz parameter
- [ ] Document explain and devils flags
- **Effort**: 10 min

### 15. Code review checklist ☐

- [ ] No Pydantic deprecation warnings
- [ ] No round-trip string conversions
- [ ] All commands use normalize_input()
- [ ] All commands pass UTC datetime to calculations
- [ ] All commands include warnings in results
- [ ] Cache is used in relocate_coords()
- [ ] Global cache singleton is working
- **Effort**: 10 min

---

## PHASE 4: OPTIONAL ENHANCEMENTS (Week 2)

### 16. Create InputContext class ☐

- [ ] Create input_pipeline/context.py
- [ ] Implement InputContext dataclass
- [ ] Add `from_normalized()` factory method
- [ ] Add `to_metadata_dict()` serialization
- [ ] Update main.py to use InputContext
- [ ] Add tests for InputContext
- **Effort**: 60 min

### 17. Implement global cache singleton ☐

- [ ] Create get_global_cache() function
- [ ] Update resolve_city() callers to use it
- [ ] Update relocate_coords() to use it
- [ ] Add --clear-cache CLI option
- [ ] Test cache persistence across commands
- **Effort**: 30 min

### 18. Add verbose/debug mode ☐

- [ ] Add `--verbose` flag to CLI commands
- [ ] Output parsing details when --verbose
- [ ] Output geopy results when --verbose
- [ ] Output cache hit/miss info when --verbose
- **Effort**: 20 min

### 19. Expand ALIASES with 50+ cities ☐

- [ ] Create ALIASES_EXTENDED with more cities
- [ ] Load from external JSON file instead of hardcoded
- [ ] Allow user-defined aliases via config file
- [ ] Add validation for latitude/longitude/timezone
- **Effort**: 45 min

---

## DONE CRITERIA

### For Phase 1 to be DONE:

- ✅ All 6 commands use normalize_input()
- ✅ All commands pass datetime/lat/lon to calculations
- ✅ No string round-trip conversions
- ✅ All 15 input_pipeline tests pass
- ✅ All 6 commands have smoke tests passing
- ✅ No Pydantic deprecation warnings
- ✅ Performance improvement of 5-10x for cached cities

### For Phase 2 to be DONE:

- ✅ InputContext class created and integrated
- ✅ Global cache singleton working
- ✅ 40+ cities in ALIASES
- ✅ End-to-end tests for all commands
- ✅ Performance benchmarks documented

### For Phase 3 to be DONE:

- ✅ All documentation updated
- ✅ CLI help text clear and complete
- ✅ Code review checklist passed
- ✅ No technical debt remaining

---

## PRIORITY & TIME ESTIMATE

### CRITICAL (Must do):

- Phase 1: All 15 tasks → 2.5 hours
- Phase 2: Tests 9-12 → 1.5 hours
- **Total CRITICAL**: 4 hours

### HIGH PRIORITY (Should do):

- Phase 3: Documentation 13-15 → 1 hour
- **Total HIGH**: 1 hour

### NICE TO HAVE (Can do):

- Phase 4: Optional enhancements 16-19 → 2-3 hours
- **Total OPTIONAL**: 2-3 hours

**TOTAL EFFORT FOR FULL OPTIMIZATION: 5-8 hours**

---

## SIGN-OFF

- [ ] Development complete (Phase 1+2)
- [ ] Testing complete (all smoke tests pass)
- [ ] Performance benchmarks documented
- [ ] Documentation updated
- [ ] Code review passed
- [ ] Ready for production deployment

**Date Started**: ****\_\_\_****
**Date Completed**: ****\_\_\_****
**Tested By**: ****\_\_\_****
**Approved By**: ****\_\_\_****
