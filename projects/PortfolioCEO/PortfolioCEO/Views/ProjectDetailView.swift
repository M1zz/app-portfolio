import SwiftUI

/// 프로젝트 상세 정보를 보여주는 뷰
/// 프로필처럼 완성도 퍼센트와 편집 기능 제공
struct ProjectDetailView: View {
    let app: AppModel
    @State private var showingEditSheet = false
    @Environment(\.dismiss) var dismiss

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // 헤더: 앱 이름과 완성도
                headerSection

                // 완성도 프로그레스 바
                completionProgressBar

                // 기본 정보 섹션
                basicInfoSection

                // 프로젝트 정보 섹션
                projectInfoSection

                // 앱스토어 정보 섹션
                appStoreInfoSection

                // 통계 섹션
                statsSection
            }
            .padding(24)
        }
        .navigationTitle("프로젝트 상세")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button(action: { showingEditSheet = true }) {
                    Label("편집", systemImage: "pencil.circle.fill")
                        .font(.title3)
                }
            }
        }
        .sheet(isPresented: $showingEditSheet) {
            ProjectEditSheet(app: app)
        }
    }

    // MARK: - Header Section

    private var headerSection: some View {
        VStack(spacing: 12) {
            // 앱 아이콘 플레이스홀더
            RoundedRectangle(cornerRadius: 20)
                .fill(LinearGradient(
                    colors: [.blue.opacity(0.6), .purple.opacity(0.6)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                ))
                .frame(width: 80, height: 80)
                .overlay {
                    Text(String(app.name.prefix(2)))
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.white)
                }

            Text(app.name)
                .font(.title2)
                .fontWeight(.bold)

            Text(app.nameEn)
                .font(.subheadline)
                .foregroundColor(.secondary)

            // 버전과 상태
            HStack(spacing: 12) {
                Label("v\(app.currentVersion)", systemImage: "number.circle.fill")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Text(app.status.displayName)
                    .font(.caption)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 4)
                    .background(app.statusColor.opacity(0.2))
                    .foregroundColor(app.statusColor)
                    .cornerRadius(8)

                Text(app.priority.displayName)
                    .font(.caption)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 4)
                    .background(app.priorityColor.opacity(0.2))
                    .foregroundColor(app.priorityColor)
                    .cornerRadius(8)
            }
        }
    }

    // MARK: - Completion Progress Bar

    private var completionProgressBar: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("프로젝트 정보 완성도")
                    .font(.headline)
                Spacer()
                Text("\(Int(projectCompletionPercentage))%")
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundColor(completionColor)
            }

            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    // 배경
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.gray.opacity(0.2))
                        .frame(height: 12)

                    // 진행 바
                    RoundedRectangle(cornerRadius: 8)
                        .fill(completionColor)
                        .frame(width: geometry.size.width * projectCompletionPercentage / 100, height: 12)
                }
            }
            .frame(height: 12)

            Text(completionMessage)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }

    // MARK: - Basic Info Section

    private var basicInfoSection: some View {
        SectionCard(title: "기본 정보", icon: "info.circle.fill") {
            VStack(spacing: 12) {
                InfoRow(label: "Bundle ID", value: app.bundleId, isFilled: true)
                InfoRow(label: "현재 버전", value: app.currentVersion, isFilled: true)
                InfoRow(
                    label: "최소 OS",
                    value: app.minimumOS ?? "미입력",
                    isFilled: app.minimumOS != nil
                )
            }
        }
    }

    // MARK: - Project Info Section

    private var projectInfoSection: some View {
        SectionCard(title: "프로젝트 정보", icon: "folder.fill") {
            VStack(spacing: 12) {
                InfoRow(
                    label: "로컬 경로",
                    value: app.localProjectPath ?? "미입력",
                    isFilled: app.localProjectPath != nil,
                    isCritical: true
                )
                InfoRow(
                    label: "GitHub 저장소",
                    value: app.githubRepo ?? "미입력",
                    isFilled: app.githubRepo != nil
                )

                if let modules = app.sharedModules, !modules.isEmpty {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("공유 모듈")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        FlowLayout(spacing: 6) {
                            ForEach(modules, id: \.self) { module in
                                Text(module)
                                    .font(.caption2)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
                                    .background(Color.blue.opacity(0.1))
                                    .foregroundColor(.blue)
                                    .cornerRadius(6)
                            }
                        }
                    }
                }
            }
        }
    }

    // MARK: - App Store Info Section

    private var appStoreInfoSection: some View {
        SectionCard(title: "App Store", icon: "app.badge.fill") {
            VStack(spacing: 12) {
                InfoRow(
                    label: "App Store URL",
                    value: app.appStoreUrl ?? "미입력",
                    isFilled: app.appStoreUrl != nil
                )

                if let appStoreUrl = app.appStoreUrl, let url = URL(string: appStoreUrl) {
                    Link(destination: url) {
                        HStack {
                            Image(systemName: "arrow.up.right.square")
                            Text("App Store에서 보기")
                        }
                        .font(.caption)
                        .foregroundColor(.blue)
                    }
                }
            }
        }
    }

    // MARK: - Stats Section

    private var statsSection: some View {
        SectionCard(title: "작업 통계", icon: "chart.bar.fill") {
            VStack(spacing: 12) {
                StatsRow(label: "전체 작업", value: "\(app.stats.totalTasks)개")
                StatsRow(label: "완료", value: "\(app.stats.done)개", color: .green)
                StatsRow(label: "진행중", value: "\(app.stats.inProgress)개", color: .orange)
                StatsRow(label: "대기", value: "\(app.stats.notStarted)개", color: .gray)

                Divider()
                    .padding(.vertical, 4)

                HStack {
                    Text("완료율")
                        .font(.headline)
                    Spacer()
                    Text("\(Int(app.completionRate))%")
                        .font(.title3)
                        .fontWeight(.bold)
                        .foregroundColor(app.progressColor)
                }
            }
        }
    }

    // MARK: - Computed Properties

    /// 프로젝트 정보 완성도 계산
    private var projectCompletionPercentage: Double {
        var totalFields: Double = 7  // 전체 필드 수
        var filledFields: Double = 3 // 기본적으로 채워진 필드 (name, bundleId, currentVersion)

        if app.minimumOS != nil { filledFields += 1 }
        if app.localProjectPath != nil { filledFields += 1 }
        if app.githubRepo != nil { filledFields += 1 }
        if app.appStoreUrl != nil { filledFields += 1 }

        return (filledFields / totalFields) * 100
    }

    private var completionColor: Color {
        switch projectCompletionPercentage {
        case 80...100: return .green
        case 50..<80: return .orange
        default: return .red
        }
    }

    private var completionMessage: String {
        let missingCount = app.missingInfoFeedbacks.filter { $0.severity == .required }.count

        if projectCompletionPercentage == 100 {
            return "✅ 모든 정보가 입력되었습니다"
        } else if missingCount > 0 {
            return "⚠️ 필수 정보 \(missingCount)개가 누락되었습니다"
        } else {
            return "💡 권장 정보를 추가하면 더 효율적으로 관리할 수 있습니다"
        }
    }
}

// MARK: - Supporting Views

struct SectionCard<Content: View>: View {
    let title: String
    let icon: String
    let content: Content

    init(title: String, icon: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.icon = icon
        self.content = content()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .foregroundColor(.blue)
                Text(title)
                    .font(.headline)
            }

            content
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}

struct InfoRow: View {
    let label: String
    let value: String
    let isFilled: Bool
    var isCritical: Bool = false

    var body: some View {
        HStack(alignment: .top) {
            Text(label)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .frame(width: 120, alignment: .leading)

            HStack(spacing: 6) {
                if !isFilled {
                    Image(systemName: isCritical ? "exclamationmark.circle.fill" : "info.circle")
                        .foregroundColor(isCritical ? .red : .orange)
                        .font(.caption)
                }

                Text(value)
                    .font(.subheadline)
                    .foregroundColor(isFilled ? .primary : .secondary)
                    .textSelection(.enabled)
            }

            Spacer()
        }
    }
}

struct StatsRow: View {
    let label: String
    let value: String
    var color: Color = .primary

    var body: some View {
        HStack {
            Text(label)
                .font(.subheadline)
                .foregroundColor(.secondary)
            Spacer()
            Text(value)
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundColor(color)
        }
    }
}

// MARK: - FlowLayout for Tags

struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = FlowResult(
            in: proposal.replacingUnspecifiedDimensions().width,
            subviews: subviews,
            spacing: spacing
        )
        return result.size
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = FlowResult(
            in: bounds.width,
            subviews: subviews,
            spacing: spacing
        )
        for (index, subview) in subviews.enumerated() {
            subview.place(at: result.positions[index], proposal: .unspecified)
        }
    }

    struct FlowResult {
        var size: CGSize
        var positions: [CGPoint]

        init(in maxWidth: CGFloat, subviews: Subviews, spacing: CGFloat) {
            var positions: [CGPoint] = []
            var currentX: CGFloat = 0
            var currentY: CGFloat = 0
            var lineHeight: CGFloat = 0

            for subview in subviews {
                let size = subview.sizeThatFits(.unspecified)

                if currentX + size.width > maxWidth, currentX > 0 {
                    currentX = 0
                    currentY += lineHeight + spacing
                    lineHeight = 0
                }

                positions.append(CGPoint(x: currentX, y: currentY))
                currentX += size.width + spacing
                lineHeight = max(lineHeight, size.height)
            }

            self.positions = positions
            self.size = CGSize(width: maxWidth, height: currentY + lineHeight)
        }
    }
}

// MARK: - Project Edit Sheet

struct ProjectEditSheet: View {
    let app: AppModel
    @Environment(\.dismiss) var dismiss

    @State private var projectName: String = ""
    @State private var projectNameEn: String = ""
    @State private var currentVersion: String = ""
    @State private var localProjectPath: String = ""
    @State private var githubRepo: String = ""
    @State private var appStoreUrl: String = ""
    @State private var minimumOS: String = ""
    @State private var isSaving = false

    var body: some View {
        NavigationStack {
            Form {
                Section("기본 정보") {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("프로젝트 이름 (한글)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        TextField("예: 버킷 클라임", text: $projectName)
                            .textFieldStyle(.roundedBorder)
                    }

                    VStack(alignment: .leading, spacing: 6) {
                        Text("프로젝트 이름 (영문)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        TextField("예: Bucket Climb", text: $projectNameEn)
                            .textFieldStyle(.roundedBorder)
                    }

                    VStack(alignment: .leading, spacing: 6) {
                        Text("현재 버전")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        TextField("예: 1.2.0", text: $currentVersion)
                            .textFieldStyle(.roundedBorder)
                    }
                }

                Section("프로젝트 정보") {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("로컬 프로젝트 경로")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        TextField("예: ~/Projects/MyApp", text: $localProjectPath)
                            .textFieldStyle(.roundedBorder)
                    }

                    VStack(alignment: .leading, spacing: 6) {
                        Text("GitHub 저장소")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        TextField("예: https://github.com/user/repo", text: $githubRepo)
                            .textFieldStyle(.roundedBorder)
                    }
                }

                Section("App Store 정보") {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("App Store URL")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        TextField("예: https://apps.apple.com/app/id1234567890", text: $appStoreUrl)
                            .textFieldStyle(.roundedBorder)
                    }

                    VStack(alignment: .leading, spacing: 6) {
                        Text("최소 지원 OS")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        TextField("예: iOS 15.0", text: $minimumOS)
                            .textFieldStyle(.roundedBorder)
                    }
                }
            }
            .formStyle(.grouped)
            .navigationTitle("프로젝트 정보 수정")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("취소") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button(isSaving ? "저장 중..." : "저장") {
                        saveChanges()
                    }
                    .disabled(isSaving)
                }
            }
            .onAppear {
                loadCurrentInfo()
            }
        }
        .frame(width: 500, height: 500)
    }

    private func loadCurrentInfo() {
        projectName = app.name
        projectNameEn = app.nameEn
        currentVersion = app.currentVersion
        localProjectPath = app.localProjectPath ?? ""
        githubRepo = app.githubRepo ?? ""
        appStoreUrl = app.appStoreUrl ?? ""
        minimumOS = app.minimumOS ?? ""

        print("📝 [ProjectEditSheet] 현재 정보 로드: \(app.name)")
    }

    private func saveChanges() {
        isSaving = true
        print("💾 [ProjectEditSheet] 저장 시작: \(app.name)")

        PortfolioService.shared.updateProjectInfo(
            appName: app.name,
            newName: projectName.isEmpty ? nil : projectName,
            newNameEn: projectNameEn.isEmpty ? nil : projectNameEn,
            currentVersion: currentVersion.isEmpty ? nil : currentVersion,
            localProjectPath: localProjectPath.isEmpty ? nil : localProjectPath,
            githubRepo: githubRepo.isEmpty ? nil : githubRepo,
            appStoreUrl: appStoreUrl.isEmpty ? nil : appStoreUrl,
            minimumOS: minimumOS.isEmpty ? nil : minimumOS
        )

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            isSaving = false
            print("✅ [ProjectEditSheet] 저장 완료")
            dismiss()
        }
    }
}
