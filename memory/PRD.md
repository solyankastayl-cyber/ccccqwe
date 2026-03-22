# Technical Analysis Module - PRD

## Original Problem Statement
Подними проект из репозитория https://github.com/solyankastayl-cyber/ccccq. Работаем только с модулем теханализа. 
1. Реализовать функционал "Save Idea" — сохранение прогноза с возможностью обновления и отслеживания.
2. Полный аудит индикаторов — 144 индикатора в системе
3. UI полировка — семантика RSI/MACD, research-язык вместо trading-языка
4. P2: Визуальная иерархия — график dominant, control bar, Story Line

## Architecture
- **Backend**: FastAPI + MongoDB
- **Frontend**: React + styled-components
- **Modules**: TA Engine, Exchange Intelligence, Microstructure, Macro Context, Capital Flow, Regime, Patterns

## What's Been Implemented (March 22, 2026)

### Session 1: Save Idea Feature ✅
- CRUD API for ideas with versioning + validation + timeline

### Session 2: Indicator Audit ✅
- Full audit: 144 indicators across all modules
- 122 working, 22 need implementation

### Session 3: P1 — Semantic Polish ✅
- RSI/MACD interpretation fixed
- Research language (no trading jargon)

### Session 4: P2 — Visual Hierarchy ✅
- **Graph dominant**: structure lines 50% opacity, 1.5px (was 3px)
- **RSI/MACD → IndicatorControlBar**: inline pill toggles
- **Story Line**: Market narrative chain with phase indicator
- **Compact spacing**: -30% vertical gaps
- **Context + Setup**: unified compact blocks

## P2 Checklist
- [x] Graph = most important visual
- [x] Overlays subdued (opacity 50%, thinner lines)
- [x] RSI/MACD as control layer (pills, not cards)
- [x] Vertical spacing reduced
- [x] Story Line added (Market Story → Phase)
- [ ] Context + Setup fully merged (partial)
- [ ] TA Brain / Confluence simplified (pending)
- [ ] Empty states (pending)

## Next Tasks (P3)
1. Empty states for all blocks
2. TA Brain — show only top 3 drivers
3. Sync conclusions across blocks
4. Analysis block as final research note

## Files Changed
- ResearchChart.jsx: structure lines opacity/width
- IndicatorControlBar.jsx: NEW — pill toggles
- StoryLine.jsx: NEW — narrative chain
- ResearchViewNew.jsx: integrated components, compact spacing
