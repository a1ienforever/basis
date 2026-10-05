from pydantic import BaseModel
from sqlalchemy import URL


class PostgresSettings(BaseModel):
    """Настройки подключения к PostgreSQL.

    Attributes:
        host: хост сервера БД.
        port: порт сервера БД.
        user: имя пользователя.
        password: пароль пользователя.
        db: имя базы данных.
    """

    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    db: str = "basis"

    @property
    def url(self) -> URL:
        """Собрать URL подключения для драйвера asyncpg.

        Returns:
            URL подключения SQLAlchemy.
        """
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.db,
        )
