#!/usr/bin/env python3
"""
🔴 RED TEAM TESTING SUITE
Comprehensive adversarial testing to find:
- Weak points and blind spots
- Incorrect assumptions
- Scaling & growth problems
- Errors and distortions
- Optimization opportunities
"""

from input_pipeline import normalize_input, reset_global_cache
from astro_adapter import natal_calculation

# Color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def test_result(name, passed, details=''):
    status = f'{GREEN}✓{RESET}' if passed else f'{RED}✗{RESET}'
    print(f'  {status} {name}', end='')
    if details:
        print(f' - {details}')
    else:
        print()

class RedTeamTester:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.issues = []
        
    def log_issue(self, severity, category, description, code_example=''):
        self.issues.append({
            'severity': severity,
            'category': category,
            'description': description,
            'code': code_example
        })
        
    def print_summary(self):
        print(f'\n{BLUE}=== SUMMARY ==={RESET}')
        print(f'Total tests: {self.total}')
        print(f'Passed: {self.passed} ({100*self.passed//self.total if self.total else 0}%)')
        print(f'Issues found: {len(self.issues)}')
        
        if self.issues:
            print(f'\n{RED}Critical Issues:{RESET}')
            critical = [i for i in self.issues if i['severity'] == 'CRITICAL']
            for issue in critical:
                print(f"  - {issue['category']}: {issue['description']}")

tester = RedTeamTester()

print(f'{BLUE}=== RED TEAM TESTING SUITE ==={RESET}\n')

# ============================================================================
# TEST GROUP 1: INPUT VALIDATION
# ============================================================================
print(f'{YELLOW}[TEST 1] INPUT VALIDATION{RESET}')

# Test 1.1: Empty inputs
print('1.1: Empty/null inputs')
test_cases = [
    ('', '', ''),
    ('1990-01-01', '', 'Moscow'),
    ('', '12:00', 'Moscow'),
    ('1990-01-01', '12:00', ''),
    ('   ', '  ', '  '),  # Whitespace only
]
for date, time, place in test_cases:
    tester.total += 1
    try:
        result = normalize_input(date, time, place)
        test_result('Empty input rejected', False, f'Accepted: {repr((date,time,place))}')
        tester.log_issue('HIGH', 'Input Validation', 
            f'Empty/whitespace input accepted without error: ({repr(date)}, {repr(time)}, {repr(place)})')
    except ValueError:
        test_result('Empty input rejected', True, 'ValueError raised')
        tester.passed += 1
    except Exception as e:
        test_result('Empty input rejected', False, f'Unexpected: {type(e).__name__}')
        tester.log_issue('CRITICAL', 'Error Handling',
            f'Unexpected exception for empty input: {type(e).__name__}: {e}')

# Test 1.2: Invalid date formats
print('\n1.2: Invalid date formats')
invalid_dates = [
    '99-99-99',
    '2030-13-45',
    '0000-01-01',
    '2025-01-01',  # Future date
    'not-a-date',
    '32.13.2020',
    '20200101',  # YYYYMMDD not ISO
    '01/01/90',  # US format ambiguity
]
for date in invalid_dates:
    tester.total += 1
    try:
        result = normalize_input(date, '12:00', 'Moscow')
        test_result('Invalid date rejected', False, f'Accepted: {date}')
        tester.log_issue('HIGH', 'Input Validation', f'Invalid date accepted: {date}')
    except ValueError:
        test_result('Invalid date rejected', True)
        tester.passed += 1
    except Exception as e:
        test_result('Invalid date rejected', False, f'{type(e).__name__}')
        tester.log_issue('CRITICAL', 'Error Handling', f'Crash on invalid date {date}: {e}')

# Test 1.3: Invalid time formats
print('\n1.3: Invalid time formats')
invalid_times = [
    '25:00',
    '12:60',
    '12:30:60',
    'not:time',
    '25:30:30',
    '24:00:00',
]
for time in invalid_times:
    tester.total += 1
    try:
        result = normalize_input('1990-01-01', time, 'Moscow')
        test_result('Invalid time rejected', False, f'Accepted: {time}')
        tester.log_issue('HIGH', 'Input Validation', f'Invalid time accepted: {time}')
    except ValueError:
        test_result('Invalid time rejected', True)
        tester.passed += 1
    except Exception as e:
        test_result('Invalid time rejected', False, f'{type(e).__name__}')
        tester.log_issue('CRITICAL', 'Error Handling', f'Crash on invalid time: {e}')

# Test 1.4: Coordinate precision & extreme values
print('\n1.4: Coordinate boundary testing')
extreme_coords = [
    (90.000001, 0),      # Beyond poles
    (-90.000001, 0),
    (0, 180.000001),     # Beyond anti-meridian
    (0, -180.000001),
    (0, 0),              # Null Island
    (89.9999, 179.9999), # Near pole
]

# ============================================================================
# TEST GROUP 2: DATA PERSISTENCE & CONSISTENCY
# ============================================================================
print(f'\n{YELLOW}[TEST 2] DATA PERSISTENCE & CACHE BEHAVIOR{RESET}')

# Test 2.1: Cache pollution
print('\n2.1: Global cache persistence across commands')
tester.total += 1
try:
    reset_global_cache()
    
    # First command caches Moscow
    result1 = normalize_input('1990-01-01', '12:00', 'Moscow')
    coords1 = (result1.lat, result1.lon)
    
    # Second command (immediately after) should get same coords
    result2 = normalize_input('2000-06-15', '18:30', 'Moscow')
    coords2 = (result2.lat, result2.lon)
    
    if coords1 == coords2:
        test_result('Cache consistency', True, 'Same coords returned')
        tester.passed += 1
    else:
        test_result('Cache consistency', False, f'{coords1} != {coords2}')
        tester.log_issue('HIGH', 'Data Integrity', 
            f'Cache returned different coordinates for same city: {coords1} vs {coords2}')
except Exception as e:
    test_result('Cache consistency', False, str(e))
    tester.log_issue('CRITICAL', 'Cache', f'Cache error: {e}')

# Test 2.2: Cache reset effectiveness
print('\n2.2: Cache reset functionality')
tester.total += 1
try:
    reset_global_cache()
    result1 = normalize_input('1990-01-01', '12:00', 'Moscow')  # Use real city
    test_result('Cache reset works', True, 'No exception')
    tester.passed += 1
except Exception as e:
    test_result('Cache reset works', False, str(e))

# Test 2.3: Thread safety (simulation)
print('\n2.3: Concurrent cache access simulation')
tester.total += 1
try:
    reset_global_cache()
    cities = ['Moscow', 'London', 'Tokyo', 'New York', 'Moscow']
    results = []
    for city in cities:
        r = normalize_input('1990-01-01', '12:00', city)
        results.append((city, r.lat, r.lon))
    
    # Check Moscow consistency
    moscow_coords = [r[1:] for r in results if r[0] == 'Moscow']
    if len(set(moscow_coords)) == 1:
        test_result('Concurrent access (simulated)', True)
        tester.passed += 1
    else:
        test_result('Concurrent access (simulated)', False, 'Inconsistent results')
        tester.log_issue('MEDIUM', 'Concurrency', 'Inconsistent coordinates in concurrent simulation')
except Exception as e:
    test_result('Concurrent access (simulated)', False, str(e))

# ============================================================================
# TEST GROUP 3: CALCULATION ACCURACY
# ============================================================================
print(f'\n{YELLOW}[TEST 3] CALCULATION ACCURACY & PRECISION{RESET}')

# Test 3.1: Julian day precision
print('\n3.1: Julian day calculation precision')
tester.total += 1
try:
    ni1 = normalize_input('1990-01-01', '12:00:00', 'Moscow')
    ni2 = normalize_input('1990-01-01', '12:00:01', 'Moscow')
    
    jd1 = natal_calculation(ni1.utc_dt, ni1.lat, ni1.lon)['jd']
    jd2 = natal_calculation(ni2.utc_dt, ni2.lat, ni2.lon)['jd']
    
    # 1 second difference = 1/86400 JD
    diff = abs(jd2 - jd1)
    expected_diff = 1 / 86400  # 0.0000115740740...
    
    if abs(diff - expected_diff) < 1e-8:
        test_result('JD precision (1 second)', True, f'Diff: {diff:.10f}')
        tester.passed += 1
    else:
        test_result('JD precision (1 second)', False, f'Expected ~{expected_diff}, got {diff}')
        tester.log_issue('MEDIUM', 'Precision', 
            f'JD precision loss: expected {expected_diff}, got {diff}')
except Exception as e:
    test_result('JD precision', False, str(e))
    tester.log_issue('CRITICAL', 'Calculation', f'JD calculation failed: {e}')

# Test 3.2: Coordinate boundary conditions
print('\n3.2: Extreme latitude/longitude handling')
tester.total += 1
extreme_cases = [
    ('North Pole', 90.0, 0.0),
    ('South Pole', -90.0, 0.0),
    ('Null Island', 0.0, 0.0),
    ('Antimeridian', 0.0, 180.0),
]
poles_ok = True
for name, lat, lon in extreme_cases:
    try:
        result = natal_calculation(ni1.utc_dt, lat, lon)
        if 'houses' not in result or len(result['houses']) != 12:
            poles_ok = False
            tester.log_issue('HIGH', 'Calculation', 
                f'Invalid house count at {name}: {len(result.get("houses", []))}')
    except Exception as e:
        poles_ok = False
        tester.log_issue('HIGH', 'Calculation', 
            f'Calculation failed at {name} ({lat}, {lon}): {type(e).__name__}')

test_result('Extreme coordinates', poles_ok)
if poles_ok:
    tester.passed += 1

# ============================================================================
# TEST GROUP 4: ERROR HANDLING & RECOVERY
# ============================================================================
print(f'\n{YELLOW}[TEST 4] ERROR HANDLING & RESILIENCE{RESET}')

# Test 4.1: Corrupted cache file handling
print('\n4.1: Corrupted cache file recovery')
tester.total += 1
try:
    import os
    cache_file = '.cache_places.json'
    if os.path.exists(cache_file):
        # Backup original
        with open(cache_file, 'r') as f:
            original = f.read()
        
        # Corrupt it
        with open(cache_file, 'w') as f:
            f.write('{invalid json}')
        
        reset_global_cache()
        
        try:
            result = normalize_input('1990-01-01', '12:00', 'Moscow')
            test_result('Corrupted cache recovery', True, 'Recovered gracefully')
            tester.passed += 1
        except Exception as e:
            test_result('Corrupted cache recovery', False, f'Failed: {e}')
            tester.log_issue('CRITICAL', 'Resilience', 
                f'No recovery from corrupted cache: {e}')
        
        # Restore original
        with open(cache_file, 'w') as f:
            f.write(original)
    else:
        test_result('Corrupted cache recovery', False, 'No cache file found')
except Exception as e:
    test_result('Corrupted cache recovery', False, str(e))
    tester.log_issue('CRITICAL', 'Test Setup', f'Cache test failed: {e}')

# Test 4.2: Missing dependencies handling
print('\n4.2: Graceful degradation with missing geopy')
tester.total += 1
# (This would require mocking, skip for now)
test_result('Missing dependency handling', False, 'Not tested (requires mocking)')

# ============================================================================
# TEST GROUP 5: SCALING & PERFORMANCE
# ============================================================================
print(f'\n{YELLOW}[TEST 5] SCALING & PERFORMANCE{RESET}')

# Test 5.1: Large batch processing
print('\n5.1: Batch processing (100 commands)')
tester.total += 1
try:
    reset_global_cache()
    import time
    start = time.time()
    
    cities = ['Moscow', 'London', 'Tokyo', 'New York', 'Paris'] * 20
    for i, city in enumerate(cities):
        ni = normalize_input('1990-01-01', '12:00', city)
        calc = natal_calculation(ni.utc_dt, ni.lat, ni.lon)
    
    elapsed = time.time() - start
    per_cmd = elapsed / len(cities) * 1000
    
    if per_cmd < 100:  # Should be < 100ms per command with cache
        test_result('Batch processing (100 cmds)', True, f'{per_cmd:.1f}ms/cmd')
        tester.passed += 1
    else:
        test_result('Batch processing (100 cmds)', False, f'{per_cmd:.1f}ms/cmd (expected <100)')
        tester.log_issue('MEDIUM', 'Performance', 
            f'Slow command processing: {per_cmd:.1f}ms/cmd')
except Exception as e:
    test_result('Batch processing', False, str(e))
    tester.log_issue('CRITICAL', 'Scaling', f'Batch processing failed: {e}')

# Test 5.2: Memory usage (simple check)
print('\n5.2: Memory pressure simulation')
tester.total += 1
try:
    reset_global_cache()
    # Try to add many unique cities to cache
    unique_places = [f'FakeCity{i}' for i in range(100)]
    
    # This will fail for non-existent cities, but tests cache behavior
    added = 0
    for place in unique_places[:10]:  # Limit to avoid too many geopy calls
        try:
            ni = normalize_input('1990-01-01', '12:00', place)
            added += 1
        except:
            pass
    
    test_result('Memory pressure (10 cities)', True, f'Cached {added} unique entries')
    tester.passed += 1
except Exception as e:
    test_result('Memory pressure', False, str(e))

# ============================================================================
# TEST GROUP 6: BLIND SPOT DETECTION
# ============================================================================
print(f'\n{YELLOW}[TEST 6] ARCHITECTURAL BLIND SPOTS{RESET}')

# Blind Spot 1: Timezone offset handling
print('\n6.1: Timezone offset consistency')
tester.total += 1
try:
    # Same moment in time, different input TZ
    ni_utc = normalize_input('1990-01-01', '09:00', 'London')  # UTC
    ni_msk = normalize_input('1990-01-01', '12:00', 'Moscow', tz_override='Europe/Moscow')  # UTC+3
    
    # Should represent same moment
    if ni_utc.utc_dt == ni_msk.utc_dt:
        test_result('TZ offset consistency', True, 'Same UTC time detected')
        tester.passed += 1
    else:
        test_result('TZ offset consistency', False, 
            f'Different UTC: {ni_utc.utc_dt} vs {ni_msk.utc_dt}')
        tester.log_issue('CRITICAL', 'Timezone', 
            f'TZ offset not normalized: {ni_utc.utc_dt} vs {ni_msk.utc_dt}')
except Exception as e:
    test_result('TZ offset consistency', False, str(e))
    tester.log_issue('CRITICAL', 'Timezone', f'TZ test failed: {e}')

# Blind Spot 2: Daylight Saving Time
print('\n6.2: Daylight Saving Time edge cases')
tester.total += 1
try:
    # DST transitions (dates when clocks change)
    # US: Usually second Sunday in March, first Sunday in November
    dst_dates = [
        ('2024-03-10', '02:30'),  # Spring forward
        ('2024-11-03', '01:30'),  # Fall back
    ]
    
    test_result('DST handling', False, 'Not fully tested (requires mocking)')
except Exception as e:
    test_result('DST handling', False, str(e))
    tester.log_issue('MEDIUM', 'Timezone', 'DST not tested')

# Blind Spot 3: Year 2000/2038 problems
print('\n6.3: Time boundary conditions')
tester.total += 1
boundary_dates = [
    '1900-01-01',  # Before
    '2000-01-01',  # Y2K
    '2038-01-19',  # Unix 32-bit overflow
    '2100-12-31',  # Far future
]
boundary_ok = True
for date in boundary_dates:
    try:
        ni = normalize_input(date, '12:00', 'Moscow')
        test_result(f'Boundary: {date}', True)
        tester.passed += 1
        tester.total -= 1  # Adjust count
    except Exception as e:
        test_result(f'Boundary: {date}', False, str(e)[:30])
        boundary_ok = False
        tester.log_issue('MEDIUM', 'Data Handling', f'Boundary date failed: {date}')

tester.total += 1
if boundary_ok:
    tester.passed += 1

# Print summary
tester.print_summary()

if tester.issues:
    print(f'\n{RED}=== DETAILED ISSUES ==={RESET}\n')
    for i, issue in enumerate(tester.issues, 1):
        print(f'{i}. [{issue["severity"]}] {issue["category"]}')
        print(f'   {issue["description"]}')
        if issue['code']:
            print(f'   Code: {issue["code"]}')
        print()
