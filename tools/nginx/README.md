# Nginx 설정

이 디렉토리는 Gift Genie의 Nginx 웹서버 설정 파일들이 저장되는 곳입니다.

## 포함될 파일들
- `nginx.conf` - 메인 Nginx 설정
- `default.conf` - 기본 사이트 설정
- `ssl.conf` - SSL/HTTPS 설정
- `proxy.conf` - 리버스 프록시 설정

## 주요 기능
- 정적 파일 서빙 (Frontend)
- API 리버스 프록시 (Backend)
- SSL 터미네이션
- 로드 밸런싱 (확장 시)

## 설정 적용
```bash
# 설정 파일 테스트
nginx -t

# 설정 리로드
nginx -s reload
```