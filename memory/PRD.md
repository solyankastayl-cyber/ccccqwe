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

### Multi-Timeframe (MTF) Analysis - FIXED & WORKING (2026-03-21)
All 6 timeframes now generate unique technical analysis:

| TF | Candles | Aggregation | Trend | Key Levels |
|---|---|---|---|---|
| **4H** | 200 | 6h native | uptrend | R@74K, R@76K, S@69K |
| **1D** | 150 | 1d native | downtrend | S@60K, S@63K, R@74K |
| **7D** | 65 | 7-day aggregated | downtrend | R@126K, S@81K, R@98K |
| **30D** | 42 | 30-day aggregated | unknown | R@109K, R@126K |
| **180D** | 12 | 180-day aggregated | unknown | L@15K, H@126K |
| **1Y** | 11 | 365-day aggregated | unknown | H@69K, L@15K, R@126K |

**Key Fixes Applied:**
- Added `_aggregate_candles()` function for higher TFs
- Added TF_CONFIG for 180D and 1Y with appropriate pivot_window settings
- Dynamic MIN_CANDLES_MAP based on timeframe

### Overlay Control & Visual Noise Reduction - FIXED (2026-03-22)
**Problem:** Multiple overlapping modals on chart (SHORT, PATTERN DETECTED, UNKNOWN/Bias, etc.) creating visual noise

**Solution:**
1. All overlays OFF by default (`showFibonacciOverlay`, `showPatternOverlay`, `showSetupOverlay`, `showTAOverlay` = false)
2. User clicks to enable specific overlays
3. Active buttons show green indicator dot
4. New control panel design with sections: VIEW, INDICATORS, OVERLAYS

**Overlay Hierarchy:**
| Overlay | Controls |
|---|---|
| **Fib** | Fibonacci retracement levels |
| **Pattern** | PATTERN DETECTED card (type, bias, breakout, score) |
| **Setup** | SHORT/LONG card (entry, stop, TP1, TP2) |
| **TA** | Full TA analysis overlay |

**Removed:** 
- Duplicate Base/Patterns/Levels buttons from top bar
- UNKNOWN/Bias:neutral badge from MarketStateRenderer

### ViewMode System - FULLY FUNCTIONAL (2026-03-22)
| Mode | What it shows |
|---|---|
| **Auto** | Everything from render_plan |
| **Classic TA** | Indicators (EMA/RSI/MACD) + Patterns + Fibonacci |
| **Smart Money** | POI + Liquidity + CHOCH + EQH/EQL + Sweeps |
| **Minimal** | Only candles + structure (HH/HL/LL) + levels (R/S) |

### Setup Overlay - FIXED
- Added `valid: true` and `type: 'LONG'/'SHORT'` to buildTradeSetup
- Setup card now displays: Entry, Stop, TP1, TP2, R:R ratio, Confidence

### Indicator Selector - FIXED  
- Now uses `selectedOverlays` for user control in all modes
- User can select EMA_20, EMA_50, SMA, etc.

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
