# Gift Genie MCP 파이프라인 데모
# 외부 라이브러리 없이 기본 구조 시연

import asyncio
import json
import hashlib
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. 데이터 모델
@dataclass
class PipelineMetrics:
    total_time: float
    ai_generation_time: float
    search_execution_time: float
    scraping_execution_time: float
    integration_time: float
    cache_hits: int = 0
    cache_misses: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

@dataclass
class MCPResponse:
    request_id: str
    success: bool
    recommendations: List[Dict[str, Any]]
    search_insights: Dict[str, Any]
    metrics: PipelineMetrics
    errors: List[str]

# 2. 시뮬레이션 클라이언트들
class MockAIClient:
    """GPT-4o-mini 시뮬레이션"""
    
    async def generate_search_strategy(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """검색 전략 생성 시뮬레이션"""
        await asyncio.sleep(0.1)  # API 호출 시뮬레이션
        
        recipient = request.get("recipient", {})
        interests = recipient.get("interests", [])
        
        return {
            "search_keywords": interests + ["선물", "추천"],
            "product_categories": ["생활용품", "전자기기", "패션"],
            "trending_terms": ["인기", "베스트", "신상"],
            "exclusions": ["중고", "리퍼"]
        }
    
    async def generate_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """최종 추천 생성 시뮬레이션"""
        await asyncio.sleep(0.1)
        
        request = context["request"]
        budget = request.get("budget", {})
        max_price = budget.get("max", 100000)
        
        # 시뮬레이션된 추천 결과
        recommendations = []
        for i in range(1, 4):  # 3개 추천
            recommendations.append({
                "rank": i,
                "product_name": f"추천 상품 {i}",
                "brand": f"브랜드 {i}",
                "price": min(max_price * 0.8, 50000 + i * 10000),
                "image_url": f"https://example.com/product{i}.jpg",
                "purchase_url": f"https://shop.example.com/product{i}",
                "recommendation_reason": f"사용자의 관심사와 예산을 고려한 {i}번째 추천입니다.",
                "match_score": 90 - i * 5,
                "tags": ["인기", "추천", f"태그{i}"]
            })
        
        return recommendations

class MockSearchClient:
    """Brave Search 시뮬레이션"""
    
    async def search_products(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """상품 검색 시뮬레이션"""
        await asyncio.sleep(0.2)
        
        keywords = strategy.get("search_keywords", [])
        
        # 시뮬레이션된 검색 결과
        results = []
        for i, keyword in enumerate(keywords[:5]):
            results.append({
                "title": f"{keyword} 관련 상품 {i+1}",
                "url": f"https://shop.example.com/{keyword}-product-{i+1}",
                "description": f"{keyword}에 대한 상세한 상품 설명입니다.",
                "domain": "example.com",
                "relevance_score": 0.9 - i * 0.1
            })
        
        return {
            "results": results,
            "total_count": len(results),
            "trending_insights": {
                "popular_domains": [("example.com", 5), ("shop.com", 3)],
                "trending_keywords": [(kw, i+1) for i, kw in enumerate(keywords)]
            }
        }

class MockScrapingClient:
    """Apify 스크래핑 시뮬레이션"""
    
    async def scrape_product_details(self, urls: List[str]) -> List[Dict[str, Any]]:
        """상품 상세정보 스크래핑 시뮬레이션"""
        await asyncio.sleep(0.3)
        
        results = []
        for i, url in enumerate(urls[:5]):
            results.append({
                "url": url,
                "name": f"상품명 {i+1}",
                "brand": f"브랜드 {i+1}",
                "price": 50000 + i * 10000,
                "original_price": 60000 + i * 12000,
                "discount_rate": 15 + i * 2,
                "image_urls": [f"https://example.com/image{i+1}.jpg"],
                "rating": 4.5 - i * 0.1,
                "review_count": 100 + i * 20,
                "description": f"상품 {i+1}에 대한 상세 설명입니다.",
                "availability": "in_stock",
                "vendor": ["쿠팡", "지마켓", "11번가"][i % 3]
            })
        
        return results

# 3. 간단한 캐시 매니저
class MockCacheManager:
    """메모리 기반 캐시 시뮬레이션"""
    
    def __init__(self):
        self.cache = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    async def get(self, prefix: str, data: Any) -> Optional[Dict]:
        key = self._generate_key(prefix, data)
        if key in self.cache:
            self.hit_count += 1
            return self.cache[key]
        else:
            self.miss_count += 1
            return None
    
    async def set(self, prefix: str, data: Any, value: Dict, ttl: int):
        key = self._generate_key(prefix, data)
        self.cache[key] = value
        # TTL은 시뮬레이션에서는 무시

# 4. 메인 파이프라인
class MCPPipelineDemo:
    """MCP 파이프라인 데모"""
    
    def __init__(self):
        self.ai_client = MockAIClient()
        self.search_client = MockSearchClient()
        self.scraping_client = MockScrapingClient()
        self.cache_manager = MockCacheManager()
    
    async def process_request(self, request: Dict[str, Any]) -> MCPResponse:
        """요청 처리 메인 함수"""
        request_id = hashlib.md5(json.dumps(request, sort_keys=True).encode()).hexdigest()[:8]
        start_time = time.time()
        
        logger.info(f"[{request_id}] 파이프라인 시작")
        
        try:
            # 1단계: AI 검색 전략 생성
            logger.info(f"[{request_id}] 1단계: AI 검색 전략 생성")
            stage_start = time.time()
            
            strategy = await self._ai_generation_stage(request)
            ai_time = time.time() - stage_start
            
            logger.info(f"[{request_id}] 검색 키워드: {strategy['search_keywords']}")
            
            # 2단계: 검색 실행
            logger.info(f"[{request_id}] 2단계: Brave Search 검색")
            stage_start = time.time()
            
            search_results = await self._search_execution_stage(strategy)
            search_time = time.time() - stage_start
            
            logger.info(f"[{request_id}] 검색 결과: {search_results['total_count']}개")
            
            # 3단계: 스크래핑 실행
            logger.info(f"[{request_id}] 3단계: Apify 스크래핑")
            stage_start = time.time()
            
            urls = [result["url"] for result in search_results["results"]]
            product_details = await self._scraping_execution_stage(urls)
            scraping_time = time.time() - stage_start
            
            logger.info(f"[{request_id}] 스크래핑 완료: {len(product_details)}개")
            
            # 4단계: 결과 통합
            logger.info(f"[{request_id}] 4단계: 결과 통합")
            stage_start = time.time()
            
            context = {
                "request": request,
                "strategy": strategy,
                "search_results": search_results["results"],
                "product_details": product_details
            }
            
            recommendations = await self._integration_stage(context)
            integration_time = time.time() - stage_start
            
            total_time = time.time() - start_time
            
            # 메트릭 생성
            metrics = PipelineMetrics(
                total_time=total_time,
                ai_generation_time=ai_time,
                search_execution_time=search_time,
                scraping_execution_time=scraping_time,
                integration_time=integration_time,
                cache_hits=self.cache_manager.hit_count,
                cache_misses=self.cache_manager.miss_count
            )
            
            logger.info(f"[{request_id}] 파이프라인 완료 ({total_time:.2f}초)")
            
            return MCPResponse(
                request_id=request_id,
                success=True,
                recommendations=recommendations,
                search_insights=search_results.get("trending_insights", {}),
                metrics=metrics,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"[{request_id}] 파이프라인 실패: {e}")
            
            metrics = PipelineMetrics(
                total_time=time.time() - start_time,
                ai_generation_time=0,
                search_execution_time=0,
                scraping_execution_time=0,
                integration_time=0,
                errors=[str(e)]
            )
            
            return MCPResponse(
                request_id=request_id,
                success=False,
                recommendations=[],
                search_insights={},
                metrics=metrics,
                errors=[str(e)]
            )
    
    async def _ai_generation_stage(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """AI 생성 단계"""
        cached = await self.cache_manager.get("ai", request)
        if cached:
            logger.info("AI 전략 캐시 히트")
            return cached
        
        strategy = await self.ai_client.generate_search_strategy(request)
        await self.cache_manager.set("ai", request, strategy, 1800)  # 30분
        
        return strategy
    
    async def _search_execution_stage(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """검색 실행 단계"""
        cached = await self.cache_manager.get("search", strategy)
        if cached:
            logger.info("검색 결과 캐시 히트")
            return cached
        
        results = await self.search_client.search_products(strategy)
        await self.cache_manager.set("search", strategy, results, 3600)  # 1시간
        
        return results
    
    async def _scraping_execution_stage(self, urls: List[str]) -> List[Dict[str, Any]]:
        """스크래핑 실행 단계"""
        return await self.scraping_client.scrape_product_details(urls)
    
    async def _integration_stage(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """결과 통합 단계"""
        return await self.ai_client.generate_recommendations(context)

# 5. 데모 실행
async def demo_main():
    """데모 실행"""
    print("🎁 Gift Genie MCP 파이프라인 데모")
    print("=" * 50)
    
    pipeline = MCPPipelineDemo()
    
    # 테스트 요청 1
    test_request_1 = {
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
    
    print("\n📝 테스트 요청 1:")
    print(f"- 받는 사람: 30대 여성")
    print(f"- 관심사: {', '.join(test_request_1['recipient']['interests'])}")
    print(f"- 예산: {test_request_1['budget']['min']:,}원 ~ {test_request_1['budget']['max']:,}원")
    print(f"- 목적: {test_request_1['occasion']}")
    
    result_1 = await pipeline.process_request(test_request_1)
    
    print(f"\n✅ 결과 1:")
    print(f"- 요청 ID: {result_1.request_id}")
    print(f"- 성공 여부: {result_1.success}")
    print(f"- 총 처리 시간: {result_1.metrics.total_time:.2f}초")
    print(f"- 추천 상품 수: {len(result_1.recommendations)}")
    print(f"- 캐시 히트/미스: {result_1.metrics.cache_hits}/{result_1.metrics.cache_misses}")
    
    if result_1.recommendations:
        print("\n🎯 추천 상품:")
        for rec in result_1.recommendations:
            print(f"  {rec['rank']}. {rec['product_name']} ({rec['brand']})")
            print(f"     가격: {rec['price']:,}원, 매칭점수: {rec['match_score']}")
            print(f"     이유: {rec['recommendation_reason']}")
    
    # 테스트 요청 2 (캐시 테스트)
    print("\n" + "=" * 50)
    print("📝 테스트 요청 2 (동일 요청으로 캐시 테스트):")
    
    result_2 = await pipeline.process_request(test_request_1)  # 같은 요청
    
    print(f"\n✅ 결과 2:")
    print(f"- 요청 ID: {result_2.request_id}")
    print(f"- 총 처리 시간: {result_2.metrics.total_time:.2f}초 (캐시로 단축)")
    print(f"- 캐시 히트/미스: {result_2.metrics.cache_hits}/{result_2.metrics.cache_misses}")
    
    # 성능 분석
    print("\n" + "=" * 50)
    print("📊 성능 분석:")
    print(f"- 첫 번째 요청: {result_1.metrics.total_time:.2f}초")
    print(f"  └ AI 생성: {result_1.metrics.ai_generation_time:.2f}초")
    print(f"  └ 검색 실행: {result_1.metrics.search_execution_time:.2f}초") 
    print(f"  └ 스크래핑: {result_1.metrics.scraping_execution_time:.2f}초")
    print(f"  └ 결과 통합: {result_1.metrics.integration_time:.2f}초")
    
    print(f"- 두 번째 요청: {result_2.metrics.total_time:.2f}초 (캐시 활용)")
    
    speed_improvement = (result_1.metrics.total_time - result_2.metrics.total_time) / result_1.metrics.total_time * 100
    print(f"- 캐시로 인한 성능 향상: {speed_improvement:.1f}%")

if __name__ == "__main__":
    asyncio.run(demo_main())