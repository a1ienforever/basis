ALEMBIC = uv run alembic -c src/infrastructure/database/alembic/alembic.ini

.PHONY: up down logs run run-broker migrate downgrade revision requirements test lint format

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

run:
	uv run uvicorn src.web_server:app --reload

run-broker:
	uv run python -m src.broker

migrate:
	$(ALEMBIC) upgrade head

downgrade:
	$(ALEMBIC) downgrade -1

# make revision m="add something"
revision:
	$(ALEMBIC) revision --autogenerate -m "$(m)"

# обновить requirements.txt для сборки образа после изменения зависимостей
requirements:
	uv export --frozen --no-dev --no-hashes --no-emit-project --no-annotate -o requirements.txt

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .
