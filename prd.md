
## **선물 추천 AI (Gift Genie) MVP 제품 요구사항 정의서 (PRD)**

**문서 버전:** 1.1  
**작성일:** 2025년 7월 25일  
**프로젝트 코드명:** Gift Genie

### **1. 제품 비전 (Product Vision)**

#### **문제 정의**
- 한국인의 87%가 선물 선택에 스트레스를 느낀다 (2024 소비자 조사 기준)
- 평균 선물 검색 시간: 2시간 이상
- 주요 pain points: 취향 파악 어려움, 예산 제약, 시간 부족

#### **솔루션**
실시간 트렌드 데이터와 AI를 결합하여 **5분 안에 완벽한 선물을 찾아주는** 개인화된 추천 서비스

#### **핵심 가치 제안**
"고민하지 마세요. AI가 받는 사람의 마음에 쏙 들 선물을 찾아드립니다."

### **2. 목표 및 성공 지표 (Goals & Success Metrics)**

#### **비즈니스 목표**
| 목표 | 지표 | MVP 목표치 | 측정 방법 |
|------|------|-----------|-----------|
| 제품-시장 적합성 검증 | 추천 만족도 | 75% 이상 | 추천 결과 피드백 |
| 사용자 가치 증명 | 재방문율 | 40% 이상 | GA4 분석 |
| 기술 안정성 확보 | API 응답 시간 | 10초 이내 | 서버 모니터링 |

#### **사용자 경험 지표**
- **추천 정확도:** 사용자가 실제 구매 링크를 클릭하는 비율 30% 이상
- **완료율:** 추천 요청 시작 → 결과 확인까지 완료하는 비율 80% 이상
- **공유율:** 추천 결과를 SNS에 공유하는 비율 10% 이상

### **3. 타겟 사용자 (Target Users)**

#### **주요 타겟 (Primary)**
- **페르소나:** 김선물 (32세, 직장인)
- **특징:** 
  - 매달 1-2회 선물 구매 필요 (생일, 기념일, 승진 축하 등)
  - 온라인 쇼핑 선호, 모바일 사용률 80%
  - 예산: 회당 5-15만원
- **Pain Point:** "받는 사람이 진짜 좋아할지 모르겠어요"

#### **보조 타겟 (Secondary)**
- 20대 후반 커플 (기념일 선물)
- 40대 부모님 (자녀 선물)
- 기업 HR 담당자 (직원 선물)

### **4. 핵심 사용자 여정 (Core User Journey)**

```
[접속] → [조건 입력] → [AI 분석] → [결과 확인] → [구매/공유]
 1분       2분         5-10초      2분         1분
```

#### **상세 플로우**

1. **랜딩 (0-30초)**
   - 명확한 가치 제안 메시지
   - 간단한 예시 결과 미리보기
   - CTA: "지금 바로 추천받기"

2. **정보 입력 (30초-2분)**
   ```
   Step 1: 받는 사람은 누구인가요?
   - [남성] [여성] [상관없음]
   
   Step 2: 나이대를 선택해주세요
   - [10대] [20대] [30대] [40대] [50대+]
   
   Step 3: 어떤 것을 좋아하나요? (최대 3개)
   - 🏃 운동/건강  📚 독서/학습  🎮 게임/e스포츠
   - 🍳 요리/맛집  ✈️ 여행/캠핑  💻 IT/가젯
   - 🎨 예술/공예  🌿 식물/반려동물  🎬 영화/공연
   
   Step 4: 예산은 어느 정도인가요?
   - [~3만원] [3-5만원] [5-10만원] [10-20만원] [20만원+]
   
   Step 5: 어떤 날인가요? (선택사항)
   - 🎂 생일  💑 기념일  🎊 축하  🙏 감사  기타
   ```

3. **AI 처리 (5-10초)**
   - 진행률 표시 (0% → 100%)
   - 단계별 메시지:
     - "트렌드 분석 중..." (25%)
     - "인기 상품 검색 중..." (50%)
     - "맞춤 추천 생성 중..." (75%)
     - "거의 완료되었어요!" (90%)

4. **결과 표시**
   - 상단: AI 종합 추천 메시지
   - 중앙: 3-5개 상품 카드
   - 하단: 추가 옵션 (다시 추천, 조건 수정)

### **5. 기능 요구사항 (Functional Requirements)**

#### **Frontend 요구사항**

**F1. 반응형 디자인**
- 모바일 우선 설계 (360px ~ )
- 태블릿/데스크톱 최적화
- 다크모드 지원

**F2. 입력 인터페이스**
- 단계별 프로그레스 바
- 이전 단계로 돌아가기 기능
- 실시간 입력 검증
- 툴팁/도움말 제공

**F3. 결과 카드 컴포넌트**
```javascript
{
  id: string,
  rank: number,  // 추천 순위
  product: {
    name: string,
    brand: string,
    price: {
      original: number,
      sale: number,
      discount_rate: number
    },
    image: {
      main: string,
      thumbnails: string[]
    },
    rating: number,
    review_count: number
  },
  recommendation: {
    reason: string,  // AI가 생성한 추천 이유
    match_score: number,  // 매칭 점수 (0-100)
    tags: string[]  // 관련 태그
  },
  purchase_options: [
    {
      vendor: string,  // "쿠팡", "네이버", "11번가"
      url: string,
      delivery: string  // "내일 도착", "2-3일"
    }
  ]
}
```

**F4. 상호작용 요소**
- 좋아요/싫어요 피드백
- 카카오톡/URL 공유
- 찜하기 (로컬 스토리지)
- "비슷한 상품 더보기"

#### **Backend 요구사항**

**B1. API 설계**
```python
# 메인 추천 엔드포인트
POST /api/v1/recommendations
Request:
{
  "recipient": {
    "gender": "male|female|neutral",
    "age_group": "teens|20s|30s|40s|50s+",
    "interests": ["sports", "reading", "gaming"],  // max 3
    "relationship": "friend|lover|parent|colleague"  // optional
  },
  "budget": {
    "min": 0,
    "max": 50000
  },
  "occasion": "birthday|anniversary|celebration",  // optional
  "exclude_categories": ["alcohol", "perfume"]  // optional
}

Response:
{
  "request_id": "uuid",
  "generated_at": "2025-07-25T10:00:00Z",
  "search_insights": {
    "trending_keywords": ["캠핑용품", "홈트레이닝"],
    "popular_categories": ["전자기기", "생활용품"]
  },
  "recommendations": [...],  // 위 F3 형식
  "alternative_query": "더 많은 결과를 원하시면..."
}
```

**B2. MCP 통합 로직**
```python
# 단계별 처리 파이프라인
async def generate_recommendations(request):
    # 1. 쿼리 생성 (100ms)
    query = build_search_query(request)
    
    # 2. Brave Search로 트렌드 파악 (2-3초)
    trends = await brave_search(query, limit=20)
    
    # 3. 상품명 추출 및 정제 (500ms)
    product_candidates = extract_products(trends)
    
    # 4. Apify로 상세 정보 수집 (3-5초)
    product_details = await apify_scrape(product_candidates[:10])
    
    # 5. GPT-4o-mini로 추천 이유 생성 (2-3초)
    recommendations = await generate_reasons(request, product_details)
    
    # 6. 최종 정렬 및 필터링 (100ms)
    return format_response(recommendations[:5])
```

**B3. 에러 처리 및 폴백**
- MCP 서비스 장애 시 캐시된 데이터 활용
- 부분 실패 허용 (최소 3개 추천 보장)
- 사용자 친화적 에러 메시지

**B4. 성능 최적화**
- Redis 캐싱 (TTL: 1시간)
- 동시 요청 제한 (Rate limiting)
- 비동기 처리 최적화

### **6. 비기능 요구사항 (Non-functional Requirements)**

| 항목 | 요구사항 | 측정 기준 |
|------|----------|-----------|
| 성능 | 전체 응답 시간 | < 10초 (P95) |
| 가용성 | 서비스 가동률 | > 99% |
| 확장성 | 동시 사용자 | 100명 지원 |
| 보안 | API 인증 | Rate limiting |
| 분석 | 이벤트 추적 | GA4, Mixpanel |

### **7. 기술 스택**

```yaml
Frontend:
  - Framework: Next.js 14 (App Router)
  - UI Library: Tailwind CSS + Shadcn/ui
  - State: Zustand
  - Analytics: GA4 + Posthog

Backend:
  - Framework: FastAPI
  - Database: PostgreSQL (Supabase)

AI/MCP:
  - Search: Brave Search API
  - Scraping: Apify
  - LLM: GPT-4o-mini
  - Future: Firecrawl (v1.1)

```

### **8. MVP 타임라인**

| 주차 | 마일스톤 | 산출물 |
|------|----------|--------|
| 1주 | 기초 설정 | 프로젝트 구조, API 설계 |
| 2주 | 백엔드 핵심 | MCP 통합, 추천 로직 |
| 3주 | 프론트엔드 | UI 구현, API 연동 |
| 4주 | 통합 테스트 | 버그 수정, 성능 최적화 |
| 5주 | 배포 준비 | 모니터링, 분석 도구 |

### **9. 리스크 및 대응 방안**

| 리스크 | 영향도 | 대응 방안 |
|--------|--------|-----------|
| API 비용 초과 | 높음 | 일일 한도 설정, 캐싱 강화 |
| 스크래핑 차단 | 중간 | 다중 소스, 프록시 활용 |
| 추천 품질 저하 | 높음 | A/B 테스트, 지속적 프롬프트 개선 |
| 응답 속도 지연 | 중간 | 프로그레시브 로딩, 부분 결과 우선 표시 |

### **10. 성공을 위한 핵심 원칙**

1. **Simple First**: 복잡한 기능보다 핵심 경험에 집중
2. **Data-Driven**: 모든 결정은 사용자 데이터 기반
3. **Fail Fast**: 빠른 실험과 학습 중시
4. **User Delight**: 기능보다 사용자 감동 우선

---