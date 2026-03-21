# Technical Analysis Module - PRD

## Original Problem Statement
Проект теханализа криптовалют. Репозиторий: `https://github.com/solyankastayl-cyber/cdcdcd1222`

Пользователь работает **только** с модулем теханализа (Research view). Требования:
1. Поднять проект (bootstrap, frontend, backend, Coinbase adapter)
2. Воссоздать функционал RSI и MACD индикаторов под графиком

## Architecture

```
/app/
├── backend/         # FastAPI backend
│   ├── modules/
│   │   ├── ta_engine/      # Technical Analysis core logic
│   │   └── broker_adapters/ # Exchange adapters (Coinbase)
│   ├── bootstrap.py
│   └── server.py
└── frontend/        # React frontend
    └── src/
        └── modules/
            └── cockpit/    # Main UI module
                ├── views/
                │   └── ResearchViewNew.jsx  # MAIN RESEARCH VIEW
                └── components/
                    └── IndicatorPanes.jsx   # RSI/MACD component
```

## Key API Endpoints
- `/api/health` - Backend health check
- `/api/ta-engine/mtf/{symbol}?timeframes={tf}` - Multi-timeframe analysis data
- `/api/ta/status` - TA Engine status
- `/api/ta/provider-health/coinbase` - Coinbase adapter health

## What's Implemented

### Session 2026-03-21
- ✅ Интеграция панели RSI/MACD в Research View (`ResearchViewNew.jsx`)
- ✅ Панель отображается под основным графиком
- ✅ RSI (14) и MACD (12,26,9) работают с реальными данными из API

## Backlog

### P2 - Future Tasks
- [ ] Добавить resizable функционал для панели осцилляторов (возможность "потянуть вверх")
- [ ] Добавить UI для выбора других осцилляторов (Stochastic, Volume, OBV, ATR, ADX)
- [ ] Добавить алерты для торговых паттернов (Head & Shoulders, Double Bottom)

## Tech Stack
- **Backend:** Python, FastAPI, MongoDB (motor async driver)
- **Frontend:** React, TailwindCSS, styled-components, lightweight-charts
- **Data:** Coinbase public API (no keys required)
- **DevOps:** Supervisor for service management

## Notes
- Работа ведётся ТОЛЬКО с модулем Research (не Chart Lab)
- Основной view: `ResearchViewNew.jsx` (импортируется как `ResearchView` в `TechAnalysisModule.jsx`)
