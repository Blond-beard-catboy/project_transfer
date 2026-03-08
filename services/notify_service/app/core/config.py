from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Название сервиса (переопределить в каждом сервисе)
    SERVICE_NAME: str = "template"
    
    # База данных
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "template_db"
    CARGO_SERVICE_URL: str = "http://localhost:8001"
    ROUTE_SERVICE_URL: str = "http://localhost:8002"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8004"  # пока не используется
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # JWT (для тех сервисов, где нужна проверка)
    JWT_SECRET: str = "super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # разрешить лишние переменные окружения

@lru_cache
def get_settings() -> Settings:
    return Settings()