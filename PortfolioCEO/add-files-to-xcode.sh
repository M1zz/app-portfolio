#!/bin/bash

# Xcode 프로젝트에 새 파일 추가 스크립트

echo "📦 Xcode 프로젝트에 새 파일 추가 중..."

cd "$(dirname "$0")"

# Xcode가 설치되어 있는지 확인
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode가 설치되어 있지 않습니다."
    exit 1
fi

PROJECT_FILE="PortfolioCEO.xcodeproj"

# 프로젝트 파일이 있는지 확인
if [ ! -d "$PROJECT_FILE" ]; then
    echo "❌ PortfolioCEO.xcodeproj를 찾을 수 없습니다."
    exit 1
fi

echo "✅ 프로젝트 파일 발견: $PROJECT_FILE"
echo ""
echo "⚠️  중요: 다음 파일들을 Xcode에서 수동으로 추가해주세요:"
echo ""
echo "1. Xcode에서 PortfolioCEO.xcodeproj를 엽니다"
echo ""
echo "2. Models 폴더를 우클릭 → Add Files to \"PortfolioCEO\""
echo "   - PortfolioCEO/Models/AppDetailInfo.swift 추가"
echo ""
echo "3. Services 폴더를 우클릭 → Add Files to \"PortfolioCEO\""
echo "   - PortfolioCEO/Services/AppDetailService.swift 추가"
echo ""
echo "4. Views 폴더를 우클릭 → Add Files to \"PortfolioCEO\""
echo "   - PortfolioCEO/Views/AppDetailFormView.swift 추가"
echo ""
echo "5. ⌘ + B 로 빌드"
echo ""
echo "또는 아래 명령어로 빌드만 시도:"
echo "  cd PortfolioCEO && xcodebuild -project PortfolioCEO.xcodeproj -scheme PortfolioCEO"
echo ""
