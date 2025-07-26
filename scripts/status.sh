#!/bin/bash

# Gift Genie - 서버 상태 확인 스크립트

echo "🔍 Gift Genie 서버 상태 확인"
echo ""

# 포트 상태 확인
echo "📡 포트 사용 현황:"
echo "   포트 8000 (Backend):"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "      ✅ 사용 중 (PID: $(lsof -ti:8000))"
else
    echo "      ❌ 사용 안함"
fi

echo "   포트 3000 (Frontend):"
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "      ✅ 사용 중 (PID: $(lsof -ti:3000))"
else
    echo "      ❌ 사용 안함"
fi

echo "   포트 3001 (Frontend 대체):"
if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "      ✅ 사용 중 (PID: $(lsof -ti:3001))"
else
    echo "      ❌ 사용 안함"
fi

echo ""

# 서비스 응답 확인
echo "🏥 서비스 응답 테스트:"

echo "   Backend API:"
if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    echo "      ✅ 정상 응답"
    curl -s http://localhost:8000/api/v1/health | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'      📊 상태: {data.get(\"status\", \"unknown\")}')
    print(f'      🕒 시간: {data.get(\"timestamp\", \"unknown\")}')
    services = data.get('services', {})
    for service, status in services.items():
        print(f'      🔧 {service}: {status}')
except:
    pass
"
else
    echo "      ❌ 응답 없음"
fi

echo "   Frontend:"
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    echo "      ✅ 포트 3000에서 정상 응답"
elif curl -s http://localhost:3001 >/dev/null 2>&1; then
    echo "      ✅ 포트 3001에서 정상 응답"
else
    echo "      ❌ 응답 없음"
fi

echo ""

# 프로세스 확인
echo "🔄 실행 중인 프로세스:"
echo "   Python (Backend):"
if pgrep -f "python main.py" >/dev/null; then
    echo "      ✅ main.py 실행 중 (PID: $(pgrep -f 'python main.py'))"
else
    echo "      ❌ 실행 안함"
fi

echo "   Node.js (Frontend):"
if pgrep -f "next dev" >/dev/null; then
    echo "      ✅ next dev 실행 중 (PID: $(pgrep -f 'next dev'))"
else
    echo "      ❌ 실행 안함"
fi

echo ""

# 접속 링크
echo "🌐 접속 링크:"
if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    echo "   📋 API 문서: http://localhost:8000/docs"
    echo "   💓 API 상태: http://localhost:8000/api/v1/health"
fi

if curl -s http://localhost:3000 >/dev/null 2>&1; then
    echo "   🎁 Gift Genie: http://localhost:3000"
elif curl -s http://localhost:3001 >/dev/null 2>&1; then
    echo "   🎁 Gift Genie: http://localhost:3001"
fi