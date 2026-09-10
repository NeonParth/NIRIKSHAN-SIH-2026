# Development Guide: NIRIKSHAN

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js (latest LTS)

### Local Development

1. **Environment Setup**
   ```bash
   cp .env.example .env
   # Update .env with your database credentials
   ```

2. **Launching the Stack**
   ```bash
   docker-compose up --build
   ```
   This will start the PostGIS database, FastAPI backend, and Vite frontend.

3. **Database Migrations**
   The application uses Alembic for migrations. To apply changes:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

4. **Seeding Demo Data**
   Canonical seed (idempotent on DEMO-001; labelled `data_source=SYNTHETIC`):
   ```bash
   docker compose exec backend python -m app.seed
   ```

## Development Workflow

### Backend
- API documentation is available at `/docs`.
- Tests can be run using `pytest` inside the backend container.

### Frontend
- The frontend runs in development mode with hot-reload via Vite.
- Components are organized by feature in `src/components/`.

## Contribution Rules
- Follow the **Golden Product Principles**: No "fraud" claims; only "risk signals."
- All new signals must be registered in `config/risk_weights.yaml`.
- Ensure every risk assessment remains explainable.
