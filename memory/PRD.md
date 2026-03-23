# Technical Analysis Module - PRD

## Original Problem Statement
Клонировать репозиторий, изучить архитектуру, работать ТОЛЬКО с модулем теханализа.

**Главная задача (2026-03-23):** 
Pattern Geometry Normalization — создать единый универсальный визуальный контракт для ВСЕХ паттернов.

Проблема была не в knowledge layer, а в render layer:
- Backend знает фигуры логически, но отдавал geometry в разных форматах
- Frontend не мог стабильно рисовать из-за отсутствия единого стандарта

## Solution Implemented

### Pattern Geometry Contract
Backend теперь отдает ЛЮБУЮ фигуру в одном формате:
```json
{
  "type": "pattern_type",
  "label": "Human Readable Label", 
  "direction": "bullish|bearish|neutral",
  "confidence": 0.85,
  "status": "active",
  "geometry": {
    "segments": [],
    "levels": [],
    "zones": [],
    "markers": []
  }
}
```

Frontend рисует ТОЛЬКО примитивы без знания бизнес-логики паттернов.

## Architecture

```
Backend Pipeline:
Coinbase Data → per_tf_builder → pattern_detectors_unified → pattern_selector → normalize_pattern_geometry() → render_plan_v2

Frontend Pipeline:  
ResearchViewNew → ResearchChart (lightweight-charts) → PatternGeometryRenderer (renders primitives only)
```

## What Was Implemented (March 23, 2026)

### 1. Pattern Geometry Contract Fixes
**File:** `/app/backend/modules/ta_engine/patterns/pattern_geometry_contract.py`

Added helper functions:
- `_get_time(p)` - Extract time from any point format
- `_get_price(p)` - Extract price from any point format
- `_to_point(p)` - Convert to standard {time, price}
- `_normalize_points_format()` - Convert LIST to DICT format

Fixed pattern handlers:
- H&S: Now handles nested `points.markers.left_shoulder` format
- Double Top/Bottom: Converts LIST `[{type: "top1"}, ...]` to DICT
- Channels: Converts LIST `[{type: "high_start"}, ...]` to DICT
- Flags: Added pole and flag boundary segment rendering
- Compression: Added zone rendering
- Breakout/Breakdown: Added marker rendering

### 2. Audit Matrix Created
**File:** `/app/backend/modules/ta_engine/PATTERN_AUDIT.md`

| Pattern Family | Registered | Detectable | Normalized | Renderable |
|----------------|------------|------------|------------|------------|
| Triangles (3) | YES | YES | YES ✅ | YES ✅ |
| H&S (2) | YES | YES | YES ✅ | YES ✅ |
| Channels (3) | YES | YES | YES ✅ | YES ✅ |
| Double (2) | YES | YES | YES ✅ | YES ✅ |
| Wedges (2) | YES | YES | YES ✅ | YES ✅ |
| Flags (2) | YES | YES | YES ✅ | YES ✅ |
| Range (1) | YES | YES | YES ✅ | YES ✅ |
| Compression (1) | YES | YES | YES ✅ | YES ✅ |
| Breakout (2) | YES | YES | YES ✅ | YES ✅ |
| Harmonic (12) | YES | NO | NO | NO |
| Candlestick (18) | YES | NO | NO | NO |
| Complex (8) | YES | NO | NO | NO |

**18 patterns fully normalized and renderable**
**38 patterns registry-only (no detector)**

## Tech Stack
- **Backend:** Python FastAPI, MongoDB
- **Frontend:** React 19, lightweight-charts, styled-components
- **Data Provider:** Coinbase

## Key Files

### Backend
- `/app/backend/modules/ta_engine/patterns/pattern_geometry_contract.py` - Universal geometry normalizer
- `/app/backend/modules/ta_engine/setup/pattern_detectors_unified.py` - 9 pattern detectors
- `/app/backend/modules/ta_engine/setup/pattern_selector.py` - Pattern selection with scoring
- `/app/backend/modules/ta_engine/per_tf_builder.py` - Main TA pipeline
- `/app/backend/modules/ta_engine/PATTERN_AUDIT.md` - Audit results

### Frontend
- `/app/frontend/src/modules/cockpit/components/ResearchChart.jsx` - Main chart
- `/app/frontend/src/modules/cockpit/components/PatternGeometryRenderer.jsx` - Primitive renderer

## API Endpoints
```
GET /api/ta-engine/status
GET /api/ta-engine/mtf/{symbol}?timeframes=4H,1D
GET /api/ta-engine/registry/patterns
```

## User Personas
1. **Trader** - Uses TA for pattern identification
2. **Analyst** - Reviews pattern accuracy
3. **Developer** - Extends pattern detection

## Backlog (P0/P1/P2)

### P0 - Done ✅
- [x] Pattern Geometry Contract audit
- [x] Fix all 9 detector normalizations
- [x] Verify rendering on frontend

### P1 - Next
- [ ] Add detectors for triple_top/triple_bottom
- [ ] Test on multiple assets (ETH, SOL)
- [ ] Add pattern history tracking

### P2 - Future
- [ ] Harmonic pattern detectors
- [ ] Candlestick pattern detectors
- [ ] Complex pattern detectors (Elliott)
- [ ] Machine learning pattern recognition
