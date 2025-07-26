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
    brave_search_api_key: Optional[str] = None
    apify_api_key: Optional[str] = None
    
    # API Limits
    max_recommendations: int = 5
    api_timeout: int = 30
    rate_limit_per_minute: int = 10
    
    # MCP Configuration
    enable_mcp_pipeline: bool = True
    enable_brave_search: bool = True
    enable_apify_scraping: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    def __init__(self, **kwargs):
        # Load from environment variables if not provided
        env_values = {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "brave_search_api_key": os.getenv("BRAVE_SEARCH_API_KEY"),
            "apify_api_key": os.getenv("APIFY_API_KEY"),
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
        settings.openai_api_key == "your-openai-api-key-here" or
        not settings.brave_search_api_key or
        not settings.apify_api_key
    )


def get_api_status() -> dict:
    """Get API service status"""
    return {
        "openai": {
            "configured": bool(settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here"),
            "simulation_mode": not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here"
        },
        "brave_search": {
            "configured": bool(settings.brave_search_api_key),
            "enabled": settings.enable_brave_search
        },
        "apify": {
            "configured": bool(settings.apify_api_key),
            "enabled": settings.enable_apify_scraping
        },
        "mcp_pipeline": {
            "enabled": settings.enable_mcp_pipeline,
            "simulation_mode": is_simulation_mode()
        }
    }