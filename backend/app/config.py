from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    allowed_origins: list[str] = ["http://localhost:5173"]
    max_response_size_mb: int = 10
    request_timeout_seconds: int = 10


settings = Settings()
