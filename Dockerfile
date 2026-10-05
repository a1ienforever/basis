FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY src ./src

CMD ["sh", "-c", "alembic -c src/infrastructure/database/alembic/alembic.ini upgrade head && uvicorn src.web_server:app --host 0.0.0.0 --port 8000"]
