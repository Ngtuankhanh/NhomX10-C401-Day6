from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    openai_api_key: str | None = None
    frontend_origin: str = "http://localhost:3000"
    booking_mode: str = "mock"
    default_language: str = "vi"
    agent_model: str = "gpt-4o"
    specialist_model: str = "gpt-4o-mini"
    judge_model: str = "gpt-4o-mini"
    observability_dir: Path = BACKEND_DIR / "runtime"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
