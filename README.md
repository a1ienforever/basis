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

## Запуск в Docker

```bash
cp .env.example .env
make up             # docker compose up --build -d
make logs
make down
```

Сервисы: `postgres`, `rabbitmq`, `migrate` (разово применяет миграции), `api`, `broker`.
Имя compose-проекта, образа и контейнеров задаёт `APP_NAME` из `.env`:
`<APP_NAME>-api`, `<APP_NAME>-broker`, `<APP_NAME>-migrate`, `<APP_NAME>-postgres`, `<APP_NAME>-rabbitmq`.
Порты на хосте — `HTTP_PORT`, `POSTGRES_PORT`, `RABBIT_PORT`, `RABBIT_MANAGEMENT_PORT`.

## Обработка платежей

Процесс `broker` читает очередь `RABBIT_QUEUE`: проводит платёж через эмулятор шлюза
(`GATEWAY_*`: задержка 2–5 с, 90% успеха), сохраняет статус и отправляет webhook на `webhook_url`.
Неудачная попытка повторяется с экспоненциальной задержкой (`CONSUMER_RETRY_DELAY`, затем вдвое больше);
после `CONSUMER_MAX_ATTEMPTS` попыток сообщение попадает в `RABBIT_DLQ`.
