# Technical Analysis Module - PRD

## Original Problem Statement
Клонировать репозиторий, изучить архитектуру, работать ТОЛЬКО с модулем теханализа.

**Главная задача (2026-03-23):** 
Pattern Geometry Normalization — создать единый универсальный визуальный контракт для ВСЕХ паттернов.

**Решённые проблемы:**
1. Backend не отдавал geometry → FIXED (geometry contract)
2. Backend отдавал geometry в разных форматах → FIXED (normalize_pattern_geometry)
3. Frontend не читал geometry → FIXED (patternGeometry prop + renderPatternGeometry)

## Solution Implemented

### Pattern Geometry Contract
Backend отдаёт ЛЮБУЮ фигуру в едином формате:
```json
{
  "type": "ascending_triangle",
  "label": "Ascending Triangle", 
  "direction": "bullish",
  "confidence": 0.85,
  "status": "active",
  "geometry": {
    "segments": [
      {"kind": "resistance", "points": [...], "color": "#64748b"},
      {"kind": "support_rising", "points": [...], "color": "#16a34a"}
    ],
    "levels": [
      {"kind": "breakout", "price": 73968.0},
      {"kind": "invalidation", "price": 70236.02}
    ],
    "zones": [],
    "markers": [...]
  }
}
```

Frontend рисует ТОЛЬКО примитивы:
- segments → LineSeries
- levels → PriceLine
- zones → AreaSeries
- markers → setMarkers

## Architecture (WORKING)

```
Backend Pipeline:
Coinbase Data → per_tf_builder → pattern_detectors_unified → pattern_selector 
  → normalize_pattern_geometry() → pattern_geometry (JSON)

Frontend Pipeline:  
ResearchViewNew:
  - setupData?.pattern_geometry → patternGeometry prop
  
ResearchChart:
  - renderPatternGeometry(chart, patternGeometry, priceSeries, candles)
  
PatternGeometryRenderer:
  - segments → chart.addSeries(LineSeries)
  - levels → priceSeries.createPriceLine()
  - markers → priceSeries.setMarkers()
```

## What Was Fixed (March 23, 2026)

### 1. Backend: pattern_geometry_contract.py
- Added `_get_time()`, `_get_price()`, `_to_point()` helpers
- Added `_normalize_points_format()` for LIST→DICT conversion
- Fixed H&S nested markers format
- Fixed Double patterns LIST conversion
- Fixed Channel patterns LIST conversion
- Fixed Flag patterns pole/boundary rendering
- Added Compression zone rendering
- Added Breakout marker rendering

### 2. Frontend: Data Flow Fix
**ResearchViewNew.jsx:**
```javascript
patternGeometry={setupData?.pattern_geometry}
```

**ResearchChart.jsx:**
```javascript
const geometryToRender = patternGeometry || patternV2?.primary_pattern;
if (geometryToRender?.geometry && showPatternOverlay) {
  renderPatternGeometry(chart, geometryToRender, priceSeries, candles);
}
```

### 3. Audit Results
| Pattern Family | Registered | Detector | Normalized | Renderable |
|----------------|------------|----------|------------|------------|
| Triangles (3) | YES | YES | YES ✅ | YES ✅ |
| H&S (2) | YES | YES | YES ✅ | YES ✅ |
| Channels (3) | YES | YES | YES ✅ | YES ✅ |
| Double (2) | YES | YES | YES ✅ | YES ✅ |
| Wedges (2) | YES | YES | YES ✅ | YES ✅ |
| Flags (2) | YES | YES | YES ✅ | YES ✅ |
| Range (1) | YES | YES | YES ✅ | YES ✅ |
| Compression (1) | YES | YES | YES ✅ | YES ✅ |
| Breakout (2) | YES | YES | YES ✅ | YES ✅ |

**18 patterns fully normalized and renderable!**

## Key Files

### Backend
- `/app/backend/modules/ta_engine/patterns/pattern_geometry_contract.py` - Universal normalizer
- `/app/backend/modules/ta_engine/setup/pattern_detectors_unified.py` - 9 detectors
- `/app/backend/modules/ta_engine/PATTERN_AUDIT.md` - Audit matrix

### Frontend
- `/app/frontend/src/modules/cockpit/views/ResearchViewNew.jsx` - Passes patternGeometry
- `/app/frontend/src/modules/cockpit/components/ResearchChart.jsx` - Calls renderer
- `/app/frontend/src/modules/cockpit/components/PatternGeometryRenderer.jsx` - Draws primitives

## API Response Structure
```
GET /api/ta-engine/mtf/BTC?timeframes=4H

{
  "tf_map": {
    "4H": {
      "primary_pattern": {...},      // Legacy format
      "pattern_geometry": {...},     // NORMALIZED format ← USE THIS
      "alternative_patterns": [...]
    }
  }
}
```

## Backlog

### P0 - Done ✅
- [x] Pattern Geometry Contract
- [x] Normalize all 9 detectors
- [x] Frontend rendering fix
- [x] E2E verification

### P1 - Next
- [ ] Add detectors for triple_top/triple_bottom
- [ ] Test on ETH, SOL
- [ ] Pattern history tracking

### P2 - Future
- [ ] Harmonic patterns (12)
- [ ] Candlestick patterns (18)
- [ ] Complex patterns (8)
