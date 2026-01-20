import SwiftUI

struct AppDetailView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @EnvironmentObject var detailService: AppDetailService

    @State private var selectedSection: DetailSection = .feedback

    var appDetail: AppDetailInfo? {
        if let folder = getFolderName(for: app.name) {
            return detailService.loadDetail(for: folder)
        }
        return nil
    }

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            headerSection
                .padding()
                .background(Color(NSColor.windowBackgroundColor))

            Divider()

            // 섹션 탭
            sectionTabs
                .padding(.horizontal)
                .padding(.vertical, 12)
                .background(Color(NSColor.windowBackgroundColor))

            Divider()

            // 선택된 섹션 컨텐츠
            ScrollView {
                Group {
                    switch selectedSection {
                    case .feedback:
                        FeedbackSectionView(app: app, appDetail: appDetail)
                    case .planning:
                        PlanningSectionView(app: app)
                    case .tasks:
                        TasksSectionView(app: app)
                    case .testing:
                        TestingSectionView(app: app)
                    case .deployment:
                        DeploymentSectionView(app: app)
                    }
                }
                .padding()
            }
        }
        .navigationTitle(app.name)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                NavigationLink(destination: ProjectDetailView(app: app)) {
                    Label("프로젝트 정보", systemImage: "info.circle")
                }
            }
        }
    }

    // MARK: - Header

    private var headerSection: some View {
        HStack(alignment: .top, spacing: 16) {
            // 상태 아이콘
            Circle()
                .fill(app.statusColor)
                .frame(width: 12, height: 12)
                .padding(.top, 8)

            VStack(alignment: .leading, spacing: 8) {
                Text(app.name)
                    .font(.system(size: 24, weight: .bold))

                if let detail = appDetail, !detail.description.isEmpty {
                    Text(detail.description)
                        .font(.body)
                        .foregroundColor(.secondary)
                }

                HStack(spacing: 16) {
                    Label("v\(app.currentVersion)", systemImage: "number.circle")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    Label(app.status.displayName, systemImage: "circle.fill")
                        .font(.caption)
                        .foregroundColor(app.statusColor)

                    if let detail = appDetail {
                        Label(detail.techStack.platforms.joined(separator: ", "), systemImage: "iphone")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }

            Spacer()
        }
    }

    // MARK: - Section Tabs

    private var sectionTabs: some View {
        HStack(spacing: 0) {
            ForEach(DetailSection.allCases, id: \.self) { section in
                Button(action: {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        selectedSection = section
                    }
                }) {
                    VStack(spacing: 8) {
                        Image(systemName: section.icon)
                            .font(.system(size: 20))
                            .foregroundColor(selectedSection == section ? .white : section.color)

                        Text(section.rawValue)
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(selectedSection == section ? .white : .primary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(selectedSection == section ? section.color : Color(NSColor.controlBackgroundColor))
                    .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
            }
        }
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.gray.opacity(0.2), lineWidth: 1)
        )
    }

    // MARK: - Helper

    private func getFolderName(for appName: String) -> String? {
        let fileManager = FileManager.default
        let home = fileManager.homeDirectoryForCurrentUser
        let mappingPath = home
            .appendingPathComponent("Documents/workspace/code/app-portfolio")
            .appendingPathComponent("app-name-mapping.json")

        guard let data = try? Data(contentsOf: mappingPath),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let apps = json["apps"] as? [String: [String: String]],
              let appInfo = apps[appName],
              let folder = appInfo["folder"] else {
            return nil
        }

        return folder
    }
}

// MARK: - Detail Section Enum

enum DetailSection: String, CaseIterable {
    case feedback = "피드백"
    case planning = "기획 의사결정"
    case tasks = "태스크"
    case testing = "테스트"
    case deployment = "배포 준비"

    var icon: String {
        switch self {
        case .feedback: return "bubble.left.and.bubble.right.fill"
        case .planning: return "lightbulb.fill"
        case .tasks: return "checklist"
        case .testing: return "checkmark.shield.fill"
        case .deployment: return "arrow.up.doc.fill"
        }
    }

    var color: Color {
        switch self {
        case .feedback: return .blue
        case .planning: return .yellow
        case .tasks: return .purple
        case .testing: return .orange
        case .deployment: return .green
        }
    }
}
