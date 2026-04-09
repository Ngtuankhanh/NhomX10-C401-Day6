from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    openai_api_key: str | None = None
    frontend_origin: str = "http://localhost:3000"
    booking_mode: str = "mock"
    default_language: str = "vi"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
