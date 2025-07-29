# AI Query Optimization Guidelines
## Intelligent Search Query Refinement for Gift Recommendations

### 🎯 Core Objectives
1. **Maximize Product Discovery**: Find relevant products within budget constraints
2. **Adapt to Korean Market**: Optimize for Naver Shopping API and Korean consumer behavior  
3. **Progressive Intelligence**: Learn from failed attempts to improve subsequent queries
4. **Context Preservation**: Maintain gift recipient relevance throughout refinement process
5. **Firecrawl Integration**: Leverage web research for market trend insights

---

## 📋 Query Refinement Strategies (5-Iteration Framework)

### **Iteration 1: Synonym Expansion** 
```yaml
Strategy: "synonym_expansion"
Goal: Expand search scope with synonyms and related terms
Approach: Conservative expansion maintaining high relevance
```

**Guidelines:**
- Add 1-2 high-relevance synonyms to original keywords
- Prioritize commonly used Korean terms over technical terms
- Consider generational language preferences (젊은층 vs 기성세대)
- Maintain core intent while broadening discovery potential

**Example Transformations:**
```
Original: ["스마트폰", "케이스"]
Refined: ["휴대폰", "스마트폰", "폰케이스", "핸드폰케이스"]

Original: ["책", "소설"]  
Refined: ["도서", "책", "베스트셀러", "소설"]

Original: ["화장품", "립스틱"]
Refined: ["코스메틱", "화장품", "립", "립스틱", "메이크업"]
```

### **Iteration 2: Category Broadening**
```yaml
Strategy: "category_broadening" 
Goal: Expand to related categories and broader product classifications
Approach: Strategic category expansion with demographic awareness
```

**Guidelines:**
- Move to parent categories or adjacent categories
- Consider cross-category gift alternatives
- Factor in recipient age, gender, and interests
- Maintain gift-appropriateness throughout expansion

**Category Mapping Examples:**
```
Electronics → Tech Accessories → Smart Devices → Digital Lifestyle
Fashion → Accessories → Personal Style → Luxury Items
Home → Living → Wellness → Self-Care
Books → Education → Hobbies → Personal Development
```

**Transformation Examples:**
```
Original: ["아이폰", "충전기"]
Broadened: ["스마트폰", "액세서리", "전자기기", "모바일"]

Original: ["운동화", "나이키"]  
Broadened: ["신발", "스포츠", "운동용품", "액티브웨어"]
```

### **Iteration 3: Firecrawl Research Integration**
```yaml
Strategy: "firecrawl_research"
Goal: Incorporate market trends and popular products from web research  
Approach: Data-driven optimization using current market intelligence
```

**Firecrawl Research Targets:**
1. **Trending Products**: `"인기 선물 추천 2024 {age}세 {gender}"`
2. **Market Analysis**: `"네이버쇼핑 베스트 {category} {budget_range}"`
3. **Seasonal Trends**: `"올해 인기 {occasion} 선물"`
4. **Demographic Insights**: `"{age}대 {gender} 선물 트렌드"`

**Integration Process:**
```python
# Firecrawl insights integration example
firecrawl_data = {
    "trending_products": ["무선이어폰", "스마트워치", "아로마디퓨저"],
    "popular_keywords": ["프리미엄", "무선", "스마트", "휴대용"],
    "price_insights": {"sweet_spot": "50000-100000", "currency": "KRW"}
}

# Integration strategy
refined_keywords = original_keywords + trending_products[:2] + popular_keywords[:1]
```

**Market Intelligence Integration:**
- **Price Trends**: Adjust keyword modifiers based on budget positioning
- **Seasonal Relevance**: Incorporate time-sensitive product preferences  
- **Demographic Trends**: Apply age/gender-specific popular terms
- **Brand Intelligence**: Include trending brands and emerging players

### **Iteration 4: Demographic Adaptation**
```yaml
Strategy: "demographic_adaptation"
Goal: Deep personalization based on recipient profile
Approach: Comprehensive demographic and psychographic optimization
```

**Demographic Optimization Matrix:**

**Age-Based Adaptations:**
```yaml
10-19세: ["틴에이저", "학생", "Z세대", "트렌디", "인스타감성"]
20-29세: ["20대", "대학생", "직장인", "힙한", "개성있는"] 
30-39세: ["30대", "실용적", "고급스러운", "품질좋은", "브랜드"]
40-49세: ["40대", "프리미엄", "건강한", "안전한", "가족"]
50세+: ["시니어", "전통적", "건강", "편안한", "고품질"]
```

**Gender-Based Adaptations:**
```yaml
남성: ["남자", "멘즈", "남성용", "실용적", "기능성"]
여성: ["여자", "여성용", "우먼즈", "예쁜", "감성적"] 
중성: ["유니섹스", "중성", "모든이에게", "범용"]
```

**Interest-Based Keyword Mapping:**
```yaml
Technology: ["스마트", "디지털", "최신", "혁신적", "IT"]
Fashion: ["스타일", "패션", "트렌드", "멋있는", "세련된"]
Health: ["건강", "웰니스", "운동", "피트니스", "자연"]
Art: ["예술적", "창의적", "감성적", "아티스틱", "디자인"]
Music: ["뮤직", "사운드", "오디오", "음향", "멜로디"]
```

### **Iteration 5: Budget Alternative Strategy**
```yaml
Strategy: "budget_alternative"
Goal: Complete pivot to budget-optimized alternatives
Approach: Radical rethinking with value-focused product discovery
```

**Budget Optimization Strategies:**

**High Budget (200,000원+)**: 
- Keywords: `["프리미엄", "럭셔리", "고급", "브랜드", "한정판"]`
- Categories: Premium brands, luxury items, exclusive products

**Medium Budget (50,000-200,000원)**:
- Keywords: `["품질좋은", "실용적", "인기", "베스트", "추천"]` 
- Categories: Mid-range brands, functional products, popular items

**Low Budget (~50,000원)**:
- Keywords: `["가성비", "알뜰", "실속", "합리적", "경제적"]`
- Categories: Value products, multi-functional items, starter products

**Alternative Product Mapping:**
```yaml
Original_Expensive → Budget_Alternative:
"아이폰 악세서리" → "스마트폰 소품"
"명품 가방" → "예쁜 에코백"  
"고급 화장품" → "천연 스킨케어"
"프리미엄 전자기기" → "실용적 생활용품"
```

---

## 🔍 Advanced Optimization Techniques

### **Keyword Quality Scoring**
```python
def calculate_keyword_quality(keyword: str, context: dict) -> float:
    score = 0.0
    
    # Naver Shopping frequency weight (0.3)
    score += naver_search_volume(keyword) * 0.3
    
    # Demographic relevance (0.25) 
    score += demographic_match(keyword, context['age'], context['gender']) * 0.25
    
    # Budget appropriateness (0.2)
    score += budget_alignment(keyword, context['budget_range']) * 0.2
    
    # Seasonality relevance (0.15)
    score += seasonal_relevance(keyword, context['occasion']) * 0.15
    
    # Competition level (0.1) - lower competition = higher score
    score += (1.0 - market_competition(keyword)) * 0.1
    
    return min(score, 1.0)
```

### **Semantic Similarity Preservation**
- **Core Intent Preservation**: Never lose primary gift intent
- **Semantic Distance Limits**: Maximum 0.3 cosine distance from original intent
- **Context Boundary Enforcement**: Maintain recipient relevance throughout
- **Gift Appropriateness Validation**: Ensure all keywords lead to giftable products

### **Multi-Modal Optimization**
```yaml
Text_Optimization: Keyword semantic enhancement
Visual_Context: Image-based product discovery cues  
Behavioral_Patterns: Purchase history and preference modeling
Temporal_Awareness: Time-sensitive trend incorporation
Cultural_Adaptation: Korean cultural gift-giving norms
```

---

## 🎨 Prompt Engineering Templates

### **Base Refinement Prompt Template**
```
당신은 네이버쇼핑 검색 최적화 전문가입니다.

현재 상황:
- 시도: {attempt_number}/{max_attempts}
- 전략: {strategy}
- 이전 실패 키워드: {failed_keywords}
- 발견된 상품 수: {previous_results}

받는 사람 프로필:
- 나이: {age}세 ({age_group})
- 성별: {gender}
- 관심사: {interests}
- 관계: {relationship}
- 예산: {budget_min:,}원 - {budget_max:,}원

{STRATEGY_SPECIFIC_GUIDELINES}

최적화 요구사항:
✅ 네이버쇼핑 실제 검색 가능한 키워드
✅ 3-5개 핵심 키워드 구성  
✅ 받는 사람 프로필 최적화
✅ 예산 범위 적합성
✅ 한글 키워드 우선 사용
✅ 실패 패턴 회피

JSON 형식으로 응답:
{
    "refined_keywords": ["키워드1", "키워드2", "키워드3"],
    "search_query": "최종 검색어", 
    "confidence_score": 0.85,
    "reasoning": "개선 논리 설명",
    "expected_products": ["예상상품1", "예상상품2"],
    "fallback_keywords": ["대안키워드1", "대안키워드2"]
}
```

### **Firecrawl Integration Prompt**
```
네이버쇼핑 시장 조사 전문가로서 다음 선물 추천을 위한 시장 인사이트를 수집해주세요.

조사 대상:
- 기본 키워드: {original_keywords}
- 타겟: {age}세 {gender}
- 예산: {budget_range}
- 상황: {occasion}

조사 영역:
1. 현재 인기 상품 트렌드 (2024 최신)
2. 해당 연령대/성별 선호 키워드  
3. 예산 대비 인기 상품군
4. 계절/이벤트 특화 상품
5. 신제품/트렌드 브랜드

결과 형식:
{
    "trending_products": ["상품명1", "상품명2"],
    "hot_keywords": ["키워드1", "키워드2"], 
    "price_insights": {"range": "가격대", "sweet_spot": "최적가격"},
    "brand_trends": ["브랜드1", "브랜드2"],
    "market_opportunity": "시장 기회 분석"
}
```

---

## 🚨 Error Handling & Edge Cases

### **Common Failure Patterns**
1. **Overly Specific Keywords**: `"아이폰13프로맥스골드256GB"` → Too narrow
2. **Generic Terms**: `"선물"` → Too broad, low conversion
3. **Typos/Variants**: Handle Korean input variations and typos
4. **Budget Misalignment**: Keywords leading to products outside budget
5. **Cultural Mismatches**: Western product terms not popular in Korea

### **Recovery Strategies**
```yaml
No_Results_Found:
  - Immediate: Broaden category, remove modifiers
  - Secondary: Switch to core product type
  - Fallback: Use demographic-generic keywords

Too_Many_Results:
  - Add specific modifiers ("프리미엄", "고급")
  - Include brand preference hints  
  - Apply price range filters

Quality_Issues:
  - Add quality indicators ("정품", "브랜드")
  - Include trust signals ("인기", "베스트")
  - Filter by established sellers

Budget_Overflow:  
  - Add budget-conscious modifiers ("합리적", "가성비")
  - Shift to alternative product categories
  - Consider bundle/set alternatives
```

### **Fallback Keyword Libraries**
```yaml
Safe_Fallbacks_By_Age:
  teens: ["학생선물", "10대선물", "틴에이저선물"]
  twenties: ["20대선물", "대학생선물", "청년선물"] 
  thirties: ["30대선물", "직장인선물", "실용선물"]
  seniors: ["어른선물", "고급선물", "프리미엄선물"]

Safe_Fallbacks_By_Gender:
  male: ["남자선물", "남성용품", "멘즈아이템"]
  female: ["여자선물", "여성용품", "여성아이템"]
  unisex: ["유니섹스", "모든이선물", "공용선물"]

Emergency_Keywords: 
  - ["선물추천", "인기선물", "베스트선물", "프리미엄선물", "특별선물"]
```

---

## 📊 Performance Optimization

### **Caching Strategy**
- **Keyword Results Cache**: 1시간 TTL for successful keyword combinations
- **Firecrawl Insights Cache**: 6시간 TTL for market research data  
- **Demographic Patterns Cache**: 24시간 TTL for age/gender optimization patterns
- **Seasonal Trends Cache**: 1주 TTL for seasonal/occasion-based insights

### **Parallel Processing**
```python
async def parallel_query_testing(keyword_variants: List[str]):
    """병렬로 여러 키워드 조합 테스트"""
    tasks = [
        test_keyword_combination(keywords) 
        for keywords in keyword_variants
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return select_best_results(results)
```

### **Success Metrics**
```yaml
Primary_KPIs:
  - Products Found Rate: >80% success in finding 3+ products
  - Query Efficiency: Average 2.3 attempts to success
  - Processing Time: <15 seconds total refinement time
  - Budget Accuracy: >90% products within budget range

Secondary_KPIs:  
  - Demographic Relevance Score: >0.8 average
  - Keyword Quality Score: >0.7 average
  - Firecrawl Integration Success: >70% useful insights
  - User Satisfaction: Post-purchase feedback integration
```

---

## 🔧 Implementation Checklist

### **Phase 1: Core Refinement Engine**
- [x] Strategy-based keyword refinement system
- [x] 5-iteration progressive optimization framework  
- [x] Demographic adaptation algorithms
- [x] Budget alignment optimization

### **Phase 2: Firecrawl Integration**
- [ ] Market research data collection via Firecrawl MCP
- [ ] Trend analysis and keyword suggestion integration
- [ ] Real-time market intelligence incorporation
- [ ] Competitive analysis and positioning

### **Phase 3: Advanced Intelligence**
- [ ] Machine learning pattern recognition
- [ ] Success prediction modeling
- [ ] Automated A/B testing for keyword strategies  
- [ ] Personalization based on user behavior

### **Phase 4: Performance Optimization**
- [ ] Caching layer implementation
- [ ] Parallel processing optimization
- [ ] Real-time performance monitoring
- [ ] Adaptive strategy selection based on performance data

---

*This document serves as the authoritative guide for AI-driven query optimization in the Gift Genie recommendation system. Update regularly based on performance data and market insights.*