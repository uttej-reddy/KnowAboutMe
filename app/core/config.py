from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    APP_NAME: str = "Portfolio"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # API Keys (optional)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Database
    DATABASE_URL: str = "sqlite:///./portfolio.db"

    # Vector DB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"

    # Documents directory (for local document loading)
    DOCUMENTS_DIR: str = "./data/documents"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
