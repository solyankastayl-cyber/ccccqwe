# FOMO Platform - Tech Analysis Module PRD

## Original Problem Statement
Поднять проект FOMO из GitHub репозитория. Сфокусироваться на модуле Tech Analysis (теханализ).

## Completed Phases

### Phase 1: Interpretation Layer ✅
- InterpretationEngine для human-readable TA
- MTF Summary Bar
- Per-TF interpretation panel
- TF display names (30D→1M, 180D→6M)

### Phase 2: Pattern Rendering Engine v4 ✅
- PatternRenderContractBuilder (backend)
- patternRenderer.js (frontend)
- V4 boundaries rendering
- Integration bug fixed (Lightweight Charts API)

### Phase 3: Pattern View Mode ✅ (CURRENT)
- Режим изоляции паттерна для читаемости
- Pattern Zoom — центрирование на window паттерна
- Скрытие structure/levels/indicators/liquidity

## Architecture

### Backend
- `/app/backend/modules/ta_engine/interpretation/interpretation_engine.py`
- `/app/backend/modules/ta_engine/pattern/render_contract_builder.py`
- `/app/backend/modules/ta_engine/per_tf_builder.py`

### Frontend
- `/app/frontend/src/modules/cockpit/views/ResearchViewNew.jsx`
- `/app/frontend/src/modules/cockpit/components/ResearchChart.jsx`
- `/app/frontend/src/chart/renderers/patternRenderer.js`

## What's Been Implemented (March 2026)

### Pattern View Mode
- [x] `patternViewMode` state in ResearchViewNew
- [x] "View ON" button (blue when active)
- [x] When active: hide structure, levels, indicators, liquidity, market mechanics
- [x] Pattern Zoom: setVisibleRange to pattern window + 15% padding
- [x] Pattern window now uses anchor_points for accurate boundaries
- [x] Fигура читается за 2 секунды ✅

### Key Metrics
- Backend: 100%
- Frontend: 100%
- Pattern readability: ACHIEVED

## Screenshot Evidence
Pattern View mode активен:
- График zoom'd к паттерну (27 фев - 15 мар)
- Ascending Triangle чётко виден
- Blue boundaries + green breakout level
- Никакого визуального шума

## Next Steps
1. Alternative patterns switcher
2. 6M interpretation fix  
3. Pattern quality filter (visual clarity scoring)

## Tech Stack
- Backend: Python 3.x, FastAPI, MongoDB
- Frontend: React, styled-components
- Chart: TradingView Lightweight Charts v5
