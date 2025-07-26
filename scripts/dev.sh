#!/bin/bash

# Gift Genie - 간단 개발 서버 실행 스크립트

echo "🎁 Gift Genie 개발 서버 실행"

# 백그라운드에서 Backend 실행
echo "🚀 Backend 시작..."
cd backend && python main.py &
BACKEND_PID=$!

# 3초 대기
sleep 3

# 백그라운드에서 Frontend 실행  
echo "🎨 Frontend 시작..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ 서버 실행 완료!"
echo "🌐 Frontend: http://localhost:3000"
echo "📋 API 문서: http://localhost:8000/docs"
echo ""
echo "⏹️  종료: Ctrl+C"

# Ctrl+C 처리
trap 'echo ""; echo "🛑 서버 종료..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

# 대기
wait