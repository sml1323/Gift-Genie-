#!/usr/bin/env python3
"""
Debug Naver search functionality
"""

import asyncio
import sys
import os

# Add backend path
sys.path.insert(0, '/home/eslway/work/Gift-Genie-/backend')

async def debug_naver_search():
    """Debug Naver search directly"""
    print("🔍 Debugging Naver Search Functionality")
    print("=" * 50)
    
    try:
        from services.ai.naver_recommendation_engine import NaverShoppingClient
        
        # Create client with empty credentials (should use simulation)
        client = NaverShoppingClient("", "")
        print(f"Naver client enabled: {client.enabled}")
        print()
        
        # Test search
        keywords = ["게임", "기술"]
        budget_max = 260000
        
        print(f"Testing search with:")
        print(f"  Keywords: {keywords}")
        print(f"  Budget max: ₩{budget_max:,}")
        print()
        
        # Call search_products directly
        products = await client.search_products(keywords, budget_max, display=5)
        
        print(f"Search results: {len(products)} products")
        print()
        
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.title}")
            print(f"   Price: ₩{product.lprice:,}")
            print(f"   Link: {product.link}")
            print(f"   Mall: {product.mallName}")
            print()
            
        if len(products) > 0:
            print("✅ Naver search simulation working correctly!")
            
            # Now test conversion to search results
            from services.ai.naver_recommendation_engine import NaverGiftRecommendationEngine
            engine = NaverGiftRecommendationEngine("", "", "")
            
            search_results = engine._convert_naver_to_search_results(products)
            print(f"\n📋 Converted to {len(search_results)} search results:")
            
            for i, result in enumerate(search_results, 1):
                print(f"{i}. {result.title}")
                print(f"   Price: {result.price} {result.currency}")
                print(f"   Display: {result.price_display}")
                print()
                
        else:
            print("❌ No products returned from search")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_naver_search())