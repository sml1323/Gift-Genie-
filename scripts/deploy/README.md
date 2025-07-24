# 배포 스크립트

이 디렉토리는 Gift Genie의 배포 관련 스크립트들이 저장되는 곳입니다.

## 포함될 스크립트들
- `deploy-staging.sh` - 스테이징 환경 배포
- `deploy-production.sh` - 프로덕션 환경 배포
- `rollback.sh` - 이전 버전 롤백
- `health-check.sh` - 배포 후 헬스체크

## 배포 명령어
```bash
# 스테이징 배포
./deploy-staging.sh

# 프로덕션 배포 (승인 필요)
./deploy-production.sh

# 롤백 (긴급 시)
./rollback.sh [version]

# 헬스체크
./health-check.sh
```

## 배포 프로세스
1. 빌드 검증
2. 테스트 실행
3. 배포 실행
4. 헬스체크
5. 알림 발송