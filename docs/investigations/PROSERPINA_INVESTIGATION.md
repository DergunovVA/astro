# Proserpina Analysis - Swiss Ephemeris ID 57
# Based on user report from online calculators

## Problem

**Proserpina (ID 57)** in Swiss Ephemeris requires `seorbel.txt` ephemeris file.
Standard pyswisseph installation doesn't include this file.

## User Report (08.01.1982, Saratov 13:40)

According to online calculators:
- **Pluto**: 26° Libra
- **Proserpina**: 29° Libra

Our verification:
- **Pluto (Swiss Eph)**: 26.80° Libra ✅ (matches within 1°)
- **Proserpina ID 57**: ERROR - no ephemeris file ❌

## Available Alternatives in Swiss Ephemeris

Checked all fictitious bodies (ID 40-70) for position near 29° Libra:

| ID | Name | Position | Distance from 29° Libra |
|---|---|---|---|
| 47 | **Poseidon** | 25.90° Libra | 3.10° |
| 44 | Apollon | 10.08° Libra | 18.92° |
| 53 | Adams | 7.99° Libra | 21.01° |
| 48 | Transpluto | 18.96° Leo | ~68° |

**Closest match: Poseidon (ID 47)** - 25.90° Libra

Difference from online calculator: **3.10°**

## Possible Explanations

### 1. Different Ephemeris Sources
Online calculators might use:
- Different orbital elements for hypothetical planets
- Older ephemeris versions
- Proprietary calculations

### 2. Proserpina Variants
There are multiple "Proserpina" theories in astrology:
- **Wemyss Proserpina** (classical)
- **Sevin Proserpina** (French school)
- **Hamburg School version**
- **Swiss Ephemeris Proserpina** (ID 57, requires seorbel.txt)

Each uses different orbital elements = different positions!

### 3. Poseidon ≈ Proserpina?
In some astrological traditions:
- Hamburg School uses **Poseidon** (ID 47)
- Some astrologers conflate Poseidon with Proserpina
- Both relate to underworld/transformation themes

## Solutions

### Option 1: Download seorbel.txt (RECOMMENDED)
```powershell
# Download Proserpina ephemeris from Swiss Ephemeris
$url = "https://www.astro.com/ftp/swisseph/ephe/seorbel.txt"
$destination = "C:\sweph\ephe\seorbel.txt"

# Create directory if not exists
New-Item -ItemType Directory -Force -Path "C:\sweph\ephe"

# Download file
Invoke-WebRequest -Uri $url -OutFile $destination

# Set ephemeris path in Python
python -c "import swisseph as swe; swe.set_ephe_path('C:/sweph/ephe'); result = swe.calc_ut(swe.julday(1982,1,8,9.667), 57); print(f'Proserpina: {result[0][0]}')"
```

### Option 2: Use Poseidon (ID 47) as proxy
**Pros:**
- Available in standard installation
- Close to reported position (3° difference)
- Part of Hamburg School system

**Cons:**
- Not exactly "Proserpina"
- 3° discrepancy needs explanation

### Option 3: Implement custom ephemeris
Calculate Proserpina using known orbital elements from astrology literature.

## Current Implementation Status

**WRONG PLANET USED:** Current code uses **Transpluto (ID 48)**
- Position: 18.96° Leo
- Distance from Pluto: 67.83°
- ❌ NOT Proserpina

## Next Steps

1. **URGENT:** Remove or replace Transpluto implementation
2. Try downloading seorbel.txt
3. If seorbel.txt works, verify position matches online calculators
4. If position still doesn't match, investigate which "Proserpina" version websites use
5. Document which variant is implemented

## URLs for Investigation

- https://eso3.com/horoscopes/natal/natal-chart/
- https://astro-online.ru/view.php

Check if these sites document their Proserpina calculation method.

## Technical Notes

```python
# Current wrong implementation
swe.calc_ut(jd, 48)  # Transpluto - 18.96° Leo ❌

# Should be (if seorbel.txt available)
swe.calc_ut(jd, 57)  # Proserpina - ~29° Libra ✅

# Or alternative
swe.calc_ut(jd, 47)  # Poseidon - 25.90° Libra ⚠️
```
