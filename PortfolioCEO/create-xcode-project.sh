#!/bin/bash
# Create new Xcode project for PortfolioCEO

echo "🔨 Creating PortfolioCEO Xcode project..."

# Open Xcode and create new project
osascript << EOF
tell application "Xcode"
    activate
end tell

display dialog "다음 단계를 따라주세요:

1. File → New → Project (⌘⇧N)
2. macOS 탭 → App 선택
3. Product Name: PortfolioCEO
4. Team: 본인 계정 선택
5. Organization Identifier: com.leeo
6. Bundle Identifier: com.leeo.PortfolioCEO
7. Interface: SwiftUI
8. Language: Swift
9. Use Core Data: 체크 해제

10. 저장 위치를 현재 폴더로 선택

완료되면 BUILD-INSTRUCTIONS.md의 5단계부터 계속 진행하세요." buttons {"확인"} default button 1
EOF

echo "✅ Xcode가 실행되었습니다."
echo "📖 자세한 내용은 BUILD-INSTRUCTIONS.md를 참고하세요."

