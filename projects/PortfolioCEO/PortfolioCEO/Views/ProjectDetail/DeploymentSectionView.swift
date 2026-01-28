import SwiftUI

struct DeploymentSectionView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @State private var showingChecklistManager = false

    private var currentChecklist: DeploymentChecklist? {
        app.deploymentChecklists?.first { $0.version == app.currentVersion }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            // 헤더
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Image(systemName: "arrow.up.doc.fill")
                        .font(.title2)
                        .foregroundColor(.green)
                    Text("배포 준비")
                        .font(.title2)
                        .bold()
                }
                Text("릴리즈 노트를 작성하고 배포 체크리스트를 확인합니다")
                    .font(.body)
                    .foregroundColor(.secondary)
            }

            Divider()

            // 버전별 태스크 그룹
            VStack(alignment: .leading, spacing: 12) {
                Text("버전별 기능 그룹")
                    .font(.headline)

                let groupedTasks = Dictionary(grouping: app.allTasks.filter { $0.targetVersion != nil }, by: { $0.targetVersion! })
                let sortedVersions = groupedTasks.keys.sorted(by: versionCompare)

                if groupedTasks.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "number.circle")
                            .font(.system(size: 48))
                            .foregroundColor(.secondary)
                        Text("버전이 설정된 태스크가 없습니다")
                            .font(.headline)
                        Text("태스크 섹션에서 각 태스크에 배포 버전을 설정하세요")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(40)
                    .background(Color(NSColor.controlBackgroundColor))
                    .cornerRadius(12)
                } else {
                    ForEach(sortedVersions, id: \.self) { version in
                        if let tasks = groupedTasks[version] {
                            VersionGroupCard(version: version, tasks: tasks)
                        }
                    }
                }
            }

            Divider()

            // 버전 정보
            VStack(alignment: .leading, spacing: 12) {
                Text("배포 버전 정보")
                    .font(.headline)

                HStack(spacing: 16) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("현재 버전")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("v\(app.currentVersion)")
                            .font(.title3)
                            .bold()
                    }
                }
                .padding()
                .background(Color.green.opacity(0.05))
                .cornerRadius(12)
            }

            Divider()

            Divider()

            // 배포 체크리스트
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("배포 체크리스트")
                        .font(.headline)

                    Spacer()

                    if let checklist = currentChecklist {
                        Text("\(checklist.items.filter { $0.isCompleted }.count)/\(checklist.items.count) 완료")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    Button(action: { showingChecklistManager = true }) {
                        HStack(spacing: 4) {
                            Image(systemName: "list.bullet.clipboard")
                            Text("관리")
                        }
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.blue.opacity(0.2))
                        .foregroundColor(.blue)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)
                }

                if let checklist = currentChecklist {
                    VStack(spacing: 8) {
                        ForEach(checklist.items) { item in
                            ChecklistItemRow(
                                item: item,
                                onToggle: {
                                    toggleChecklistItem(checklistId: checklist.id, itemId: item.id)
                                }
                            )
                        }
                    }

                    // 진행률 바
                    VStack(alignment: .leading, spacing: 8) {
                        ProgressView(value: checklist.progress)
                            .tint(.green)
                        Text(checklist.isCompleted ? "배포 준비 완료!" : "배포 준비 중...")
                            .font(.caption)
                            .foregroundColor(checklist.isCompleted ? .green : .secondary)
                    }

                    if checklist.isCompleted {
                        Button(action: {}) {
                            HStack {
                                Image(systemName: "paperplane.fill")
                                Text("App Store Connect에서 배포")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                        }
                        .buttonStyle(.plain)
                    }
                } else {
                    VStack(spacing: 16) {
                        Image(systemName: "checklist")
                            .font(.system(size: 48))
                            .foregroundColor(.secondary)
                        Text("체크리스트가 없습니다")
                            .font(.headline)
                        Button(action: createDefaultChecklist) {
                            HStack(spacing: 4) {
                                Image(systemName: "plus.circle.fill")
                                Text("기본 체크리스트 생성")
                            }
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(Color.green.opacity(0.2))
                            .foregroundColor(.green)
                            .cornerRadius(8)
                        }
                        .buttonStyle(.plain)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(40)
                }
            }
        }
        .sheet(isPresented: $showingChecklistManager) {
            ChecklistManagerView(app: app)
                .environmentObject(portfolioService)
        }
    }

    // MARK: - Actions

    private func versionCompare(_ v1: String, _ v2: String) -> Bool {
        let parts1 = v1.split(separator: ".").compactMap { Int($0) }
        let parts2 = v2.split(separator: ".").compactMap { Int($0) }

        for i in 0..<max(parts1.count, parts2.count) {
            let part1 = i < parts1.count ? parts1[i] : 0
            let part2 = i < parts2.count ? parts2[i] : 0

            if part1 != part2 {
                return part1 > part2
            }
        }
        return false
    }

    private func createDefaultChecklist() {
        let checklist = DeploymentChecklist(
            version: app.currentVersion,
            items: ChecklistItem.defaultItems()
        )
        portfolioService.addDeploymentChecklist(appName: app.name, checklist: checklist)
    }

    private func toggleChecklistItem(checklistId: String, itemId: String) {
        guard var checklist = app.deploymentChecklists?.first(where: { $0.id == checklistId }) else {
            return
        }

        if let index = checklist.items.firstIndex(where: { $0.id == itemId }) {
            checklist.items[index].isCompleted.toggle()
            if checklist.items[index].isCompleted {
                checklist.items[index].completedAt = Date()
            } else {
                checklist.items[index].completedAt = nil
            }

            if checklist.isCompleted {
                checklist.completedAt = Date()
            } else {
                checklist.completedAt = nil
            }

            portfolioService.updateDeploymentChecklist(appName: app.name, checklist: checklist)
        }
    }

}

// MARK: - Checklist Item Row

struct ChecklistItemRow: View {
    let item: ChecklistItem
    let onToggle: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Button(action: onToggle) {
                Image(systemName: item.isCompleted ? "checkmark.circle.fill" : "circle")
                    .font(.title3)
                    .foregroundColor(item.isCompleted ? .green : .gray)
            }
            .buttonStyle(.plain)

            VStack(alignment: .leading, spacing: 4) {
                Text(item.title)
                    .font(.body)
                    .foregroundColor(item.isCompleted ? .secondary : .primary)
                    .strikethrough(item.isCompleted)

                if let completedAt = item.completedAt {
                    Text("완료: \(formatDate(completedAt))")
                        .font(.caption2)
                        .foregroundColor(.green)
                }
            }

            Spacer()
        }
        .padding()
        .background(item.isCompleted ? Color.green.opacity(0.05) : Color(NSColor.controlBackgroundColor))
        .cornerRadius(8)
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy.MM.dd HH:mm"
        return formatter.string(from: date)
    }
}

// MARK: - Checklist Manager View

struct ChecklistManagerView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) var dismiss

    @State private var selectedChecklist: DeploymentChecklist?
    @State private var showingAddChecklist = false

    private var sortedChecklists: [DeploymentChecklist] {
        (app.deploymentChecklists ?? []).sorted { c1, c2 in
            compareVersions(c1.version, c2.version) > 0
        }
    }

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                Text("배포 체크리스트 관리")
                    .font(.headline)

                Spacer()

                Button("닫기") {
                    dismiss()
                }
            }
            .padding()

            Divider()

            // 체크리스트 목록
            ScrollView {
                VStack(spacing: 16) {
                    if sortedChecklists.isEmpty {
                        VStack(spacing: 16) {
                            Image(systemName: "checklist")
                                .font(.system(size: 48))
                                .foregroundColor(.secondary)
                            Text("체크리스트가 없습니다")
                                .font(.headline)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(40)
                    } else {
                        ForEach(sortedChecklists) { checklist in
                            ChecklistCard(
                                checklist: checklist,
                                onDelete: {
                                    portfolioService.deleteDeploymentChecklist(appName: app.name, checklistId: checklist.id)
                                }
                            )
                        }
                    }
                }
                .padding()
            }

            Divider()

            // 하단 버튼
            HStack {
                Spacer()

                Button(action: { showingAddChecklist = true }) {
                    HStack(spacing: 4) {
                        Image(systemName: "plus.circle.fill")
                        Text("새 체크리스트")
                    }
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
        .frame(width: 600, height: 500)
        .sheet(isPresented: $showingAddChecklist) {
            ChecklistEditorView(app: app)
                .environmentObject(portfolioService)
        }
    }

    private func compareVersions(_ v1: String, _ v2: String) -> Int {
        let parts1 = v1.split(separator: ".").compactMap { Int($0) }
        let parts2 = v2.split(separator: ".").compactMap { Int($0) }

        for i in 0..<max(parts1.count, parts2.count) {
            let part1 = i < parts1.count ? parts1[i] : 0
            let part2 = i < parts2.count ? parts2[i] : 0

            if part1 != part2 {
                return part1 - part2
            }
        }
        return 0
    }
}

// MARK: - Checklist Card

struct ChecklistCard: View {
    let checklist: DeploymentChecklist
    let onDelete: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                HStack(spacing: 8) {
                    Image(systemName: checklist.isCompleted ? "checkmark.circle.fill" : "circle")
                        .foregroundColor(checklist.isCompleted ? .green : .gray)
                    Text("v\(checklist.version)")
                        .font(.headline)
                }

                Spacer()

                Text(formatDate(checklist.createdAt))
                    .font(.caption)
                    .foregroundColor(.secondary)

                Button(action: onDelete) {
                    Image(systemName: "trash.circle.fill")
                        .foregroundColor(.red)
                }
                .buttonStyle(.plain)
            }

            Divider()

            // 진행률
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text("\(checklist.items.filter { $0.isCompleted }.count)/\(checklist.items.count) 완료")
                        .font(.subheadline)
                    Spacer()
                    Text("\(Int(checklist.progress * 100))%")
                        .font(.subheadline)
                        .foregroundColor(checklist.isCompleted ? .green : .secondary)
                }

                ProgressView(value: checklist.progress)
                    .tint(checklist.isCompleted ? .green : .blue)
            }

            // 항목 요약
            VStack(alignment: .leading, spacing: 4) {
                ForEach(checklist.items.prefix(3)) { item in
                    HStack(spacing: 8) {
                        Image(systemName: item.isCompleted ? "checkmark.circle.fill" : "circle")
                            .font(.caption)
                            .foregroundColor(item.isCompleted ? .green : .gray)
                        Text(item.title)
                            .font(.caption)
                            .foregroundColor(item.isCompleted ? .secondary : .primary)
                            .strikethrough(item.isCompleted)
                    }
                }

                if checklist.items.count > 3 {
                    Text("외 \(checklist.items.count - 3)개 항목...")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy.MM.dd"
        return formatter.string(from: date)
    }
}

// MARK: - Checklist Editor

struct ChecklistEditorView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) var dismiss

    @State private var version: String = ""
    @State private var useTemplate = true
    @State private var items: [ChecklistItem] = ChecklistItem.defaultItems()

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                Text("새 체크리스트")
                    .font(.headline)

                Spacer()

                Button("취소") {
                    dismiss()
                }
            }
            .padding()

            Divider()

            // 입력 폼
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("버전")
                            .font(.subheadline)
                            .bold()
                        TextField("1.0.0", text: $version)
                            .textFieldStyle(.roundedBorder)
                    }

                    Toggle("기본 템플릿 사용", isOn: $useTemplate)
                        .onChange(of: useTemplate) { _, newValue in
                            if newValue {
                                items = ChecklistItem.defaultItems()
                            }
                        }

                    if !useTemplate {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("체크리스트 항목")
                                .font(.subheadline)
                                .bold()

                            ForEach(items.indices, id: \.self) { index in
                                HStack {
                                    TextField("항목 제목", text: $items[index].title)
                                        .textFieldStyle(.roundedBorder)

                                    Button(action: {
                                        items.remove(at: index)
                                    }) {
                                        Image(systemName: "minus.circle.fill")
                                            .foregroundColor(.red)
                                    }
                                    .buttonStyle(.plain)
                                }
                            }

                            Button(action: {
                                items.append(ChecklistItem(title: ""))
                            }) {
                                HStack(spacing: 4) {
                                    Image(systemName: "plus.circle.fill")
                                    Text("항목 추가")
                                }
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
                .padding()
            }

            Divider()

            // 하단 버튼
            HStack {
                Spacer()

                Button("생성") {
                    createChecklist()
                    dismiss()
                }
                .keyboardShortcut(.defaultAction)
                .buttonStyle(.borderedProminent)
                .disabled(version.isEmpty || items.isEmpty)
            }
            .padding()
        }
        .frame(width: 500, height: 600)
        .onAppear {
            version = app.currentVersion
        }
    }

    private func createChecklist() {
        let checklist = DeploymentChecklist(version: version, items: items)
        portfolioService.addDeploymentChecklist(appName: app.name, checklist: checklist)
    }
}

// MARK: - Version Group Card

struct VersionGroupCard: View {
    let version: String
    let tasks: [AppTask]
    @State private var isExpanded = true

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 헤더
            Button(action: {
                withAnimation {
                    isExpanded.toggle()
                }
            }) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        HStack(spacing: 8) {
                            Image(systemName: "number.circle.fill")
                                .foregroundColor(.blue)
                            Text("v\(version)")
                                .font(.headline)
                        }

                        HStack(spacing: 12) {
                            let completedCount = tasks.filter { $0.status == .done }.count
                            let totalCount = tasks.count
                            let progress = Double(completedCount) / Double(totalCount)

                            Text("\(totalCount)개 기능")
                                .font(.caption)
                                .foregroundColor(.secondary)

                            Text("•")
                                .font(.caption)
                                .foregroundColor(.secondary)

                            Text("\(completedCount)개 완료 (\(Int(progress * 100))%)")
                                .font(.caption)
                                .foregroundColor(progress >= 1.0 ? .green : .secondary)
                        }
                    }

                    Spacer()

                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .foregroundColor(.secondary)
                        .font(.caption)
                }
            }
            .buttonStyle(.plain)

            // 태스크 목록
            if isExpanded {
                Divider()

                VStack(alignment: .leading, spacing: 8) {
                    ForEach(tasks) { task in
                        HStack(spacing: 8) {
                            Image(systemName: task.status.icon)
                                .foregroundColor(task.status.color)
                                .font(.caption)

                            Text(task.name)
                                .font(.body)
                                .foregroundColor(task.status == .done ? .secondary : .primary)
                                .strikethrough(task.status == .done)

                            Spacer()

                            Text(task.status.displayName)
                                .font(.caption)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(task.status.color.opacity(0.2))
                                .foregroundColor(task.status.color)
                                .cornerRadius(4)
                        }
                        .padding(.vertical, 4)
                    }
                }

                // 진행률 바
                let completedCount = tasks.filter { $0.status == .done }.count
                let totalCount = tasks.count
                let progress = Double(completedCount) / Double(totalCount)

                VStack(alignment: .leading, spacing: 8) {
                    ProgressView(value: progress)
                        .tint(.blue)
                    Text(progress >= 1.0 ? "✓ 모든 기능 완료!" : "진행 중...")
                        .font(.caption)
                        .foregroundColor(progress >= 1.0 ? .green : .secondary)
                }
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}
