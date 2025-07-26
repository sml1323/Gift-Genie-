#!/bin/bash

# Gift Genie - 통합 실행 스크립트
# Frontend (Next.js) + Backend (FastAPI) 동시 실행

echo "🎁 Gift Genie 통합 서버 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로세스 종료 함수
cleanup() {
    echo -e "\n${YELLOW}🔄 서버를 종료하는 중...${NC}"
    
    # 백그라운드 프로세스 종료
    if [ ! -z "$BACKEND_PID" ]; then
        echo -e "${RED}🛑 Backend 서버 종료 (PID: $BACKEND_PID)${NC}"
        kill $BACKEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo -e "${RED}🛑 Frontend 서버 종료 (PID: $FRONTEND_PID)${NC}"
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    # 포트 사용 프로세스 강제 종료
    echo -e "${YELLOW}🧹 포트 정리 중...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3001 | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}✅ 모든 서버가 정상적으로 종료되었습니다.${NC}"
    exit 0
}

# Ctrl+C 시그널 처리
trap cleanup INT TERM

# 현재 디렉토리 확인
if [ ! -f "prd.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Gift Genie 프로젝트 루트 디렉토리에서 실행해주세요.${NC}"
    echo -e "${BLUE}💡 올바른 위치: /home/eslway/work/Gift-Genie-/${NC}"
    exit 1
fi

echo -e "${BLUE}📂 프로젝트 루트 디렉토리 확인됨${NC}"

# 포트 사용 확인 및 정리
echo -e "${YELLOW}🔍 포트 사용 상태 확인 중...${NC}"

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  포트 8000 이미 사용 중 - 기존 프로세스 종료${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  포트 3000 이미 사용 중 - 기존 프로세스 종료${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  포트 3001 이미 사용 중 - 기존 프로세스 종료${NC}"
    lsof -ti:3001 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Backend 시작
echo -e "\n${BLUE}🚀 Backend (FastAPI) 시작 중...${NC}"
cd backend

# Python 가상환경 확인
if [ -d "venv" ]; then
    echo -e "${YELLOW}📦 가상환경 활성화${NC}"
    source venv/bin/activate
fi

# 의존성 확인
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ backend/main.py 파일을 찾을 수 없습니다.${NC}"
    exit 1
fi

# Backend 실행
echo -e "${GREEN}🔧 FastAPI 서버 시작 (포트 8000)${NC}"
python main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Backend 시작 대기
echo -e "${YELLOW}⏳ Backend 서버 시작 대기 중...${NC}"
sleep 5

# Backend 헬스체크
echo -e "${BLUE}🏥 Backend 헬스체크${NC}"
if curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo -e "${GREEN}✅ Backend 서버 정상 실행 (PID: $BACKEND_PID)${NC}"
    echo -e "${BLUE}📋 API 문서: http://localhost:8000/docs${NC}"
else
    echo -e "${RED}❌ Backend 서버 시작 실패${NC}"
    cat ../logs/backend.log
    cleanup
    exit 1
fi

# Frontend 시작
echo -e "\n${BLUE}🎨 Frontend (Next.js) 시작 중...${NC}"
cd ../frontend

# Node.js 모듈 확인
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 npm install 실행 중...${NC}"
    npm install
fi

# Frontend 실행
echo -e "${GREEN}🔧 Next.js 서버 시작 (포트 3000)${NC}"
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Frontend 시작 대기
echo -e "${YELLOW}⏳ Frontend 서버 시작 대기 중...${NC}"
sleep 10

# Frontend 헬스체크
echo -e "${BLUE}🏥 Frontend 헬스체크${NC}"
FRONTEND_PORT=3000
if ! curl -s http://localhost:3000 > /dev/null; then
    echo -e "${YELLOW}⚠️  포트 3000 실패, 포트 3001 확인 중...${NC}"
    if curl -s http://localhost:3001 > /dev/null; then
        FRONTEND_PORT=3001
        echo -e "${GREEN}✅ Frontend 서버 정상 실행 (포트 3001)${NC}"
    else
        echo -e "${RED}❌ Frontend 서버 시작 실패${NC}"
        cat ../logs/frontend.log
        cleanup
        exit 1
    fi
else
    echo -e "${GREEN}✅ Frontend 서버 정상 실행 (포트 3000)${NC}"
fi

# 성공 메시지
echo -e "\n${GREEN}🎉 Gift Genie 서버가 성공적으로 시작되었습니다!${NC}\n"

echo -e "${BLUE}📱 서비스 접속 주소:${NC}"
echo -e "   🎁 Gift Genie: ${GREEN}http://localhost:${FRONTEND_PORT}${NC}"
echo -e "   📋 API 문서:   ${GREEN}http://localhost:8000/docs${NC}"
echo -e "   💓 API 상태:   ${GREEN}http://localhost:8000/api/v1/health${NC}"

echo -e "\n${BLUE}🔧 실행 중인 서비스:${NC}"
echo -e "   📡 Backend:  FastAPI (PID: ${BACKEND_PID})"
echo -e "   🌐 Frontend: Next.js  (PID: ${FRONTEND_PID})"

echo -e "\n${YELLOW}💡 사용법:${NC}"
echo -e "   • 서버 종료: ${GREEN}Ctrl+C${NC}"
echo -e "   • 로그 확인: ${GREEN}tail -f logs/backend.log${NC} 또는 ${GREEN}tail -f logs/frontend.log${NC}"
echo -e "   • API 테스트: ${GREEN}curl http://localhost:8000/api/v1/health${NC}"

echo -e "\n${GREEN}🚀 Gift Genie가 실행 중입니다. 브라우저에서 확인해보세요!${NC}"
echo -e "${BLUE}⏹️  종료하려면 Ctrl+C를 누르세요.${NC}\n"

# 로그 실시간 출력 (선택사항)
cd ..
mkdir -p logs

# 서버 계속 실행
while true; do
    sleep 1
    
    # 프로세스 상태 확인
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Backend 서버가 예기치 않게 종료되었습니다.${NC}"
        cleanup
        exit 1
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Frontend 서버가 예기치 않게 종료되었습니다.${NC}"
        cleanup
        exit 1
    fi
done