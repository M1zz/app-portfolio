# ⚡ 빠른 빌드 가이드

5분 안에 Portfolio CEO 앱을 빌드하는 방법입니다.

## 🎯 전제조건

- macOS 13.0 이상
- Xcode 14.0 이상
- Swift 5.7 이상

## 🚀 1분 빌드

### 방법 1: Xcode에서 새 프로젝트 생성 (추천)

```bash
# 1. Xcode 열기
open -a Xcode

# 2. Create a new Xcode project
#    → macOS → App
#    → Product Name: PortfolioCEO
#    → Interface: SwiftUI
#    → Language: Swift
#    → 저장 위치: 현재 폴더

# 3. 제공된 파일들을 Xcode 프로젝트에 드래그 앤 드롭
#    - Models/
#    - Services/
#    - Views/
```

### 방법 2: 제공된 템플릿 사용

이미 생성된 Swift 파일들을 Xcode 프로젝트에 추가만 하면 됩니다.

## 📁 파일 구조

```
PortfolioCEO/
├── PortfolioCEO/
│   ├── PortfolioCEOApp.swift         ✅ 메인 앱
│   ├── ContentView.swift              ✅ 루트 뷰
│   ├── Models/
│   │   ├── AppModel.swift            ✅ 앱 데이터 모델
│   │   └── Portfolio.swift           ✅ 포트폴리오 모델
│   ├── Services/
│   │   ├── PortfolioService.swift    ✅ 데이터 서비스
│   │   └── NotificationService.swift ✅ 알림 서비스
│   └── Views/
│       ├── DashboardView.swift       ✅ 대시보드
│       ├── BriefingView.swift        ⚠️ placeholder 필요
│       ├── AppsGridView.swift        ⚠️ placeholder 필요
│       ├── DecisionCenterView.swift  ⚠️ placeholder 필요
│       ├── QuickSearchView.swift     ⚠️ placeholder 필요
│       └── SettingsView.swift        ⚠️ placeholder 필요
└── README.md
```

## ⚠️ 필수 수정사항

### 1. Portfolio.swift 수정

`TaskStats`가 중복 정의되어 있습니다. 다음과 같이 수정:

```swift
// Portfolio.swift에서 제거
// TaskStats는 AppModel.swift에 이미 정의되어 있음

// 또는 import 추가
import AppModel  // 만약 별도 모듈이라면
```

### 2. 포트폴리오 경로 설정

`PortfolioService.swift`에서 경로 확인:

```swift
private var portfolioPath: URL {
    let home = fileManager.homeDirectoryForCurrentUser
    // 본인의 경로로 변경
    return home.appendingPathComponent("Documents/workspace/code/app-portfolio")
}
```

### 3. Info.plist 권한 추가

Xcode에서:
1. Target → Info
2. Custom macOS Application Target Properties에 추가:

```
NSUserNotificationUsageDescription
→ "일일 CEO 브리핑을 알려드립니다"

NSAppleEventsUsageDescription
→ "터미널에서 스크립트를 실행합니다"
```

## 🏗️ 빌드

```bash
# Xcode에서
⌘ + B  # 빌드
⌘ + R  # 실행
```

## 🐛 빌드 에러 해결

### 에러: "Cannot find PortfolioService in scope"

→ 파일을 Xcode 프로젝트에 추가했는지 확인
→ Target Membership 체크

### 에러: "Cannot find type 'AppModel'"

→ Models 폴더의 모든 파일이 프로젝트에 포함되었는지 확인

### 에러: Duplicate 'TaskStats'

→ Portfolio.swift에서 TaskStats 정의 제거
→ AppModel.swift에만 존재하도록

## ✅ 빌드 성공 후

1. 앱 실행
2. 포트폴리오 데이터 자동 로드
3. 대시보드 확인
4. 알림 권한 허용

## 🎯 최소 기능 버전

시간이 없다면 다음 View들을 간단하게 만드세요:

```swift
// BriefingView.swift
struct BriefingView: View {
    var body: some View {
        Text("브리핑")
    }
}

// 나머지도 동일하게
```

나중에 천천히 기능을 추가하세요!

---

**5분 안에 실행 가능한 앱을 만들고, 나중에 개선하세요!** ⚡
