#!/usr/bin/env python3
"""
Test frontend-backend integration with the actual API flow
"""

import asyncio
import aiohttp
import json

async def test_full_integration():
    """Test the complete frontend-backend integration flow"""
    
    print("🔍 Testing Complete Frontend-Backend Integration")
    print("=" * 60)
    
    # Step 1: Test recommendation API (what frontend actually calls)
    test_request = {
        "recipient_age": 25,
        "recipient_gender": "여성",
        "relationship": "friend",
        "budget_min": 30000,
        "budget_max": 100000,
        "currency": "KRW",
        "interests": ["커피", "독서"],
        "occasion": "생일"
    }
    
    api_url = "http://localhost:8000/api/v1/recommendations/naver"
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📤 Calling API (simulating frontend request)...")
            async with session.post(
                api_url,
                json=test_request,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    print("✅ API Response Successful")
                    print(f"   Request ID: {data.get('request_id')}")
                    print(f"   Success: {data.get('success')}")
                    print(f"   Processing Time: {data.get('total_processing_time', 0):.2f}s")
                    
                    # Step 2: Simulate frontend sessionStorage.setItem()
                    print("\n📝 Simulating Frontend Data Storage...")
                    recommendations = data.get('recommendations', [])
                    search_results = data.get('search_results', [])
                    
                    if recommendations:
                        print(f"✅ Recommendations to store: {len(recommendations)} items")
                        print("   Left section will show:")
                        for i, rec in enumerate(recommendations):
                            print(f"     {i+1}. {rec.get('title', 'No title')[:50]}...")
                            print(f"        Price: {rec.get('price_display', 'No price')}")
                            print(f"        Category: {rec.get('category', 'No category')}")
                            print(f"        Confidence: {rec.get('confidence_score', 0):.2f}")
                    else:
                        print("❌ No recommendations to store - LEFT SECTION WILL BE EMPTY")
                    
                    if search_results:
                        print(f"\n✅ Search Results to store: {len(search_results)} items")
                        print("   Right section will show:")
                        for i, result in enumerate(search_results[:3]):
                            print(f"     {i+1}. {result.get('title', 'No title')[:50]}...")
                            print(f"        Price: {result.get('price_display', 'No price')}")
                            print(f"        Domain: {result.get('domain', 'No domain')}")
                    else:
                        print("❌ No search results to store - RIGHT SECTION WILL BE EMPTY")
                    
                    # Step 3: Simulate what frontend result page would see
                    print("\n🖥️  Simulating Frontend Result Page Rendering...")
                    print("   sessionStorage.getItem('giftRecommendations') would return:")
                    print(f"   - recommendations.length: {len(recommendations)}")
                    print(f"   - search_results.length: {len(search_results)}")
                    
                    if recommendations:
                        print("   ✅ Left section (🎁 추천 선물) will display recommendations")
                    else:
                        print("   ❌ Left section (🎁 추천 선물) will be empty")
                    
                    if search_results:
                        print("   ✅ Right section (🔍 발견한 상품들) will display search results")
                    else:
                        print("   ❌ Right section (🔍 발견한 상품들) will be empty")
                    
                    # Save complete response for inspection
                    with open('/tmp/frontend_integration_test.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print("\n💾 Complete response saved to /tmp/frontend_integration_test.json")
                    
                    return data
                    
                else:
                    error_text = await response.text()
                    print(f"❌ API Error - Status {response.status}")
                    print(f"Response: {error_text}")
                    return None
                    
    except Exception as e:
        print(f"💥 Integration Test Failed: {e}")
        import traceback
        print(traceback.format_exc())
        return None

async def main():
    result = await test_full_integration()
    
    print("\n" + "=" * 60)
    if result and result.get('recommendations'):
        print("🎉 INTEGRATION TEST SUCCESS!")
        print("✅ Backend is working correctly")
        print("✅ Frontend should now display left section properly")
        print("✅ The issue in the screenshot should be RESOLVED")
        print("\n💡 Next step: Refresh the frontend page and test manually")
    else:
        print("❌ INTEGRATION TEST FAILED!")
        print("The left section will still be empty")

if __name__ == "__main__":
    asyncio.run(main())