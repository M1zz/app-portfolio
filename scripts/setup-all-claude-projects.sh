#!/bin/bash
# 모든 앱의 Claude 프로젝트를 자동 생성

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 모든 앱의 Claude 프로젝트 생성 시작"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# apps/ 폴더의 JSON 파일 읽기
for json_file in apps/*.json; do
    # JSON에서 앱 이름 추출
    APP_NAME_KO=$(grep '"name"' "$json_file" | head -1 | sed 's/.*": "//; s/".*//')
    APP_NAME_EN=$(grep '"nameEn"' "$json_file" | head -1 | sed 's/.*": "//; s/".*//')

    echo "📱 처리 중: $APP_NAME_KO ($APP_NAME_EN)"

    # create-claude-project.sh 실행
    ./scripts/create-claude-project.sh "$APP_NAME_KO" "$APP_NAME_EN"

    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 모든 Claude 프로젝트 생성 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 생성된 프로젝트: $(ls -1 claude-projects/ | wc -l)개"
echo ""
echo "🎯 사용 예시:"
echo "  cd claude-projects/double-reminder"
echo "  claude chat"
echo "  '현재 앱 상태 요약해줘'"
echo ""
echo "📚 공통 리소스:"
echo "  - claude-projects/shared/design-system.md"
echo "  - claude-projects/shared/coding-standards.md"
echo ""
