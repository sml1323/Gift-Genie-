"""
Gift Genie - Enhanced Naver Shopping Recommendation Engine
Integrated with intelligent query refinement and 5-iteration retry mechanism
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from models.request.recommendation import GiftRequest
from models.response.recommendation import EnhancedRecommendationResponse, GiftRecommendation
from services.ai.naver_recommendation_engine import NaverGiftRecommendationEngine
from services.ai.intelligent_query_refinement import IntelligentQueryRefinementEngine

logger = logging.getLogger(__name__)


@dataclass
class EnhancedRecommendationMetrics:
    """향상된 추천 시스템 메트릭"""
    ai_generation_time: float
    query_refinement_time: float
    naver_search_time: float
    total_processing_time: float
    refinement_attempts: int
    final_products_found: int
    success_rate: float
    query_strategies_used: List[str]


class EnhancedNaverRecommendationEngine:
    """5회 재시도 메커니즘을 가진 향상된 네이버 쇼핑 추천 엔진"""
    
    def __init__(self, openai_api_key: str, naver_client_id: str, naver_client_secret: str):
        # 기존 네이버 엔진 초기화
        self.naver_engine = NaverGiftRecommendationEngine(
            openai_api_key=openai_api_key,
            naver_client_id=naver_client_id,
            naver_client_secret=naver_client_secret
        )
        
        # 지능형 쿼리 개선 엔진 초기화
        self.query_refiner = IntelligentQueryRefinementEngine(
            openai_api_key=openai_api_key,
            enable_firecrawl=False  # 현재는 규칙 기반 시장 조사 사용
        )
    
    async def generate_recommendations_with_retry(
        self, 
        request: GiftRequest
    ) -> EnhancedRecommendationResponse:
        """5회 재시도 메커니즘을 사용한 향상된 추천 생성"""
        
        start_time = time.time()
        request_id = f"enhanced_{int(start_time)}"
        
        logger.info(f"🔄 Starting enhanced recommendation with retry mechanism")
        logger.info(f"  → Request ID: {request_id}")
        logger.info(f"  → Recipient: {request.recipient_age}yo {request.recipient_gender}")
        logger.info(f"  → Budget: ${request.budget_min}-${request.budget_max}")
        logger.info(f"  → Interests: {request.interests}")
        
        try:
            # 1단계: 기본 AI 추천 생성
            ai_start_time = time.time()
            ai_response = await self.naver_engine.ai_engine.generate_recommendations(request)
            ai_time = time.time() - ai_start_time
            
            if not ai_response.success or not ai_response.recommendations:
                logger.error("❌ AI recommendation generation failed")
                return self._create_error_response(request_id, "AI recommendation failed", start_time)
            
            logger.info(f"✅ AI generated {len(ai_response.recommendations)} recommendations in {ai_time:.2f}s")
            
            # 2단계: AI 추천에서 검색 키워드 추출
            original_keywords = self._extract_keywords_from_ai_recommendations(ai_response.recommendations)
            logger.info(f"🔍 Extracted keywords: {original_keywords}")
            
            # 3단계: 지능형 쿼리 개선을 통한 상품 검색
            refinement_start_time = time.time()
            
            # 선물 컨텍스트 준비
            gift_context = {
                'recipient_age': request.recipient_age,
                'recipient_gender': request.recipient_gender,
                'interests': request.interests,
                'occasion': request.occasion,
                'budget_min': request.budget_min,
                'budget_max': request.budget_max,
                'relationship': request.relationship
            }
            
            # 예산을 KRW로 변환 (간단한 변환)
            budget_max_krw = int(request.budget_max * 1300)  # USD to KRW
            
            # 네이버 쇼핑 검색 함수 정의
            async def search_function(keywords: List[str], budget_krw: int) -> List[Any]:
                return await self.naver_engine.naver_client.search_products_multi_sort(
                    keywords=keywords,
                    budget_max_krw=budget_krw,
                    display=20
                )
            
            # 지능형 재시도 메커니즘 실행
            final_products, refinement_session = await self.query_refiner.refine_search_with_retries(
                original_keywords=original_keywords,
                gift_context=gift_context,
                search_function=search_function,
                budget_max_krw=budget_max_krw
            )
            
            refinement_time = time.time() - refinement_start_time
            
            # 4단계: AI 추천과 네이버 상품 매칭
            integration_start_time = time.time()
            
            if final_products:
                # 상품이 발견된 경우 AI 추천과 통합
                enhanced_recommendations = await self._integrate_ai_and_naver_results(
                    ai_recommendations=ai_response.recommendations,
                    naver_products=final_products,
                    request=request
                )
                integration_time = time.time() - integration_start_time
                
                # 성공 응답 생성
                total_time = time.time() - start_time
                
                metrics = EnhancedRecommendationMetrics(
                    ai_generation_time=ai_time,
                    query_refinement_time=refinement_time,
                    naver_search_time=sum(a.processing_time for a in refinement_session.attempts),
                    total_processing_time=total_time,
                    refinement_attempts=len(refinement_session.attempts),
                    final_products_found=len(final_products),
                    success_rate=1.0 if refinement_session.final_success else 0.8,
                    query_strategies_used=[a.refinement_strategy for a in refinement_session.attempts]
                )
                
                logger.info(f"🎯 Enhanced recommendation completed successfully")
                logger.info(f"  → Total time: {total_time:.2f}s")
                logger.info(f"  → Refinement attempts: {metrics.refinement_attempts}")
                logger.info(f"  → Final products: {metrics.final_products_found}")
                logger.info(f"  → Success rate: {metrics.success_rate:.2%}")
                
                return EnhancedRecommendationResponse(
                    request_id=request_id,
                    recommendations=enhanced_recommendations,
                    ai_processing_time=ai_time,
                    naver_processing_time=refinement_time,
                    integration_time=integration_time,
                    total_processing_time=total_time,
                    naver_results_count=len(final_products),
                    created_at=datetime.fromtimestamp(start_time).isoformat(),
                    success=True,
                    enhancement_metrics=asdict(metrics),
                    refinement_session=asdict(refinement_session)
                )
            else:
                # 상품을 찾지 못한 경우 AI 추천만 반환
                integration_time = time.time() - integration_start_time
                total_time = time.time() - start_time
                
                logger.warning(f"⚠️ No products found after {len(refinement_session.attempts)} attempts")
                logger.info(f"  → Falling back to AI-only recommendations")
                
                metrics = EnhancedRecommendationMetrics(
                    ai_generation_time=ai_time,
                    query_refinement_time=refinement_time,
                    naver_search_time=sum(a.processing_time for a in refinement_session.attempts),
                    total_processing_time=total_time,
                    refinement_attempts=len(refinement_session.attempts),
                    final_products_found=0,
                    success_rate=0.5,  # 부분 성공
                    query_strategies_used=[a.refinement_strategy for a in refinement_session.attempts]
                )\n                \n                return EnhancedRecommendationResponse(\n                    request_id=request_id,\n                    recommendations=ai_response.recommendations,\n                    ai_processing_time=ai_time,\n                    naver_processing_time=refinement_time,\n                    integration_time=integration_time,\n                    total_processing_time=total_time,\n                    naver_results_count=0,\n                    created_at=datetime.fromtimestamp(start_time).isoformat(),\n                    success=True,  # AI 추천은 성공\n                    enhancement_metrics=asdict(metrics),\n                    refinement_session=asdict(refinement_session),\n                    fallback_mode=True\n                )\n                \n        except Exception as e:\n            logger.error(f\"❌ Enhanced recommendation failed: {str(e)}\")\n            return self._create_error_response(request_id, str(e), start_time)\n    \n    def _extract_keywords_from_ai_recommendations(\n        self, \n        recommendations: List[GiftRecommendation]\n    ) -> List[str]:\n        \"\"\"AI 추천에서 검색 키워드 추출\"\"\"\n        \n        keywords = []\n        \n        for rec in recommendations:\n            # 제목에서 핵심 키워드 추출\n            title_words = rec.title.split()\n            for word in title_words:\n                # 불용어 제거 및 의미있는 단어만 선택\n                if len(word) >= 2 and word not in ['세트', '용품', '제품', '상품', '아이템']:\n                    keywords.append(word)\n            \n            # 카테고리도 키워드로 추가\n            if rec.category and rec.category not in keywords:\n                keywords.append(rec.category)\n        \n        # 중복 제거 및 최대 5개 키워드 선택\n        unique_keywords = list(dict.fromkeys(keywords))  # 순서 보존하며 중복 제거\n        return unique_keywords[:5]\n    \n    async def _integrate_ai_and_naver_results(\n        self,\n        ai_recommendations: List[GiftRecommendation],\n        naver_products: List[Any],\n        request: GiftRequest\n    ) -> List[GiftRecommendation]:\n        \"\"\"AI 추천과 네이버 상품 결과 통합\"\"\"\n        \n        logger.info(f\"🔗 Integrating {len(ai_recommendations)} AI recs with {len(naver_products)} Naver products\")\n        \n        integrated_recommendations = []\n        \n        # AI 추천을 네이버 상품과 매칭\n        for i, ai_rec in enumerate(ai_recommendations):\n            if i < len(naver_products):\n                # 네이버 상품 정보로 AI 추천 강화\n                naver_product = naver_products[i]\n                \n                enhanced_rec = GiftRecommendation(\n                    title=naver_product.title if naver_product.title else ai_rec.title,\n                    description=ai_rec.description,  # AI 설명 유지\n                    category=ai_rec.category,\n                    estimated_price=naver_product.lprice // 1300 if naver_product.lprice else ai_rec.estimated_price,  # KRW to USD\n                    currency=\"USD\",\n                    price_display=f\"${naver_product.lprice // 1300}\" if naver_product.lprice else ai_rec.price_display,\n                    reasoning=ai_rec.reasoning,  # AI 추론 유지\n                    purchase_link=naver_product.link if naver_product.link else None,\n                    image_url=naver_product.image if naver_product.image else None,\n                    confidence_score=min(ai_rec.confidence_score + 0.1, 1.0),  # 실제 상품 매칭으로 신뢰도 증가\n                    naver_product_info={\n                        \"product_id\": naver_product.productId,\n                        \"mall_name\": naver_product.mallName,\n                        \"brand\": naver_product.brand,\n                        \"maker\": naver_product.maker,\n                        \"quality_score\": getattr(naver_product, 'quality_score', 0.8)\n                    }\n                )\n                \n                integrated_recommendations.append(enhanced_rec)\n            else:\n                # 네이버 상품이 부족한 경우 AI 추천 그대로 사용\n                integrated_recommendations.append(ai_rec)\n        \n        # 추가 네이버 상품이 있는 경우 추가 추천으로 포함\n        if len(naver_products) > len(ai_recommendations):\n            for i in range(len(ai_recommendations), min(len(naver_products), 5)):\n                naver_product = naver_products[i]\n                \n                additional_rec = GiftRecommendation(\n                    title=naver_product.title,\n                    description=f\"네이버 쇼핑에서 발견한 인기 상품입니다. {request.relationship}에게 드리기 좋은 실용적인 선물입니다.\",\n                    category=naver_product.category1 or \"일반상품\",\n                    estimated_price=naver_product.lprice // 1300 if naver_product.lprice else 50,\n                    currency=\"USD\",\n                    price_display=f\"${naver_product.lprice // 1300}\" if naver_product.lprice else \"$50\",\n                    reasoning=f\"시장에서 검증된 인기 상품으로 {request.occasion}에 적합한 선물입니다.\",\n                    purchase_link=naver_product.link,\n                    image_url=naver_product.image,\n                    confidence_score=0.75,\n                    naver_product_info={\n                        \"product_id\": naver_product.productId,\n                        \"mall_name\": naver_product.mallName,\n                        \"brand\": naver_product.brand,\n                        \"maker\": naver_product.maker,\n                        \"quality_score\": getattr(naver_product, 'quality_score', 0.8)\n                    }\n                )\n                \n                integrated_recommendations.append(additional_rec)\n        \n        logger.info(f\"✅ Integration complete: {len(integrated_recommendations)} enhanced recommendations\")\n        return integrated_recommendations\n    \n    def _create_error_response(\n        self, \n        request_id: str, \n        error_message: str, \n        start_time: float\n    ) -> EnhancedRecommendationResponse:\n        \"\"\"오류 응답 생성\"\"\"\n        \n        total_time = time.time() - start_time\n        \n        return EnhancedRecommendationResponse(\n            request_id=request_id,\n            recommendations=[],\n            ai_processing_time=0.0,\n            naver_processing_time=0.0,\n            integration_time=0.0,\n            total_processing_time=total_time,\n            naver_results_count=0,\n            created_at=datetime.fromtimestamp(start_time).isoformat(),\n            success=False,\n            error_message=error_message\n        )