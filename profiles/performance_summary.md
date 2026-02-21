# DSL Performance Profiling Report

**Date:** 2026-02-21 11:43:58  
**Stage:** 2 Task 2.2  
**Iterations:** 1000 per component

---

## Executive Summary

| Component | Avg Time (ms) | Target | Status |
|-----------|---------------|--------|--------|
| Lexer | 0.2753 | < 1ms | ✅ |
| Parser | 0.4033 | < 5ms | ✅ |
| Evaluator | 0.3118 | < 10ms | ✅ |
| **End-to-End** | **0.4468** | **< 50ms** | **✅** |

---

## Detailed Results

### Lexer Performance

- **Average Time:** 0.2753ms per formula
- **Throughput:** 3632 formulas/second
- **Profile:** [profiles/lexer_profile.txt](../profiles/lexer_profile.txt)

**Analysis:**
- Tokenization является быстрым (< 1ms)
- Основные вызовы: `Lexer.__init__()`, `Lexer.tokenize()`, `Lexer.current_char`

### Parser Performance

- **Average Time:** 0.4033ms per formula
- **Throughput:** 2480 formulas/second
- **Profile:** [profiles/parser_profile.txt](../profiles/parser_profile.txt)

**Analysis:**
- AST construction быстрая благодаря recursive descent
- Основные вызовы: `Parser.parse()`, `Parser.parse_expression()`, `Parser.parse_term()`

### Evaluator Performance

- **Average Time:** 0.3118ms per formula
- **Throughput:** 3207 formulas/second
- **Profile:** [profiles/evaluator_profile.txt](../profiles/evaluator_profile.txt)

**Analysis:**
- Execution время зависит от сложности формулы
- Основные вызовы: `Evaluator.evaluate()`, `Evaluator._eval_node()`, dict lookups

### End-to-End Pipeline

- **Average Time:** 0.4468ms per formula
- **Throughput:** 2238 formulas/second
- **Profile:** [profiles/end_to_end_profile.txt](../profiles/end_to_end_profile.txt)

**Breakdown (estimated):**
- Lexer: 61.6%
- Parser: 90.3%
- Evaluator: 69.8%

---

## Bottleneck Analysis

### Top Time Consumers

1. **Dictionary lookups** in Evaluator (chart_data access)
2. **String operations** in Lexer (current_char iteration)
3. **Recursive calls** in Parser (parse_expression, parse_term)

### Optimization Opportunities

1. **AST Caching:** Cache parsed AST for repeated formulas
2. **Chart Data Indexing:** Pre-index chart_data для faster lookups
3. **Token Pool:** Reuse Token objects вместо creating new

---

## Recommendations

### Immediate (Stage 2)
- ✅ Establish baseline metrics (this report)
- ⏳ Create performance test suite
- ⏳ Document acceptable thresholds

### Short-term (Stage 3)
- 🔧 Implement AST caching layer
- 🔧 Optimize Evaluator dict access
- 🔧 Add batch processing for multiple formulas

### Long-term (v2.0)
- 🚀 Consider Cython compilation for hot paths
- 🚀 Profile memory usage with memory_profiler
- 🚀 Implement lazy evaluation for complex formulas

---

## Test Configuration

**Formulas tested:**
- Simple: 5 formulas (e.g., `Sun.Sign == Aries`)
- Medium: 5 formulas (e.g., `Sun.Sign == Aries AND Moon.House == 1`)
- Complex: 5 formulas (e.g., nested logic with aggregators)

**Chart data:**
- 10 planets with full attributes
- All major dignities represented
- Mixed retrograde states

**Environment:**
- Python 3.13.2
- Platform: win32
- Iterations: 1000 per component

---

## Conclusion

DSL система показывает ✅ ОТЛИЧНУЮ производительность:
- End-to-end: 0.4468ms (target < 50ms)
- Готовность к production: Да

**Status:** Task 2.2 ✅ COMPLETE
