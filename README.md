# DevOps

Репозиторий для лабораторных по дисциплине DevOps.

## Services
- `backend/` - FastAPI REST API for detector profiles, traffic ingest, monitoring, detections, generator jobs
- `frontend/` - React web client (react-scripts runtime, no Vite)
- `ml-service/` - FastAPI ML inference service
- `postgres` - durable operational store for detector/detection/generator domain
- `influxdb` - time-series store for traffic points

## Quick Start
1. Build and start stack:
   - `docker compose up -d --build`
2. Open frontend:
   - `http://localhost:3000`
3. API docs:
   - `http://localhost:8000/docs`

Detailed feature validation steps:
- `specs/001-rework-detector-workflow/quickstart.md`

## Local Validation
1. Frontend unit tests + build:
   - `cd frontend && npm run typecheck && npm test && npm run build`
2. Backend tests:
   - `PYTHONPATH=. .venv/bin/python -m pytest -q backend/tests`
3. ML service tests:
   - `PYTHONPATH=ml-service .venv/bin/python -m pytest -q ml-service/tests`

## Engineering Governance
Проектные правила разработки и качества закреплены в
`.specify/memory/constitution.md`.
