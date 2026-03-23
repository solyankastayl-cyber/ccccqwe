# Technical Analysis Module - PRD

## Original Problem Statement
Клонировать репозиторий, изучить архитектуру, работать ТОЛЬКО с модулем теханализа.

## Phase 1 COMPLETE: Pattern Geometry Contract
**Проблема:** Backend не отдавал geometry / отдавал в разных форматах → Frontend не мог рисовать
**Решение:** Единый geometry contract с normalize_pattern_geometry()

## Phase 2 COMPLETE: Pattern Selection Engine v2.0 (PSE)
**Проблема:** Рисовался мусор, много фигур, нет фильтрации
**Решение:** Production-ready cascade filtering

### PSE v2.0 Pipeline
```
1. Hard gating → убить мусор (channels, ranges, low touches)
2. Geometry score → shape quality >= 0.62
3. Context score → market fit >= 0.50  
4. Relevance score → recency + proximity >= 0.60
5. Final score → weighted combination >= 0.68
6. Conflict resolution → dedupe overlapping
7. Winner selection → gap check >= 0.05
```

### Thresholds
| Score | Threshold |
|-------|-----------|
| MIN_TOUCHES | 4 |
| MIN_SPAN | 12 candles |
| MIN_CONTAINMENT | 0.65 |
| MIN_GEOMETRY_SCORE | 0.62 |
| MIN_CONTEXT_SCORE | 0.50 |
| MIN_RELEVANCE_SCORE | 0.60 |
| MIN_FINAL_SCORE | 0.68 |
| MIN_WINNER_GAP | 0.05 |

### Score Weights
```
final_score = geometry * 0.40 + context * 0.25 + relevance * 0.25 + clarity * 0.10
```

## API Response Format
```json
{
  "primary_pattern": {
    "type": "ascending_triangle",
    "direction": "bullish",
    "status": "active",
    "final_score": 0.71,
    "scores": {
      "geometry": 0.75,
      "context": 0.57,
      "relevance": 0.82,
      "clarity": 0.67
    },
    "geometry": {
      "segments": [...],
      "levels": [...],
      "markers": [...]
    }
  }
}
```

## Key Files

### Backend
- `/app/backend/modules/ta_engine/setup/pattern_selector.py` - PSE v2.0
- `/app/backend/modules/ta_engine/setup/pattern_candidate.py` - Score fields
- `/app/backend/modules/ta_engine/patterns/pattern_geometry_contract.py` - Geometry normalizer
- `/app/backend/modules/ta_engine/per_tf_builder.py` - Main pipeline

### Frontend
- `/app/frontend/src/modules/cockpit/components/PatternGeometryRenderer.jsx` - Renders primitives
- `/app/frontend/src/modules/cockpit/components/ResearchChart.jsx` - Uses patternGeometry prop

## Testing Results
```
[PatternSelector] Starting with 2 candidates
[PatternSelector] HARD_GATE: descending_channel is forbidden (market_state)
[PatternSelector] SURVIVOR ascending_triangle: final=0.71 (geo=0.75, ctx=0.57, rel=0.82, clar=0.67)
[PatternSelector] WINNER: ascending_triangle final_score=0.71
```

## What Was Implemented

| Date | Feature | Status |
|------|---------|--------|
| Mar 23, 2026 | Pattern Geometry Contract | DONE ✅ |
| Mar 23, 2026 | Frontend data flow fix | DONE ✅ |
| Mar 23, 2026 | PSE v2.0 cascade filtering | DONE ✅ |
| Mar 23, 2026 | Hard gating (forbidden types) | DONE ✅ |
| Mar 23, 2026 | Multi-score validation | DONE ✅ |
| Mar 23, 2026 | Conflict resolution | DONE ✅ |

## Backlog

### P0 - Done ✅
- [x] Pattern Geometry Contract
- [x] Frontend rendering
- [x] PSE v2.0 selection
- [x] Cascade filtering

### P1 - Next
- [ ] Test on ETH, SOL
- [ ] Add triple_top/triple_bottom detectors
- [ ] Visual confidence bar on chart

### P2 - Future
- [ ] Harmonic patterns
- [ ] Candlestick patterns
- [ ] Pattern backtesting
