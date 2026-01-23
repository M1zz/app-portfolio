import SwiftUI

// MARK: - App Workflow Filter

enum AppWorkflowFilter: String, CaseIterable {
    case all = "전체"
    case notDeployed = "미배포"
    case needsFeedback = "피드백 필요"
    case pendingProposal = "기획 제안 대기"
    case deciding = "의사결정"
    case testing = "테스트 중"
    case deployed = "배포완료"

    var color: Color {
        switch self {
        case .all: return .gray
        case .notDeployed: return .red
        case .needsFeedback: return .orange      // 피드백 필요: 주황
        case .pendingProposal: return .blue      // 기획 제안 대기: 파랑
        case .deciding: return .purple           // 의사결정: 보라
        case .testing: return .yellow            // 테스트: 노랑
        case .deployed: return .green            // 배포: 초록
        }
    }

    var icon: String {
        switch self {
        case .all: return "square.grid.2x2"
        case .notDeployed: return "icloud.slash"
        case .needsFeedback: return "exclamationmark.bubble"
        case .pendingProposal: return "lightbulb"
        case .deciding: return "checkmark.circle"
        case .testing: return "testtube.2"
        case .deployed: return "checkmark.seal.fill"
        }
    }
}

struct AppsGridView: View {
    @EnvironmentObject var portfolio: PortfolioService
    @State private var selectedFilter: AppWorkflowFilter = .all
    @State private var selectedCategory: String? = nil
    @State private var showingAddAppSheet = false
    @State private var appNameToDelete: String?
    @State private var showingDeleteConfirmation = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    // 필터/그룹 요약
                    WorkflowFilterBar(selectedFilter: $selectedFilter)

                    // 카테고리 필터
                    if !portfolio.availableCategories.isEmpty {
                        CategoryFilterBar(
                            selectedCategory: $selectedCategory,
                            categories: portfolio.availableCategories
                        )
                    }

                    LazyVGrid(columns: [GridItem(.adaptive(minimum: 300))], spacing: 20) {
                        ForEach(filteredApps) { app in
                            NavigationLink(destination: AppDetailView(app: app)
                                .environmentObject(portfolio)
                                .environmentObject(AppDetailService.shared)) {
                                EnhancedAppCard(app: app)
                                    .environmentObject(portfolio)
                            }
                            .buttonStyle(.plain)
                            .contextMenu {
                                Button(role: .destructive) {
                                    appNameToDelete = app.name
                                    showingDeleteConfirmation = true
                                } label: {
                                    Label("앱 삭제", systemImage: "trash")
                                }
                            }
                        }
                    }
                }
                .padding()
            }
            .navigationTitle(selectedFilter.rawValue)
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button(action: {
                        showingAddAppSheet = true
                    }) {
                        Label("새 앱 추가", systemImage: "plus")
                    }
                }
            }
        }
        .sheet(isPresented: $showingAddAppSheet) {
            AddAppSheet()
                .environmentObject(portfolio)
        }
        .alert("앱 삭제", isPresented: $showingDeleteConfirmation) {
            Button("취소", role: .cancel) {
                appNameToDelete = nil
            }
            Button("삭제", role: .destructive) {
                if let appName = appNameToDelete {
                    _ = portfolio.deleteApp(appName: appName)
                    appNameToDelete = nil
                }
            }
        } message: {
            if let appName = appNameToDelete {
                Text("'\(appName)' 앱을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.")
            }
        }
        .onAppear {
            portfolio.loadWorkflowStatus()
        }
    }

    private var filteredApps: [AppModel] {
        let apps: [AppModel]

        switch selectedFilter {
        case .all:
            apps = portfolio.apps

        case .notDeployed:
            apps = portfolio.apps.filter { app in
                // App Store URL이 없거나 비어있는 앱 (미배포)
                app.appStoreUrl == nil || app.appStoreUrl?.isEmpty == true
            }

        case .needsFeedback:
            apps = portfolio.apps.filter { app in
                let folder = portfolio.getFolderName(for: app.name)
                guard let status = portfolio.appWorkflowStatus[folder] else { return false }
                return status.currentStage == .ready
            }

        case .pendingProposal:
            // 피드백이 있고 의사결정이 없는 앱 (기획 제안 대기)
            apps = portfolio.apps.filter { app in
                let folder = portfolio.getFolderName(for: app.name)
                guard let status = portfolio.appWorkflowStatus[folder] else { return false }
                return status.feedbackCount > 0 && status.pendingDecisionCount == 0
            }

        case .deciding:
            apps = portfolio.apps.filter { app in
                let folder = portfolio.getFolderName(for: app.name)
                guard let status = portfolio.appWorkflowStatus[folder] else { return false }
                return status.currentStage == .decision
            }

        case .testing:
            apps = portfolio.apps.filter { app in
                let folder = portfolio.getFolderName(for: app.name)
                let status = portfolio.appWorkflowStatus[folder]
                // 워크플로우가 완료되고 (피드백도 없고 의사결정도 없고) status가 active인 앱
                return status?.feedbackCount == 0 &&
                       status?.pendingDecisionCount == 0 &&
                       app.status == .active
            }

        case .deployed:
            apps = portfolio.apps.filter { app in
                // 배포 완료 또는 유지보수 상태인 앱
                app.status == .archived || app.status == .maintenance
            }
        }

        // 카테고리 필터 적용
        if let category = selectedCategory {
            apps = apps.filter { app in
                app.categories?.contains(category) ?? false
            }
        }

        // Sort by: 1) feedback count (descending), 2) name
        return apps.sorted { app1, app2 in
            let folder1 = portfolio.getFolderName(for: app1.name)
            let folder2 = portfolio.getFolderName(for: app2.name)

            let feedbackCount1 = portfolio.appWorkflowStatus[folder1]?.feedbackCount ?? 0
            let feedbackCount2 = portfolio.appWorkflowStatus[folder2]?.feedbackCount ?? 0

            if feedbackCount1 != feedbackCount2 {
                return feedbackCount1 > feedbackCount2  // More feedback first
            }

            return app1.name < app2.name  // Alphabetical order
        }
    }

    private func calculateProjectCompletion(for app: AppModel) -> Int {
        var totalFields: Double = 7
        var filledFields: Double = 3  // name, bundleId, currentVersion

        if app.minimumOS != nil && !app.minimumOS!.isEmpty { filledFields += 1 }
        if app.localProjectPath != nil && !app.localProjectPath!.isEmpty { filledFields += 1 }
        if app.githubRepo != nil && !app.githubRepo!.isEmpty { filledFields += 1 }
        if app.appStoreUrl != nil && !app.appStoreUrl!.isEmpty { filledFields += 1 }

        return Int((filledFields / totalFields) * 100)
    }

    private func compareVersions(_ v1: String, _ v2: String) -> Int {
        let parts1 = v1.split(separator: ".").compactMap { Int($0) }
        let parts2 = v2.split(separator: ".").compactMap { Int($0) }

        for i in 0..<max(parts1.count, parts2.count) {
            let part1 = i < parts1.count ? parts1[i] : 0
            let part2 = i < parts2.count ? parts2[i] : 0

            if part1 != part2 {
                return part1 - part2  // Return difference
            }
        }
        return 0  // Versions are equal
    }
}

// MARK: - Add App Sheet

struct AddAppSheet: View {
    @EnvironmentObject var portfolio: PortfolioService
    @Environment(\.dismiss) var dismiss

    @State private var name = ""
    @State private var nameEn = ""
    @State private var bundleId = ""
    @State private var currentVersion = "1.0.0"
    @State private var selectedStatus: AppStatus = .planning
    @State private var selectedPriority: Priority = .medium

    @State private var minimumOS = ""
    @State private var localProjectPath = ""
    @State private var githubRepo = ""
    @State private var appStoreUrl = ""

    @State private var showingError = false
    @State private var errorMessage = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("필수 정보") {
                    LabeledContent("앱 이름 (한글)") {
                        TextField("예: 클립키보드", text: $name)
                            .textFieldStyle(.roundedBorder)
                    }

                    LabeledContent("앱 이름 (영문)") {
                        TextField("예: Clip Keyboard", text: $nameEn)
                            .textFieldStyle(.roundedBorder)
                    }

                    LabeledContent("Bundle ID") {
                        TextField("예: com.company.app", text: $bundleId)
                            .textFieldStyle(.roundedBorder)
                    }

                    LabeledContent("현재 버전") {
                        TextField("1.0.0", text: $currentVersion)
                            .textFieldStyle(.roundedBorder)
                    }

                    Picker("상태", selection: $selectedStatus) {
                        ForEach([AppStatus.active, .planning, .maintenance, .archived], id: \.self) { status in
                            Text(status.displayName).tag(status)
                        }
                    }

                    Picker("우선순위", selection: $selectedPriority) {
                        ForEach([Priority.high, .medium, .low], id: \.self) { priority in
                            Text(priority.displayName).tag(priority)
                        }
                    }
                }

                Section("선택 정보") {
                    LabeledContent("최소 OS 버전") {
                        TextField("예: 16.0", text: $minimumOS)
                            .textFieldStyle(.roundedBorder)
                    }

                    LabeledContent("로컬 프로젝트 경로") {
                        TextField("예: ../toki", text: $localProjectPath)
                            .textFieldStyle(.roundedBorder)
                    }

                    LabeledContent("GitHub 저장소") {
                        TextField("예: https://github.com/...", text: $githubRepo)
                            .textFieldStyle(.roundedBorder)
                    }

                    LabeledContent("App Store URL") {
                        TextField("예: https://apps.apple.com/...", text: $appStoreUrl)
                            .textFieldStyle(.roundedBorder)
                    }
                }
            }
            .formStyle(.grouped)
            .navigationTitle("새 앱 추가")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("취소") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("추가") {
                        createApp()
                    }
                    .disabled(!isValid)
                }
            }
        }
        .frame(width: 600, height: 700)
        .alert("오류", isPresented: $showingError) {
            Button("확인", role: .cancel) {}
        } message: {
            Text(errorMessage)
        }
    }

    private var isValid: Bool {
        !name.isEmpty && !nameEn.isEmpty && !bundleId.isEmpty && !currentVersion.isEmpty
    }

    private func createApp() {
        let success = portfolio.createApp(
            name: name,
            nameEn: nameEn,
            bundleId: bundleId,
            currentVersion: currentVersion,
            status: selectedStatus,
            priority: selectedPriority,
            minimumOS: minimumOS.isEmpty ? nil : minimumOS,
            localProjectPath: localProjectPath.isEmpty ? nil : localProjectPath,
            githubRepo: githubRepo.isEmpty ? nil : githubRepo,
            appStoreUrl: appStoreUrl.isEmpty ? nil : appStoreUrl
        )

        if success {
            dismiss()
        } else {
            errorMessage = "앱을 추가하는데 실패했습니다. 이미 존재하는 이름일 수 있습니다."
            showingError = true
        }
    }
}

// MARK: - Workflow Filter Bar

struct WorkflowFilterBar: View {
    @EnvironmentObject var portfolio: PortfolioService
    @Binding var selectedFilter: AppWorkflowFilter

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(AppWorkflowFilter.allCases, id: \.self) { filter in
                    FilterChip(
                        filter: filter,
                        isSelected: selectedFilter == filter,
                        count: countForFilter(filter),
                        onTap: { selectedFilter = filter }
                    )
                }
            }
            .padding(.horizontal, 4)
        }
    }

    private func countForFilter(_ filter: AppWorkflowFilter) -> Int {
        switch filter {
        case .all:
            return portfolio.apps.count

        case .notDeployed:
            return portfolio.apps.filter { app in
                app.appStoreUrl == nil || app.appStoreUrl?.isEmpty == true
            }.count

        case .needsFeedback:
            return portfolio.apps.filter { app in
                let folder = portfolio.getFolderName(for: app.name)
                guard let status = portfolio.appWorkflowStatus[folder] else { return false }
                return status.currentStage == .ready
            }.count

        case .pendingProposal:
            return portfolio.apps.filter { app in
                let folder = portfolio.getFolderName(for: app.name)
                guard let status = portfolio.appWorkflowStatus[folder] else { return false }
                return status.feedbackCount > 0 && status.pendingDecisionCount == 0
            }.count

        case .deciding:
            return portfolio.apps.filter { app in
                let folder = portfolio.getFolderName(for: app.name)
                guard let status = portfolio.appWorkflowStatus[folder] else { return false }
                return status.currentStage == .decision
            }.count

        case .testing:
            return portfolio.apps.filter { app in
                let folder = portfolio.getFolderName(for: app.name)
                let status = portfolio.appWorkflowStatus[folder]
                return status?.feedbackCount == 0 &&
                       status?.pendingDecisionCount == 0 &&
                       app.status == .active
            }.count

        case .deployed:
            return portfolio.apps.filter { app in
                app.status == .archived || app.status == .maintenance
            }.count
        }
    }
}

struct FilterChip: View {
    let filter: AppWorkflowFilter
    let isSelected: Bool
    let count: Int
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 6) {
                Image(systemName: filter.icon)
                    .font(.caption)
                Text("\(count)")
                    .fontWeight(.semibold)
                Text(filter.rawValue)
                    .font(.caption)
            }
            .foregroundColor(isSelected ? .white : filter.color)
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(isSelected ? filter.color : filter.color.opacity(0.1))
            .cornerRadius(12)
        }
        .buttonStyle(.plain)
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
                    .foregroundColor(.primary)

                Spacer()

                Text("v\(app.currentVersion)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            HStack {
                Text(app.status.displayName)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(app.statusColor.opacity(0.2))
                    .foregroundColor(app.statusColor)
                    .cornerRadius(4)

                Spacer()

                if app.stats.totalTasks > 0 {
                    Text("\(app.stats.done)/\(app.stats.totalTasks) 완료")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
        .shadow(radius: 2)
        .contentShape(Rectangle())
    }
}

// MARK: - Enhanced App Card

struct EnhancedAppCard: View {
    let app: AppModel
    @EnvironmentObject var portfolio: PortfolioService

    private var workflowStatus: AppWorkflowStatus? {
        let folder = portfolio.getFolderName(for: app.name)
        return portfolio.appWorkflowStatus[folder]
    }

    private var workflowStageColor: Color {
        guard let status = workflowStatus else { return .gray }
        switch status.currentStage {
        case .ready: return .orange
        case .feedback: return .blue
        case .decision: return .purple
        }
    }

    private var workflowStageIcon: String {
        guard let status = workflowStatus else { return "circle" }
        switch status.currentStage {
        case .ready: return "exclamationmark.bubble"
        case .feedback: return "bubble.left.and.bubble.right"
        case .decision: return "checkmark.circle"
        }
    }

    /// 최근 2주 이내에 업데이트 되었는지 확인
    private var isRecentlyUpdated: Bool {
        guard let modDate = portfolio.appFileModificationDates[app.bundleId] else {
            return false
        }
        let twoWeeksAgo = Calendar.current.date(byAdding: .day, value: -14, to: Date()) ?? Date()
        return modDate > twoWeeksAgo
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // 상단: 워크플로우 상태 바
            HStack(spacing: 6) {
                Image(systemName: workflowStageIcon)
                    .font(.caption2)
                    .foregroundColor(workflowStageColor)

                Text(workflowStatus?.statusDescription ?? "대기")
                    .font(.caption2)
                    .fontWeight(.medium)
                    .foregroundColor(workflowStageColor)

                Spacer()

                // 필수 정보 누락 경고
                if !app.hasRequiredInfo {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.caption2)
                        .foregroundColor(.red)
                }
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(workflowStageColor.opacity(0.1))

            // 메인 컨텐츠
            VStack(alignment: .leading, spacing: 12) {
                // 앱 이름과 버전
                HStack {
                    Circle()
                        .fill(app.priorityColor)
                        .frame(width: 8, height: 8)

                    Text(app.name)
                        .font(.headline)
                        .foregroundColor(.primary)

                    Spacer()

                    Text("v\(app.currentVersion)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                // 진행 상태 (피드백, 의사결정, 태스크 분리)
                HStack(spacing: 12) {
                    // 피드백 상태 (파랑)
                    if let status = workflowStatus, status.feedbackCount > 0 {
                        HStack(spacing: 4) {
                            Image(systemName: "bubble.left.fill")
                                .font(.caption2)
                            Text("\(status.feedbackCount)")
                                .font(.caption2)
                                .fontWeight(.medium)
                        }
                        .foregroundColor(.blue)
                    }

                    // 의사결정 상태 (노랑)
                    if let status = workflowStatus, status.pendingDecisionCount > 0 {
                        HStack(spacing: 4) {
                            Image(systemName: "lightbulb.fill")
                                .font(.caption2)
                            Text("\(status.pendingDecisionCount)")
                                .font(.caption2)
                                .fontWeight(.medium)
                        }
                        .foregroundColor(.yellow)
                    }

                    // 태스크 상태 (보라)
                    if app.stats.totalTasks > 0 {
                        HStack(spacing: 4) {
                            Image(systemName: "checklist")
                                .font(.caption2)
                            Text("\(app.stats.done)/\(app.stats.totalTasks)")
                                .font(.caption2)
                                .fontWeight(.medium)
                        }
                        .foregroundColor(.purple)
                    }

                    Spacer()
                }

                // 프로젝트 정보 상태 (100%가 아닐 때만 표시)
                let completionPercent = calculateProjectCompletion()
                if completionPercent < 100 {
                    HStack(spacing: 8) {
                        Image(systemName: "folder.fill")
                            .font(.caption2)
                            .foregroundColor(.orange)

                        Text("정보 \(completionPercent)%")
                            .font(.caption2)
                            .foregroundColor(.orange)

                        Spacer()

                        // 다음 작업 수
                        if !app.nextTasks.isEmpty {
                            HStack(spacing: 4) {
                                Image(systemName: "list.bullet")
                                    .font(.caption2)
                                Text("\(app.nextTasks.count)개")
                                    .font(.caption2)
                            }
                            .foregroundColor(.secondary)
                        }
                    }
                } else {
                    // 100%일 때는 다음 작업 수만 표시
                    HStack(spacing: 8) {
                        Spacer()

                        if !app.nextTasks.isEmpty {
                            HStack(spacing: 4) {
                                Image(systemName: "list.bullet")
                                    .font(.caption2)
                                Text("\(app.nextTasks.count)개")
                                    .font(.caption2)
                            }
                            .foregroundColor(.secondary)
                        }
                    }
                }
            }
            .padding(12)
        }
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .strokeBorder(workflowStageColor.opacity(0.3), lineWidth: 2)
        )
        .contentShape(Rectangle())
    }

    private func calculateProjectCompletion() -> Int {
        var totalFields: Double = 7
        var filledFields: Double = 3  // name, bundleId, currentVersion

        if app.minimumOS != nil { filledFields += 1 }
        if app.localProjectPath != nil { filledFields += 1 }
        if app.githubRepo != nil { filledFields += 1 }
        if app.appStoreUrl != nil { filledFields += 1 }

        return Int((filledFields / totalFields) * 100)
    }
}
