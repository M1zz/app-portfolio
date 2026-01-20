# 🔨 Xcode 프로젝트 빌드 가이드

손상된 프로젝트를 복구하고 처음부터 만드는 방법입니다.

---

## ⚡ 방법 1: Xcode GUI로 새 프로젝트 생성 (추천!)

### 1단계: Xcode에서 새 프로젝트 생성

```bash
# Xcode 열기
open -a Xcode
```

### 2단계: 새 프로젝트 만들기

1. **File** → **New** → **Project** (⌘⇧N)
2. **macOS** 탭 선택
3. **App** 선택
4. **Next** 클릭

### 3단계: 프로젝트 설정

```
Product Name: PortfolioCEO
Team: (본인 계정)
Organization Identifier: com.leeo
Bundle Identifier: com.leeo.PortfolioCEO
Interface: SwiftUI
Language: Swift
```

**중요:** "Use Core Data" 체크 해제

### 4단계: 저장 위치

```
현재 위치: ~/Documents/workspace/code/app-portfolio/
폴더 선택: PortfolioCEO (기존 폴더 덮어쓰기 또는 병합)
```

### 5단계: 파일 추가

Xcode 프로젝트가 생성되면:

1. 왼쪽 Navigator에서 **PortfolioCEO** 폴더 우클릭
2. **Add Files to "PortfolioCEO"** 선택
3. 다음 폴더들을 선택:
   - `Models/` 폴더
   - `Services/` 폴더
   - `Views/` 폴더
4. **Options:**
   - ✅ Copy items if needed
   - ✅ Create groups
   - ✅ Add to targets: PortfolioCEO

### 6단계: 기본 파일 교체

생성된 기본 파일들을 우리 파일로 교체:

1. **PortfolioCEOApp.swift** → 우리 버전으로 교체
2. **ContentView.swift** → 우리 버전으로 교체

### 7단계: 누락된 View 파일 생성

다음 파일들을 Xcode에서 직접 생성 (⌘N):

#### BriefingView.swift
```swift
import SwiftUI

struct BriefingView: View {
    @EnvironmentObject var portfolio: PortfolioService

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text("CEO 일일 브리핑")
                    .font(.largeTitle)
                    .bold()

                Text("터미널에서 ./scripts/ceo-daily-briefing.sh를 실행하세요")
                    .foregroundColor(.secondary)

                Button("터미널에서 브리핑 생성") {
                    PortfolioService.shared.openInTerminal(script: "ceo-daily-briefing.sh")
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
    }
}
```

#### AppsGridView.swift
```swift
import SwiftUI

struct AppsGridView: View {
    @EnvironmentObject var portfolio: PortfolioService

    var body: some View {
        ScrollView {
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 280))], spacing: 20) {
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
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Circle()
                    .fill(app.statusColor)
                    .frame(width: 12, height: 12)

                Text(app.name)
                    .font(.headline)

                Spacer()

                Text("v\(app.currentVersion)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            ProgressView(value: app.completionRate, total: 100)
                .tint(app.progressColor)

            HStack {
                Text("\(Int(app.completionRate))% 완료")
                    .font(.caption)
                Spacer()
                Text("\(app.stats.done)/\(app.stats.totalTasks)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            if let nextTask = app.nextTasks.first {
                Text("다음: \(nextTask)")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}
```

#### DecisionCenterView.swift
```swift
import SwiftUI

struct DecisionCenterView: View {
    @EnvironmentObject var portfolio: PortfolioService
    @StateObject private var decisionQueue = DecisionQueueService.shared
    @StateObject private var requestQueue = RequestQueueService.shared

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // 대기 중인 결정사항
                if !decisionQueue.pendingDecisions.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("⏳ 대기 중인 결정")
                            .font(.headline)

                        ForEach(decisionQueue.pendingDecisions) { decision in
                            DecisionCard(decision: decision)
                        }
                    }
                }

                // 대기 중인 요청사항
                if !requestQueue.requests.filter({ $0.status == "pending" }).isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("📝 대기 중인 요청")
                            .font(.headline)

                        ForEach(requestQueue.requests.filter { $0.status == "pending" }) { request in
                            RequestCard(request: request)
                        }
                    }
                }

                // 실행 버튼
                Divider()

                VStack(spacing: 12) {
                    Text("🤖 처리 실행")
                        .font(.headline)

                    Button("모든 결정/요청 처리") {
                        PortfolioService.shared.openInTerminal(script: "ceo-process-all.sh")
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                }
            }
            .padding()
        }
    }
}

struct DecisionCard: View {
    let decision: CEODecision

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(decision.appName)
                .font(.subheadline)
                .bold()

            if let issue = decision.issue {
                Text(issue)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            if let option = decision.selectedOption {
                HStack {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                    Text("선택: \(option)")
                        .font(.caption)
                }
            }
        }
        .padding()
        .background(Color.blue.opacity(0.1))
        .cornerRadius(8)
    }
}

struct RequestCard: View {
    let request: CEORequest

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(request.appName)
                .font(.subheadline)
                .bold()

            if let title = request.title {
                Text(title)
                    .font(.caption)
            }

            HStack {
                Text(request.type)
                    .font(.caption2)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.orange.opacity(0.2))
                    .cornerRadius(4)

                if let priority = request.priority {
                    Text(priority)
                        .font(.caption2)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.red.opacity(0.2))
                        .cornerRadius(4)
                }
            }
        }
        .padding()
        .background(Color.orange.opacity(0.1))
        .cornerRadius(8)
    }
}
```

#### QuickSearchView.swift
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
        VStack(spacing: 0) {
            // 검색 바
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.secondary)

                TextField("앱 검색...", text: $searchText)
                    .textFieldStyle(.plain)

                if !searchText.isEmpty {
                    Button {
                        searchText = ""
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding()
            .background(Color(NSColor.controlBackgroundColor))

            Divider()

            // 결과 리스트
            List(filteredApps) { app in
                Button {
                    // 앱 선택 시 동작
                    dismiss()
                } label: {
                    HStack {
                        Circle()
                            .fill(app.statusColor)
                            .frame(width: 8, height: 8)

                        VStack(alignment: .leading) {
                            Text(app.name)
                                .font(.body)
                            Text(app.nameEn)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }

                        Spacer()

                        Text("\(Int(app.completionRate))%")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .buttonStyle(.plain)
            }
        }
        .frame(width: 500, height: 400)
    }
}
```

#### SettingsView.swift
```swift
import SwiftUI

struct SettingsView: View {
    @AppStorage("portfolioPath") private var portfolioPath = "~/Documents/workspace/code/app-portfolio"
    @AppStorage("enableNotifications") private var enableNotifications = true
    @AppStorage("dailyBriefingTime") private var dailyBriefingTime = 9

    var body: some View {
        Form {
            Section("포트폴리오") {
                TextField("경로", text: $portfolioPath)
                    .textFieldStyle(.roundedBorder)

                Button("폴더 선택...") {
                    selectFolder()
                }
            }

            Section("알림") {
                Toggle("일일 브리핑 알림", isOn: $enableNotifications)

                if enableNotifications {
                    Stepper("알림 시간: \(dailyBriefingTime)시", value: $dailyBriefingTime, in: 0...23)
                }
            }

            Section("정보") {
                LabeledContent("버전", value: "1.0.0")
                LabeledContent("빌드", value: "1")
            }
        }
        .formStyle(.grouped)
        .padding()
        .frame(width: 450, height: 350)
    }

    func selectFolder() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false

        if panel.runModal() == .OK {
            if let url = panel.url {
                portfolioPath = url.path
            }
        }
    }
}
```

### 8단계: 빌드 설정

1. 프로젝트 Navigator에서 최상위 **PortfolioCEO** 클릭
2. **Targets** → **PortfolioCEO** 선택
3. **Signing & Capabilities** 탭:
   - Team 선택
   - Bundle Identifier 확인
4. **Info** 탭에서 추가:
   - Key: `NSUserNotificationUsageDescription`
   - Value: `일일 CEO 브리핑을 알려드립니다`
   - Key: `NSAppleEventsUsageDescription`
   - Value: `터미널에서 스크립트를 실행합니다`

### 9단계: 빌드 및 실행

```
⌘ + B    # 빌드
⌘ + R    # 실행
```

---

## 🐛 문제 해결

### "Cannot find PortfolioService in scope"

→ Services 폴더가 제대로 추가되지 않음
→ 왼쪽 Navigator에서 파일 확인, Target Membership 체크

### "Duplicate symbol TaskStats"

→ Portfolio.swift에서 TaskStats 정의 제거
→ AppModel.swift에만 존재하도록

### 빌드는 되는데 실행 시 크래시

→ JSON 파일 경로 확인
→ PortfolioService.swift의 portfolioPath 수정

---

## ⚡ 방법 2: 터미널로 프로젝트 생성

더 빠르게 하려면:

```bash
cd ~/Documents/workspace/code/app-portfolio

# 기존 프로젝트 제거
rm -rf PortfolioCEO/PortfolioCEO.xcodeproj

# 새 Swift Package 생성 (선택사항)
cd PortfolioCEO
swift package init --type executable

# 하지만 macOS 앱은 GUI로 만드는 게 더 쉽습니다!
```

---

## 📋 체크리스트

빌드 전 확인:

- [ ] Xcode 14.0 이상 설치
- [ ] macOS 13.0 이상
- [ ] 모든 .swift 파일이 프로젝트에 추가됨
- [ ] Target Membership 체크됨
- [ ] Info.plist에 권한 추가
- [ ] Team 선택됨
- [ ] Bundle Identifier 설정됨

빌드 후 확인:

- [ ] 앱이 실행됨
- [ ] 포트폴리오 데이터 로드됨
- [ ] 대시보드에 앱들이 표시됨
- [ ] 검색 (⌘K) 작동
- [ ] 새로고침 (⌘R) 작동

---

## 🎯 최소 기능으로 빌드

시간이 없다면 View 파일들을 최소한으로:

```swift
struct BriefingView: View {
    var body: some View { Text("브리핑") }
}

struct AppsGridView: View {
    var body: some View { Text("앱 목록") }
}

struct DecisionCenterView: View {
    var body: some View { Text("의사결정") }
}

struct QuickSearchView: View {
    var body: some View { Text("검색") }
}

struct SettingsView: View {
    var body: some View { Text("설정") }
}
```

나중에 천천히 기능 추가!

---

**이제 Xcode GUI로 새 프로젝트를 만드세요!**
**5분이면 충분합니다!** ⚡
