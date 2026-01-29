import SwiftUI

struct DeploymentSectionView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @State private var showingChecklistManager = false
    @State private var showingVersionHistory = false
    @State private var showingMetadataEditor = false
    @State private var showingScreenshotManager = false
    @State private var showingReminderEditor = false
    @State private var showingBuildAutomationEditor = false

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
                            .font(.body)
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
                HStack {
                    Text("배포 버전 정보")
                        .font(.headline)

                    Spacer()

                    Button(action: { showingScreenshotManager = true }) {
                        HStack(spacing: 4) {
                            Image(systemName: "photo")
                            Text("스크린샷")
                        }
                        .font(.body)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.pink.opacity(0.2))
                        .foregroundColor(.pink)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)

                    Button(action: { showingMetadataEditor = true }) {
                        HStack(spacing: 4) {
                            Image(systemName: "info.circle")
                            Text("앱스토어 정보")
                        }
                        .font(.body)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.blue.opacity(0.2))
                        .foregroundColor(.blue)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)

                    Button(action: { showingVersionHistory = true }) {
                        HStack(spacing: 4) {
                            Image(systemName: "clock.arrow.circlepath")
                            Text("히스토리")
                        }
                        .font(.body)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.purple.opacity(0.2))
                        .foregroundColor(.purple)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)
                }

                HStack(spacing: 16) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("현재 버전")
                            .font(.body)
                            .foregroundColor(.secondary)
                        Text("v\(app.currentVersion)")
                            .font(.title3)
                            .bold()
                    }

                    Divider()
                        .frame(height: 40)

                    VStack(alignment: .leading, spacing: 4) {
                        Text("배포된 버전")
                            .font(.body)
                            .foregroundColor(.secondary)
                        if let history = app.versionHistory, !history.isEmpty {
                            Text("\(history.filter { $0.status == .released }.count)개")
                                .font(.title3)
                                .foregroundColor(.green)
                        } else {
                            Text("0개")
                                .font(.title3)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                .padding()
                .background(Color.green.opacity(0.05))
                .cornerRadius(12)
            }

            Divider()

            Divider()

            // 배포 알림 설정
            VStack(alignment: .leading, spacing: 12) {
                Text("배포 알림 설정")
                    .font(.headline)

                if let reminder = app.deploymentReminder {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: reminder.enabled ? "bell.fill" : "bell.slash")
                                .foregroundColor(reminder.enabled ? .blue : .secondary)
                            Text(reminder.enabled ? "알림 활성화" : "알림 비활성화")
                                .font(.subheadline)

                            Spacer()

                            Button(action: { showingReminderEditor = true }) {
                                HStack(spacing: 4) {
                                    Image(systemName: "gear")
                                    Text("설정")
                                }
                                .font(.body)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.gray.opacity(0.2))
                                .foregroundColor(.gray)
                                .cornerRadius(6)
                            }
                            .buttonStyle(.plain)
                        }

                        if reminder.enabled {
                            HStack(spacing: 20) {
                                if let days = reminder.daysSinceLastDeployment {
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text("마지막 배포")
                                            .font(.body)
                                            .foregroundColor(.secondary)
                                        Text("\(days)일 전")
                                            .font(.body)
                                            .foregroundColor(days >= reminder.reminderDays ? .red : .primary)
                                    }
                                }

                                if let days = reminder.daysUntilNextPlanned, days > 0 {
                                    Divider()
                                        .frame(height: 30)

                                    VStack(alignment: .leading, spacing: 4) {
                                        Text("다음 배포 예정")
                                            .font(.body)
                                            .foregroundColor(.secondary)
                                        Text("\(days)일 후")
                                            .font(.body)
                                            .foregroundColor(.blue)
                                    }
                                }
                            }
                            .padding()
                            .background(reminder.shouldRemind ? Color.red.opacity(0.1) : Color(NSColor.controlBackgroundColor))
                            .cornerRadius(8)

                            if reminder.shouldRemind {
                                HStack(spacing: 8) {
                                    Image(systemName: "exclamationmark.triangle.fill")
                                        .foregroundColor(.orange)
                                    Text("배포를 고려해보세요")
                                        .font(.subheadline)
                                        .foregroundColor(.orange)
                                }
                                .padding(12)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color.orange.opacity(0.1))
                                .cornerRadius(8)
                            }
                        }
                    }
                } else {
                    VStack(spacing: 16) {
                        Image(systemName: "bell.badge")
                            .font(.system(size: 32))
                            .foregroundColor(.secondary)
                        Text("배포 알림이 설정되지 않았습니다")
                            .font(.subheadline)
                        Button(action: { showingReminderEditor = true }) {
                            HStack(spacing: 4) {
                                Image(systemName: "plus.circle.fill")
                                Text("알림 설정")
                            }
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(Color.blue.opacity(0.2))
                            .foregroundColor(.blue)
                            .cornerRadius(8)
                        }
                        .buttonStyle(.plain)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(20)
                    .background(Color(NSColor.controlBackgroundColor))
                    .cornerRadius(12)
                }
            }

            Divider()

            // 빌드 자동화
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("빌드 자동화")
                        .font(.headline)

                    Spacer()

                    Button(action: { showingBuildAutomationEditor = true }) {
                        HStack(spacing: 4) {
                            Image(systemName: "gear")
                            Text("설정")
                        }
                        .font(.body)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.orange.opacity(0.2))
                        .foregroundColor(.orange)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)
                }

                if let automation = app.buildAutomation {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack(spacing: 20) {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("빌드 번호")
                                    .font(.body)
                                    .foregroundColor(.secondary)
                                Text("\(automation.buildNumber)")
                                    .font(.title3)
                                    .bold()
                            }

                            Divider()
                                .frame(height: 40)

                            VStack(alignment: .leading, spacing: 4) {
                                Text("자동 증가")
                                    .font(.body)
                                    .foregroundColor(.secondary)
                                Text(automation.autoincrementEnabled ? "활성화" : "비활성화")
                                    .font(.body)
                                    .foregroundColor(automation.autoincrementEnabled ? .green : .secondary)
                            }

                            if let lastBuild = automation.lastBuildDate {
                                Divider()
                                    .frame(height: 40)

                                VStack(alignment: .leading, spacing: 4) {
                                    Text("마지막 빌드")
                                        .font(.body)
                                        .foregroundColor(.secondary)
                                    Text(formatDate(lastBuild))
                                        .font(.body)
                                }
                            }
                        }
                        .padding()
                        .background(Color.orange.opacity(0.05))
                        .cornerRadius(8)

                        if !automation.buildScripts.isEmpty {
                            Text("빌드 스크립트")
                                .font(.subheadline)
                                .bold()

                            VStack(spacing: 8) {
                                ForEach(automation.buildScripts) { script in
                                    HStack {
                                        Image(systemName: script.enabled ? "checkmark.circle.fill" : "circle")
                                            .foregroundColor(script.enabled ? .green : .gray)
                                        Text(script.name)
                                            .font(.body)
                                        Spacer()
                                        Text(script.phase.rawValue)
                                            .font(.body)
                                            .padding(.horizontal, 8)
                                            .padding(.vertical, 4)
                                            .background(Color.orange.opacity(0.2))
                                            .foregroundColor(.orange)
                                            .cornerRadius(4)
                                    }
                                    .padding()
                                    .background(Color(NSColor.controlBackgroundColor))
                                    .cornerRadius(8)
                                }
                            }
                        }

                        Button(action: {
                            portfolioService.incrementBuildNumber(appName: app.name)
                        }) {
                            HStack {
                                Image(systemName: "plus.circle.fill")
                                Text("빌드 번호 증가")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.orange.opacity(0.2))
                            .foregroundColor(.orange)
                            .cornerRadius(8)
                        }
                        .buttonStyle(.plain)
                    }
                } else {
                    VStack(spacing: 16) {
                        Image(systemName: "hammer.circle")
                            .font(.system(size: 32))
                            .foregroundColor(.secondary)
                        Text("빌드 자동화가 설정되지 않았습니다")
                            .font(.subheadline)
                        Button(action: { showingBuildAutomationEditor = true }) {
                            HStack(spacing: 4) {
                                Image(systemName: "plus.circle.fill")
                                Text("설정 시작")
                            }
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(Color.orange.opacity(0.2))
                            .foregroundColor(.orange)
                            .cornerRadius(8)
                        }
                        .buttonStyle(.plain)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(20)
                    .background(Color(NSColor.controlBackgroundColor))
                    .cornerRadius(12)
                }
            }

            Divider()

            // 배포 체크리스트
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("배포 체크리스트")
                        .font(.headline)

                    Spacer()

                    if let checklist = currentChecklist {
                        Text("\(checklist.items.filter { $0.isCompleted }.count)/\(checklist.items.count) 완료")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    Button(action: { showingChecklistManager = true }) {
                        HStack(spacing: 4) {
                            Image(systemName: "list.bullet.clipboard")
                            Text("관리")
                        }
                        .font(.body)
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
                            .font(.body)
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
        .sheet(isPresented: $showingVersionHistory) {
            VersionHistoryView(app: app)
                .environmentObject(portfolioService)
        }
        .sheet(isPresented: $showingMetadataEditor) {
            AppStoreMetadataEditorView(app: app)
                .environmentObject(portfolioService)
        }
        .sheet(isPresented: $showingScreenshotManager) {
            ScreenshotManagerView(app: app)
                .environmentObject(portfolioService)
        }
        .sheet(isPresented: $showingReminderEditor) {
            DeploymentReminderEditorView(app: app)
                .environmentObject(portfolioService)
        }
        .sheet(isPresented: $showingBuildAutomationEditor) {
            BuildAutomationEditorView(app: app)
                .environmentObject(portfolioService)
        }
    }

    // MARK: - Actions

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy.MM.dd"
        return formatter.string(from: date)
    }

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
                        .font(.body)
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
                    .font(.body)
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
                            .font(.body)
                            .foregroundColor(item.isCompleted ? .green : .gray)
                        Text(item.title)
                            .font(.body)
                            .foregroundColor(item.isCompleted ? .secondary : .primary)
                            .strikethrough(item.isCompleted)
                    }
                }

                if checklist.items.count > 3 {
                    Text("외 \(checklist.items.count - 3)개 항목...")
                        .font(.body)
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
                                .font(.body)
                                .foregroundColor(.secondary)

                            Text("•")
                                .font(.body)
                                .foregroundColor(.secondary)

                            Text("\(completedCount)개 완료 (\(Int(progress * 100))%)")
                                .font(.body)
                                .foregroundColor(progress >= 1.0 ? .green : .secondary)
                        }
                    }

                    Spacer()

                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .foregroundColor(.secondary)
                        .font(.body)
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
                                .font(.body)

                            Text(task.name)
                                .font(.body)
                                .foregroundColor(task.status == .done ? .secondary : .primary)
                                .strikethrough(task.status == .done)

                            Spacer()

                            Text(task.status.displayName)
                                .font(.body)
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
                        .font(.body)
                        .foregroundColor(progress >= 1.0 ? .green : .secondary)
                }
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}

// MARK: - Version History View

struct VersionHistoryView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) var dismiss

    @State private var showingAddHistory = false
    @State private var selectedHistory: VersionHistory?
    @State private var showingEditHistory = false

    private var sortedHistory: [VersionHistory] {
        (app.versionHistory ?? []).sorted { h1, h2 in
            compareVersions(h1.version, h2.version) > 0
        }
    }

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                Text("버전 히스토리")
                    .font(.headline)

                Spacer()

                Button("닫기") {
                    dismiss()
                }
            }
            .padding()

            Divider()

            // 히스토리 목록
            ScrollView {
                VStack(spacing: 20) {
                    if sortedHistory.isEmpty {
                        VStack(spacing: 16) {
                            Image(systemName: "clock.arrow.circlepath")
                                .font(.system(size: 48))
                                .foregroundColor(.secondary)
                            Text("버전 히스토리가 없습니다")
                                .font(.headline)
                            Text("버전별 배포 이력을 기록하여 관리하세요")
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(40)
                    } else {
                        // 타임라인
                        VStack(alignment: .leading, spacing: 0) {
                            ForEach(sortedHistory.indices, id: \.self) { index in
                                VersionHistoryCard(
                                    history: sortedHistory[index],
                                    isLast: index == sortedHistory.count - 1,
                                    onEdit: {
                                        selectedHistory = sortedHistory[index]
                                        showingEditHistory = true
                                    },
                                    onDelete: {
                                        portfolioService.deleteVersionHistory(appName: app.name, historyId: sortedHistory[index].id)
                                    }
                                )
                            }
                        }
                    }
                }
                .padding()
            }

            Divider()

            // 하단 버튼
            HStack {
                Spacer()

                Button(action: { showingAddHistory = true }) {
                    HStack(spacing: 4) {
                        Image(systemName: "plus.circle.fill")
                        Text("버전 추가")
                    }
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
        .frame(width: 700, height: 600)
        .sheet(isPresented: $showingAddHistory) {
            VersionHistoryEditorView(app: app, existingHistory: nil)
                .environmentObject(portfolioService)
        }
        .sheet(isPresented: $showingEditHistory) {
            if let history = selectedHistory {
                VersionHistoryEditorView(app: app, existingHistory: history)
                    .environmentObject(portfolioService)
            }
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

// MARK: - Version History Card

struct VersionHistoryCard: View {
    let history: VersionHistory
    let isLast: Bool
    let onEdit: () -> Void
    let onDelete: () -> Void

    var body: some View {
        HStack(alignment: .top, spacing: 16) {
            // 타임라인 아이콘
            VStack(spacing: 0) {
                Image(systemName: history.status.icon)
                    .font(.system(size: 20))
                    .foregroundColor(history.status.color)
                    .frame(width: 40, height: 40)
                    .background(Circle().fill(history.status.color.opacity(0.2)))

                if !isLast {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .frame(width: 2)
                        .padding(.vertical, 8)
                }
            }

            // 버전 정보
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("v\(history.version)")
                        .font(.title3)
                        .bold()

                    Text(history.status.rawValue)
                        .font(.body)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(history.status.color.opacity(0.2))
                        .foregroundColor(history.status.color)
                        .cornerRadius(6)

                    Spacer()

                    if let releaseDate = history.releaseDate {
                        Text(formatDate(releaseDate))
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    Button(action: onEdit) {
                        Image(systemName: "pencil.circle.fill")
                            .foregroundColor(.blue)
                    }
                    .buttonStyle(.plain)

                    Button(action: onDelete) {
                        Image(systemName: "trash.circle.fill")
                            .foregroundColor(.red)
                    }
                    .buttonStyle(.plain)
                }

                if !history.changelog.isEmpty {
                    Text(history.changelog)
                        .font(.body)
                        .foregroundColor(.primary)
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color(NSColor.controlBackgroundColor))
                        .cornerRadius(8)
                }

                if let appStoreUrl = history.appStoreUrl, !appStoreUrl.isEmpty {
                    Link(destination: URL(string: appStoreUrl)!) {
                        HStack(spacing: 4) {
                            Image(systemName: "link")
                            Text("App Store 링크")
                        }
                        .font(.body)
                        .foregroundColor(.blue)
                    }
                }
            }
            .padding(.bottom, isLast ? 0 : 20)
        }
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy.MM.dd"
        return formatter.string(from: date)
    }
}

// MARK: - Version History Editor

struct VersionHistoryEditorView: View {
    let app: AppModel
    let existingHistory: VersionHistory?

    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) var dismiss

    @State private var version: String = ""
    @State private var status: DeploymentStatus = .preparing
    @State private var releaseDate: Date = Date()
    @State private var changelog: String = ""
    @State private var appStoreUrl: String = ""
    @State private var hasReleaseDate = false

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                Text(existingHistory == nil ? "새 버전 추가" : "버전 히스토리 편집")
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

                    VStack(alignment: .leading, spacing: 8) {
                        Text("상태")
                            .font(.subheadline)
                            .bold()
                        Picker("", selection: $status) {
                            ForEach(DeploymentStatus.allCases, id: \.self) { status in
                                HStack {
                                    Image(systemName: status.icon)
                                    Text(status.rawValue)
                                }
                                .tag(status)
                            }
                        }
                        .pickerStyle(.segmented)
                    }

                    Toggle("배포일 설정", isOn: $hasReleaseDate)

                    if hasReleaseDate {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("배포일")
                                .font(.subheadline)
                                .bold()
                            DatePicker("", selection: $releaseDate, displayedComponents: .date)
                                .labelsHidden()
                        }
                    }

                    Divider()

                    VStack(alignment: .leading, spacing: 8) {
                        Text("변경사항")
                            .font(.subheadline)
                            .bold()

                        TextEditor(text: $changelog)
                            .frame(minHeight: 150)
                            .padding(8)
                            .background(Color(NSColor.textBackgroundColor))
                            .cornerRadius(8)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                            )

                        Text("주요 변경사항을 요약하여 작성하세요")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        Text("App Store URL (선택)")
                            .font(.subheadline)
                            .bold()
                        TextField("https://apps.apple.com/...", text: $appStoreUrl)
                            .textFieldStyle(.roundedBorder)
                    }
                }
                .padding()
            }

            Divider()

            // 하단 버튼
            HStack {
                Spacer()

                Button("저장") {
                    saveHistory()
                    dismiss()
                }
                .keyboardShortcut(.defaultAction)
                .buttonStyle(.borderedProminent)
                .disabled(version.isEmpty)
            }
            .padding()
        }
        .frame(width: 600, height: 650)
        .onAppear {
            if let history = existingHistory {
                version = history.version
                status = history.status
                releaseDate = history.releaseDate ?? Date()
                hasReleaseDate = history.releaseDate != nil
                changelog = history.changelog
                appStoreUrl = history.appStoreUrl ?? ""
            } else {
                version = app.currentVersion
            }
        }
    }

    private func saveHistory() {
        let history = VersionHistory(
            id: existingHistory?.id ?? UUID().uuidString,
            version: version,
            releaseDate: hasReleaseDate ? releaseDate : nil,
            status: status,
            changelog: changelog,
            appStoreUrl: appStoreUrl.isEmpty ? nil : appStoreUrl
        )

        if existingHistory != nil {
            portfolioService.updateVersionHistory(appName: app.name, history: history)
        } else {
            portfolioService.addVersionHistory(appName: app.name, history: history)
        }
    }
}

// MARK: - App Store Metadata Editor

struct AppStoreMetadataEditorView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) var dismiss

    @State private var descriptionKo: String = ""
    @State private var descriptionEn: String = ""
    @State private var keywords: String = ""
    @State private var promotionalText: String = ""
    @State private var supportUrl: String = ""
    @State private var privacyUrl: String = ""
    @State private var ageRating: String = ""
    @State private var primaryCategory: String = ""
    @State private var secondaryCategory: String = ""

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                Text("App Store 메타데이터")
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
                    // 앱 설명
                    VStack(alignment: .leading, spacing: 8) {
                        Text("앱 설명 (한글)")
                            .font(.subheadline)
                            .bold()

                        TextEditor(text: $descriptionKo)
                            .frame(minHeight: 100)
                            .padding(8)
                            .background(Color(NSColor.textBackgroundColor))
                            .cornerRadius(8)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                            )

                        Text("최대 4000자")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        Text("App Description (English)")
                            .font(.subheadline)
                            .bold()

                        TextEditor(text: $descriptionEn)
                            .frame(minHeight: 100)
                            .padding(8)
                            .background(Color(NSColor.textBackgroundColor))
                            .cornerRadius(8)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                            )

                        Text("Maximum 4000 characters")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    Divider()

                    // 키워드
                    VStack(alignment: .leading, spacing: 8) {
                        Text("키워드")
                            .font(.subheadline)
                            .bold()

                        TextField("키워드1, 키워드2, 키워드3", text: $keywords)
                            .textFieldStyle(.roundedBorder)

                        Text("쉼표로 구분하여 입력 (최대 100자)")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    // 프로모션 텍스트
                    VStack(alignment: .leading, spacing: 8) {
                        Text("프로모션 텍스트")
                            .font(.subheadline)
                            .bold()

                        TextEditor(text: $promotionalText)
                            .frame(minHeight: 60)
                            .padding(8)
                            .background(Color(NSColor.textBackgroundColor))
                            .cornerRadius(8)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                            )

                        Text("앱 스토어 검색 결과 상단에 표시되는 텍스트 (최대 170자)")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    Divider()

                    // URL들
                    VStack(alignment: .leading, spacing: 8) {
                        Text("지원 URL")
                            .font(.subheadline)
                            .bold()
                        TextField("https://...", text: $supportUrl)
                            .textFieldStyle(.roundedBorder)
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        Text("개인정보 처리방침 URL")
                            .font(.subheadline)
                            .bold()
                        TextField("https://...", text: $privacyUrl)
                            .textFieldStyle(.roundedBorder)
                    }

                    Divider()

                    // 연령 등급 및 카테고리
                    HStack(spacing: 20) {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("연령 등급")
                                .font(.subheadline)
                                .bold()
                            TextField("4+", text: $ageRating)
                                .textFieldStyle(.roundedBorder)
                        }

                        VStack(alignment: .leading, spacing: 8) {
                            Text("기본 카테고리")
                                .font(.subheadline)
                                .bold()
                            TextField("유틸리티", text: $primaryCategory)
                                .textFieldStyle(.roundedBorder)
                        }

                        VStack(alignment: .leading, spacing: 8) {
                            Text("보조 카테고리")
                                .font(.subheadline)
                                .bold()
                            TextField("생산성", text: $secondaryCategory)
                                .textFieldStyle(.roundedBorder)
                        }
                    }
                }
                .padding()
            }

            Divider()

            // 하단 버튼
            HStack {
                Spacer()

                Button("저장") {
                    saveMetadata()
                    dismiss()
                }
                .keyboardShortcut(.defaultAction)
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
        .frame(width: 700, height: 700)
        .onAppear {
            loadMetadata()
        }
    }

    private func loadMetadata() {
        if let metadata = app.appStoreMetadata {
            descriptionKo = metadata.descriptionKo
            descriptionEn = metadata.descriptionEn
            keywords = metadata.keywords.joined(separator: ", ")
            promotionalText = metadata.promotionalText
            supportUrl = metadata.supportUrl ?? ""
            privacyUrl = metadata.privacyUrl ?? ""
            ageRating = metadata.ageRating ?? ""
            primaryCategory = metadata.primaryCategory ?? ""
            secondaryCategory = metadata.secondaryCategory ?? ""
        }
    }

    private func saveMetadata() {
        let keywordArray = keywords.split(separator: ",").map { $0.trimmingCharacters(in: .whitespaces) }

        let metadata = AppStoreMetadata(
            descriptionKo: descriptionKo,
            descriptionEn: descriptionEn,
            keywords: keywordArray,
            promotionalText: promotionalText,
            supportUrl: supportUrl.isEmpty ? nil : supportUrl,
            privacyUrl: privacyUrl.isEmpty ? nil : privacyUrl,
            ageRating: ageRating.isEmpty ? nil : ageRating,
            primaryCategory: primaryCategory.isEmpty ? nil : primaryCategory,
            secondaryCategory: secondaryCategory.isEmpty ? nil : secondaryCategory
        )

        portfolioService.updateAppStoreMetadata(appName: app.name, metadata: metadata)
    }
}

// MARK: - Screenshot Manager

struct ScreenshotManagerView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) var dismiss

    @State private var folderPath: String = ""
    @State private var devices: [DeviceScreenshot] = DeviceScreenshot.defaultDevices()

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                Text("스크린샷 관리")
                    .font(.headline)

                Spacer()

                Button("닫기") {
                    dismiss()
                }
            }
            .padding()

            Divider()

            // 입력 폼
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // 폴더 경로
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("스크린샷 폴더 경로")
                                .font(.subheadline)
                                .bold()

                            Spacer()

                            if !folderPath.isEmpty {
                                Button(action: openInFinder) {
                                    HStack(spacing: 4) {
                                        Image(systemName: "folder")
                                        Text("Finder에서 열기")
                                    }
                                    .font(.body)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
                                    .background(Color.blue.opacity(0.2))
                                    .foregroundColor(.blue)
                                    .cornerRadius(6)
                                }
                                .buttonStyle(.plain)
                            }
                        }

                        TextField("/Users/yourname/Screenshots", text: $folderPath)
                            .textFieldStyle(.roundedBorder)

                        Text("스크린샷이 저장된 폴더의 경로를 입력하세요")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    Divider()

                    // 디바이스별 체크리스트
                    VStack(alignment: .leading, spacing: 8) {
                        Text("디바이스별 스크린샷")
                            .font(.subheadline)
                            .bold()

                        ForEach($devices) { $device in
                            HStack {
                                Button(action: {
                                    device.isReady.toggle()
                                }) {
                                    Image(systemName: device.isReady ? "checkmark.circle.fill" : "circle")
                                        .font(.title3)
                                        .foregroundColor(device.isReady ? .green : .gray)
                                }
                                .buttonStyle(.plain)

                                Text(device.deviceType)
                                    .font(.body)

                                Spacer()

                                Stepper(value: $device.count, in: 0...10) {
                                    Text("\(device.count)개")
                                        .font(.body)
                                        .foregroundColor(.secondary)
                                }
                                .frame(width: 120)
                            }
                            .padding()
                            .background(device.isReady ? Color.green.opacity(0.05) : Color(NSColor.controlBackgroundColor))
                            .cornerRadius(8)
                        }

                        // 진행률
                        let readyCount = devices.filter { $0.isReady }.count
                        let totalCount = devices.count
                        let progress = Double(readyCount) / Double(totalCount)

                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text("\(readyCount)/\(totalCount) 완료")
                                    .font(.subheadline)
                                Spacer()
                                Text("\(Int(progress * 100))%")
                                    .font(.subheadline)
                                    .foregroundColor(progress >= 1.0 ? .green : .secondary)
                            }

                            ProgressView(value: progress)
                                .tint(progress >= 1.0 ? .green : .blue)
                        }
                        .padding(.top, 8)
                    }

                    if !folderPath.isEmpty {
                        Text("💡 Finder에서 폴더를 열어 스크린샷을 확인하세요")
                            .font(.body)
                            .foregroundColor(.blue)
                            .padding()
                            .background(Color.blue.opacity(0.1))
                            .cornerRadius(8)
                    }
                }
                .padding()
            }

            Divider()

            // 하단 버튼
            HStack {
                Spacer()

                Button("저장") {
                    saveScreenshotInfo()
                    dismiss()
                }
                .keyboardShortcut(.defaultAction)
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
        .frame(width: 600, height: 600)
        .onAppear {
            loadScreenshotInfo()
        }
    }

    private func loadScreenshotInfo() {
        if let screenshots = app.screenshots {
            folderPath = screenshots.folderPath ?? ""
            devices = screenshots.devices
        }
    }

    private func saveScreenshotInfo() {
        let info = ScreenshotInfo(folderPath: folderPath.isEmpty ? nil : folderPath, devices: devices)
        portfolioService.updateScreenshotInfo(appName: app.name, screenshots: info)
    }

    private func openInFinder() {
        let url = URL(fileURLWithPath: folderPath)
        NSWorkspace.shared.open(url)
    }
}

// MARK: - Deployment Reminder Editor

struct DeploymentReminderEditorView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) var dismiss

    @State private var enabled: Bool = false
    @State private var reminderDays: Int = 30
    @State private var updateCycle: UpdateCycle = .monthly
    @State private var hasLastDeploymentDate = false
    @State private var lastDeploymentDate: Date = Date()
    @State private var hasNextPlannedDate = false
    @State private var nextPlannedDate: Date = Date()

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                Text("배포 알림 설정")
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
                    Toggle("배포 알림 활성화", isOn: $enabled)
                        .font(.headline)

                    if enabled {
                        Divider()

                        // 알림 주기
                        VStack(alignment: .leading, spacing: 8) {
                            Text("알림 주기")
                                .font(.subheadline)
                                .bold()

                            HStack {
                                Stepper(value: $reminderDays, in: 1...365) {
                                    Text("\(reminderDays)일마다 알림")
                                        .font(.body)
                                }
                            }

                            Text("마지막 배포 이후 \(reminderDays)일이 지나면 알림이 표시됩니다")
                                .font(.body)
                                .foregroundColor(.secondary)
                        }

                        Divider()

                        // 업데이트 주기
                        VStack(alignment: .leading, spacing: 8) {
                            Text("업데이트 주기")
                                .font(.subheadline)
                                .bold()

                            Picker("", selection: $updateCycle) {
                                ForEach(UpdateCycle.allCases, id: \.self) { cycle in
                                    Text(cycle.rawValue)
                                        .tag(cycle)
                                }
                            }
                            .pickerStyle(.segmented)

                            if updateCycle != .adhoc {
                                Text("\(updateCycle.days)일 주기로 업데이트")
                                    .font(.body)
                                    .foregroundColor(.secondary)
                            } else {
                                Text("비정기 업데이트")
                                    .font(.body)
                                    .foregroundColor(.secondary)
                            }
                        }

                        Divider()

                        // 마지막 배포일
                        VStack(alignment: .leading, spacing: 8) {
                            Toggle("마지막 배포일 설정", isOn: $hasLastDeploymentDate)

                            if hasLastDeploymentDate {
                                DatePicker(
                                    "배포일",
                                    selection: $lastDeploymentDate,
                                    displayedComponents: .date
                                )
                                .datePickerStyle(.compact)

                                if let days = daysSince(lastDeploymentDate) {
                                    Text("\(days)일 전")
                                        .font(.body)
                                        .foregroundColor(days >= reminderDays ? .red : .secondary)
                                }
                            }
                        }

                        Divider()

                        // 다음 배포 예정일
                        VStack(alignment: .leading, spacing: 8) {
                            Toggle("다음 배포 예정일 설정", isOn: $hasNextPlannedDate)

                            if hasNextPlannedDate {
                                DatePicker(
                                    "예정일",
                                    selection: $nextPlannedDate,
                                    displayedComponents: .date
                                )
                                .datePickerStyle(.compact)

                                if let days = daysUntil(nextPlannedDate) {
                                    if days > 0 {
                                        Text("\(days)일 후")
                                            .font(.body)
                                            .foregroundColor(.blue)
                                    } else if days == 0 {
                                        Text("오늘")
                                            .font(.body)
                                            .foregroundColor(.orange)
                                    } else {
                                        Text("\(abs(days))일 지남")
                                            .font(.body)
                                            .foregroundColor(.red)
                                    }
                                }
                            }
                        }
                    }
                }
                .padding()
            }

            Divider()

            // 하단 버튼
            HStack {
                Spacer()

                Button("저장") {
                    saveReminder()
                    dismiss()
                }
                .keyboardShortcut(.defaultAction)
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
        .frame(width: 500, height: 600)
        .onAppear {
            loadReminder()
        }
    }

    private func loadReminder() {
        if let reminder = app.deploymentReminder {
            enabled = reminder.enabled
            reminderDays = reminder.reminderDays
            updateCycle = reminder.updateCycle

            if let date = reminder.lastDeploymentDate {
                hasLastDeploymentDate = true
                lastDeploymentDate = date
            }

            if let date = reminder.nextPlannedDate {
                hasNextPlannedDate = true
                nextPlannedDate = date
            }
        }
    }

    private func saveReminder() {
        let reminder = DeploymentReminder(
            enabled: enabled,
            reminderDays: reminderDays,
            lastDeploymentDate: hasLastDeploymentDate ? lastDeploymentDate : nil,
            nextPlannedDate: hasNextPlannedDate ? nextPlannedDate : nil,
            updateCycle: updateCycle
        )

        portfolioService.updateDeploymentReminder(appName: app.name, reminder: reminder)
    }

    private func daysSince(_ date: Date) -> Int? {
        let calendar = Calendar.current
        let components = calendar.dateComponents([.day], from: date, to: Date())
        return components.day
    }

    private func daysUntil(_ date: Date) -> Int? {
        let calendar = Calendar.current
        let components = calendar.dateComponents([.day], from: Date(), to: date)
        return components.day
    }
}

// MARK: - Build Automation Editor

struct BuildAutomationEditorView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) var dismiss

    @State private var buildNumber: Int = 1
    @State private var autoincrementEnabled: Bool = false
    @State private var xcodeProjectPath: String = ""
    @State private var buildScripts: [BuildScript] = []
    @State private var showingScriptEditor = false
    @State private var editingScript: BuildScript?

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                Text("빌드 자동화 설정")
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
                    // 빌드 번호
                    VStack(alignment: .leading, spacing: 8) {
                        Text("빌드 번호")
                            .font(.subheadline)
                            .bold()

                        HStack {
                            Stepper(value: $buildNumber, in: 1...99999) {
                                Text("\(buildNumber)")
                                    .font(.title3)
                                    .bold()
                            }
                        }

                        Text("현재 빌드 번호입니다")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    Divider()

                    // 자동 증가
                    VStack(alignment: .leading, spacing: 8) {
                        Toggle("빌드 번호 자동 증가", isOn: $autoincrementEnabled)
                            .font(.subheadline)
                            .bold()

                        Text("활성화하면 빌드할 때마다 빌드 번호가 자동으로 증가합니다")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    Divider()

                    // Xcode 프로젝트 경로
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Xcode 프로젝트 경로 (선택)")
                            .font(.subheadline)
                            .bold()

                        TextField("/path/to/Project.xcodeproj", text: $xcodeProjectPath)
                            .textFieldStyle(.roundedBorder)

                        Text("프로젝트 파일(.xcodeproj) 또는 워크스페이스(.xcworkspace) 경로")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    Divider()

                    // 빌드 스크립트
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("빌드 스크립트")
                                .font(.subheadline)
                                .bold()

                            Spacer()

                            Button(action: {
                                editingScript = nil
                                showingScriptEditor = true
                            }) {
                                HStack(spacing: 4) {
                                    Image(systemName: "plus.circle.fill")
                                    Text("추가")
                                }
                                .font(.body)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.blue.opacity(0.2))
                                .foregroundColor(.blue)
                                .cornerRadius(6)
                            }
                            .buttonStyle(.plain)
                        }

                        if buildScripts.isEmpty {
                            VStack(spacing: 12) {
                                Image(systemName: "doc.text")
                                    .font(.system(size: 32))
                                    .foregroundColor(.secondary)
                                Text("빌드 스크립트가 없습니다")
                                    .font(.body)
                                    .foregroundColor(.secondary)

                                Button(action: {
                                    buildScripts = BuildScript.defaultScripts()
                                }) {
                                    HStack(spacing: 4) {
                                        Image(systemName: "wand.and.stars")
                                        Text("기본 스크립트 추가")
                                    }
                                    .font(.body)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(Color.purple.opacity(0.2))
                                    .foregroundColor(.purple)
                                    .cornerRadius(6)
                                }
                                .buttonStyle(.plain)
                            }
                            .frame(maxWidth: .infinity)
                            .padding(20)
                            .background(Color(NSColor.controlBackgroundColor))
                            .cornerRadius(8)
                        } else {
                            VStack(spacing: 8) {
                                ForEach($buildScripts) { $script in
                                    HStack {
                                        Button(action: {
                                            script.enabled.toggle()
                                        }) {
                                            Image(systemName: script.enabled ? "checkmark.circle.fill" : "circle")
                                                .font(.title3)
                                                .foregroundColor(script.enabled ? .green : .gray)
                                        }
                                        .buttonStyle(.plain)

                                        VStack(alignment: .leading, spacing: 4) {
                                            Text(script.name)
                                                .font(.body)
                                            Text(script.phase.rawValue)
                                                .font(.body)
                                                .foregroundColor(.secondary)
                                        }

                                        Spacer()

                                        Button(action: {
                                            editingScript = script
                                            showingScriptEditor = true
                                        }) {
                                            Image(systemName: "pencil.circle.fill")
                                                .foregroundColor(.blue)
                                        }
                                        .buttonStyle(.plain)

                                        Button(action: {
                                            buildScripts.removeAll { $0.id == script.id }
                                        }) {
                                            Image(systemName: "trash.circle.fill")
                                                .foregroundColor(.red)
                                        }
                                        .buttonStyle(.plain)
                                    }
                                    .padding()
                                    .background(script.enabled ? Color.green.opacity(0.05) : Color(NSColor.controlBackgroundColor))
                                    .cornerRadius(8)
                                }
                            }
                        }
                    }
                }
                .padding()
            }

            Divider()

            // 하단 버튼
            HStack {
                Spacer()

                Button("저장") {
                    saveAutomation()
                    dismiss()
                }
                .keyboardShortcut(.defaultAction)
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
        .frame(width: 600, height: 700)
        .sheet(isPresented: $showingScriptEditor) {
            BuildScriptEditorView(
                script: editingScript,
                onSave: { script in
                    if let index = buildScripts.firstIndex(where: { $0.id == script.id }) {
                        buildScripts[index] = script
                    } else {
                        buildScripts.append(script)
                    }
                }
            )
        }
        .onAppear {
            loadAutomation()
        }
    }

    private func loadAutomation() {
        if let automation = app.buildAutomation {
            buildNumber = automation.buildNumber
            autoincrementEnabled = automation.autoincrementEnabled
            xcodeProjectPath = automation.xcodeProjectPath ?? ""
            buildScripts = automation.buildScripts
        }
    }

    private func saveAutomation() {
        let automation = BuildAutomation(
            buildNumber: buildNumber,
            autoincrementEnabled: autoincrementEnabled,
            xcodeProjectPath: xcodeProjectPath.isEmpty ? nil : xcodeProjectPath,
            buildScripts: buildScripts,
            lastBuildDate: app.buildAutomation?.lastBuildDate
        )

        portfolioService.updateBuildAutomation(appName: app.name, automation: automation)
    }
}

// MARK: - Build Script Editor

struct BuildScriptEditorView: View {
    let script: BuildScript?
    let onSave: (BuildScript) -> Void

    @Environment(\.dismiss) var dismiss

    @State private var name: String = ""
    @State private var scriptContent: String = ""
    @State private var phase: BuildPhase = .preBuild
    @State private var enabled: Bool = true

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                Text(script == nil ? "새 빌드 스크립트" : "빌드 스크립트 편집")
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
                        Text("스크립트 이름")
                            .font(.subheadline)
                            .bold()
                        TextField("예: 빌드 번호 자동 증가", text: $name)
                            .textFieldStyle(.roundedBorder)
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        Text("실행 단계")
                            .font(.subheadline)
                            .bold()
                        Picker("", selection: $phase) {
                            ForEach(BuildPhase.allCases, id: \.self) { phase in
                                Text(phase.rawValue)
                                    .tag(phase)
                            }
                        }
                        .pickerStyle(.segmented)

                        Text(phase.description)
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        Text("스크립트")
                            .font(.subheadline)
                            .bold()

                        TextEditor(text: $scriptContent)
                            .frame(minHeight: 200)
                            .font(.system(.body, design: .monospaced))
                            .padding(8)
                            .background(Color(NSColor.textBackgroundColor))
                            .cornerRadius(8)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                            )

                        Text("Bash 쉘 스크립트를 입력하세요")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    Toggle("활성화", isOn: $enabled)
                }
                .padding()
            }

            Divider()

            // 하단 버튼
            HStack {
                Spacer()

                Button("저장") {
                    let newScript = BuildScript(
                        id: script?.id ?? UUID().uuidString,
                        name: name,
                        script: scriptContent,
                        phase: phase,
                        enabled: enabled
                    )
                    onSave(newScript)
                    dismiss()
                }
                .keyboardShortcut(.defaultAction)
                .buttonStyle(.borderedProminent)
                .disabled(name.isEmpty || scriptContent.isEmpty)
            }
            .padding()
        }
        .frame(width: 600, height: 600)
        .onAppear {
            if let script = script {
                name = script.name
                scriptContent = script.script
                phase = script.phase
                enabled = script.enabled
            }
        }
    }
}
