# Technical Analysis Module - PRD

## Original Problem Statement
Клонировать репозиторий, изучить архитектуру, работать ТОЛЬКО с модулем теханализа.

## COMPLETED PHASES

### Phase 1: Pattern Geometry Contract ✅
- Backend нормализует geometry в единый формат
- Frontend рисует только примитивы (segments, levels, markers)

### Phase 2: Pattern Selection Engine v2.0 ✅
- 7-этапный cascade filtering
- Strict thresholds для отсева мусора

### Phase 3: Structure Builder v2 + Pattern Engine v3 ✅
**Проблема:** Входные данные были мусорными → паттерны получались кривыми
**Решение:** Clean structure layer с TF-adaptive filtering

## Architecture (FINAL)

```
candles
→ pivots
→ Structure Builder v2 (filter by min_move per TF)
→ Pattern Engine v3 (line fit + touch validation)
→ PSE v2.0 (cascade selection)
→ Geometry Contract (normalize)
→ Frontend Renderer (primitives only)
```

## Structure Builder v2 Features

### TF-Specific Configuration
| TF | min_move | min_span | touch_tolerance |
|----|----------|----------|-----------------|
| 1H | 1.0% | 15 | 0.8% |
| 4H | 1.5% | 20 | 1.0% |
| 1D | 3.0% | 30 | 1.2% |
| 7D | 5.0% | 40 | 1.5% |
| 30D | 8.0% | 60 | 2.0% |
| 180D | 12.0% | 80 | 2.5% |
| 1Y | 20.0% | 120 | 3.0% |

### Pipeline
1. **filter_pivots()** - Remove small moves based on min_move %
2. **extract_structure()** - Keep only swing highs/lows
3. **separate_highs_lows()** - Split for pattern detection

## Pattern Engine v3 Features

### Line Fitting
- Uses numpy `polyfit()` for regression
- Not just connecting points

### Touch Validation
- Counts touches within tolerance
- Minimum 2 touches required

### Pattern Types
- Triangles (ascending, descending, symmetrical)
- Channels (ascending, descending, horizontal)
- Double Top/Bottom
- Head & Shoulders

### Conflict Resolution
- Triangle checked before Channel
- More specific patterns preferred

## Key Files

### Backend
- `/app/backend/modules/ta_engine/setup/structure_builder.py` - Structure Builder v2
- `/app/backend/modules/ta_engine/setup/pattern_engine_v3.py` - Pattern Engine v3
- `/app/backend/modules/ta_engine/setup/pattern_selector.py` - PSE v2.0
- `/app/backend/modules/ta_engine/patterns/pattern_geometry_contract.py` - Geometry normalizer

### Frontend
- `/app/frontend/src/modules/cockpit/components/PatternGeometryRenderer.jsx`
- `/app/frontend/src/modules/cockpit/components/ResearchChart.jsx`

## Testing Results

### 4H Timeframe
```
[StructureBuilder] Filtered pivots: 28 → 24 (min_move=0.015)
[StructureBuilder] Structure points: 23
[PatternV3] Double Top detected
Pattern: ascending_triangle (score=0.71)
```

### 7D Timeframe
```
[StructureBuilder] Filtered pivots: 14 → 10 (min_move=0.05)
Pattern: falling_wedge (score=0.68)
```

### 30D+ Timeframes
```
[PatternV3] Not enough structure points
Pattern: None (correct - insufficient data/touches)
```

## Backlog

### P0 - DONE ✅
- [x] Pattern Geometry Contract
- [x] PSE v2.0 cascade filtering
- [x] Structure Builder v2 (TF-adaptive)
- [x] Pattern Engine v3 (line fit + validation)

### P1 - Next
- [ ] Visual confidence indicator on chart
- [ ] Test on ETH, SOL
- [ ] Add pattern history tracking

### P2 - Future
- [ ] Harmonic pattern detectors
- [ ] Candlestick pattern detectors
