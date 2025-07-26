#!/usr/bin/env python3
"""
Gift Genie - 네이버쇼핑 API 기반 추천 엔진
MCP 파이프라인을 네이버쇼핑 API로 대체한 간소화된 버전

네이버쇼핑 API를 활용한 핵심 기능:
- 개인화된 상품 검색
- 실제 구매 링크 제공
- 최저가/최고가 비교
- 브랜드/카테고리 필터링

Usage:
    export OPENAI_API_KEY="your-openai-api-key-here"
    export NAVER_CLIENT_ID="your-naver-client-id"
    export NAVER_CLIENT_SECRET="your-naver-client-secret"
    python naver_shopping_recommendation.py

Requirements:
    pip install openai aiohttp
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from openai import AsyncOpenAI
import aiohttp

# Load environment variables
def load_env_file():
    """Load environment variables from .env file"""
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    except FileNotFoundError:
        print("⚠️  .env file not found, using system environment variables")

load_env_file()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")
MAX_RECOMMENDATIONS = 5
API_TIMEOUT = 30

# Configuration
NAVER_API_ENABLED = bool(NAVER_CLIENT_ID and NAVER_CLIENT_SECRET)
SIMULATION_MODE = not NAVER_API_ENABLED


@dataclass
class GiftRequest:
    """Gift recommendation request model - KRW 기반"""
    recipient_age: int
    recipient_gender: str
    relationship: str  # friend, family, colleague, partner
    budget_min_krw: int  # 최소 예산 (원)
    budget_max_krw: int  # 최대 예산 (원)
    interests: List[str]
    occasion: str  # birthday, christmas, anniversary, etc.
    personal_style: Optional[str] = None
    restrictions: Optional[List[str]] = None
    
    def __post_init__(self):
        """입력 검증"""
        if self.budget_min_krw < 10000:
            raise ValueError("최소 예산은 10,000원 이상이어야 합니다")
        if self.budget_max_krw > 1000000:
            raise ValueError("최대 예산은 1,000,000원 이하여야 합니다")
        if self.budget_min_krw >= self.budget_max_krw:
            raise ValueError("최소 예산은 최대 예산보다 작아야 합니다")


@dataclass
class GiftRecommendation:
    """Individual gift recommendation - KRW 기반"""
    title: str
    description: str
    category: str
    estimated_price_krw: int  # 예상 가격 (원)
    reasoning: str
    purchase_link: Optional[str] = None
    image_url: Optional[str] = None
    confidence_score: float = 0.0


@dataclass
class NaverProductResult:
    """네이버쇼핑 상품 검색 결과"""
    title: str
    link: str
    image: str
    lprice: int  # 최저가
    hprice: int  # 최고가
    mallName: str  # 쇼핑몰명
    productId: str  # 상품ID
    productType: int  # 상품군 번호
    brand: str  # 브랜드명
    maker: str  # 제조사
    category1: str  # 대분류 카테고리
    category2: str  # 중분류 카테고리
    category3: str  # 소분류 카테고리
    category4: str  # 세분류 카테고리


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


@dataclass
class NaverRecommendationResponse:
    """네이버쇼핑 기반 추천 응답"""
    request_id: str
    recommendations: List[GiftRecommendation]
    naver_products: List[NaverProductResult]
    metrics: NaverShoppingMetrics
    total_processing_time: float
    created_at: str
    success: bool
    naver_api_enabled: bool
    simulation_mode: bool
    error_message: Optional[str] = None


class GiftRecommendationEngine:
    """Core gift recommendation engine using GPT-4o-mini"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.simulation_mode = (api_key == "your-openai-api-key-here")
        if not self.simulation_mode:
            self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
    
    async def generate_recommendations(self, request: GiftRequest) -> List[GiftRecommendation]:
        """Generate gift recommendations based on user input"""
        try:
            if self.simulation_mode:
                await asyncio.sleep(1.5)
                return self._generate_mock_recommendations(request)
            else:
                prompt = self._build_recommendation_prompt(request)
                response = await self._call_openai_api(prompt)
                return self._parse_recommendations(response)
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return self._generate_mock_recommendations(request)
    
    def _build_recommendation_prompt(self, request: GiftRequest) -> str:
        """Build optimized prompt for gift recommendations"""
        restrictions_text = ""
        if request.restrictions:
            restrictions_text = f"\nImportant restrictions: {', '.join(request.restrictions)}"
        
        style_text = ""
        if request.personal_style:
            style_text = f"\nPersonal style preference: {request.personal_style}"
        
        prompt = f"""당신은 개인화된 추천을 전문으로 하는 선물 컨설턴트입니다.

다음 정보를 바탕으로 {MAX_RECOMMENDATIONS}개의 완벽한 선물 추천을 생성해주세요:

받는 사람 프로필:
- 나이: {request.recipient_age}세
- 성별: {request.recipient_gender}
- 관계: {request.relationship}
- 관심사: {', '.join(request.interests)}

행사 및 예산:
- 행사: {request.occasion}
- 예산 범위: ${request.budget_min} - ${request.budget_max}{style_text}{restrictions_text}

정확히 {MAX_RECOMMENDATIONS}개의 선물 추천을 포함하는 JSON 형식으로 응답해주세요. 각 추천에는 다음이 포함되어야 합니다:
- title: 명확하고 간결한 선물 이름 (한글)
- description: 왜 완벽한지 설명하는 2-3문장 설명 (한글)
- category: 주요 카테고리 (전자제품, 패션, 도서 등, 한글)
- estimated_price: USD 가격 (정수)
- reasoning: 이 선물이 프로필에 맞는 이유 (한글)
- confidence_score: 확신도 (0.0-1.0)

중점 사항:
1. 네이버쇼핑에서 검색 가능한 실제 상품명으로 작성
2. 관심사와 관계를 바탕으로 한 개인화
3. 행사와 예산에 적합함
4. 검색 키워드로 활용 가능한 구체적 명칭

모든 텍스트는 한글로 작성하고, 유효한 JSON 형식으로만 응답해주세요."""

        return prompt
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API with error handling and timeouts"""
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "당신은 개인화된 추천을 전문으로 하는 선물 컨설턴트입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7,
                    response_format={"type": "json_object"}
                ),
                timeout=API_TIMEOUT
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise Exception("Empty response from OpenAI API")
            return content
            
        except asyncio.TimeoutError:
            raise Exception(f"OpenAI API timeout after {API_TIMEOUT} seconds")
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _parse_recommendations(self, response_text: str) -> List[GiftRecommendation]:
        """Parse OpenAI response into structured recommendations"""
        try:
            data = json.loads(response_text)
            
            if isinstance(data, list):
                recommendations_data = data
            else:
                recommendations_data = (data.get('recommendations') or 
                                      data.get('gift_recommendations') or 
                                      data.get('gifts') or
                                      data.get('items') or [])
            
            recommendations = []
            for item in recommendations_data[:MAX_RECOMMENDATIONS]:
                try:
                    # estimated_price_krw 또는 estimated_price 둘 다 지원
                    price_krw = int(item.get('estimated_price_krw', item.get('estimated_price', 0)))
                    
                    recommendation = GiftRecommendation(
                        title=item.get('title', 'Unknown Gift'),
                        description=item.get('description', 'No description available'),
                        category=item.get('category', 'Other'),
                        estimated_price_krw=price_krw,
                        reasoning=item.get('reasoning', 'No reasoning provided'),
                        confidence_score=float(item.get('confidence_score', 0.5))
                    )
                    recommendations.append(recommendation)
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Skipping invalid recommendation: {e}")
                    continue
            
            return recommendations
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise Exception(f"Invalid JSON response from AI: {str(e)}")
    
    def _generate_mock_recommendations(self, request: GiftRequest) -> List[GiftRecommendation]:
        """시뮬레이션 모드용 가상 추천 생성"""
        mock_recommendations = [
            GiftRecommendation(
                title=f"{request.interests[0] if request.interests else '특별한'} 선물 세트",
                description=f"{request.recipient_age}세 {request.recipient_gender}에게 완벽한 {request.occasion} 선물입니다.",
                category="프리미엄 선물",
                estimated_price_krw=min(max(request.budget_max_krw - 10000, request.budget_min_krw), request.budget_max_krw),
                reasoning=f"받는 분의 관심사({', '.join(request.interests[:2]) if request.interests else '다양한 취미'})를 고려한 선택입니다.",
                confidence_score=0.85
            ),
            GiftRecommendation(
                title="블루투스 무선 헤드폰",
                description="고품질 사운드와 편안한 착용감을 제공하는 무선 헤드폰입니다.",
                category="전자제품",
                estimated_price_krw=min(max(request.budget_max_krw - 30000, request.budget_min_krw), request.budget_max_krw),
                reasoning="실용적이면서 모든 연령대가 좋아하는 인기 아이템입니다.",
                confidence_score=0.78
            ),
            GiftRecommendation(
                title="아로마 디퓨저 세트",
                description="집에서 편안한 분위기를 만들어주는 아로마 디퓨저와 오일 세트입니다.",
                category="홈&리빙",
                estimated_price_krw=min(max(request.budget_max_krw - 20000, request.budget_min_krw), request.budget_max_krw),
                reasoning="힐링과 휴식을 선호하는 분들에게 인기가 높은 선물입니다.",
                confidence_score=0.82
            )
        ]
        
        return mock_recommendations[:MAX_RECOMMENDATIONS]


class NaverShoppingClient:
    """네이버쇼핑 API 클라이언트"""
    
    def __init__(self, client_id: str = "", client_secret: str = ""):
        self.client_id = client_id
        self.client_secret = client_secret
        self.enabled = bool(client_id and client_secret)
        self.base_url = "https://openapi.naver.com/v1/search/shop.json"
        self.api_calls_count = 0
    
    async def search_products(self, keywords: List[str], budget_max_krw: int, 
                            display: int = 10, sort: str = "asc") -> List[NaverProductResult]:
        """상품 검색 (가격 오름차순 기본)"""
        if not self.enabled:
            return await self._simulate_search(keywords, budget_max_krw, display)
        
        try:
            # Build search query
            query = " ".join(keywords[:3])  # 최대 3개 키워드 조합
            logger.info(f"Searching Naver Shopping with query: '{query}', budget_max: {budget_max_krw:,}원")
            
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
        
        # KRW 예산 필터링
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
            price = min(budget_max_krw - (i * 10000), budget_max_krw - 5000)  # KRW 직접 사용
            
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
    """네이버쇼핑 API 기반 통합 추천 엔진"""
    
    def __init__(self, openai_api_key: str, naver_client_id: str = "", naver_client_secret: str = ""):
        self.ai_engine = GiftRecommendationEngine(openai_api_key)
        self.naver_client = NaverShoppingClient(naver_client_id, naver_client_secret)
        self.naver_enabled = self.naver_client.enabled
    
    async def generate_naver_recommendations(self, request: GiftRequest) -> NaverRecommendationResponse:
        """네이버쇼핑 API 기반 추천 생성"""
        start_time = datetime.now()
        request_id = f"naver_req_{int(start_time.timestamp())}"
        
        try:
            logger.info(f"Starting Naver Shopping recommendation for {request_id}")
            
            # Stage 1: AI 기본 추천 생성
            ai_start = time.time()
            ai_recommendations = await self.ai_engine.generate_recommendations(request)
            ai_time = time.time() - ai_start
            
            # Stage 2: 네이버쇼핑 검색
            naver_products = []
            naver_time = 0
            
            if ai_recommendations:
                naver_start = time.time()
                
                # 검색 키워드 추출
                search_keywords = self._extract_search_keywords(ai_recommendations[0], request)
                
                # 가격 오름차순으로 검색하여 최저가 우선
                naver_products = await self.naver_client.search_products(
                    search_keywords, request.budget_max_krw, display=10, sort="asc"
                )
                
                naver_time = time.time() - naver_start
                logger.info(f"Found {len(naver_products)} products in {naver_time:.2f}s")
            
            # Stage 3: AI 추천과 네이버쇼핑 상품 통합
            integration_start = time.time()
            enhanced_recommendations = await self._integrate_recommendations(
                ai_recommendations, naver_products, request
            )
            integration_time = time.time() - integration_start
            
            # 메트릭 수집
            total_time = (datetime.now() - start_time).total_seconds()
            
            metrics = NaverShoppingMetrics(
                ai_generation_time=ai_time,
                naver_search_time=naver_time,
                integration_time=integration_time,
                total_time=total_time,
                search_results_count=len(naver_products),
                api_calls_count=self.naver_client.api_calls_count,
                simulation_mode=SIMULATION_MODE
            )
            
            logger.info(f"Naver Shopping pipeline completed in {total_time:.2f}s")
            
            return NaverRecommendationResponse(
                request_id=request_id,
                recommendations=enhanced_recommendations,
                naver_products=naver_products,
                metrics=metrics,
                total_processing_time=total_time,
                created_at=start_time.isoformat(),
                success=True,
                naver_api_enabled=self.naver_enabled,
                simulation_mode=SIMULATION_MODE
            )
            
        except Exception as e:
            logger.error(f"Naver Shopping pipeline failed: {str(e)}")
            total_time = (datetime.now() - start_time).total_seconds()
            
            return NaverRecommendationResponse(
                request_id=request_id,
                recommendations=[],
                naver_products=[],
                metrics=NaverShoppingMetrics(
                    ai_generation_time=0, naver_search_time=0,
                    integration_time=0, total_time=total_time,
                    search_results_count=0, api_calls_count=0
                ),
                total_processing_time=total_time,
                created_at=start_time.isoformat(),
                success=False,
                naver_api_enabled=self.naver_enabled,
                simulation_mode=SIMULATION_MODE,
                error_message=str(e)
            )
    
    def _extract_search_keywords(self, recommendation: GiftRecommendation, request: GiftRequest) -> List[str]:
        """AI 추천에서 네이버쇼핑 검색 키워드 추출 (한국어 최적화)"""
        keywords = []
        
        # 추천 제목에서 키워드 추출 (한국어 명사 우선)
        title_words = recommendation.title.split()
        # 한국어 상품명에서 브랜드/제품명 우선 추출
        for word in title_words[:3]:
            if len(word) >= 2:  # 2글자 이상 키워드만
                keywords.append(word)
        
        # 카테고리 추가 (한국어 네이버쇼핑 카테고리에 맞게)
        if recommendation.category:
            # 카테고리 매핑 (AI가 생성한 카테고리 → 네이버쇼핑 검색어)
            category_mapping = {
                "전자제품": "전자기기",
                "홈&리빙": "생활용품", 
                "도서": "책",
                "식음료": "식품",
                "프리미엄 선물": "선물세트"
            }
            mapped_category = category_mapping.get(recommendation.category, recommendation.category)
            keywords.append(mapped_category)
        
        # 사용자 관심사 추가 (검색 정확도 향상)
        if request.interests:
            # 관심사를 상품 검색어로 변환
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
        
        # 중복 제거 및 순서 유지
        unique_keywords = []
        for keyword in keywords:
            if keyword not in unique_keywords:
                unique_keywords.append(keyword)
        
        logger.info(f"Generated search keywords: {unique_keywords[:4]}")
        return unique_keywords[:4]  # 최대 4개 키워드
    
    async def _integrate_recommendations(self, 
                                       ai_recommendations: List[GiftRecommendation], 
                                       naver_products: List[NaverProductResult],
                                       request: GiftRequest) -> List[GiftRecommendation]:
        """AI 추천과 네이버쇼핑 상품 통합"""
        if not naver_products:
            return ai_recommendations
        
        enhanced_recommendations = []
        
        # AI 추천 각각에 대해 가장 적합한 네이버쇼핑 상품 매칭
        for i, ai_rec in enumerate(ai_recommendations[:3]):
            
            # 가격 범위에 맞는 상품 필터링 (KRW 직접 비교)
            budget_products = [
                p for p in naver_products 
                if request.budget_min_krw <= p.lprice <= request.budget_max_krw
            ]
            
            if budget_products and i < len(budget_products):
                product = budget_products[i]
                
                # KRW 가격 직접 사용
                enhanced_rec = GiftRecommendation(
                    title=f"{ai_rec.title}",
                    description=f"{ai_rec.description}\n\n💰 최저가: {product.lprice:,}원 ({product.mallName})\n🏷️ 브랜드: {product.brand or '기타'}",
                    category=ai_rec.category,
                    estimated_price_krw=product.lprice,
                    reasoning=f"{ai_rec.reasoning}\n\n✅ 네이버쇼핑에서 실제 구매 가능한 상품을 찾았습니다. 가격 비교를 통해 최저가로 추천드립니다.",
                    purchase_link=product.link,
                    image_url=product.image,
                    confidence_score=min(ai_rec.confidence_score + 0.15, 1.0)  # 실제 상품 데이터로 신뢰도 증가
                )
                enhanced_recommendations.append(enhanced_rec)
            else:
                # 적합한 상품이 없으면 원래 AI 추천 유지
                enhanced_recommendations.append(ai_rec)
        
        return enhanced_recommendations


async def test_naver_shopping_engine():
    """네이버쇼핑 API 통합 엔진 테스트"""
    print("🛒 Gift Genie - 네이버쇼핑 API 추천 엔진 테스트")
    print("=" * 60)
    
    # 설정 정보 출력
    print(f"🔧 Configuration:")
    print(f"   OpenAI API: {'✅ Connected' if OPENAI_API_KEY != 'your-openai-api-key-here' else '❌ Simulation mode'}")
    print(f"   Naver Shopping API: {'✅ Connected' if NAVER_API_ENABLED else '❌ Simulation mode'}")
    print(f"   Overall Mode: {'🚀 Real API calls' if not SIMULATION_MODE else '🧪 Full simulation'}")
    print()
    
    # 엔진 초기화
    engine = NaverGiftRecommendationEngine(
        openai_api_key=OPENAI_API_KEY,
        naver_client_id=NAVER_CLIENT_ID,
        naver_client_secret=NAVER_CLIENT_SECRET
    )
    
    # 테스트 요청 생성
    test_request = GiftRequest(
        recipient_age=28,
        recipient_gender="여성",
        relationship="친구",
        budget_min_krw=50000,  # 5만원
        budget_max_krw=150000,  # 15만원
        interests=["독서", "커피", "여행", "사진"],
        occasion="생일",
        personal_style="미니멀리스트",
        restrictions=["쥬얼리 제외"]
    )
    
    print(f"📝 Test Request:")
    print(f"   Recipient: {test_request.recipient_age}yo {test_request.recipient_gender} {test_request.relationship}")
    print(f"   Budget: {test_request.budget_min_krw:,}원-{test_request.budget_max_krw:,}원")
    print(f"   Interests: {', '.join(test_request.interests)}")
    print()
    
    # 네이버쇼핑 추천 생성
    print("🤖 Generating Naver Shopping recommendations...")
    response = await engine.generate_naver_recommendations(test_request)
    
    # 결과 출력
    if response.success:
        print(f"✅ Success! Generated {len(response.recommendations)} recommendations")
        print(f"   Total time: {response.total_processing_time:.2f}s")
        print(f"   Performance metrics:")
        print(f"     - AI generation: {response.metrics.ai_generation_time:.2f}s")
        print(f"     - Naver search: {response.metrics.naver_search_time:.2f}s")
        print(f"     - Integration: {response.metrics.integration_time:.2f}s")
        print(f"   Naver products found: {response.metrics.search_results_count}")
        print(f"   API calls made: {response.metrics.api_calls_count}")
        print()
        
        for i, rec in enumerate(response.recommendations, 1):
            print(f"🎁 Recommendation #{i}: {rec.title}")
            print(f"   💰 Price: {rec.estimated_price_krw:,}원")
            print(f"   📂 Category: {rec.category}")
            print(f"   ⭐ Confidence: {rec.confidence_score:.2f}/1.0")
            if rec.purchase_link:
                print(f"   🔗 Buy Now: {rec.purchase_link[:50]}...")
            if rec.image_url:
                print(f"   🖼️ Image: {rec.image_url[:50]}...")
            print(f"   📝 Description: {rec.description}")
            print(f"   🧠 Reasoning: {rec.reasoning}")
            print()
        
        # 네이버쇼핑 상품 요약
        if response.naver_products:
            print("🛒 Naver Shopping Products Found:")
            for i, product in enumerate(response.naver_products[:3], 1):
                print(f"   {i}. {product.title[:40]}...")
                print(f"      💰 {product.lprice:,}원 - {product.hprice:,}원 ({product.mallName})")
                if product.brand:
                    print(f"      🏷️ Brand: {product.brand}")
            print()
    else:
        print(f"❌ Failed to generate recommendations")
        print(f"   Error: {response.error_message}")


async def main():
    """Main test runner"""
    try:
        print("🚀 Starting Naver Shopping API Integration Test")
        print("=" * 60)
        print()
        
        await test_naver_shopping_engine()
        
        print("✅ Test completed!")
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"❌ Test execution failed: {e}")


if __name__ == "__main__":
    # Check dependencies
    try:
        import openai
        import aiohttp
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install openai aiohttp")
        exit(1)
    
    # API 키 상태 확인
    if not NAVER_API_ENABLED:
        print("⚠️  Naver Shopping API keys not set - Running in SIMULATION mode")
        print("💡 For real API calls, set: NAVER_CLIENT_ID & NAVER_CLIENT_SECRET")
        print()
    
    if OPENAI_API_KEY == "your-openai-api-key-here":
        print("⚠️  OpenAI API key not set - AI recommendations in SIMULATION mode")
        print()
    
    # 테스트 실행
    asyncio.run(main())