from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    SERVER_NAME: str = "localhost"
    SERVER_HOST: str = "http://localhost"

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost:4200","http://localhost:3000"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # Frontend development
        "http://localhost:5173",  # Vite dev server
        "https://pitline-corner-frontend.vercel.app",  # Vercel production
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Pitline Corner"
    VERSION: str = "1.0.0"

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "pitline_corner"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        values = info.data if hasattr(info, "data") else {}
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER", "postgres"),
            password=values.get("POSTGRES_PASSWORD", "postgres"),
            host=values.get("POSTGRES_SERVER", "localhost"),
            port=values.get("POSTGRES_PORT", "5432"),
            path=f"/{values.get('POSTGRES_DB', 'pitline_corner') or ''}",
        )

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Test database
    TEST_DATABASE_URL: Optional[str] = None

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "production"

    model_config = {"env_file": ".env"}


settings = Settings()
