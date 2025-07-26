"""
Gift Genie - Request Models
Pydantic models for API request validation
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class GiftRequest(BaseModel):
    """Gift recommendation request model"""
    recipient_age: int = Field(..., ge=1, le=120, description="Recipient's age")
    recipient_gender: str = Field(..., pattern="^(male|female|neutral|남성|여성|중성)$", description="Recipient's gender")
    relationship: str = Field(..., description="Relationship to recipient (friend, family, colleague, partner, etc.)")
    budget_min: int = Field(..., ge=0, description="Minimum budget in USD")
    budget_max: int = Field(..., ge=1, description="Maximum budget in USD")
    interests: List[str] = Field(..., min_items=1, max_items=5, description="List of recipient's interests")
    occasion: str = Field(..., description="Occasion for the gift (birthday, christmas, anniversary, etc.)")
    personal_style: Optional[str] = Field(None, description="Personal style preference")
    restrictions: Optional[List[str]] = Field(None, description="Allergies, preferences, or restrictions")

    @validator('budget_max')
    def budget_max_must_be_greater_than_min(cls, v, values):
        if 'budget_min' in values and v <= values['budget_min']:
            raise ValueError('budget_max must be greater than budget_min')
        return v

    @validator('interests')
    def interests_must_not_be_empty_strings(cls, v):
        if any(not interest.strip() for interest in v):
            raise ValueError('interests cannot contain empty strings')
        return [interest.strip() for interest in v]

    class Config:
        json_schema_extra = {
            "example": {
                "recipient_age": 28,
                "recipient_gender": "여성",
                "relationship": "친구",
                "budget_min": 50,
                "budget_max": 150,
                "interests": ["독서", "커피", "여행", "사진"],
                "occasion": "생일",
                "personal_style": "미니멀리스트",
                "restrictions": ["쥬얼리 제외", "친환경 제품 선호"]
            }
        }