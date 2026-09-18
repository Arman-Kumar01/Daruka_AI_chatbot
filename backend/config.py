import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "Darukaa AI Biodiversity Intelligence System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # LLM Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto") # auto, gemini, openai, local
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    PROCESSED_FILE: Path = BASE_DIR / "data" / "processed" / "knowledge_chunks.json"
    METADATA_CATALOG: Path = BASE_DIR / "data" / "metadata" / "sources_catalog.json"
    CHROMA_PERSIST_DIR: Path = BASE_DIR / "data" / "chroma_db"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
