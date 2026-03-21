# TA Engine PRD

## Project Overview
TA Engine - Technical Analysis platform for crypto markets with multi-timeframe analysis, pattern detection, and live data from Coinbase.

## Architecture
- **Backend**: FastAPI (Python)
- **Frontend**: React with TradingView Lightweight Charts
- **Database**: MongoDB
- **Live Data**: Coinbase Exchange API

## Core Modules (TA Engine Focus)

### 1. TA Engine (`/backend/modules/ta_engine/`)
- **Indicators**: 15 indicators (SMA, EMA, RSI, MACD, Bollinger, ATR, VWAP, Supertrend, Volume Profile, CCI, Williams %R, Ichimoku, Parabolic SAR, Donchian, Keltner)
- **Patterns**: 14+ patterns (Triangles, Channels, Head & Shoulders, Double Top/Bottom, Cup & Handle, Harmonic Gartley/Bat)
- **Hypothesis Engine**: Direction + conviction scoring
- **MTF Orchestrator**: Multi-timeframe alignment

### 2. Broker Adapters (`/backend/modules/broker_adapters/`)
- **Coinbase Adapter**: Live market data, order execution
- Base adapter interface for extensibility

### 3. Exchange Intelligence
- Funding context, OI snapshots
- Liquidation events, Order flow

## Key API Endpoints
- `GET /api/ta-engine/status` - Health check
- `GET /api/ta-engine/hypothesis/{symbol}` - TA hypothesis
- `GET /api/ta-engine/mtf/{symbol}` - Multi-timeframe analysis
- `GET /api/ta-engine/render-plan-v2/{symbol}` - Full visualization layers
- `GET /api/provider/coinbase/ticker/{symbol}` - Live ticker
- `GET /api/provider/coinbase/candles/{symbol}` - Live candles

## What's Been Implemented (2026-03-21)
- [x] Repository cloned and explored
- [x] Bootstrap executed - 15 collections created
- [x] MongoDB connected with all data
- [x] Coinbase Provider live (BTC $70,400+)
- [x] Backend server running (port 8001)
- [x] Frontend running (port 3000)
- [x] TA Engine hypothesis working
- [x] MTF analysis working
- [x] Pattern detection working

### Deep Analysis Blocks - FIXED & WORKING (2026-03-21)
- [x] **Detected Elements**: 37 elements - patterns, indicators, structure, levels  
- [x] **Technical Summary**: Asset (BTCUSDT), Timeframe (4H/1D), Technical Bias, Confidence, Market Regime
- [x] **Primary Setup**: Setup Type (uptrend/symmetrical triangle), Direction, Confluence Score
- [x] **Market Structure**: HH×2, HL×1, LL×1 + resistance×2, support×1
- [x] **Key Drivers**: RSI, MACD, ADX, PRICE_EMA_POSITION, SMA_STACK, ICHI
- [x] **Conflicts/Risks**: properly displaying
- [x] **Setup Breakdown**: textual explanation working
- [x] **Pattern Detection**: Symmetrical Triangle at 69% confidence

### Key Fix Applied
- Fixed `unifiedSetup` object in `ResearchViewNew.jsx` to properly map backend data (indicators, structure, levels) to DeepAnalysisBlocks and PatternActivationLayer components

## Data Loaded
- BTC: 5,692 daily candles
- ETH: 1,495 daily candles
- SOL: 1,495 daily candles
- SPX: 19,242 daily candles
- DXY: 13,366 daily candles
- Exchange Intelligence: Funding, OI, Liquidations for BTC/ETH/SOL (720 records each)
- Microstructure: 720 snapshots per symbol

## Next Tasks (P0)
- [ ] Test frontend /tech-analysis route
- [ ] Verify chart rendering with live data
- [ ] Test pattern visualization

## Backlog (P1)
- [ ] Add more harmonic patterns
- [ ] Enhance execution layer
- [ ] Real-time WebSocket feeds
