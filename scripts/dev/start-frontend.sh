#!/bin/bash

# Gift Genie Frontend Development Starter
# 프론트엔드 개발 서버를 시작하는 스크립트

set -e

echo "🎁 Gift Genie Frontend Development Server"
echo "========================================="

# 프론트엔드 디렉토리로 이동
cd "$(dirname "$0")/../../frontend"

# Node.js 버전 확인
echo "📋 Checking Node.js version..."
node_version=$(node -v)
echo "   Node.js version: $node_version"

if ! node -e "process.exit(process.version.split('.')[0].slice(1) >= 18 ? 0 : 1)"; then
    echo "❌ Error: Node.js 18+ is required"
    echo "   Please install Node.js 18 or higher"
    exit 1
fi

# package.json 존재 확인
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found"
    echo "   Make sure you're in the frontend directory"
    exit 1
fi

# node_modules 확인 및 설치
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# 환경 변수 파일 확인
if [ ! -f ".env.local" ]; then
    echo "⚠️  Warning: .env.local not found"
    if [ -f ".env.local.example" ]; then
        echo "📝 Creating .env.local from example..."
        cp .env.local.example .env.local
        echo "✅ Created .env.local - please edit it with your settings"
    else
        echo "❌ Error: .env.local.example not found"
        exit 1
    fi
fi

# TypeScript 컴파일 확인
echo "🔍 Checking TypeScript..."
npm run type-check

if [ $? -eq 0 ]; then
    echo "✅ TypeScript check passed"
else
    echo "❌ TypeScript errors found - please fix them first"
    exit 1
fi

# 개발 서버 시작
echo ""
echo "🚀 Starting development server..."
echo "   Frontend will be available at: http://localhost:3000"
echo "   Press Ctrl+C to stop the server"
echo ""

# 백그라운드에서 서버 상태 확인
(
    sleep 5
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ Frontend server is running successfully!"
    else
        echo "⚠️  Frontend server might not be responding yet..."
    fi
) &

npm run dev