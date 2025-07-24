# Docker 설정

이 디렉토리는 Gift Genie의 Docker 관련 설정 파일들이 저장되는 곳입니다.

## 포함될 파일들
- `Dockerfile` - 애플리케이션 이미지 빌드
- `docker-compose.yml` - 개발 환경 설정
- `docker-compose.prod.yml` - 프로덕션 환경 설정
- 환경별 Docker 설정 파일들

## 개발 환경 실행
```bash
# 개발 환경 시작
docker-compose up -d

# 프로덕션 환경 시작  
docker-compose -f docker-compose.prod.yml up -d
```