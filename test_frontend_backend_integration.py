#!/usr/bin/env python3
"""
Frontend-Backend Integration Test
Test the complete frontend-backend integration with real API calls
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

# Test request payload (matches frontend format)
TEST_REQUEST = {
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

async def test_health_endpoint():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/api/v1/health") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status}")
                return False

async def test_naver_endpoint():
    """Test Naver Shopping API endpoint"""
    print("\n🛒 Testing Naver Shopping endpoint...")
    
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        
        async with session.post(
            f"{API_BASE_URL}/api/v1/recommendations/naver",
            json=TEST_REQUEST,
            headers={"Content-Type": "application/json"}
        ) as response:
            duration = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                print(f"✅ Naver API test passed ({duration:.2f}s)")
                print(f"   Request ID: {data.get('request_id', 'N/A')}")
                print(f"   Recommendations: {len(data.get('recommendations', []))}")
                print(f"   Search results: {len(data.get('search_results', []))}")
                print(f"   Simulation mode: {data.get('simulation_mode', 'N/A')}")
                
                # Show first recommendation
                if data.get('recommendations'):
                    rec = data['recommendations'][0]
                    print(f"   Sample: {rec.get('title', 'N/A')} - ${rec.get('estimated_price', 'N/A')}")
                
                return True
            else:
                error_text = await response.text()
                print(f"❌ Naver API test failed: {response.status}")
                print(f"   Error: {error_text}")
                return False

async def test_enhanced_endpoint():
    """Test enhanced endpoint (frontend compatibility)"""
    print("\n⚡ Testing enhanced endpoint (frontend compatibility)...")
    
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        
        async with session.post(
            f"{API_BASE_URL}/api/v1/recommendations/enhanced",
            json=TEST_REQUEST,
            headers={"Content-Type": "application/json"}
        ) as response:
            duration = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                print(f"✅ Enhanced API test passed ({duration:.2f}s)")
                print(f"   Request ID: {data.get('request_id', 'N/A')}")
                print(f"   Recommendations: {len(data.get('recommendations', []))}")
                print(f"   MCP enabled: {data.get('mcp_enabled', 'N/A')}")
                return True
            else:
                error_text = await response.text()
                print(f"❌ Enhanced API test failed: {response.status}")
                print(f"   Error: {error_text}")
                return False

async def test_basic_endpoint():
    """Test basic recommendations endpoint"""
    print("\n🤖 Testing basic recommendations endpoint...")
    
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        
        async with session.post(
            f"{API_BASE_URL}/api/v1/recommendations/basic",
            json=TEST_REQUEST,
            headers={"Content-Type": "application/json"}
        ) as response:
            duration = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                print(f"✅ Basic API test passed ({duration:.2f}s)")
                print(f"   Request ID: {data.get('request_id', 'N/A')}")
                print(f"   Recommendations: {len(data.get('recommendations', []))}")
                return True
            else:
                error_text = await response.text()
                print(f"❌ Basic API test failed: {response.status}")
                print(f"   Error: {error_text}")
                return False

async def test_frontend_integration():
    """Test the exact flow that frontend will use"""
    print("\n🌐 Testing frontend integration flow...")
    
    # This simulates the exact API call that frontend will make
    frontend_request = TEST_REQUEST.copy()
    
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        
        # Primary endpoint (what updated frontend will call)
        async with session.post(
            f"{API_BASE_URL}/api/v1/recommendations/naver",
            json=frontend_request,
            headers={"Content-Type": "application/json"}
        ) as response:
            duration = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                print(f"✅ Frontend integration test passed ({duration:.2f}s)")
                
                # Validate response structure
                required_fields = ['request_id', 'recommendations', 'search_results', 'pipeline_metrics']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"⚠️  Warning: Missing fields in response: {missing_fields}")
                else:
                    print("✅ Response structure is valid")
                
                # Validate recommendations
                if data.get('recommendations'):
                    rec = data['recommendations'][0]
                    rec_fields = ['title', 'description', 'category', 'estimated_price', 'reasoning']
                    missing_rec_fields = [field for field in rec_fields if field not in rec]
                    
                    if missing_rec_fields:
                        print(f"⚠️  Warning: Missing recommendation fields: {missing_rec_fields}")
                    else:
                        print("✅ Recommendation structure is valid")
                
                return True, data
            else:
                error_text = await response.text()
                print(f"❌ Frontend integration test failed: {response.status}")
                print(f"   Error: {error_text}")
                return False, None

async def main():
    """Run all integration tests"""
    print("🧪 Gift Genie Frontend-Backend Integration Test")
    print("=" * 60)
    
    # Test sequence
    tests = [
        ("Health Check", test_health_endpoint),
        ("Naver API", test_naver_endpoint),
        ("Enhanced API", test_enhanced_endpoint),
        ("Basic API", test_basic_endpoint),
        ("Frontend Integration", lambda: test_frontend_integration())
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if test_name == "Frontend Integration":
                success, data = await test_func()
            else:
                success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Frontend-Backend integration is ready!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())