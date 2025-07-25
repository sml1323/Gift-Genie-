#!/usr/bin/env python3
"""
간단한 실제 스크래핑 테스트
실제 이미지 URL을 얻어보는 예시
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

async def simple_scrape_test(url: str):
    """간단한 스크래핑 테스트"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 제목 찾기
                    title_selectors = ['h1', '.product-title', '[data-testid="product-title"]', 'title']
                    title = "Unknown"
                    for selector in title_selectors:
                        element = soup.select_one(selector)
                        if element:
                            title = element.get_text().strip()[:100]
                            break
                    
                    # 이미지 찾기
                    img_selectors = [
                        'img[src*="product"]', 
                        '.product-image img', 
                        'img[alt*="product"]',
                        'meta[property="og:image"]'
                    ]
                    image_url = None
                    for selector in img_selectors:
                        element = soup.select_one(selector)
                        if element:
                            image_url = element.get('src') or element.get('content')
                            if image_url and image_url.startswith('http'):
                                break
                    
                    # 가격 찾기 (간단한 패턴)
                    price_text = soup.get_text()
                    price_match = re.search(r'[\$₩](\d+(?:,\d{3})*(?:\.\d{2})?)', price_text)
                    price = price_match.group(1) if price_match else None
                    
                    return {
                        'url': url,
                        'title': title,
                        'image': image_url,
                        'price': price,
                        'success': True
                    }
                else:
                    return {
                        'url': url,
                        'error': f'HTTP {response.status}',
                        'success': False
                    }
    except Exception as e:
        return {
            'url': url,
            'error': str(e),
            'success': False
        }

async def test_real_sites():
    """실제 사이트들 테스트"""
    test_urls = [
        "https://caffemuseo.co.kr/",
        "https://www.megacoffee.co.kr/",
        "https://www.amazon.com/dp/B08N5WRWNW",  # 아마존 예시
    ]
    
    print("🔍 실제 스크래핑 테스트 시작...")
    
    for url in test_urls:
        print(f"\n📄 테스트: {url}")
        result = await simple_scrape_test(url)
        
        if result['success']:
            print(f"✅ 제목: {result['title']}")
            print(f"🖼️  이미지: {result['image']}")
            print(f"💰 가격: {result['price']}")
        else:
            print(f"❌ 실패: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_real_sites())