# NIRIKSHAN

Evidence-driven risk analysis platform for identifying **potential anomalies** in MPLADS-style project records.

NIRIKSHAN does **not** automatically establish fraud or wrongdoing. Assessments produce explainable **risk signals** for human verification.

Phase 1 is a foundation: data model, APIs, deterministic risk engine, synthetic demo data, and a government-monitoring UI.

## Currently implemented (Phase 1)

- PostGIS-backed project, evidence, tender, contractor, award, and risk tables
- FastAPI `/api/v1` with pagination, provenance fields, and OpenAPI at `/docs`
- YAML-configured rule-based risk engine (no ML models)
- React + TypeScript + Vite + Tailwind + Leaflet UI
- Synthetic demo dataset labelled `data_source=SYNTHETIC`
- Human review status updates (no production authentication)
- Alembic migrations, pytest, Vitest, GitHub Actions CI, Docker Compose files

## Planned (not implemented)

- Production ML / computer vision / NLP pipelines
- Official MPLADS API ingestion
- GIS duplication beyond simple distance
- Graph database relationship analysis
- Blockchain, Kafka, Kubernetes, Neo4j
- Production SSO, RBAC, audit log, rate limiting, object storage

## Quick start

### Docker (recommended when Docker is installed)

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000/docs
- Health: http://localhost:8000/health
- UI: http://localhost:5173

### Local (without Docker)

1. Start a PostGIS-enabled PostgreSQL instance.
2. Copy `.env.example` to `.env` and set `DATABASE_URL`.
3. Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

4. Frontend (requires Node.js 20+):

```bash
cd frontend
npm install
npm run dev
```

## Important language

Use: potential anomaly, high risk, requires verification.

Do not use: fraud detected, MP is corrupt, contractor is corrupt, fraud proved.

## Documentation

- [Architecture](docs/PROJECT_ARCHITECTURE.md)
- [Data model](docs/DATA_MODEL.md)
- [Risk engine](docs/RISK_ENGINE.md)
- [Development](docs/DEVELOPMENT.md)
- [API](docs/API.md)
