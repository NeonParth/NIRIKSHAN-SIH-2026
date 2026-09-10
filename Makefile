.PHONY: test backend-test frontend-test up down migrate seed

up:
	docker compose up --build

down:
	docker compose down

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m app.seed

backend-test:
	cd backend && python -m pytest -q

frontend-test:
	cd frontend && npm test

test: backend-test frontend-test
