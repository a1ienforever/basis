from urllib.parse import quote

from pydantic import BaseModel


class RabbitSettings(BaseModel):
    host: str = "localhost"
    port: int = 5672
    user: str = "guest"
    password: str = "guest"
    vhost: str = "/"

    @property
    def url(self) -> str:
        credentials = f"{quote(self.user, safe='')}:{quote(self.password, safe='')}"
        return f"amqp://{credentials}@{self.host}:{self.port}/{self.vhost.lstrip('/')}"
