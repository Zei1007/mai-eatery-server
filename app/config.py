from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./mai_eatery.db"
    JWT_SECRET: str = "change-me-in-production"
    JWT_EXPIRE_MINUTES: int = 480
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env"}


settings = Settings()
