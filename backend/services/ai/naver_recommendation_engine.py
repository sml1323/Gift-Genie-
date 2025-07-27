"""
Gift Genie - Naver Shopping API Recommendation Engine
Integrated version for FastAPI backend with KRW/USD conversion support
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)

# Constants
MAX_RECOMMENDATIONS = 5
API_TIMEOUT = 30
USD_TO_KRW_RATE = 1300  # Approximate conversion rate


@dataclass
class NaverProductResult:
    """네이버쇼핑 상품 검색 결과"""
    title: str
    link: str
    image: str
    lprice: int  # 최저가 (KRW)
    hprice: int  # 최고가 (KRW)
    mallName: str
    productId: str
    productType: int
    brand: str
    maker: str
    category1: str
    category2: str
    category3: str
    category4: str


@dataclass
class NaverShoppingMetrics:
    """네이버쇼핑 API 성능 메트릭"""
    ai_generation_time: float
    naver_search_time: float
    integration_time: float
    total_time: float
    search_results_count: int
    api_calls_count: int
    simulation_mode: bool = False


class NaverShoppingClient:
    """네이버쇼핑 API 클라이언트"""
    
    def __init__(self, client_id: str = "", client_secret: str = ""):
        self.client_id = client_id
        self.client_secret = client_secret
        self.enabled = bool(client_id and client_secret)
        self.base_url = "https://openapi.naver.com/v1/search/shop.json"
        self.api_calls_count = 0
    
    async def search_products(self, keywords: List[str], budget_max_usd: int, 
                            display: int = 10, sort: str = "asc") -> List[NaverProductResult]:
        """상품 검색 (USD 예산을 KRW로 변환)"""
        budget_max_krw = budget_max_usd * USD_TO_KRW_RATE
        
        if not self.enabled:
            return await self._simulate_search(keywords, budget_max_krw, display)
        
        try:
            # Build search query
            query = " ".join(keywords[:3])  # 최대 3개 키워드 조합
            logger.info(f"Searching Naver Shopping: '{query}', budget_max: ${budget_max_usd} ({budget_max_krw:,}원)")
            
            headers = {
                "X-Naver-Client-Id": self.client_id,
                "X-Naver-Client-Secret": self.client_secret
            }
            
            params = {
                "query": query,
                "display": display,
                "start": 1,
                "sort": sort  # asc: 가격 오름차순, dsc: 가격 내림차순
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    self.api_calls_count += 1
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Naver API returned {len(data.get('items', []))} raw products")
                        results = self._process_search_results(data, budget_max_krw)
                        logger.info(f"After filtering: {len(results)} products within budget")
                        return results
                    else:
                        logger.warning(f"Naver Shopping API error: {response.status}")
                        return await self._simulate_search(keywords, budget_max_krw, display)
                        
        except Exception as e:
            logger.error(f"Naver Shopping API failed: {e}")
            return await self._simulate_search(keywords, budget_max_krw, display)
    
    def _process_search_results(self, data: Dict[str, Any], budget_max_krw: int) -> List[NaverProductResult]:
        """네이버쇼핑 검색 결과 처리"""
        results = []
        items = data.get("items", [])
        
        logger.info(f"Budget filter: max {budget_max_krw:,}원")
        
        if items:
            logger.info(f"Sample API response item: {items[0]}")
        
        filtered_count = 0
        for item in items:
            try:
                # 가격 필터링 (예산 내 상품만)
                lprice_str = item.get("lprice", "0")
                if not lprice_str or lprice_str == "":
                    logger.warning(f"Product '{item.get('title', 'Unknown')}' has no price, skipping")
                    continue
                
                try:
                    lprice = int(lprice_str)
                except ValueError:
                    logger.warning(f"Invalid price format '{lprice_str}' for product '{item.get('title', 'Unknown')}'")
                    continue
                
                if lprice > budget_max_krw:
                    filtered_count += 1
                    continue
                
                # 제목에서 HTML 태그 제거
                title = self._clean_html_tags(item.get("title", ""))
                
                # hprice 처리 (빈 문자열인 경우 lprice 사용)
                hprice_str = item.get("hprice", "")
                if hprice_str and hprice_str != "":
                    try:
                        hprice = int(hprice_str)
                    except ValueError:
                        hprice = lprice
                else:
                    hprice = lprice
                
                # productType 처리
                try:
                    product_type = int(item.get("productType", 1))
                except ValueError:
                    product_type = 1
                
                result = NaverProductResult(
                    title=title,
                    link=item.get("link", ""),
                    image=item.get("image", ""),
                    lprice=lprice,
                    hprice=hprice,
                    mallName=item.get("mallName", ""),
                    productId=item.get("productId", ""),
                    productType=product_type,
                    brand=item.get("brand", ""),
                    maker=item.get("maker", ""),
                    category1=item.get("category1", ""),
                    category2=item.get("category2", ""),
                    category3=item.get("category3", ""),
                    category4=item.get("category4", "")
                )
                results.append(result)
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid product: {e}")
                continue
        
        logger.info(f"Filtering results: {filtered_count} products over budget, {len(results)} products within budget")
        return results
    
    def _clean_html_tags(self, text: str) -> str:
        """HTML 태그 제거"""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    async def _simulate_search(self, keywords: List[str], budget_max_krw: int, display: int) -> List[NaverProductResult]:
        """시뮬레이션 모드"""
        await asyncio.sleep(0.8)
        
        # 키워드 기반 가상 상품 생성
        keyword = keywords[0] if keywords else "선물"
        
        sample_products = []
        for i in range(min(display, 5)):
            price = min(budget_max_krw - (i * 10000), budget_max_krw - 5000)
            
            sample_products.append(NaverProductResult(
                title=f"{keyword} 추천 상품 #{i+1}",
                link=f"https://shopping.naver.com/product/{1000+i}",
                image=f"https://source.unsplash.com/400x400/?{keyword},product",
                lprice=price,
                hprice=price + 10000,
                mallName=f"쇼핑몰{i+1}",
                productId=f"prod_{1000+i}",
                productType=1,
                brand=f"브랜드{i+1}",
                maker=f"제조사{i+1}",
                category1="생활/건강",
                category2="생활용품",
                category3=keyword,
                category4=""
            ))
        
        return sample_products


class NaverGiftRecommendationEngine:
    """네이버쇼핑 API 기반 통합 추천 엔진 - FastAPI 백엔드용"""
    
    def __init__(self, openai_api_key: str, naver_client_id: str = "", naver_client_secret: str = ""):
        from services.ai.recommendation_engine import GiftRecommendationEngine
        
        self.ai_engine = GiftRecommendationEngine(openai_api_key)
        self.naver_client = NaverShoppingClient(naver_client_id, naver_client_secret)
        self.naver_enabled = self.naver_client.enabled
    
    async def generate_naver_recommendations(self, request):
        """
        네이버쇼핑 API 기반 추천 생성 (FastAPI 백엔드용)
        
        Args:
            request: GiftRequest 모델 인스턴스
            
        Returns:
            EnhancedRecommendationResponse와 호환되는 구조
        """
        start_time = datetime.now()
        request_id = f"naver_req_{int(start_time.timestamp())}"
        
        try:
            logger.info(f"Starting Naver Shopping recommendation for {request_id}")
            
            # Stage 1: AI 기본 추천 생성
            ai_start = time.time()
            ai_response = await self.ai_engine.generate_recommendations(request)
            ai_time = time.time() - ai_start
            
            if not ai_response.success:
                raise Exception(f"AI generation failed: {ai_response.error_message}")
            
            # Stage 2: 네이버쇼핑 검색
            naver_products = []
            naver_time = 0
            naver_start = time.time()
            
            # Extract keywords from user interests and occasion
            search_keywords = request.interests[:2] if request.interests else ["선물"]
            if request.occasion and request.occasion not in search_keywords:
                search_keywords.append(request.occasion)
            
            logger.info(f"Searching with keywords: {search_keywords}, budget_max: {request.budget_max}")
            
            # Convert KRW budget to USD for naver client (which expects USD)
            from utils.currency import convert_currency
            budget_max_usd = convert_currency(request.budget_max, request.currency, "USD") if request.currency == "KRW" else request.budget_max
            
            # Always search for products (regardless of AI recommendations)
            naver_products = await self.naver_client.search_products(
                search_keywords, budget_max_usd, display=10, sort="asc"
            )
            
            naver_time = time.time() - naver_start
            logger.info(f"Found {len(naver_products)} products in {naver_time:.2f}s")
            
            # Stage 3: AI 추천과 네이버쇼핑 상품 통합
            integration_start = time.time()
            enhanced_recommendations = await self._integrate_recommendations(
                ai_response.recommendations, naver_products, request
            )
            integration_time = time.time() - integration_start
            
            # 네이버 상품을 ProductSearchResult로 변환
            search_results = self._convert_naver_to_search_results(naver_products)
            
            # 메트릭 수집
            total_time = (datetime.now() - start_time).total_seconds()
            
            # EnhancedRecommendationResponse 구조로 반환
            from models.response.recommendation import (
                EnhancedRecommendationResponse, 
                MCPPipelineMetrics
            )
            
            metrics = MCPPipelineMetrics(
                ai_generation_time=ai_time,
                search_execution_time=naver_time,
                scraping_execution_time=0.0,  # 네이버 API는 스크래핑 불필요
                integration_time=integration_time,
                total_time=total_time,
                search_results_count=len(naver_products),
                product_details_count=len(naver_products),
                cache_simulation=not self.naver_enabled
            )
            
            logger.info(f"Naver Shopping pipeline completed in {total_time:.2f}s")
            
            return EnhancedRecommendationResponse(
                request_id=request_id,
                recommendations=enhanced_recommendations,
                search_results=search_results,
                pipeline_metrics=metrics,
                total_processing_time=total_time,
                created_at=start_time.isoformat(),
                success=True,
                mcp_enabled=False,  # MCP 사용 안함
                simulation_mode=not self.naver_enabled,
                error_message=None
            )
            
        except Exception as e:
            logger.error(f"Naver Shopping pipeline failed: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            total_time = (datetime.now() - start_time).total_seconds()
            
            from models.response.recommendation import (
                EnhancedRecommendationResponse, 
                MCPPipelineMetrics
            )
            
            return EnhancedRecommendationResponse(
                request_id=request_id,
                recommendations=[],
                search_results=[],
                pipeline_metrics=MCPPipelineMetrics(
                    ai_generation_time=0, search_execution_time=0,
                    scraping_execution_time=0, integration_time=0, 
                    total_time=total_time, search_results_count=0, 
                    product_details_count=0, cache_simulation=True
                ),
                total_processing_time=total_time,
                created_at=start_time.isoformat(),
                success=False,
                mcp_enabled=False,
                simulation_mode=True,
                error_message=str(e)
            )
    
    def _extract_search_keywords(self, recommendation, request) -> List[str]:
        """AI 추천에서 네이버쇼핑 검색 키워드 추출 (한국어 최적화)"""
        keywords = []
        
        # 추천 제목에서 키워드 추출
        title_words = recommendation.title.split()
        for word in title_words[:3]:
            if len(word) >= 2:  # 2글자 이상 키워드만
                keywords.append(word)
        
        # 카테고리 추가
        if recommendation.category:
            # 카테고리 매핑
            category_mapping = {
                "전자제품": "전자기기",
                "홈&리빙": "생활용품", 
                "도서": "책",
                "식음료": "식품",
                "프리미엄 선물": "선물세트"
            }
            mapped_category = category_mapping.get(recommendation.category, recommendation.category)
            keywords.append(mapped_category)
        
        # 사용자 관심사 추가
        if request.interests:
            interest_mapping = {
                "독서": "책",
                "커피": "원두",
                "여행": "여행용품",
                "사진": "카메라",
                "운동": "스포츠용품",
                "요리": "주방용품",
                "음악": "오디오"
            }
            for interest in request.interests[:2]:
                mapped_interest = interest_mapping.get(interest, interest)
                keywords.append(mapped_interest)
        
        # 중복 제거
        unique_keywords = []
        for keyword in keywords:
            if keyword not in unique_keywords:
                unique_keywords.append(keyword)
        
        logger.info(f"Generated search keywords: {unique_keywords[:4]}")
        return unique_keywords[:4]
    
    async def _integrate_recommendations(self, ai_recommendations: List, naver_products: List[NaverProductResult], request) -> List:
        """AI 추천과 네이버쇼핑 상품 통합"""
        if not naver_products:
            return ai_recommendations
        
        enhanced_recommendations = []
        
        # AI 추천 각각에 대해 가장 적합한 네이버쇼핑 상품 매칭
        for i, ai_rec in enumerate(ai_recommendations[:3]):
            
            # 가격 범위에 맞는 상품 필터링 (USD로 변환하여 비교)
            budget_products = []
            for p in naver_products:
                price_usd = p.lprice // USD_TO_KRW_RATE
                # 예산 범위를 약간 넓혀서 더 많은 상품 매칭
                if (request.budget_min * 0.8) <= price_usd <= (request.budget_max * 1.2):
                    budget_products.append(p)
            
            if budget_products and i < len(budget_products):
                product = budget_products[i]
                
                # USD 가격으로 변환
                price_usd = product.lprice // USD_TO_KRW_RATE
                
                # GiftRecommendation 객체 생성 (기존 모델과 호환)
                from models.response.recommendation import GiftRecommendation
                
                enhanced_rec = GiftRecommendation(
                    title=f"{ai_rec.title}",
                    description=f"{ai_rec.description}\n\n💰 최저가: {product.lprice:,}원 (≈${price_usd}) - {product.mallName}\n🏷️ 브랜드: {product.brand or '기타'}",
                    category=ai_rec.category,
                    estimated_price=product.lprice,
                    currency="KRW",
                    price_display=f"₩{product.lprice:,}",
                    reasoning=f"{ai_rec.reasoning}\n\n✅ 네이버쇼핑에서 실제 구매 가능한 상품을 찾았습니다. 가격 비교를 통해 최저가로 추천드립니다.",
                    purchase_link=product.link,
                    image_url=product.image,
                    confidence_score=min(ai_rec.confidence_score + 0.15, 1.0)
                )
                enhanced_recommendations.append(enhanced_rec)
            else:
                # 적합한 상품이 없으면 원래 AI 추천 유지
                enhanced_recommendations.append(ai_rec)
        
        return enhanced_recommendations
    
    def _convert_naver_to_search_results(self, naver_products: List[NaverProductResult]) -> List:
        """네이버 상품을 ProductSearchResult로 변환"""
        from models.response.recommendation import ProductSearchResult
        from utils.currency import format_currency
        
        search_results = []
        for product in naver_products[:5]:
            # Keep price in KRW (no conversion needed for Korean products)
            price_krw = product.lprice
            
            search_result = ProductSearchResult(
                title=product.title,
                url=product.link,
                description=f"{product.brand} {product.category3}".strip(),
                domain="shopping.naver.com",
                price=price_krw,
                currency="KRW",
                price_display=format_currency(price_krw, "KRW"),
                image_url=product.image,
                rating=None,  # 네이버쇼핑 API에서 제공하지 않음
                review_count=None
            )
            search_results.append(search_result)
        
        return search_results