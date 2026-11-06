.PHONY: up down api worker web test lint migrate fmt install

up:
	docker compose up -d redis postgres

down:
	docker compose down

api:
	.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	.venv/bin/python -m app.worker

web:
	cd web && npm run dev

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	cp -n .env.example .env || true
	cd web && npm install

test:
	.venv/bin/pytest -q
	cd web && npm test -- --run

lint:
	.venv/bin/ruff check app tests
	cd web && npm run lint

fmt:
	.venv/bin/ruff check --fix app tests
	.venv/bin/ruff format app tests

migrate:
	.venv/bin/alembic upgrade head

stack:
	docker compose up --build -d
