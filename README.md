# Netra Prototype

This is a minimal prototype of the Netra admin platform with a FastAPI backend and a static HTML/JS admin dashboard.

## Run locally (no Docker)

- Prereqs: Python 3.11+
- Backend:
  ```bash
  cd backend
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload --port 8000
  ```
- Frontend: open `frontend/index.html` directly in a browser or serve via a static server (e.g., `npx serve frontend`). The page assumes backend at `http://localhost:8000`.

## Run with Docker Compose

```bash
docker compose up --build
```
- Backend at `http://localhost:8000/healthz`
- Frontend at `http://localhost:8080/`

## What’s included
- FastAPI endpoints: health, cameras (list/create), signal control (mode/set/state), simple ingest for violations, pending challans, create challan.
- In-memory stores for quick demo.
- Minimal admin UI to test flows: add camera, set mode/phase, seed violation, issue challan.

## Next steps
- Secure endpoints (OAuth2/JWT), role-based UI.
- Persist to Postgres/TimescaleDB.
- Add map view with junction overlays.
- Integrate with the OpenAPI spec (`docs/api/openapi.yaml`).
