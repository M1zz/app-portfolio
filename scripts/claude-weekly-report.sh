#!/bin/bash
# Claude 기반 주간 리포트 자동 생성
# 사용법: ./scripts/claude-weekly-report.sh

set -e

WEEK=$(date +"%Y-%m-%d")
REPORT_FILE="reports/weekly-$WEEK.md"

echo "📊 주간 리포트 생성 중..."
echo "   파일: $REPORT_FILE"
echo ""

claude << EOF
현재 포트폴리오 데이터를 분석해서 주간 리포트를 생성해줘:

1. portfolio-summary.json과 apps/ 폴더의 모든 JSON 파일을 읽어
2. 다음 내용으로 $REPORT_FILE 파일을 생성:
   - 이번 주 완료된 태스크들 (recentlyCompleted 참고)
   - 현재 진행 중인 태스크들 (status: in-progress)
   - 우선순위 높은 앱들의 다음 주 계획 (nextTasks)
   - 주요 지표 변화 (전체 완료율, 앱별 진행도)
   - 배포 예정 앱 목록

리포트는 간결하고 실행 가능한 형태로 작성해줘.
EOF

echo ""
echo "✅ 주간 리포트 생성 완료: $REPORT_FILE"
echo "   확인: cat $REPORT_FILE"
