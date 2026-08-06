"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """App configuration via .env file or environment variables."""


    # NVIDIA NIM
    nvidia_nim_api_key: str = ""
    nvidia_nim_model: str = "nvidia/nemotron-3-super-120b-a12b"
    nvidia_max_concurrent_requests: int = 5

    # Database
    database_url: str = "sqlite+aiosqlite:///./forecast.db"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Upload
    max_upload_size_mb: int = 50

    # Paths
    upload_dir: Path = Path("uploads")
    report_dir: Path = Path("reports")

    model_config = {
        "env_file": ["../.env", ".env"],
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    def ensure_dirs(self):
        """Create upload and report directories if they don't exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
