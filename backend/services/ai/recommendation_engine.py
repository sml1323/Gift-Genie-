"""
Gift Genie - AI Recommendation Engine
Core gift recommendation engine using GPT-4o-mini
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import List, Optional
from openai import AsyncOpenAI

from models.request.recommendation import GiftRequest
from models.response.recommendation import GiftRecommendation, RecommendationResponse
from utils.currency import enhance_price_with_currency, normalize_budget_to_usd

logger = logging.getLogger(__name__)

# Constants
MAX_RECOMMENDATIONS = 5
API_TIMEOUT = 30


class GiftRecommendationEngine:
    """Core gift recommendation engine using GPT-4o-mini"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.simulation_mode = (api_key == "your-openai-api-key-here" or not api_key)
        if not self.simulation_mode:
            self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
    
    async def generate_recommendations(self, request: GiftRequest) -> RecommendationResponse:
        """Generate gift recommendations based on user input"""
        start_time = datetime.now()
        request_id = f"req_{int(start_time.timestamp())}"
        
        try:
            logger.info(f"Processing recommendation request {request_id} (simulation_mode: {self.simulation_mode})")
            
            if self.simulation_mode:
                # Simulation mode - generate mock recommendations
                await asyncio.sleep(1.5)  # Simulate AI processing time
                recommendations = self._generate_mock_recommendations(request)
            else:
                # Real mode - use OpenAI API
                # Build the prompt for GPT-4o-mini
                prompt = self._build_recommendation_prompt(request)
                
                # Call OpenAI API
                response = await self._call_openai_api(prompt)
                
                # Parse recommendations from response
                recommendations = self._parse_recommendations(response)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Successfully generated {len(recommendations)} recommendations in {processing_time:.2f}s")
            
            return RecommendationResponse(
                request_id=request_id,
                recommendations=recommendations,
                total_processing_time=processing_time,
                created_at=start_time.isoformat(),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return RecommendationResponse(
                request_id=request_id,
                recommendations=[],
                total_processing_time=processing_time,
                created_at=start_time.isoformat(),
                success=False,
                error_message=str(e)
            )
    
    def _build_recommendation_prompt(self, request: GiftRequest) -> str:
        """Build optimized prompt for gift recommendations"""
        restrictions_text = ""
        if request.restrictions:
            restrictions_text = f"\nImportant restrictions: {', '.join(request.restrictions)}"
        
        style_text = ""
        if request.personal_style:
            style_text = f"\nPersonal style preference: {request.personal_style}"
        
        prompt = f"""당신은 실제 쇼핑몰에서 구매 가능한 상품을 잘 아는 선물 컨설턴트입니다.

다음 정보를 바탕으로 {MAX_RECOMMENDATIONS}개의 **실제 상품명**으로 선물 추천을 생성해주세요:

받는 사람 프로필:
- 나이: {request.recipient_age}세
- 성별: {request.recipient_gender}
- 관계: {request.relationship}
- 관심사: {', '.join(request.interests)}

행사 및 예산:
- 행사: {request.occasion}
- 예산 범위: ${request.budget_min} - ${request.budget_max}{style_text}{restrictions_text}

**중요: title은 반드시 실제 존재하는 상품명으로 작성하세요**

정확한 실제 상품명 예시:
- "무선 블루투스 이어폰" (O)
- "아로마 디퓨저 세트" (O)  
- "스마트 워치" (O)
- "프리미엄 디지털 미니맵 송풍" (X - 이상한 조합)
- "리스트 LIST 미니맵" (X - 의미불명)

정확히 {MAX_RECOMMENDATIONS}개의 선물 추천을 포함하는 JSON 형식으로 응답해주세요:
- title: **실제 쇼핑몰에서 검색 가능한 정확한 상품명** (한글)
- description: 왜 완벽한지 설명하는 2-3문장 설명 (한글)
- category: 주요 카테고리 (전자제품, 홈리빙, 도서, 패션, 스포츠 등, 한글)
- estimated_price: USD 가격 (정수)
- currency: "USD" 또는 "KRW"
- price_display: "$50" 또는 "₩65,000" 형식의 가격 표시
- reasoning: 이 선물이 프로필에 맞는 이유 (한글)
- confidence_score: 확신도 (0.0-1.0)

**검증 기준:**
1. title이 네이버쇼핑에서 실제 검색 가능한 상품명인지 확인
2. 관심사와 직접 연관된 구체적 상품 선택
3. 예산 범위 내 현실적 가격 설정
4. 받는 사람 프로필에 적합한 상품 선별

모든 텍스트는 한글로 작성하고, 유효한 JSON 형식으로만 응답해주세요."""

        return prompt
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API with error handling and timeouts"""
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "당신은 개인화된 추천을 전문으로 하는 선물 컨설턴트입니다. 모든 응답은 한글로 작성해주세요."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7,
                    response_format={"type": "json_object"}
                ),
                timeout=API_TIMEOUT
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise Exception("Empty response from OpenAI API")
            return content
            
        except asyncio.TimeoutError:
            raise Exception(f"OpenAI API timeout after {API_TIMEOUT} seconds")
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _parse_recommendations(self, response_text: str) -> List[GiftRecommendation]:
        """Parse OpenAI response into structured recommendations"""
        try:
            # Parse JSON response
            data = json.loads(response_text)
            
            # Handle different response formats
            if isinstance(data, list):
                recommendations_data = data
            else:
                # Try multiple possible keys
                recommendations_data = (data.get('recommendations') or 
                                      data.get('gift_recommendations') or 
                                      data.get('gifts') or
                                      data.get('items') or [])
            
            recommendations = []
            for item in recommendations_data[:MAX_RECOMMENDATIONS]:
                try:
                    estimated_price = int(item.get('estimated_price', 0))
                    currency = item.get('currency', 'USD')
                    price_display = item.get('price_display', f"${estimated_price}" if currency == 'USD' else f"₩{estimated_price:,}")
                    
                    recommendation = GiftRecommendation(
                        title=item.get('title', 'Unknown Gift'),
                        description=item.get('description', 'No description available'),
                        category=item.get('category', 'Other'),
                        estimated_price=estimated_price,
                        currency=currency,
                        price_display=price_display,
                        reasoning=item.get('reasoning', 'No reasoning provided'),
                        confidence_score=float(item.get('confidence_score', 0.5))
                    )
                    recommendations.append(recommendation)
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Skipping invalid recommendation: {e}")
                    continue
            
            return recommendations
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise Exception(f"Invalid JSON response from AI: {str(e)}")
    
    def _generate_mock_recommendations(self, request: GiftRequest) -> List[GiftRecommendation]:
        """시뮬레이션 모드용 가상 추천 생성"""
        
        # Normalize budget to USD for internal processing (legacy compatibility)
        budget_min_usd, budget_max_usd = normalize_budget_to_usd(
            request.budget_min, request.budget_max, request.currency
        )
        
        # Calculate sample prices in USD
        price_high = min(max(budget_max_usd - 10, budget_min_usd), budget_max_usd)
        price_mid = min(max(budget_max_usd - 30, budget_min_usd), budget_max_usd)
        price_low = min(max(budget_max_usd - 20, budget_min_usd), budget_max_usd)
        
        # Convert prices to target currency for display
        price_high_enhanced = enhance_price_with_currency(price_high, request.currency)
        price_mid_enhanced = enhance_price_with_currency(price_mid, request.currency)
        price_low_enhanced = enhance_price_with_currency(price_low, request.currency)
        
        mock_recommendations = [
            GiftRecommendation(
                title=f"{request.interests[0] if request.interests else '특별한'} 선물 - 프리미엄",
                description=f"{request.recipient_age}세 {request.recipient_gender}에게 완벽한 {request.occasion} 선물입니다. 고품질 소재와 세련된 디자인으로 특별함을 선사합니다.",
                category="프리미엄 선물",
                estimated_price=price_high_enhanced["estimated_price"],
                currency=price_high_enhanced["currency"],
                price_display=price_high_enhanced["price_display"],
                reasoning=f"받는 분의 관심사({', '.join(request.interests[:2]) if request.interests else '다양한 취미'})를 고려하여 선별한 고품질 제품입니다.",
                confidence_score=0.85
            ),
            GiftRecommendation(
                title=f"{request.relationship}을 위한 베스트셀러 아이템",
                description=f"많은 사람들이 선택한 인기 상품으로, {request.occasion}에 특히 의미있는 선물입니다. 실용성과 감성을 모두 만족시킵니다.",
                category="인기 상품",
                estimated_price=price_mid_enhanced["estimated_price"],
                currency=price_mid_enhanced["currency"],
                price_display=price_mid_enhanced["price_display"],
                reasoning=f"{request.relationship} 관계에서 가장 인기있는 선물 카테고리 중 하나로, 실패할 확률이 낮습니다.",
                confidence_score=0.78
            ),
            GiftRecommendation(
                title="한정 에디션 선물세트",
                description=f"특별한 {request.occasion}을 위한 한정판 선물세트입니다. 아름다운 포장과 함께 특별함을 더합니다.",
                category="한정 상품",  
                estimated_price=price_low_enhanced["estimated_price"],
                currency=price_low_enhanced["currency"],
                price_display=price_low_enhanced["price_display"],
                reasoning="한정 에디션 제품은 희소성과 특별함을 동시에 선사하여 기억에 남는 선물이 됩니다.",
                confidence_score=0.82
            )
        ]
        
        return mock_recommendations[:MAX_RECOMMENDATIONS]