# 빌드 스크립트

이 디렉토리는 Gift Genie의 빌드 관련 스크립트들이 저장되는 곳입니다.

## 포함될 스크립트들
- `build-frontend.sh` - Frontend 빌드 스크립트
- `build-backend.sh` - Backend 빌드 스크립트
- `build-all.sh` - 전체 빌드 스크립트
- `optimize.js` - 번들 최적화 스크립트

## 빌드 명령어
```bash
# Frontend 빌드
./build-frontend.sh

# Backend 빌드
./build-backend.sh

# 전체 빌드
./build-all.sh

# 프로덕션 빌드 (최적화 포함)
./build-all.sh --production
```

## 환경별 빌드
- Development: 소스맵 포함, 압축 없음
- Production: 최적화, 압축, 소스맵 제외