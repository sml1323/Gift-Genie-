#!/usr/bin/env python3
"""
Test KRW currency support in Gift Genie API
"""

import asyncio
import aiohttp
import json

async def test_krw_api():
    """Test KRW currency support"""
    
    # Test request with KRW
    request_data = {
        "recipient_age": 28,
        "recipient_gender": "여성", 
        "relationship": "친구",
        "budget_min": 65000,
        "budget_max": 195000,
        "currency": "KRW",
        "interests": ["독서", "커피"],
        "occasion": "생일"
    }
    
    print("🧪 Testing KRW Currency Support")
    print("=" * 50)
    print(f"Request: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/api/v1/recommendations/basic",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"✅ Success! Status: {response.status}")
                    print(f"Request ID: {data['request_id']}")
                    print(f"Processing time: {data['total_processing_time']:.2f}s")
                    print()
                    
                    # Display recommendations with currency info
                    print("📝 Recommendations:")
                    for i, rec in enumerate(data['recommendations'], 1):
                        print(f"{i}. {rec['title']}")
                        print(f"   Price: {rec['price_display']} ({rec['currency']})")
                        print(f"   Raw price: {rec['estimated_price']}")
                        print(f"   Category: {rec['category']}")
                        print()
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Error: {response.status}")
                    print(f"Response: {error_text}")
                    
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_krw_api())