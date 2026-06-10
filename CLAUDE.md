# VisionGrid — Developer Guide

## Project Overview
VisionGrid is an open-source real-time computer vision platform. Multi-protocol camera ingestion + YOLO detection + privacy-first architecture.

## Tech Stack
- Backend: Python 3.11+ / FastAPI / OpenCV / Ultralytics YOLO
- Frontend: Next.js 14+ / TypeScript / Tailwind CSS
- Infra: Docker Compose / PostgreSQL / Redis

## Commands

```bash
# Backend
cd backend && pip install -e ".[dev]"
pytest                          # Run tests
ruff check .                    # Lint
ruff format .                   # Format
mypy .                          # Type check
visiongrid serve                # Run dev server

# Frontend
cd frontend && npm install
npm run dev                     # Dev server on :3000
npm run build                   # Production build
npm run lint                    # ESLint
npm test                        # Jest/Vitest tests
```

## Architecture Principles
- Edge-first: all detection runs locally, cloud is optional
- Hardware-agnostic: any camera over RTSP/ONVIF/USB/HTTP
- Privacy-by-design: no raw video leaves the local network
- Extensible: plugin system for models, alerts, integrations

## Conventions
- Python: Ruff formatting, type hints required, async-first
- TypeScript: strict mode, functional components, no any
- Commits: Conventional Commits (feat/fix/docs/refactor/test/chore)
- API: RESTful with /api/v1/ prefix, WebSocket for real-time events
