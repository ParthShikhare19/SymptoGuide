"""Application configuration management"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "SymptoGuide API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # ML Model
    MODEL_PATH: str = "ml_artifacts/models"
    MODEL_VERSION: str = "v1"
    ENABLE_MODEL_CACHE: bool = True
    
    # Redis Cache (optional)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600
    ENABLE_CACHE: bool = False
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Model Training
    TRAINING_DATA_PATH: str = "data/cleaned_datasets"
    TEST_SIZE: float = 0.2
    RANDOM_STATE: int = 42
    CV_FOLDS: int = 5
    
    # Feature Engineering
    USE_SMOTE: bool = True
    AUGMENTATION_FACTOR: int = 3
    ENABLE_INTERACTION_FEATURES: bool = True
    
    # Hyperparameter Tuning
    ENABLE_HYPERPARAM_TUNING: bool = True
    OPTUNA_TRIALS: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
