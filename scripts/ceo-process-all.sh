#!/bin/bash
# CEO 워크플로우 전체 처리 (마스터 스크립트)

set -e

PORTFOLIO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PORTFOLIO_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 CEO 워크플로우 전체 처리"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. 결정사항 처리
echo "1️⃣  결정사항 큐 처리..."
if [ -f "decisions-queue.json" ]; then
    ./scripts/process-decisions.sh
else
    echo "   ⏭️  건너뛰기 (큐 없음)"
fi
echo ""

# 2. 요구사항 처리
echo "2️⃣  요구사항 큐 처리..."
if [ -f "requests-queue.json" ]; then
    ./scripts/process-requests.sh
else
    echo "   ⏭️  건너뛰기 (큐 없음)"
fi
echo ""

# 3. CEO 피드백 반영
echo "3️⃣  CEO 피드백 반영..."
if [ -f "ceo-feedback.json" ]; then
    # 피드백 파일이 비어있지 않으면
    if [ -s "ceo-feedback.json" ]; then
        claude << EOF
ceo-feedback.json을 읽어서 포트폴리오에 반영해줘:

1. appFeedback을 apps/*.json에 반영
2. weeklyGoals를 기록
3. 처리 후 ceo-feedback.json을 ceo-feedback-archive/에 이동

간단히 요약해줘.
EOF
    fi
else
    echo "   ⏭️  건너뛰기 (피드백 없음)"
fi
echo ""

# 4. 포트폴리오 요약 재생성
echo "4️⃣  포트폴리오 요약 재생성..."
python3 scripts/generate-portfolio-summary.py 2>/dev/null || echo "   ⚠️  요약 생성 스크립트가 없습니다"
echo ""

# 5. 대시보드 업데이트
echo "5️⃣  대시보드 업데이트..."
python3 scripts/generate-dashboard.py > /dev/null 2>&1
python3 scripts/generate-badges.py > /dev/null 2>&1
cp dashboard/index.html docs/index.html
echo "   ✅ 대시보드 업데이트 완료"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 모든 CEO 입력 처리 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 macOS 앱에서 결과를 확인하세요."
echo "   앱이 자동으로 새로고침됩니다."
echo ""
echo "📊 다음 명령어:"
echo "   ./scripts/ceo-daily-briefing.sh    # 새 브리핑 생성"
echo "   ./scripts/ceo-dashboard.sh         # 현황 확인"
echo "   ./scripts/open-dashboard.sh        # 웹 대시보드"
echo ""
