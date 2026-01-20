# ⚡ PortfolioCEO 빠른 시작 가이드

모든 View 파일이 생성되었습니다! 이제 Xcode 프로젝트만 만들면 됩니다.

## ✅ 완료된 작업

- ✅ PortfolioCEOApp.swift
- ✅ ContentView.swift
- ✅ Models/AppModel.swift
- ✅ Models/Portfolio.swift
- ✅ Services/PortfolioService.swift
- ✅ Services/NotificationService.swift
- ✅ Services/DecisionQueueService.swift
- ✅ Services/RequestQueueService.swift
- ✅ Views/DashboardView.swift
- ✅ Views/BriefingView.swift (새로 생성됨!)
- ✅ Views/AppsGridView.swift (새로 생성됨!)
- ✅ Views/DecisionCenterView.swift (새로 생성됨!)
- ✅ Views/QuickSearchView.swift (새로 생성됨!)
- ✅ Views/SettingsView.swift (새로 생성됨!)

## 🔨 다음 단계: Xcode 프로젝트 생성 (3분)

### 1단계: 새 프로젝트 만들기

Xcode가 이미 열려있습니다. 다음을 수행하세요:

1. **File** → **New** → **Project** (⌘⇧N)
2. **macOS** 탭 선택
3. **App** 선택 후 **Next**

### 2단계: 프로젝트 설정

```
Product Name: PortfolioCEO
Team: (본인 Apple Developer 계정)
Organization Identifier: com.leeo
Bundle Identifier: com.leeo.PortfolioCEO
Interface: SwiftUI
Language: Swift
```

**중요:** "Use Core Data" 체크 해제 ❌

### 3단계: 저장 위치

```
위치: /Users/hyunholee/Documents/workspace/code/app-portfolio/PortfolioCEO

⚠️  주의: "PortfolioCEO" 폴더를 선택하세요!
         (현재 폴더가 아닌 한 단계 위 폴더)
```

Xcode가 물어보면:
- **"Replace" 또는 "Merge"** 선택 (기존 파일 유지)

### 4단계: 기존 파일 확인 및 정리

프로젝트가 생성되면 Xcode는 기본 파일을 만듭니다:
- `PortfolioCEOApp.swift` (이미 있음 - 우리 버전 사용)
- `ContentView.swift` (이미 있음 - 우리 버전 사용)

왼쪽 Navigator에서:

1. Xcode가 생성한 중복 파일이 있다면 삭제
2. 우리가 만든 파일들이 제대로 포함되었는지 확인:
   ```
   PortfolioCEO/
   ├── PortfolioCEOApp.swift
   ├── ContentView.swift
   ├── Models/
   │   ├── AppModel.swift
   │   └── Portfolio.swift
   ├── Services/
   │   ├── PortfolioService.swift
   │   ├── NotificationService.swift
   │   ├── DecisionQueueService.swift
   │   └── RequestQueueService.swift
   └── Views/
       ├── DashboardView.swift
       ├── BriefingView.swift
       ├── AppsGridView.swift
       ├── DecisionCenterView.swift
       ├── QuickSearchView.swift
       └── SettingsView.swift
   ```

만약 Models/, Services/, Views/ 폴더가 안 보이면:
1. PortfolioCEO 폴더 우클릭
2. **Add Files to "PortfolioCEO"**
3. Models/, Services/, Views/ 폴더 선택
4. Options:
   - ✅ Copy items if needed
   - ✅ Create groups
   - ✅ Add to targets: PortfolioCEO

### 5단계: Build Settings 설정

1. 프로젝트 Navigator에서 최상위 **PortfolioCEO** (파란 아이콘) 클릭
2. **TARGETS** → **PortfolioCEO** 선택
3. **Signing & Capabilities** 탭:
   - **Team**: 본인 계정 선택
   - **Bundle Identifier**: `com.leeo.PortfolioCEO` 확인

4. **Info** 탭:
   - **Custom macOS Application Target Properties** 섹션에서 `+` 클릭
   - 다음 두 항목 추가:

   ```
   Key: NSUserNotificationUsageDescription
   Type: String
   Value: 일일 CEO 브리핑을 알려드립니다

   Key: NSAppleEventsUsageDescription
   Type: String
   Value: 터미널에서 스크립트를 실행합니다
   ```

### 6단계: 빌드 및 실행!

```
⌘ + B    # 빌드
⌘ + R    # 실행
```

빌드 에러가 나면:
- PortfolioService.swift의 `openInTerminal` 메서드 확인
- 모든 파일이 Target Membership에 포함되었는지 확인

### 7단계: 테스트

앱이 실행되면:
1. 대시보드에 앱 23개가 표시되는지 확인
2. ⌘K 눌러서 Quick Search 테스트
3. ⌘R 눌러서 새로고침 테스트

## 🐛 문제 해결

### "Cannot find PortfolioService in scope"
→ Services/ 폴더가 프로젝트에 추가되지 않음
→ Step 4 다시 수행

### "Duplicate symbol"
→ Xcode가 생성한 기본 파일과 우리 파일이 충돌
→ 중복 파일 삭제

### 빌드는 되는데 앱이 크래시
→ JSON 파일 경로 확인
→ `~/Documents/workspace/code/app-portfolio` 폴더에 `apps/` 폴더와 `portfolio-summary.json` 있는지 확인

## 📚 더 자세한 내용

BUILD-INSTRUCTIONS.md 참고

---

**준비 완료! 이제 Xcode에서 3분만 작업하면 됩니다!** 🚀
