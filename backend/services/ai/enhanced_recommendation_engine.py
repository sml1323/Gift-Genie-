"""
Gift Genie - Enhanced Recommendation Engine
MCP 파이프라인 통합 추천 엔진
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import List

from models.request.recommendation import GiftRequest
from models.response.recommendation import (
    GiftRecommendation, ProductSearchResult, MCPPipelineMetrics, 
    EnhancedRecommendationResponse
)
from services.ai.recommendation_engine import GiftRecommendationEngine
from services.search.brave_search import BraveSearchClient
from services.scraping.apify_service import ApifyScrapingClient

logger = logging.getLogger(__name__)


class EnhancedGiftRecommendationEngine:
    """MCP 파이프라인 통합 추천 엔진"""
    
    def __init__(self, openai_api_key: str, brave_api_key: str = "", apify_api_key: str = ""):
        self.ai_engine = GiftRecommendationEngine(openai_api_key)
        self.search_client = BraveSearchClient(brave_api_key)
        self.scraping_client = ApifyScrapingClient(apify_api_key)
        self.mcp_enabled = True  # MCP 파이프라인 항상 활성화
        
        # Check if in simulation mode
        self.simulation_mode = (
            openai_api_key == "your-openai-api-key-here" or
            not openai_api_key or 
            not brave_api_key or 
            not apify_api_key
        )
    
    async def generate_enhanced_recommendations(self, request: GiftRequest) -> EnhancedRecommendationResponse:
        """강화된 MCP 파이프라인 추천 생성"""
        start_time = datetime.now()
        request_id = f"enhanced_req_{int(start_time.timestamp())}"
        
        try:
            logger.info(f"Starting enhanced MCP pipeline for request {request_id}")
            
            # Stage 1: AI 기본 추천 생성
            ai_start = time.time()
            ai_response = await self.ai_engine.generate_recommendations(request)
            ai_time = time.time() - ai_start
            
            if not ai_response.success:
                raise Exception(f"AI generation failed: {ai_response.error_message}")
            
            # Stage 2: 상품 검색 (MCP 활성 시)
            search_results = []
            search_time = 0
            
            if self.mcp_enabled and ai_response.recommendations:
                search_start = time.time()
                
                # 검색 키워드 추출
                keywords = self._extract_search_keywords(ai_response.recommendations[0], request)
                search_results = await self.search_client.search_products(keywords, request.budget_max)
                
                search_time = time.time() - search_start
                logger.info(f"Found {len(search_results)} products in {search_time:.2f}s")
            
            # Stage 3: 상품 상세정보 스크래핑
            scraping_time = 0
            if search_results:
                scraping_start = time.time()
                search_results = await self.scraping_client.scrape_product_details(search_results)
                scraping_time = time.time() - scraping_start
                logger.info(f"Enhanced {len(search_results)} products with detailed info in {scraping_time:.2f}s")
            
            # Stage 4: AI 추천과 실제 상품 통합
            integration_start = time.time()
            enhanced_recommendations = await self._integrate_recommendations(
                ai_response.recommendations, search_results, request
            )
            integration_time = time.time() - integration_start
            
            # 메트릭 수집
            total_time = (datetime.now() - start_time).total_seconds()
            
            pipeline_metrics = MCPPipelineMetrics(
                ai_generation_time=ai_time,
                search_execution_time=search_time,
                scraping_execution_time=scraping_time,
                integration_time=integration_time,
                total_time=total_time,
                search_results_count=len(search_results),
                product_details_count=len([r for r in search_results if r.image_url]),
                cache_simulation=self.simulation_mode
            )
            
            logger.info(f"Enhanced pipeline completed in {total_time:.2f}s")
            
            return EnhancedRecommendationResponse(
                request_id=request_id,
                recommendations=enhanced_recommendations,
                search_results=search_results,
                pipeline_metrics=pipeline_metrics,
                total_processing_time=total_time,
                created_at=start_time.isoformat(),
                success=True,
                mcp_enabled=self.mcp_enabled,
                simulation_mode=self.simulation_mode
            )
            
        except Exception as e:
            logger.error(f"Enhanced pipeline failed: {str(e)}")
            total_time = (datetime.now() - start_time).total_seconds()
            
            return EnhancedRecommendationResponse(
                request_id=request_id,
                recommendations=[],
                search_results=[],
                pipeline_metrics=MCPPipelineMetrics(
                    ai_generation_time=0, search_execution_time=0,
                    scraping_execution_time=0, integration_time=0,
                    total_time=total_time, search_results_count=0,
                    product_details_count=0
                ),
                total_processing_time=total_time,
                created_at=start_time.isoformat(),
                success=False,
                mcp_enabled=self.mcp_enabled,
                simulation_mode=self.simulation_mode,
                error_message=str(e)
            )
    
    def _extract_search_keywords(self, recommendation: GiftRecommendation, request: GiftRequest) -> List[str]:
        """검색 키워드 추출"""
        keywords = []
        
        # 추천 제목에서 키워드 추출
        title_words = recommendation.title.split()
        keywords.extend(title_words[:2])  # 첫 2개 단어
        
        # 카테고리 추가
        keywords.append(recommendation.category)
        
        # 사용자 관심사 추가
        if request.interests:
            keywords.extend(request.interests[:2])
        
        return keywords[:5]  # 최대 5개
    
    async def _integrate_recommendations(self, 
                                       ai_recommendations: List[GiftRecommendation], 
                                       search_results: List[ProductSearchResult],
                                       request: GiftRequest) -> List[GiftRecommendation]:
        """추천과 실제 상품 통합"""
        if not search_results:
            return ai_recommendations
        
        # AI 추천과 실제 상품을 매칭
        enhanced_recommendations = []
        
        for i, ai_rec in enumerate(ai_recommendations[:3]):  # 상위 3개만
            if i < len(search_results):
                product = search_results[i]
                
                # AI 추천에 실제 상품 정보 통합
                enhanced_rec = GiftRecommendation(
                    title=f"{ai_rec.title} ({product.domain})",
                    description=f"{ai_rec.description}\n\n품명: {product.title}\n평점: {product.rating or 'N/A'}⭐ (리뷰 {product.review_count or 0}개)",
                    category=ai_rec.category,
                    estimated_price=product.price or ai_rec.estimated_price,
                    reasoning=f"{ai_rec.reasoning}\n\n이 제품은 실제 구매 가능한 상품으로, {product.domain}에서 판매 중입니다.",
                    purchase_link=product.url,
                    image_url=product.image_url,
                    confidence_score=min(ai_rec.confidence_score + 0.1, 1.0)  # MCP 데이터로 신뢰도 상승
                )
                enhanced_recommendations.append(enhanced_rec)
            else:
                enhanced_recommendations.append(ai_rec)
        
        return enhanced_recommendations