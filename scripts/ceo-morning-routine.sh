#!/bin/bash
# CEO 아침 루틴 - 한 번에 실행
# 5분 안에 하루를 시작하세요

set -e

clear

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "☀️  Good Morning, CEO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏰ $(date '+%Y년 %m월 %d일 %H:%M')"
echo ""

# 1. 데이터 검증
echo "🔍 데이터 무결성 확인 중..."
python3 scripts/validate-portfolio.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ 데이터 정상"
else
    echo "   ⚠️  데이터 이상 감지 - 확인 필요"
fi
echo ""

# 2. 일일 브리핑 생성
echo "📊 오늘의 브리핑 생성 중..."
./scripts/ceo-daily-briefing.sh > /dev/null 2>&1
echo "   ✅ 브리핑 준비 완료"
echo ""

# 3. 대시보드 생성
echo "📈 대시보드 업데이트 중..."
python3 scripts/generate-dashboard.py > /dev/null 2>&1
echo "   ✅ 대시보드 준비 완료"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 4. 브리핑 표시
echo "📋 오늘의 CEO 브리핑:"
echo ""

BRIEFING_FILE="reports/ceo-briefing-$(date +%Y-%m-%d).md"
if [ -f "$BRIEFING_FILE" ]; then
    cat "$BRIEFING_FILE"
else
    echo "⚠️  브리핑 파일을 찾을 수 없습니다."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 다음 액션:"
echo ""
echo "1. 브리핑을 읽고 의사결정을 내리세요"
echo "2. 모든 제안을 승인하려면:"
echo "   ./scripts/ceo-decision.sh briefing approve"
echo ""
echo "3. 시각적 대시보드를 보려면:"
echo "   ./scripts/open-dashboard.sh"
echo ""
echo "4. 전체 현황을 보려면:"
echo "   ./scripts/ceo-dashboard.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Have a productive day! 🚀"
echo ""
