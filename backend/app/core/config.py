import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    FRONTEND_PORT: int = 5173

    # Security
    JWT_SECRET: str = "production_super_secret_jwt_key_replace_in_prod_934184910283"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Database
    DATABASE_URL: str = "sqlite:///./claim_agent.db"

    # LLM Provider: "gemini", "openai", "anthropic", or "local"
    LLM_PROVIDER: str = "local"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    GEMINI_MODEL: str = "gemini-2.5-flash"
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # Storage
    STORAGE_DIR: str = os.path.join("backend", "data", "uploads")
    MAX_FILE_SIZE_MB: int = 25

    # Business Rules & Configurable Thresholds
    FRAUD_FLAG_THRESHOLD: int = 65
    HIGH_VALUE_THRESHOLD_INR: float = 100000.0
    MIN_CONFIDENCE_AUTO_APPROVE: float = 0.85
    MAX_SLA_HOURS_CRITICAL: int = 2
    MAX_SLA_HOURS_HIGH: int = 6
    MAX_SLA_HOURS_NORMAL: int = 24

    # Supported Languages for Customer Communication
    SUPPORTED_LANGUAGES: List[str] = ["en", "hi", "kn"]

    # External APIs
    MAPS_API_KEY: Optional[str] = None
    EMAIL_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
