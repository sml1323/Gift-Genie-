#!/usr/bin/env python3
"""
Debug API response to see exact structure
"""

import asyncio
import aiohttp
import json

async def debug_api_response():
    """Debug API response structure"""
    
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
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/api/v1/recommendations/basic",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    print("🔍 Full API Response:")
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                    
                    print("\n📊 First Recommendation Structure:")
                    if data.get('recommendations'):
                        rec = data['recommendations'][0]
                        print(f"Available keys: {list(rec.keys())}")
                        for key, value in rec.items():
                            print(f"  {key}: {value}")
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Error: {response.status}")
                    print(f"Response: {error_text}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_api_response())