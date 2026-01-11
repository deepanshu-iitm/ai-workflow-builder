import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Workflow Builder"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://workflow_user:workflow_pass@localhost:5432/workflow_db"
    
    # Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"
    
    # SerpAPI
    SERPAPI_API_KEY: str = ""
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"
    
    # File Upload
    UPLOAD_DIRECTORY: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
