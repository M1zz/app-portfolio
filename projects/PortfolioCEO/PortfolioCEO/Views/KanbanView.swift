import SwiftUI

// MARK: - Kanban Column Type

enum KanbanColumn: String, CaseIterable {
    case backlog = "백로그"
    case todo = "진행전"
    case inProgress = "진행중"
    case done = "완료"

    var color: Color {
        switch self {
        case .backlog: return .gray
        case .todo: return .blue
        case .inProgress: return .orange
        case .done: return .green
        }
    }

    var icon: String {
        switch self {
        case .backlog: return "tray"
        case .todo: return "circle"
        case .inProgress: return "arrow.clockwise.circle.fill"
        case .done: return "checkmark.circle.fill"
        }
    }
}

// MARK: - Kanban Task Item (with app info)

struct KanbanTaskItem: Identifiable {
    let id = UUID()
    let task: AppTask
    let app: AppModel

    var column: KanbanColumn {
        switch task.status {
        case .done:
            return .done
        case .inProgress:
            return .inProgress
        case .notStarted:
            // 백로그: targetDate와 targetVersion이 모두 없는 것
            if task.targetDate == nil && task.targetVersion == nil {
                return .backlog
            }
            return .todo
        }
    }
}

// MARK: - Global Kanban View (전체 앱 태스크)

struct KanbanView: View {
    @EnvironmentObject var portfolio: PortfolioService
    @State private var selectedApp: String? = nil
    @State private var showCompleted = false

    private var allTasks: [KanbanTaskItem] {
        var items: [KanbanTaskItem] = []

        for app in portfolio.apps {
            // 앱 필터 적용
            if let selectedApp = selectedApp, app.name != selectedApp {
                continue
            }

            for task in app.allTasks {
                items.append(KanbanTaskItem(task: task, app: app))
            }
        }

        return items
    }

    private func tasksFor(column: KanbanColumn) -> [KanbanTaskItem] {
        allTasks.filter { $0.column == column }
    }

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("칸반 보드")
                        .font(.title2)
                        .bold()
                    Text("전체 앱의 태스크를 한눈에 관리합니다")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                // 앱 필터
                Picker("앱 필터", selection: $selectedApp) {
                    Text("전체 앱").tag(nil as String?)
                    Divider()
                    ForEach(portfolio.apps) { app in
                        Text(app.name).tag(app.name as String?)
                    }
                }
                .frame(width: 200)

                // 완료 토글
                Toggle(isOn: $showCompleted) {
                    Text("완료 표시")
                        .font(.caption)
                }
                .toggleStyle(.switch)
                .padding(.leading, 16)
            }
            .padding()
            .background(Color(NSColor.controlBackgroundColor))

            Divider()

            // 칸반 컬럼들
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(alignment: .top, spacing: 16) {
                    ForEach(KanbanColumn.allCases, id: \.self) { column in
                        if column == .done && !showCompleted {
                            // 완료 컬럼 숨김 (접힌 상태)
                            CollapsedKanbanColumnView(
                                column: column,
                                count: tasksFor(column: column).count,
                                onExpand: { showCompleted = true }
                            )
                        } else {
                            KanbanColumnView(
                                column: column,
                                tasks: tasksFor(column: column),
                                showAppName: selectedApp == nil
                            )
                        }
                    }
                }
                .padding()
            }
        }
    }
}

// MARK: - Collapsed Column View

struct CollapsedKanbanColumnView: View {
    let column: KanbanColumn
    let count: Int
    let onExpand: () -> Void

    var body: some View {
        VStack(spacing: 12) {
            // 헤더
            HStack(spacing: 6) {
                Image(systemName: column.icon)
                    .foregroundColor(column.color)
                Text(column.rawValue)
                    .font(.headline)
                Text("\(count)")
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 2)
                    .background(column.color.opacity(0.2))
                    .foregroundColor(column.color)
                    .cornerRadius(10)
            }

            Button(action: onExpand) {
                VStack(spacing: 8) {
                    Image(systemName: "eye")
                        .font(.title3)
                    Text("펼치기")
                        .font(.caption)
                }
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 40)
            }
            .buttonStyle(.plain)

            Spacer()
        }
        .frame(width: 80)
        .padding()
        .background(Color(NSColor.controlBackgroundColor).opacity(0.5))
        .cornerRadius(12)
    }
}

// MARK: - Kanban Column View

struct KanbanColumnView: View {
    let column: KanbanColumn
    let tasks: [KanbanTaskItem]
    let showAppName: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 컬럼 헤더
            HStack(spacing: 6) {
                Image(systemName: column.icon)
                    .foregroundColor(column.color)
                Text(column.rawValue)
                    .font(.headline)
                Spacer()
                Text("\(tasks.count)")
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 2)
                    .background(column.color.opacity(0.2))
                    .foregroundColor(column.color)
                    .cornerRadius(10)
            }
            .padding(.bottom, 4)

            Divider()

            // 태스크 카드들
            ScrollView {
                LazyVStack(spacing: 8) {
                    if tasks.isEmpty {
                        Text("태스크 없음")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 40)
                    } else {
                        ForEach(tasks) { item in
                            KanbanTaskCard(item: item, showAppName: showAppName)
                        }
                    }
                }
            }
        }
        .frame(width: 280)
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}

// MARK: - Kanban Task Card

struct KanbanTaskCard: View {
    let item: KanbanTaskItem
    let showAppName: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // 앱 이름 (전체 보기일 때만)
            if showAppName {
                HStack(spacing: 4) {
                    Circle()
                        .fill(item.app.priorityColor)
                        .frame(width: 6, height: 6)
                    Text(item.app.name)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }

            // 태스크 이름
            Text(item.task.name)
                .font(.subheadline)
                .lineLimit(2)

            // 메타 정보
            HStack(spacing: 8) {
                if let targetDate = item.task.targetDate {
                    Label(targetDate, systemImage: "calendar")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }

                if let targetVersion = item.task.targetVersion {
                    Label("v\(targetVersion)", systemImage: "number.circle")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }

                Spacer()
            }

            // 라벨들
            if let labels = item.task.labels, !labels.isEmpty {
                HStack(spacing: 4) {
                    ForEach(labels.prefix(3), id: \.self) { label in
                        Text(label)
                            .font(.caption2)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(labelColor(for: label).opacity(0.2))
                            .foregroundColor(labelColor(for: label))
                            .cornerRadius(4)
                    }

                    if labels.count > 3 {
                        Text("+\(labels.count - 3)")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .padding(12)
        .background(Color(NSColor.textBackgroundColor))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .strokeBorder(item.column.color.opacity(0.3), lineWidth: 1)
        )
    }

    private func labelColor(for label: String) -> Color {
        switch label {
        case "브랜치 시작": return .purple
        case "긴급", "urgent": return .red
        case "버그", "bug": return .red
        case "기능", "feature": return .blue
        default: return .gray
        }
    }
}

// MARK: - App-specific Kanban View (개별 앱용)

struct AppKanbanView: View {
    let app: AppModel
    @State private var showCompleted = false

    private var tasks: [KanbanTaskItem] {
        app.allTasks.map { KanbanTaskItem(task: $0, app: app) }
    }

    private func tasksFor(column: KanbanColumn) -> [KanbanTaskItem] {
        tasks.filter { $0.column == column }
    }

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                Text("칸반 보드")
                    .font(.headline)

                Spacer()

                // 완료 토글
                Toggle(isOn: $showCompleted) {
                    Text("완료 표시")
                        .font(.caption)
                }
                .toggleStyle(.switch)
            }
            .padding(.bottom, 12)

            // 칸반 컬럼들
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(alignment: .top, spacing: 12) {
                    ForEach(KanbanColumn.allCases, id: \.self) { column in
                        if column == .done && !showCompleted {
                            CollapsedKanbanColumnView(
                                column: column,
                                count: tasksFor(column: column).count,
                                onExpand: { showCompleted = true }
                            )
                        } else {
                            KanbanColumnView(
                                column: column,
                                tasks: tasksFor(column: column),
                                showAppName: false
                            )
                        }
                    }
                }
            }
        }
    }
}
