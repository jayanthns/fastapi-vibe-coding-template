from typing import ClassVar, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    app_name: str = "FastAPI Vibe Coding"
    environment: str = "development"
    debug: bool = True

    # Database
    # Direct URL takes precedence if provided (env: DATABASE_URL)
    database_url: Optional[str] = None

    # Discrete credentials (envs: DATABASE_DRIVER, DATABASE_HOST, DATABASE_PORT,
    # DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    database_driver: Optional[str] = None  # e.g., "postgresql+asyncpg"
    database_host: Optional[str] = None
    database_port: Optional[int] = None
    database_username: Optional[str] = None
    database_password: Optional[str] = None
    database_name: Optional[str] = None

    # Alternate/distributed env names commonly used
    database_user: Optional[str] = None  # alias for username (e.g., DATABASE_USER)
    database_pass: Optional[str] = None  # alias for password (e.g., DATABASE_PASS)
    db_host: Optional[str] = None  # alias for host (e.g., DB_HOST)
    db_port: Optional[int] = None  # alias for port (e.g., DB_PORT)
    db_name: Optional[str] = None  # alias for name (e.g., DB_NAME)

    # CORS
    backend_cors_origins: list[str] | str = "*"

    # Pydantic v2 uses model_config; legacy Config kept for reference was removed

    @model_validator(mode="after")
    def assemble_database_url(self) -> "Settings":
        # If a full URL is provided, use it as-is
        if self.database_url:
            return self

        # Try to construct from discrete credentials if provided
        username = self.database_username or self.database_user
        password = self.database_password or self.database_pass
        name = self.database_name or self.db_name
        host = self.database_host or self.db_host or "localhost"
        port = self.database_port or self.db_port or 5432

        if name and username and password:
            driver = self.database_driver or "postgresql+asyncpg"
            self.database_url = (
                f"{driver}://{username}:{password}" f"@{host}:{port}/{name}"
            )
            return self

        # Fallback to local SQLite async database
        self.database_url = "sqlite+aiosqlite:///./app.db"
        return self

    @model_validator(mode="after")
    def normalize_cors(self) -> "Settings":
        value = self.backend_cors_origins
        if isinstance(value, str):
            if value.strip() == "*":
                self.backend_cors_origins = ["*"]
            else:
                self.backend_cors_origins = [
                    v.strip() for v in value.split(",") if v.strip()
                ]
        return self


settings = Settings()
