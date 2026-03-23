# FOMO Platform - Tech Analysis Module PRD

## Original Problem Statement
Поднять проект FOMO из GitHub репозитория. Сфокусироваться на модуле Tech Analysis (теханализ).  
Проблема: backend работает правильно, но frontend показывает "no trade / нет анализа" вместо осмысленного TA.

## Architecture

### Backend (Python/FastAPI)
- `/app/backend/modules/ta_engine/` - TA Engine module
  - `interpretation/interpretation_engine.py` - Interpretation Layer (NEW)
  - `mtf_engine.py` - Multi-Timeframe Engine
  - `per_tf_builder.py` - Per-TF Builder
  - `ta_routes.py` - API routes

### Frontend (React)
- `/app/frontend/src/modules/cockpit/views/ResearchViewNew.jsx` - Research View

## User Personas
1. **Trader/Researcher** - Uses TA module to analyze market structure
2. **Technical Analyst** - Needs clear interpretation of patterns and trends

## Core Requirements (Static)
1. MTF Analysis with proper interpretation
2. Human-readable TA language (not trading terminal language)
3. Summary across timeframes (HTF/MTF/LTF)
4. Clear TF naming (1M, 6M instead of 30D, 180D)

## What's Been Implemented (March 2026)

### Session 1 - Interpretation Layer
- [x] Created InterpretationEngine class
  - `_interpret_htf()` - Macro context interpretation
  - `_interpret_mtf()` - Mid-term pattern interpretation  
  - `_interpret_ltf()` - Local detail interpretation
  - `build_one_line_summary()` - One-line MTF summary
- [x] Integrated into MTF Engine and per_tf_builder
- [x] Added summary_text to API response
- [x] Frontend: MTF Summary Bar above chart
- [x] Frontend: Per-TF interpretation panel
- [x] Frontend: TF display names (30D→1M, 180D→6M)
- [x] Replaced trading language with research language

## Prioritized Backlog

### P0 (Critical) - DONE
- [x] Interpretation Layer
- [x] MTF Summary Bar
- [x] TF naming fix

### P1 (High Priority)
- [ ] Smart Highlight Layer (подсветка ключевых зон)
- [ ] Hover explanation on chart
- [ ] Visual Mapping Layer improvements

### P2 (Medium Priority)  
- [ ] Indicator cards with click-to-show overlay
- [ ] Pattern confidence visualization
- [ ] Structure phase indicators

## Next Tasks
1. Review and improve interpretation text quality
2. Add Smart Highlight Layer for key zones
3. Improve indicator toggle UX

## Tech Stack
- Backend: Python 3.x, FastAPI, MongoDB
- Frontend: React, styled-components
- Chart: TradingView Lightweight Charts
