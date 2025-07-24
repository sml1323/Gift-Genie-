# Gift Genie - Claude Code 프로젝트 가이드

> 🚨 **빠른 시작**: Claude는 자동으로 파일을 읽지 않습니다. 다음 명령어로 시작하세요:  
> `"CLAUDE.md와 task.md를 읽고, 현재 상황을 파악한 후 다음 작업을 제안해줘"`

## 🎯 프로젝트 개요
**이름**: Gift Genie (선물 추천 AI)  
**기술스택**: Next.js 14, FastAPI, MCP (Brave Search + Apify + GPT-4o-mini)  
**목표**: 5분 안에 완벽한 선물 추천 서비스 MVP 구축

## 📚 참고 문서 우선순위

### 1차 필수 문서 (매번 확인)
- `prd.md` - 제품 요구사항 및 비즈니스 목표
- `task.md` - 현재 진행상황 및 주간 마일스톤

### 2차 기술 문서 (구현 시 참조)
- `docs/architecture/implementation-plan.md` - 상세 기술 구현 가이드
- `docs/api/` - API 설계 문서 (생성 예정)
- `shared/types/` - 공통 타입 정의

### 3차 프로젝트 관리 문서
- `scripts/` - 빌드/배포 자동화 스크립트
- `docs/testing/` - 테스트 전략 문서

## 🛠️ 개발 컨텍스트

### 현재 상태 (Week 0 완료)
- ✅ 프로젝트 구조 설계 완료
- ✅ 개발 계획 수립 완료  
- ⏳ Week 1 (기초 설정) 대기 중

### 다음 작업 우선순위
1. **Frontend 초기화**: Next.js 14 + Tailwind + Shadcn/ui 설정
2. **Backend 초기화**: FastAPI + PostgreSQL 연결
3. **Monorepo 설정**: 워크스페이스 및 공통 도구 설정

## 🔧 개발 환경 설정

### 필수 도구
```bash
# Node.js 18+ 
# Python 3.9+
# PostgreSQL (Supabase 사용 예정)
# Docker (개발 환경)
```

### MCP 서비스 API 키 필요
- Brave Search API Key
- Apify API Key  
- OpenAI API Key (GPT-4o-mini)

## 📊 성공 지표

### 기술적 목표
- API 응답시간: < 10초 (P95)
- 서비스 가용성: > 99%
- 추천 완료율: > 80%

### 비즈니스 목표
- 추천 만족도: > 75%
- 재방문율: > 40%  
- 구매 전환율: > 30%

## 🚀 명령어 단축키

### 개발 시작
```bash
cd /Users/imseungmin/work/new_project
# task.md 확인 → 현재 주차 작업 파악
# implementation-plan.md 참조 → 기술 구현 방법
```

### 진행상황 업데이트
```markdown
# task.md에서 완료된 항목을 ✅로 변경
- [x] Next.js 14 프로젝트 초기화 ✅
- [ ] Tailwind CSS 설정 ⬜
```

## 🎨 코딩 스타일 가이드

### Frontend (TypeScript + React)
- 컴포넌트명: PascalCase
- 파일명: kebab-case  
- Hooks: use + PascalCase
- Tailwind CSS 우선 사용

### Backend (Python + FastAPI)  
- 함수명: snake_case
- 클래스명: PascalCase
- 비동기 처리 우선 (async/await)
- Pydantic 모델 적극 활용

## 📋 **중요: Claude 사용 방법**

> ⚠️ **핵심**: Claude는 자동으로 이 파일들을 읽지 않습니다!  
> 매번 명시적으로 읽어달라고 요청해야 합니다.

### **권장 세션 시작 명령어**

**새 작업 시**:
```
"CLAUDE.md와 task.md를 읽고, 현재 상황을 파악한 후 다음 작업을 제안해줘"
```

**계속 작업 시**:
```
"CLAUDE.md, task.md, implementation-plan.md를 읽고 Week 1 작업을 계속해줘"
```

**문제 해결 시**:
```
"CLAUDE.md와 prd.md를 읽고 [구체적 문제]를 해결해줘"
```

### **작업 완료 후**
1. `task.md`에서 완료 항목을 ✅로 업데이트 요청
2. 작업 로그에 날짜별 기록 추가 요청
3. 다음 세션을 위한 컨텍스트 정리

### 문제 발생 시
1. `prd.md` 재확인 → 원래 요구사항 대비 검토
2. `docs/architecture/implementation-plan.md` → 기술적 대안 검토
3. 리스크 대응책 적용

## 🔍 디버깅 가이드

### 자주 참조할 섹션
- PRD의 "사용자 여정" - UX 관련 문제
- PRD의 "API 설계" - 백엔드 연동 문제  
- implementation-plan의 "에러 처리 전략" - 예외 상황

### 성능 이슈 시
- implementation-plan의 "성능 최적화" 섹션 참조
- 목표: API 응답 10초, 번들 크기 최적화

---

*Claude가 이 프로젝트를 효율적으로 지원하기 위한 가이드 v1.0*