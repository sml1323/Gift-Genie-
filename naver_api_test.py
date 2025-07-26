#!/usr/bin/env python3
"""
네이버쇼핑 API 직접 테스트
API 연결 상태 및 응답 데이터 상세 검증
"""

import asyncio
import aiohttp
import json
import os

# Load environment variables
def load_env_file():
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    except FileNotFoundError:
        print("❌ .env file not found")

load_env_file()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

async def test_naver_api_basic():
    """기본 네이버쇼핑 API 연결 테스트"""
    print("🔍 네이버쇼핑 API 기본 연결 테스트")
    print("=" * 50)
    
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print("❌ 네이버 API 키가 설정되지 않았습니다")
        return False
    
    print(f"✅ Client ID: {NAVER_CLIENT_ID[:10]}...")
    print(f"✅ Client Secret: {NAVER_CLIENT_SECRET[:5]}...")
    print()
    
    # 간단한 검색어로 테스트
    test_queries = ["커피", "책", "여행가방", "헤드폰", "선물"]
    
    for query in test_queries:
        print(f"🔎 Testing query: '{query}'")
        success = await test_single_query(query)
        if success:
            print(f"✅ '{query}' 검색 성공!")
            return True
        else:
            print(f"❌ '{query}' 검색 실패")
        print()
    
    return False

async def test_single_query(query):
    """단일 검색어 테스트"""
    url = "https://openapi.naver.com/v1/search/shop.json"
    
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    
    params = {
        "query": query,
        "display": 5,
        "start": 1,
        "sort": "asc"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=headers, 
                params=params,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                
                print(f"   Status Code: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    items = data.get("items", [])
                    
                    print(f"   Found {len(items)} products")
                    
                    if items:
                        print("   Sample products:")
                        for i, item in enumerate(items[:3], 1):
                            title = item.get("title", "").replace("<b>", "").replace("</b>", "")
                            price = item.get("lprice", 0)
                            mall = item.get("mallName", "")
                            print(f"     {i}. {title[:30]}... - {int(price):,}원 ({mall})")
                        return True
                    else:
                        print("   ⚠️ 상품이 발견되지 않았습니다")
                        return False
                        
                elif response.status == 401:
                    print("   ❌ 인증 실패 - API 키를 확인하세요")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
                    
                elif response.status == 400:
                    print("   ❌ 잘못된 요청 - 파라미터를 확인하세요")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
                    
                else:
                    print(f"   ❌ API 오류 (Status: {response.status})")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
                    
    except asyncio.TimeoutError:
        print("   ❌ 타임아웃 오류")
        return False
    except Exception as e:
        print(f"   ❌ 네트워크 오류: {str(e)}")
        return False

async def test_advanced_search():
    """고급 검색 테스트 (가격 필터링, 정렬 등)"""
    print("\n🎯 고급 검색 기능 테스트")
    print("=" * 50)
    
    # 가격대별 검색 테스트
    test_cases = [
        {"query": "커피 드립백", "sort": "asc", "display": 10},
        {"query": "독서 램프", "sort": "dsc", "display": 5},
        {"query": "여행 가방", "sort": "sim", "display": 3}
    ]
    
    for case in test_cases:
        print(f"🔎 Testing: {case['query']} (sort: {case['sort']}, display: {case['display']})")
        
        url = "https://openapi.naver.com/v1/search/shop.json"
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        
        params = {
            "query": case["query"],
            "display": case["display"],
            "start": 1,
            "sort": case["sort"]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("items", [])
                        
                        print(f"   ✅ Found {len(items)} products")
                        
                        if items:
                            prices = [int(item.get("lprice", 0)) for item in items if item.get("lprice")]
                            if prices:
                                print(f"   💰 Price range: {min(prices):,}원 ~ {max(prices):,}원")
                                
                                # 정렬 확인
                                if case["sort"] == "asc" and len(prices) > 1:
                                    if prices == sorted(prices):
                                        print("   ✅ 가격 오름차순 정렬 확인")
                                    else:
                                        print("   ⚠️ 가격 정렬이 예상과 다름")
                                
                                # 샘플 출력
                                print("   Sample products:")
                                for item in items[:2]:
                                    title = item.get("title", "").replace("<b>", "").replace("</b>", "")
                                    print(f"     - {title[:40]}... ({int(item.get('lprice', 0)):,}원)")
                        print()
                    else:
                        print(f"   ❌ Error {response.status}")
                        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            
async def test_error_handling():
    """에러 처리 테스트"""
    print("\n🛡️ 에러 처리 테스트")
    print("=" * 50)
    
    # 잘못된 API 키 테스트
    print("1. 잘못된 API 키 테스트")
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": "invalid_id",
        "X-Naver-Client-Secret": "invalid_secret"
    }
    params = {"query": "test", "display": 1}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=5)) as response:
                print(f"   Status: {response.status}")
                if response.status == 401:
                    print("   ✅ 인증 실패 에러 정상 처리됨")
                else:
                    print(f"   ⚠️ 예상과 다른 응답: {response.status}")
    except Exception as e:
        print(f"   ❌ 네트워크 오류: {str(e)}")
    
    print()
    
    # 빈 검색어 테스트
    print("2. 빈 검색어 테스트")
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": "", "display": 1}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=5)) as response:
                print(f"   Status: {response.status}")
                if response.status == 400:
                    print("   ✅ 잘못된 요청 에러 정상 처리됨")
                else:
                    error_text = await response.text()
                    print(f"   ⚠️ 예상과 다른 응답: {response.status} - {error_text}")
    except Exception as e:
        print(f"   ❌ 네트워크 오류: {str(e)}")

async def main():
    """메인 테스트 실행"""
    print("🧪 네이버쇼핑 API 종합 테스트")
    print("=" * 60)
    print()
    
    # 1. 기본 연결 테스트
    basic_success = await test_naver_api_basic()
    
    if basic_success:
        # 2. 고급 기능 테스트
        await test_advanced_search()
        
        # 3. 에러 처리 테스트
        await test_error_handling()
        
        print("\n✅ 모든 테스트 완료!")
        print("💡 네이버쇼핑 API가 정상적으로 작동합니다.")
    else:
        print("\n❌ 기본 연결 테스트 실패")
        print("💡 네이버 개발자센터에서 API 키 설정을 확인하세요.")

if __name__ == "__main__":
    asyncio.run(main())