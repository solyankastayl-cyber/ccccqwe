# Technical Analysis Module - PRD

## Original Problem Statement
Клонировать репозиторий, изучить архитектуру, работать ТОЛЬКО с модулем теханализа.

## COMPLETED PHASES

### Phase 1: Pattern Geometry Contract ✅
- Backend нормализует geometry в единый формат
- Frontend рисует только примитивы

### Phase 2: Pattern Selection Engine v2.0 ✅
- 7-этапный cascade filtering
- Strict thresholds

### Phase 3: Structure Builder v2 + Pattern Engine v3 ✅
- TF-adaptive pivot filtering
- Line fit + touch validation

### Phase 4: MTF Engine v2.0 ✅
**Проблема:** Все TF обрабатывались одинаково → HTF без паттернов = "ошибка"
**Решение:** Role-based анализ — каждый TF имеет свою роль

## MTF Architecture (FINAL)

```
TF Roles:
- HTF (1M, 6M, 1Y, 30D, 180D) → CONTEXT (trend, regime, major levels)
- MTF (1D, 7D) → PATTERNS (main TA layer)
- LTF (4H) → DETAIL (local patterns, confirmation)
```

### Key Principle
**NO PATTERN on HTF is NOT an error — it's valid.**

HTF gives CONTEXT, not patterns.

## API Response Example

```json
{
  "mtf_analysis": {
    "summary": {
      "one_line": "30D: Neutral · 7D: Falling Wedge · 4H: Ascending Triangle",
      "macro_trend": "neutral",
      "narrative": "Macro context is neutral. Mid-term shows falling wedge (bullish). Short-term shows local ascending triangle."
    },
    "analyses": {
      "30D": {"role": "htf", "trend": "neutral", "pattern": null},
      "7D": {"role": "mtf", "trend": "neutral", "pattern": "falling_wedge"},
      "4H": {"role": "ltf", "trend": "neutral", "pattern": "ascending_triangle"}
    }
  }
}
```

## Key Files

### Backend
- `/app/backend/modules/ta_engine/mtf_engine.py` - MTF Engine v2.0
- `/app/backend/modules/ta_engine/mtf/mtf_orchestrator.py` - Updated orchestrator
- `/app/backend/modules/ta_engine/setup/structure_builder.py` - Structure Builder v2
- `/app/backend/modules/ta_engine/setup/pattern_engine_v3.py` - Pattern Engine v3
- `/app/backend/modules/ta_engine/setup/pattern_selector.py` - PSE v2.0

## Testing Results

```
MTF ENGINE v2.0 ANALYSIS
========================
30D (HTF): trend=neutral, pattern=None → CONTEXT ONLY ✅
7D (MTF): trend=neutral, pattern=falling_wedge → MAIN PATTERN ✅  
4H (LTF): trend=neutral, pattern=ascending_triangle → LOCAL DETAIL ✅

NARRATIVE: Macro context is neutral. Mid-term shows falling wedge (bullish). 
Short-term shows local ascending triangle.
```

## Backlog

### P0 - DONE ✅
- [x] Pattern Geometry Contract
- [x] PSE v2.0
- [x] Structure Builder v2
- [x] Pattern Engine v3
- [x] MTF Engine v2.0 (role-based)

### P1 - Next
- [ ] Rename 30D→1M, 180D→6M in data provider
- [ ] Add visual MTF summary on frontend
- [ ] Test on ETH, SOL

### P2 - Future
- [ ] Harmonic patterns
- [ ] Candlestick patterns
