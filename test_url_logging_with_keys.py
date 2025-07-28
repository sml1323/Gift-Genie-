#!/usr/bin/env python3
"""
Test URL logging for Naver API client with fake API keys to avoid simulation mode
"""

import asyncio
import sys
import os
import logging

# Add backend to path
sys.path.append('/home/eslway/work/Gift-Genie-/backend')

from services.ai.naver_recommendation_engine import NaverShoppingClient

# Set up logging to see the output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_url_logging_with_keys():
    """Test the URL logging functionality with fake API keys to bypass simulation mode"""
    print("🧪 Testing Naver API URL Logging with Fake Keys")
    print("=" * 50)
    
    # Create client with fake API keys to avoid simulation mode
    # This will cause the actual API call to fail, but we'll see the URL logging
    client = NaverShoppingClient("fake_client_id", "fake_client_secret")
    
    # Test search with typical parameters
    keywords = ["커피메이커", "원두"]
    budget_max_krw = 150000
    
    print(f"Testing search with keywords: {keywords}")
    print(f"Budget max: ₩{budget_max_krw:,}")
    print(f"Client enabled: {client.enabled}")
    print()
    
    try:
        # This should trigger the URL logging before the API call fails
        results = await client.search_products(
            keywords=keywords,
            budget_max_krw=budget_max_krw,
            display=5,
            sort="asc"
        )
        
        print(f"✅ Search completed successfully!")
        print(f"Found {len(results)} results")
        
        if results:
            print("\nFirst result:")
            result = results[0]
            print(f"  Title: {result.title}")
            print(f"  Price: ₩{result.lprice:,}")
            print(f"  Link: {result.link}")
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_url_logging_with_keys())