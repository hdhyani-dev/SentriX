"""
ChainBreak application configuration.

Loads settings from environment variables / .env file.
All settings have safe defaults so the app runs without a .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root if present
_project_root = Path(__file__).resolve().parent.parent
_env_path = _project_root / ".env"
if _env_path.exists():
    load_dotenv(_env_path)


class Settings:
    """Application settings loaded from environment variables."""

    APP_ENV: str = os.getenv("APP_ENV", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{_project_root / 'chainbreak.db'}")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # AI provider (optional)
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "")

    # Graph analysis limits
    MAX_PATH_LENGTH: int = int(os.getenv("MAX_PATH_LENGTH", "6"))
    MAX_CANDIDATE_PATHS: int = int(os.getenv("MAX_CANDIDATE_PATHS", "50"))
    MAX_GRAPH_NODES: int = int(os.getenv("MAX_GRAPH_NODES", "1000"))

    @property
    def ai_configured(self) -> bool:
        """Check if AI provider is configured with an API key."""
        return bool(self.AI_PROVIDER and self.AI_API_KEY)

    @property
    def project_root(self) -> Path:
        return _project_root


settings = Settings()
