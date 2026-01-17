#!/bin/bash
# Claude 기반 태스크 자동 업데이트 스크립트
# 사용법: ./scripts/claude-update-task.sh "앱이름" "태스크명" "상태"
# 예시: ./scripts/claude-update-task.sh "라포 맵" "클라우드 백업기능" "done"

set -e

APP_NAME="$1"
TASK_NAME="$2"
STATUS="$3"

if [ -z "$APP_NAME" ] || [ -z "$TASK_NAME" ] || [ -z "$STATUS" ]; then
    echo "❌ 사용법: $0 \"앱이름\" \"태스크명\" \"상태\""
    echo ""
    echo "상태 옵션:"
    echo "  - done (완료)"
    echo "  - in-progress (진행중)"
    echo "  - not-started (미시작)"
    echo ""
    echo "예시:"
    echo "  $0 \"라포 맵\" \"클라우드 백업기능\" \"done\""
    exit 1
fi

# Claude에게 작업 요청
echo "🤖 Claude가 태스크를 업데이트하고 있습니다..."
echo "   앱: $APP_NAME"
echo "   태스크: $TASK_NAME"
echo "   상태: $STATUS"
echo ""

claude << EOF
apps/ 폴더에서 "$APP_NAME" 앱의 JSON 파일을 찾아서 다음 작업을 해줘:

1. allTasks 배열에서 "$TASK_NAME" 태스크를 찾아 status를 "$STATUS"로 변경
2. stats를 재계산해서 업데이트 (totalTasks, done, inProgress, notStarted)
3. nextTasks와 recentlyCompleted 배열 업데이트
4. portfolio-summary.json 재생성

변경사항을 명확하게 설명해줘.
EOF

echo ""
echo "✅ 완료! Git 커밋을 원하면 다음 명령어를 실행하세요:"
echo "   git add . && git commit -m \"Update: $APP_NAME - $TASK_NAME ($STATUS)\""
