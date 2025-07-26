#!/bin/bash

# Gift Genie - 서버 종료 스크립트

echo "🛑 Gift Genie 서버 종료 중..."

# 포트별 프로세스 종료
echo "📡 Backend 서버 종료 (포트 8000)"
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "   포트 8000: 실행 중인 프로세스 없음"

echo "🌐 Frontend 서버 종료 (포트 3000, 3001)"
lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "   포트 3000: 실행 중인 프로세스 없음"
lsof -ti:3001 | xargs kill -9 2>/dev/null || echo "   포트 3001: 실행 중인 프로세스 없음"

# Python 프로세스 중 main.py 실행 중인 것들 종료
echo "🐍 Python 백엔드 프로세스 정리"
pkill -f "python main.py" 2>/dev/null || echo "   Python main.py: 실행 중인 프로세스 없음"

# Node.js 개발 서버 종료
echo "📦 Node.js 개발 서버 정리" 
pkill -f "next dev" 2>/dev/null || echo "   Next.js dev: 실행 중인 프로세스 없음"

echo ""
echo "✅ 모든 Gift Genie 서버가 종료되었습니다."