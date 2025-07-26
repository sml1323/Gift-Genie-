#!/usr/bin/env python3
"""
Real API Test - Testing with actual API keys
"""

import asyncio
import aiohttp
import json
import time

API_BASE_URL = "http://localhost:8000"

# Test request with realistic Korean user scenario
TEST_REQUEST = {
    "recipient_age": 25,
    "recipient_gender": "여성",
    "relationship": "친구", 
    "budget_min": 30,
    "budget_max": 80,
    "interests": ["커피", "독서", "미니멀"],
    "occasion": "생일",
    "personal_style": "미니멀리스트",
    "restrictions": []
}

async def test_real_api_performance():
    """Test real API performance and accuracy"""
    print("🔥 Real API Performance Test")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        print(f"📝 Test Request:")
        print(f"   Age: {TEST_REQUEST['recipient_age']}")
        print(f"   Gender: {TEST_REQUEST['recipient_gender']}")
        print(f"   Budget: ${TEST_REQUEST['budget_min']}-{TEST_REQUEST['budget_max']}")
        print(f"   Interests: {', '.join(TEST_REQUEST['interests'])}")
        
        start_time = time.time()
        
        async with session.post(
            f"{API_BASE_URL}/api/v1/recommendations/naver",
            json=TEST_REQUEST,
            headers={"Content-Type": "application/json"}
        ) as response:
            duration = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                
                print(f"\n⏱️ Performance Metrics:")
                print(f"   Total Time: {duration:.2f}s")
                print(f"   AI Generation: {data['pipeline_metrics']['ai_generation_time']:.2f}s")
                print(f"   Naver Search: {data['pipeline_metrics']['search_execution_time']:.2f}s") 
                print(f"   Integration: {data['pipeline_metrics']['integration_time']:.2f}s")
                print(f"   Simulation Mode: {data['simulation_mode']}")
                
                # Analyze recommendations
                recommendations = data.get('recommendations', [])
                search_results = data.get('search_results', [])
                
                print(f"\n📊 Quality Analysis:")
                print(f"   Recommendations: {len(recommendations)}")
                print(f"   Search Results: {len(search_results)}")
                
                # Budget compliance check
                budget_compliant = 0
                for rec in recommendations:
                    price = rec['estimated_price']
                    if TEST_REQUEST['budget_min'] <= price <= TEST_REQUEST['budget_max']:
                        budget_compliant += 1
                    print(f"   💰 {rec['title']}: ${price} ({'✅' if TEST_REQUEST['budget_min'] <= price <= TEST_REQUEST['budget_max'] else '❌'})")
                
                compliance_rate = (budget_compliant / len(recommendations)) * 100 if recommendations else 0
                print(f"   📈 Budget Compliance: {compliance_rate:.0f}%")
                
                # Show real products found
                if search_results:
                    print(f"\n🛒 Real Products Found:")
                    for i, product in enumerate(search_results[:3], 1):
                        print(f"   {i}. {product['title']}")
                        print(f"      💰 ${product.get('price', 'N/A')} on {product['domain']}")
                        if product.get('rating'):
                            print(f"      ⭐ {product['rating']}/5 ({product.get('review_count', 0)} reviews)")
                
                return duration < 10 and compliance_rate >= 80
            else:
                error_text = await response.text()
                print(f"❌ API Error: {response.status}")
                print(f"   {error_text}")
                return False

async def main():
    """Run real API test"""
    print("🚀 Gift Genie Real API Integration Test")
    print("=" * 60)
    
    success = await test_real_api_performance()
    
    print(f"\n🎯 Test Result:")
    if success:
        print("✅ Real API integration working optimally!")
        print("🎉 Ready for production use with actual Korean products")
    else:
        print("⚠️  Performance or accuracy needs improvement")
        print("💡 Consider optimizing AI prompts or budget matching logic")

if __name__ == "__main__":
    asyncio.run(main())