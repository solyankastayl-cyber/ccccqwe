# Technical Analysis Module - PRD

## Original Problem Statement
Подними проект из репозитория https://github.com/solyankastayl-cyber/ccccq. Работаем только с модулем теханализа. 
1. Реализовать функционал "Save Idea"
2. Полный аудит индикаторов — 144 индикатора
3. UI полировка — P1 (семантика) + P2 (визуальная иерархия)
4. **FIX PATTERN DETECTION & RENDERING** — главная проблема

## Architecture Overview
```
Backend: per_tf_builder → run_all_detectors → pattern_selector → render_plan_v2
Frontend: ResearchViewNew → ResearchChart (lightweight-charts)
```

## What Was Fixed (March 22, 2026)

### CRITICAL FIX: Pattern Detection Pipeline

**PROBLEM:** Паттерны не отображались на графике
**ROOT CAUSE:** Несколько багов в цепочке detection → geometry → render

**Fixes Applied:**

1. **`pattern_detectors_unified.py` не импортировался**
   - Добавлен импорт в `per_tf_builder.py`
   - Декораторы `@register_pattern` теперь выполняются

2. **`run_all_detectors()` вызывался с НЕПРАВИЛЬНЫМИ аргументами**
   - Было: `run_all_detectors(candles, validator, pivot_highs_raw, ...)`
   - Стало: `run_all_detectors(candles=, pivots_high=, pivots_low=, ...)`
   - `validator` передавался вместо `pivots_high`!

3. **`detect_triangles_unified` вызывал `detect_best_pattern`**
   - Это возвращало ОДИН паттерн (channel победил triangle)
   - Исправлено: вызываем каждый `validate_*_triangle` напрямую

4. **`pattern_selector` отклонял паттерны по `near_price`**
   - `MAX_PRICE_DISTANCE` было 5% — слишком строго
   - Изменено на 15%

5. **`MIN_PRIMARY_SCORE` было 0.50**
   - Изменено на 0.45 для более широкого охвата

### RESULT
- `ascending_triangle` detected: geo=0.93, conf=0.85
- Pattern selected and rendered on chart
- Story Line shows "ascending triangle"
- Geometry (lines) visible on graph

## Files Changed

### Backend
- `/app/backend/modules/ta_engine/per_tf_builder.py`
  - Fixed import of `pattern_detectors_unified`
  - Fixed `run_all_detectors()` call arguments
  
- `/app/backend/modules/ta_engine/setup/pattern_detectors_unified.py`
  - `detect_triangles_unified` now calls validators directly
  - Added detailed logging

- `/app/backend/modules/ta_engine/setup/pattern_selector.py`
  - `MAX_PRICE_DISTANCE`: 0.05 → 0.15
  - `MIN_PRIMARY_SCORE`: 0.50 → 0.45

- `/app/backend/modules/ta_engine/setup/__init__.py`
  - Added import of `pattern_detectors_unified`

### Frontend (P2)
- `/app/frontend/src/modules/cockpit/components/ResearchChart.jsx`
  - Structure lines opacity 50%, width 1.5px
  
- `/app/frontend/src/modules/cockpit/components/IndicatorControlBar.jsx`
  - NEW: RSI/MACD as pill toggles
  
- `/app/frontend/src/modules/cockpit/components/StoryLine.jsx`
  - NEW: Market narrative chain

## Testing Results
- Pattern detection: ✅ ascending_triangle found
- Pattern rendering: ✅ visible on chart
- Structure rendering: ✅ HH/HL markers visible
- Levels rendering: ✅ S/R lines visible

## Next Tasks
1. Test more pattern types (double top/bottom, head & shoulders)
2. FVG / Order Block visualization
3. Pattern expiration and recency tuning
