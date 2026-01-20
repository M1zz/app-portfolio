# 📱 Portfolio CEO - macOS App

23개 iOS 앱을 CEO처럼 관리하는 macOS 네이티브 앱입니다.

## 🎯 개념

```
┌─────────────────┐
│   macOS 앱      │  → 시각화, 알림, 대시보드
│  (읽기 전용)    │
└────────┬────────┘
         │ 파일 감시
         ↓
┌─────────────────┐
│  JSON 파일      │  ← Claude CLI가 업데이트
│ portfolio 데이터│
└────────┬────────┘
         ↑
         │ 명령 실행
┌─────────────────┐
│  Claude CLI     │  → 모든 작업 수행
│  (ceo-*.sh)     │
└─────────────────┘
```

**macOS 앱의 역할:**
- ✅ JSON 파일 읽기 및 시각화
- ✅ 실시간 파일 변경 감지 및 자동 새로고침
- ✅ 일일 브리핑 알림 (매일 9시)
- ✅ 대시보드, 검색, 통계 표시

**Claude CLI의 역할:**
- ✅ 모든 명령 실행 (`ceo-daily-briefing.sh` 등)
- ✅ JSON 파일 업데이트
- ✅ 실제 작업 수행 (태스크 업데이트, 배포 등)

---

## 🚀 빠른 시작

### 1단계: Xcode 프로젝트 생성

```bash
# Xcode 열기
open -a Xcode

# File → New → Project
# macOS → App
# Product Name: PortfolioCEO
# Interface: SwiftUI
# Language: Swift
```

### 2단계: 파일 추가

생성된 `PortfolioCEO` 폴더의 파일들을 Xcode 프로젝트에 드래그 앤 드롭:

```
PortfolioCEO/
├── PortfolioCEOApp.swift       # ✅ 이미 생성됨
├── ContentView.swift            # ✅ 이미 생성됨 (업데이트됨)
├── Models/
│   ├── AppModel.swift          # 추가 필요
│   ├── Portfolio.swift         # 추가 필요
│   └── AppDetailInfo.swift     # ✨ 새 기능: 앱 상세 정보
├── Services/
│   ├── PortfolioService.swift  # 추가 필요
│   ├── NotificationService.swift # 추가 필요
│   └── AppDetailService.swift  # ✨ 새 기능: 앱 상세 정보 저장
└── Views/
    ├── DashboardView.swift     # 추가 필요
    └── AppDetailFormView.swift # ✨ 새 기능: 입력 폼
```

**⚠️ 중요**: 다음 3개 파일을 반드시 Xcode 프로젝트에 추가하세요:
1. `Models/AppDetailInfo.swift`
2. `Services/AppDetailService.swift`
3. `Views/AppDetailFormView.swift`

### 3단계: 누락된 View 파일 생성

다음 파일들을 직접 생성하거나 간단한 placeholder로 만드세요:

**BriefingView.swift**
```swift
import SwiftUI

struct BriefingView: View {
    var body: some View {
        Text("CEO 브리핑")
            .font(.largeTitle)
    }
}
```

**AppsGridView.swift**
```swift
import SwiftUI

struct AppsGridView: View {
    @EnvironmentObject var portfolio: PortfolioService

    var body: some View {
        ScrollView {
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 250))]) {
                ForEach(portfolio.apps) { app in
                    AppCard(app: app)
                }
            }
            .padding()
        }
    }
}

struct AppCard: View {
    let app: AppModel

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Circle()
                    .fill(app.statusColor)
                    .frame(width: 12, height: 12)
                Text(app.name)
                    .font(.headline)
            }

            ProgressView(value: app.completionRate, total: 100)
                .tint(app.progressColor)

            Text("\(Int(app.completionRate))% 완료")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}
```

**DecisionCenterView.swift**
```swift
import SwiftUI

struct DecisionCenterView: View {
    var body: some View {
        VStack {
            Text("의사결정 센터")
                .font(.largeTitle)

            Text("터미널에서 Claude CLI로 명령을 실행하세요")
                .foregroundColor(.secondary)

            Button("일일 브리핑 생성") {
                PortfolioService.shared.openInTerminal(script: "ceo-daily-briefing.sh")
            }
            .buttonStyle(.bordered)
        }
    }
}
```

**QuickSearchView.swift**
```swift
import SwiftUI

struct QuickSearchView: View {
    @EnvironmentObject var portfolio: PortfolioService
    @State private var searchText = ""
    @Environment(\.dismiss) var dismiss

    var filteredApps: [AppModel] {
        if searchText.isEmpty {
            return portfolio.apps
        }
        return portfolio.apps.filter {
            $0.name.localizedCaseInsensitiveContains(searchText) ||
            $0.nameEn.localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        VStack {
            TextField("앱 검색...", text: $searchText)
                .textFieldStyle(.roundedBorder)
                .padding()

            List(filteredApps) { app in
                Button {
                    // 앱 상세 화면으로
                    dismiss()
                } label: {
                    HStack {
                        Circle()
                            .fill(app.statusColor)
                            .frame(width: 8, height: 8)
                        Text(app.name)
                        Spacer()
                        Text("\(Int(app.completionRate))%")
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .frame(width: 500, height: 400)
    }
}
```

**SettingsView.swift**
```swift
import SwiftUI

struct SettingsView: View {
    @AppStorage("portfolioPath") private var portfolioPath = "~/Documents/workspace/code/app-portfolio"
    @AppStorage("enableNotifications") private var enableNotifications = true

    var body: some View {
        Form {
            Section("포트폴리오") {
                TextField("경로", text: $portfolioPath)
                    .textFieldStyle(.roundedBorder)
            }

            Section("알림") {
                Toggle("일일 브리핑 알림", isOn: $enableNotifications)
            }
        }
        .padding()
        .frame(width: 400, height: 300)
    }
}
```

### 4단계: 권한 설정

**Info.plist에 추가:**

1. File → New → File → Property List
2. `Info.plist` 생성
3. 다음 추가:

```xml
<key>NSUserNotificationUsageDescription</key>
<string>일일 CEO 브리핑을 알려드립니다</string>

<key>NSAppleEventsUsageDescription</key>
<string>터미널에서 스크립트를 실행합니다</string>
```

### 5단계: 빌드 및 실행

```
⌘ + R
```

---

## 🎨 주요 기능

### 1. 대시보드
- 23개 앱 전체 현황
- KPI 요약 (완료율, 진행 중, 우선순위)
- 차트 및 그래프
- 위험 요소 알림

### 2. 실시간 업데이트
- JSON 파일 변경 자동 감지
- Claude CLI로 데이터 업데이트하면 앱이 즉시 반영
- 수동 새로고침도 가능 (⌘R)

### 3. 일일 브리핑 알림
- 매일 아침 9시 자동 알림
- 클릭하면 브리핑 화면으로 이동
- 긴급 의사결정 필요 시 추가 알림

### 4. 빠른 검색
- ⌘K로 검색 창 열기
- 앱 이름으로 즉시 검색
- 상태, 진행률 확인

### 5. 터미널 연동
- 버튼 클릭으로 터미널에서 스크립트 실행
- Claude CLI 명령 쉽게 실행
- 결과는 앱에 자동 반영

### 6. 앱 정보 입력 ✨ (NEW)
- Claude 문서 생성을 위한 앱 상세 정보 입력
- 소스 코드 경로, 앱 설명, 주요 기능 입력
- 기술 스택 (UI, 데이터, 플랫폼, 익스텐션)
- 제약사항 및 주의사항 관리
- JSON 파일로 저장 (`app-details/*.json`)
- 저장 후 Claude에게 문서 생성 요청

---

## 🔧 커스터마이징

### 포트폴리오 경로 변경

```swift
// PortfolioService.swift에서 수정
private var portfolioPath: URL {
    let home = fileManager.homeDirectoryForCurrentUser
    return home.appendingPathComponent("YOUR/CUSTOM/PATH")
}
```

### 알림 시간 변경

```swift
// NotificationService.swift에서 수정
dateComponents.hour = 10  // 10시로 변경
dateComponents.minute = 30  // 10:30
```

### 테마 커스터마이징

```swift
// ContentView.swift에서 색상 변경
.tint(.purple)  // 앱 전체 강조 색상
```

---

## 🐛 문제 해결

### JSON 파일을 찾을 수 없음
```bash
# 포트폴리오 경로 확인
ls ~/Documents/workspace/code/app-portfolio/apps/

# 경로가 다르면 PortfolioService.swift 수정
```

### 알림이 오지 않음
```
System Settings → Notifications → Portfolio CEO
→ Allow notifications 활성화
```

### 파일 변경이 감지되지 않음
```swift
// 수동 새로고침: ⌘R 또는 새로고침 버튼 클릭
```

---

## 📚 다음 단계

### 추가 기능 구현 아이디어

1. **브리핑 화면 구현**
   - CEO 브리핑 Markdown 파싱
   - 의사결정 버튼 (A/B 선택)
   - 터미널로 결정 자동 전송

2. **앱 상세 화면**
   - 개별 앱 깊이 있는 정보
   - 태스크 목록 표시
   - 진행 타임라인

3. **통계 및 리포트**
   - 주간/월간 리포트 뷰어
   - 차트 및 인사이트
   - 트렌드 분석

4. **위젯 지원**
   - macOS 위젯으로 요약 정보
   - 알림 센터 통합

---

## 🎯 사용 시나리오

### 아침 루틴
```
1. 9:00 AM - 알림 도착
2. 앱 클릭 → 브리핑 확인
3. 대시보드에서 전체 현황 파악
4. 터미널에서 필요한 명령 실행
```

### 의사결정
```
1. 브리핑에서 긴급 결정 확인
2. 옵션 검토
3. 터미널에서 결정 실행:
   ./scripts/ceo-decision.sh briefing approve
4. 앱이 자동으로 새로고침되어 결과 확인
```

### 진행 상황 확인
```
1. ⌘K로 검색
2. 앱 이름 입력
3. 상세 정보 확인
4. 터미널로 추가 작업
```

---

## 💡 팁

1. **Dock에 고정**: 빠른 접근을 위해 Dock에 앱 고정
2. **단축키 활용**: ⌘K 검색, ⌘R 새로고침
3. **알림 설정**: 방해 금지 모드에서도 알림 받도록 설정
4. **멀티 모니터**: 한 화면에 앱, 다른 화면에 터미널

---

## 🔗 관련 문서

- [APP-DETAILS-GUIDE.md](../APP-DETAILS-GUIDE.md) - ✨ 앱 정보 입력 상세 가이드
- [INTEGRATED-WORKFLOW.md](../INTEGRATED-WORKFLOW.md) - Claude 통합 워크플로우
- [QUICK-COMMANDS.md](../QUICK-COMMANDS.md) - 빠른 명령어
- [CEO-OPERATION-SYSTEM.md](../CEO-OPERATION-SYSTEM.md) - CEO 운영 시스템
- [CEO-QUICK-START.md](../CEO-QUICK-START.md) - CEO 모드 빠른 시작
- [AUTOMATION-GUIDE.md](../AUTOMATION-GUIDE.md) - 자동화 가이드

---

**macOS 앱으로 포트폴리오를 시각화하고, Claude CLI로 실행하세요!** 📱✨
