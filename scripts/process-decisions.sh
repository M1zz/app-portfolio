#!/bin/bash
# CEO 결정사항 처리 스크립트

set -e

QUEUE_FILE="decisions-queue.json"
PORTFOLIO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PORTFOLIO_DIR"

if [ ! -f "$QUEUE_FILE" ]; then
    echo "⚠️  $QUEUE_FILE 파일이 없습니다."
    echo '{"pendingDecisions":[],"completedDecisions":[]}' > "$QUEUE_FILE"
    echo "✅ 빈 큐 파일을 생성했습니다."
    exit 0
fi

echo "📋 CEO 결정사항 처리 중..."
echo ""

claude << EOF
$QUEUE_FILE 파일을 읽어서 pendingDecisions를 처리해줘:

각 결정에 대해:

1. **feature-decision** (기능 결정):
   - selectedOption에 따라 해당 앱에 태스크 추가
   - apps/{앱파일}.json의 allTasks에 추가
   - stats 업데이트
   - notes에 CEO의 메모 추가

2. **priority-change** (우선순위 변경):
   - apps/{앱파일}.json의 priority 필드 업데이트
   - action이 "pause"면 notes에 기록

3. **task-update** (태스크 상태 변경):
   - 해당 태스크의 status 업데이트
   - stats 재계산

처리 후:
- 각 결정을 completedDecisions로 이동
- status: "completed"
- completedAt: 현재 시간
- result: "success"
- pendingDecisions에서 제거

변경사항:
- apps/*.json 업데이트됨
- $QUEUE_FILE 업데이트됨
- portfolio-summary.json 재생성

실행 결과를 간단히 요약해서 보여줘.
EOF

echo ""
echo "✅ 결정사항 처리 완료!"
echo "   macOS 앱에서 결과를 확인하세요."
