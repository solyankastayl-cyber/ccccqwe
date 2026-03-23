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
  - `pattern/render_contract_builder.py` - Pattern Render Contract V4
  - `mtf_engine.py` - Multi-Timeframe Engine
  - `per_tf_builder.py` - Per-TF Builder

### Frontend (React)
- `/app/frontend/src/modules/cockpit/views/ResearchViewNew.jsx` - Research View
- `/app/frontend/src/modules/cockpit/components/ResearchChart.jsx` - Research Chart
- `/app/frontend/src/chart/renderers/patternRenderer.js` - V4 Pattern Renderer

## What's Been Implemented (March 2026)

### Session 1 - Interpretation Layer ✅
- [x] InterpretationEngine class
- [x] MTF Summary Bar
- [x] Per-TF interpretation panel
- [x] TF display names (30D→1M, 180D→6M)

### Session 2 - Pattern Rendering Engine v4 ✅
- [x] PatternRenderContractBuilder (backend)
- [x] patternRenderer.js (frontend)
- [x] V4 integration in ResearchChart
- [x] Disabled legacy renderer when V4 available

### Session 3 - Integration Debug ✅ (CURRENT)
- [x] Fixed timestamp format (seconds not ms)
- [x] Fixed API import (LineSeries from lightweight-charts)
- [x] Added `data` to useEffect dependencies
- [x] Disabled patternGeometry when V4 contract exists
- [x] Increased lineWidth for visibility
- [x] **V4 BOUNDARIES NOW VISIBLE ON CHART** ✅

## Key Fix Details
Problem: V4 boundaries rendered but not visible
Root causes found and fixed:
1. ✅ Wrong Lightweight Charts API (`addLineSeries` → `addSeries(LineSeries, options)`)
2. ✅ Missing `data` in useEffect dependencies
3. ✅ Legacy renderer overriding V4 (disabled via `patternGeometry={...pattern_render_contract ? null : ...}`)
4. ✅ lineWidth too thin (increased to 3)

## Testing Results
- Backend: 100%
- Frontend: 95%
- V4 boundaries: VISIBLE (blue lines)
- Breakout level: VISIBLE (green dashed)
- Pattern card: WORKING
- Interpretation: WORKING

## Next Steps
1. Pattern View mode (hide structure when viewing pattern)
2. Alternative patterns switcher
3. Visual quality filter
4. 6M timeframe interpretation fix

## Tech Stack
- Backend: Python 3.x, FastAPI, MongoDB
- Frontend: React, styled-components
- Chart: TradingView Lightweight Charts v5
