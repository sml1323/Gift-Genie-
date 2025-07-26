# Gift Genie - AI 선물 추천 서비스

5분 안에 완벽한 선물을 찾아주는 개인화된 추천 서비스

## 🚀 Claude Code 빠른 시작 가이드

### ⚠️ 중요: Claude 사용법

Claude는 **자동으로 프로젝트 파일을 읽지 않습니다**. 매번 명시적으로 요청해야 합니다.

### 📋 권장 명령어 템플릿

**새 작업 시작할 때**:
```
"CLAUDE.md와 task.md를 읽고, 현재 상황을 파악한 후 다음 작업을 제안해줘"
```

**특정 주차 작업할 때**:
```
"CLAUDE.md, task.md, implementation-plan.md를 읽고 Week 1 작업을 시작해줘"
```

**문제 해결할 때**:
```
"CLAUDE.md와 prd.md를 읽고 [구체적 문제]를 해결해줘"
```

## 📁 주요 파일 구조

```
📄 CLAUDE.md                    # Claude용 프로젝트 가이드 (필수)
📄 task.md                      # 진행상황 체크리스트 (필수)
📄 prd.md                       # 제품 요구사항 정의서
📁 docs/architecture/
  └── implementation-plan.md     # 기술 구현 상세 가이드
📁 frontend/                     # Next.js 14 프론트엔드
📁 backend/                      # FastAPI 백엔드
📁 shared/                       # 공통 타입 및 유틸리티
```

## 🎯 프로젝트 정보

- **기술 스택**: Next.js 14, FastAPI, MCP (Brave Search + Apify + GPT-4o-mini)
- **개발 기간**: 5주 (MVP)
- **목표**: API 응답 10초 이내, 추천 만족도 75% 이상

## 🚀 서버 실행 방법

### 📜 통합 실행 스크립트

**한 번에 Frontend + Backend 실행**:
```bash
# 메인 실행 스크립트 (추천)
./start.sh

# 또는 간단한 개발 버전
./scripts/dev.sh
```

**서버 관리 명령어**:
```bash
# 서버 상태 확인
./scripts/status.sh

# 서버 종료
./scripts/stop.sh
```

### 🔧 수동 실행 (개발용)

**Backend (FastAPI)**:
```bash
cd backend
python main.py
# 접속: http://localhost:8000/docs
```

**Frontend (Next.js)**:
```bash
cd frontend
npm run dev
# 접속: http://localhost:3000
```

## 📊 현재 진행 상황

현재 상태를 확인하려면:
```
"task.md를 읽고 현재 진행률을 알려줘"
```

---

*Gift Genie v1.0 - 2025.07.24*