"""
Gift Genie - Recommendations Router
API endpoints for gift recommendations
"""

import os
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from models.request.recommendation import GiftRequest
from models.response.recommendation import EnhancedRecommendationResponse, RecommendationResponse
from services.ai.recommendation_engine import GiftRecommendationEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize engines (will be moved to dependency injection later)
def get_basic_engine():
    """Get basic recommendation engine instance"""
    return GiftRecommendationEngine(
        api_key=os.getenv("OPENAI_API_KEY", "")
    )

def get_naver_engine():
    """Get Naver Shopping recommendation engine instance"""
    from services.ai.naver_recommendation_engine import NaverGiftRecommendationEngine
    return NaverGiftRecommendationEngine(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        naver_client_id=os.getenv("NAVER_CLIENT_ID", ""),
        naver_client_secret=os.getenv("NAVER_CLIENT_SECRET", "")
    )




@router.post("/recommendations/basic", response_model=RecommendationResponse)
async def create_basic_recommendations(
    request: GiftRequest,
    background_tasks: BackgroundTasks
):
    """
    Create basic gift recommendations using AI only
    
    This endpoint provides faster recommendations using only AI generation,
    without product search and scraping. Ideal for quick responses.
    """
    try:
        logger.info(f"Basic recommendation request: {request.recipient_age}yo {request.recipient_gender}, budget ${request.budget_min}-{request.budget_max}")
        
        engine = get_basic_engine()
        response = await engine.generate_recommendations(request)
        
        # Log metrics in background
        if response.success:
            background_tasks.add_task(
                log_basic_metrics,
                response.request_id,
                response.total_processing_time,
                len(response.recommendations)
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Basic recommendation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "recommendation_failed",
                "message": "Failed to generate recommendations. Please try again.",
                "suggestions": [
                    "Check your input parameters",
                    "Try with a different budget range",
                    "Simplify your interests list"
                ]
            }
        )


@router.post("/recommendations", response_model=EnhancedRecommendationResponse)
async def create_recommendations(
    request: GiftRequest,
    background_tasks: BackgroundTasks
):
    """
    Create gift recommendations (default endpoint - uses Naver Shopping)
    
    This endpoint redirects to the Naver Shopping API endpoint for
    real product recommendations with Korean market integration.
    """
    # Redirect to Naver Shopping endpoint for best results
    return await create_naver_recommendations(request, background_tasks)


@router.post("/recommendations/enhanced", response_model=EnhancedRecommendationResponse)
async def create_enhanced_recommendations(
    request: GiftRequest,
    background_tasks: BackgroundTasks
):
    """
    Create enhanced gift recommendations (legacy frontend compatibility)
    
    This endpoint provides the same functionality as /recommendations/naver
    but maintains compatibility with older frontend versions.
    """
    # Use the same Naver Shopping implementation
    return await create_naver_recommendations(request, background_tasks)


@router.get("/recommendations/{request_id}")
async def get_recommendation_status(request_id: str):
    """
    Get recommendation status by request ID
    (For future implementation - currently returns not found)
    """
    # This would be implemented with a database/cache in production
    raise HTTPException(
        status_code=404,
        detail={
            "error": "not_implemented",
            "message": "Recommendation history lookup not yet implemented",
            "request_id": request_id
        }
    )




async def log_basic_metrics(request_id: str, processing_time: float, recommendation_count: int):
    """Background task to log basic recommendation metrics"""
    logger.info(f"Basic recommendation metrics for {request_id}:")
    logger.info(f"  - Total time: {processing_time:.2f}s")
    logger.info(f"  - Recommendations: {recommendation_count}")


@router.post("/recommendations/naver", response_model=EnhancedRecommendationResponse)
async def create_naver_recommendations(
    request: GiftRequest,
    background_tasks: BackgroundTasks
):
    """
    Create gift recommendations using Naver Shopping API
    
    This endpoint uses direct Naver Shopping API integration:
    1. AI-powered recommendation generation
    2. Real product search via Naver Shopping API
    3. Price comparison and optimization
    4. Integration of AI recommendations with real products
    
    Benefits:
    - Real Korean products with actual purchase links
    - Accurate pricing in KRW (converted to USD for compatibility)
    - No MCP dependencies, faster response time
    - Better local market relevance
    """
    try:
        logger.info(f"Naver Shopping recommendation request: {request.recipient_age}yo {request.recipient_gender}, budget ${request.budget_min}-{request.budget_max}")
        
        engine = get_naver_engine()
        response = await engine.generate_naver_recommendations(request)
        
        # Log metrics in background
        if response.success:
            background_tasks.add_task(
                log_naver_metrics,
                response.request_id,
                response.pipeline_metrics,
                len(response.recommendations)
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Naver Shopping recommendation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "naver_recommendation_failed",
                "message": "Failed to generate Naver Shopping recommendations. Please try again.",
                "fallback_suggestion": "Try the basic recommendations endpoint: /api/v1/recommendations/basic",
                "naver_api_required": "Ensure NAVER_CLIENT_ID and NAVER_CLIENT_SECRET are set"
            }
        )


async def log_naver_metrics(request_id: str, metrics, recommendation_count: int):
    """Background task to log Naver Shopping recommendation metrics"""
    logger.info(f"Naver Shopping metrics for {request_id}:")
    logger.info(f"  - Total time: {metrics.total_time:.2f}s")
    logger.info(f"  - AI generation: {metrics.ai_generation_time:.2f}s")
    logger.info(f"  - Naver search: {metrics.search_execution_time:.2f}s")
    logger.info(f"  - Integration: {metrics.integration_time:.2f}s")
    logger.info(f"  - Recommendations: {recommendation_count}")
    logger.info(f"  - Search results: {metrics.search_results_count}")
    logger.info(f"  - Simulation mode: {metrics.cache_simulation}")


# Note: Exception handlers should be added to the main app, not router