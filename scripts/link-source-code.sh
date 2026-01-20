#!/bin/bash
# 각 Claude 프로젝트에 소스코드 경로 연결

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 소스코드 경로 연결 시작"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 소스코드 매핑 (앱폴더:로컬경로)
MAPPINGS=(
    "bami-log:$HOME/Documents/workspace/code/BamiLog"
    "clip-keyboard:$HOME/Documents/workspace/code/Token-memo"
    "rapport-map:$HOME/Documents/workspace/code/RapportMap"
    "rebound-journal:$HOME/Documents/workspace/code/Rebound-Journal"
    "donkko-mart:$HOME/Documents/workspace/code/DontGoMart"
    "relax-on:$HOME/Documents/workspace/code/RelaxOn"
    "life-restaurant:$HOME/Documents/workspace/code/RestaurantMap"
    "whisper:$HOME/Documents/workspace/code/Soksak"
    "bucket-climb:$HOME/Documents/workspace/code/BucketClimb"
    "schedule-assistant:$HOME/Documents/workspace/code/ScheduleDensity"
)

# 각 매핑 처리
for mapping in "${MAPPINGS[@]}"; do
    app_folder="${mapping%%:*}"
    source_path="${mapping##*:}"

    PROJECT_FILE="claude-projects/$app_folder/.claude-project"

    if [ ! -f "$PROJECT_FILE" ]; then
        echo "⚠️  $app_folder: .claude-project 없음 (건너뜀)"
        continue
    fi

    if [ ! -d "$source_path" ]; then
        echo "⚠️  $app_folder: 소스코드 없음 at $source_path"
        continue
    fi

    echo "🔗 $app_folder → $source_path"

    # .claude-project에 sourcePath 추가
    jq --arg path "$source_path" '. + {sourcePath: $path}' "$PROJECT_FILE" > "$PROJECT_FILE.tmp"
    mv "$PROJECT_FILE.tmp" "$PROJECT_FILE"

    # context.md에 소스코드 정보 추가
    CONTEXT_FILE="claude-projects/$app_folder/context.md"
    if [ -f "$CONTEXT_FILE" ]; then
        if ! grep -q "## 소스코드 위치" "$CONTEXT_FILE"; then
            cat >> "$CONTEXT_FILE" << EOF

## 소스코드 위치

\`$source_path\`

**주의**: 이 경로의 실제 코드를 수정합니다. 작업 전 백업 권장.
EOF
        fi
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 소스코드 경로 연결 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 사용 방법:"
echo "  cd claude-projects/rapport-map"
echo "  claude chat"
echo "  '현재 코드 구조 분석해줘'"
echo ""
