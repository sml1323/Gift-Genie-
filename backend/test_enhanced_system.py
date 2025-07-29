#!/usr/bin/env python3
"""
Gift Genie - Enhanced System Test
Test the new intelligent query refinement and retry mechanism
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.request.recommendation import GiftRequest
from services.ai.enhanced_naver_engine import EnhancedNaverRecommendationEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_enhanced_recommendation_system():
    """향상된 추천 시스템 테스트"""
    
    logger.info("🧪 Starting Enhanced Recommendation System Test")
    
    # 환경 변수 확인
    openai_key = os.getenv("OPENAI_API_KEY", "")
    naver_id = os.getenv("NAVER_CLIENT_ID", "")
    naver_secret = os.getenv("NAVER_CLIENT_SECRET", "")
    
    if not openai_key:
        logger.warning("⚠️ OPENAI_API_KEY not set - using simulation mode")
    if not naver_id or not naver_secret:
        logger.warning("⚠️ Naver API credentials not set - using simulation mode")
    
    # 향상된 엔진 초기화
    engine = EnhancedNaverRecommendationEngine(
        openai_api_key=openai_key,
        naver_client_id=naver_id,
        naver_client_secret=naver_secret
    )
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "어려운 키워드 조합 (전자제품)",
            "request": GiftRequest(
                recipient_age=25,
                recipient_gender="남성",
                relationship="친구",
                interests=["기술", "음악", "게임"],
                occasion="생일",
                budget_min=50,
                budget_max=150,
                currency="USD"
            )
        },
        {
            "name": "넓은 예산 범위 (여성 화장품)",
            "request": GiftRequest(
                recipient_age=30,
                recipient_gender="여성",
                relationship="동료",
                interests=["뷰티", "패션", "요리"],
                occasion="승진축하",
                budget_min=30,
                budget_max=200,
                currency="USD"
            )
        },
        {
            "name": "제한적 예산 (학생 선물)",
            "request": GiftRequest(
                recipient_age=20,
                recipient_gender="여성",
                relationship="후배",
                interests=["공부", "카페", "독서"],
                occasion="졸업",
                budget_min=20,
                budget_max=50,
                currency="USD"
            )
        },
        {
            "name": "모호한 관심사 (중년 남성)",
            "request": GiftRequest(
                recipient_age=45,
                recipient_gender="남성",
                relationship="상사",
                interests=["골프", "와인", "독서"],
                occasion="승진축하",
                budget_min=100,
                budget_max=300,
                currency="USD"
            )
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 Test Case {i}: {test_case['name']}")
        logger.info(f"{'='*60}")
        
        try:
            start_time = datetime.now()
            
            # 향상된 추천 실행
            response = await engine.generate_recommendations_with_retry(test_case['request'])
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 결과 분석
            success = response.success
            recommendations_count = len(response.recommendations)
            has_naver_products = response.naver_results_count > 0
            
            # 개선 메트릭 분석
            enhancement_metrics = response.enhancement_metrics if hasattr(response, 'enhancement_metrics') else {}
            refinement_attempts = enhancement_metrics.get('refinement_attempts', 0)
            final_products_found = enhancement_metrics.get('final_products_found', 0)
            
            logger.info(f"📊 Test Results:")
            logger.info(f"  ✅ Success: {success}")
            logger.info(f"  📝 Recommendations: {recommendations_count}")
            logger.info(f"  🛍️ Naver Products: {response.naver_results_count}")
            logger.info(f"  🔄 Refinement Attempts: {refinement_attempts}")
            logger.info(f"  🎯 Final Products Found: {final_products_found}")
            logger.info(f"  ⏱️ Total Time: {duration:.2f}s")
            
            if response.success and response.recommendations:
                logger.info(f"  📋 Sample Recommendations:")
                for j, rec in enumerate(response.recommendations[:3], 1):
                    logger.info(f"    {j}. {rec.title} - {rec.price_display}")
                    logger.info(f"       Confidence: {rec.confidence_score:.2f}")
                    logger.info(f"       Has Link: {'Yes' if rec.purchase_link else 'No'}")
            
            results.append({
                "test_case": test_case['name'],
                "success": success,
                "recommendations_count": recommendations_count,
                "naver_products_count": response.naver_results_count,
                "refinement_attempts": refinement_attempts,
                "final_products_found": final_products_found,
                "total_time": duration,
                "has_purchase_links": any(rec.purchase_link for rec in response.recommendations) if response.recommendations else False
            })
            
        except Exception as e:
            logger.error(f"❌ Test Case {i} failed: {str(e)}")
            results.append({
                "test_case": test_case['name'],
                "success": False,
                "error": str(e),
                "total_time": (datetime.now() - start_time).total_seconds()
            })
    
    # 종합 결과 분석
    logger.info(f"\n{'='*60}")
    logger.info(f"🏁 FINAL TEST RESULTS")
    logger.info(f"{'='*60}")
    
    successful_tests = sum(1 for r in results if r.get('success', False))
    total_tests = len(results)
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    
    avg_time = sum(r.get('total_time', 0) for r in results) / len(results)
    avg_recommendations = sum(r.get('recommendations_count', 0) for r in results) / len(results)
    avg_attempts = sum(r.get('refinement_attempts', 0) for r in results) / len(results)
    
    tests_with_naver = sum(1 for r in results if r.get('naver_products_count', 0) > 0)
    tests_with_links = sum(1 for r in results if r.get('has_purchase_links', False))
    
    logger.info(f"📈 Overall Performance:")
    logger.info(f"  ✅ Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
    logger.info(f"  ⏱️ Average Time: {avg_time:.2f}s")
    logger.info(f"  📝 Average Recommendations: {avg_recommendations:.1f}")
    logger.info(f"  🔄 Average Refinement Attempts: {avg_attempts:.1f}")
    logger.info(f"  🛍️ Tests with Naver Products: {tests_with_naver}/{total_tests}")
    logger.info(f"  🔗 Tests with Purchase Links: {tests_with_links}/{total_tests}")
    
    # 성능 분석
    logger.info(f"\n🎯 Performance Analysis:")
    if success_rate >= 90:
        logger.info("  🟢 EXCELLENT: System performing above expectations")
    elif success_rate >= 75:
        logger.info("  🟡 GOOD: System performing well with minor issues")
    elif success_rate >= 50:
        logger.info("  🟠 FAIR: System needs improvement")
    else:
        logger.info("  🔴 POOR: System requires major fixes")
    
    if avg_time <= 10:
        logger.info("  🟢 FAST: Response time excellent")
    elif avg_time <= 20:
        logger.info("  🟡 MODERATE: Response time acceptable")
    else:
        logger.info("  🟠 SLOW: Response time needs optimization")
    
    # 개선 제안
    logger.info(f"\n💡 Improvement Suggestions:")
    if tests_with_naver < total_tests:
        logger.info("  - Consider fallback strategies when Naver API fails")
    if avg_attempts > 3:
        logger.info("  - Optimize initial keyword generation to reduce refinement attempts")
    if avg_time > 15:
        logger.info("  - Implement caching for frequently requested product categories")
    
    return results


async def main():
    """메인 테스트 실행"""
    try:
        results = await test_enhanced_recommendation_system()
        
        # 결과를 JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"\n📄 Test results saved to: {filename}")
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)