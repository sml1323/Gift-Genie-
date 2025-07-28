#!/usr/bin/env python3
"""
Debug script for Naver integration issue
"""

import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_naver_integration():
    """Debug the Naver integration step by step"""
    
    # Mock request data with all required fields
    class MockRequest:
        def __init__(self):
            self.recipient_age = 25
            self.recipient_gender = '여성'
            self.relationship = '친구'
            self.budget_min = 50000
            self.budget_max = 150000
            self.currency = 'KRW'
            self.interests = ['커피']
            self.occasion = '생일'
            self.personal_style = '미니멀리스트'
            self.restrictions = []
    
    request = MockRequest()
    
    print("=== DEBUG: Naver Integration ===")
    print(f"Budget: ₩{request.budget_min:,} - ₩{request.budget_max:,}")
    print(f"Interests: {request.interests}")
    print()
    
    try:
        from services.ai.naver_recommendation_engine import NaverGiftRecommendationEngine
        
        engine = NaverGiftRecommendationEngine('test-key')
        
        print("Step 1: Testing AI recommendations...")
        ai_response = await engine.ai_engine.generate_recommendations(request)
        print(f"  AI Success: {ai_response.success}")
        print(f"  AI Recommendations: {len(ai_response.recommendations)}")
        
        # If AI fails, test fallback
        if not ai_response.success:
            print("  -> AI failed, testing fallback...")
            ai_response = await engine._create_fallback_ai_recommendations(request)
            print(f"  Fallback Success: {ai_response.success}")
            print(f"  Fallback Recommendations: {len(ai_response.recommendations)}")
        
        for i, rec in enumerate(ai_response.recommendations[:3]):
            print(f"    {i+1}. {rec.title}")
        print()
        
        print("Step 2: Testing Naver searches...")
        all_products = []
        
        for i, ai_rec in enumerate(ai_response.recommendations[:3]):
            # Extract keywords
            keywords = engine._extract_search_keywords_from_ai_rec(ai_rec, request)
            print(f"  AI Rec {i+1}: '{ai_rec.title}' -> Keywords: {keywords}")
            
            # Search products
            products = await engine.naver_client.search_products(
                keywords, request.budget_min, request.budget_max, display=5, sort="asc"
            )
            
            print(f"    -> Found {len(products)} products")
            for j, product in enumerate(products[:2]):
                print(f"      {j+1}. {product.title[:40]}... - ₩{product.lprice:,}")
                print(f"         Image: {product.image}")
            
            # Set AI recommendation index
            for product in products:
                product.ai_recommendation_index = i
                all_products.append(product)
        
        print(f"\nStep 3: Total products collected: {len(all_products)}")
        
        print("Step 4: Testing Smart Integration...")
        enhanced_recs = await engine._smart_integrate_recommendations(
            ai_response.recommendations, all_products, request
        )
        
        print(f"  Enhanced recommendations: {len(enhanced_recs)}")
        for i, rec in enumerate(enhanced_recs):
            print(f"    {i+1}. {rec.title}")
            print(f"       Image: {rec.image_url}")
            print(f"       Price: ₩{rec.estimated_price:,}")
            print(f"       Link: {rec.purchase_link}")
        
        print("\n=== INTEGRATION SUCCESSFUL ===")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_naver_integration())