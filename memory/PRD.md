# FOMO Platform - Tech Analysis Module PRD

## Original Problem Statement
Поднять проект FOMO из GitHub репозитория. Сфокусироваться на модуле Tech Analysis (теханализ).

### Phase 1: Interpretation Layer
Проблема: backend работает правильно, но frontend показывает "no trade / нет анализа" вместо осмысленного TA.

### Phase 2: Pattern Rendering Engine v4
Проблема: фигуры рисуются как "соединённые pivot точки", а не как proper TA formations.

## Architecture

### Backend (Python/FastAPI)
- `/app/backend/modules/ta_engine/` - TA Engine module
  - `interpretation/interpretation_engine.py` - Interpretation Layer
  - `pattern/render_contract_builder.py` - Pattern Render Contract V4 (NEW)
  - `mtf_engine.py` - Multi-Timeframe Engine
  - `per_tf_builder.py` - Per-TF Builder
  - `ta_routes.py` - API routes

### Frontend (React)
- `/app/frontend/src/modules/cockpit/views/ResearchViewNew.jsx` - Research View
- `/app/frontend/src/modules/cockpit/components/ResearchChart.jsx` - Research Chart
- `/app/frontend/src/chart/renderers/patternRenderer.js` - V4 Pattern Renderer (NEW)

## User Personas
1. **Trader/Researcher** - Uses TA module to analyze market structure
2. **Technical Analyst** - Needs clear interpretation of patterns and trends

## Core Requirements (Static)
1. MTF Analysis with proper interpretation
2. Human-readable TA language (not trading terminal language)
3. Summary across timeframes (HTF/MTF/LTF)
4. Clear TF naming (1M, 6M instead of 30D, 180D)
5. Pattern rendering as proper TA formations (bounded windows, clean boundaries)

## What's Been Implemented (March 2026)

### Session 1 - Interpretation Layer
- [x] Created InterpretationEngine class
- [x] Integrated into MTF Engine and per_tf_builder
- [x] Added summary_text to API response
- [x] Frontend: MTF Summary Bar above chart
- [x] Frontend: Per-TF interpretation panel
- [x] Frontend: TF display names (30D→1M, 180D→6M)
- [x] Replaced trading language with research language

### Session 2 - Pattern Rendering Engine v4
- [x] Created PatternRenderContractBuilder
  - `_build_triangle()` - Triangle render contract
  - `_build_wedge()` - Wedge render contract
  - `_build_channel()` - Channel render contract
  - `_build_double()` - Double top/bottom render contract
  - `_build_head_shoulders()` - H&S render contract
- [x] Integrated into per_tf_builder (pattern_render_contract, alternative_render_contracts)
- [x] Frontend: patternRenderer.js with Lightweight Charts API
  - `drawBoundaries()` - Trendlines bounded by window
  - `drawLevels()` - Horizontal levels (neckline, breakout)
  - `drawMarkers()` - Pattern markers (LS, H, RS)
- [x] Frontend: V4 render contract integration in ResearchChart
- [x] Console logs: "[PatternRenderer] Rendered ascending_triangle: 2 boundaries, 1 levels"

## Render Contract Structure (V4)
```json
{
  "type": "ascending_triangle",
  "label": "Ascending Triangle",
  "direction": "bullish",
  "confidence": 0.74,
  "window": {"start": timestamp, "end": timestamp},
  "render": {
    "boundaries": [
      {"id": "upper_boundary", "kind": "trendline", "x1": t1, "y1": p1, "x2": t2, "y2": p2},
      {"id": "lower_boundary", "kind": "trendline", "x1": t1, "y1": p1, "x2": t2, "y2": p2}
    ],
    "levels": [
      {"id": "breakout_level", "kind": "resistance_breakout", "price": 74100}
    ],
    "touch_points": [...],
    "markers": [...],
    "zones": []
  }
}
```

## Prioritized Backlog

### P0 (Critical) - DONE
- [x] Interpretation Layer
- [x] MTF Summary Bar
- [x] TF naming fix
- [x] Pattern Render Contract V4
- [x] Frontend V4 Renderer

### P1 (High Priority)
- [ ] Pattern View mode (hide structure, show only pattern)
- [ ] Pattern quality filter (visual clarity)
- [ ] Alternative patterns switcher UI

### P2 (Medium Priority)  
- [ ] Smart Highlight Layer
- [ ] Hover explanation on chart
- [ ] Touch points visualization

## Testing Results
- Backend: 100%
- Frontend: 95%
- Minor issues: WebSocket warnings (non-blocking)

## Tech Stack
- Backend: Python 3.x, FastAPI, MongoDB
- Frontend: React, styled-components
- Chart: TradingView Lightweight Charts v5
