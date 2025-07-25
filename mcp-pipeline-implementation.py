# Gift Genie MCP 파이프라인 구현
# Sequential MCP 서버를 활용한 실제 구현 예시

import asyncio
import aiohttp
import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import redis
import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. 설정 및 상수
class Config:
    """MCP 파이프라인 설정"""
    OPENAI_API_KEY = "your-openai-api-key"
    BRAVE_API_KEY = "your-brave-search-api-key"
    APIFY_API_KEY = "your-apify-api-key"
    
    REDIS_URL = "redis://localhost:6379"
    
    # 타임아웃 설정
    AI_TIMEOUT = 10
    SEARCH_TIMEOUT = 8
    SCRAPING_TIMEOUT = 15
    
    # 재시도 설정
    MAX_RETRIES = 3
    RETRY_DELAY = [1, 2, 4]  # 지수 백오프
    
    # 캐시 TTL
    SEARCH_CACHE_TTL = 3600    # 1시간
    PRODUCT_CACHE_TTL = 21600  # 6시간
    AI_CACHE_TTL = 1800        # 30분

# 2. 예외 정의
class MCPPipelineError(Exception):
    """MCP 파이프라인 기본 예외"""
    pass

class AIGenerationError(MCPPipelineError):
    """AI 생성 단계 오류"""
    pass

class SearchExecutionError(MCPPipelineError):
    """검색 실행 단계 오류"""
    pass

class ScrapingExecutionError(MCPPipelineError):
    """스크래핑 실행 단계 오류"""
    pass

class IntegrationError(MCPPipelineError):
    """결과 통합 단계 오류"""
    pass

# 3. 데이터 모델
@dataclass
class PipelineMetrics:
    """파이프라인 성능 메트릭"""
    total_time: float
    ai_generation_time: float
    search_execution_time: float
    scraping_execution_time: float
    integration_time: float
    cache_hits: int
    cache_misses: int
    errors: List[str]

@dataclass
class MCPResponse:
    """MCP 파이프라인 통합 응답"""
    request_id: str
    success: bool
    recommendations: List[Dict[str, Any]]
    search_insights: Dict[str, Any]
    metrics: PipelineMetrics
    errors: List[str]

# 4. 캐시 관리자
class CacheManager:
    """Redis 기반 캐시 관리"""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """캐시 키 생성"""
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    async def get(self, prefix: str, data: Any) -> Optional[Dict]:
        """캐시 조회"""
        key = self._generate_key(prefix, data)
        try:
            cached = self.redis.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        return None
    
    async def set(self, prefix: str, data: Any, value: Dict, ttl: int):
        """캐시 저장"""
        key = self._generate_key(prefix, data)
        try:
            self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Cache set error: {e}")

# 5. MCP 서비스 클라이언트
class AIClient:
    """GPT-4o-mini 클라이언트"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    async def generate_search_strategy(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """검색 전략 생성"""
        prompt = self._build_search_prompt(request)
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            async with session.post(
                self.base_url, 
                headers=headers, 
                json=payload,
                timeout=Config.AI_TIMEOUT
            ) as response:
                if response.status != 200:
                    raise AIGenerationError(f"AI API error: {response.status}")
                
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # JSON 파싱 실패 시 기본 전략 반환
                    return self._fallback_search_strategy(request)
    
    def _build_search_prompt(self, request: Dict[str, Any]) -> str:
        """검색 프롬프트 구성"""
        recipient = request["recipient"]
        budget = request["budget"]
        
        return f"""
다음 조건에 맞는 선물 검색 전략을 JSON 형태로 생성해주세요:

받는 사람:
- 성별: {recipient.get('gender', '상관없음')}
- 나이대: {recipient.get('age_group', '30대')}
- 관심사: {', '.join(recipient.get('interests', []))}

예산: {budget.get('min', 0):,}원 ~ {budget.get('max', 100000):,}원

다음 JSON 형식으로 응답해주세요:
{{
    "search_keywords": ["키워드1", "키워드2", "키워드3"],
    "product_categories": ["카테고리1", "카테고리2"],
    "trending_terms": ["트렌드1", "트렌드2"],
    "exclusions": ["제외할_키워드1", "제외할_키워드2"]
}}
"""
    
    def _fallback_search_strategy(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """기본 검색 전략"""
        recipient = request["recipient"]
        interests = recipient.get("interests", [])
        
        return {
            "search_keywords": interests + ["선물", "추천"],
            "product_categories": ["생활용품", "전자기기"],
            "trending_terms": ["인기", "베스트"],
            "exclusions": []
        }
    
    async def generate_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """최종 추천 생성"""
        prompt = self._build_recommendation_prompt(context)
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 1000
            }
            
            async with session.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=Config.AI_TIMEOUT
            ) as response:
                if response.status != 200:
                    raise IntegrationError(f"AI API error: {response.status}")
                
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                
                try:
                    return json.loads(content)["recommendations"]
                except (json.JSONDecodeError, KeyError):
                    return self._fallback_recommendations(context)
    
    def _build_recommendation_prompt(self, context: Dict[str, Any]) -> str:
        """추천 생성 프롬프트"""
        return f"""
다음 검색 결과와 상품 정보를 바탕으로 3-5개의 개인화된 선물 추천을 생성해주세요:

사용자 요청: {context['request']}
검색 결과: {context['search_results'][:3]}  # 처음 3개만
상품 상세정보: {context['product_details'][:3]}  # 처음 3개만

다음 JSON 형식으로 응답해주세요:
{{
    "recommendations": [
        {{
            "rank": 1,
            "product_name": "상품명",
            "brand": "브랜드",
            "price": 50000,
            "image_url": "이미지_URL",
            "purchase_url": "구매_URL",
            "recommendation_reason": "이 상품을 추천하는 구체적인 이유",
            "match_score": 85,
            "tags": ["태그1", "태그2"]
        }}
    ]
}}
"""
    
    def _fallback_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """기본 추천"""
        return [
            {
                "rank": 1,
                "product_name": "개인화 추천 상품",
                "brand": "Gift Genie",
                "price": 50000,
                "image_url": "",
                "purchase_url": "",
                "recommendation_reason": "사용자의 관심사와 예산을 고려한 추천입니다.",
                "match_score": 75,
                "tags": ["추천", "인기"]
            }
        ]

class SearchClient:
    """Brave Search 클라이언트"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
    
    async def search_products(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """상품 검색"""
        keywords = strategy["search_keywords"]
        query = " ".join(keywords[:3])  # 최대 3개 키워드
        
        params = {
            "q": f"{query} 쇼핑 구매",
            "count": 20,
            "search_lang": "ko",
            "country": "KR",
            "safesearch": "moderate"
        }
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=Config.SEARCH_TIMEOUT
            ) as response:
                if response.status != 200:
                    raise SearchExecutionError(f"Search API error: {response.status}")
                
                data = await response.json()
                return self._process_search_results(data)
    
    def _process_search_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """검색 결과 처리"""
        results = data.get("web", {}).get("results", [])
        
        processed_results = []
        for result in results[:10]:  # 상위 10개만
            processed_results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "description": result.get("description", ""),
                "domain": result.get("profile", {}).get("name", "")
            })
        
        return {
            "results": processed_results,
            "total_count": len(processed_results),
            "trending_insights": self._extract_trends(results)
        }
    
    def _extract_trends(self, results: List[Dict]) -> Dict[str, Any]:
        """트렌드 인사이트 추출"""
        domains = {}
        keywords = {}
        
        for result in results:
            domain = result.get("profile", {}).get("name", "")
            if domain:
                domains[domain] = domains.get(domain, 0) + 1
            
            title = result.get("title", "").lower()
            for word in title.split():
                if len(word) > 2:
                    keywords[word] = keywords.get(word, 0) + 1
        
        return {
            "popular_domains": sorted(domains.items(), key=lambda x: x[1], reverse=True)[:5],
            "trending_keywords": sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        }

class ScrapingClient:
    """Apify 스크래핑 클라이언트"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.apify.com/v2"
    
    async def scrape_product_details(self, urls: List[str]) -> List[Dict[str, Any]]:
        """상품 상세정보 스크래핑"""
        # 실제 구현에서는 Apify Actor를 사용
        # 여기서는 시뮬레이션
        results = []
        
        for url in urls[:5]:  # 최대 5개
            try:
                result = await self._scrape_single_product(url)
                results.append(result)
            except Exception as e:
                logger.warning(f"Scraping failed for {url}: {e}")
                results.append(self._fallback_product_data(url))
        
        return results
    
    async def _scrape_single_product(self, url: str) -> Dict[str, Any]:
        """단일 상품 스크래핑 (시뮬레이션)"""
        await asyncio.sleep(0.5)  # API 호출 시뮬레이션
        
        return {
            "url": url,
            "name": "스크래핑된 상품명",
            "price": 75000,
            "original_price": 90000,
            "discount_rate": 17,
            "image_urls": ["https://example.com/image.jpg"],
            "rating": 4.5,
            "review_count": 124,
            "brand": "추출된 브랜드",
            "description": "상품 설명...",
            "availability": "in_stock"
        }
    
    def _fallback_product_data(self, url: str) -> Dict[str, Any]:
        """기본 상품 데이터"""
        return {
            "url": url,
            "name": "상품 정보 확인 필요",
            "price": 0,
            "original_price": 0,
            "discount_rate": 0,
            "image_urls": [],
            "rating": 0,
            "review_count": 0,
            "brand": "",
            "description": "",
            "availability": "unknown"
        }

# 6. 메인 파이프라인 오케스트레이터
class MCPPipeline:
    """MCP 파이프라인 오케스트레이터"""
    
    def __init__(self):
        self.ai_client = AIClient(Config.OPENAI_API_KEY)
        self.search_client = SearchClient(Config.BRAVE_API_KEY)
        self.scraping_client = ScrapingClient(Config.APIFY_API_KEY)
        self.cache_manager = CacheManager(Config.REDIS_URL)
    
    async def process_request(self, request: Dict[str, Any]) -> MCPResponse:
        """요청 처리 메인 함수"""
        request_id = hashlib.md5(json.dumps(request, sort_keys=True).encode()).hexdigest()
        start_time = time.time()
        
        metrics = PipelineMetrics(
            total_time=0,
            ai_generation_time=0,
            search_execution_time=0,
            scraping_execution_time=0,
            integration_time=0,
            cache_hits=0,
            cache_misses=0,
            errors=[]
        )
        
        try:
            # 1단계: AI 검색 전략 생성
            logger.info("Starting AI generation stage")
            stage_start = time.time()
            
            strategy = await self._execute_with_retry(
                self._ai_generation_stage,
                request,
                "ai_generation"
            )
            
            metrics.ai_generation_time = time.time() - stage_start
            
            # 2단계: 검색 실행
            logger.info("Starting search execution stage")
            stage_start = time.time()
            
            search_results = await self._execute_with_retry(
                self._search_execution_stage,
                strategy,
                "search_execution"
            )
            
            metrics.search_execution_time = time.time() - stage_start
            
            # 3단계: 스크래핑 실행 (병렬)
            logger.info("Starting scraping execution stage")
            stage_start = time.time()
            
            product_details = await self._execute_with_retry(
                self._scraping_execution_stage,
                search_results["results"],
                "scraping_execution"
            )
            
            metrics.scraping_execution_time = time.time() - stage_start
            
            # 4단계: 결과 통합
            logger.info("Starting integration stage")
            stage_start = time.time()
            
            context = {
                "request": request,
                "strategy": strategy,
                "search_results": search_results["results"],
                "product_details": product_details
            }
            
            recommendations = await self._execute_with_retry(
                self._integration_stage,
                context,
                "integration"
            )
            
            metrics.integration_time = time.time() - stage_start
            metrics.total_time = time.time() - start_time
            
            return MCPResponse(
                request_id=request_id,
                success=True,
                recommendations=recommendations,
                search_insights=search_results.get("trending_insights", {}),
                metrics=metrics,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            metrics.total_time = time.time() - start_time
            metrics.errors.append(str(e))
            
            return MCPResponse(
                request_id=request_id,
                success=False,
                recommendations=[],
                search_insights={},
                metrics=metrics,
                errors=[str(e)]
            )
    
    async def _execute_with_retry(self, func, *args, stage_name: str):
        """재시도 로직이 포함된 실행"""
        last_error = None
        
        for attempt in range(Config.MAX_RETRIES):
            try:
                return await func(*args)
            except Exception as e:
                last_error = e
                if attempt < Config.MAX_RETRIES - 1:
                    delay = Config.RETRY_DELAY[attempt]
                    logger.warning(f"{stage_name} failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{stage_name} failed after {Config.MAX_RETRIES} attempts: {e}")
        
        raise last_error
    
    async def _ai_generation_stage(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """AI 생성 단계"""
        cached = await self.cache_manager.get("ai", request)
        if cached:
            return cached
        
        strategy = await self.ai_client.generate_search_strategy(request)
        await self.cache_manager.set("ai", request, strategy, Config.AI_CACHE_TTL)
        
        return strategy
    
    async def _search_execution_stage(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """검색 실행 단계"""
        cached = await self.cache_manager.get("search", strategy)
        if cached:
            return cached
        
        results = await self.search_client.search_products(strategy)
        await self.cache_manager.set("search", strategy, results, Config.SEARCH_CACHE_TTL)
        
        return results
    
    async def _scraping_execution_stage(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """스크래핑 실행 단계"""
        urls = [result["url"] for result in search_results[:5]]
        
        # 캐시 확인 (URL별)
        cached_results = []
        urls_to_scrape = []
        
        for url in urls:
            cached = await self.cache_manager.get("product", {"url": url})
            if cached:
                cached_results.append(cached)
            else:
                urls_to_scrape.append(url)
        
        # 스크래핑 실행
        if urls_to_scrape:
            scraped_results = await self.scraping_client.scrape_product_details(urls_to_scrape)
            
            # 결과 캐시
            for result in scraped_results:
                await self.cache_manager.set(
                    "product", 
                    {"url": result["url"]}, 
                    result, 
                    Config.PRODUCT_CACHE_TTL
                )
            
            cached_results.extend(scraped_results)
        
        return cached_results
    
    async def _integration_stage(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """결과 통합 단계"""
        return await self.ai_client.generate_recommendations(context)

# 7. 사용 예시
async def main():
    """사용 예시"""
    pipeline = MCPPipeline()
    
    # 테스트 요청
    test_request = {
        "recipient": {
            "gender": "female",
            "age_group": "30s",
            "interests": ["reading", "coffee", "travel"]
        },
        "budget": {
            "min": 30000,
            "max": 100000
        },
        "occasion": "birthday"
    }
    
    # 파이프라인 실행
    result = await pipeline.process_request(test_request)
    
    print(f"Request ID: {result.request_id}")
    print(f"Success: {result.success}")
    print(f"Total Time: {result.metrics.total_time:.2f}s")
    print(f"Recommendations: {len(result.recommendations)}")
    
    if result.errors:
        print(f"Errors: {result.errors}")

if __name__ == "__main__":
    asyncio.run(main())