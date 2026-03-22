# Technical Analysis Module - PRD

## Original Problem Statement
Подними проект из репозитория https://github.com/solyankastayl-cyber/ccccq. Работаем только с модулем теханализа. Реализовать функционал "Save Idea" — сохранение прогноза с возможностью обновления и отслеживания.

## Architecture
- **Backend**: FastAPI + MongoDB (modules/ta_engine/ideas/)
- **Frontend**: React + styled-components (modules/cockpit/)
- **Key Files**:
  - Backend: idea_routes.py, idea_service.py, models.py, repository.py
  - Frontend: IdeasPanel.jsx, HypothesesView.jsx, TechAnalysisModule.jsx, setupService.js

## Core Requirements
1. ✅ Save trading idea with technical analysis snapshot
2. ✅ Update idea (create new version with fresh analysis)
3. ✅ Validate idea predictions against market outcome
4. ✅ View idea timeline (versions + validations)
5. ✅ List and filter saved ideas
6. ✅ Delete ideas

## What's Been Implemented (March 22, 2026)
### Backend
- POST /api/ta/ideas - Create idea
- GET /api/ta/ideas - List ideas with filters
- GET /api/ta/ideas/{id} - Get idea details
- POST /api/ta/ideas/{id}/update - Update with new version
- POST /api/ta/ideas/{id}/validate - Validate predictions
- GET /api/ta/ideas/{id}/timeline - Timeline view
- DELETE /api/ta/ideas/{id} - Delete idea

### Frontend
- IdeasPanel component (list, expand, update, validate, delete)
- Integration into HypothesesView (sidebar panel)
- Save Idea button in TechAnalysisModule header
- Toast notifications for user feedback
- setupService extended with Ideas API methods

## Testing Results
- Backend: 100% (8/8 tests passed)
- Frontend: 100% (6/6 features tested)

## User Personas
- Traders using technical analysis for market predictions
- Portfolio managers tracking prediction accuracy

## Backlog (P1/P2 Features)
- P1: Tags filtering in IdeasPanel
- P1: Notes editing for ideas
- P2: Export ideas to CSV/PDF
- P2: Share ideas with team
- P2: Historical accuracy analytics dashboard

## Next Tasks
1. Implement tags filtering UI
2. Add notes editing in expanded view
3. Accuracy tracking visualization
