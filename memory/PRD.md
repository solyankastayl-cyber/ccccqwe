# Technical Analysis Module - PRD

## Original Problem Statement
Проект теханализа криптовалют. Репозиторий: `https://github.com/solyankastayl-cyber/cdcdcd1222`

Пользователь работает **только** с модулем теханализа (Research view). Требования:
1. Поднять проект (bootstrap, frontend, backend, Coinbase adapter)
2. Воссоздать функционал RSI и MACD индикаторов под графиком
3. **Показывать интерпретацию индикаторов, а не просто сырые данные**

## Architecture

```
/app/
├── backend/
│   └── modules/ta_engine/
│       └── indicators/
│           ├── indicator_visualization.py  # Raw pane data
│           └── indicator_insights.py       # NEW: Interpretation engine
└── frontend/
    └── src/modules/cockpit/
        ├── views/
        │   └── ResearchViewNew.jsx  # Main Research view
        └── components/
            ├── IndicatorPanes.jsx    # Raw charts
            └── IndicatorInsights.jsx # NEW: State/summary cards
```

## What's Implemented

### Session 2026-03-22
- ✅ **Indicator Insights Engine** (backend)
  - RSI states: oversold, near_oversold, neutral, bullish_pressure, overbought
  - MACD states: bullish/bearish crossover, momentum building/fading, neutral
  - Returns: value, state, bias, strength, summary, color

- ✅ **IndicatorInsights component** (frontend)
  - Shows state badge (e.g., "NEAR OVERSOLD")
  - Shows summary text (e.g., "RSI approaching oversold — downside momentum continues")
  - Shows bias and strength indicators

- ✅ ChartLab tab removed from UI
- ✅ Research tab icon changed to BarChart2

## API Contract

```json
{
  "indicator_insights": {
    "rsi": {
      "value": 33.12,
      "state": "near_oversold",
      "bias": "bearish",
      "strength": "medium",
      "summary": "RSI approaching oversold — downside momentum continues.",
      "color": "#86efac"
    },
    "macd": {
      "state": "bearish_momentum_fading",
      "bias": "neutral",
      "strength": "low",
      "summary": "MACD slightly negative — weak bearish bias.",
      "color": "#fecaca"
    }
  }
}
```

## Backlog

### P1 - Short Term
- [ ] Add ADX interpretation (trend strength)
- [ ] Add Volume/OBV interpretation (confirmation)
- [ ] Resizable panel for indicator section

### P2 - Future
- [ ] Trading alerts for key patterns
- [ ] Divergence detection (RSI/MACD vs price)

