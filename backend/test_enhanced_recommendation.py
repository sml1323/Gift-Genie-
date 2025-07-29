#!/usr/bin/env python3
"""
Enhanced Gift Recommendation System Test
Tests the new 5-iteration retry mechanism with intelligent query refinement
"""

import asyncio
import os
import logging
import sys
from datetime import datetime

# Add the backend directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai.naver_recommendation_engine import NaverGiftRecommendationEngine
from models.request.recommendation import GiftRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_enhanced_recommendation_system():
    """Enhanced 추천 시스템 테스트"""
    
    print("🚀 Enhanced Gift Recommendation System Test Starting...")
    print("=" * 60)
    
    # API 키 확인
    openai_key = os.getenv("OPENAI_API_KEY", "")
    naver_client_id = os.getenv("NAVER_CLIENT_ID", "")
    naver_client_secret = os.getenv("NAVER_CLIENT_SECRET", "")
    
    print(f"📋 Configuration Check:")
    print(f"  - OpenAI API Key: {'✅ Configured' if openai_key else '❌ Missing'}")
    print(f"  - Naver Client ID: {'✅ Configured' if naver_client_id else '❌ Missing'}")
    print(f"  - Naver Client Secret: {'✅ Configured' if naver_client_secret else '❌ Missing'}")
    print()
    
    # 추천 엔진 초기화
    engine = NaverGiftRecommendationEngine(
        openai_api_key=openai_key,
        naver_client_id=naver_client_id,
        naver_client_secret=naver_client_secret
    )
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "20대 여성 생일선물 (어려운 케이스)",
            "request": GiftRequest(
                recipient_age=25,
                recipient_gender="여성",
                relationship="친구",
                interests=["음악", "여행", "카페"],
                occasion="생일",
                budget_min=50000,
                budget_max=150000,
                currency="KRW",
                restrictions=["알레르기 없음"]
            )
        },
        {
            "name": "30대 남성 승진축하 (일반적인 케이스)", 
            "request": GiftRequest(
                recipient_age=32,
                recipient_gender="남성",
                relationship="동료",
                interests=["기술", "커피", "골프"],
                occasion="승진축하",
                budget_min=100000,
                budget_max=300000,
                currency="KRW",
                restrictions=[]
            )
        }
    ]
    
    # 각 테스트 케이스 실행
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        
        start_time = datetime.now()
        
        try:
            # Enhanced 추천 실행
            response = await engine.generate_naver_recommendations(test_case['request'])
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            print(f"⏱️  Processing Time: {processing_time:.2f}s")
            print(f"📊 Results:")
            
            if hasattr(response, 'recommendations') and response.recommendations:
                print(f"  - Total Recommendations: {len(response.recommendations)}")
                print(f"  - Success: ✅")
                
                # 상위 3개 추천 표시
                for j, rec in enumerate(response.recommendations[:3], 1):
                    print(f"  {j}. {rec.title}")
                    print(f"     Category: {rec.category}")
                    print(f"     Price: {rec.price_display}")
                    print(f"     Confidence: {rec.confidence_score:.2f}")
                    if hasattr(rec, 'purchase_link') and rec.purchase_link:
                        print(f"     🛒 Available for purchase")
                    print()
                
            else:
                print(f"  - No recommendations found: ❌")
                if hasattr(response, 'error_message'):
                    print(f"  - Error: {response.error_message}")
            
            # 성능 메트릭 표시
            if hasattr(response, 'metrics'):
                metrics = response.metrics
                print(f"📈 Performance Metrics:")
                print(f"  - AI Generation Time: {metrics.ai_generation_time:.2f}s")
                print(f"  - Naver Search Time: {metrics.naver_search_time:.2f}s")
                print(f"  - Integration Time: {metrics.integration_time:.2f}s")
                print(f"  - Total Time: {metrics.total_time:.2f}s")
                print(f"  - API Calls: {metrics.api_calls_count}")
                print(f"  - Search Results: {metrics.search_results_count}")
            
        except Exception as e:
            print(f"❌ Test Failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60 + "\n")
    
    print("🏁 Enhanced Recommendation System Test Complete!")


async def test_query_refinement_only():
    """쿼리 개선 메커니즘만 단독 테스트"""
    
    print("🔬 Query Refinement Engine Test Starting...")
    print("=" * 50)
    
    from services.ai.intelligent_query_refinement import IntelligentQueryRefinementEngine
    
    openai_key = os.getenv("OPENAI_API_KEY", "")
    engine = IntelligentQueryRefinementEngine(openai_key)
    
    # 시뮬레이션 검색 함수
    async def mock_search_function(keywords, budget_max):
        """Mock search function that simulates finding products"""
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # 특정 키워드 조합에서만 성공하도록 시뮬레이션
        success_keywords = ["인기", "추천", "트렌드", "베스트", "프리미엄"]
        found_products = sum(1 for kw in keywords if any(success_kw in kw for success_kw in success_keywords))
        
        # 시뮬레이션 상품 리스트 (found_products 개수만큼)
        mock_products = []
        for i in range(found_products):
            mock_products.append({
                "title": f"Mock Product {i+1}",
                "price": budget_max // 2,
                "category": "테스트"
            })
        
        logger.info(f"Mock search: {keywords} → {len(mock_products)} products found")
        return mock_products
    
    # 테스트 데이터
    test_keywords = ["블루투스 이어폰", "무선 헤드셋"]
    gift_context = {
        'recipient_age': '25',
        'recipient_gender': '여성',
        'interests': ['음악', '기술'],
        'budget_min': 50000,
        'budget_max': 150000,
        'occasion': '생일',
        'relationship': '친구'
    }
    
    print(f"🎯 Test Keywords: {test_keywords}")
    print(f"👤 Gift Context: {gift_context}")
    print()
    
    try:
        # 재시도 메커니즘 실행
        products, session = await engine.refine_search_with_retries(
            original_keywords=test_keywords,
            gift_context=gift_context,
            search_function=mock_search_function,
            budget_max_krw=150000
        )
        
        print(f"📊 Refinement Results:")
        print(f"  - Final Success: {'✅' if session.final_success else '❌'}")
        print(f"  - Total Attempts: {len(session.attempts)}")
        print(f"  - Products Found: {len(products)}")
        print(f"  - Processing Time: {session.total_processing_time:.2f}s")
        
        if session.best_attempt:
            best = session.best_attempt
            print(f"  - Best Strategy: {best.refinement_strategy}")
            print(f"  - Best Keywords: {best.refined_keywords}")
        
        print(f"\n🔄 Attempt Details:")
        for attempt in session.attempts:
            status = "✅" if attempt.success else "❌"
            print(f"  {attempt.attempt_number}. {attempt.refinement_strategy}: {status}")
            print(f"     Keywords: {attempt.refined_keywords}")
            print(f"     Products: {attempt.products_found}")
            print(f"     Time: {attempt.processing_time:.2f}s")
            
    except Exception as e:
        print(f"❌ Refinement Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 Query Refinement Test Complete!")


async def main():
    """메인 테스트 실행"""
    
    print("🎁 Gift Genie Enhanced Recommendation System Test Suite")
    print("=" * 60)
    
    # 1. 쿼리 개선 메커니즘 단독 테스트
    await test_query_refinement_only()
    
    print("\n" + "=" * 60 + "\n")
    
    # 2. 전체 추천 시스템 테스트
    await test_enhanced_recommendation_system()


if __name__ == "__main__":
    asyncio.run(main())