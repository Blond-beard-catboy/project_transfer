from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    SERVICE_NAME: str = "api_gateway"
    JWT_SECRET: str = "super-secret-key"
    JWT_ALGORITHM: str = "HS256"

    USER_SERVICE_URL: str = "http://localhost:8000"
    CARGO_SERVICE_URL: str = "http://localhost:8001"
    ROUTE_SERVICE_URL: str = "http://localhost:8002"
    ORDER_SERVICE_URL: str = "http://localhost:8003"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8004"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()