ALEMBIC = uv run alembic -c src/infrastructure/database/alembic/alembic.ini

.PHONY: run run-broker migrate downgrade revision test lint format

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

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .
