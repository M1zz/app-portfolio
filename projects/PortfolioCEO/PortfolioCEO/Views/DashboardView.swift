import SwiftUI
import Charts

struct DashboardView: View {
    @EnvironmentObject var portfolio: PortfolioService
    @StateObject private var decisionQueue = DecisionQueueService.shared
    @State private var showingAIAnalysis = false
    // @State private var aiAnalysisResults: [String: [PlanningFeature]] = []
    @State private var showingPlanDocument = false
    @State private var planDocument = ""
    @State private var planTitle = ""

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // 프로젝트 정보 입력 필요 알림 (최우선)
                MissingInfoAlertCard()

                // 버전 변경 감지 알림
                VersionChangesAlertCard()

                // 전체 앱 개수 요약
                TotalAppsCard()

                // 워크플로우 상태 카드
                WorkflowStatusCard()

                // 최근 활동
                RecentActivityCard()

                // 위험 요소
                if !riskyApps.isEmpty {
                    RiskAlertsCard(apps: riskyApps)
                }

                // iCloud 동기화 (하단 배치)
                iCloudSyncCard()
            }
            .padding()
        }
        // .sheet(isPresented: $showingPlanDocument) {
        //     PlanningDocumentView(document: planDocument, title: planTitle)
        // }
        .onAppear {
            portfolio.loadWorkflowStatus()
            decisionQueue.loadQueue()
        }
    }

    private var riskyApps: [AppModel] {
        portfolio.apps.filter { $0.healthStatus == .critical }
    }

    // private func runAIAnalysis() {
    //     let results = AIAnalysisService.shared.analyzeMutipleProjects(apps: portfolio.apps)
    //     aiAnalysisResults = results
    //     showingAIAnalysis = true
    // }

    // private func generateComprehensivePlan() {
    //     planDocument = PlanningDocumentGenerator.shared.generateComprehensivePlan(for: portfolio.apps)
    //     planTitle = "프로젝트 종합 기획서"
    //     showingPlanDocument = true
    // }

    // private func generateIndividualPlan(for app: AppModel) {
    //     planDocument = PlanningDocumentGenerator.shared.generateProjectPlan(for: app)
    //     planTitle = "\(app.name) 기획서"
    //     showingPlanDocument = true
    // }
}

// MARK: - Missing Info Alert Card
struct MissingInfoAlertCard: View {
    @EnvironmentObject var portfolio: PortfolioService
    @State private var selectedApp: AppModel?
    @State private var showingProjectInfo = false

    private var appsWithMissingInfo: [AppModel] {
        portfolio.apps.filter { !$0.hasRequiredInfo }
    }

    var body: some View {
        ZStack {
            if !appsWithMissingInfo.isEmpty {
                alertCard
            }
        }
        .sheet(isPresented: $showingProjectInfo) {
            if let app = selectedApp {
                ProjectInfoSheet(app: app)
                    .onAppear {
                        print("📋 [MissingInfoAlert] ProjectInfoSheet 열림: \(app.name)")
                    }
            }
        }
        .onChange(of: showingProjectInfo) { _, newValue in
            print("🔄 [MissingInfoAlert] showingProjectInfo 변경: \(newValue)")
            if !newValue {
                print("  → 시트가 닫혔습니다")
            } else if selectedApp == nil {
                print("  ⚠️ selectedApp이 nil입니다!")
            }
        }
    }

    private var alertCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            // 헤더
            HStack(spacing: 12) {
                Image(systemName: "exclamationmark.triangle.fill")
                    .font(.title2)
                    .foregroundColor(.red)

                VStack(alignment: .leading, spacing: 4) {
                    Text("⚠️ 프로젝트 정보 입력 필요")
                        .font(.headline)
                        .foregroundColor(.red)
                    Text("\(appsWithMissingInfo.count)개 앱의 필수 정보를 입력해주세요")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }

                Spacer()
            }

            Divider()

            // 앱 목록
            VStack(alignment: .leading, spacing: 8) {
                ForEach(appsWithMissingInfo.prefix(5)) { app in
                    Button(action: {
                        print("🔘 [MissingInfoAlert] 버튼 클릭: \(app.name)")
                        selectedApp = app
                        print("  ✓ selectedApp 설정됨: \(selectedApp?.name ?? "nil")")
                        showingProjectInfo = true
                        print("  ✓ showingProjectInfo = true")
                    }) {
                        HStack(spacing: 12) {
                            Image(systemName: "exclamationmark.circle.fill")
                                .foregroundColor(.red)

                            VStack(alignment: .leading, spacing: 2) {
                                Text(app.name)
                                    .font(.body)
                                    .fontWeight(.medium)
                                    .foregroundColor(.primary)

                                // 첫 번째 필수 피드백 메시지
                                if let firstRequired = app.missingInfoFeedbacks.filter({ $0.severity == .required }).first {
                                    Text(firstRequired.message)
                                        .font(.caption)
                                        .foregroundColor(.red)
                                }
                            }

                            Spacer()

                            Image(systemName: "arrow.right.circle.fill")
                                .foregroundColor(.red)
                        }
                        .padding(12)
                        .background(Color.red.opacity(0.1))
                        .cornerRadius(8)
                    }
                    .buttonStyle(.plain)
                }

                if appsWithMissingInfo.count > 5 {
                    Text("외 \(appsWithMissingInfo.count - 5)개 더 있음")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.leading, 12)
                }
            }
        }
        .padding()
        .background(Color.red.opacity(0.05))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.red.opacity(0.3), lineWidth: 2)
        )
    }
}

// MARK: - Version Changes Alert Card
struct VersionChangesAlertCard: View {
    @EnvironmentObject var portfolio: PortfolioService
    @State private var isUpdating = false

    var body: some View {
        ZStack {
            if !portfolio.versionChanges.isEmpty {
                alertCard
            }
        }
    }

    private var alertCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            // 헤더
            HStack(spacing: 12) {
                Image(systemName: "arrow.up.circle.fill")
                    .font(.title2)
                    .foregroundColor(.blue)

                VStack(alignment: .leading, spacing: 4) {
                    Text("🔄 버전 변경 감지")
                        .font(.headline)
                        .foregroundColor(.blue)
                    Text("\(portfolio.versionChanges.count)개 앱의 버전이 프로젝트에서 변경되었습니다")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Button(action: updateAllVersions) {
                    HStack(spacing: 6) {
                        if isUpdating {
                            ProgressView()
                                .scaleEffect(0.7)
                        } else {
                            Image(systemName: "arrow.clockwise")
                        }
                        Text("모두 업데이트")
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                .buttonStyle(.plain)
                .disabled(isUpdating)
            }

            Divider()

            // 변경된 앱 목록
            VStack(alignment: .leading, spacing: 8) {
                ForEach(portfolio.versionChanges) { change in
                    HStack(spacing: 12) {
                        Image(systemName: "app.fill")
                            .foregroundColor(.blue)

                        VStack(alignment: .leading, spacing: 2) {
                            Text(change.appName)
                                .font(.body)
                                .fontWeight(.medium)

                            HStack(spacing: 4) {
                                Text(change.currentVersion)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                    .strikethrough()

                                Image(systemName: "arrow.right")
                                    .font(.caption2)
                                    .foregroundColor(.secondary)

                                Text(change.detectedVersion)
                                    .font(.caption)
                                    .foregroundColor(.blue)
                                    .fontWeight(.semibold)
                            }
                        }

                        Spacer()

                        Button(action: {
                            portfolio.updateVersionFromProject(appName: change.appName)
                        }) {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                        }
                        .buttonStyle(.plain)
                    }
                    .padding(12)
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(8)
                }
            }
        }
        .padding()
        .background(Color.blue.opacity(0.05))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.blue.opacity(0.3), lineWidth: 2)
        )
    }

    private func updateAllVersions() {
        isUpdating = true
        portfolio.updateAllVersionsFromProjects()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            isUpdating = false
        }
    }
}

// MARK: - Total Apps Card
struct TotalAppsCard: View {
    @EnvironmentObject var portfolio: PortfolioService

    var body: some View {
        HStack(spacing: 15) {
            KPICard(
                title: "전체 앱",
                value: "\(portfolio.apps.count)",
                subtitle: "활성 \(portfolio.activeApps.count)개",
                color: .blue,
                icon: "app.fill"
            )
        }
    }
}

struct KPICard: View {
    let title: String
    let value: String
    let subtitle: String
    let color: Color
    let icon: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(color)
                Text(title)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Text(value)
                .font(.system(size: 32, weight: .bold))
                .foregroundColor(color)

            Text(subtitle)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}

// MARK: - High Priority Apps
struct HighPriorityAppsCard: View {
    @EnvironmentObject var portfolio: PortfolioService

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("🔥 우선순위 높은 앱")
                .font(.headline)

            ForEach(portfolio.highPriorityApps.prefix(5)) { app in
                AppProgressRow(app: app)
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}

struct AppProgressRow: View {
    let app: AppModel

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Circle()
                    .fill(app.statusColor)
                    .frame(width: 8, height: 8)

                Text(app.name)
                    .font(.subheadline)
                    .fontWeight(.medium)

                Spacer()

                Text("\(Int(app.completionRate))%")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            ProgressView(value: app.completionRate, total: 100)
                .tint(app.progressColor)

            if let nextTask = app.nextTasks.first {
                Text("다음: \(nextTask)")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
            }
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Progress Chart
struct ProgressChartCard: View {
    @EnvironmentObject var portfolio: PortfolioService

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("📊 상태별 분포")
                .font(.headline)

            if let overview = portfolio.portfolio?.overview {
                if #available(macOS 14.0, *) {
                    Chart {
                        SectorMark(
                            angle: .value("완료", overview.totalDone),
                            innerRadius: .ratio(0.6),
                            angularInset: 2
                        )
                        .foregroundStyle(.green)

                        SectorMark(
                            angle: .value("진행 중", overview.totalInProgress),
                            innerRadius: .ratio(0.6),
                            angularInset: 2
                        )
                        .foregroundStyle(.orange)

                        SectorMark(
                            angle: .value("대기", overview.totalNotStarted),
                            innerRadius: .ratio(0.6),
                            angularInset: 2
                        )
                        .foregroundStyle(.gray)
                    }
                    .frame(height: 200)
                } else {
                    Text("차트는 macOS 14.0 이상에서 지원됩니다")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                HStack(spacing: 20) {
                    LegendItem(color: .green, label: "완료", value: overview.totalDone)
                    LegendItem(color: .orange, label: "진행 중", value: overview.totalInProgress)
                    LegendItem(color: .gray, label: "대기", value: overview.totalNotStarted)
                }
                .font(.caption)
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}

struct LegendItem: View {
    let color: Color
    let label: String
    let value: Int

    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(color)
                .frame(width: 8, height: 8)
            Text(label)
            Text("(\(value))")
                .foregroundColor(.secondary)
        }
    }
}

// MARK: - Recent Activity
struct RecentActivityCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("📋 최근 활동")
                .font(.headline)

            Text("여기에 최근 완료된 태스크들이 표시됩니다")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}

// MARK: - Risk Alerts
struct RiskAlertsCard: View {
    let apps: [AppModel]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "exclamationmark.triangle.fill")
                    .foregroundColor(.red)
                Text("⚠️ 주의 필요")
                    .font(.headline)
            }

            ForEach(apps) { app in
                HStack {
                    VStack(alignment: .leading) {
                        Text(app.name)
                            .fontWeight(.medium)
                        Text("진행률: \(Int(app.completionRate))% - 정체 중")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    Spacer()

                    Button("조치하기") {
                        // 터미널에서 해당 앱 상태 확인
                        PortfolioService.shared.openInTerminal(script: "claude-app-status.sh '\(app.name)'")
                    }
                    .buttonStyle(.bordered)
                }
                .padding(.vertical, 4)
            }
        }
        .padding()
        .background(Color.red.opacity(0.1))
        .cornerRadius(12)
    }
}

// MARK: - AI Feedback Analysis Card

// Commented out: not used currently
/*
struct AIFeedbackAnalysisCard: View {
    let onAnalyze: () -> Void
    let results: [String: [PlanningFeature]]

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                HStack(spacing: 8) {
                    Image(systemName: "sparkles")
                        .font(.title2)
                        .foregroundColor(.yellow)
                    VStack(alignment: .leading, spacing: 4) {
                        Text("AI 피드백 분석")
                            .font(.headline)
                        Text("모든 프로젝트의 피드백을 분석하여 기능 제안을 생성합니다")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                Spacer()

                Button(action: onAnalyze) {
                    HStack(spacing: 6) {
                        Image(systemName: "wand.and.stars")
                        Text("전체 분석 실행")
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(Color.yellow.opacity(0.2))
                    .foregroundColor(.yellow)
                    .cornerRadius(8)
                }
                .buttonStyle(.plain)
            }

            if !results.isEmpty {
                Divider()

                VStack(alignment: .leading, spacing: 12) {
                    Text("분석 결과")
                        .font(.subheadline)
                        .foregroundColor(.secondary)

                    ForEach(Array(results.keys.sorted()), id: \.self) { appName in
                        if let suggestions = results[appName], !suggestions.isEmpty {
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(appName)
                                        .font(.body)
                                        .fontWeight(.medium)
                                    Text("\(suggestions.count)개의 기능 제안 생성됨")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }

                                Spacer()

                                HStack(spacing: 8) {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundColor(.green)
                                    Text("\(suggestions.count)")
                                        .font(.caption)
                                        .fontWeight(.bold)
                                        .foregroundColor(.green)
                                }
                            }
                            .padding(.vertical, 8)
                            .padding(.horizontal, 12)
                            .background(Color.green.opacity(0.05))
                            .cornerRadius(8)
                        }
                    }
                }
            } else {
                HStack {
                    Image(systemName: "info.circle")
                        .foregroundColor(.blue)
                    Text("분석 버튼을 눌러 모든 프로젝트의 피드백을 분석하세요")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding()
                .background(Color.blue.opacity(0.05))
                .cornerRadius(8)
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}
*/

// MARK: - Planning Document Card

struct PlanningDocumentCard: View {
    @EnvironmentObject var portfolio: PortfolioService
    let onGenerateComprehensive: () -> Void
    let onGenerateIndividual: (AppModel) -> Void

    @State private var showingProjectPicker = false
    @State private var selectedApp: AppModel?

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                HStack(spacing: 8) {
                    Image(systemName: "doc.text.fill")
                        .font(.title2)
                        .foregroundColor(.purple)
                    VStack(alignment: .leading, spacing: 4) {
                        Text("기획서 생성")
                            .font(.headline)
                        Text("피드백을 바탕으로 마크다운 기획서를 자동 생성합니다")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                Spacer()

                HStack(spacing: 12) {
                    Button(action: { showingProjectPicker.toggle() }) {
                        HStack(spacing: 6) {
                            Image(systemName: "doc.badge.plus")
                            Text("개별 프로젝트")
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(Color.purple.opacity(0.1))
                        .foregroundColor(.purple)
                        .cornerRadius(8)
                    }
                    .buttonStyle(.plain)
                    .popover(isPresented: $showingProjectPicker) {
                        ProjectPickerPopover(
                            apps: portfolio.apps,
                            onSelect: { app in
                                selectedApp = app
                                onGenerateIndividual(app)
                                showingProjectPicker = false
                            }
                        )
                    }

                    Button(action: onGenerateComprehensive) {
                        HStack(spacing: 6) {
                            Image(systemName: "doc.on.doc.fill")
                            Text("종합 기획서")
                        }
                        .padding(.horizontal, 16)
                        .padding(.vertical, 10)
                        .background(Color.purple.opacity(0.2))
                        .foregroundColor(.purple)
                        .cornerRadius(8)
                    }
                    .buttonStyle(.plain)
                }
            }

            Divider()

            HStack(spacing: 20) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("포함 내용")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    VStack(alignment: .leading, spacing: 2) {
                        FeatureBadge(icon: "bubble.left.fill", text: "피드백 분석")
                        FeatureBadge(icon: "lightbulb.fill", text: "기능 제안")
                        FeatureBadge(icon: "checklist", text: "태스크 현황")
                        FeatureBadge(icon: "flag.fill", text: "우선순위")
                    }
                }

                Spacer()

                VStack(alignment: .leading, spacing: 4) {
                    Text("출력 형식")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    HStack(spacing: 8) {
                        Image(systemName: "doc.plaintext")
                            .foregroundColor(.purple)
                        Text("Markdown (.md)")
                            .font(.caption)
                            .fontWeight(.medium)
                    }
                }
            }
            .padding()
            .background(Color.purple.opacity(0.05))
            .cornerRadius(8)
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}

struct FeatureBadge: View {
    let icon: String
    let text: String

    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: icon)
                .font(.caption2)
                .foregroundColor(.purple)
            Text(text)
                .font(.caption2)
        }
    }
}

struct ProjectPickerPopover: View {
    let apps: [AppModel]
    let onSelect: (AppModel) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("프로젝트 선택")
                .font(.headline)
                .padding(.horizontal)
                .padding(.top)

            Divider()

            ScrollView {
                VStack(spacing: 0) {
                    ForEach(apps) { app in
                        Button(action: {
                            onSelect(app)
                        }) {
                            HStack {
                                Circle()
                                    .fill(app.statusColor)
                                    .frame(width: 8, height: 8)

                                Text(app.name)
                                    .font(.body)
                                    .foregroundColor(.primary)

                                Spacer()

                                Text("v\(app.currentVersion)")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            .padding(.horizontal)
                            .padding(.vertical, 8)
                            .contentShape(Rectangle())
                        }
                        .buttonStyle(.plain)
                        .background(
                            Color.purple.opacity(0.05)
                                .opacity(0)
                        )
                        .onHover { hovering in
                            // Hover effect handled by system
                        }

                        if app.id != apps.last?.id {
                            Divider()
                        }
                    }
                }
            }
            .frame(maxHeight: 300)
        }
        .frame(width: 280)
    }
}

// MARK: - Workflow Status Card

struct WorkflowStatusCard: View {
    @EnvironmentObject var portfolio: PortfolioService

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // 헤더
            HStack {
                Image(systemName: "arrow.triangle.2.circlepath")
                    .font(.title2)
                    .foregroundColor(.blue)
                Text("앱별 워크플로우 상태")
                    .font(.headline)

                Spacer()

                Button(action: {
                    portfolio.loadWorkflowStatus()
                }) {
                    Image(systemName: "arrow.clockwise")
                }
                .buttonStyle(.plain)
            }

            Divider()

            // 3단계 요약
            HStack(spacing: 20) {
                StageCard(
                    stage: "피드백 필요",
                    appFolders: portfolio.appsNeedingFeedback(),
                    color: .orange,
                    icon: "exclamationmark.bubble.fill",
                    allApps: portfolio.apps
                )

                StageCard(
                    stage: "피드백 분석중",
                    appFolders: portfolio.appsWithActiveFeedback(),
                    color: .blue,
                    icon: "bubble.left.and.bubble.right.fill",
                    allApps: portfolio.apps
                )

                StageCard(
                    stage: "의사결정 대기",
                    appFolders: portfolio.appsNeedingDecision(),
                    color: .purple,
                    icon: "checkmark.circle.fill",
                    allApps: portfolio.apps
                )
            }

            Divider()

            // 앱별 상세 상태
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(portfolio.apps) { app in
                        AppWorkflowItem(
                            app: app,
                            status: portfolio.appWorkflowStatus[getFolderName(for: app)]
                        )
                    }
                }
                .padding(.horizontal, 4)
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }

    private func getFolderName(for app: AppModel) -> String {
        // app.name에서 폴더명 추론 또는 매핑 사용
        let mapping: [String: String] = [
            "클립키보드": "clip-keyboard",
            "나만의 버킷": "my-bucket",
            "버킷 클라임": "bucket-climb",
            "데일리 트래커": "daily-tracker",
            "포트폴리오 CEO": "portfolioceo",
            "바미로그": "bami-log",
            "쿨타임": "cooltime",
            "오늘의 주접": "daily-compliment",
            "돈꼬마트": "donkko-mart",
            "두 번 알림": "double-reminder",
            "잘 싸워보세": "fight-well",
            "외국어는 언어다": "foreign-is-language",
            "인생 맛집": "life-restaurant",
            "세끼": "three-meals",
            "픽셀 미미": "pixel-mimi",
            "포항 어드벤쳐": "pohang-adventure",
            "확률계산기": "probability-calculator",
            "퀴즈": "quiz",
            "욕망의 무지개": "rainbow-of-desire",
            "라포 맵": "rapport-map",
            "리바운드 저널": "rebound-journal",
            "릴렉스 온": "relax-on",
            "내마음에저장": "save-in-my-heart",
            "일정비서": "schedule-assistant",
            "공유일 설계자": "shared-day-designer",
            "휴가 플래너": "shared-day-designer",
            "속삭": "whisper"
        ]
        return mapping[app.name] ?? app.name.lowercased()
    }
}

struct StageCard: View {
    let stage: String
    let appFolders: [String]
    let color: Color
    let icon: String
    let allApps: [AppModel]

    @EnvironmentObject var portfolio: PortfolioService
    @State private var showingFullList = false
    @State private var selectedApp: AppModel?
    @State private var showingProjectInfo = false

    // folder name -> app name 매핑
    private let folderToNameMapping: [String: String] = [
        "clip-keyboard": "클립키보드",
        "my-bucket": "나만의 버킷",
        "bucket-climb": "버킷 클라임",
        "daily-tracker": "데일리 트래커",
        "portfolioceo": "포트폴리오 CEO",
        "bami-log": "바미로그",
        "cooltime": "쿨타임",
        "daily-compliment": "오늘의 주접",
        "donkko-mart": "돈꼬마트",
        "double-reminder": "두 번 알림",
        "fight-well": "잘 싸워보세",
        "foreign-is-language": "외국어는 언어다",
        "life-restaurant": "인생 맛집",
        "three-meals": "세끼",
        "pixel-mimi": "픽셀 미미",
        "pohang-adventure": "포항 어드벤쳐",
        "probability-calculator": "확률계산기",
        "quiz": "퀴즈",
        "rainbow-of-desire": "욕망의 무지개",
        "rapport-map": "라포 맵",
        "rebound-journal": "리바운드 저널",
        "relax-on": "릴렉스 온",
        "save-in-my-heart": "내마음에저장",
        "schedule-assistant": "일정비서",
        "shared-day-designer": "공유일 설계자",
        "whisper": "속삭"
    ]

    private var appsInThisStage: [AppModel] {
        let nameToFolderMapping = Dictionary(uniqueKeysWithValues:
            folderToNameMapping.map { ($0.value, $0.key) })

        return allApps.filter { app in
            if let folder = nameToFolderMapping[app.name] {
                return appFolders.contains(folder)
            }
            return false
        }
    }

    var body: some View {
        Button(action: {
            if !appsInThisStage.isEmpty {
                showingFullList = true
            }
        }) {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Image(systemName: icon)
                        .foregroundColor(color)
                    Text(stage)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Text("\(appFolders.count)")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(color)

                // 앱 이름 리스트
                if appsInThisStage.isEmpty {
                    Text("없음")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                        .italic()
                } else {
                    VStack(alignment: .leading, spacing: 2) {
                        ForEach(appsInThisStage.prefix(3)) { app in
                            HStack(spacing: 4) {
                                Text("• \(app.name)")
                                    .font(.caption2)
                                    .foregroundColor(.primary)
                                    .lineLimit(1)

                                // 필수 정보 누락 표시
                                if !app.hasRequiredInfo {
                                    Image(systemName: "exclamationmark.circle.fill")
                                        .font(.caption2)
                                        .foregroundColor(.red)
                                }
                            }
                        }

                        if appsInThisStage.count > 3 {
                            Text("외 \(appsInThisStage.count - 3)개")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                                .italic()
                        }
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding()
            .background(color.opacity(0.1))
            .cornerRadius(8)
        }
        .buttonStyle(.plain)
        .sheet(isPresented: $showingFullList) {
            AppListSheet(
                title: stage,
                apps: appsInThisStage,
                color: color,
                onSelectApp: { app in
                    selectedApp = app
                    showingFullList = false
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                        showingProjectInfo = true
                    }
                }
            )
        }
        .sheet(isPresented: $showingProjectInfo) {
            if let app = selectedApp {
                ProjectInfoSheet(app: app)
            }
        }
    }
}

// MARK: - App List Sheet
struct AppListSheet: View {
    let title: String
    let apps: [AppModel]
    let color: Color
    let onSelectApp: (AppModel) -> Void

    @Environment(\.dismiss) var dismiss

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                Text(title)
                    .font(.headline)
                Spacer()
                Button("닫기") {
                    dismiss()
                }
            }
            .padding()
            .background(Color(NSColor.controlBackgroundColor))

            Divider()

            // 앱 목록
            ScrollView {
                VStack(spacing: 12) {
                    ForEach(apps) { app in
                        Button(action: {
                            onSelectApp(app)
                        }) {
                            HStack(spacing: 12) {
                                Circle()
                                    .fill(color)
                                    .frame(width: 10, height: 10)

                                VStack(alignment: .leading, spacing: 4) {
                                    HStack {
                                        Text(app.name)
                                            .font(.body)
                                            .fontWeight(.medium)
                                            .foregroundColor(.primary)

                                        if !app.hasRequiredInfo {
                                            Image(systemName: "exclamationmark.circle.fill")
                                                .foregroundColor(.red)
                                        }
                                    }

                                    // 누락된 필수 정보 표시
                                    let requiredFeedbacks = app.missingInfoFeedbacks.filter { $0.severity == .required }
                                    if !requiredFeedbacks.isEmpty {
                                        Text(requiredFeedbacks.first!.message)
                                            .font(.caption)
                                            .foregroundColor(.red)
                                    }
                                }

                                Spacer()

                                Image(systemName: "chevron.right")
                                    .foregroundColor(.secondary)
                            }
                            .padding()
                            .background(Color(NSColor.controlBackgroundColor))
                            .cornerRadius(8)
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding()
            }
        }
        .frame(width: 500, height: 600)
    }
}

// MARK: - Project Info Sheet
struct ProjectInfoSheet: View {
    let app: AppModel

    @Environment(\.dismiss) var dismiss
    @State private var localProjectPath: String = ""
    @State private var githubRepo: String = ""
    @State private var appStoreUrl: String = ""
    @State private var minimumOS: String = ""
    @State private var isSaving = false

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                Text("\(app.name) 프로젝트 정보")
                    .font(.headline)
                Spacer()
                Button("닫기") {
                    print("❌ [ProjectInfoSheet] 닫기 버튼 클릭")
                    dismiss()
                }
            }
            .padding()
            .background(Color(NSColor.controlBackgroundColor))

            Divider()

            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // 필수 정보 피드백
                    if !app.missingInfoFeedbacks.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("필요한 정보")
                                .font(.headline)

                            ForEach(app.missingInfoFeedbacks) { feedback in
                                HStack(alignment: .top, spacing: 8) {
                                    Image(systemName: feedback.severity == .required ? "exclamationmark.circle.fill" : "info.circle.fill")
                                        .foregroundColor(feedback.severity == .required ? .red : .orange)

                                    VStack(alignment: .leading, spacing: 4) {
                                        Text(feedback.message)
                                            .font(.body)
                                            .foregroundColor(feedback.severity == .required ? .red : .orange)
                                    }
                                }
                                .padding()
                                .background((feedback.severity == .required ? Color.red : Color.orange).opacity(0.1))
                                .cornerRadius(8)
                            }
                        }
                    }

                    // 입력 폼
                    VStack(alignment: .leading, spacing: 16) {
                        Text("프로젝트 정보 입력")
                            .font(.headline)

                        // 로컬 프로젝트 경로
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text("소스 코드 경로")
                                    .font(.subheadline)
                                    .fontWeight(.medium)
                                Text("*")
                                    .foregroundColor(.red)
                            }
                            TextField("예: ~/Projects/MyApp", text: $localProjectPath)
                                .textFieldStyle(.roundedBorder)
                            Text("Xcode 프로젝트가 있는 폴더 경로를 입력하세요")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }

                        // GitHub 저장소
                        VStack(alignment: .leading, spacing: 8) {
                            Text("GitHub 저장소")
                                .font(.subheadline)
                                .fontWeight(.medium)
                            TextField("예: https://github.com/username/repo", text: $githubRepo)
                                .textFieldStyle(.roundedBorder)
                        }

                        // App Store URL
                        VStack(alignment: .leading, spacing: 8) {
                            Text("App Store URL")
                                .font(.subheadline)
                                .fontWeight(.medium)
                            TextField("예: https://apps.apple.com/app/id123456789", text: $appStoreUrl)
                                .textFieldStyle(.roundedBorder)
                        }

                        // 최소 OS 버전
                        VStack(alignment: .leading, spacing: 8) {
                            Text("최소 지원 OS 버전")
                                .font(.subheadline)
                                .fontWeight(.medium)
                            TextField("예: iOS 15.0", text: $minimumOS)
                                .textFieldStyle(.roundedBorder)
                        }

                        // 저장 버튼
                        HStack {
                            Spacer()
                            Button(isSaving ? "저장 중..." : "저장") {
                                saveProjectInfo()
                            }
                            .buttonStyle(.borderedProminent)
                            .disabled(localProjectPath.isEmpty || isSaving)
                        }
                    }
                }
                .padding()
            }
        }
        .frame(width: 600, height: 700)
        .onAppear {
            print("📄 [ProjectInfoSheet] onAppear 실행: \(app.name)")
            loadCurrentInfo()
        }
    }

    private func loadCurrentInfo() {
        print("📥 [ProjectInfoSheet] 현재 정보 로드:")
        localProjectPath = app.localProjectPath ?? ""
        githubRepo = app.githubRepo ?? ""
        appStoreUrl = app.appStoreUrl ?? ""
        minimumOS = app.minimumOS ?? ""
        print("  - localProjectPath: '\(localProjectPath)'")
        print("  - githubRepo: '\(githubRepo)'")
        print("  - appStoreUrl: '\(appStoreUrl)'")
        print("  - minimumOS: '\(minimumOS)'")
    }

    private func saveProjectInfo() {
        isSaving = true

        print("💾 저장 시작: \(app.name)")
        print("  - localProjectPath: \(localProjectPath)")
        print("  - githubRepo: \(githubRepo)")
        print("  - appStoreUrl: \(appStoreUrl)")
        print("  - minimumOS: \(minimumOS)")

        PortfolioService.shared.updateProjectInfo(
            appName: app.name,
            localProjectPath: localProjectPath.isEmpty ? nil : localProjectPath,
            githubRepo: githubRepo.isEmpty ? nil : githubRepo,
            appStoreUrl: appStoreUrl.isEmpty ? nil : appStoreUrl,
            minimumOS: minimumOS.isEmpty ? nil : minimumOS
        )

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            isSaving = false
            dismiss()
        }
    }
}

struct AppWorkflowItem: View {
    let app: AppModel
    let status: AppWorkflowStatus?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // 앱 이름
            Text(app.name)
                .font(.caption)
                .fontWeight(.medium)
                .lineLimit(1)

            // 상태 표시
            if let status = status {
                HStack(spacing: 4) {
                    Circle()
                        .fill(stageColor(for: status.currentStage))
                        .frame(width: 6, height: 6)

                    Text(status.statusDescription)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }

                // 카운터 표시
                HStack(spacing: 8) {
                    if status.feedbackCount > 0 {
                        Label("\(status.feedbackCount)", systemImage: "bubble.left.fill")
                            .font(.caption2)
                            .foregroundColor(.blue)
                    }

                    if status.pendingDecisionCount > 0 {
                        Label("\(status.pendingDecisionCount)", systemImage: "checkmark.circle.fill")
                            .font(.caption2)
                            .foregroundColor(.purple)
                    }

                    if status.feedbackCount == 0 && status.pendingDecisionCount == 0 {
                        Label("0", systemImage: "exclamationmark.triangle.fill")
                            .font(.caption2)
                            .foregroundColor(.orange)
                    }
                }
            } else {
                Text("상태 없음")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 12)
        .background(Color(NSColor.controlBackgroundColor).opacity(0.5))
        .cornerRadius(8)
        .frame(width: 140)
    }

    private func stageColor(for stage: WorkflowStage) -> Color {
        switch stage {
        case .ready: return .orange
        case .feedback: return .blue
        case .decision: return .purple
        }
    }
}

// MARK: - iCloud Sync Card

struct iCloudSyncCard: View {
    @EnvironmentObject var portfolio: PortfolioService
    @StateObject private var cloudKitService = CloudKitSyncService.shared
    @State private var isSyncing = false
    @State private var syncStatus: SyncStatusType = .idle

    enum SyncStatusType {
        case idle
        case syncing
        case success
        case error(String)

        var color: Color {
            switch self {
            case .idle: return .secondary
            case .syncing: return .blue
            case .success: return .green
            case .error: return .red
            }
        }

        var icon: String {
            switch self {
            case .idle: return "icloud"
            case .syncing: return "icloud.and.arrow.up"
            case .success: return "checkmark.icloud.fill"
            case .error: return "exclamationmark.icloud.fill"
            }
        }

        var description: String {
            switch self {
            case .idle: return "대기 중"
            case .syncing: return "동기화 중..."
            case .success: return "동기화 완료"
            case .error(let msg): return "오류: \(msg)"
            }
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 헤더
            HStack {
                Image(systemName: syncStatus.icon)
                    .font(.title2)
                    .foregroundColor(syncStatus.color)

                VStack(alignment: .leading, spacing: 2) {
                    Text("iOS 앱 동기화")
                        .font(.headline)

                    Text(syncStatus.description)
                        .font(.caption)
                        .foregroundColor(syncStatus.color)
                }

                Spacer()

                // 동기화 버튼
                Button(action: syncNow) {
                    HStack(spacing: 6) {
                        if isSyncing {
                            ProgressView()
                                .scaleEffect(0.7)
                        } else {
                            Image(systemName: "arrow.triangle.2.circlepath")
                        }
                        Text(isSyncing ? "동기화 중" : "지금 동기화")
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                .buttonStyle(.plain)
                .disabled(isSyncing)
            }

            Divider()

            // 동기화 정보
            HStack(spacing: 20) {
                // 앱 개수
                VStack(alignment: .leading, spacing: 4) {
                    Text("동기화 대상")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    HStack(spacing: 4) {
                        Image(systemName: "app.fill")
                            .foregroundColor(.blue)
                        Text("\(portfolio.apps.count)개 앱")
                            .font(.body)
                            .fontWeight(.medium)
                    }
                }

                Spacer()

                // 마지막 동기화 시간
                VStack(alignment: .trailing, spacing: 4) {
                    Text("마지막 동기화")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    if let lastSync = cloudKitService.lastSyncDate {
                        Text(lastSync, style: .relative)
                            .font(.body)
                            .foregroundColor(.secondary)
                    } else {
                        Text("아직 안함")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                }
            }

            // CloudKit 상태
            HStack(spacing: 8) {
                Image(systemName: cloudKitService.isCloudKitAvailable ? "checkmark.circle.fill" : "xmark.circle.fill")
                    .foregroundColor(cloudKitService.isCloudKitAvailable ? .green : .red)

                Text(cloudKitService.isCloudKitAvailable ? "CloudKit 연결됨" : "CloudKit 연결 안됨")
                    .font(.caption)
                    .foregroundColor(cloudKitService.isCloudKitAvailable ? .green : .red)

                Spacer()

                Text("CEOfeedback 앱과 동기화됩니다")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding(8)
            .background(Color(NSColor.controlBackgroundColor).opacity(0.5))
            .cornerRadius(6)
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }

    private func syncNow() {
        isSyncing = true
        syncStatus = .syncing

        // CloudKit 동기화 실행
        portfolio.syncToiCloud()

        // 비동기 완료 대기
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            isSyncing = false
            if let error = cloudKitService.syncError {
                syncStatus = .error(error)
            } else {
                syncStatus = .success
            }

            // 3초 후 상태 초기화
            DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                if case .success = syncStatus {
                    syncStatus = .idle
                }
            }
        }
    }
}
