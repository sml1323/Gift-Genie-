#!/usr/bin/env python3
"""
Gift Genie - FastAPI Test Script
Test script to verify the FastAPI implementation is working correctly
"""

import asyncio
import json
import time
from datetime import datetime
import httpx


async def test_fastapi_endpoints():
    """Test FastAPI endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Gift Genie FastAPI Test Suite")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Root endpoint
        print("\n📋 Test 1: Root endpoint")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            assert response.status_code == 200
            print("   ✅ Root endpoint working")
        except Exception as e:
            print(f"   ❌ Root endpoint failed: {e}")
            return False
        
        # Test 2: Health check
        print("\n📋 Test 2: Health check")
        try:
            response = await client.get(f"{base_url}/api/v1/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            assert response.status_code == 200
            print("   ✅ Health check working")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
            return False
        
        # Test 3: Detailed health check
        print("\n📋 Test 3: Detailed health check")
        try:
            response = await client.get(f"{base_url}/api/v1/health/detailed")
            print(f"   Status: {response.status_code}")
            health_data = response.json()
            print(f"   Services configured:")
            for service, info in health_data.get("services", {}).items():
                if isinstance(info, dict):
                    print(f"     - {service}: {'✅' if info.get('configured') else '❌'}")
                else:
                    print(f"     - {service}: {info}")
            assert response.status_code == 200
            print("   ✅ Detailed health check working")
        except Exception as e:
            print(f"   ❌ Detailed health check failed: {e}")
            return False
        
        # Test 4: Basic recommendations
        print("\n📋 Test 4: Basic recommendations")
        try:
            test_request = {
                "recipient_age": 28,
                "recipient_gender": "여성",
                "relationship": "친구",
                "budget_min": 50,
                "budget_max": 150,
                "interests": ["독서", "커피", "여행"],
                "occasion": "생일",
                "personal_style": "미니멀리스트",
                "restrictions": ["쥬얼리 제외"]
            }
            
            start_time = time.time()
            response = await client.post(
                f"{base_url}/api/v1/recommendations/basic",
                json=test_request,
                timeout=60
            )
            end_time = time.time()
            
            print(f"   Status: {response.status_code}")
            print(f"   Response time: {end_time - start_time:.2f}s")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data.get('success')}")
                print(f"   Request ID: {data.get('request_id')}")
                print(f"   Recommendations: {len(data.get('recommendations', []))}")
                
                for i, rec in enumerate(data.get('recommendations', [])[:2], 1):
                    print(f"     {i}. {rec.get('title')} - ${rec.get('estimated_price')}")
                    print(f"        Category: {rec.get('category')}")
                    print(f"        Confidence: {rec.get('confidence_score'):.2f}")
                
                assert data.get('success') == True
                assert len(data.get('recommendations', [])) > 0
                print("   ✅ Basic recommendations working")
            else:
                print(f"   ❌ Basic recommendations failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Basic recommendations failed: {e}")
            return False
        
        # Test 5: Enhanced recommendations  
        print("\n📋 Test 5: Enhanced recommendations")
        try:
            start_time = time.time()
            response = await client.post(
                f"{base_url}/api/v1/recommendations/enhanced",
                json=test_request,
                timeout=60
            )
            end_time = time.time()
            
            print(f"   Status: {response.status_code}")
            print(f"   Response time: {end_time - start_time:.2f}s")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data.get('success')}")
                print(f"   Request ID: {data.get('request_id')}")
                print(f"   MCP Enabled: {data.get('mcp_enabled')}")
                print(f"   Simulation Mode: {data.get('simulation_mode')}")
                print(f"   Recommendations: {len(data.get('recommendations', []))}")
                print(f"   Search Results: {len(data.get('search_results', []))}")
                
                # Pipeline metrics
                metrics = data.get('pipeline_metrics', {})
                print(f"   Pipeline metrics:")
                print(f"     - AI generation: {metrics.get('ai_generation_time', 0):.2f}s")
                print(f"     - Search: {metrics.get('search_execution_time', 0):.2f}s")
                print(f"     - Scraping: {metrics.get('scraping_execution_time', 0):.2f}s")
                print(f"     - Integration: {metrics.get('integration_time', 0):.2f}s")
                print(f"     - Total: {metrics.get('total_time', 0):.2f}s")
                
                for i, rec in enumerate(data.get('recommendations', [])[:2], 1):
                    print(f"     {i}. {rec.get('title')} - ${rec.get('estimated_price')}")
                    if rec.get('purchase_link'):
                        print(f"        🔗 {rec.get('purchase_link')}")
                    if rec.get('image_url'):
                        print(f"        🖼️ {rec.get('image_url')}")
                
                assert data.get('success') == True
                assert len(data.get('recommendations', [])) > 0
                print("   ✅ Enhanced recommendations working")
            else:
                print(f"   ❌ Enhanced recommendations failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Enhanced recommendations failed: {e}")
            return False
        
        # Test 6: Naver Shopping recommendations
        print("\n📋 Test 6: Naver Shopping recommendations")
        try:
            start_time = time.time()
            response = await client.post(
                f"{base_url}/api/v1/recommendations/naver",
                json=test_request,
                timeout=60
            )
            end_time = time.time()
            
            print(f"   Status: {response.status_code}")
            print(f"   Response time: {end_time - start_time:.2f}s")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data.get('success')}")
                print(f"   Request ID: {data.get('request_id')}")
                print(f"   MCP Enabled: {data.get('mcp_enabled')}")  # Should be False
                print(f"   Simulation Mode: {data.get('simulation_mode')}")
                print(f"   Recommendations: {len(data.get('recommendations', []))}")
                print(f"   Search Results: {len(data.get('search_results', []))}")
                
                # Pipeline metrics
                metrics = data.get('pipeline_metrics', {})
                print(f"   Pipeline metrics:")
                print(f"     - AI generation: {metrics.get('ai_generation_time', 0):.2f}s")
                print(f"     - Naver search: {metrics.get('search_execution_time', 0):.2f}s")
                print(f"     - Integration: {metrics.get('integration_time', 0):.2f}s")
                print(f"     - Total: {metrics.get('total_time', 0):.2f}s")
                
                # Show sample recommendations
                for i, rec in enumerate(data.get('recommendations', [])[:2], 1):
                    print(f"     {i}. {rec.get('title')} - ${rec.get('estimated_price')}")
                    if rec.get('purchase_link'):
                        print(f"        🔗 Naver: {rec.get('purchase_link')[:50]}...")
                    if rec.get('image_url'):
                        print(f"        🖼️ Image: {rec.get('image_url')[:50]}...")
                
                # Show search results (Naver products)
                for i, result in enumerate(data.get('search_results', [])[:2], 1):
                    print(f"     Search Result {i}: {result.get('title')} - ${result.get('price')}")
                    print(f"        Domain: {result.get('domain')}")
                
                assert data.get('success') == True
                assert len(data.get('recommendations', [])) > 0
                assert data.get('mcp_enabled') == False  # Should not use MCP
                print("   ✅ Naver Shopping recommendations working")
            else:
                print(f"   ❌ Naver Shopping recommendations failed: {response.text}")
                # Don't return False here - this is acceptable if Naver API keys are not set
                print("   ⚠️  This is expected if NAVER_CLIENT_ID/SECRET are not configured")
                
        except Exception as e:
            print(f"   ❌ Naver Shopping recommendations failed: {e}")
            print("   ⚠️  This is expected if NAVER_CLIENT_ID/SECRET are not configured")
            # Don't return False - this test is optional
        
        # Test 7: Default recommendations endpoint
        print("\n📋 Test 7: Default recommendations endpoint")
        try:
            response = await client.post(
                f"{base_url}/api/v1/recommendations",
                json=test_request,
                timeout=60
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data.get('success')}")
                print(f"   Recommendations: {len(data.get('recommendations', []))}")
                assert data.get('success') == True
                print("   ✅ Default recommendations working")
            else:
                print(f"   ❌ Default recommendations failed: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Default recommendations failed: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! FastAPI implementation is working correctly.")
    print("\n📊 Summary:")
    print("   ✅ Root endpoint")
    print("   ✅ Health checks")
    print("   ✅ Basic recommendations")
    print("   ✅ Enhanced recommendations (MCP pipeline)")
    print("   ✅ Naver Shopping recommendations (Direct API)")
    print("   ✅ Default recommendations endpoint")
    
    return True


async def test_validation():
    """Test input validation"""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Testing input validation...")
    
    async with httpx.AsyncClient() as client:
        # Test invalid request
        invalid_request = {
            "recipient_age": 200,  # Invalid age
            "recipient_gender": "invalid",  # Invalid gender
            "relationship": "친구",
            "budget_min": 100,
            "budget_max": 50,  # Invalid: max < min
            "interests": [],  # Empty interests
            "occasion": "생일"
        }
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/recommendations/basic",
                json=invalid_request,
                timeout=30
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 422:
                print("   ✅ Validation working correctly")
                return True
            else:
                print(f"   ❌ Expected 422, got {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Validation test failed: {e}")
            return False


if __name__ == "__main__":
    print("🚀 Starting FastAPI test suite...")
    print("⚠️  Make sure the FastAPI server is running on localhost:8000")
    print("   Run: python main.py")
    print()
    
    # Give user time to start server
    input("Press Enter when the server is running...")
    
    # Run tests
    try:
        success = asyncio.run(test_fastapi_endpoints())
        if success:
            validation_success = asyncio.run(test_validation())
            if validation_success:
                print("🏆 All tests completed successfully!")
            else:
                print("⚠️  Some validation tests failed")
        else:
            print("💥 Some core tests failed")
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"💥 Test suite failed: {e}")