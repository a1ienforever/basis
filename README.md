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

## Аутентификация

Все эндпоинты `/api/v1/*` требуют статический ключ из `AUTH_API_KEY` в заголовке `X-API-Key`;
без него или с неверным ключом возвращается `401`. `/health`, `/docs` и `/openapi.json` открыты.

```bash
curl -H "X-API-Key: $AUTH_API_KEY" localhost:8000/api/v1/payments/<payment_id>
```

## Примеры запросов

Полная схема запросов и ответов — в `/docs`.

### Создание платежа

Заголовок `Idempotency-Key` обязателен: повторный запрос с тем же ключом не создаёт
новый платёж, а возвращает уже созданный.

```bash
curl -i -X POST localhost:8000/api/v1/payments \
  -H "X-API-Key: $AUTH_API_KEY" \
  -H "Idempotency-Key: order-42" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "1500.00",
    "currency": "RUB",
    "description": "Заказ №42",
    "metadata": {"order_id": 42, "source": "web"},
    "webhook_url": "http://localhost:9000/webhooks/payments"
  }'
```

`202 Accepted`:

```json
{
  "payment_id": "0b4e0e5e-2f6a-4c0a-9f7e-6a1b2c3d4e5f",
  "status": "pending",
  "created_at": "2026-10-06T12:00:00.123456+00:00"
}
```

Ограничения полей: `amount` — положительное число с не более чем двумя знаками после
запятой, `currency` — `RUB`, `USD` или `EUR`, `description` — до 255 символов,
`webhook_url` — схема `http` или `https`, до 2048 символов, `metadata` — любой JSON-объект.

### Получение информации о платеже

```bash
curl -s localhost:8000/api/v1/payments/0b4e0e5e-2f6a-4c0a-9f7e-6a1b2c3d4e5f \
  -H "X-API-Key: $AUTH_API_KEY"
```

`200 OK`:

```json
{
  "payment_id": "0b4e0e5e-2f6a-4c0a-9f7e-6a1b2c3d4e5f",
  "amount": "1500.00",
  "currency": "RUB",
  "description": "Заказ №42",
  "metadata": {"order_id": 42, "source": "web"},
  "status": "succeeded",
  "webhook_url": "http://localhost:9000/webhooks/payments",
  "created_at": "2026-10-06T12:00:00.123456+00:00",
  "processed_at": "2026-10-06T12:00:03.654321+00:00"
}
```

### Webhook-уведомление

После обработки платежа `broker` отправляет `POST` на `webhook_url` с телом:

```json
{
  "payment_id": "0b4e0e5e-2f6a-4c0a-9f7e-6a1b2c3d4e5f",
  "status": "succeeded",
  "amount": "1500.00",
  "currency": "RUB",
  "description": "Заказ №42",
  "metadata": {"order_id": 42, "source": "web"},
  "processed_at": "2026-10-06T12:00:03.654321+00:00"
}
```

Получателя для проверки можно поднять одной командой:

```bash
python -m http.server 9000     # или любой приёмник, отвечающий 2xx
```

Из контейнера `broker` сервис на хосте доступен как `http://host.docker.internal:9000`.

### Коды ошибок

| Код | Когда |
| --- | --- |
| `401` | нет заголовка `X-API-Key` или ключ неверный |
| `404` | платежа с таким `payment_id` нет |
| `409` | платёж с таким `Idempotency-Key` создан параллельным запросом |
| `422` | нет заголовка `Idempotency-Key` или тело не прошло валидацию схемы |
| `400` | данные платежа не прошли доменную валидацию (сумма, валюта, URL, описание) |

Тело ответа с ошибкой — `{"detail": "<описание>"}`.

## Обработка платежей

Процесс `broker` читает очередь `RABBIT_QUEUE`: проводит платёж через эмулятор шлюза
(`GATEWAY_*`: задержка 2–5 с, 90% успеха), сохраняет статус и отправляет webhook на `webhook_url`.
Запрос к шлюзу уходит с заголовком `Idempotency-Key` платежа — тем же, с которым платёж пришёл
от клиента, чтобы шлюз мог отбросить повторный запрос и не списать средства заново.
Неудачная попытка повторяется с экспоненциальной задержкой (`CONSUMER_RETRY_DELAY`, затем вдвое больше);
после `CONSUMER_MAX_ATTEMPTS` попыток сообщение попадает в `RABBIT_DLQ`.
