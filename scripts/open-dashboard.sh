#!/bin/bash
# 대시보드 생성 및 브라우저에서 열기

set -e

echo "📊 대시보드 생성 중..."
python3 scripts/generate-dashboard.py

echo ""
echo "🌐 브라우저에서 대시보드 열기..."
open dashboard/index.html

echo ""
echo "✅ 완료!"
echo "   새로고침: F5 또는 Cmd+R"
echo "   재생성: ./scripts/open-dashboard.sh"
