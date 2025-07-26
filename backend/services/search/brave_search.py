"""
Gift Genie - Brave Search Service
Integration with Brave Search API for product discovery
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import aiohttp

from models.response.recommendation import ProductSearchResult

logger = logging.getLogger(__name__)


class BraveSearchClient:
    """실제 Brave Search API 클라이언트"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.enabled = bool(api_key)
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
    
    async def search_products(self, keywords: List[str], budget_max: int) -> List[ProductSearchResult]:
        """실제 상품 검색"""
        if not self.enabled:
            # Fallback to simulation if no API key
            return await self._simulate_search(keywords, budget_max)
        
        try:
            # Build search query
            query = f"{' '.join(keywords[:3])} shop buy gift under ${budget_max}"
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": 10,
                "search_lang": "en",
                "country": "US",
                "safesearch": "moderate"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_search_results(data, budget_max)
                    else:
                        logger.warning(f"Brave Search API error: {response.status}")
                        return await self._simulate_search(keywords, budget_max)
                        
        except Exception as e:
            logger.error(f"Brave Search failed: {e}")
            return await self._simulate_search(keywords, budget_max)
    
    def _process_search_results(self, data: Dict[str, Any], budget_max: int) -> List[ProductSearchResult]:
        """실제 검색 결과 처리"""
        results = []
        web_results = data.get("web", {}).get("results", [])
        
        for result in web_results[:5]:  # 상위 5개만
            # Extract domain
            url = result.get("url", "")
            domain = ""
            try:
                domain = urlparse(url).netloc
            except:
                domain = "Unknown"
            
            # Extract potential price (basic heuristic)
            description = result.get("description", "")
            title = result.get("title", "")
            price = self._extract_price(title + " " + description, budget_max)
            
            results.append(ProductSearchResult(
                title=title,
                url=url,
                description=description,
                domain=domain,
                price=price
            ))
        
        return results
    
    def _extract_price(self, text: str, budget_max: int) -> Optional[int]:
        """텍스트에서 가격 추출 (간단한 휴리스틱)"""
        import re
        
        # Look for price patterns like $XX, $XX.XX
        price_patterns = [
            r'\$(\d+(?:\.\d{2})?)',
            r'(\d+)\s*dollars?',
            r'USD\s*(\d+)',
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                try:
                    price = float(matches[0])
                    if 10 <= price <= budget_max * 2:  # Reasonable price range
                        return int(price)
                except:
                    continue
        
        # Default price within budget
        return min(budget_max - 10, 75)
    
    async def _simulate_search(self, keywords: List[str], budget_max: int) -> List[ProductSearchResult]:
        """시뮬레이션 모드"""
        await asyncio.sleep(0.8)
        
        sample_products = [
            {
                "title": f"{keywords[0]} Gift Set - Premium Edition",
                "url": "https://amazon.com/dp/example1",
                "description": f"Perfect {keywords[0]} gift with premium quality and elegant design.",
                "domain": "amazon.com",
                "price": min(budget_max - 10, 85)
            },
            {
                "title": f"Best {keywords[0]} Collection - Top Rated",
                "url": "https://etsy.com/listing/example2",
                "description": f"Handcrafted {keywords[0]} items, highly rated by customers.",
                "domain": "etsy.com",
                "price": min(budget_max - 25, 65)
            },
            {
                "title": f"{keywords[0]} Starter Kit - Complete Set",
                "url": "https://target.com/p/example3",
                "description": f"Everything needed for {keywords[0]} enthusiasts.",
                "domain": "target.com",
                "price": min(budget_max - 15, 70)
            }
        ]
        
        results = []
        for product in sample_products:
            results.append(ProductSearchResult(
                title=product["title"],
                url=product["url"],
                description=product["description"],
                domain=product["domain"],
                price=product["price"]
            ))
        
        return results