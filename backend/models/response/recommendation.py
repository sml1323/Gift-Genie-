"""
Gift Genie - Response Models
Pydantic models for API responses
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class GiftRecommendation(BaseModel):
    """Individual gift recommendation"""
    title: str = Field(..., description="Gift title/name")
    description: str = Field(..., description="Detailed description of the gift")
    category: str = Field(..., description="Gift category")
    estimated_price: int = Field(..., ge=0, description="Estimated price amount")
    currency: Literal["USD", "KRW"] = Field(default="KRW", description="Price currency")
    price_display: str = Field(..., description="Formatted price for display (e.g., '₩65,000' or '$50')")
    reasoning: str = Field(..., description="AI reasoning for this recommendation")
    purchase_link: Optional[str] = Field(None, description="Direct purchase link")
    image_url: Optional[str] = Field(None, description="Product image URL")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "독서 애호가를 위한 프리미엄 선물",
                "description": "28세 여성에게 완벽한 생일 선물입니다. 고품질 소재와 세련된 디자인으로 특별함을 선사합니다.",
                "category": "프리미엄 선물",
                "estimated_price": 182000,
                "currency": "KRW",
                "price_display": "₩182,000",
                "reasoning": "받는 분의 관심사(독서, 커피)를 고려하여 선별한 고품질 제품입니다.",
                "purchase_link": "https://amazon.com/dp/example1",
                "image_url": "https://source.unsplash.com/400x400/?reading,product",
                "confidence_score": 0.85
            }
        }


class ProductSearchResult(BaseModel):
    """검색된 상품 정보"""
    title: str = Field(..., description="Product title")
    url: str = Field(..., description="Product URL")
    description: str = Field(..., description="Product description")
    domain: str = Field(..., description="E-commerce domain")
    price: Optional[int] = Field(None, ge=0, description="Product price amount")
    currency: Optional[Literal["USD", "KRW"]] = Field(default="KRW", description="Price currency")
    price_display: Optional[str] = Field(None, description="Formatted price for display")
    image_url: Optional[str] = Field(None, description="Product image URL")
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Product rating (0-5)")
    review_count: Optional[int] = Field(None, ge=0, description="Number of reviews")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Coffee Gift Set - Premium Edition",
                "url": "https://amazon.com/dp/example1",
                "description": "Perfect coffee gift with premium quality and elegant design.",
                "domain": "amazon.com",
                "price": 110500,
                "currency": "KRW",
                "price_display": "₩110,500",
                "image_url": "https://source.unsplash.com/400x400/?coffee,product",
                "rating": 4.1,
                "review_count": 200
            }
        }


class MCPPipelineMetrics(BaseModel):
    """MCP 파이프라인 성능 메트릭"""
    ai_generation_time: float = Field(..., description="AI generation time in seconds")
    search_execution_time: float = Field(..., description="Search execution time in seconds")
    scraping_execution_time: float = Field(..., description="Scraping execution time in seconds")
    integration_time: float = Field(..., description="Integration time in seconds")
    total_time: float = Field(..., description="Total pipeline time in seconds")
    search_results_count: int = Field(..., ge=0, description="Number of search results found")
    product_details_count: int = Field(..., ge=0, description="Number of products with detailed info")
    cache_simulation: bool = Field(True, description="Whether cache simulation was used")

    class Config:
        json_schema_extra = {
            "example": {
                "ai_generation_time": 1.5,
                "search_execution_time": 0.8,
                "scraping_execution_time": 1.2,
                "integration_time": 0.3,
                "total_time": 3.8,
                "search_results_count": 5,
                "product_details_count": 5,
                "cache_simulation": True
            }
        }


class EnhancedRecommendationResponse(BaseModel):
    """Enhanced recommendation response with MCP data"""
    request_id: str = Field(..., description="Unique request identifier")
    recommendations: List[GiftRecommendation] = Field(..., description="List of gift recommendations")
    search_results: List[ProductSearchResult] = Field(..., description="Search results from MCP pipeline")
    pipeline_metrics: MCPPipelineMetrics = Field(..., description="Performance metrics")
    total_processing_time: float = Field(..., description="Total processing time in seconds")
    created_at: str = Field(..., description="Response creation timestamp")
    success: bool = Field(..., description="Whether the request was successful")
    mcp_enabled: bool = Field(..., description="Whether MCP pipeline was enabled")
    simulation_mode: bool = Field(..., description="Whether simulation mode was used")
    error_message: Optional[str] = Field(None, description="Error message if request failed")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "enhanced_req_1732537200",
                "recommendations": [],
                "search_results": [],
                "pipeline_metrics": {
                    "ai_generation_time": 1.5,
                    "search_execution_time": 0.8,
                    "scraping_execution_time": 1.2,
                    "integration_time": 0.3,
                    "total_time": 3.8,
                    "search_results_count": 5,
                    "product_details_count": 5,
                    "cache_simulation": True
                },
                "total_processing_time": 3.8,
                "created_at": "2025-07-26T10:00:00Z",
                "success": True,
                "mcp_enabled": True,
                "simulation_mode": False,
                "error_message": None
            }
        }


class RecommendationResponse(BaseModel):
    """Basic recommendation response (Legacy)"""
    request_id: str = Field(..., description="Unique request identifier")
    recommendations: List[GiftRecommendation] = Field(..., description="List of gift recommendations")
    total_processing_time: float = Field(..., description="Total processing time in seconds")
    created_at: str = Field(..., description="Response creation timestamp")
    success: bool = Field(..., description="Whether the request was successful")
    error_message: Optional[str] = Field(None, description="Error message if request failed")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_1732537200",
                "recommendations": [],
                "total_processing_time": 2.5,
                "created_at": "2025-07-26T10:00:00Z",
                "success": True,
                "error_message": None
            }
        }