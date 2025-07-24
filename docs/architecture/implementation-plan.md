# Gift Genie - 상세 구현 계획서

## 🎯 구현 전략 개요

**핵심 원칙**: Simple First → 복잡한 기능보다 핵심 경험에 집중  
**개발 방식**: 반복적 개발 (Iterative Development)  
**품질 보증**: 각 단계별 검증 후 다음 단계 진행

## 📋 Week 1: 기초 설정 상세 계획

### Day 1-2: 프로젝트 초기화
```bash
# 1. Next.js 14 프로젝트 초기화
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# 2. FastAPI 프로젝트 초기화  
mkdir backend && cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn pydantic sqlalchemy psycopg2-binary python-multipart

# 3. Monorepo 설정
npm init -w frontend -w backend
```

**주요 설정 파일**:
- `package.json` (root) - 워크스페이스 설정
- `frontend/next.config.js` - API 프록시 설정
- `backend/main.py` - FastAPI 엔트리포인트
- `docker-compose.yml` - 개발 환경

### Day 3-4: UI/UX 기초 설정
```typescript
// frontend/components/ui/ - Shadcn/ui 설치
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input card progress select

// 핵심 컴포넌트 스케치
- RecommendationForm (5단계 입력)
- ProgressIndicator (AI 처리 진행률)
- ProductCard (추천 결과)
- FeedbackButtons (좋아요/싫어요)
```

### Day 5-7: 백엔드 기초 및 API 설계
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Gift Genie API", version="1.0.0")

# CORS 설정 (개발용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 핵심 라우터
app.include_router(recommendations.router, prefix="/api/v1")
```

**API 엔드포인트 구조**:
```
POST /api/v1/recommendations       # 추천 생성
GET  /api/v1/recommendations/{id}  # 결과 조회
POST /api/v1/feedback             # 피드백 제출
GET  /api/v1/trends               # 트렌드 데이터
```

## 📋 Week 2: MCP 통합 및 추천 엔진

### Day 8-10: MCP 서비스 통합
```python
# backend/services/search/brave_search.py
class BraveSearchService:
    async def search_trending_gifts(self, query: str, limit: int = 20):
        # Brave Search API 호출
        # 트렌드 키워드 기반 상품 검색
        pass

# backend/services/scraping/apify_service.py  
class ApifyScrapingService:
    async def get_product_details(self, product_urls: List[str]):
        # Apify로 상품 상세 정보 수집
        # 가격, 이미지, 리뷰 등
        pass

# backend/services/ai/recommendation_engine.py
class RecommendationEngine:
    async def generate_recommendations(self, user_request: UserRequest):
        # GPT-4o-mini로 개인화 추천 생성
        # 추천 이유 및 매칭 점수 계산
        pass
```

### Day 11-14: 추천 파이프라인 구현
```python
# 핵심 추천 파이프라인
async def create_recommendation(request: RecommendationRequest):
    # 1. 검색 쿼리 생성
    search_query = build_search_query(request)
    
    # 2. Brave Search로 트렌드 분석
    trends = await brave_search.search(search_query)
    
    # 3. 상품 후보 추출
    candidates = extract_product_candidates(trends)
    
    # 4. Apify로 상세 정보 수집  
    products = await apify_service.scrape_products(candidates)
    
    # 5. AI 추천 생성
    recommendations = await ai_service.generate_recommendations(request, products)
    
    # 6. 결과 저장 및 반환
    return save_and_format_results(recommendations)
```

## 📋 Week 3: 프론트엔드 핵심 기능

### Day 15-17: 입력 폼 컴포넌트
```typescript
// frontend/components/forms/RecommendationForm.tsx
interface FormStep {
  step: number;
  title: string;
  component: React.ComponentType;
}

const steps: FormStep[] = [
  { step: 1, title: "받는 사람", component: RecipientStep },
  { step: 2, title: "나이대", component: AgeStep },
  { step: 3, title: "관심사", component: InterestsStep },
  { step: 4, title: "예산", component: BudgetStep },
  { step: 5, title: "상황", component: OccasionStep },
];

// Zustand 상태 관리
interface RecommendationState {
  currentStep: number;
  formData: Partial<RecommendationRequest>;
  isLoading: boolean;
  results: RecommendationResult[];
}
```

### Day 18-21: 결과 표시 및 상호작용
```typescript
// frontend/components/cards/ProductCard.tsx
interface ProductCardProps {
  recommendation: RecommendationResult;
  onFeedback: (id: string, feedback: 'like' | 'dislike') => void;
  onShare: (id: string, platform: 'kakao' | 'url') => void;
}

// 핵심 기능
- 가격 비교 (여러 쇼핑몰)
- 이미지 갤러리
- AI 추천 이유 표시
- 구매 링크 연결
- 피드백 수집
```

## 📋 Week 4: 통합 및 최적화

### Day 22-24: 성능 최적화
```typescript
// 프론트엔드 최적화
- React.memo, useMemo, useCallback 적용
- 이미지 최적화 (Next.js Image 컴포넌트)
- 코드 스플리팅 (dynamic import)
- 번들 크기 분석 및 최적화

// 백엔드 최적화  
- Redis 캐싱 구현
- 데이터베이스 인덱스 최적화
- 비동기 처리 개선
- API 응답 압축
```

### Day 25-28: 테스트 및 품질 보증
```bash
# E2E 테스트 설정
npm install -D @playwright/test
npx playwright install

# 테스트 시나리오
- 전체 추천 프로세스 (입력 → 결과)
- 에러 상황 처리
- 다양한 디바이스/브라우저
- 성능 벤치마크
```

## 📋 Week 5: 배포 및 모니터링

### Day 29-31: 분석 도구 설정
```typescript
// GA4 이벤트 추적
gtag('event', 'recommendation_start', {
  user_type: 'new_user',
  device_type: 'mobile'
});

gtag('event', 'recommendation_complete', {
  satisfaction_score: 4.5,
  time_taken: 120 // seconds
});

// Posthog 사용자 여정 분석
posthog.capture('form_step_completed', {
  step: 3,
  interests_selected: ['sports', 'gaming']
});
```

### Day 32-35: 배포 인프라
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      
  backend:
    build: ./backend  
    ports:
      - "8000:8000" 
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - BRAVE_API_KEY=${BRAVE_API_KEY}
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./tools/nginx:/etc/nginx/conf.d
```

## 🔧 기술적 구현 세부사항

### 상태 관리 전략
```typescript
// Zustand 스토어 구조
interface AppState {
  // 추천 폼 상태
  recommendation: RecommendationState;
  
  // 전역 UI 상태  
  ui: {
    theme: 'light' | 'dark';
    loading: boolean;
    error: string | null;
  };
  
  // 사용자 피드백
  feedback: {
    history: FeedbackItem[];
    preferences: UserPreferences;
  };
}
```

### 에러 처리 전략
```python
# 백엔드 에러 처리
class RecommendationError(Exception):
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code

# 전역 에러 핸들러
@app.exception_handler(RecommendationError)
async def recommendation_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "fallback_action": "try_different_criteria"
        }
    )
```

### 보안 고려사항
```python
# API 인증 및 제한
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/recommendations")
@limiter.limit("10/minute")  # 분당 10회 제한
async def create_recommendation(request: Request, data: RecommendationRequest):
    # API 키 검증
    # 입력 데이터 검증
    # SQL 인젝션 방지
    pass
```

## 📊 성능 모니터링 지표

### 백엔드 메트릭
- API 응답 시간 (P50, P95, P99)
- 처리량 (RPS - Requests Per Second)
- 에러율 (4xx, 5xx)
- MCP 서비스별 응답 시간

### 프론트엔드 메트릭  
- Core Web Vitals (LCP, FID, CLS)
- 번들 크기 및 로딩 시간
- 페이지별 bounce rate
- 사용자 여정 완료율

### 비즈니스 메트릭
- 추천 요청 → 완료 전환율
- 추천 결과 → 구매 클릭율  
- 사용자 만족도 (피드백 기반)
- 재방문율 및 retention

## 🚀 배포 체크리스트

### 프로덕션 준비
- [ ] 환경 변수 보안 설정
- [ ] SSL 인증서 설정
- [ ] 도메인 DNS 설정
- [ ] CDN 설정 (이미지, 정적 파일)
- [ ] 데이터베이스 백업 자동화
- [ ] 로그 수집 시스템
- [ ] 모니터링 대시보드
- [ ] 알림 설정 (서버 다운, 에러 급증)

### 사용자 테스트
- [ ] 베타 사용자 그룹 모집
- [ ] 피드백 수집 프로세스
- [ ] A/B 테스트 준비
- [ ] 사용성 테스트 진행

---

*구현 계획 v1.0 - 2025.07.24*