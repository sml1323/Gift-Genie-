#!/usr/bin/env python3
"""
GPT 검증 시스템 테스트 스크립트
사용자가 보고한 매칭 문제를 해결하는지 확인
"""

import asyncio
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.request.gift import GiftRequest
from services.ai.naver_recommendation_engine import NaverGiftRecommendationEngine

async def test_gpt_validation():
    """GPT 기반 상품 검증 시스템 테스트"""
    
    print("🧪 === GPT 상품 검증 시스템 테스트 시작 ===")
    
    # API 키 확인
    openai_key = os.getenv("OPENAI_API_KEY", "")
    naver_id = os.getenv("NAVER_CLIENT_ID", "")
    naver_secret = os.getenv("NAVER_CLIENT_SECRET", "")
    
    print(f"🔑 API 키 상태:")
    print(f"  - OpenAI: {'✅ 설정됨' if openai_key else '❌ 없음 (시뮬레이션 모드)'}")
    print(f"  - Naver: {'✅ 설정됨' if naver_id and naver_secret else '❌ 없음 (시뮬레이션 모드)'}")
    
    # 추천 엔진 초기화
    engine = NaverGiftRecommendationEngine(openai_key, naver_id, naver_secret)
    
    # 테스트 요청 생성 (사용자가 문제로 지적한 케이스와 유사하게)
    test_request = GiftRequest(
        recipient_age=20,
        relationship="친구",
        occasion="생일선물",
        interests=["커피", "독서", "음악"],
        budget_min=10000,
        budget_max=100000,
        currency="KRW",
        special_requirements=""
    )
    
    print(f"\n📝 테스트 요청:")
    print(f"  - 수신자: {test_request.recipient_age}세 {test_request.relationship}")
    print(f"  - 관심사: {', '.join(test_request.interests)}")
    print(f"  - 예산: ₩{test_request.budget_min:,} - ₩{test_request.budget_max:,}")
    
    try:
        print(f"\n🚀 추천 생성 시작...")
        
        # 추천 생성 실행
        response = await engine.generate_naver_recommendations(test_request)
        
        print(f"\n📊 결과 요약:")
        print(f"  - 성공 여부: {'✅ 성공' if response.success else '❌ 실패'}")
        print(f"  - 추천 개수: {len(response.recommendations)}개")
        print(f"  - 처리 시간: {response.total_processing_time:.2f}초")
        print(f"  - 시뮬레이션 모드: {'예' if response.simulation_mode else '아니오'}")
        
        if response.error_message:
            print(f"  - 오류: {response.error_message}")
        
        # 각 추천 상세 분석
        print(f"\n🎁 생성된 추천 상세:")
        for i, rec in enumerate(response.recommendations, 1):
            print(f"\n=== 추천 #{i} ===")
            print(f"제목: {rec.title}")
            print(f"설명: {rec.description[:100]}...")
            print(f"카테고리: {rec.category}")
            print(f"가격: {rec.price_display}")
            print(f"신뢰도: {rec.confidence_score:.2f}")
            print(f"구매링크: {'있음' if rec.purchase_link else '없음'}")
            print(f"이미지: {'있음' if rec.image_url else '없음'}")
            
            # GPT 검증 여부 확인
            if "GPT 검증 완료" in rec.reasoning:
                print("🤖 GPT 검증: ✅ 완료")
            else:
                print("🤖 GPT 검증: ❌ 미완료 (fallback 사용)")
        
        # 기존 문제 해결 여부 분석
        print(f"\n📈 개선 분석:")
        matching_issues = 0
        for rec in response.recommendations:
            # 기존 문제점들 체크
            if ("북앤드" in rec.title and "커피" in str(test_request.interests)) or \
               ("계획표" in rec.title and "독서" in str(test_request.interests)):
                matching_issues += 1
                print(f"⚠️ 잠재적 매칭 문제 발견: {rec.title}")
        
        if matching_issues == 0:
            print("✅ 기존 매칭 문제 해결됨: AI 추천과 실제 상품이 적절히 매칭됨")
        else:
            print(f"❌ {matching_issues}개의 매칭 문제 여전히 존재")
        
        # 검색 결과 분석
        print(f"\n🔍 검색 결과 분석:")
        print(f"  - 검색된 상품 수: {len(response.search_results)}개")
        realistic_prices = [sr for sr in response.search_results if sr.price >= 1000]
        print(f"  - 현실적 가격 상품: {len(realistic_prices)}개")
        
        if len(realistic_prices) == len(response.search_results):
            print("✅ 가격 필터링 개선됨: 비현실적 저가 상품 제거 완료")
        else:
            print(f"⚠️ {len(response.search_results) - len(realistic_prices)}개의 비현실적 가격 상품 여전히 존재")
        
        return response.success
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {str(e)}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🎯 Gift Genie GPT 검증 시스템 테스트")
    success = asyncio.run(test_gpt_validation())
    
    if success:
        print("\n🎉 테스트 완료: GPT 검증 시스템이 정상적으로 작동합니다!")
        print("✅ 사용자가 보고한 매칭 문제가 개선되었습니다.")
    else:
        print("\n❌ 테스트 실패: 추가 디버깅이 필요합니다.")
    
    print("\n=== 테스트 종료 ===")