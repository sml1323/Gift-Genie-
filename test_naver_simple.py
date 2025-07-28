#!/usr/bin/env python3
"""
Simple test for Naver API to catch errors
"""

import asyncio
import aiohttp
import json

async def simple_naver_test():
    """Simple test"""
    
    request_data = {
        "recipient_age": 25,
        "recipient_gender": "남성",
        "relationship": "친구", 
        "budget_min": 50000,
        "budget_max": 150000,
        "currency": "KRW",
        "interests": ["커피"],
        "occasion": "생일"
    }
    
    print("🧪 Simple Naver Test")
    print(json.dumps(request_data, ensure_ascii=False, indent=2))
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/api/v1/recommendations/naver",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                text = await response.text()
                print(f"Response status: {response.status}")
                print(f"Response length: {len(text)}")
                print()
                
                if response.status == 200:
                    data = json.loads(text)
                    print(f"Success: {data.get('success')}")
                    print(f"Error message: {data.get('error_message')}")
                    print(f"Search results: {len(data.get('search_results', []))}")
                    print(f"Simulation mode: {data.get('simulation_mode')}")
                    
                    if data.get('search_results'):
                        print("\nFirst search result:")
                        result = data['search_results'][0]
                        for key, value in result.items():
                            print(f"  {key}: {value}")
                else:
                    print(f"Error response: {text}")
                    
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(simple_naver_test())