from urllib.parse import quote

from pydantic import BaseModel


class RabbitSettings(BaseModel):
    """Настройки подключения к RabbitMQ.

    Attributes:
        host: хост брокера.
        port: порт брокера.
        user: имя пользователя.
        password: пароль пользователя.
        vhost: виртуальный хост.
    """

    host: str = "localhost"
    port: int = 5672
    user: str = "guest"
    password: str = "guest"
    vhost: str = "/"

    @property
    def url(self) -> str:
        """Собрать AMQP URL подключения.

        Returns:
            URL подключения с экранированными учётными данными.
        """
        credentials = f"{quote(self.user, safe='')}:{quote(self.password, safe='')}"
        return f"amqp://{credentials}@{self.host}:{self.port}/{self.vhost.lstrip('/')}"
