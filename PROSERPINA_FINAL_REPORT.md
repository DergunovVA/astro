# PROSERPINA INVESTIGATION - FINAL REPORT

## Summary

**Goal:** Find and implement Proserpina showing ~29° Libra for 08.01.1982 Saratov

**Result:** File seorbel.txt successfully downloaded, but Swiss Ephemeris Proserpina shows different position

---

## Comparison Table

| Source | Position for 08.01.1982 Saratov | Notes |
|--------|--------------------------------|-------|
| **Online calculators** | 29° Libra | User reported |
| **Pluto (reference)** | 26.80° Libra | ✅ Matches expected |
| **Proserpina ID 57** | 3.28° Scorpio | ❌ Does NOT match |
| **Poseidon ID 47** | 25.90° Libra | ⚠️ Close (3.1° diff) |

---

## Technical Details

### File Downloaded
- **Source:** `https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/seorbel.txt`
- **Size:** 6,063 bytes
- **Location:** `C:\sweph\ephe\seorbel.txt`
- **Status:** ✅ Downloaded and working

### Proserpina Definition in seorbel.txt
```
# Hypothetical planet Proserpina, data from Valentin Abramov
# see also http://www.geocities.ws/rognavaldre/proserpina.html
J1900,JDATE, 170.73, 79.225630, 0, 0, 0, 0, Proserpina #18
```

This is **Proserpina according to Valentin Abramov**.
Orbital elements: semi-axis 79.23 AU, eccentricity 0, etc.

---

## Analysis

### Why the Discrepancy?

There are **multiple "Proserpina" definitions** in astrology:

1. **Swiss Ephemeris Proserpina (ID 57)** - Valentin Abramov version
   - Position: 3.28° Scorpio (1982)
   - 6.48° from Pluto (close but wrong side)

2. **Hamburg School Poseidon (ID 47)**
   - Position: 25.90° Libra (1982)
   - Only 0.90° from Pluto
   - **Closest to online calculators**

3. **Other Proserpina versions** (not in Swiss Ephemeris):
   - Wemyss Proserpina
   - Sevin/Spica Proserpina
   - ISIS-Transpluto confusion

Online calculators likely use:
- **Poseidon** and call it "Proserpina" (common practice)
- OR custom orbital elements not in Swiss Ephemeris

---

## Recommendations

### Option 1: Use Poseidon (ID 47) as "Proserpina" ⭐ RECOMMENDED
**Pros:**
- Position 25.90° Libra matches online calculators within 3°
- Available in standard Swiss Ephemeris
- Part of Hamburg School system (widely accepted)
- Very close to Pluto (0.90° conjunction)

**Cons:**
- Technically "Poseidon", not "Proserpina"
- 3.1° difference from expected 29° Libra

**Implementation:**
```python
result = swe.calc_ut(jd, 47)  # Poseidon as "Proserpina"
```

**Documentation:** Note that this is Hamburg School Poseidon, commonly used as "Proserpina" in modern astrology.

---

### Option 2: Use Swiss Ephemeris Proserpina (ID 57)
**Pros:**
- Technically correct "Proserpina" per Swiss Ephemeris
- seorbel.txt now available
- Based on Valentin Abramov research

**Cons:**
- Position 3.28° Scorpio does NOT match online calculators
- May confuse users expecting 29° Libra
- Not standard in Western astrology

---

### Option 3: Provide Both
Let users choose:
- `--proserpina-mode=poseidon` (default, matches online calculators)
- `--proserpina-mode=abramov` (Swiss Ephemeris ID 57)

---

## Current Implementation Status

### ❌ WRONG: Current code uses ID 48 (ISIS)
```python
# src/modules/astro_adapter.py line 66
result = swe.calc_ut(jd, 48)  # This is ISIS, not Proserpina!
planets["Transpluto"] = float(result[0][0])
```

**Problems:**
- ID 48 = ISIS (18.96° Leo) - far from expected position
- Named "Transpluto" but comments say "Proserpina"
- Nomenclature confusion

---

## Proposed Fix

Replace ID 48 with ID 47 (Poseidon):

```python
# Proserpina (Hamburg School Poseidon)
# Commonly used as "Proserpina" in modern astrology
# Close to Pluto, represents transformation/underworld themes
try:
    result = swe.calc_ut(jd, 47)  # Poseidon
    planets["Proserpina"] = float(result[0][0])
except Exception:
    pass
```

Or keep seorbel.txt and use ID 57 (with documentation about difference).

---

## Verification Results

**For 08.01.1982 09:40 UTC (Saratov 13:40 local):**

```
Pluto:           26.80° Libra  ✅ verified
Poseidon (47):   25.90° Libra  (0.90° from Pluto)
Proserpina (57):  3.28° Scorpio (6.48° from Pluto)
ISIS (48):       18.96° Leo     (67.83° from Pluto) ❌ wrong
```

---

## Decision Required

**Which implementation should we use?**

1. ⭐ **Poseidon (ID 47)** - matches online calculators best
2. **Proserpina (ID 57)** - technically correct per Swiss Ephemeris
3. **Both with user option**
4. **None** - remove feature until clarified

---

## Files Created

- `C:\sweph\ephe\seorbel.txt` - Downloaded ephemeris file
- `download_seorbel.py` - Download script
- `test_all_bodies.py` - All bodies verification
- `check_proserpina_orbit.py` - Orbital movement check
- `PROSERPINA_INVESTIGATION.md` - This report

---

**Next Action:** Replace ID 48 with either ID 47 (Poseidon) or ID 57 (Proserpina) based on decision.
