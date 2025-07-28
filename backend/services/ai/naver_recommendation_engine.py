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
    ai_recommendation_index: Optional[int] = None  # AI 추천과의 매칭 인덱스
    search_method: Optional[str] = None  # 검색에 사용된 정렬 방식 (sim, asc, dsc)
    quality_score: Optional[float] = None  # 상품 품질 점수 (0.0 - 1.0)


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
    
    async def search_products_multi_sort(self, keywords: List[str], budget_max_krw: int, 
                            display: int = 30) -> List[NaverProductResult]:
        """다중 정렬 방식을 활용한 고품질 상품 검색"""
        if not self.enabled:
            return await self._simulate_search(keywords, budget_max_krw, display)
        
        logger.info(f"🔄 Multi-sort search starting for keywords: {keywords}")
        
        all_products = []
        sort_methods = ["sim", "asc", "dsc"]  # 정확도 → 가격낮은순 → 가격높은순
        
        for sort_method in sort_methods:
            try:
                # 각 정렬 방식으로 더 적은 개수씩 검색 (총합이 display가 되도록)
                search_count = display // len(sort_methods) + (1 if sort_method == "sim" else 0)
                
                products = await self.search_products(keywords, budget_max_krw, search_count, sort_method)
                
                logger.info(f"  → {sort_method} 정렬: {len(products)}개 상품 발견")
                
                # 각 상품에 검색 방식 정보 추가
                for product in products:
                    product.search_method = sort_method
                    all_products.append(product)
                    
            except Exception as e:
                logger.warning(f"  → {sort_method} 정렬 검색 실패: {e}")
                continue
        
        # 강화된 중복 제거 시스템 (productId + 유사 상품명 기준)
        unique_products = []
        seen_product_ids = set()
        seen_product_signatures = set()  # 유사한 상품명 탐지용
        
        for product in all_products:
            # 1차: productId 기준 중복 제거
            if product.productId in seen_product_ids:
                continue
            
            # 2차: 유사한 상품명 기준 중복 제거
            product_signature = self._create_product_signature(product)
            if product_signature in seen_product_signatures:
                continue
            
            # 3차: 동일 브랜드+카테고리에서 너무 많은 상품 방지 (다양성 확보)
            brand_category_key = f"{product.brand}_{product.category3}"
            brand_category_count = sum(1 for p in unique_products 
                                     if f"{p.brand}_{p.category3}" == brand_category_key)
            if brand_category_count >= 3:  # 동일 브랜드+카테고리 최대 3개
                continue
            
            unique_products.append(product)
            seen_product_ids.add(product.productId)
            seen_product_signatures.add(product_signature)
        
        logger.info(f"🎯 Multi-sort 결과: 총 {len(all_products)}개 → 중복 제거 후 {len(unique_products)}개")
        
        # 품질 스코어 계산 및 상품 품질 기반 정렬
        logger.info("📊 상품 품질 스코어 계산 중...")
        
        quality_scored_products = []
        for product in unique_products:
            # 품질 스코어 계산
            quality_score = self.calculate_product_quality_score(product)
            product.quality_score = quality_score
            
            # 검색 방식 보너스 적용 (sim이 더 정확하므로 보너스)
            if getattr(product, 'search_method', 'sim') == 'sim':
                product.quality_score += 0.1  # sim 검색 보너스
            
            quality_scored_products.append(product)
        
        # 품질 스코어 기준으로 내림차순 정렬
        quality_scored_products.sort(key=lambda p: p.quality_score, reverse=True)
        
        # 품질 스코어 로깅 (상위 5개)
        for i, product in enumerate(quality_scored_products[:5]):
            logger.info(f"  #{i+1}: {product.title[:40]}... - 품질점수: {product.quality_score:.2f} ({product.search_method})")
        
        return quality_scored_products

    async def search_products(self, keywords: List[str], budget_max_krw: int, 
                            display: int = 10, sort: str = "asc") -> List[NaverProductResult]:
        """상품 검색 (최대 예산만 사용)"""
        
        if not self.enabled:
            return await self._simulate_search(keywords, budget_max_krw, display)
        
        try:
            # Build optimized search query
            query = self._optimize_search_query(keywords)
            logger.info(f"🔍 Naver API 검색 시작")
            logger.info(f"  - 검색 쿼리: '{query}'")
            logger.info(f"  - 원본 키워드: {keywords}")
            logger.info(f"  - 예산 범위: 최대 ₩{budget_max_krw:,}")
            logger.info(f"  - 표시 개수: {display}개")
            logger.info(f"  - 정렬 방식: {sort}")
            
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
            
            # Build complete request URL for logging
            import urllib.parse
            url_params = urllib.parse.urlencode(params)
            full_request_url = f"{self.base_url}?{url_params}"
            logger.info(f"🌐 Naver API 요청 URL: {full_request_url}")
            
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
                        logger.info(f"✅ Naver API 응답 성공: {len(data.get('items', []))}개 원시 상품 데이터")
                        results = self._process_search_results(data, budget_max_krw)
                        logger.info(f"📊 필터링 결과: {len(results)}개 예산 내 상품 (쿼리: '{query}')")
                        return results
                    else:
                        logger.warning(f"❌ Naver Shopping API 오류: HTTP {response.status} (쿼리: '{query}')")
                        return await self._simulate_search(keywords, budget_max_krw, display)
                        
        except Exception as e:
            logger.error(f"❌ Naver Shopping API 실패: {e} (쿼리: '{query if 'query' in locals() else keywords}')")
            return await self._simulate_search(keywords, budget_max_krw, display)
    
    def _process_search_results(self, data: Dict[str, Any], budget_max_krw: int) -> List[NaverProductResult]:
        """네이버쇼핑 검색 결과 처리 (품질 필터링 강화)"""
        results = []
        items = data.get("items", [])
        
        # 개선된 예산 범위 설정 - 현실적인 최소 가격 적용
        # 예산의 1/3을 최소가로 설정하여 더 넓은 가격 범위 확보
        budget_min_krw = max(10000, budget_max_krw // 3)  # 예산의 1/3, 최소 10,000원
        logger.info(f"Budget filter: {budget_min_krw:,}원 - {budget_max_krw:,}원")
        
        if items:
            logger.info(f"Sample API response item: {items[0]}")
        
        filtered_count = 0
        quality_filtered = 0
        for item in items:
            try:
                # 가격 필터링
                lprice_str = item.get("lprice", "0")
                if not lprice_str or lprice_str == "":
                    logger.warning(f"Product '{item.get('title', 'Unknown')}' has no price, skipping")
                    continue
                
                try:
                    lprice = int(lprice_str)
                except ValueError:
                    logger.warning(f"Invalid price format '{lprice_str}' for product '{item.get('title', 'Unknown')}'")
                    continue
                
                # 예산 범위 체크 (최소/최대 예산 모두 확인)
                if lprice < budget_min_krw or lprice > budget_max_krw:
                    filtered_count += 1
                    continue
                
                # 품질 필터링 - 부적절한 상품 제외
                title = self._clean_html_tags(item.get("title", ""))
                if self._is_low_quality_product(title):
                    quality_filtered += 1
                    logger.info(f"Quality filter: Excluding '{title[:50]}...' - low quality product")
                    continue
                
                # 제목은 이미 위에서 처리됨
                
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
        
        logger.info(f"Filtering results: {filtered_count} products outside budget, {quality_filtered} low-quality products, {len(results)} valid products")
        return results
    
    def _clean_html_tags(self, text: str) -> str:
        """HTML 태그 제거"""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    def _is_low_quality_product(self, title: str) -> bool:
        """저품질/부적절한 상품 필터링"""
        title_lower = title.lower()
        
        # 견적서, 주문제작, 문의 상품 제외
        exclude_keywords = [
            "견적서", "견적", "문의", "상담", "주문제작", "맞춤제작", "커스텀",
            "배송비", "추가비", "도선료", "제주", "택배비", "결제상품", 
            "참고용", "샘플", "테스트", "더미", "예시"
        ]
        
        for keyword in exclude_keywords:
            if keyword in title_lower:
                return True
        
        # 제목이 너무 짧거나 의미없는 경우
        if len(title.strip()) < 5:
            return True
            
        # 괄호 안에 문의사항이 있는 경우
        if "고객센터" in title or "문의바랍니다" in title:
            return True
            
        return False
    
    def _optimize_search_query(self, keywords: List[str]) -> str:
        """검색 키워드 최적화 - 가장 효과적인 검색어 조합 생성"""
        if not keywords:
            return "선물"
        
        # 핵심 제품명 우선순위 설정
        priority_keywords = []
        modifier_keywords = []
        
        for keyword in keywords:
            keyword_clean = keyword.lower().strip()
            
            # 핵심 제품명 (높은 우선순위) - 확장된 키워드 리스트
            if keyword_clean in ["카메라", "이어폰", "스피커", "노트북", "시계", "가방", "지갑", 
                               "향수", "책", "컵", "램프", "차", "와인", "초콜릿",
                               # 추가된 우선순위 키워드들
                               "주방용품", "게임", "운동용품", "헬스", "트래커", "콘솔",
                               "선물세트", "세트", "전자기기", "액세서리", "생활용품",
                               "키친용품", "게임기", "피트니스", "건강용품", "스마트"]:
                priority_keywords.append(keyword_clean)
            
            # 수식어/형용사 (낮은 우선순위) - 확장된 리스트
            elif keyword_clean in ["프리미엄", "고급", "스마트", "무선", "디지털", "맞춤형",
                                "최신", "전문가용", "초보자용", "휴대용", "가정용", "비즈니스용"]:
                modifier_keywords.append(keyword_clean)
            
            # 일반 키워드
            elif len(keyword_clean) >= 2:
                priority_keywords.append(keyword_clean)
        
        # 검색어 조합 전략 - 네이버 쇼핑 최적화
        # 단일 핵심 키워드 우선 사용 (네이버 쇼핑에서 잘 검색되는 패턴)
        naver_optimized_patterns = {
            "주방용품": ["주방용품", "키친용품", "주방 세트"],
            "게임": ["게임기", "콘솔", "닌텐도", "플레이스테이션"],
            "운동": ["운동용품", "헬스용품", "피트니스"],
            "커피": ["커피메이커", "원두", "커피머신"],
            "이어폰": ["이어폰", "헤드폰", "무선이어폰", "블루투스"],
            "노트북": ["노트북", "컴퓨터", "랩탑"],
            "시계": ["시계", "손목시계", "스마트워치"]
        }
        
        if priority_keywords:
            # 핵심 제품명에 대한 네이버 최적화 검색어 사용
            main_key = priority_keywords[0]
            if main_key in naver_optimized_patterns:
                # 가장 효과적인 검색어 선택 (첫 번째)
                return naver_optimized_patterns[main_key][0]
            else:
                # 단일 키워드 사용
                return main_key
        else:
            # 핵심 제품명이 없으면 수식어 중 1개만 사용
            return modifier_keywords[0] if modifier_keywords else "선물"
    
    async def _simulate_search(self, keywords: List[str], budget_max_krw: int, display: int) -> List[NaverProductResult]:
        """시뮬레이션 모드"""
        await asyncio.sleep(0.8)
        
        # 키워드 기반 가상 상품 생성
        keyword = keywords[0] if keywords else "선물"
        
        sample_products = []
        # 최대 예산 내에서 다양한 가격 생성 (0원부터 최대까지)
        for i in range(min(display, 5)):
            # 0원부터 최대 예산까지 다양한 가격 생성
            price = (budget_max_krw * (i + 1) // (display + 1))
            
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
    
    def calculate_product_quality_score(self, product: NaverProductResult) -> float:
        """상품 품질 점수 계산 (0.0 - 1.0)"""
        score = 0.0
        
        # 1. 브랜드 신뢰도 (0.4 가중치)
        brand_score = self._calculate_brand_trust_score(product.brand)
        score += brand_score * 0.4
        
        # 2. 쇼핑몰 신뢰도 (0.3 가중치)
        mall_score = self._calculate_mall_trust_score(product.mallName)
        score += mall_score * 0.3
        
        # 3. 상품명 품질 (0.2 가중치)
        title_score = self._calculate_title_quality_score(product.title)
        score += title_score * 0.2
        
        # 4. 가격 적정성 (0.1 가중치)
        price_score = self._calculate_price_reasonableness_score(product)
        score += price_score * 0.1
        
        return min(1.0, max(0.0, score))  # 0.0 - 1.0 범위로 제한
    
    def _calculate_brand_trust_score(self, brand: str) -> float:
        """브랜드 신뢰도 점수 계산"""
        if not brand or brand.strip() == "":
            return 0.3  # 브랜드 정보 없음
        
        brand_lower = brand.lower().strip()
        
        # 최고급 브랜드 (1.0)
        premium_brands = {
            # 전자제품
            "삼성", "samsung", "lg", "애플", "apple", "소니", "sony", "필립스", "philips",
            "다이슨", "dyson", "보세", "bose", "하만카돈", "harman kardon", "마셜", "marshall",
            # 패션/라이프스타일  
            "나이키", "nike", "아디다스", "adidas", "유니클로", "uniqlo", "코치", "coach",
            "랄프로렌", "ralph lauren", "휴고보스", "hugo boss", "캘빈클라인", "calvin klein",
            # 뷰티/생활용품
            "아모레퍼시픽", "설화수", "헤라", "hera", "랑콤", "lancome", "에스티로더", "estee lauder",
            # 주방용품
            "쿠진아트", "cuisinart", "브라운", "braun", "테팔", "tefal", "피스카르스", "fiskars"
        }
        
        # 신뢰브랜드 (0.8)
        trusted_brands = {
            "코웨이", "coway", "위닉스", "winix", "청호나이스", "sk매직", "대웅제약", "동화약품",
            "아시아나", "대한항공", "현대", "hyundai", "기아", "kia", "롯데", "lotte", "신세계"
        }
        
        # 일반브랜드 (0.6)
        known_brands = {
            "무인양품", "muji", "이케아", "ikea", "다이소", "올리브영", "gs25", "세븐일레븐",
            "미니스톱", "cu", "스타벅스", "starbucks", "맥도날드", "mcdonalds", "kfc"
        }
        
        # 브랜드 매칭 확인
        for brand_name in premium_brands:
            if brand_name in brand_lower:
                return 1.0
                
        for brand_name in trusted_brands:
            if brand_name in brand_lower:
                return 0.8
                
        for brand_name in known_brands:
            if brand_name in brand_lower:
                return 0.6
        
        # 한글/영문 브랜드명이 있으면 일반 점수
        if any(c.isalpha() for c in brand):
            return 0.5
        
        return 0.3  # 알 수 없는 브랜드
    
    def _calculate_mall_trust_score(self, mall_name: str) -> float:
        """쇼핑몰 신뢰도 점수 계산"""
        if not mall_name or mall_name.strip() == "":
            return 0.3
        
        mall_lower = mall_name.lower().strip()
        
        # 최고 신뢰 쇼핑몰 (1.0)
        premium_malls = {
            "네이버쇼핑", "naver", "쿠팡", "coupang", "11번가", "11st", "gmarket", "지마켓",
            "옥션", "auction", "인터파크", "interpark", "롯데온", "lotteon", "하이마트", "himart",
            "이마트", "emart", "홈플러스", "homeplus", "코스트코", "costco"
        }
        
        # 신뢰 쇼핑몰 (0.8)
        trusted_malls = {
            "올리브영", "oliveyoung", "gs shop", "cj온스타일", "ns홈쇼핑", "현대홈쇼핑",
            "롯데홈쇼핑", "아이허브", "iherb", "무신사", "musinsa", "29cm", "브랜디", "brandi"
        }
        
        # 일반 쇼핑몰 (0.6)
        known_malls = {
            "티몬", "tmon", "위메프", "wemakeprice", "스타일쉐어", "stylenanda", "코코", "coco",
            "도매킹", "마켓비", "marketb", "공영쇼핑", "디앤샵", "dnshop", "에이블리", "ably"
        }
        
        # 쇼핑몰 매칭 확인
        for mall in premium_malls:
            if mall in mall_lower:
                return 1.0
                
        for mall in trusted_malls:
            if mall in mall_lower:
                return 0.8
                
        for mall in known_malls:
            if mall in mall_lower:
                return 0.6
        
        # 기타 쇼핑몰
        return 0.4
    
    def _calculate_title_quality_score(self, title: str) -> float:
        """상품명 품질 점수 계산"""
        if not title or len(title.strip()) < 5:
            return 0.1
        
        score = 0.5  # 기본 점수
        title_clean = title.strip()
        
        # 긍정적 요소들
        positive_indicators = [
            ("정품", 0.2), ("공식", 0.15), ("무료배송", 0.1), ("당일배송", 0.1),
            ("리뷰", 0.05), ("평점", 0.05), ("베스트", 0.1), ("인기", 0.1),
            ("프리미엄", 0.05), ("고급", 0.05), ("브랜드", 0.05)
        ]
        
        for indicator, boost in positive_indicators:
            if indicator in title_clean:
                score += boost
        
        # 부정적 요소들
        negative_indicators = [
            ("중고", -0.3), ("리퍼", -0.2), ("파손", -0.4), ("불량", -0.4),
            ("반품", -0.2), ("교환불가", -0.2), ("AS불가", -0.2), ("미개봉", -0.1),
            ("견적", -0.3), ("문의", -0.2), ("상담", -0.2), ("주문제작", -0.1)
        ]
        
        for indicator, penalty in negative_indicators:
            if indicator in title_clean:
                score += penalty
        
        # 제목 길이 적정성 (너무 짧거나 너무 길면 감점)
        length = len(title_clean)
        if length < 10:
            score -= 0.2
        elif length > 100:
            score -= 0.1
        elif 20 <= length <= 60:  # 적정 길이
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _calculate_price_reasonableness_score(self, product: NaverProductResult) -> float:
        """가격 적정성 점수 계산"""
        # 기본적으로 가격이 있으면 0.5점
        if product.lprice <= 0:
            return 0.0
        
        # 가격대별 적정성 평가
        price = product.lprice
        
        if price < 5000:  # 너무 저렴하면 의심스러움
            return 0.3
        elif 5000 <= price <= 10000:  # 저가 적정
            return 0.6
        elif 10000 <= price <= 100000:  # 중가 적정
            return 0.8
        elif 100000 <= price <= 500000:  # 고가 적정
            return 0.9
        elif 500000 <= price <= 1000000:  # 프리미엄 적정
            return 0.7
        else:  # 너무 비싸면 선호도 낮음
            return 0.5
    
    def _create_product_signature(self, product: NaverProductResult) -> str:
        """상품의 고유 시그니처 생성 (유사 상품 탐지용)"""
        title = product.title.lower()
        
        # HTML 태그 제거
        import re
        title_clean = re.sub(r'<[^>]+>', '', title)
        
        # 특수문자 제거 및 정규화
        title_clean = re.sub(r'[^\w\s가-힣]', ' ', title_clean)
        title_clean = re.sub(r'\s+', ' ', title_clean).strip()
        
        # 핵심 키워드 추출 (브랜드명, 제품명, 모델명 등)
        words = title_clean.split()
        
        # 불용어 제거
        stop_words = {
            '정품', '공식', '무료배송', '당일배송', '특가', '할인', '세일', 'sale',
            '추천', '인기', '베스트', '신상', '최신', '한정', '스페셜',
            '블랙', '화이트', '레드', '블루', '그린', '옐로우', '핑크', '그레이',
            '대형', '중형', '소형', '미니', '라지', 'xs', 's', 'm', 'l', 'xl', 'xxl',
            '개', '구', '매', '입', '장', '개월', '년', '일', '시간'
        }
        
        # 핵심 단어만 추출 (3글자 이상, 불용어 제외)
        core_words = []
        for word in words:
            if len(word) >= 3 and word not in stop_words:
                core_words.append(word)
        
        # 상위 5개 핵심 단어로 시그니처 생성
        signature_words = sorted(core_words[:5])
        signature = '_'.join(signature_words)
        
        # 브랜드 정보도 포함
        if product.brand and len(product.brand.strip()) > 0:
            brand_clean = re.sub(r'[^\w가-힣]', '', product.brand.lower())
            signature = f"{brand_clean}_{signature}"
        
        return signature


class NaverGiftRecommendationEngine:
    """네이버쇼핑 API 기반 통합 추천 엔진 - FastAPI 백엔드용"""
    
    def __init__(self, openai_api_key: str, naver_client_id: str = "", naver_client_secret: str = ""):
        from services.ai.recommendation_engine import GiftRecommendationEngine
        
        self.ai_engine = GiftRecommendationEngine(openai_api_key)
        self.naver_client = NaverShoppingClient(naver_client_id, naver_client_secret)
        self.naver_enabled = self.naver_client.enabled
    
    async def generate_naver_recommendations(self, request):
        """
        네이버쇼핑 API 기반 추천 생성 (FastAPI 백엔드용) - 개선된 매칭 알고리즘
        
        Args:
            request: GiftRequest 모델 인스턴스
            
        Returns:
            EnhancedRecommendationResponse와 호환되는 구조
        """
        start_time = datetime.now()
        request_id = f"naver_req_{int(start_time.timestamp())}"
        
        try:
            print(f"🔥 DEBUG: Starting Naver Shopping recommendation for {request_id}")
            logger.info(f"Starting Naver Shopping recommendation for {request_id}")
            
            # Stage 1: AI 기본 추천 생성
            ai_start = time.time()
            
            # Check if OpenAI API key is available
            import os
            openai_key = os.getenv("OPENAI_API_KEY", "")
            print(f"🔥 DEBUG: OpenAI API key check: key='{openai_key}', length={len(openai_key)}, bool={bool(openai_key)}")
            logger.info(f"OpenAI API key check: key='{openai_key}', length={len(openai_key)}, bool={bool(openai_key)}")
            
            if not openai_key:
                print(f"🔥 DEBUG: Using fallback recommendations - no OpenAI API key")
                logger.info("OpenAI API key not configured, using fallback recommendations directly")
                ai_response = await self._create_fallback_ai_recommendations(request)
                ai_time = time.time() - ai_start
            else:
                print(f"🔥 DEBUG: Using OpenAI API with key")
                ai_response = await self.ai_engine.generate_recommendations(request)
                ai_time = time.time() - ai_start
                
                # If AI generation fails (e.g., invalid API key), create fallback recommendations
                if not ai_response.success:
                    logger.warning(f"AI generation failed: {ai_response.error_message}")
                    logger.info("Creating fallback recommendations based on user interests")
                    ai_response = await self._create_fallback_ai_recommendations(request)
                    ai_time = time.time() - ai_start
                    logger.info(f"Fallback AI recommendations created successfully: {len(ai_response.recommendations)} recommendations")
            
            # Stage 2: AI 추천별 개별 네이버쇼핑 검색
            all_naver_products = []
            naver_time = 0
            naver_start = time.time()
            
            # Use KRW budget directly for Naver Shopping (Korean marketplace)
            if request.currency == "KRW":
                budget_max_krw = request.budget_max
            else:
                # Convert USD to KRW for Naver Shopping
                budget_max_krw = request.budget_max * USD_TO_KRW_RATE
            
            # AI 추천별로 개별 검색 수행
            for i, ai_rec in enumerate(ai_response.recommendations[:3]):
                # AI 추천에서 검색 키워드 추출
                search_keywords = self._extract_search_keywords_from_ai_rec(ai_rec, request)
                
                logger.info(f"🎁 AI 추천 {i+1}: '{ai_rec.title}' (카테고리: {ai_rec.category})")
                logger.info(f"  → 추출된 검색 키워드: {search_keywords}")
                
                # 각 AI 추천에 대해 다중 정렬 네이버 검색 수행 (더 많은 결과)
                products = await self.naver_client.search_products_multi_sort(
                    search_keywords, budget_max_krw, display=35  # 강화된 다중 정렬로 최대한 다양한 결과
                )
                
                logger.info(f"  → 발견된 상품: {len(products)}개 (AI 추천 {i+1} 용)")
                if products:
                    price_range = f"₩{min(p.lprice for p in products):,} - ₩{max(p.lprice for p in products):,}"
                    logger.info(f"  → 가격 범위: {price_range}")
                
                # AI 추천과 연결해서 저장
                for product in products:
                    product.ai_recommendation_index = i
                    all_naver_products.append(product)
            
            naver_time = time.time() - naver_start
            logger.info(f"📊 전체 검색 결과: {len(all_naver_products)}개 상품 ({naver_time:.2f}초 소요)")
            logger.info(f"  → 네이버 API 호출 횟수: {self.naver_client.api_calls_count}번")
            
            # Debug: Log product details
            for i, product in enumerate(all_naver_products):
                logger.info(f"  Product {i+1}: {product.title[:50]}... - ₩{product.lprice:,} (AI rec #{product.ai_recommendation_index})")
                logger.info(f"    Image: {product.image}")
                logger.info(f"    Link: {product.link}")
            
            # Stage 3: 스마트 매칭 통합
            integration_start = time.time()
            enhanced_recommendations = await self._smart_integrate_recommendations(
                ai_response.recommendations, all_naver_products, request
            )
            integration_time = time.time() - integration_start
            
            # 네이버 상품을 ProductSearchResult로 변환
            search_results = self._convert_naver_to_search_results(all_naver_products)
            
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
                search_results_count=len(all_naver_products),
                product_details_count=len(all_naver_products),
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
    
    def _get_enhanced_keyword_mapping(self) -> Dict[str, List[str]]:
        """대폭 확장된 스마트 키워드 매핑 시스템"""
        return {
            # === 전자제품 (확장) ===
            "커피": ["커피메이커", "원두", "커피머신", "드립커피", "에스프레소", "모카포트", "핸드드립"],
            "메이커": ["커피메이커", "제조기", "머신"],
            "이어폰": ["이어폰", "헤드폰", "무선이어폰", "블루투스이어폰", "에어팟", "헤드셋", "이어버드"],
            "헤드폰": ["헤드폰", "이어폰", "무선헤드폰", "오버이어", "온이어", "헤드셋"],
            "무선": ["무선이어폰", "블루투스", "와이어리스", "wireless"],
            "스피커": ["스피커", "블루투스스피커", "무선스피커", "사운드바", "오디오", "음향기기"],
            "블루투스": ["블루투스", "무선", "wireless", "bluetooth"],
            "노트북": ["노트북", "컴퓨터", "랩탑", "laptop", "PC", "맥북"],
            "컴퓨터": ["컴퓨터", "노트북", "데스크탑", "PC", "맥", "mac"],
            "태블릿": ["태블릿", "아이패드", "갤럭시탭", "패드", "태블릿PC"],
            "카메라": ["카메라", "디지털카메라", "DSLR", "미러리스", "캠코더", "액션캠"],
            "모니터": ["모니터", "디스플레이", "LCD", "LED", "화면", "스크린"],
            "스마트폰": ["스마트폰", "핸드폰", "아이폰", "갤럭시", "휴대폰", "폰"],
            
            # === 게임/엔터테인먼트 (확장) ===
            "게임": ["게임기", "콘솔", "게임", "플레이스테이션", "닌텐도", "xbox", "게임패드"],
            "콘솔": ["게임기", "콘솔", "플레이스테이션", "닌텐도", "xbox"],
            "닌텐도": ["닌텐도", "게임기", "스위치", "switch", "nintendo"],
            "플레이스테이션": ["플레이스테이션", "콘솔", "PS5", "PS4", "playstation"],
            "최신": ["게임기", "전자제품", "신제품", "최신형"],
            
            # === 홈&리빙 (대폭 확장) ===
            "향수": ["향수", "퍼퓸", "fragrance", "perfume", "디퓨저", "방향제"],
            "캔들": ["캔들", "양초", "향초", "아로마캔들", "캔들홀더"],
            "머그컵": ["머그컵", "컵", "머그", "텀블러", "커피컵"],
            "컵": ["머그컵", "컵", "텀블러", "글라스", "잔", "티컵"],
            "담요": ["담요", "블랭킷", "이불", "덮개", "throw"],
            "쿠션": ["쿠션", "방석", "베개", "pillow", "cushion"],
            "램프": ["램프", "조명", "등", "전등", "스탠드", "무드등"],
            "조명": ["조명", "램프", "등", "전등", "라이트", "LED"],
            "주방용품": ["주방용품", "키친용품", "요리도구", "조리도구", "kitchen"],
            "키친": ["키친용품", "주방용품", "kitchen", "요리용품"],
            "프리미엄": ["주방용품", "고급용품", "프리미엄", "럭셔리", "최고급"],
            "주방": ["주방용품", "키친용품", "요리용품", "조리용품"],
            "인테리어": ["인테리어소품", "장식품", "데코", "홈데코", "소품"],
            "식물": ["화분", "식물", "그린테리어", "공기정화식물", "다육식물"],
            
            # === 도서/문구 (확장) ===
            "책": ["도서", "책", "서적", "book", "읽을거리"],
            "도서": ["도서", "책", "서적", "북", "읽을거리"],
            "노트": ["노트", "다이어리", "필기구", "수첩", "메모장"],
            "다이어리": ["다이어리", "노트", "플래너", "스케줄러", "일정관리"],
            "펜": ["펜", "볼펜", "필기구", "문구", "만년필"],
            "만년필": ["만년필", "펜", "고급펜", "필기구"],
            "문구": ["문구", "필기구", "사무용품", "펜", "노트"],
            
            # === 패션/액세서리 (확장) ===
            "지갑": ["지갑", "반지갑", "장지갑", "카드지갑", "wallet"],
            "가방": ["가방", "백팩", "핸드백", "토트백", "크로스백", "숄더백"],
            "백팩": ["백팩", "가방", "배낭", "backpack", "등가방"],
            "시계": ["시계", "손목시계", "스마트워치", "워치", "watch"],
            "스마트워치": ["스마트워치", "시계", "워치", "갤럭시워치", "애플워치"],
            "반지": ["반지", "링", "ring", "커플링", "약혼반지"],
            "목걸이": ["목걸이", "네클리스", "펜던트", "necklace", "체인"],
            "귀걸이": ["귀걸이", "이어링", "earring", "피어싱"],
            "팔찌": ["팔찌", "브레이슬릿", "밴드", "bracelet"],
            "선글라스": ["선글라스", "썬글라스", "안경", "sunglass"],
            
            # === 건강/피트니스 (대폭 확장) ===
            "운동": ["운동용품", "헬스", "피트니스", "스포츠", "트레이닝"],
            "요가": ["요가매트", "요가", "필라테스", "스트레칭", "yoga"],
            "덤벨": ["덤벨", "웨이트", "바벨", "운동기구", "근력운동"],
            "매트": ["요가매트", "운동매트", "매트", "바닥재"],
            "운동용품": ["운동용품", "헬스용품", "피트니스용품", "스포츠용품"],
            "헬스": ["헬스용품", "운동용품", "피트니스", "gym"],
            "트래커": ["스마트워치", "피트니스트래커", "활동량계", "밴드"],
            "피트니스": ["피트니스용품", "운동용품", "헬스", "fitness"],
            "스마트": ["스마트워치", "스마트제품", "IoT", "스마트홈"],
            "러닝": ["러닝화", "조깅", "운동화", "running"],
            "수영": ["수영복", "수영용품", "물안경", "swimming"],
            
            # === 식품/음료 (확장) ===
            "차": ["차", "티", "허브티", "tea", "홍차", "녹차"],
            "티": ["티", "차", "tea", "허브티", "건강차"],
            "원두": ["원두", "커피원두", "원두커피", "coffee"],
            "와인": ["와인", "포도주", "wine", "레드와인", "화이트와인"],
            "초콜릿": ["초콜릿", "달콤한", "chocolate", "카카오", "디저트"],
            "건강식품": ["건강식품", "영양제", "비타민", "보충제", "건강보조식품"],
            
            # === 뷰티/케어 (신규 추가) ===
            "향수": ["향수", "퍼퓸", "fragrance", "perfume", "디퓨저"],
            "화장품": ["화장품", "코스메틱", "메이크업", "스킨케어", "cosmetic"],
            "스킨케어": ["스킨케어", "화장품", "기초화장품", "로션", "크림"],
            "마스크": ["마스크팩", "페이스마스크", "시트마스크", "팩"],
            
            # === 자동차/교통 (신규 추가) ===
            "자동차": ["자동차용품", "차량용품", "카악세서리", "자동차"],
            "차량": ["차량용품", "자동차용품", "카악세서리"],
            
            # === 여행/레저 (신규 추가) ===
            "여행": ["여행용품", "캐리어", "여행가방", "travel"],
            "캐리어": ["캐리어", "여행가방", "trolley", "여행용품"],
            "텐트": ["텐트", "캠핑용품", "camping", "아웃도어"],
            "캠핑": ["캠핑용품", "아웃도어", "camping", "등산용품"],
            
            # === 육아/완구 (신규 추가) ===
            "아기": ["유아용품", "베이비", "아기용품", "baby"],
            "완구": ["장난감", "토이", "toy", "어린이용품"],
            
            # === 기타 확장 ===
            "선물": ["선물세트", "기프트", "gift", "present", "기념품"],
            "세트": ["선물세트", "세트", "set", "패키지"],
            "전자기기": ["전자제품", "디지털", "전자", "기기"],
            "액세서리": ["액세서리", "소품", "accessory", "장신구"],
            "생활용품": ["생활용품", "일용품", "household", "라이프스타일"],
            "프리미엄": ["프리미엄", "고급", "럭셔리", "최고급", "premium"],
            "고급": ["고급", "프리미엄", "럭셔리", "상급", "premium"],
            "브랜드": ["브랜드", "명품", "정품", "brand"],
            "정품": ["정품", "브랜드", "공식", "오리지널"],
            "한정": ["한정판", "리미티드", "스페셜", "limited"],
            "신상": ["신상품", "신제품", "최신", "new"]
        }

    def _extract_search_keywords_from_ai_rec(self, ai_recommendation, request) -> List[str]:
        """AI 추천에서 정확한 검색 키워드 추출 (상품명 기반)"""
        keywords = []
        
        # 1. AI 추천 제목에서 핵심 상품명 추출
        title_words = ai_recommendation.title.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
        
        # 대폭 확장된 스마트 키워드 매핑 시스템 사용
        product_keywords = self._get_enhanced_keyword_mapping()
        
        # 제목에서 매칭되는 상품 키워드 찾기
        for word in title_words:
            word_clean = word.lower().strip()
            if word_clean in product_keywords:
                keywords.extend(product_keywords[word_clean])
                logger.info(f"Found product keyword '{word_clean}' -> {product_keywords[word_clean]}")
            elif len(word_clean) >= 2 and word_clean not in ['및', '그리고', '또는', '위한']:
                keywords.append(word_clean)
        
        # 2. 카테고리 기반 키워드 추가
        if ai_recommendation.category:
            category_keywords = {
                "전자제품": ["전자기기", "디지털"],
                "홈&리빙": ["생활용품", "인테리어"], 
                "도서": ["책", "도서"],
                "패션": ["패션", "액세서리"],
                "식음료": ["식품", "음료"],
                "프리미엄 선물": ["선물세트", "고급"]
            }
            if ai_recommendation.category in category_keywords:
                keywords.extend(category_keywords[ai_recommendation.category])
        
        # 3. 중복 제거 및 우선순위 정렬
        unique_keywords = []
        seen = set()
        for keyword in keywords:
            if keyword not in seen and keyword:
                unique_keywords.append(keyword)
                seen.add(keyword)
        
        # 최대 4개 키워드 반환
        final_keywords = unique_keywords[:4] if unique_keywords else ["선물"]
        logger.info(f"🔍 AI 추천 '{ai_recommendation.title}' -> 최종 검색 키워드: {final_keywords}")
        return final_keywords
    
    async def _smart_integrate_recommendations(self, ai_recommendations: List, naver_products: List[NaverProductResult], request) -> List:
        """스마트 AI 추천과 네이버쇼핑 상품 통합 (GPT 기반 상품 검증 및 재선별)"""
        logger.info(f"🔄 Smart Integration starting - AI recs: {len(ai_recommendations)}, Naver products: {len(naver_products)}")
        
        if not ai_recommendations:
            logger.warning("No AI recommendations available, creating recommendations from Naver products")
            return await self._create_recommendations_from_products(naver_products[:3], request)
        
        enhanced_recommendations = []
        used_product_ids = set()  # Track used products to prevent duplicates
        
        # 예산을 KRW로 통일 (최대 예산만 사용)
        budget_max_krw = request.budget_max
        if request.currency == "USD":
            budget_max_krw = request.budget_max * USD_TO_KRW_RATE
        
        logger.info(f"Budget range: 최대 ₩{budget_max_krw:,}")
        
        # AI 추천별로 매칭 수행
        for i, ai_rec in enumerate(ai_recommendations[:3]):
            logger.info(f"🎯 Processing AI recommendation {i+1}: '{ai_rec.title}'")
            
            # 해당 AI 추천과 연결된 상품들 찾기 (이미 사용된 상품 제외)
            relevant_products = [
                p for p in naver_products 
                if hasattr(p, 'ai_recommendation_index') 
                and p.ai_recommendation_index == i
                and p.productId not in used_product_ids  # Deduplication
            ]
            
            logger.info(f"  -> Found {len(relevant_products)} relevant products for AI rec {i+1}")
            
            if not relevant_products:
                logger.warning(f"No relevant products found for AI recommendation {i+1}, using fallback")
                # 예산 범위 내 다른 상품들에서 찾기 (이미 사용된 것 제외)
                fallback_products = [
                    p for p in naver_products 
                    if p.lprice <= budget_max_krw * 1.5  # 최대 예산의 1.5배까지 허용
                    and p.productId not in used_product_ids  # Deduplication
                ]
                relevant_products = fallback_products[:3]
                logger.info(f"  -> Using {len(relevant_products)} fallback products (unused)")
            
            if relevant_products:
                # 🔥 GPT 기반 상품 검증 및 재선별
                validated_product = await self._gpt_validate_and_select_product(ai_rec, relevant_products, budget_max_krw)
                
                if validated_product:
                    # 상품 ID를 사용 목록에 추가하여 중복 방지
                    used_product_ids.add(validated_product.productId)
                    
                    # 매칭된 상품으로 추천 생성
                    enhanced_rec = self._create_enhanced_recommendation_with_product(ai_rec, validated_product, request)
                    enhanced_recommendations.append(enhanced_rec)
                    
                    logger.info(f"✅ GPT validated match: '{ai_rec.title}' with '{validated_product.title[:50]}...' (₩{validated_product.lprice:,}) - Product ID: {validated_product.productId}")
                else:
                    # GPT가 적합한 제품을 찾지 못한 경우
                    logger.warning(f"❌ GPT validation failed for '{ai_rec.title}' - no suitable products found")
                    # AI 추천을 그대로 사용 (KRW 변환)
                    ai_rec_krw = self._convert_ai_rec_to_krw(ai_rec, budget_max_krw)
                    enhanced_recommendations.append(ai_rec_krw)
                
            else:
                # 매칭되는 상품이 없으면 AI 추천을 그대로 사용 (KRW 변환)
                ai_rec_krw = self._convert_ai_rec_to_krw(ai_rec, budget_max_krw)
                enhanced_recommendations.append(ai_rec_krw)
                logger.info(f"⚠️ No matching product found for '{ai_rec.title}', using original AI recommendation")
        
        logger.info(f"🎯 Smart Integration completed - Final recommendations: {len(enhanced_recommendations)}")
        return enhanced_recommendations
    
    async def _gpt_validate_and_select_product(self, ai_rec, naver_products: List[NaverProductResult], budget_max_krw: int) -> Optional[NaverProductResult]:
        """
        GPT를 사용하여 네이버 상품 중 AI 추천과 가장 적합한 상품을 검증하고 선택
        사용자가 요청한 대로, 상품명과 설명, 가격 등을 GPT에게 전달하여 재검수
        """
        try:
            # Check if we have OpenAI API key
            import os
            openai_key = os.getenv("OPENAI_API_KEY", "")
            if not openai_key:
                logger.info("🔥 No OpenAI API key - falling back to traditional matching")
                return self._select_best_matching_product(naver_products, budget_max_krw, ai_rec.title)
            
            # Prepare product information for GPT evaluation with quality scores
            products_info = []
            for i, product in enumerate(naver_products[:5]):  # Limit to top 5 for efficiency
                # Calculate quality score if not already done
                if not hasattr(product, 'quality_score') or product.quality_score is None:
                    quality_score = self.naver_client.calculate_product_quality_score(product)
                    product.quality_score = quality_score
                else:
                    quality_score = product.quality_score
                
                # Get individual quality components
                brand_score = self.naver_client._calculate_brand_trust_score(product.brand)
                mall_score = self.naver_client._calculate_mall_trust_score(product.mallName)
                title_score = self.naver_client._calculate_title_quality_score(product.title)
                
                products_info.append({
                    'index': i,
                    'title': product.title,
                    'price': product.lprice,
                    'brand': product.brand,
                    'category': f"{product.category1} > {product.category2} > {product.category3}".replace(' > ', ' > ').strip(' > '),
                    'mall': product.mallName,
                    'quality_score': quality_score,
                    'brand_trust': brand_score,
                    'mall_trust': mall_score,
                    'title_quality': title_score,
                    'search_method': getattr(product, 'search_method', 'unknown')
                })
            
            # Create enhanced GPT prompt for product validation with quality metrics
            validation_prompt = f"""
**선물 추천 상품 검증 및 선별 (품질 지표 포함)**

AI가 추천한 선물:
- 제목: {ai_rec.title}
- 설명: {ai_rec.description[:200]}...
- 카테고리: {ai_rec.category}
- 예상 가격: {ai_rec.price_display}

네이버쇼핑 검색 결과 (최대 예산: ₩{budget_max_krw:,}):
"""
            
            for product in products_info:
                validation_prompt += f"""
[{product['index']}] {product['title']}
    📊 품질 지표:
    - 종합 품질점수: {product['quality_score']:.2f}/1.0
    - 브랜드 신뢰도: {product['brand_trust']:.2f} ({product['brand'] or '미지정'})
    - 쇼핑몰 신뢰도: {product['mall_trust']:.2f} ({product['mall']})
    - 상품명 품질: {product['title_quality']:.2f}
    - 검색방식: {product['search_method']}
    
    💰 가격 정보:
    - 가격: ₩{product['price']:,}
    - 카테고리: {product['category']}
"""
            
            validation_prompt += f"""

**선별 기준 (우선순위 순):**
1. **연관성**: AI 추천과의 매칭도 (가장 중요)
2. **품질 점수**: 브랜드, 쇼핑몰, 상품명 품질 종합 평가
3. **가격 적정성**: 예산 범위 내 적정 가격
4. **신뢰도**: 브랜드와 쇼핑몰의 신뢰성

**요청사항:**
1. 위 기준을 종합적으로 고려하여 가장 적합한 상품을 선택하세요.
2. 연관성이 너무 낮은 상품(예: 커피 추천 → 책 상품)은 품질이 높아도 제외하세요.
3. 품질점수가 0.3 미만인 상품은 가급적 피하세요.
4. 예산을 크게 초과하는 상품도 제외하세요.
5. 모든 조건을 만족하는 상품이 없다면 "NONE"을 반환하세요.

**반환 형식:** 선택한 상품의 인덱스 번호만 반환 (0, 1, 2, 3, 4 중 하나) 또는 "NONE"
**예시:** 2
**반환:**
"""
            
            # Call OpenAI API for validation
            import openai
            import asyncio
            
            def call_openai_sync():
                client = openai.OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "선물 추천 전문가로서, AI 추천과 실제 상품의 연관성을 정확히 평가하여 가장 적합한 상품을 선택하세요."},
                        {"role": "user", "content": validation_prompt}
                    ],
                    max_tokens=50,
                    temperature=0.1
                )
                return response.choices[0].message.content.strip()
            
            # Run in thread to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, call_openai_sync)
            
            logger.info(f"🔥 GPT validation result for '{ai_rec.title}': {result}")
            
            # 디버그: GPT 검증 과정 로깅
            self._log_gpt_validation_process(ai_rec, products_info, result)
            
            # Parse GPT response
            if result.upper() == "NONE":
                logger.info(f"❌ GPT found no suitable products for '{ai_rec.title}' - 매칭되는 상품이 없습니다")
                return None
            
            try:
                selected_index = int(result.strip())
                if 0 <= selected_index < len(naver_products):
                    selected_product = naver_products[selected_index]
                    logger.info(f"✅ GPT selected product {selected_index}: '{selected_product.title[:50]}...' (₩{selected_product.lprice:,})")
                    return selected_product
                else:
                    logger.warning(f"⚠️ GPT returned invalid index {selected_index}, falling back to traditional matching")
                    return self._select_best_matching_product(naver_products, budget_max_krw, ai_rec.title)
            except ValueError:
                logger.warning(f"⚠️ GPT returned non-numeric result '{result}', falling back to traditional matching")
                return self._select_best_matching_product(naver_products, budget_max_krw, ai_rec.title)
            
        except Exception as e:
            logger.error(f"🔥 GPT validation failed: {str(e)}, falling back to traditional matching")
            return self._select_best_matching_product(naver_products, budget_max_krw, ai_rec.title)
    
    def _log_gpt_validation_process(self, ai_rec, products_info: List[Dict], gpt_result: str):
        """GPT 검증 과정을 상세히 로깅하여 디버깅 지원"""
        logger.info("🔍 === GPT 상품 검증 과정 상세 로그 ===")
        logger.info(f"📝 AI 추천: '{ai_rec.title}' (카테고리: {ai_rec.category})")
        logger.info(f"🔎 후보 상품 {len(products_info)}개:")
        
        for product in products_info:
            logger.info(f"  [{product['index']}] {product['title'][:60]}... - ₩{product['price']:,}")
        
        logger.info(f"🤖 GPT 선택 결과: {gpt_result}")
        
        if gpt_result.upper() != "NONE":
            try:
                selected_idx = int(gpt_result.strip())
                if 0 <= selected_idx < len(products_info):
                    selected = products_info[selected_idx]
                    logger.info(f"✅ 선택된 상품: [{selected_idx}] {selected['title'][:60]}... - ₩{selected['price']:,}")
                    logger.info(f"💡 선택 이유: GPT가 AI 추천 '{ai_rec.title}'와 가장 관련성이 높다고 판단")
                else:
                    logger.warning(f"⚠️ 잘못된 인덱스: {selected_idx}")
            except ValueError:
                logger.warning(f"⚠️ 숫자가 아닌 응답: {gpt_result}")
        else:
            logger.info("❌ GPT 판단: 적합한 상품이 없음")
        
        logger.info("🔍 === GPT 검증 과정 로그 끝 ===")
    
    def _select_best_matching_product(self, products: List[NaverProductResult], budget_max_krw: int, ai_title: str = "") -> NaverProductResult:
        """예산과 관련성에 가장 적합한 상품 선택"""
        target_price = budget_max_krw // 2  # 최대 예산의 절반을 목표 가격으로 설정
        
        # 최대 예산 내 상품 우선 선택
        budget_products = [p for p in products if p.lprice <= budget_max_krw]
        if not budget_products:
            budget_products = products
        
        if len(budget_products) == 1:
            return budget_products[0]
        
        # 관련성 점수 계산하여 최적 상품 선택
        best_product = None
        best_score = -1
        
        for product in budget_products:
            # 가격 점수 (목표 가격에 가까울수록 높은 점수)
            price_score = 1.0 - (abs(product.lprice - target_price) / target_price)
            price_score = max(0, price_score) * 0.3  # 30% 가중치
            
            # 관련성 점수 (AI 추천 제목과 상품명의 유사도)
            relevance_score = self._calculate_relevance_score(ai_title, product.title) * 0.7  # 70% 가중치
            
            total_score = price_score + relevance_score
            
            if total_score > best_score:
                best_score = total_score
                best_product = product
        
        return best_product or budget_products[0]
    
    def _calculate_relevance_score(self, ai_title: str, product_title: str) -> float:
        """AI 추천과 상품명의 관련성 점수 계산 (0-1)"""
        if not ai_title or not product_title:
            return 0.0
            
        ai_keywords = set(ai_title.lower().split())
        product_keywords = set(product_title.lower().split())
        
        # 공통 키워드 비율
        common_keywords = ai_keywords.intersection(product_keywords)
        if not ai_keywords:
            return 0.0
            
        return len(common_keywords) / len(ai_keywords)
    
    def _create_enhanced_recommendation_with_product(self, ai_rec, product: NaverProductResult, request):
        """AI 추천과 매칭된 상품으로 향상된 추천 생성 (GPT 검증 포함)"""
        from models.response.recommendation import GiftRecommendation
        
        # 상품명에서 핵심 키워드 추출해서 제목 개선
        product_title_clean = self.naver_client._clean_html_tags(product.title)
        
        # AI 제목의 핵심 의도 유지하되 실제 상품으로 업데이트
        enhanced_title = self._merge_ai_intent_with_product(ai_rec.title, product_title_clean)
        
        # GPT 검증 완료를 나타내는 강화된 reasoning
        enhanced_reasoning = f"""{ai_rec.reasoning}

🤖 GPT 검증 완료: AI 추천과 실제 상품의 연관성을 분석하여 가장 적합한 제품을 선별했습니다.
✅ 네이버쇼핑에서 정확히 매칭된 실제 구매 가능한 상품입니다."""
        
        return GiftRecommendation(
            title=enhanced_title,
            description=f"{ai_rec.description}\n\n🛍️ 실제 상품: {product_title_clean}\n💰 가격: ₩{product.lprice:,} ({product.mallName})\n🏷️ 브랜드: {product.brand or '기타'}",
            category=ai_rec.category,
            estimated_price=product.lprice,
            currency="KRW",
            price_display=f"₩{product.lprice:,}",
            reasoning=enhanced_reasoning,
            purchase_link=product.link,
            image_url=product.image,
            confidence_score=min(ai_rec.confidence_score + 0.2, 1.0)  # GPT 검증 보너스 증가
        )
    
    def _merge_ai_intent_with_product(self, ai_title: str, product_title: str) -> str:
        """AI 의도와 실제 상품명을 자연스럽게 결합"""
        # AI 제목에서 형용사/수식어 추출
        ai_descriptors = []
        ai_words = ai_title.split()
        
        descriptors = ['프리미엄', '고급', '스마트', '무선', '휴대용', '전문가용', '초보자용', '독서용', '운동용', '커피', '차', '여행용']
        for word in ai_words:
            if any(desc in word for desc in descriptors):
                ai_descriptors.append(word)
        
        # 상품명에서 핵심 명사 추출 (앞 2-3 단어)
        product_words = product_title.split()[:3]
        product_core = ' '.join(product_words)
        
        # 결합
        if ai_descriptors:
            return f"{'•'.join(ai_descriptors)} {product_core}"
        else:
            return product_core
    
    def _convert_ai_rec_to_krw(self, ai_rec, budget_max_krw: int):
        """AI 추천을 KRW로 변환"""
        ai_rec_krw = ai_rec
        if ai_rec.currency != "KRW":
            ai_rec_krw.estimated_price = int(ai_rec.estimated_price * USD_TO_KRW_RATE) if ai_rec.estimated_price else budget_max_krw // 2
            ai_rec_krw.currency = "KRW"
            ai_rec_krw.price_display = f"₩{ai_rec_krw.estimated_price:,}"
        return ai_rec_krw
    
    async def _create_recommendations_from_products(self, naver_products: List[NaverProductResult], request) -> List:
        """네이버 상품에서 직접 추천 생성 (AI 추천이 없을 때)"""
        from models.response.recommendation import GiftRecommendation
        
        recommendations = []
        for i, product in enumerate(naver_products[:3]):
            rec = GiftRecommendation(
                title=f"추천 상품 #{i+1}: {product.title[:30]}...",
                description=f"네이버쇼핑에서 찾은 '{request.occasion}' 선물 추천 상품입니다.",
                category=product.category3 or "일반 상품",
                estimated_price=product.lprice,
                currency="KRW",
                price_display=f"₩{product.lprice:,}",
                reasoning=f"사용자의 관심사 '{', '.join(request.interests[:2])}'에 적합한 상품입니다.",
                purchase_link=product.link,
                image_url=product.image,
                confidence_score=0.7 + (i * 0.05)
            )
            recommendations.append(rec)
        
        return recommendations
    
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
    
    async def _create_fallback_ai_recommendations(self, request):
        """OpenAI API 사용 불가 시 관심사 기반 대체 추천 생성"""
        from models.response.recommendation import GiftRecommendation
        
        # Create a mock AI response structure
        class MockAIResponse:
            def __init__(self):
                self.success = True
                self.recommendations = []
                self.error_message = None
        
        mock_response = MockAIResponse()
        
        # Interest-based recommendation templates with diverse categories
        interest_templates = {
            "커피": {
                "title": "프리미엄 커피 메이커",
                "description": "집에서도 카페 수준의 커피를 즐길 수 있는 고품질 커피 메이커입니다. 다양한 추출 방식을 지원하여 취향에 맞는 완벽한 커피를 만들 수 있습니다.",
                "category": "전자제품",
                "reasoning": "커피를 좋아하는 분에게는 직접 만든 고품질 커피를 즐길 수 있는 기회를 선사하는 의미있는 선물입니다."
            },
            "독서": {
                "title": "베스트셀러 도서 세트",
                "description": "최근 화제가 된 베스트셀러 도서들을 엄선한 컬렉션입니다. 다양한 장르의 책들로 구성되어 새로운 지적 여행을 선사합니다.",
                "category": "도서",
                "reasoning": "독서를 즐기는 분에게는 새로운 이야기와 지식을 탐험할 수 있는 기회를 제공하는 완벽한 선물입니다."
            },
            "운동": {
                "title": "프리미엄 운동용품 세트",
                "description": "집에서도 효과적으로 운동할 수 있는 고품질 운동용품 세트입니다. 다양한 운동에 활용할 수 있도록 구성되었습니다.",
                "category": "스포츠",
                "reasoning": "운동을 좋아하는 분에게는 더욱 즐겁고 효과적인 운동 경험을 선사하는 실용적인 선물입니다."
            },
            "요리": {
                "title": "고급 요리 도구 세트",
                "description": "전문 요리사가 사용하는 수준의 고품질 요리 도구들로 구성된 세트입니다. 요리의 즐거움을 한층 높여줍니다.",
                "category": "주방용품",
                "reasoning": "요리를 즐기는 분에게는 더욱 편리하고 전문적인 요리 경험을 선사하는 훌륭한 선물입니다."
            },
            "음악": [
                {
                    "title": "고음질 무선 이어폰",
                    "description": "최신 기술이 적용된 고음질 무선 이어폰으로, 언제 어디서나 최고의 음악 감상 경험을 제공합니다.",
                    "category": "전자제품",
                    "reasoning": "음악을 사랑하는 분에게는 더욱 몰입감 있는 음악 감상 경험을 선사하는 특별한 선물입니다."
                },
                {
                    "title": "음악 관련 도서",
                    "description": "음악의 역사와 이론, 유명 음악가의 이야기를 담은 교양서입니다. 음악에 대한 깊이 있는 이해를 돕습니다.",
                    "category": "도서",
                    "reasoning": "음악을 좋아하는 분에게 음악에 대한 지식과 통찰을 제공하는 의미있는 선물입니다."
                },
                {
                    "title": "클래식 음반 컬렉션",
                    "description": "명작 클래식 음악을 엄선한 CD 컬렉션으로, 집에서 고품질 음악 감상을 즐길 수 있습니다.",
                    "category": "음반/CD",
                    "reasoning": "음악 애호가에게 다양한 클래식 음악을 감상할 수 있는 기회를 선사하는 특별한 선물입니다."
                }
            ]
        }
        
        # Track used categories to ensure diversity
        used_categories = set()
        
        # Generate recommendations based on user interests with diversity
        for i, interest in enumerate(request.interests[:3]):
            templates = interest_templates.get(interest)
            if not templates:
                # Generic fallback for unknown interests
                template = {
                    "title": f"{interest} 관련 프리미엄 상품",
                    "description": f"{interest}에 관심이 있는 분을 위한 특별한 선물입니다. 고품질 제품으로 만족도가 높습니다.",
                    "category": "일반 상품",
                    "reasoning": f"{interest}에 대한 관심사를 고려하여 선별한 의미있는 선물입니다."
                }
            else:
                # Handle both single template and multiple templates
                if isinstance(templates, list):
                    # Multiple options available - select most diverse
                    available_templates = []
                    for template_option in templates:
                        if template_option["category"] not in used_categories:
                            available_templates.append(template_option)
                    
                    # Use diverse template if available, otherwise use first
                    template = available_templates[0] if available_templates else templates[0]
                else:
                    # Single template
                    template = templates
            
            # Track category to ensure diversity
            used_categories.add(template["category"])
            
            # Calculate price within budget (0 to max budget)
            price = (request.budget_max * (i + 1) // 4)  # Distribute prices from 25% to 100% of max budget
            
            rec = GiftRecommendation(
                title=template["title"],
                description=template["description"],
                category=template["category"],
                estimated_price=price,
                currency=request.currency,
                price_display=f"₩{price:,}" if request.currency == "KRW" else f"${price}",
                reasoning=template["reasoning"],
                purchase_link=None,  # Will be filled by Naver integration
                image_url=None,      # Will be filled by Naver integration
                confidence_score=0.85 - (i * 0.05)  # Slightly lower confidence for fallback
            )
            
            mock_response.recommendations.append(rec)
        
        # Add a generic recommendation if not enough interests
        if len(mock_response.recommendations) < 3:
            remaining = 3 - len(mock_response.recommendations)
            for i in range(remaining):
                price = request.budget_max // 2  # Use half of max budget for generic recommendations
                rec = GiftRecommendation(
                    title=f"{request.occasion} 특별 선물",
                    description=f"{request.relationship}에게 드리는 {request.occasion} 기념 선물입니다. 특별한 의미를 담은 고품질 상품입니다.",
                    category="선물",
                    estimated_price=price,
                    currency=request.currency,
                    price_display=f"₩{price:,}" if request.currency == "KRW" else f"${price}",
                    reasoning=f"{request.occasion}에 어울리는 의미있는 선물입니다.",
                    purchase_link=None,
                    image_url=None,
                    confidence_score=0.8 - (i * 0.05)
                )
                mock_response.recommendations.append(rec)
        
        logger.info(f"Created {len(mock_response.recommendations)} fallback AI recommendations")
        return mock_response