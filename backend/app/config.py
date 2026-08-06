"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """App configuration via .env file or environment variables."""

    # NVIDIA NIM
    nvidia_api_key: str = ""
    nvidia_model: str = "nvidia/llama-3.3-nemotron-super-49b-v1"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"

    # Google Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

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
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    def ensure_dirs(self):
        """Create upload and report directories if they don't exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
