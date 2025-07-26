"""
Gift Genie - Health Check Router
Health check endpoints for monitoring and status
"""

import os
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    version: str
    services: dict


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        services={
            "api": "running",
            "openai": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured",
            "brave_search": "configured" if os.getenv("BRAVE_SEARCH_API_KEY") else "not_configured",
            "apify": "configured" if os.getenv("APIFY_API_KEY") else "not_configured"
        }
    )


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with more information"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": {
            "python_version": "3.9+",
            "fastapi_version": "0.104+",
            "deployment": os.getenv("ENVIRONMENT", "development")
        },
        "services": {
            "api_server": "running",
            "openai_api": {
                "configured": bool(os.getenv("OPENAI_API_KEY")),
                "model": "gpt-4o-mini"
            },
            "brave_search": {
                "configured": bool(os.getenv("BRAVE_SEARCH_API_KEY")),
                "endpoint": "https://api.search.brave.com/res/v1/web/search"
            },
            "apify_scraping": {
                "configured": bool(os.getenv("APIFY_API_KEY")),
                "endpoint": "https://api.apify.com/v2"
            }
        },
        "features": {
            "ai_recommendations": True,
            "mcp_pipeline": True,
            "product_search": True,
            "detail_scraping": True
        }
    }