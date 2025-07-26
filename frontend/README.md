# Gift Genie Frontend

AI 기반 개인화 선물 추천 서비스의 Next.js 14 프론트엔드입니다.

## 🚀 빠른 시작

### 필수 요구사항
- Node.js 18+
- npm 또는 yarn

### 설치 및 실행

```bash
# 의존성 설치
npm install

# 환경 변수 설정
cp .env.local.example .env.local
# .env.local 파일을 편집하여 API URL 등을 설정하세요

# 개발 서버 시작
npm run dev
```

개발 서버는 [http://localhost:3000](http://localhost:3000)에서 실행됩니다.

## 📁 프로젝트 구조

```
frontend/
├── app/                    # Next.js 14 App Router
│   ├── globals.css        # 전역 스타일
│   ├── layout.tsx         # 루트 레이아웃
│   ├── page.tsx           # 홈페이지
│   └── recommendations/   # 추천 페이지
├── components/            # React 컴포넌트
│   ├── ui/               # 기본 UI 컴포넌트
│   ├── forms/            # 폼 컴포넌트
│   ├── cards/            # 카드 컴포넌트
│   └── layout/           # 레이아웃 컴포넌트
├── lib/                  # 유틸리티 라이브러리
│   ├── api.ts           # API 클라이언트
│   ├── store.ts         # Zustand 스토어
│   └── utils.ts         # 헬퍼 함수
├── types/               # TypeScript 타입 정의
├── hooks/               # 커스텀 React Hooks
└── styles/              # 추가 스타일
```

## 🛠️ 기술 스택

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Shadcn/ui
- **State Management**: Zustand
- **Form Handling**: React Hook Form + Zod
- **HTTP Client**: Fetch API
- **Icons**: Lucide React

## 🎨 디자인 시스템

### 색상 팔레트
- Primary: Orange (#f97316)
- Secondary: Blue (#0ea5e9)
- 중성색: Gray 계열

### 컴포넌트
- `Button`: 다양한 variant 지원
- `Toast`: 알림 메시지
- `Form Controls`: 입력 폼 요소들

## 📝 사용 가능한 스크립트

```bash
# 개발 서버 시작
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 서버 시작
npm run start

# 린팅
npm run lint

# 타입 체크
npm run type-check
```

## 🔧 환경 변수

`.env.local` 파일에서 설정:

- `NEXT_PUBLIC_API_URL`: 백엔드 API URL
- `NEXT_PUBLIC_ENABLE_MOCK_API`: 모의 API 사용 여부

## 🚦 개발 가이드

### 컴포넌트 생성
```tsx
// components/example/example-component.tsx
import { cn } from '@/lib/utils'

interface ExampleProps {
  className?: string
}

export function ExampleComponent({ className }: ExampleProps) {
  return (
    <div className={cn("default-styles", className)}>
      {/* 컴포넌트 내용 */}
    </div>
  )
}
```

### API 사용
```tsx
import { giftGenieAPI } from '@/lib/api'
import { useGiftGenieStore } from '@/lib/store'

// 추천 요청
const response = await giftGenieAPI.getRecommendations(request)
```

### 상태 관리
```tsx
import { useGiftGenieStore } from '@/lib/store'

function MyComponent() {
  const { formData, updateFormData } = useGiftGenieStore()
  
  // 상태 사용
}
```

## 🧪 테스트

현재 구현된 기능:
- ✅ 기본 프로젝트 구조
- ✅ UI 컴포넌트 시스템
- ✅ 상태 관리
- ✅ API 통합 (모의 API 포함)
- ✅ 반응형 디자인

다음 구현 예정:
- [ ] 5단계 추천 폼
- [ ] 결과 페이지
- [ ] 로딩 상태 관리
- [ ] 에러 처리

## 📞 지원

문제가 발생하면 다음을 확인해주세요:

1. Node.js 버전이 18+ 인지 확인
2. 모든 의존성이 설치되었는지 확인: `npm install`
3. 환경 변수가 올바르게 설정되었는지 확인
4. 백엔드 서버가 실행 중인지 확인

---

Gift Genie Frontend v0.1.0