# Technical Analysis Module - PRD

## Original Problem Statement
Подними проект, клонируя репозиторий https://github.com/solyankastayl-cyber/343434343jghjhj. Изучи архитектуру, подними bootstrap. Работаем ТОЛЬКО с модулем теханализа.

**Главная задача:** Pattern Geometry Normalization — создать единый универсальный визуальный контракт для ВСЕХ паттернов.

Backend должен отдавать любую фигуру в одном формате:
- type, label, direction, confidence, status
- geometry: { segments[], levels[], zones[], markers[] }

Frontend рисует ТОЛЬКО примитивы, не зная бизнес-логику конкретных паттернов.

## Architecture Overview
```
Backend: Coinbase Data → per_tf_builder → pattern_detectors_unified → pattern_selector → pattern_geometry_contract → render_plan_v2
Frontend: ResearchViewNew → ResearchChart (lightweight-charts) → PatternGeometryRenderer
```

## Tech Stack
- **Backend:** Python FastAPI, MongoDB
- **Frontend:** React 19, lightweight-charts, styled-components
- **Data Provider:** Coinbase

## What Was Implemented (March 22, 2026)

### Pattern Geometry Contract (COMPLETE)

**File:** `/app/backend/modules/ta_engine/patterns/pattern_geometry_contract.py`

Universal schema for pattern visualization:
```python
{
    "type": "ascending_triangle",
    "label": "Ascending Triangle",
    "direction": "bullish",
    "confidence": 0.85,
    "status": "active",
    "geometry": {
        "segments": [
            {"kind": "resistance", "style": "solid", "points": [...]},
            {"kind": "support_rising", "style": "solid", "points": [...]}
        ],
        "levels": [
            {"kind": "breakout", "price": 73968.0, "label": "Breakout"},
            {"kind": "invalidation", "price": 70236.0, "label": "Invalidation"}
        ],
        "zones": [],
        "markers": [...]
    }
}
```

**Supported Patterns:**
- Triangles: ascending, descending, symmetrical
- Channels: ascending, descending, horizontal
- Head & Shoulders / Inverse H&S
- Double Top / Double Bottom
- Triple Top / Triple Bottom
- Wedges: rising, falling
- Flags / Pennants
- Range / Rectangle

### Key Files

**Backend:**
- `/app/backend/modules/ta_engine/patterns/pattern_geometry_contract.py` - Universal geometry contract
- `/app/backend/modules/ta_engine/setup/pattern_detectors_unified.py` - Pattern detectors with @register_pattern
- `/app/backend/modules/ta_engine/setup/pattern_selector.py` - Pattern selection with Market Context Scoring
- `/app/backend/modules/ta_engine/per_tf_builder.py` - Main TA pipeline (calls normalize_pattern_geometry)
- `/app/backend/modules/ta_engine/ta_routes.py` - API endpoints

**Frontend:**
- `/app/frontend/src/modules/cockpit/components/ResearchChart.jsx` - Main chart component
- `/app/frontend/src/modules/cockpit/components/PatternGeometryRenderer.jsx` - Universal geometry renderer
- `/app/frontend/src/modules/cockpit/views/ResearchViewNew.jsx` - Research terminal orchestrator

### API Endpoints

```
GET /api/ta-engine/status              - Health check
GET /api/ta-engine/mtf/{symbol}        - Multi-timeframe analysis (main endpoint)
GET /api/ta-engine/mtf/{symbol}/{tf}   - Single timeframe analysis
GET /api/ta-engine/render-plan-v2/{symbol} - Render plan only
GET /api/ta-engine/registry/patterns   - Pattern registry
GET /api/ta-engine/registry/indicators - Indicator registry
```

### Testing Results

**Pattern Detection:**
- ascending_triangle: DETECTED (confidence 0.85)
- Geometry returned: 2 segments, 2 levels, 4 markers

**Frontend Rendering:**
- Candles: OK
- Structure (HH/HL/LH/LL): OK
- Levels (S/R): OK
- Pattern geometry: OK
- Indicators (RSI, MACD): OK

## User Personas

1. **Trader** - Uses TA module to identify patterns and setups
2. **Analyst** - Reviews pattern detection accuracy
3. **Developer** - Extends pattern detection logic

## Core Requirements

1. Backend MUST normalize ALL patterns to geometry contract
2. Frontend MUST render ONLY primitives (no pattern-specific logic)
3. Each timeframe is isolated (1 TF = 1 world)
4. Channels/trends are market_state, NOT patterns

## What's Been Implemented

| Date | Feature | Status |
|------|---------|--------|
| Mar 22, 2026 | Project setup from GitHub | DONE |
| Mar 22, 2026 | Pattern Geometry Contract | DONE |
| Mar 22, 2026 | Universal Pattern Renderer | DONE |
| Mar 22, 2026 | Frontend compilation fix | DONE |

## Next Tasks (P0/P1)

### P0 - Critical
1. [ ] Test all 15+ pattern types with geometry
2. [ ] Add FVG/Order Block to geometry contract
3. [ ] Verify geometry on historical data

### P1 - Important
1. [ ] Improve pattern confidence scoring
2. [ ] Add pattern expiration visualization
3. [ ] StoryLine component integration with geometry

### P2 - Nice to have
1. [ ] Pattern backtesting module
2. [ ] Custom pattern definition UI
3. [ ] Export patterns as JSON/CSV

## Backlog

- Multi-asset pattern correlation
- Machine learning pattern recognition
- Social sharing of patterns
