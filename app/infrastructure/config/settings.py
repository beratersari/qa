from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Language Learning App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = f"sqlite:///{os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))}/language_learning.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password hashing
    BCRYPT_ROUNDS: int = 12
    
    # Logging
    LOG_LEVEL: str = "INFO"  # TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: str = "logs/app.log"  # Path to log file for JSON structured logs
    LOG_CONSOLE: bool = True  # Enable console logging
    LOG_JSON_FILE: bool = True  # Use JSON format for file logs (Elasticsearch-compatible)
    
    model_config = {"env_file": ".env"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
