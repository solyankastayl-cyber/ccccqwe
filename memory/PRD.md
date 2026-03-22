# Technical Analysis Module - PRD

## Original Problem Statement
Подними проект из репозитория https://github.com/solyankastayl-cyber/ccccq. Работаем только с модулем теханализа. 
1. Реализовать функционал "Save Idea" — сохранение прогноза с возможностью обновления и отслеживания.
2. Полный аудит индикаторов — 144 индикатора в системе
3. UI полировка — семантика RSI/MACD, research-язык вместо trading-языка

## Architecture
- **Backend**: FastAPI + MongoDB (modules/ta_engine/, modules/exchange_intelligence/, modules/microstructure_intelligence_v2/)
- **Frontend**: React + styled-components (modules/cockpit/)
- **Key Modules**:
  - TA Engine: 38 classic technical indicators
  - Exchange Intelligence: 31 exchange/derivatives indicators
  - Microstructure: 23 orderbook/pressure indicators
  - Macro Context: 15 macroeconomic indicators
  - Capital Flow: 14 rotation indicators
  - Regime Intelligence: 8 market regime indicators
  - Patterns/Structure: 15 pattern detection indicators

## What's Been Implemented (March 22, 2026)

### Session 1: Save Idea Feature
- POST /api/ta/ideas - Create idea
- GET /api/ta/ideas - List ideas
- POST /api/ta/ideas/{id}/update - Update version
- POST /api/ta/ideas/{id}/validate - Validate
- GET /api/ta/ideas/{id}/timeline - Timeline
- IdeasPanel component in HypothesesView

### Session 2: Indicator Audit
- Full audit of 144 indicators across all modules
- Created INDICATORS_FULL_AUDIT.md
- Identified 19 TA indicators needing implementation
- All Exchange/Microstructure/Macro indicators functional

### Session 3: UI Polish (P1)
- IndicatorInsights V3: RSI/MACD cards with proper interpretation
  - RSI 37 · Near Oversold → "Selling pressure weakening"
  - MACD · Bearish Fading → "Selling pressure easing"
- Market Context: Research-oriented language
- Technical Setup: "Setup Quality" instead of "Tradeability"
- Key insight line: "Resistance at X defines upside risk"

## Testing Results
- Save Idea: 100% (all API endpoints working)
- UI: RSI/MACD cards display correctly
- Market Context/Technical Setup blocks render

## Backlog (P1/P2 Features)

### P1: Remaining UI Polish
- [ ] P2: Визуальная иерархия — график главный
- [ ] P3: Empty states для блоков без данных
- [ ] P4: Синхронизация выводов между блоками

### P1: Missing TA Indicators (19)
- VWMA, HMA, Pivot Points, Fibonacci Retracement
- Stochastic RSI, MFI
- ROC, TRIX
- Volume bars, A/D Line, CMF
- BB Width, Historical Volatility
- DMI (+DI/-DI), Aroon

### P2: Pattern Visualization
- Liquidity Zones rendering
- FVG rendering  
- Order Block rendering

## Next Tasks
1. Implement remaining TA indicators
2. Complete UI hierarchy polish
3. Empty states for all blocks
4. Story line chain improvement
