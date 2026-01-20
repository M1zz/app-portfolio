#!/bin/bash
# CEO 운영 시스템 초기화

set -e

echo "👔 CEO Operation System 초기화 중..."
echo ""

# 1. 필요한 폴더 생성
echo "📁 1. 폴더 구조 생성..."
mkdir -p reports/ceo-briefings
mkdir -p reports/ceo-reviews
mkdir -p decisions

# 2. 스크립트 실행 권한 부여
echo "🔧 2. 스크립트 권한 설정..."
chmod +x scripts/ceo-*.sh

# 3. 첫 브리핑 생성
echo "📊 3. 첫 번째 브리핑 생성..."
./scripts/ceo-daily-briefing.sh

# 4. 대시보드 생성
echo "📈 4. CEO 대시보드 생성..."
python3 scripts/generate-dashboard.py

# 5. 완료 메시지
echo ""
echo "✅ CEO 운영 시스템 초기화 완료!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "👔 Welcome to CEO Operation Mode"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 다음 단계:"
echo ""
echo "1️⃣  오늘의 브리핑 확인"
echo "   ./scripts/ceo-daily-briefing.sh"
echo ""
echo "2️⃣  전체 현황 파악"
echo "   ./scripts/ceo-dashboard.sh"
echo ""
echo "3️⃣  의사결정 실행"
echo "   ./scripts/ceo-decision.sh briefing approve"
echo ""
echo "4️⃣  시각적 대시보드"
echo "   ./scripts/open-dashboard.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 매일 아침 루틴:"
echo "   ./scripts/ceo-daily-briefing.sh && ./scripts/ceo-dashboard.sh"
echo ""
echo "📅 매주 일요일 저녁:"
echo "   ./scripts/ceo-weekly-review.sh"
echo ""
echo "📚 자세한 가이드:"
echo "   cat CEO-OPERATION-SYSTEM.md"
echo ""
echo "🚀 이제 당신은 CEO입니다. 전략에 집중하세요!"
