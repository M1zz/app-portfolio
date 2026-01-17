#!/bin/bash
# GitHub Pages 자동 배포 스크립트

set -e

echo "🚀 GitHub Pages 배포 준비 중..."
echo ""

# 1. 대시보드 생성
echo "📊 1. 대시보드 생성..."
python3 scripts/generate-dashboard.py

# 2. 통계 페이지 생성
echo "📈 2. 통계 페이지 생성..."
python3 scripts/generate-badges.py

# 3. docs 폴더로 복사
echo "📁 3. docs 폴더로 복사..."
mkdir -p docs
cp dashboard/index.html docs/index.html

# 4. 데이터 검증
echo "🔍 4. 데이터 검증..."
python3 scripts/validate-portfolio.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 검증 실패! 수정 후 다시 시도하세요."
    exit 1
fi

# 5. Git 상태 확인
echo ""
echo "📋 5. 변경사항 확인..."
git status --short

echo ""
read -p "Git에 커밋하고 푸시하시겠습니까? (y/N): " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo ""
    echo "💾 Git 커밋 중..."

    git add dashboard/index.html docs/index.html STATS.md
    git commit -m "🚀 Deploy: Update dashboard and stats"

    echo "📤 GitHub에 푸시 중..."
    git push origin main

    echo ""
    echo "✅ 배포 완료!"
    echo ""
    echo "🌐 약 1-2분 후 다음 URL에서 확인 가능:"
    echo "   https://hyunholee.github.io/app-portfolio/"
    echo ""
    echo "💡 GitHub 유저네임이 다르면 URL을 수정하세요."
else
    echo ""
    echo "⏸️  배포 취소"
    echo "   수동으로 커밋하려면:"
    echo "   git add ."
    echo "   git commit -m \"Update dashboard\""
    echo "   git push"
fi
