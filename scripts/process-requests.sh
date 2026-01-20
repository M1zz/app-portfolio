#!/bin/bash
# CEO 요구사항 처리 스크립트

set -e

QUEUE_FILE="requests-queue.json"
PORTFOLIO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PORTFOLIO_DIR"

if [ ! -f "$QUEUE_FILE" ]; then
    echo "⚠️  $QUEUE_FILE 파일이 없습니다."
    echo '{"requests":[]}' > "$QUEUE_FILE"
    exit 0
fi

echo "📝 CEO 요구사항 처리 중..."
echo ""

claude << EOF
$QUEUE_FILE 파일을 읽어서 status가 "pending"인 요청들을 처리해줘:

각 요청 type에 따라:

1. **new-task** (새 태스크):
   - apps/{appName}.json에 새 태스크 추가
   - title을 태스크 name으로
   - description을 notes로 (있으면)
   - priority에 따라 nextTasks 순서 조정
   - targetVersion 설정 (있으면)
   - status: "not-started"
   - stats 업데이트

2. **bug-report** (버그 리포트):
   - 새 태스크로 추가
   - severity가 "high"면 priority도 high
   - status: "not-started"
   - 태스크명 앞에 "[버그]" 접두사

3. **note** (메모):
   - apps/{appName}.json의 notes 필드에 추가
   - 타임스탬프와 함께 기록

처리 후:
- 각 요청의 status를 "processed"로 변경
- processedAt: 현재 시간

변경사항:
- apps/*.json 업데이트
- $QUEUE_FILE 업데이트
- portfolio-summary.json 재생성

처리 결과 요약
EOF

echo ""
echo "✅ 요구사항 처리 완료!"
