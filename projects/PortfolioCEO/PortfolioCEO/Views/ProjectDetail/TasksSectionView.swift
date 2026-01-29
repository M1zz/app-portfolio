import SwiftUI

enum TaskViewMode: String, CaseIterable {
    case list = "목록"
    case kanban = "칸반"

    var icon: String {
        switch self {
        case .list: return "list.bullet"
        case .kanban: return "rectangle.split.3x1"
        }
    }
}

struct TasksSectionView: View {
    let app: AppModel
    @State private var showCompletedTasks = false
    @State private var showArchivedTasks = false  // 지난 완료 표시 여부
    @State private var viewMode: TaskViewMode = .list

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            // 헤더
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Image(systemName: "checklist")
                        .font(.title2)
                        .foregroundColor(.purple)
                    Text("태스크")
                        .font(.title2)
                        .bold()

                    Spacer()

                    // 뷰 모드 선택
                    Picker("", selection: $viewMode) {
                        ForEach(TaskViewMode.allCases, id: \.self) { mode in
                            Label(mode.rawValue, systemImage: mode.icon)
                                .tag(mode)
                        }
                    }
                    .pickerStyle(.segmented)
                    .frame(width: 150)
                }
                Text("프로젝트 작업을 관리하고 진행 상황을 추적합니다")
                    .font(.body)
                    .foregroundColor(.secondary)
            }

            Divider()

            // 태스크 통계
            HStack(spacing: 12) {
                // 완료 / 전체
                VStack(spacing: 4) {
                    Text("진행률")
                        .font(.body)
                        .foregroundColor(.secondary)
                    HStack(alignment: .firstTextBaseline, spacing: 4) {
                        Text("\(app.stats.done)")
                            .font(.system(size: 28, weight: .bold))
                            .foregroundColor(.green)
                        Text("/")
                            .font(.title3)
                            .foregroundColor(.secondary)
                        Text("\(app.stats.totalTasks)")
                            .font(.title3)
                            .foregroundColor(.secondary)
                    }
                    Text("\(Int(Double(app.stats.done) / Double(max(app.stats.totalTasks, 1)) * 100))%")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.green.opacity(0.1))
                .cornerRadius(12)

                TaskStatCard(
                    title: "진행전",
                    count: app.stats.notStarted,
                    color: .blue
                )
                TaskStatCard(
                    title: "진행중",
                    count: app.stats.inProgress,
                    color: .orange
                )
                TaskStatCard(
                    title: "완료",
                    count: app.stats.done,
                    color: .green
                )
            }

            Divider()

            // 태스크 목록 헤더 (목록 모드일 때만)
            if viewMode == .list {
                HStack {
                    Text(showCompletedTasks ? "전체 태스크" : "진행 중 태스크")
                        .font(.headline)

                    Spacer()

                    // 이전 완료 토글 (완료 표시 중이고 이전 완료가 있을 때만)
                    if showCompletedTasks && app.previousDoneCount > 0 {
                        Button(action: {
                            showArchivedTasks.toggle()
                        }) {
                            HStack(spacing: 4) {
                                Image(systemName: showArchivedTasks ? "clock.arrow.circlepath" : "clock")
                                Text(showArchivedTasks ? "이전완료 숨기기" : "이전완료 (\(app.previousDoneCount))")
                            }
                            .font(.body)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(Color.secondary.opacity(0.2))
                            .foregroundColor(.secondary)
                            .cornerRadius(8)
                        }
                        .buttonStyle(.plain)
                    }

                    Button(action: {
                        showCompletedTasks.toggle()
                        if !showCompletedTasks {
                            showArchivedTasks = false
                        }
                    }) {
                        HStack(spacing: 4) {
                            Image(systemName: showCompletedTasks ? "eye.slash" : "eye")
                            Text(showCompletedTasks ? "완료 숨기기" : "완료 보기 (\(app.stats.done))")
                        }
                        .font(.body)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.green.opacity(0.2))
                        .foregroundColor(.green)
                        .cornerRadius(8)
                    }
                    .buttonStyle(.plain)
                }
            }

            // 뷰 모드에 따라 다른 표시
            if viewMode == .kanban {
                // 칸반 뷰
                AppKanbanView(app: app)
                    .frame(minHeight: 400)
            } else {
                // 목록 뷰
                if activeTasks.isEmpty && completedTasks.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "list.bullet.clipboard")
                            .font(.system(size: 48))
                            .foregroundColor(.secondary)
                        Text("태스크가 없습니다")
                            .font(.headline)
                        Text("태스크는 프로젝트 JSON 파일에서 관리됩니다")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(40)
                } else {
                    VStack(alignment: .leading, spacing: 12) {
                        // 진행 중 태스크
                        if !activeTasks.isEmpty {
                            ForEach(activeTasks) { task in
                                TaskRowView(task: task)
                            }
                        }

                        // 완료된 태스크 (토글로 표시/숨김)
                        if showCompletedTasks {
                            // 이번 빌드 완료 (v{currentVersion})
                            if !app.currentBuildDoneTasks.isEmpty {
                                Divider()
                                    .padding(.vertical, 8)

                                HStack {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundColor(.green)
                                    Text("이번 빌드 완료 - v\(app.currentVersion) (\(app.currentBuildDoneCount))")
                                        .font(.subheadline)
                                        .foregroundColor(.green)
                                }

                                ForEach(app.currentBuildDoneTasks) { task in
                                    TaskRowView(task: task)
                                        .opacity(0.7)
                                }
                            }

                            // 이전 버전 완료 (토글 활성화 시)
                            if showArchivedTasks && !app.previousDoneTasks.isEmpty {
                                Divider()
                                    .padding(.vertical, 8)

                                HStack {
                                    Image(systemName: "clock")
                                        .foregroundColor(.secondary)
                                    Text("이전 버전 완료 (\(app.previousDoneCount)) - 카운트 제외")
                                        .font(.subheadline)
                                        .foregroundColor(.secondary)
                                }

                                ForEach(app.previousDoneTasks) { task in
                                    HStack {
                                        TaskRowView(task: task)
                                        if let ver = task.targetVersion {
                                            Text("v\(ver)")
                                                .font(.caption)
                                                .foregroundColor(.secondary)
                                                .padding(.horizontal, 6)
                                                .padding(.vertical, 2)
                                                .background(Color.secondary.opacity(0.2))
                                                .cornerRadius(4)
                                        }
                                    }
                                    .opacity(0.4)
                                }
                            }
                        }

                        // 진행 중 태스크가 없을 때
                        if activeTasks.isEmpty && !showCompletedTasks {
                            VStack(spacing: 12) {
                                Image(systemName: "checkmark.circle.fill")
                                    .font(.system(size: 40))
                                    .foregroundColor(.green)
                                Text("모든 태스크를 완료했습니다!")
                                    .font(.headline)
                                Text("완료된 태스크를 보려면 '완료 보기' 버튼을 누르세요")
                                    .font(.body)
                                    .foregroundColor(.secondary)
                            }
                            .frame(maxWidth: .infinity)
                            .padding(40)
                        }
                    }
                }
            }
        }
    }

    private var activeTasks: [AppTask] {
        app.allTasks.filter { $0.status != .done }
    }

    private var completedTasks: [AppTask] {
        app.allTasks.filter { $0.status == .done }
    }
}

struct TaskStatCard: View {
    let title: String
    let count: Int
    let color: Color
    var subtitle: String? = nil

    var body: some View {
        VStack(spacing: 4) {
            Text(title)
                .font(.body)
                .foregroundColor(.secondary)
            Text("\(count)")
                .font(.system(size: 28, weight: .bold))
                .foregroundColor(color)
            if let subtitle = subtitle {
                Text(subtitle)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(12)
    }
}

struct TaskRowView: View {
    let task: AppTask
    @State private var isExpanded = false
    @State private var showingCommitSheet = false
    @State private var hasBranchStartLabel = false
    @State private var targetVersion: String = ""
    @State private var showingVersionSheet = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // 메인 행
            HStack {
                VStack(alignment: .leading, spacing: 8) {
                    HStack(spacing: 8) {
                        Text(task.name)
                            .font(.body)

                        // 브랜치 시작 라벨 표시
                        if let labels = task.labels, labels.contains("브랜치 시작") {
                            HStack(spacing: 4) {
                                Image(systemName: "arrow.triangle.branch")
                                    .font(.body)
                                Text("브랜치 시작")
                                    .font(.body)
                            }
                            .padding(.horizontal, 6)
                            .padding(.vertical, 3)
                            .background(Color.purple.opacity(0.2))
                            .foregroundColor(.purple)
                            .cornerRadius(4)
                        }
                    }

                    HStack(spacing: 12) {
                        if let targetDate = task.targetDate {
                            Label(targetDate, systemImage: "calendar")
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                        if let targetVersion = task.targetVersion {
                            Label("v\(targetVersion)", systemImage: "number.circle")
                                .font(.body)
                                .foregroundColor(.secondary)
                        }

                        // 기타 라벨들 표시
                        if let labels = task.labels {
                            ForEach(labels.filter { $0 != "브랜치 시작" }, id: \.self) { label in
                                Text(label)
                                    .font(.body)
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(Color.gray.opacity(0.2))
                                    .foregroundColor(.gray)
                                    .cornerRadius(4)
                            }
                        }
                    }
                }

                Spacer()

                // 확장 버튼
                if task.status != .done {
                    Button(action: {
                        isExpanded.toggle()
                    }) {
                        Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                            .foregroundColor(.secondary)
                    }
                    .buttonStyle(.plain)
                }

                // 상태 배지
                HStack(spacing: 4) {
                    Image(systemName: task.status.icon)
                    Text(task.status.displayName)
                        .font(.body)
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(task.status.color.opacity(0.2))
                .foregroundColor(task.status.color)
                .cornerRadius(6)
            }
            .padding()

            // 확장 영역 (액션 버튼들)
            if isExpanded {
                Divider()

                VStack(spacing: 12) {
                    // 브랜치 시작 토글
                    Toggle(isOn: $hasBranchStartLabel) {
                        HStack(spacing: 8) {
                            Image(systemName: "arrow.triangle.branch")
                                .foregroundColor(.purple)
                            Text("브랜치 시작")
                                .font(.body)
                        }
                    }
                    .toggleStyle(.switch)
                    .padding()
                    .background(Color.purple.opacity(0.1))
                    .cornerRadius(8)
                    .onChange(of: hasBranchStartLabel) { _, newValue in
                        updateBranchStartLabel(enabled: newValue)
                    }

                    // 버전 설정 버튼
                    Button(action: {
                        showingVersionSheet = true
                    }) {
                        HStack(spacing: 4) {
                            Image(systemName: "number.circle")
                            Text(targetVersion.isEmpty ? "배포 버전 설정" : "배포 버전: v\(targetVersion)")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 8)
                        .background(Color.blue.opacity(0.1))
                        .foregroundColor(.blue)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)

                    // 커밋 버튼
                    Button(action: {
                        showingCommitSheet = true
                    }) {
                        HStack(spacing: 4) {
                            Image(systemName: "checkmark.circle")
                            Text("작업 완료 & 커밋")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 8)
                        .background(Color.green.opacity(0.1))
                        .foregroundColor(.green)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)
                }
                .padding()
            }
        }
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(8)
        .sheet(isPresented: $showingCommitSheet) {
            TaskCommitSheet(task: task)
        }
        .sheet(isPresented: $showingVersionSheet) {
            TaskVersionSheet(task: task, currentVersion: $targetVersion, onSave: { newVersion in
                updateTaskVersion(version: newVersion)
            })
        }
        .onAppear {
            // 현재 라벨 상태 로드
            hasBranchStartLabel = task.labels?.contains("브랜치 시작") ?? false
            targetVersion = task.targetVersion ?? ""
        }
    }

    private func updateBranchStartLabel(enabled: Bool) {
        var updatedLabels: [String] = task.labels?.filter { $0 != "브랜치 시작" } ?? []
        if enabled {
            updatedLabels.append("브랜치 시작")
        }

        // JSON 파일 업데이트
        updateTaskLabels(taskName: task.name, labels: updatedLabels.isEmpty ? nil : updatedLabels)
    }

    private func updateTaskVersion(version: String) {
        let versionToSave = version.isEmpty ? nil : version
        updateTaskField(taskName: task.name, field: "targetVersion", value: versionToSave)
        targetVersion = version
    }

    private func updateTaskField(taskName: String, field: String, value: Any?) {
        let fileManager = FileManager.default
        let home = fileManager.homeDirectoryForCurrentUser
        let appsDir = home.appendingPathComponent("Documents/code/app-portfolio/apps")

        guard let files = try? fileManager.contentsOfDirectory(at: appsDir, includingPropertiesForKeys: nil) else {
            print("❌ [TaskRowView] apps 디렉토리를 읽을 수 없습니다")
            return
        }

        for file in files where file.pathExtension == "json" {
            guard let data = try? Data(contentsOf: file),
                  var json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                continue
            }

            guard var allTasks = json["allTasks"] as? [[String: Any]] else {
                continue
            }

            var found = false
            for (index, var task) in allTasks.enumerated() {
                if let name = task["name"] as? String, name == taskName {
                    if let value = value {
                        task[field] = value
                    } else {
                        task.removeValue(forKey: field)
                    }
                    allTasks[index] = task
                    found = true
                    break
                }
            }

            if found {
                json["allTasks"] = allTasks

                if let updatedData = try? JSONSerialization.data(withJSONObject: json, options: .prettyPrinted) {
                    try? updatedData.write(to: file)
                    print("✅ [TaskRowView] \(field) 업데이트: \(taskName)")
                }
                break
            }
        }
    }

    private func updateTaskLabels(taskName: String, labels: [String]?) {
        let fileManager = FileManager.default
        let home = fileManager.homeDirectoryForCurrentUser
        let appsDir = home.appendingPathComponent("Documents/code/app-portfolio/apps")

        // 모든 JSON 파일 검색
        guard let files = try? fileManager.contentsOfDirectory(at: appsDir, includingPropertiesForKeys: nil) else {
            print("❌ [TaskRowView] apps 디렉토리를 읽을 수 없습니다")
            return
        }

        for file in files where file.pathExtension == "json" {
            guard let data = try? Data(contentsOf: file),
                  var json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                continue
            }

            guard var allTasks = json["allTasks"] as? [[String: Any]] else {
                continue
            }

            // 태스크 찾기 및 업데이트
            var found = false
            for (index, var task) in allTasks.enumerated() {
                if let name = task["name"] as? String, name == taskName {
                    if let labels = labels {
                        task["labels"] = labels
                    } else {
                        task.removeValue(forKey: "labels")
                    }
                    allTasks[index] = task
                    found = true
                    break
                }
            }

            if found {
                json["allTasks"] = allTasks

                // 저장
                if let updatedData = try? JSONSerialization.data(withJSONObject: json, options: .prettyPrinted) {
                    try? updatedData.write(to: file)
                    print("✅ [TaskRowView] 브랜치 시작 라벨 업데이트: \(taskName) = \(labels != nil && labels!.contains("브랜치 시작"))")
                }
                break
            }
        }
    }
}

// MARK: - Task Version Sheet

struct TaskVersionSheet: View {
    let task: AppTask
    @Binding var currentVersion: String
    let onSave: (String) -> Void
    @Environment(\.dismiss) var dismiss
    @State private var versionInput: String = ""

    var body: some View {
        VStack(spacing: 20) {
            // 헤더
            VStack(spacing: 8) {
                Text("배포 버전 설정")
                    .font(.title2)
                    .bold()

                Text(task.name)
                    .font(.headline)
                    .foregroundColor(.secondary)
            }

            Divider()

            // 버전 입력
            VStack(alignment: .leading, spacing: 12) {
                Text("이 태스크가 포함될 배포 버전을 입력하세요")
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                HStack(spacing: 8) {
                    Text("v")
                        .font(.body)
                        .foregroundColor(.secondary)

                    TextField("예: 1.1.0", text: $versionInput)
                        .textFieldStyle(.roundedBorder)
                        .font(.body)
                }

                Text("버전을 설정하면 배포 탭에서 버전별로 태스크를 그룹화해서 볼 수 있습니다")
                    .font(.body)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color.blue.opacity(0.05))
            .cornerRadius(8)

            Spacer()

            // 액션 버튼
            HStack(spacing: 12) {
                Button("취소") {
                    dismiss()
                }
                .keyboardShortcut(.escape)

                Button(versionInput.isEmpty ? "버전 제거" : "저장") {
                    onSave(versionInput)
                    dismiss()
                }
                .keyboardShortcut(.return)
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(24)
        .frame(width: 500, height: 350)
        .onAppear {
            versionInput = currentVersion
        }
    }
}

// MARK: - Task Commit Sheet

struct TaskCommitSheet: View {
    let task: AppTask
    @Environment(\.dismiss) var dismiss
    @State private var commitMessage: String = ""
    @State private var isCommitting = false

    var body: some View {
        VStack(spacing: 20) {
            // 헤더
            VStack(spacing: 8) {
                Text("작업 완료 & 커밋")
                    .font(.title2)
                    .bold()

                Text(task.name)
                    .font(.headline)
                    .foregroundColor(.secondary)
            }

            Divider()

            // 커밋 메시지 입력
            VStack(alignment: .leading, spacing: 8) {
                Text("커밋 메시지")
                    .font(.headline)

                TextEditor(text: $commitMessage)
                    .frame(height: 100)
                    .padding(8)
                    .background(Color(NSColor.textBackgroundColor))
                    .cornerRadius(8)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.blue, lineWidth: 1)
                    )

                Text("변경사항을 커밋하고 태스크를 완료 처리합니다")
                    .font(.body)
                    .foregroundColor(.secondary)
            }

            Spacer()

            // 액션 버튼
            HStack(spacing: 12) {
                Button("취소") {
                    dismiss()
                }
                .keyboardShortcut(.escape)

                Button(isCommitting ? "커밋 중..." : "커밋하기") {
                    commitChanges()
                }
                .keyboardShortcut(.return)
                .buttonStyle(.borderedProminent)
                .disabled(commitMessage.isEmpty || isCommitting)
            }
        }
        .padding(24)
        .frame(width: 500, height: 350)
        .onAppear {
            // 기본 커밋 메시지 설정
            commitMessage = "feat: \(task.name)\n\nCo-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
        }
    }

    private func commitChanges() {
        isCommitting = true

        // git add 및 commit 실행
        let script = """
        tell application "Terminal"
            activate
            do script "echo '📝 작업 커밋 중...' && git add . && git commit -m \"\(commitMessage.replacingOccurrences(of: "\"", with: "\\\""))\" && echo '✅ 커밋 완료!'"
        end tell
        """

        if let appleScript = NSAppleScript(source: script) {
            var error: NSDictionary?
            appleScript.executeAndReturnError(&error)

            if let error = error {
                print("❌ 커밋 실패: \(error)")
                isCommitting = false
            } else {
                print("✅ 커밋 성공: \(task.name)")

                // 잠시 후 시트 닫기
                DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                    isCommitting = false
                    dismiss()
                }
            }
        }
    }
}

// TaskStatus extension for icon
extension TaskStatus {
    var icon: String {
        switch self {
        case .done: return "checkmark.circle.fill"
        case .inProgress: return "arrow.clockwise.circle.fill"
        case .todo: return "circle.dashed"
        case .notStarted: return "circle"
        }
    }
}
