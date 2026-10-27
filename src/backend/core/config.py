from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Newspaper Distribution System"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    secret_key: str = "change-me-in-production-use-a-long-random-string"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/newsdb"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    access_token_expire_minutes: int = 60

    session_dir: str = ".sessions"
    session_checkpoint_interval_seconds: int = 300


settings = Settings()
