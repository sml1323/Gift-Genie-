"""
Gift Genie - Intelligent Query Refinement Engine
AI-driven query optimization with 5-iteration retry mechanism
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Constants
MAX_RETRY_ATTEMPTS = 5
QUERY_REFINEMENT_TIMEOUT = 10
MIN_PRODUCTS_THRESHOLD = 3  # Minimum products needed to consider search successful


@dataclass
class QueryRefinementAttempt:
    """단일 쿼리 개선 시도 기록"""
    attempt_number: int
    original_keywords: List[str]
    refined_keywords: List[str]
    search_query: str  
    products_found: int
    success: bool
    refinement_strategy: str  # "synonym_expansion", "category_broadening", "market_research", "demographic_adaptation", "budget_alternative"
    processing_time: float
    failure_reason: Optional[str] = None
    market_insights: Optional[Dict[str, Any]] = None


@dataclass
class QueryRefinementSession:
    """전체 쿼리 개선 세션 기록"""
    session_id: str
    gift_request_context: Dict[str, Any]
    attempts: List[QueryRefinementAttempt]
    final_success: bool
    total_products_found: int
    total_processing_time: float
    best_attempt: Optional[QueryRefinementAttempt] = None


class IntelligentQueryRefinementEngine:
    """AI 기반 쿼리 개선 엔진"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.simulation_mode = (openai_api_key == "your-openai-api-key-here" or not openai_api_key)
        
        if not self.simulation_mode:
            self.client = AsyncOpenAI(api_key=openai_api_key)
        
        # 개선 전략 가중치 (시도 횟수에 따라 조정)
        self.refinement_strategies = [
            "synonym_expansion",      # 1차: 동의어 확장
            "category_broadening",    # 2차: 카테고리 확장  
            "market_research",        # 3차: 시장 조사 기반 개선
            "demographic_adaptation", # 4차: 인구통계학적 적응
            "budget_alternative"      # 5차: 예산 대안 상품
        ]
    
    async def refine_search_with_retries(
        self, 
        original_keywords: List[str],
        gift_context: Dict[str, Any],
        search_function,  # 검색 함수 (Naver Shopping API)
        budget_max_krw: int
    ) -> Tuple[List[Any], QueryRefinementSession]:
        """5회 재시도로 최적 상품 검색"""
        
        session_id = f"refine_{int(time.time())}"
        session_start_time = time.time()
        
        logger.info(f"🔄 Starting intelligent query refinement session {session_id}")
        logger.info(f"  → Original keywords: {original_keywords}")
        logger.info(f"  → Gift context: {gift_context}")
        
        session = QueryRefinementSession(
            session_id=session_id,
            gift_request_context=gift_context,
            attempts=[],
            final_success=False,
            total_products_found=0,
            total_processing_time=0.0
        )
        
        best_products = []
        best_attempt = None
        
        for attempt_num in range(1, MAX_RETRY_ATTEMPTS + 1):
            attempt_start_time = time.time()
            
            # 시도별 개선 전략 선택
            strategy = self.refinement_strategies[min(attempt_num - 1, len(self.refinement_strategies) - 1)]
            
            logger.info(f"📈 Attempt {attempt_num}/{MAX_RETRY_ATTEMPTS} - Strategy: {strategy}")
            
            try:
                # 1단계: 키워드 개선
                if attempt_num == 1:
                    # 첫 시도는 원본 키워드 사용
                    refined_keywords = original_keywords.copy()
                    search_query = " ".join(refined_keywords)
                else:
                    # AI 기반 키워드 개선
                    refined_keywords, search_query = await self._refine_keywords_with_ai(
                        original_keywords=original_keywords,
                        previous_attempts=session.attempts,
                        strategy=strategy,
                        gift_context=gift_context,
                        attempt_number=attempt_num
                    )
                
                # 2단계: 시장 조사 인사이트 수집 (3차 시도부터)
                market_insights = None
                if attempt_num >= 3 and strategy == "market_research":
                    market_insights = await self._get_market_insights(
                        keywords=refined_keywords,
                        gift_context=gift_context
                    )
                    
                    # 시장 조사 결과로 키워드 재조정
                    if market_insights and market_insights.get("suggested_products"):
                        refined_keywords = self._integrate_market_suggestions(
                            refined_keywords, market_insights
                        )
                        search_query = " ".join(refined_keywords)
                
                # 3단계: 개선된 키워드로 상품 검색
                logger.info(f"  → Refined keywords: {refined_keywords}")
                logger.info(f"  → Search query: '{search_query}'")
                
                products = await search_function(refined_keywords, budget_max_krw)
                
                attempt_time = time.time() - attempt_start_time
                products_count = len(products)
                
                # 4단계: 시도 결과 기록
                attempt = QueryRefinementAttempt(
                    attempt_number=attempt_num,
                    original_keywords=original_keywords,
                    refined_keywords=refined_keywords,
                    search_query=search_query,
                    products_found=products_count,
                    success=products_count >= MIN_PRODUCTS_THRESHOLD,
                    refinement_strategy=strategy,
                    processing_time=attempt_time,
                    market_insights=market_insights
                )
                
                session.attempts.append(attempt)
                
                logger.info(f"  ✅ Found {products_count} products in {attempt_time:.2f}s")
                
                # 5단계: 성공 조건 체크
                if products_count >= MIN_PRODUCTS_THRESHOLD:
                    best_products = products
                    best_attempt = attempt
                    session.final_success = True
                    session.best_attempt = attempt
                    logger.info(f"🎯 Success! Found sufficient products on attempt {attempt_num}")
                    break
                elif products_count > len(best_products):
                    # 이전 시도보다 더 많은 상품을 찾은 경우 기록
                    best_products = products
                    best_attempt = attempt
                    session.best_attempt = attempt
                
                # 6단계: 다음 시도를 위한 대기
                if attempt_num < MAX_RETRY_ATTEMPTS:
                    logger.info(f"  ⏳ Insufficient products ({products_count}), trying next strategy...")
                    await asyncio.sleep(0.5)  # API 호출 간격 조정
                
            except Exception as e:
                attempt_time = time.time() - attempt_start_time
                logger.error(f"  ❌ Attempt {attempt_num} failed: {str(e)}")
                
                failed_attempt = QueryRefinementAttempt(
                    attempt_number=attempt_num,
                    original_keywords=original_keywords,
                    refined_keywords=refined_keywords if 'refined_keywords' in locals() else original_keywords,
                    search_query=search_query if 'search_query' in locals() else " ".join(original_keywords),
                    products_found=0,
                    success=False,
                    refinement_strategy=strategy,
                    processing_time=attempt_time,
                    failure_reason=str(e)
                )
                
                session.attempts.append(failed_attempt)
                continue
        
        # 세션 완료 처리
        session.total_processing_time = time.time() - session_start_time
        session.total_products_found = len(best_products)
        
        if not session.final_success and best_products:
            logger.warning(f"⚠️  Session completed with partial success: {len(best_products)} products found")
        elif not best_products:
            logger.error(f"❌ Session failed: No products found after {MAX_RETRY_ATTEMPTS} attempts")
        
        self._log_session_summary(session)
        
        return best_products, session
    
    async def _refine_keywords_with_ai(
        self,
        original_keywords: List[str],
        previous_attempts: List[QueryRefinementAttempt],
        strategy: str,
        gift_context: Dict[str, Any],
        attempt_number: int
    ) -> Tuple[List[str], str]:
        """AI 기반 키워드 개선"""
        
        if self.simulation_mode:
            return await self._simulate_keyword_refinement(original_keywords, strategy, attempt_number)
        
        # 이전 시도 분석
        failed_keywords = []
        for attempt in previous_attempts:
            if not attempt.success:
                failed_keywords.extend(attempt.refined_keywords)
        failed_keywords = list(set(failed_keywords))  # 중복 제거
        
        # 개선 전략별 프롬프트 생성
        strategy_prompts = {
            "synonym_expansion": "동의어와 유사 표현을 활용해 검색 범위를 확장하세요.",
            "category_broadening": "상위 카테고리나 관련 카테고리로 검색 범위를 넓히세요.",
            "market_research": "시장 인기 상품과 트렌드를 반영한 현재 소비자 선호에 맞는 키워드로 조정하세요.",
            "demographic_adaptation": "받는 사람의 나이, 성별, 관심사에 더 특화된 키워드로 조정하세요.",
            "budget_alternative": "예산 범위에 맞는 대안 상품 키워드로 완전히 전환하세요."
        }
        
        prompt = f"""네이버쇼핑 검색 최적화 전문가로서, 선물 추천 검색 쿼리를 개선해주세요.

**현재 상황:**
- 시도 횟수: {attempt_number}/{MAX_RETRY_ATTEMPTS}
- 개선 전략: {strategy}
- 원본 키워드: {original_keywords}
- 실패한 키워드들: {failed_keywords}

**받는 사람 정보:**
- 나이: {gift_context.get('recipient_age', 'unknown')}세
- 성별: {gift_context.get('recipient_gender', 'unknown')}
- 관심사: {gift_context.get('interests', [])}
- 예산: ${gift_context.get('budget_min', 0)}-${gift_context.get('budget_max', 0)}

**개선 전략 지침:**
{strategy_prompts.get(strategy, '키워드를 최적화하세요.')}

**요구사항:**
1. 네이버쇼핑에서 실제 검색 가능한 상품명 키워드 생성
2. 3-5개의 핵심 키워드로 구성
3. 한글 키워드 사용 (필수)
4. 실패한 키워드 패턴 회피
5. 받는 사람 프로필에 최적화

다음 JSON 형식으로 응답해주세요:
{{
    "refined_keywords": ["키워드1", "키워드2", "키워드3"],
    "search_query": "키워드1 키워드2 키워드3",
    "reasoning": "개선 이유 설명",
    "expected_improvement": "개선 효과 예상"
}}"""

        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "당신은 네이버쇼핑 검색 최적화 전문가입니다. 실제 상품 검색에 효과적인 키워드를 생성하세요."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7,
                    response_format={"type": "json_object"}
                ),
                timeout=QUERY_REFINEMENT_TIMEOUT
            )
            
            result = json.loads(response.choices[0].message.content)
            refined_keywords = result.get("refined_keywords", original_keywords)
            search_query = result.get("search_query", " ".join(refined_keywords))
            
            logger.info(f"  🧠 AI refinement: {result.get('reasoning', 'No reasoning provided')}")
            
            return refined_keywords, search_query
            
        except Exception as e:
            logger.error(f"AI keyword refinement failed: {e}")
            # 폴백: 규칙 기반 키워드 개선
            return await self._fallback_keyword_refinement(original_keywords, strategy, attempt_number)
    
    async def _get_market_insights(
        self,
        keywords: List[str],
        gift_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """시장 조사 기반 인사이트 수집"""
        
        try:
            age = gift_context.get('recipient_age', '')
            gender = gift_context.get('recipient_gender', '')
            
            logger.info(f"📊 Market research starting for: {keywords}")
            
            # 단순한 규칙 기반 시장 인사이트 생성
            insights = await self._generate_market_insights(keywords, age, gender)
            
            logger.info(f"  ✅ Market insights collected: {len(insights.get('suggested_products', []))} products")
            return insights
            
        except Exception as e:
            logger.error(f"Market insights collection failed: {e}")
            return None
    
    async def _generate_market_insights(
        self,
        keywords: List[str],
        age: str,
        gender: str
    ) -> Dict[str, Any]:
        """규칙 기반 시장 인사이트 생성"""
        
        await asyncio.sleep(0.5)  # 시뮬레이션 지연
        
        # 나이대별 인기 상품 매핑
        age_based_products = {
            'teens': ['학용품', '게임', 'K-POP 굿즈', '스마트폰 액세서리'],
            'twenties': ['무선이어폰', '노트북', '커피', '패션악세서리'],
            'thirties': ['스마트워치', '화장품', '마사지기', '홍차'],
            'forties': ['건강식품', '골프용품', '고급차', '블루투스스피커'],
            'seniors': ['건강기능식품', '전통차', '산책용품', '마사지의자']
        }
        
        age_group = self._get_age_group(age)
        suggested_products = age_based_products.get(age_group, ['선물세트', '프리미엄상품'])
        
        # 성별별 키워드 조정
        trending_keywords = ['인기', '추천', '베스트']
        if gender == '여성':
            trending_keywords.extend(['예쁜', '감성적', '여성용'])
        elif gender == '남성':
            trending_keywords.extend(['실용적', '기능성', '남성용'])
        
        return {
            "suggested_products": suggested_products[:3],
            "trending_keywords": trending_keywords[:4],
            "price_trends": {
                "average_price": "₩75,000",
                "popular_range": "₩50,000-₩150,000"
            },
            "market_insights": f"{age_group} 연령대에서 인기 있는 상품 카테고리 중심"
        }
    
    def _get_age_group(self, age: str) -> str:
        """나이를 그룹으로 분류"""
        try:
            age_num = int(age) if age.isdigit() else 25
            if age_num < 20:
                return 'teens'
            elif age_num < 30:
                return 'twenties'
            elif age_num < 40:
                return 'thirties'
            elif age_num < 50:
                return 'forties'
            else:
                return 'seniors'
        except:
            return 'twenties'  # 기본값
    
    def _integrate_market_suggestions(
        self,
        current_keywords: List[str],
        market_insights: Dict[str, Any]
    ) -> List[str]:
        """시장 인사이트를 현재 키워드에 통합"""
        
        suggested_products = market_insights.get("suggested_products", [])
        trending_keywords = market_insights.get("trending_keywords", [])
        
        # 기존 키워드 + 시장 제안 + 트렌딩 키워드 조합
        integrated_keywords = current_keywords.copy()
        
        # 가장 관련성 높은 제안 상품 1-2개 추가
        for product in suggested_products[:2]:
            if product not in integrated_keywords:
                integrated_keywords.append(product)
        
        # 트렌딩 키워드 1개 추가
        for keyword in trending_keywords[:1]:
            if keyword not in integrated_keywords and len(integrated_keywords) < 5:
                integrated_keywords.append(keyword)
        
        # 최대 5개 키워드로 제한
        return integrated_keywords[:5]
    
    async def _simulate_keyword_refinement(
        self,
        original_keywords: List[str],
        strategy: str,
        attempt_number: int
    ) -> Tuple[List[str], str]:
        """시뮬레이션 모드에서의 키워드 개선"""
        
        await asyncio.sleep(0.5)  # AI 처리 시뮬레이션
        
        # 전략별 시뮬레이션 키워드 변환
        strategy_transforms = {
            "synonym_expansion": lambda kw: [f"{kw}+확장", "무선", "프리미엄"],
            "category_broadening": lambda kw: [f"{kw}+카테고리", "생활용품", "액세서리"],
            "market_research": lambda kw: [f"{kw}+인기", "트렌드", "추천"],
            "demographic_adaptation": lambda kw: [f"{kw}+맞춤", "개인화", "선물"],
            "budget_alternative": lambda kw: [f"{kw}+대안", "합리적", "가성비"]
        }
        
        base_keyword = original_keywords[0] if original_keywords else "선물"
        transform_func = strategy_transforms.get(strategy, lambda kw: [kw])
        
        refined_keywords = transform_func(base_keyword)
        search_query = " ".join(refined_keywords)
        
        return refined_keywords, search_query
    
    async def _fallback_keyword_refinement(
        self,
        original_keywords: List[str],
        strategy: str,
        attempt_number: int
    ) -> Tuple[List[str], str]:
        """AI 실패 시 규칙 기반 폴백 키워드 개선"""
        
        # 간단한 규칙 기반 개선
        base_keywords = original_keywords.copy()
        
        # 시도 횟수에 따른 키워드 수정
        modifiers = ["프리미엄", "인기", "추천", "베스트", "신상"]
        modifier = modifiers[min(attempt_number - 1, len(modifiers) - 1)]
        
        refined_keywords = [modifier] + base_keywords[:3]
        search_query = " ".join(refined_keywords)
        
        return refined_keywords, search_query
    
    def _log_session_summary(self, session: QueryRefinementSession):
        """세션 요약 로깅"""
        
        logger.info(f"📊 Query Refinement Session Summary ({session.session_id})")
        logger.info(f"  → Total attempts: {len(session.attempts)}")
        logger.info(f"  → Final success: {session.final_success}")
        logger.info(f"  → Total products found: {session.total_products_found}")
        logger.info(f"  → Total processing time: {session.total_processing_time:.2f}s")
        
        if session.best_attempt:
            best = session.best_attempt
            logger.info(f"  → Best attempt: #{best.attempt_number} ({best.refinement_strategy})")
            logger.info(f"    - Keywords: {best.refined_keywords}")
            logger.info(f"    - Products: {best.products_found}")
            logger.info(f"    - Time: {best.processing_time:.2f}s")
        
        # 실패한 전략들 로깅
        failed_strategies = [a.refinement_strategy for a in session.attempts if not a.success]
        if failed_strategies:
            logger.info(f"  → Failed strategies: {failed_strategies}")