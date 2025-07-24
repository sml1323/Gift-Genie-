# 개발 스크립트

이 디렉토리는 Gift Genie의 개발 환경 관련 스크립트들이 저장되는 곳입니다.

## 포함될 스크립트들
- `setup-dev.sh` - 개발 환경 초기 설정
- `start-dev.sh` - 개발 서버 시작
- `reset-db.sh` - 개발 DB 초기화
- `seed-data.js` - 테스트 데이터 생성

## 개발 명령어
```bash
# 개발 환경 초기 설정 (최초 1회)
./setup-dev.sh

# 개발 서버 시작
./start-dev.sh

# 데이터베이스 초기화
./reset-db.sh

# 테스트 데이터 생성
node seed-data.js
```

## 개발 환경 구성
- Frontend: Next.js 개발 서버 (Port 3000)
- Backend: FastAPI 개발 서버 (Port 8000)  
- Database: PostgreSQL (Port 5432)
- Redis: 캐시 서버 (Port 6379)