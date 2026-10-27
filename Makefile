.PHONY: dev backend frontend migrate test lint

dev:
	make -j2 backend frontend

backend:
	PYTHONPATH=src uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	PYTHONPATH=src streamlit run src/frontend/main.py --server.port 8501

migrate:
	alembic -c config/alembic.ini upgrade head

migrate-new:
	alembic -c config/alembic.ini revision --autogenerate -m "$(msg)"

test:
	pytest tests/ -v --tb=short --cov=src --cov-report=term-missing

lint:
	ruff check src/ tests/
	mypy src/

format:
	ruff format src/ tests/

install:
	pip install -e ".[dev,frontend]"
