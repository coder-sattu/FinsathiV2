"""Application configuration settings."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from env."""

    port: int = 8080
    database_url: str = "postgresql+asyncpg://claimbot:claimbot@localhost:5432/claimbot"
    data_dir: str = "./data"
    upload_dir: str = "./uploads"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"
    gemini_timeout_ms: int = 4000
    sarvam_api_key: str = ""
    sarvam_chat_model: str = "sarvam-105b-conversations"
    sarvam_translate_model: str = "mayura:v1"
    llm_enabled: bool = True
    doc_ai_enabled: bool = True
    doc_ai_timeout_ms: int = 20000
    max_input_chars: int = 500
    max_upload_mb: int = 5
    high_value_threshold: int = 500000
    cors_origin: str = "http://localhost:5173"
    hinglish_translation_enabled: bool = False
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = "team.finsathi@gmail.com"
    smtp_password: str = ""
    notify_email: str = "iamsatvashil@gmail.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def data_path(self) -> Path:
        # resolve data dir
        return Path(self.data_dir).resolve()

    @property
    def upload_path(self) -> Path:
        # resolve upload dir
        return Path(self.upload_dir).resolve()


settings = Settings()
