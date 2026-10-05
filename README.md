# basis

## Запуск

```bash
cp .env.example .env
uv sync
docker compose up -d postgres rabbitmq
make migrate
make run            # HTTP: http://localhost:8000/docs
make run-broker     # подписчики RabbitMQ (отдельный процесс)
```

Целиком в Docker: `docker compose up --build`.
