#!/bin/bash
# 404 에러 해결 및 배포 스크립트

set -e

echo "🔧 GitHub Pages 404 에러 해결 중..."
echo ""

# 1. URL 수정
echo "📝 1. README URL 수정 중..."
sed -i '' 's/hyunholee\.github\.io/M1zz.github.io/g' README.md
sed -i '' 's/\[YOUR-USERNAME\]/M1zz/g' README.md GITHUB-PAGES-SETUP.md QUICK-START.md STATS.md scripts/generate-badges.py

echo "✅ URL 수정 완료"
echo ""

# 2. 대시보드 재생성
echo "📊 2. 대시보드 재생성 중..."
python3 scripts/generate-dashboard.py
python3 scripts/generate-badges.py
cp dashboard/index.html docs/index.html

echo "✅ 대시보드 생성 완료"
echo ""

# 3. 데이터 검증
echo "🔍 3. 데이터 검증 중..."
python3 scripts/validate-portfolio.py

if [ $? -ne 0 ]; then
    echo "❌ 검증 실패!"
    exit 1
fi

echo "✅ 검증 통과"
echo ""

# 4. Git 커밋 및 푸시
echo "📋 4. 변경사항:"
git status --short

echo ""
read -p "커밋하고 GitHub에 푸시하시겠습니까? (y/N): " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo ""
    echo "💾 Git 작업 중..."

    git add .
    git commit -m "🚀 Fix GitHub Pages 404 error and deploy dashboard"
    git push origin main

    echo ""
    echo "✅ GitHub에 푸시 완료!"
    echo ""
    echo "⏳ 1-2분 후 다음 URL에서 확인하세요:"
    echo "   https://m1zz.github.io/app-portfolio/"
    echo ""
    echo "📌 GitHub Pages 설정이 필요하면:"
    echo "   1. https://github.com/M1zz/app-portfolio/settings/pages"
    echo "   2. Source: Deploy from a branch"
    echo "   3. Branch: main / Folder: /docs"
    echo "   4. Save"
else
    echo ""
    echo "⏸️  취소됨"
fi
