import SwiftUI

struct DeploymentSectionView: View {
    let app: AppModel
    @State private var releaseNotes: String = ""
    @State private var targetVersion: String = ""
    @State private var checklistItems: [DeploymentChecklistItem] = []

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

                    Image(systemName: "arrow.right")
                        .foregroundColor(.secondary)

                    VStack(alignment: .leading, spacing: 4) {
                        Text("배포 버전")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        TextField("1.0.0", text: $targetVersion)
                            .textFieldStyle(.roundedBorder)
                            .frame(width: 100)
                    }
                }
                .padding()
                .background(Color.green.opacity(0.05))
                .cornerRadius(12)
            }

            Divider()

            // 릴리즈 노트
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("릴리즈 노트")
                        .font(.headline)
                    Spacer()
                    Button(action: saveReleaseNotes) {
                        HStack(spacing: 4) {
                            Image(systemName: "square.and.arrow.down.fill")
                            Text("저장")
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.green.opacity(0.2))
                        .foregroundColor(.green)
                        .cornerRadius(8)
                    }
                    .buttonStyle(.plain)
                    .disabled(releaseNotes.isEmpty || targetVersion.isEmpty)
                }

                TextEditor(text: $releaseNotes)
                    .frame(minHeight: 200)
                    .padding(8)
                    .background(Color(NSColor.textBackgroundColor))
                    .cornerRadius(8)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.green, lineWidth: 2)
                    )

                if releaseNotes.isEmpty {
                    Text("릴리즈 노트 작성 팁:\n• 새로운 기능\n• 개선 사항\n• 버그 수정\n• 알려진 이슈")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.horizontal, 8)
                }
            }

            Divider()

            // 배포 체크리스트
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("배포 체크리스트")
                        .font(.headline)

                    Spacer()

                    Text("\(checklistItems.filter { $0.isCompleted }.count)/\(checklistItems.count) 완료")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                if checklistItems.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "checklist")
                            .font(.system(size: 48))
                            .foregroundColor(.secondary)
                        Text("체크리스트가 없습니다")
                            .font(.headline)
                        Button(action: loadDefaultChecklist) {
                            HStack(spacing: 4) {
                                Image(systemName: "plus.circle.fill")
                                Text("기본 체크리스트 불러오기")
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
                } else {
                    VStack(spacing: 8) {
                        ForEach($checklistItems) { $item in
                            DeploymentChecklistRow(item: $item, onSave: saveChecklist)
                        }
                    }

                    // 진행률 바
                    let progress = Double(checklistItems.filter { $0.isCompleted }.count) / Double(max(checklistItems.count, 1))
                    VStack(alignment: .leading, spacing: 8) {
                        ProgressView(value: progress)
                            .tint(.green)
                        Text(progress >= 1.0 ? "배포 준비 완료!" : "배포 준비 중...")
                            .font(.caption)
                            .foregroundColor(progress >= 1.0 ? .green : .secondary)
                    }
                }
            }

            if !checklistItems.isEmpty && checklistItems.allSatisfy({ $0.isCompleted }) {
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
        }
        .onAppear {
            loadDeploymentData()
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

    private func loadDefaultChecklist() {
        checklistItems = [
            DeploymentChecklistItem(title: "모든 테스트 통과 확인", isCompleted: false),
            DeploymentChecklistItem(title: "버전 번호 업데이트", isCompleted: false),
            DeploymentChecklistItem(title: "릴리즈 노트 작성", isCompleted: false),
            DeploymentChecklistItem(title: "앱 아이콘 및 스크린샷 준비", isCompleted: false),
            DeploymentChecklistItem(title: "프로덕션 빌드 생성", isCompleted: false),
            DeploymentChecklistItem(title: "App Store Connect 메타데이터 업데이트", isCompleted: false),
            DeploymentChecklistItem(title: "심사 노트 작성", isCompleted: false),
            DeploymentChecklistItem(title: "최종 검토", isCompleted: false)
        ]
        saveChecklist()
    }

    private func loadDeploymentData() {
        let fileManager = FileManager.default
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let deploymentDir = documentsPath.appendingPathComponent("project-deployment")

        if !fileManager.fileExists(atPath: deploymentDir.path) {
            try? fileManager.createDirectory(at: deploymentDir, withIntermediateDirectories: true)
        }

        let folderName = app.name
            .lowercased()
            .replacingOccurrences(of: " ", with: "-")
        let filePath = deploymentDir.appendingPathComponent("\(folderName).json")

        guard let data = try? Data(contentsOf: filePath) else { return }

        let decoder = JSONDecoder()
        if let loaded = try? decoder.decode(DeploymentData.self, from: data) {
            releaseNotes = loaded.releaseNotes
            targetVersion = loaded.targetVersion
            checklistItems = loaded.checklistItems
        }
    }

    private func saveReleaseNotes() {
        saveDeploymentData()
    }

    private func saveChecklist() {
        saveDeploymentData()
    }

    private func saveDeploymentData() {
        let fileManager = FileManager.default
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let deploymentDir = documentsPath.appendingPathComponent("project-deployment")

        let folderName = app.name
            .lowercased()
            .replacingOccurrences(of: " ", with: "-")
        let filePath = deploymentDir.appendingPathComponent("\(folderName).json")

        let deploymentData = DeploymentData(
            releaseNotes: releaseNotes,
            targetVersion: targetVersion,
            checklistItems: checklistItems
        )

        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]

        guard let data = try? encoder.encode(deploymentData) else { return }
        try? data.write(to: filePath, options: .atomic)
    }
}

// MARK: - Deployment Checklist Row

struct DeploymentChecklistRow: View {
    @Binding var item: DeploymentChecklistItem
    let onSave: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Button(action: {
                item.isCompleted.toggle()
                if item.isCompleted {
                    item.completedAt = Date()
                } else {
                    item.completedAt = nil
                }
                onSave()
            }) {
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

// MARK: - Models

struct DeploymentData: Codable {
    var releaseNotes: String
    var targetVersion: String
    var checklistItems: [DeploymentChecklistItem]
}

struct DeploymentChecklistItem: Identifiable, Codable {
    let id: String
    var title: String
    var isCompleted: Bool
    var completedAt: Date?

    init(id: String = UUID().uuidString, title: String, isCompleted: Bool, completedAt: Date? = nil) {
        self.id = id
        self.title = title
        self.isCompleted = isCompleted
        self.completedAt = completedAt
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
