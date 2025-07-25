#!/usr/bin/env python3
"""
실제 Apify API 사용 예시
Gift Genie에서 상품 정보를 실제로 스크래핑하는 방법
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any

class RealApifyClient:
    """실제 Apify API 클라이언트 예시"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.apify.com/v2"
    
    async def scrape_product_page(self, url: str) -> Dict[str, Any]:
        """실제 상품 페이지 스크래핑"""
        
        # 1. Apify Actor 실행 (예: Web Scraper)
        actor_id = "apify/web-scraper"  # 범용 웹 스크래퍼
        
        # 2. 스크래핑 설정
        scraping_config = {
            "startUrls": [{"url": url}],
            "pageFunction": """
                async function pageFunction(context) {
                    const { page, request } = context;
                    
                    // 상품 정보 추출
                    const title = await page.$eval('h1, .product-title, [data-testid="product-title"]', 
                        el => el.textContent.trim()).catch(() => 'Unknown Product');
                    
                    const price = await page.$eval('.price, .product-price, [data-testid="price"]', 
                        el => el.textContent.trim()).catch(() => null);
                    
                    const image = await page.$eval('img[src*="product"], .product-image img, [data-testid="product-image"]', 
                        el => el.src).catch(() => null);
                    
                    const rating = await page.$eval('.rating, .stars, [data-testid="rating"]', 
                        el => el.textContent.trim()).catch(() => null);
                    
                    return {
                        url: request.url,
                        title,
                        price,
                        image,
                        rating,
                        scrapedAt: new Date().toISOString()
                    };
                }
            """
        }
        
        # 3. Apify 작업 실행
        async with aiohttp.ClientSession() as session:
            # Actor 실행 요청
            async with session.post(
                f"{self.base_url}/acts/{actor_id}/runs",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=scraping_config
            ) as response:
                run_data = await response.json()
                run_id = run_data["data"]["id"]
            
            # 4. 완료 대기 (폴링)
            for _ in range(30):  # 최대 5분 대기
                await asyncio.sleep(10)
                
                async with session.get(
                    f"{self.base_url}/actor-runs/{run_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    run_status = await response.json()
                    
                    if run_status["data"]["status"] == "SUCCEEDED":
                        # 5. 결과 다운로드
                        async with session.get(
                            f"{self.base_url}/actor-runs/{run_id}/dataset/items",
                            headers={"Authorization": f"Bearer {self.api_key}"}
                        ) as response:
                            results = await response.json()
                            return results[0] if results else {}
            
            return {}  # 타임아웃

# 사용 예시
async def example_usage():
    """실제 사용 예시"""
    # .env 파일에서 API 키를 로드하세요
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    apify = RealApifyClient(os.getenv("APIFY_API_KEY"))
    
    # 실제 상품 페이지 스크래핑
    result = await apify.scrape_product_page("https://www.amazon.com/dp/B08N5WRWNW")
    
    print("스크래핑 결과:")
    print(f"제품명: {result.get('title')}")
    print(f"가격: {result.get('price')}")
    print(f"이미지: {result.get('image')}")
    print(f"평점: {result.get('rating')}")

if __name__ == "__main__":
    asyncio.run(example_usage())