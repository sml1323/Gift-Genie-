"""
Gift Genie - Configuration Management
Environment variables and application settings
"""

import os
from typing import Optional
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings from environment variables"""
    
    # API Configuration
    app_name: str = "Gift Genie API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Configuration
    cors_origins: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://gift-genie.vercel.app"
    ]
    
    # API Keys
    openai_api_key: Optional[str] = None
    naver_client_id: Optional[str] = None
    naver_client_secret: Optional[str] = None
    
    # API Limits
    max_recommendations: int = 5
    api_timeout: int = 30
    rate_limit_per_minute: int = 10
    
    # Logging
    log_level: str = "INFO"
    
    def __init__(self, **kwargs):
        # Load from environment variables if not provided
        env_values = {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "naver_client_id": os.getenv("NAVER_CLIENT_ID"),
            "naver_client_secret": os.getenv("NAVER_CLIENT_SECRET"),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "host": os.getenv("HOST", "0.0.0.0"),
            "port": int(os.getenv("PORT", "8000")),
        }
        
        # Update with environment values
        for key, value in env_values.items():
            if value is not None and key not in kwargs:
                kwargs[key] = value
        
        super().__init__(**kwargs)


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def is_simulation_mode() -> bool:
    """Check if application is running in simulation mode"""
    return (
        not settings.openai_api_key or
        settings.openai_api_key == "your-openai-api-key-here"
    )


def get_api_status() -> dict:
    """Get API service status"""
    return {
        "openai": {
            "configured": bool(settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here"),
            "simulation_mode": not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here"
        },
        "naver_shopping": {
            "configured": bool(settings.naver_client_id and settings.naver_client_secret),
            "simulation_mode": not settings.naver_client_id or not settings.naver_client_secret
        },
        "simulation_mode": is_simulation_mode()
    }