#\!/usr/bin/env python3
"""
Gift Genie - AI Engine Debug Test
AI 추천 엔진 단독 테스트
"""

import asyncio
import json
import aiohttp

async def test_basic_ai():
    """기본 AI 추천 테스트"""
    
    test_request = {
        "recipient_age": 28,
        "recipient_gender": "남성",
        "relationship": "친구",
        "interests": ["커피", "독서"],
        "occasion": "생일선물",
        "budget_min": 50000,
        "budget_max": 200000,
        "currency": "KRW",
        "special_requirements": "프리미엄 제품 선호"
    }
    
    print("🧪 AI 추천 엔진 단독 테스트")
    print("=" * 40)
    
    try:
        async with aiohttp.ClientSession() as session:
            # 기본 AI 추천 API 테스트
            async with session.post(
                "http://localhost:8000/api/v1/recommendations/basic",
                json=test_request,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ AI 추천 성공\!")
                    print(f"추천 개수: {len(data.get('recommendations', []))}")
                    
                    for i, rec in enumerate(data.get('recommendations', [])):
                        print(f"\n추천 #{i+1}:")
                        print(f"  제목: {rec.get('title')}")
                        print(f"  카테고리: {rec.get('category')}")
                        print(f"  가격: {rec.get('price_display')}")
                else:
                    error_text = await response.text()
                    print(f"❌ AI 추천 실패: {error_text}")
                    
    except Exception as e:
        print(f"🚨 예외 발생: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_basic_ai())
EOF < /dev/null
