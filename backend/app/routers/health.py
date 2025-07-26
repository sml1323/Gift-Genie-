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
            "naver_shopping": "configured" if (os.getenv("NAVER_CLIENT_ID") and os.getenv("NAVER_CLIENT_SECRET")) else "not_configured"
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
            "naver_shopping": {
                "configured": bool(os.getenv("NAVER_CLIENT_ID") and os.getenv("NAVER_CLIENT_SECRET")),
                "endpoint": "https://openapi.naver.com/v1/search/shop.json"
            }
        },
        "features": {
            "ai_recommendations": True,
            "naver_integration": True,
            "product_search": True,
            "real_products": True
        }
    }