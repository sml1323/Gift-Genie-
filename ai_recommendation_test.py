#!/usr/bin/env python3
"""
Gift Genie - AI Recommendation Engine Test
Simple single-file implementation for testing GPT-4o-mini integration

Week 2 AI/MCP Integration Test

Usage:
    export OPENAI_API_KEY="your-api-key-here"
    python ai_recommendation_test.py

Requirements:
    pip install openai
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
MAX_RECOMMENDATIONS = 5
API_TIMEOUT = 30


@dataclass
class GiftRequest:
    """Gift recommendation request model"""
    recipient_age: int
    recipient_gender: str
    relationship: str  # friend, family, colleague, partner
    budget_min: int
    budget_max: int
    interests: List[str]
    occasion: str  # birthday, christmas, anniversary, etc.
    personal_style: Optional[str] = None
    restrictions: Optional[List[str]] = None  # allergies, preferences, etc.


@dataclass
class GiftRecommendation:
    """Individual gift recommendation"""
    title: str
    description: str
    category: str
    estimated_price: int
    reasoning: str
    purchase_link: Optional[str] = None
    image_url: Optional[str] = None
    confidence_score: float = 0.0


@dataclass
class RecommendationResponse:
    """Complete recommendation response"""
    request_id: str
    recommendations: List[GiftRecommendation]
    total_processing_time: float
    created_at: str
    success: bool
    error_message: Optional[str] = None


class GiftRecommendationEngine:
    """Core gift recommendation engine using GPT-4o-mini"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
    
    async def generate_recommendations(self, request: GiftRequest) -> RecommendationResponse:
        """Generate gift recommendations based on user input"""
        start_time = datetime.now()
        request_id = f"req_{int(start_time.timestamp())}"
        
        try:
            logger.info(f"Processing recommendation request {request_id}")
            
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
        
        prompt = f"""당신은 개인화된 추천을 전문으로 하는 선물 컨설턴트입니다.

다음 정보를 바탕으로 {MAX_RECOMMENDATIONS}개의 완벽한 선물 추천을 생성해주세요:

받는 사람 프로필:
- 나이: {request.recipient_age}세
- 성별: {request.recipient_gender}
- 관계: {request.relationship}
- 관심사: {', '.join(request.interests)}

행사 및 예산:
- 행사: {request.occasion}
- 예산 범위: ${request.budget_min} - ${request.budget_max}{style_text}{restrictions_text}

정확히 {MAX_RECOMMENDATIONS}개의 선물 추천을 포함하는 JSON 형식으로 응답해주세요. 각 추천에는 다음이 포함되어야 합니다:
- title: 명확하고 간결한 선물 이름 (한글)
- description: 왜 완벽한지 설명하는 2-3문장 설명 (한글)
- category: 주요 카테고리 (전자제품, 패션, 도서 등, 한글)
- estimated_price: USD 가격 (정수)
- reasoning: 이 선물이 프로필에 맞는 이유 (한글)
- confidence_score: 확신도 (0.0-1.0)

중점 사항:
1. 관심사와 관계를 바탕으로 한 개인화
2. 행사와 예산에 적합함
3. 실용적이면서도 사려 깊은 추천
4. 받는 사람의 나이와 선호도 고려

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
                    recommendation = GiftRecommendation(
                        title=item.get('title', 'Unknown Gift'),
                        description=item.get('description', 'No description available'),
                        category=item.get('category', 'Other'),
                        estimated_price=int(item.get('estimated_price', 0)),
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


async def test_recommendation_engine():
    """Test the recommendation engine with sample data"""
    print("🎁 Gift Genie AI Recommendation Engine Test")
    print("=" * 50)
    
    # Initialize engine
    engine = GiftRecommendationEngine(OPENAI_API_KEY)
    
    # Create test request
    test_request = GiftRequest(
        recipient_age=28,
        recipient_gender="여성",
        relationship="친구",
        budget_min=50,
        budget_max=150,
        interests=["독서", "커피", "여행", "사진"],
        occasion="생일",
        personal_style="미니멀리스트",
        restrictions=["쥬얼리 제외", "친환경 제품 선호"]
    )
    
    print(f"📝 Test Request:")
    print(f"   Recipient: {test_request.recipient_age}yo {test_request.recipient_gender} {test_request.relationship}")
    print(f"   Budget: ${test_request.budget_min}-{test_request.budget_max}")
    print(f"   Interests: {', '.join(test_request.interests)}")
    print(f"   Occasion: {test_request.occasion}")
    print()
    
    # Generate recommendations
    print("🤖 Generating recommendations...")
    response = await engine.generate_recommendations(test_request)
    
    # Display results
    if response.success:
        print(f"✅ Success! Generated {len(response.recommendations)} recommendations in {response.total_processing_time:.2f}s")
        print()
        
        for i, rec in enumerate(response.recommendations, 1):
            print(f"🎁 Recommendation #{i}: {rec.title}")
            print(f"   💰 Price: ${rec.estimated_price}")
            print(f"   📂 Category: {rec.category}")
            print(f"   ⭐ Confidence: {rec.confidence_score:.1f}/1.0")
            print(f"   📝 Description: {rec.description}")
            print(f"   🧠 Reasoning: {rec.reasoning}")
            print()
    else:
        print(f"❌ Failed to generate recommendations")
        print(f"   Error: {response.error_message}")
        print(f"   Processing time: {response.total_processing_time:.2f}s")


async def test_error_handling():
    """Test error handling with invalid API key"""
    print("🧪 Testing Error Handling")
    print("=" * 30)
    
    # Test with invalid API key
    engine = GiftRecommendationEngine("invalid-key")
    
    test_request = GiftRequest(
        recipient_age=25,
        recipient_gender="남성",
        relationship="형제",
        budget_min=30,
        budget_max=80,
        interests=["게임", "음악"],
        occasion="졸업"
    )
    
    response = await engine.generate_recommendations(test_request)
    
    if not response.success:
        print(f"✅ Error handling working correctly")
        print(f"   Error captured: {response.error_message}")
    else:
        print(f"❌ Expected error but got success")


async def main():
    """Main test runner"""
    try:
        print("🚀 Starting Gift Genie AI/MCP Integration Tests")
        print("=" * 60)
        print()
        
        # Test 1: Normal recommendation flow
        await test_recommendation_engine()
        
        # Test 2: Error handling (주석 처리)
        # print("-" * 60)
        # print()
        # await test_error_handling()
        
        print()
        print("✅ All tests completed!")
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"❌ Test execution failed: {e}")


if __name__ == "__main__":
    # Check for required dependencies
    try:
        import openai
    except ImportError as e:
        print(f"❌ Missing required dependency: {e}")
        print("Install with: pip install openai")
        exit(1)
    
    # Check for API key
    if OPENAI_API_KEY == "your-openai-api-key-here":
        print("❌ OpenAI API key not set!")
        print("Set your API key with: export OPENAI_API_KEY='your-api-key-here'")
        exit(1)
    
    # Run tests
    asyncio.run(main())