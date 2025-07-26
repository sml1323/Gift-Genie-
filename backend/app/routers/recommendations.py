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
from services.ai.enhanced_recommendation_engine import EnhancedGiftRecommendationEngine
from services.ai.recommendation_engine import GiftRecommendationEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize engines (will be moved to dependency injection later)
def get_enhanced_engine():
    """Get enhanced recommendation engine instance"""
    return EnhancedGiftRecommendationEngine(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        brave_api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""),
        apify_api_key=os.getenv("APIFY_API_KEY", "")
    )

def get_basic_engine():
    """Get basic recommendation engine instance"""
    return GiftRecommendationEngine(
        api_key=os.getenv("OPENAI_API_KEY", "")
    )


@router.post("/recommendations/enhanced", response_model=EnhancedRecommendationResponse)
async def create_enhanced_recommendations(
    request: GiftRequest,
    background_tasks: BackgroundTasks
):
    """
    Create enhanced gift recommendations using full MCP pipeline
    
    This endpoint uses the complete MCP (Model Context Protocol) pipeline:
    1. AI-powered recommendation generation
    2. Product search via Brave Search API
    3. Detailed product scraping via Apify
    4. Integration and enhancement of results
    """
    try:
        logger.info(f"Enhanced recommendation request: {request.recipient_age}yo {request.recipient_gender}, budget ${request.budget_min}-{request.budget_max}")
        
        engine = get_enhanced_engine()
        response = await engine.generate_enhanced_recommendations(request)
        
        # Log metrics in background
        if response.success:
            background_tasks.add_task(
                log_recommendation_metrics,
                response.request_id,
                response.pipeline_metrics,
                len(response.recommendations)
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Enhanced recommendation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "recommendation_failed",
                "message": "Failed to generate enhanced recommendations. Please try again.",
                "fallback_suggestion": "Try the basic recommendations endpoint: /api/v1/recommendations/basic"
            }
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
    background_tasks: BackgroundTasks,
    mode: str = "enhanced"
):
    """
    Create gift recommendations (default endpoint)
    
    Parameters:
    - mode: "enhanced" (default) for full MCP pipeline, "basic" for AI-only
    """
    if mode == "basic":
        basic_response = await create_basic_recommendations(request, background_tasks)
        # Convert to enhanced format for consistency
        return EnhancedRecommendationResponse(
            request_id=basic_response.request_id,
            recommendations=basic_response.recommendations,
            search_results=[],
            pipeline_metrics={
                "ai_generation_time": basic_response.total_processing_time,
                "search_execution_time": 0.0,
                "scraping_execution_time": 0.0,
                "integration_time": 0.0,
                "total_time": basic_response.total_processing_time,
                "search_results_count": 0,
                "product_details_count": 0,
                "cache_simulation": True
            },
            total_processing_time=basic_response.total_processing_time,
            created_at=basic_response.created_at,
            success=basic_response.success,
            mcp_enabled=False,
            simulation_mode=True,
            error_message=basic_response.error_message
        )
    else:
        return await create_enhanced_recommendations(request, background_tasks)


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


async def log_recommendation_metrics(request_id: str, metrics, recommendation_count: int):
    """Background task to log recommendation metrics"""
    logger.info(f"Recommendation metrics for {request_id}:")
    logger.info(f"  - Total time: {metrics.total_time:.2f}s")
    logger.info(f"  - AI generation: {metrics.ai_generation_time:.2f}s")
    logger.info(f"  - Search: {metrics.search_execution_time:.2f}s")
    logger.info(f"  - Scraping: {metrics.scraping_execution_time:.2f}s")
    logger.info(f"  - Integration: {metrics.integration_time:.2f}s")
    logger.info(f"  - Recommendations: {recommendation_count}")
    logger.info(f"  - Search results: {metrics.search_results_count}")
    logger.info(f"  - Enhanced products: {metrics.product_details_count}")


async def log_basic_metrics(request_id: str, processing_time: float, recommendation_count: int):
    """Background task to log basic recommendation metrics"""
    logger.info(f"Basic recommendation metrics for {request_id}:")
    logger.info(f"  - Total time: {processing_time:.2f}s")
    logger.info(f"  - Recommendations: {recommendation_count}")


# Note: Exception handlers should be added to the main app, not router