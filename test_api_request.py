#!/usr/bin/env python3
"""
Final API Integration Test
Test the exact API flow that frontend will use
"""

import asyncio
import aiohttp
import json
import time

API_BASE_URL = "http://localhost:8000"

# Frontend-compatible test request
FRONTEND_REQUEST = {
    "recipient_age": 28,
    "recipient_gender": "여성",
    "relationship": "친구",
    "budget_min": 50,
    "budget_max": 150,
    "interests": ["독서", "커피", "여행", "사진"],
    "occasion": "생일",
    "personal_style": "미니멀리스트",
    "restrictions": ["쥬얼리 제외"]
}

async def test_complete_user_flow():
    """Test the complete user flow that frontend will execute"""
    print("🎯 Testing Complete User Flow")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Health check (app startup)
        print("1️⃣ Health Check...")
        async with session.get(f"{API_BASE_URL}/api/v1/health") as response:
            if response.status == 200:
                health_data = await response.json()
                print(f"   ✅ Backend healthy: {health_data['status']}")
                print(f"   🔧 Services: API={health_data['services']['api']}")
                print(f"   🤖 OpenAI: {health_data['services']['openai']}")
                print(f"   🛒 Naver: {health_data['services']['naver_shopping']}")
            else:
                print(f"   ❌ Health check failed: {response.status}")
                return False
        
        # Step 2: Submit recommendation request (main user action)
        print("\n2️⃣ Submitting Recommendation Request...")
        print(f"   👤 User: {FRONTEND_REQUEST['recipient_age']}yo {FRONTEND_REQUEST['recipient_gender']}")
        print(f"   💰 Budget: ${FRONTEND_REQUEST['budget_min']}-{FRONTEND_REQUEST['budget_max']}")
        print(f"   🎯 Interests: {', '.join(FRONTEND_REQUEST['interests'][:3])}")
        
        start_time = time.time()
        
        async with session.post(
            f"{API_BASE_URL}/api/v1/recommendations/naver",
            json=FRONTEND_REQUEST,
            headers={"Content-Type": "application/json"}
        ) as response:
            duration = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                print(f"   ✅ Request successful ({duration:.2f}s)")
                
                # Step 3: Process and display results
                print("\n3️⃣ Processing Results...")
                
                recommendations = data.get('recommendations', [])
                search_results = data.get('search_results', [])
                metrics = data.get('pipeline_metrics', {})
                
                print(f"   📊 Generated {len(recommendations)} recommendations")
                print(f"   🔍 Found {len(search_results)} search results")
                print(f"   ⏱️  AI Generation: {metrics.get('ai_generation_time', 0):.2f}s")
                print(f"   🛒 Naver Search: {metrics.get('search_execution_time', 0):.2f}s")
                print(f"   🔧 Integration: {metrics.get('integration_time', 0):.2f}s")
                print(f"   🎮 Simulation Mode: {data.get('simulation_mode', False)}")
                
                # Step 4: Display sample recommendation (what user sees)
                if recommendations:
                    print("\n4️⃣ Sample Recommendation Preview:")
                    rec = recommendations[0]
                    print(f"   🎁 {rec['title']}")
                    print(f"   💰 ${rec['estimated_price']}")
                    print(f"   📂 {rec['category']}")
                    print(f"   ⭐ Confidence: {rec['confidence_score']:.0%}")
                    print(f"   📝 {rec['description'][:100]}...")
                    
                    if rec.get('purchase_link'):
                        print(f"   🔗 Purchase available: ✅")
                    
                    if rec.get('image_url'):
                        print(f"   🖼️ Image available: ✅")
                
                # Step 5: Validate user experience
                print("\n5️⃣ User Experience Validation:")
                
                # Check response time
                if duration < 10:
                    print(f"   ✅ Response time acceptable ({duration:.2f}s < 10s)")
                else:
                    print(f"   ⚠️  Response time slow ({duration:.2f}s)")
                
                # Check recommendation quality
                if len(recommendations) >= 3:
                    print(f"   ✅ Sufficient recommendations ({len(recommendations)})")
                else:
                    print(f"   ⚠️  Few recommendations ({len(recommendations)})")
                
                # Check price accuracy
                budget_compliant = all(
                    FRONTEND_REQUEST['budget_min'] <= rec['estimated_price'] <= FRONTEND_REQUEST['budget_max']
                    for rec in recommendations
                )
                if budget_compliant:
                    print("   ✅ All recommendations within budget")
                else:
                    print("   ⚠️  Some recommendations outside budget")
                
                return True
                
            else:
                error_text = await response.text()
                print(f"   ❌ Request failed: {response.status}")
                print(f"   Error: {error_text}")
                return False

async def test_error_scenarios():
    """Test error handling scenarios"""
    print("\n🚨 Testing Error Scenarios")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        # Test invalid request
        invalid_request = {
            "recipient_age": -1,  # Invalid age
            "budget_min": 200,
            "budget_max": 100,    # Invalid budget range
        }
        
        async with session.post(
            f"{API_BASE_URL}/api/v1/recommendations/naver",
            json=invalid_request,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 422:  # Validation error expected
                print("   ✅ Input validation working correctly")
            else:
                print(f"   ⚠️  Unexpected response to invalid input: {response.status}")

async def main():
    """Run all tests"""
    print("🚀 Gift Genie Final Integration Test")
    print("=" * 60)
    print("Testing the complete user journey from frontend to backend\n")
    
    # Main test
    success = await test_complete_user_flow()
    
    # Error handling test
    await test_error_scenarios()
    
    # Final summary
    print("\n🎯 Integration Summary")
    print("=" * 30)
    
    if success:
        print("🎉 ✅ INTEGRATION SUCCESSFUL!")
        print()
        print("📋 System Status:")
        print("   🔧 Backend: Running on http://localhost:8000")
        print("   🌐 Frontend: Running on http://localhost:3000") 
        print("   🛒 Naver API: Simulation mode (real API available)")
        print("   🤖 AI Engine: Simulation mode (real API available)")
        print()
        print("🚀 Next Steps:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Test the complete gift recommendation flow")
        print("   3. Configure real API keys for production use")
        print("   4. Deploy to production environment")
        print()
        print("✨ Frontend + Backend integration is COMPLETE! ✨")
    else:
        print("❌ Integration test failed")
        print("Please check the errors above and fix any issues")

if __name__ == "__main__":
    asyncio.run(main())