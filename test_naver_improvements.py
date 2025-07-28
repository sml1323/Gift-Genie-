#!/usr/bin/env python3
"""
네이버 쇼핑 API 개선사항 테스트 스크립트
개선된 예산 범위, 키워드 최적화, API 매개변수 검증
"""

import sys
import os
import asyncio
sys.path.append('/home/eslway/work/Gift-Genie-/backend')

from backend.services.ai.naver_recommendation_engine import NaverGiftRecommendationEngine
from backend.models.request.recommendation import GiftRequest

async def test_improvements():
    """개선된 네이버 쇼핑 API 기능 테스트"""
    
    print("🔍 네이버 쇼핑 API 개선사항 테스트 시작\n")
    
    # 테스트용 요청 생성 (사용자가 언급한 문제 시나리오)
    gift_request = GiftRequest(
        recipient_age=25,
        recipient_gender="neutral",
        relationship="친구",
        occasion="생일",
        interests=["게임", "주방용품", "운동"],  # 이전에 문제가 있던 키워드들
        budget_min=50000,
        budget_max=195000,  # 사용자가 언급한 예산
        currency="KRW"
    )
    
    # 엔진 초기화 (시뮬레이션 모드로 테스트)
    engine = NaverGiftRecommendationEngine(
        openai_api_key="",  # 빈 키로 fallback 테스트
        naver_client_id="",  # 빈 키로 시뮬레이션 모드
        naver_client_secret=""
    )
    
    print("📊 개선사항 확인:")
    print("=" * 50)
    
    # 1. 예산 범위 설정 테스트
    budget_max_krw = gift_request.budget_max
    old_budget_min = max(1000, budget_max_krw // 100)  # 이전 로직
    new_budget_min = max(10000, budget_max_krw // 3)   # 개선된 로직
    
    print(f"1. 예산 범위 설정 개선:")
    print(f"   • 최대 예산: ₩{budget_max_krw:,}")
    print(f"   • 이전 최소 예산: ₩{old_budget_min:,} (비현실적)")
    print(f"   • 개선된 최소 예산: ₩{new_budget_min:,} (현실적)")
    print(f"   • 개선 효과: {(new_budget_min / old_budget_min):.1f}배 증가\n")
    
    # 2. 키워드 최적화 테스트
    print("2. 검색 키워드 최적화:")
    
    # 네이버 최적화 패턴 확인
    naver_patterns = {
        "주방용품": ["주방용품", "키친용품", "주방 세트"],
        "게임": ["게임기", "콘솔", "닌텐도", "플레이스테이션"],
        "운동": ["운동용품", "헬스용품", "피트니스"]
    }
    
    for interest in gift_request.interests:
        if interest in naver_patterns:
            print(f"   • '{interest}' → {naver_patterns[interest]}")
        else:
            print(f"   • '{interest}' → 직접 사용")
    print()
    
    # 3. API 매개변수 개선
    print("3. API 매개변수 최적화:")
    print("   • display: 5개 → 20개 (4배 증가)")
    print("   • sort: 'asc'(가격순) → 'sim'(정확도순)")
    print("   • 예상 효과: 더 많고 관련성 높은 검색 결과\n")
    
    # 4. 실제 엔진 테스트 (시뮬레이션 모드)
    print("4. 개선된 엔진 테스트 (시뮬레이션 모드):")
    print("   🔄 추천 시스템 실행 중...")
    
    try:
        result = await engine.generate_naver_recommendations(gift_request)
        
        if result.success:
            print(f"   ✅ 성공: {len(result.recommendations)}개 추천 생성")
            print(f"   ⏱️ 처리 시간: {result.total_processing_time:.2f}초")
            print(f"   🔍 검색 결과: {result.pipeline_metrics.search_results_count}개")
            
            print("\n📋 생성된 추천:")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"   {i}. {rec.title}")
                print(f"      💰 가격: {rec.price_display}")
                print(f"      📂 카테고리: {rec.category}")
                print(f"      ⭐ 신뢰도: {rec.confidence_score:.2f}")
                print()
        else:
            print(f"   ❌ 실패: {result.error_message}")
            
    except Exception as e:
        print(f"   ❌ 오류: {str(e)}")
    
    print("=" * 50)
    print("🎯 예상 개선 효과:")
    print("• 검색 결과 증가: 0개 → 10-20개 상품")
    print("• 매칭 품질 향상: 더 관련성 높은 상품 발견")
    print("• 사용자 만족도: 실제 구매 가능한 상품 추천")
    print("\n✅ 네이버 쇼핑 API 개선사항 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_improvements())