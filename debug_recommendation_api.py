#!/usr/bin/env python3
"""
Debug script to test recommendation API and identify the exact issue
"""

import asyncio
import aiohttp
import json

async def test_recommendation_api():
    """Test the recommendation API and print detailed response"""
    
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
    
    url = "http://localhost:8000/api/v1/recommendations/naver"
    
    print("🔍 Testing Naver Recommendations API")
    print(f"Request: {json.dumps(test_request, ensure_ascii=False, indent=2)}")
    print(f"URL: {url}")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=test_request,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                print(f"Status Code: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"\n✅ SUCCESS - API Response:")
                    print(f"Request ID: {data.get('request_id')}")
                    print(f"Success: {data.get('success')}")
                    print(f"Total Processing Time: {data.get('total_processing_time')}s")
                    print(f"Simulation Mode: {data.get('simulation_mode')}")
                    
                    # Check recommendations
                    recommendations = data.get('recommendations', [])
                    print(f"\n🎁 Recommendations: {len(recommendations)} items")
                    for i, rec in enumerate(recommendations):
                        print(f"  {i+1}. {rec.get('title')}")
                        print(f"     Price: {rec.get('price_display', rec.get('estimated_price'))}")
                        print(f"     Category: {rec.get('category')}")
                        print(f"     Confidence: {rec.get('confidence_score', 0):.2f}")
                    
                    # Check search results
                    search_results = data.get('search_results', [])
                    print(f"\n🔍 Search Results: {len(search_results)} items")
                    for i, result in enumerate(search_results[:3]):
                        print(f"  {i+1}. {result.get('title')}")
                        print(f"     Price: {result.get('price_display', result.get('price'))}")
                        print(f"     Domain: {result.get('domain')}")
                    
                    # Check pipeline metrics
                    metrics = data.get('pipeline_metrics', {})
                    print(f"\n📊 Pipeline Metrics:")
                    print(f"  AI Generation: {metrics.get('ai_generation_time', 0):.2f}s")
                    print(f"  Search Execution: {metrics.get('search_execution_time', 0):.2f}s")
                    print(f"  Integration: {metrics.get('integration_time', 0):.2f}s")
                    print(f"  Search Results Count: {metrics.get('search_results_count', 0)}")
                    
                    # Save response for inspection
                    with open('/tmp/api_response.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"\n💾 Full response saved to /tmp/api_response.json")
                    
                    return data
                    
                else:
                    error_text = await response.text()
                    print(f"\n❌ ERROR - Status {response.status}")
                    print(f"Response: {error_text}")
                    return None
                    
    except Exception as e:
        print(f"\n💥 EXCEPTION: {e}")
        import traceback
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    result = asyncio.run(test_recommendation_api())
    
    if result:
        print("\n" + "=" * 60)
        print("✅ API TEST SUCCESSFUL")
        
        # Check the key fields that frontend expects
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"✅ Found {len(recommendations)} recommendations")
            print("✅ Frontend should display these recommendations")
        else:
            print("❌ No recommendations found - this would cause empty left section")
            
        search_results = result.get('search_results', [])
        if search_results:
            print(f"✅ Found {len(search_results)} search results")
            print("✅ Frontend should display these in right section")
        else:
            print("❌ No search results found")
            
    else:
        print("\n" + "=" * 60)
        print("❌ API TEST FAILED")
        print("This explains why the frontend left section is empty!")