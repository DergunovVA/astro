# Performance Monitoring Guide

Comprehensive guide for performance monitoring, regression detection, and CI/CD integration for the Astrology DSL system.

**Created:** 2025-02-16  
**Version:** 1.0  
**Status:** Production Ready

---

## Table of Contents

- [Overview](#overview)
- [Performance Thresholds](#performance-thresholds)
- [Baseline Management](#baseline-management)
- [Regression Testing](#regression-testing)
- [CI/CD Integration](#cicd-integration)
- [Local Development](#local-development)
- [Interpreting Results](#interpreting-results)
- [Troubleshooting](#troubleshooting)

---

## Overview

### Performance Monitoring System

The Astrology DSL performance monitoring system consists of:

1. **Performance Thresholds** ([config/performance_thresholds.yaml](../config/performance_thresholds.yaml))
   - Target, warning, and critical thresholds for all components
   - Based on Stage 2 Task 2.2 profiling results
   - Updated: 2025-02-16

2. **Benchmark Suite** ([tests/test_performance_dsl.py](../tests/test_performance_dsl.py))
   - 25 comprehensive benchmarks across Lexer, Parser, Evaluator
   - Saved baseline: `.benchmarks/stage2_baseline.json`

3. **Regression Tests** ([tests/test_performance_regression.py](../tests/test_performance_regression.py))
   - Automated regression detection
   - Critical threshold enforcement (CI/CD failures)
   - Throughput validation

### Current Performance Baseline

**Established:** 2025-02-16 (Stage 2 Task 2.2)

| Component      | Avg Time (μs) | Throughput (ops/s) | Status                          |
| -------------- | ------------- | ------------------ | ------------------------------- |
| **Lexer**      | 275.3         | 3,632              | ✅ **3.6x faster than target**  |
| **Parser**     | 403.3         | 2,480              | ✅ **12.4x faster than target** |
| **Evaluator**  | 311.8         | 3,207              | ✅ **32x faster than target**   |
| **End-to-End** | 446.8         | 2,238              | ✅ **112x faster than target**  |

**System Throughput:** 2,238 formulas/second  
**Caching Speedup:** 12.3x with AST caching

---

## Performance Thresholds

### Threshold Levels

Each component has three threshold levels:

1. **Target** - Optimal performance goal
2. **Warning** - Performance degradation alert (should investigate)
3. **Critical** - Maximum acceptable performance (CI/CD failure)

### Example: Lexer Simple Formula

```yaml
lexer:
  simple:
    current_avg: 13.0 # μs (microseconds)
    target: 30 # μs - Optimal goal
    warning: 50 # μs - Alert threshold
    critical: 100 # μs - Failure threshold
```

**Interpretation:**

- ✅ **< 30μs:** Excellent (beating target)
- ⚠️ **30-50μs:** Good (below warning)
- ⚠️ **50-100μs:** Degraded (warning threshold exceeded)
- ❌ **> 100μs:** Critical (CI/CD fails)

### All Thresholds

See [config/performance_thresholds.yaml](../config/performance_thresholds.yaml) for complete threshold definitions.

---

## Baseline Management

### Viewing Saved Baselines

```bash
# List all saved baselines
ls .benchmarks/Windows-CPython-3.13-64bit/

# View baseline details
cat .benchmarks/Windows-CPython-3.13-64bit/0001_stage2_baseline.json
```

### Comparing Against Baseline

```bash
# Run benchmarks and compare to baseline
pytest tests/test_performance_dsl.py --benchmark-only \
      --benchmark-compare=stage2_baseline \
      --benchmark-compare-fail=mean:10%

# Options:
#   --benchmark-compare=BASELINE_NAME  - Compare to named baseline
#   --benchmark-compare-fail=SPEC      - Fail if regression > threshold
#     Examples:
#       mean:10%  - Fail if mean slowdown > 10%
#       min:5%    - Fail if minimum time slowdown > 5%
#       max:20%   - Fail if maximum time slowdown > 20%
```

### Creating New Baseline

```bash
# Run benchmarks and save as new baseline
pytest tests/test_performance_dsl.py --benchmark-only \
      --benchmark-save=new_baseline_name

# ⚠️ IMPORTANT: Only create new baselines after:
#   1. Code review approval
#   2. Verification that performance improvements are real
#   3. Documentation of what changed
```

### Baseline Update Workflow

1. **Make performance improvements**
2. **Run regression tests**
   ```bash
   pytest tests/test_performance_regression.py --benchmark-only
   ```
3. **Compare to current baseline**
   ```bash
   pytest tests/test_performance_dsl.py --benchmark-only --benchmark-compare=stage2_baseline
   ```
4. **Create pull request with benchmark results**
5. **After approval, save new baseline**
   ```bash
   pytest tests/test_performance_dsl.py --benchmark-only --benchmark-save=stage3_optimization
   ```
6. **Commit new baseline to repository**
   ```bash
   git add .benchmarks/
   git commit -m "perf: Update performance baseline after Stage 3 optimizations"
   ```

---

## Regression Testing

### Running Regression Tests

```bash
# Run all regression tests
pytest tests/test_performance_regression.py --benchmark-only -v

# Run specific test class
pytest tests/test_performance_regression.py::TestLexerRegression --benchmark-only

# Run critical threshold tests only
pytest tests/test_performance_regression.py::TestCriticalThresholds --benchmark-only
```

### Regression Test Categories

#### 1. Component Regression Tests

**Lexer, Parser, Evaluator regression detection**

```bash
pytest tests/test_performance_regression.py::TestLexerRegression --benchmark-only
pytest tests/test_performance_regression.py::TestParserRegression --benchmark-only
pytest tests/test_performance_regression.py::TestEvaluatorRegression --benchmark-only
```

**Tests check:** Current performance vs warning thresholds

#### 2. End-to-End Regression Tests

**Full pipeline performance validation**

```bash
pytest tests/test_performance_regression.py::TestEndToEndRegression --benchmark-only
```

**Tests check:** Complete Lexer → Parser → Evaluator pipeline

#### 3. Critical Threshold Tests

**CI/CD failure triggers (severe regressions)**

```bash
pytest tests/test_performance_regression.py::TestCriticalThresholds --benchmark-only
```

**Tests check:** Critical thresholds that MUST NOT be exceeded

#### 4. Throughput Regression Tests

**System-wide throughput validation**

```bash
pytest tests/test_performance_regression.py::TestThroughputRegression --benchmark-only
```

**Tests check:** Batch processing performance

### Understanding Regression Results

#### ✅ Pass - No Regression

```
tests/test_performance_regression.py::TestLexerRegression::test_lexer_simple_regression PASSED
  Mean: 12.5μs < 50μs (warning threshold)
```

**Action:** None required, performance is good

#### ⚠️ Warning - Performance Degraded

```
tests/test_performance_regression.py::TestParserRegression::test_parser_medium_regression PASSED
  Mean: 95.0μs (warning: 92.5μs exceeded, critical: 250μs OK)
```

**Action:**

- Investigate what caused slowdown
- Review recent commits
- Consider optimization if trend continues

#### ❌ Critical - Build Failed

```
tests/test_performance_regression.py::TestCriticalThresholds::test_critical_e2e_complex FAILED
  Mean: 2150.0μs > 2000μs (CRITICAL THRESHOLD EXCEEDED)
```

**Action:**

- ❌ DO NOT MERGE this code
- Identify performance regression cause
- Fix or revert changes
- Re-run tests

---

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/performance.yml`:

```yaml
name: Performance Regression Tests

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  performance:
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.13
        uses: actions/setup-python@v4
        with:
          python-version: "3.13"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest-benchmark pyyaml

      - name: Run performance regression tests
        run: |
          pytest tests/test_performance_regression.py --benchmark-only -v

      - name: Compare to baseline (informational)
        run: |
          pytest tests/test_performance_dsl.py --benchmark-only --benchmark-compare=stage2_baseline
        continue-on-error: true # Don't fail build, just show comparison

      - name: Generate HTML report
        run: |
          pytest tests/test_performance_dsl.py --benchmark-only --benchmark-histogram
        if: always()

      - name: Upload benchmark results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: |
            .benchmarks/
            benchmark-*.svg
        if: always()
```

### CI/CD Configuration Options

Edit [config/performance_thresholds.yaml](../config/performance_thresholds.yaml):

```yaml
ci_cd:
  fail_on_critical: true # ✅ Fail build if critical threshold exceeded
  warn_on_warning: true # ⚠️ Show warning if warning threshold exceeded
  benchmark_on_pr: true # Run benchmarks on pull requests
  compare_to_baseline: true # Always compare to saved baseline
  save_new_baseline: false # Don't auto-save (manual approval required)
```

### Pull Request Checks

**Recommended PR workflow:**

1. **Developer runs benchmarks locally**

   ```bash
   pytest tests/test_performance_regression.py --benchmark-only
   ```

2. **CI runs regression tests on PR**
   - ✅ Pass: No critical thresholds exceeded
   - ⚠️ Warning: Performance degradation detected (log warning)
   - ❌ Fail: Critical threshold exceeded (block merge)

3. **Reviewer checks benchmark comparison**

   ```bash
   # CI outputs comparison table
   Compare to baseline:
     test_lexer_simple: 12.5μs vs 13.0μs (3.8% faster ✅)
     test_parser_complex: 165.0μs vs 155.9μs (5.8% slower ⚠️)
   ```

4. **Decision:**
   - Small regressions (<10%): Review and approve if justified
   - Large regressions (>20%): Request optimization
   - Critical failures: Block merge until fixed

---

## Local Development

### Quick Start

```bash
# 1. Install dependencies
pip install pytest-benchmark pyyaml

# 2. Run performance tests
pytest tests/test_performance_dsl.py --benchmark-only

# 3. Run regression tests
pytest tests/test_performance_regression.py --benchmark-only

# 4. Compare to baseline
pytest tests/test_performance_dsl.py --benchmark-only --benchmark-compare=stage2_baseline
```

### Before Committing Code

```bash
# Run full test suite including performance
pytest tests/ -v

# Check for performance regressions
pytest tests/test_performance_regression.py --benchmark-only -v

# If all pass: ✅ Safe to commit
```

### Investigating Slowdowns

#### 1. Identify Slow Component

```bash
# Run component-specific tests
pytest tests/test_performance_regression.py::TestLexerRegression --benchmark-only
pytest tests/test_performance_regression.py::TestParserRegression --benchmark-only
pytest tests/test_performance_regression.py::TestEvaluatorRegression --benchmark-only
```

#### 2. Profile Specific Formula

```bash
# Use profiling tool
python tools/profile_dsl.py

# Check generated reports
cat profiles/performance_summary.md
```

#### 3. Compare Detailed Metrics

```bash
# Generate detailed benchmark comparison
pytest tests/test_performance_dsl.py --benchmark-only \
      --benchmark-compare=stage2_baseline \
      --benchmark-verbose
```

---

## Interpreting Results

### Benchmark Output Explained

```
tests/test_performance_dsl.py::test_lexer_simple_property PASSED
------------------------------------------------------------------------
Name (time in us)                    Min        Max      Mean    StdDev
test_lexer_simple_property         4.70    2098.70     12.99     63.43
------------------------------------------------------------------------
```

**Metrics:**

- **Min:** Fastest execution time (best case)
- **Max:** Slowest execution time (worst case)
- **Mean:** Average execution time (**primary metric**)
- **StdDev:** Standard deviation (consistency indicator)

**Good indicators:**

- ✅ Low mean (fast average)
- ✅ Low StdDev (consistent performance)
- ✅ Min close to mean (no warm-up penalty)

**Warning signs:**

- ⚠️ High StdDev (inconsistent, maybe GC issues)
- ⚠️ Large max (outliers indicate problems)
- ⚠️ Mean significantly higher than min (warm-up issues)

### Comparison Output

```
Comparing against: stage2_baseline (0001_stage2_baseline.json)
-------------------------------------------------------------------
Name                    Before       Now       Change    % Change
test_lexer_simple      13.00μs    12.50μs     -0.50μs      -3.8%  ✅
test_parser_complex   155.90μs   165.00μs     +9.10μs      +5.8%  ⚠️
-------------------------------------------------------------------
```

**Interpretation:**

- **Negative change:** Performance improvement ✅
- **Small positive change (<10%):** Acceptable variation
- **Medium positive change (10-20%):** Investigate ⚠️
- **Large positive change (>20%):** Regression, fix required ❌

### Threshold Warning Levels

```yaml
# From config/performance_thresholds.yaml

lexer:
  simple:
    target: 30 # Goal to beat
    warning: 50 # Investigation threshold
    critical: 100 # Failure threshold
```

**Status interpretation:**

| Current Time | Status       | Action                            |
| ------------ | ------------ | --------------------------------- |
| 12.5μs       | ✅ Excellent | None - beating target by 2.4x     |
| 28.0μs       | ✅ Good      | None - under target               |
| 45.0μs       | ⚠️ Warning   | Investigate - approaching warning |
| 65.0μs       | ⚠️ Degraded  | Optimize - warning exceeded       |
| 120.0μs      | ❌ Critical  | **FIX IMMEDIATELY** - build fails |

---

## Troubleshooting

### Problem: Inconsistent Benchmark Results

**Symptoms:** High standard deviation, wildly varying times

**Causes:**

- Background processes consuming CPU
- Insufficient warmup rounds
- Garbage collection interference

**Solutions:**

```bash
# 1. Close unnecessary applications

# 2. Increase benchmark rounds
pytest tests/test_performance_dsl.py --benchmark-only --benchmark-min-rounds=100

# 3. Disable GC during benchmarks
pytest tests/test_performance_dsl.py --benchmark-only --benchmark-disable-gc

# 4. Run multiple times and average
for i in {1..5}; do
  pytest tests/test_performance_dsl.py --benchmark-only --benchmark-autosave
done
```

### Problem: Baseline Comparison Fails

**Symptoms:** `--benchmark-compare` can't find baseline

**Causes:**

- Baseline not saved
- Wrong baseline name
- Different Python version

**Solutions:**

```bash
# 1. List available baselines
ls .benchmarks/Windows-CPython-3.13-64bit/

# 2. Verify baseline exists
cat .benchmarks/Windows-CPython-3.13-64bit/0001_stage2_baseline.json

# 3. Use correct baseline name (number + name)
pytest tests/test_performance_dsl.py --benchmark-only --benchmark-compare=0001_stage2_baseline

# 4. If missing, create baseline
pytest tests/test_performance_dsl.py --benchmark-only --benchmark-save=stage2_baseline
```

### Problem: Tests Pass Locally, Fail in CI

**Symptoms:** Regression tests pass on dev machine, fail in GitHub Actions

**Causes:**

- Different hardware (CI runners slower)
- Different Python version
- Missing dependencies

**Solutions:**

1. **Adjust CI thresholds** (temporarily):

   ```yaml
   # config/performance_thresholds.yaml
   ci_cd:
     fail_on_critical: true # Keep this
     warn_on_warning: false # Disable warnings in CI
   ```

2. **Use platform-specific baselines:**

   ```bash
   # Save CI-specific baseline
   pytest --benchmark-save=stage2_baseline_ci
   ```

3. **Run tests in CI-like environment:**
   ```bash
   # Use Docker with same Python version
   docker run -it python:3.13 /bin/bash
   ```

### Problem: Performance Suddenly Degraded

**Symptoms:** All tests slower than before, no clear cause

**Investigation steps:**

1. **Check recent commits:**

   ```bash
   git log --oneline -10
   ```

2. **Profile specific components:**

   ```bash
   python tools/profile_dsl.py
   cat profiles/performance_summary.md
   ```

3. **Compare to previous baseline:**

   ```bash
   pytest tests/test_performance_dsl.py --benchmark-only \
         --benchmark-compare=stage2_baseline \
         --benchmark-verbose
   ```

4. **Bisect to find regression:**
   ```bash
   git bisect start
   git bisect bad HEAD
   git bisect good <last-known-good-commit>
   # Git will checkout commits, run tests at each:
   pytest tests/test_performance_regression.py --benchmark-only
   git bisect good  # or git bisect bad
   ```

---

## Performance Optimization Workflow

### 1. Identify Bottleneck

```bash
# Run profiler
python tools/profile_dsl.py

# Check detailed profile
python -m pstats profiles/end_to_end_profile.txt
>>> sort cumtime
>>> stats 10
```

### 2. Create Optimization Hypothesis

Example findings from profiling:

- Lexer: `read_identifier()` takes 0.814s (string operations)
- Parser: Recursive calls take 2.029s (parse_term)
- Evaluator: Dict lookups take 0.3s (chart_data access)

### 3. Implement Optimization

Example: Add AST caching

```python
# src/dsl/parser.py
class Parser:
    def __init__(self):
        self._ast_cache = {}  # formula -> AST

    def parse(self, formula: str):
        if formula in self._ast_cache:
            return self._ast_cache[formula]  # Cache hit!

        ast = self._parse_impl(formula)
        self._ast_cache[formula] = ast
        return ast
```

### 4. Measure Improvement

```bash
# Run benchmarks
pytest tests/test_performance_dsl.py --benchmark-only --benchmark-save=after_caching

# Compare before/after
pytest tests/test_performance_dsl.py --benchmark-only \
      --benchmark-compare=stage2_baseline
      --benchmark-compare=after_caching
```

### 5. Validate No Regression

```bash
# Run regression tests
pytest tests/test_performance_regression.py --benchmark-only

# Run full test suite
pytest tests/ -v
```

### 6. Update Documentation

```python
# Update config/performance_thresholds.yaml if targets change
# Create docs/STAGE_3_OPTIMIZATION.md documenting changes
# Update baseline after code review
```

---

## Monitoring Dashboard (Future)

### Planned Features

- **Grafana Dashboard:** Real-time performance metrics
- **Prometheus Integration:** Historical performance tracking
- **Alerts:** Slack/email notifications on regressions
- **Automated Reports:** Weekly performance summaries

### Current Workaround

```bash
# Generate HTML performance report
pytest tests/test_performance_dsl.py --benchmark-only --benchmark-histogram

# Open in browser
start benchmark-*.svg  # Windows
open benchmark-*.svg   # macOS
xdg-open benchmark-*.svg  # Linux
```

---

## Best Practices

### ✅ DO

- Run regression tests before every commit
- Compare to baseline when optimizing
- Document performance improvements in PRs
- Update thresholds after major optimizations
- Save baselines after code review approval
- Profile before optimizing (measure first!)

### ❌ DON'T

- Auto-update baselines in CI (manual approval only)
- Ignore warning threshold violations
- Optimize without measuring
- Commit code that fails critical thresholds
- Update thresholds to "fix" regressions (fix the code!)
- Skip regression tests "to save time"

---

## References

- **Profiling Results:** [profiles/performance_summary.md](../profiles/performance_summary.md)
- **Task 2.2 Report:** [docs/STAGE_2_TASK_2.2_COMPLETED.md](./STAGE_2_TASK_2.2_COMPLETED.md)
- **Benchmark Suite:** [tests/test_performance_dsl.py](../tests/test_performance_dsl.py)
- **Regression Tests:** [tests/test_performance_regression.py](../tests/test_performance_regression.py)
- **Thresholds Config:** [config/performance_thresholds.yaml](../config/performance_thresholds.yaml)
- **pytest-benchmark docs:** https://pytest-benchmark.readthedocs.io/

---

## Support

**Questions or issues?**

1. Check [Troubleshooting](#troubleshooting) section
2. Review [profiling results](../profiles/performance_summary.md)
3. Run `python tools/profile_dsl.py` for detailed analysis
4. Check [Task 2.2 completion report](./STAGE_2_TASK_2.2_COMPLETED.md)

---

**Created:** 2025-02-16  
**Last Updated:** 2025-02-16  
**Version:** 1.0  
**Status:** ✅ Production Ready
