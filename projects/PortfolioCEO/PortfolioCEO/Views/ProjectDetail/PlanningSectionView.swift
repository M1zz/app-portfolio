import SwiftUI

struct PlanningSectionView: View {
    let app: AppModel
    @EnvironmentObject var decisionQueueService: DecisionQueueService
    @EnvironmentObject var portfolioService: PortfolioService
    @State private var suggestions: [PlanningFeature] = []
    @State private var decisions: [PlanningDecisionRecord] = []
    @State private var planningDocuments: [PlanningDocument] = []
    @State private var expandedDecisions: Set<String> = []
    @State private var selectedOptions: [String: String] = [:]

    // 해당 앱의 의사결정들만 필터링
    var appPendingDecisions: [PlanningDecision] {
        decisionQueueService.pendingDecisions.filter { decision in
            decision.app == app.name
        }
    }

    var appCompletedDecisions: [PlanningDecision] {
        decisionQueueService.completedDecisions.filter { decision in
            decision.app == app.name
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            // 헤더
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Image(systemName: "lightbulb.fill")
                        .font(.title2)
                        .foregroundColor(.yellow)
                    Text("기획 및 의사결정")
                        .font(.title2)
                        .bold()

                    Spacer()

                    if !appPendingDecisions.isEmpty {
                        Text("\(appPendingDecisions.count)개 대기 중")
                            .font(.body)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.orange.opacity(0.2))
                            .foregroundColor(.orange)
                            .cornerRadius(6)
                    }
                }
                Text("AI 기능 제안을 검토하고 의사결정을 내립니다")
                    .font(.body)
                    .foregroundColor(.secondary)
            }

            Divider()

            // 의사결정 대기 중
            if !appPendingDecisions.isEmpty {
                VStack(alignment: .leading, spacing: 16) {
                    HStack {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundColor(.orange)
                        Text("의사결정 대기 중")
                            .font(.headline)

                        Spacer()

                        Button(action: {
                            decisionQueueService.loadQueue()
                        }) {
                            HStack(spacing: 4) {
                                Image(systemName: "arrow.clockwise")
                                Text("새로고침")
                            }
                            .font(.body)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.gray.opacity(0.2))
                            .cornerRadius(6)
                        }
                        .buttonStyle(.plain)
                    }

                    ForEach(appPendingDecisions) { decision in
                        AppDecisionCard(
                            decision: decision,
                            isExpanded: expandedDecisions.contains(decision.id),
                            selectedOption: selectedOptions[decision.id],
                            onToggleExpand: {
                                toggleExpansion(for: decision.id)
                            },
                            onSelectOption: { optionId in
                                selectedOptions[decision.id] = optionId
                            },
                            onApprove: {
                                if let selectedOption = selectedOptions[decision.id] {
                                    decisionQueueService.approveDecision(id: decision.id, selectedOption: selectedOption)
                                    selectedOptions.removeValue(forKey: decision.id)
                                    expandedDecisions.remove(decision.id)
                                }
                            },
                            onDelete: {
                                decisionQueueService.deleteDecision(id: decision.id)
                                selectedOptions.removeValue(forKey: decision.id)
                                expandedDecisions.remove(decision.id)
                            }
                        )
                    }
                }

                Divider()
            }

            // 의사결정 히스토리
            if !appCompletedDecisions.isEmpty {
                VStack(alignment: .leading, spacing: 16) {
                    HStack {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                        Text("의사결정 히스토리")
                            .font(.headline)

                        Spacer()

                        Text("\(appCompletedDecisions.count)개 완료")
                            .font(.body)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.green.opacity(0.2))
                            .foregroundColor(.green)
                            .cornerRadius(6)
                    }

                    ForEach(appCompletedDecisions) { decision in
                        CompletedDecisionHistoryCard(
                            decision: decision,
                            onRevert: {
                                decisionQueueService.rejectDecision(id: decision.id)
                            },
                            onCreateTasks: {
                                createTasksFromDecision(decision)
                            }
                        )
                    }
                }

                Divider()
            }

            // 기획서 목록
            VStack(alignment: .leading, spacing: 16) {
                HStack {
                    Text("생성된 기획서")
                        .font(.headline)

                    Spacer()

                    Button(action: generateAIPlanningDocument) {
                        HStack(spacing: 4) {
                            Image(systemName: "sparkles")
                            Text("AI 기획서 생성")
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.purple.opacity(0.2))
                        .foregroundColor(.purple)
                        .cornerRadius(8)
                    }
                    .buttonStyle(.plain)
                }

                if planningDocuments.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "doc.text")
                            .font(.system(size: 48))
                            .foregroundColor(.secondary)
                        Text("아직 기획서가 없습니다")
                            .font(.headline)
                        Text("AI 기획서 생성 버튼을 눌러 피드백 기반 기획서를 만드세요")
                            .font(.body)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(40)
                } else {
                    ForEach(planningDocuments) { doc in
                        GeneratedDocumentCard(document: doc)
                    }
                }
            }

            Divider()

            // 기능 제안 목록
            VStack(alignment: .leading, spacing: 16) {
                HStack {
                    Text("기능 제안")
                        .font(.headline)
                    Spacer()
                    Button(action: generateSuggestions) {
                        HStack(spacing: 4) {
                            Image(systemName: "sparkles")
                            Text("AI 제안 생성")
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.yellow.opacity(0.2))
                        .foregroundColor(.yellow)
                        .cornerRadius(8)
                    }
                    .buttonStyle(.plain)
                }

                if suggestions.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "lightbulb.slash")
                            .font(.system(size: 48))
                            .foregroundColor(.secondary)
                        Text("아직 기능 제안이 없습니다")
                            .font(.headline)
                        Text("AI 제안 생성 버튼을 눌러 기능을 제안받으세요")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(40)
                } else {
                    ForEach($suggestions) { $suggestion in
                        PlanningFeatureCard(
                            suggestion: $suggestion,
                            onApprove: {
                                approveSuggestion(suggestion)
                            },
                            onReject: {
                                rejectSuggestion(suggestion)
                            }
                        )
                    }
                }
            }

            if !decisions.isEmpty {
                Divider()

                // 의사결정 기록
                VStack(alignment: .leading, spacing: 12) {
                    Text("의사결정 기록")
                        .font(.headline)

                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 12) {
                            ForEach(decisions) { decision in
                                DecisionRecordCard(decision: decision)
                            }
                        }
                    }
                }
            }
        }
        .onAppear {
            loadSuggestions()
            loadPlanningDocuments()
            decisionQueueService.loadQueue()
        }
    }

    private func toggleExpansion(for id: String) {
        if expandedDecisions.contains(id) {
            expandedDecisions.remove(id)
        } else {
            expandedDecisions.insert(id)
        }
    }

    private func generateSuggestions() {
        // 피드백 메모 로드
        let notes = loadNotes()

        if notes.isEmpty {
            // 피드백이 없으면 기본 제안 생성
            let newSuggestions = [
                PlanningFeature(
                    title: "다크 모드 지원",
                    description: "사용자가 다크 모드를 켜고 끌 수 있는 기능을 추가합니다",
                    priority: "높음",
                    status: .pending
                ),
                PlanningFeature(
                    title: "위젯 추가",
                    description: "홈 화면에서 바로 확인할 수 있는 위젯을 제공합니다",
                    priority: "높음",
                    status: .pending
                ),
                PlanningFeature(
                    title: "검색 기능 개선",
                    description: "더 빠르고 정확한 검색 알고리즘을 적용합니다",
                    priority: "중간",
                    status: .pending
                )
            ]
            suggestions.append(contentsOf: newSuggestions)
        } else {
            // AI 분석 서비스를 사용하여 피드백 기반 제안 생성
            let newSuggestions = AIAnalysisService.shared.generateFeatureSuggestionsFromFeedback(
                appName: app.name,
                notes: notes
            )
            suggestions.append(contentsOf: newSuggestions)
        }

        saveSuggestions()
    }

    private func approveSuggestion(_ suggestion: PlanningFeature) {
        let decision = PlanningDecisionRecord(
            type: .approve,
            content: suggestion.title
        )
        decisions.append(decision)
        saveSuggestions()
        saveDecisions()
    }

    private func rejectSuggestion(_ suggestion: PlanningFeature) {
        let decision = PlanningDecisionRecord(
            type: .reject,
            content: suggestion.title
        )
        decisions.append(decision)
        saveSuggestions()
        saveDecisions()
    }

    private func loadSuggestions() {
        let planningDir = portfolioService.planningDirectory
        let folderName = portfolioService.getFolderName(for: app.name)
        let suggestionsPath = planningDir.appendingPathComponent("\(folderName)-suggestions.json")
        let decisionsPath = planningDir.appendingPathComponent("\(folderName)-decisions.json")

        print("📥 [PlanningSection] 제안 로드 시도: \(suggestionsPath.path)")

        // 제안 로드
        if let data = try? Data(contentsOf: suggestionsPath) {
            let decoder = JSONDecoder()
            if let loaded = try? decoder.decode([PlanningFeature].self, from: data) {
                suggestions = loaded
                print("✅ [PlanningSection] \(loaded.count)개 제안 로드 완료")
            }
        }

        // 의사결정 로드
        if let data = try? Data(contentsOf: decisionsPath) {
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            if let loaded = try? decoder.decode([PlanningDecisionRecord].self, from: data) {
                decisions = loaded
            }
        }
    }

    private func saveSuggestions() {
        let planningDir = portfolioService.planningDirectory
        let folderName = portfolioService.getFolderName(for: app.name)
        let filePath = planningDir.appendingPathComponent("\(folderName)-suggestions.json")

        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]

        guard let data = try? encoder.encode(suggestions) else { return }
        try? data.write(to: filePath, options: .atomic)
        print("✅ [PlanningSection] 제안 저장 완료: \(filePath.path)")
    }

    private func saveDecisions() {
        let planningDir = portfolioService.planningDirectory
        let folderName = portfolioService.getFolderName(for: app.name)
        let filePath = planningDir.appendingPathComponent("\(folderName)-decisions.json")

        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601

        guard let data = try? encoder.encode(decisions) else { return }
        try? data.write(to: filePath, options: .atomic)
    }

    private func loadNotes() -> [ProjectNote] {
        let notesDir = portfolioService.projectNotesDirectory
        let folderName = portfolioService.getFolderName(for: app.name)
        let filePath = notesDir.appendingPathComponent("\(folderName).json")

        print("📥 [PlanningSection] 노트 로드 시도: \(filePath.path)")

        guard let data = try? Data(contentsOf: filePath) else { return [] }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        if let loaded = try? decoder.decode([ProjectNote].self, from: data) {
            return loaded
        }

        return []
    }

    private func loadPlanningDocuments() {
        let fileManager = FileManager.default
        let home = fileManager.homeDirectoryForCurrentUser
        let planningDocsDir = home.appendingPathComponent("Documents/planning-documents")

        guard fileManager.fileExists(atPath: planningDocsDir.path) else { return }

        do {
            let files = try fileManager.contentsOfDirectory(
                at: planningDocsDir,
                includingPropertiesForKeys: [.contentModificationDateKey],
                options: .skipsHiddenFiles
            )

            let appFolderName = portfolioService.getFolderName(for: app.name)
            let matchingFiles = files.filter { file in
                let filename = file.lastPathComponent
                return filename.hasSuffix(".md") &&
                       (filename.contains(app.name) || filename.contains(appFolderName))
            }

            planningDocuments = matchingFiles.compactMap { fileURL in
                guard let content = try? String(contentsOf: fileURL, encoding: .utf8),
                      let attributes = try? fileManager.attributesOfItem(atPath: fileURL.path),
                      let modificationDate = attributes[.modificationDate] as? Date else {
                    return nil
                }

                // 파일 이름에서 제목 추출
                let filename = fileURL.deletingPathExtension().lastPathComponent
                let title = extractTitle(from: content) ?? filename

                return PlanningDocument(
                    id: fileURL.path,
                    title: title,
                    filePath: fileURL.path,
                    createdAt: modificationDate
                )
            }.sorted { $0.createdAt > $1.createdAt }

            print("📄 [PlanningSectionView] 기획서 \(planningDocuments.count)개 로드 완료")

        } catch {
            print("❌ [PlanningSectionView] 기획서 로드 실패: \(error)")
        }
    }

    private func extractTitle(from markdown: String) -> String? {
        // 첫 번째 # 제목을 찾음
        let lines = markdown.components(separatedBy: .newlines)
        for line in lines {
            if line.hasPrefix("#") {
                return line.replacingOccurrences(of: "#", with: "").trimmingCharacters(in: .whitespaces)
            }
        }
        return nil
    }

    private func generateAIPlanningDocument() {
        // 피드백 로드
        let notes = loadNotes()

        if notes.isEmpty {
            print("⚠️ [PlanningSectionView] 피드백이 없어 기획서를 생성할 수 없습니다")
            return
        }

        // 피드백 내용 정리
        let feedbackContent = notes.map { "- \($0.content)" }.joined(separator: "\n")

        let appFolder = portfolioService.getFolderName(for: app.name)
        let fileManager = FileManager.default
        let home = fileManager.homeDirectoryForCurrentUser
        let planningDocsDir = home.appendingPathComponent("Documents/planning-documents")

        // 디렉토리 생성
        if !fileManager.fileExists(atPath: planningDocsDir.path) {
            try? fileManager.createDirectory(at: planningDocsDir, withIntermediateDirectories: true)
        }

        // 날짜 포맷
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        let dateString = dateFormatter.string(from: Date())

        // 파일명 생성
        let firstFeedback = notes.first?.content.prefix(20).replacingOccurrences(of: " ", with: "").replacingOccurrences(of: "/", with: "-") ?? "기획서"
        let filename = "\(app.name)-\(firstFeedback)-기획서-\(dateString).md"
        let outputPath = planningDocsDir.appendingPathComponent(filename)

        // Claude CLI로 기획서 생성
        let prompt = """
        다음은 "\(app.name)" 앱에 대한 사용자 피드백입니다:

        \(feedbackContent)

        이 피드백을 분석하여 상세한 기획서를 작성해주세요. 다음 형식을 따라주세요:

        # \(app.name) - [피드백 주제] 기획서

        **작성일**: \(Date().formatted(.dateTime.year().month().day()))
        **현재 버전**: v\(app.currentVersion)
        **상태**: \(app.status.displayName)
        **우선순위**: \(app.priority.displayName)

        ---

        ## 📋 개요

        ### 피드백 내용
        [피드백 요약]

        ### 배경
        - **현재 상황**: [현재 상태 분석]
        - **기회**: [개선 기회]
        - **예상 효과**: [기대 효과]

        ### 비즈니스 임팩트
        - ✅ [임팩트 항목들]

        ---

        ## 💡 3가지 구현 방안

        ### 옵션 A: [간단한 방안] ⭐ (추천)

        #### 개발 기간
        **[일수]**

        #### 지원 범위
        - [범위 설명]

        #### 예상 비용
        - **총 비용**: [비용 추정]

        #### 구현 내용
        1. [단계별 구현 내용]

        #### 장점
        - ✅ [장점들]

        #### 단점
        - ⚠️ [단점들]

        ---

        ### 옵션 B: [중간 방안]

        [옵션 A와 동일한 형식]

        ---

        ### 옵션 C: [완전한 방안]

        [옵션 A와 동일한 형식]

        ---

        ## 🎯 권장 사항

        **추천**: 옵션 A

        **이유**:
        1. [추천 이유들]

        ---

        ## 📅 구현 로드맵

        ### 1주차
        - [작업 항목]

        ### 2주차
        - [작업 항목]

        ---

        ## ✅ 체크리스트

        - [ ] [체크 항목들]
        """

        print("🤖 [PlanningSectionView] Claude CLI 호출 시작...")

        // Claude CLI 실행
        let task = Process()
        task.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        task.arguments = ["claude", "-p", prompt]

        let pipe = Pipe()
        task.standardOutput = pipe

        do {
            try task.run()

            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            if let output = String(data: data, encoding: .utf8) {
                // 기획서를 파일로 저장
                try? output.write(to: outputPath, atomically: true, encoding: .utf8)
                print("✅ [PlanningSectionView] 기획서 생성 완료: \(outputPath.path)")

                // 리스트 새로고침
                loadPlanningDocuments()
            }
        } catch {
            print("❌ [PlanningSectionView] Claude CLI 실행 실패: \(error)")
        }
    }

    private func createTasksFromDecision(_ decision: PlanningDecision) {
        print("🎯 [PlanningSectionView] 의사결정으로부터 태스크 생성: \(decision.title)")

        // 선택된 옵션 찾기
        guard let selectedOptionId = decision.decision,
              let selectedOption = decision.implementationOptions.first(where: { $0.id == selectedOptionId }) else {
            print("❌ [PlanningSectionView] 선택된 옵션을 찾을 수 없습니다")
            return
        }

        // 앱 폴더 이름 가져오기
        let appFolder = portfolioService.getFolderName(for: app.name)
        let fileManager = FileManager.default
        let home = fileManager.homeDirectoryForCurrentUser
        let appsDir = home.appendingPathComponent("Documents/code/app-portfolio/apps")
        let jsonFile = appsDir.appendingPathComponent("\(appFolder).json")

        print("📂 [PlanningSectionView] JSON 파일 경로: \(jsonFile.path)")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ [PlanningSectionView] JSON 파일을 찾을 수 없습니다: \(jsonFile.path)")
            return
        }

        do {
            // JSON 파일 읽기
            let data = try Data(contentsOf: jsonFile)
            guard var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                print("❌ [PlanningSectionView] JSON 파싱 실패")
                return
            }

            // 현재 태스크 배열 가져오기
            var allTasks = json["allTasks"] as? [[String: Any]] ?? []
            var stats = json["stats"] as? [String: Int] ?? [:]

            // 새로운 태스크 생성
            let taskName = "\(decision.title.replacingOccurrences(of: "을 추가하여 글로벌 시장에 진출할까요?", with: "").replacingOccurrences(of: "?", with: "")) (\(selectedOption.label))"

            let newTask: [String: Any?] = [
                "name": taskName,
                "status": "not-started",
                "targetDate": nil,
                "targetVersion": "1.1.0"
            ]

            allTasks.append(newTask)

            // stats 업데이트
            let totalTasks = allTasks.count
            let done = allTasks.filter { ($0["status"] as? String) == "done" }.count
            let inProgress = allTasks.filter { ($0["status"] as? String) == "in-progress" }.count
            let notStarted = allTasks.filter { ($0["status"] as? String) == "not-started" }.count

            stats["totalTasks"] = totalTasks
            stats["done"] = done
            stats["inProgress"] = inProgress
            stats["notStarted"] = notStarted

            // nextTasks도 업데이트
            var nextTasks = json["nextTasks"] as? [String] ?? []
            if !nextTasks.contains(taskName) {
                nextTasks.insert(taskName, at: 0)
            }

            // JSON 업데이트
            json["allTasks"] = allTasks
            json["stats"] = stats
            json["nextTasks"] = nextTasks

            // JSON 파일에 저장
            let updatedData = try JSONSerialization.data(withJSONObject: json, options: .prettyPrinted)
            try updatedData.write(to: jsonFile)

            print("✅ [PlanningSectionView] 태스크 생성 완료: \(taskName)")
            print("   - 총 태스크: \(totalTasks)개")
            print("   - 대기: \(notStarted)개")

        } catch {
            print("❌ [PlanningSectionView] 태스크 생성 실패: \(error)")
        }
    }
}

// MARK: - Planning Feature Card

struct PlanningFeatureCard: View {
    @Binding var suggestion: PlanningFeature
    let onApprove: () -> Void
    let onReject: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(suggestion.title)
                        .font(.headline)
                    Text(suggestion.description)
                        .font(.body)
                        .foregroundColor(.secondary)
                }
                Spacer()

                // 상태 배지
                HStack(spacing: 4) {
                    Text(suggestion.status.rawValue)
                        .font(.body)
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(suggestion.status.color.opacity(0.2))
                .foregroundColor(suggestion.status.color)
                .cornerRadius(6)
            }

            HStack(spacing: 12) {
                Label("우선순위: \(suggestion.priority)", systemImage: "flag.fill")
                    .font(.body)
                    .foregroundColor(.blue)
            }

            if suggestion.status == .pending {
                Divider()

                HStack(spacing: 8) {
                    Button(action: {
                        suggestion.status = .rejected
                        onReject()
                    }) {
                        HStack {
                            Image(systemName: "xmark.circle.fill")
                            Text("거절")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 8)
                        .background(Color.red.opacity(0.1))
                        .foregroundColor(.red)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)

                    Button(action: {
                        suggestion.status = .approved
                        onApprove()
                    }) {
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                            Text("승인")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 8)
                        .background(Color.green.opacity(0.1))
                        .foregroundColor(.green)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(suggestion.status.color.opacity(0.3), lineWidth: 1)
        )
    }
}

struct DecisionRecordCard: View {
    let decision: PlanningDecisionRecord

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: decision.type.icon)
                    .foregroundColor(decision.type.color)
                Text(decision.type.rawValue)
                    .font(.body)
                    .foregroundColor(decision.type.color)
            }
            Text(decision.content)
                .font(.body)
                .lineLimit(2)
            Text(formatDate(decision.createdAt))
                .font(.body)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(width: 200)
        .background(decision.type.color.opacity(0.1))
        .cornerRadius(8)
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

// MARK: - Models

struct PlanningFeature: Identifiable, Codable {
    let id: String
    let title: String
    let description: String
    let priority: String
    var status: PlanningStatus

    init(id: String = UUID().uuidString, title: String, description: String, priority: String, status: PlanningStatus) {
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
    }
}

enum PlanningStatus: String, Codable {
    case pending = "대기"
    case approved = "승인됨"
    case rejected = "거절됨"

    var color: Color {
        switch self {
        case .pending: return .orange
        case .approved: return .green
        case .rejected: return .red
        }
    }
}

struct PlanningDecisionRecord: Identifiable, Codable {
    let id: String
    let type: DecisionType
    let content: String
    let createdAt: Date

    init(id: String = UUID().uuidString, type: DecisionType, content: String, createdAt: Date = Date()) {
        self.id = id
        self.type = type
        self.content = content
        self.createdAt = createdAt
    }
}

enum DecisionType: String, Codable {
    case approve = "승인"
    case reject = "거절"

    var color: Color {
        switch self {
        case .approve: return .green
        case .reject: return .red
        }
    }

    var icon: String {
        switch self {
        case .approve: return "checkmark.circle.fill"
        case .reject: return "xmark.circle.fill"
        }
    }
}

// MARK: - Planning Document

struct PlanningDocument: Identifiable {
    let id: String
    let title: String
    let filePath: String
    let createdAt: Date
}

// MARK: - Planning Option

struct PlanningOption: Identifiable {
    let id: String
    let title: String
    let description: String
    let period: String
    let cost: String
    var status: OptionStatus

    enum OptionStatus {
        case pending
        case approved
        case rejected

        var color: Color {
            switch self {
            case .pending: return .orange
            case .approved: return .green
            case .rejected: return .red
            }
        }

        var label: String {
            switch self {
            case .pending: return "검토 중"
            case .approved: return "승인됨"
            case .rejected: return "거절됨"
            }
        }
    }
}

struct PlanningOptionCard: View {
    @State var option: PlanningOption

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 헤더
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 6) {
                    Text(option.title)
                        .font(.headline)
                        .foregroundColor(.primary)

                    HStack(spacing: 12) {
                        if !option.period.isEmpty {
                            Label(option.period, systemImage: "clock")
                                .font(.body)
                                .foregroundColor(.secondary)
                        }

                        if !option.cost.isEmpty {
                            Label(option.cost, systemImage: "dollarsign.circle")
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                    }
                }

                Spacer()

                // 상태 배지
                Text(option.status.label)
                    .font(.body)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(option.status.color.opacity(0.2))
                    .foregroundColor(option.status.color)
                    .cornerRadius(6)
            }

            // 설명
            if !option.description.isEmpty {
                Text(option.description)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .lineLimit(3)
            }

            // 액션 버튼
            if option.status == .pending {
                Divider()

                HStack(spacing: 8) {
                    Button(action: {
                        option.status = .rejected
                    }) {
                        HStack {
                            Image(systemName: "xmark.circle.fill")
                            Text("거절")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 8)
                        .background(Color.red.opacity(0.1))
                        .foregroundColor(.red)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)

                    Button(action: {
                        option.status = .approved
                    }) {
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                            Text("승인")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 8)
                        .background(Color.green.opacity(0.1))
                        .foregroundColor(.green)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .padding()
        .background(Color(NSColor.textBackgroundColor))
        .cornerRadius(10)
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(option.status.color.opacity(0.3), lineWidth: 1.5)
        )
    }
}

struct GeneratedDocumentCard: View {
    let document: PlanningDocument
    @State private var showingDocument = false
    @State private var isExpanded = false
    @State private var options: [PlanningOption] = []

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 헤더
            HStack(spacing: 12) {
                Image(systemName: "doc.text.fill")
                    .font(.title2)
                    .foregroundColor(.blue)

                VStack(alignment: .leading, spacing: 4) {
                    Text(document.title)
                        .font(.headline)
                        .foregroundColor(.primary)

                    Text(formatDate(document.createdAt))
                        .font(.body)
                        .foregroundColor(.secondary)
                }

                Spacer()

                HStack(spacing: 8) {
                    Button(action: {
                        isExpanded.toggle()
                    }) {
                        HStack(spacing: 4) {
                            Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                            Text(isExpanded ? "접기" : "제안 보기")
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.blue.opacity(0.2))
                        .foregroundColor(.blue)
                        .cornerRadius(8)
                    }
                    .buttonStyle(.plain)

                    Button(action: {
                        openInEditor()
                    }) {
                        Image(systemName: "arrow.up.right.square")
                            .foregroundColor(.secondary)
                    }
                    .buttonStyle(.plain)
                    .help("외부 에디터에서 열기")
                }
            }

            // 옵션 리스트
            if isExpanded {
                Divider()

                if options.isEmpty {
                    Text("옵션을 파싱하는 중...")
                        .font(.body)
                        .foregroundColor(.secondary)
                        .padding(.vertical, 8)
                } else {
                    VStack(spacing: 12) {
                        ForEach(options) { option in
                            PlanningOptionCard(option: option)
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.blue.opacity(0.3), lineWidth: 1)
        )
        .onAppear {
            parseDocument()
        }
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy.MM.dd HH:mm"
        return formatter.string(from: date)
    }

    private func openInEditor() {
        let url = URL(fileURLWithPath: document.filePath)
        NSWorkspace.shared.open(url)
    }

    private func parseDocument() {
        guard let content = try? String(contentsOf: URL(fileURLWithPath: document.filePath), encoding: .utf8) else {
            return
        }

        var parsedOptions: [PlanningOption] = []
        let lines = content.components(separatedBy: .newlines)

        var currentOption: String?
        var currentTitle: String?
        var currentDescription: [String] = []
        var currentPeriod: String?
        var currentCost: String?

        for line in lines {
            // 옵션 시작 (### 옵션 A:, ### 옵션 B: 등)
            if line.hasPrefix("### 옵션") {
                // 이전 옵션 저장
                if let option = currentOption, let title = currentTitle {
                    parsedOptions.append(PlanningOption(
                        id: option,
                        title: title,
                        description: currentDescription.joined(separator: "\n"),
                        period: currentPeriod ?? "",
                        cost: currentCost ?? "",
                        status: .pending
                    ))
                }

                // 새 옵션 시작
                currentOption = line
                currentTitle = line.replacingOccurrences(of: "###", with: "").trimmingCharacters(in: .whitespaces)
                currentDescription = []
                currentPeriod = nil
                currentCost = nil
            }
            // 개발 기간
            else if line.hasPrefix("#### 개발 기간") {
                // 다음 줄 읽기
                continue
            }
            else if line.hasPrefix("**") && line.contains("일") && currentPeriod == nil {
                currentPeriod = line.replacingOccurrences(of: "**", with: "").trimmingCharacters(in: .whitespaces)
            }
            // 예상 비용
            else if line.hasPrefix("#### 예상 비용") || line.hasPrefix("#### 총 비용") {
                continue
            }
            else if line.hasPrefix("- **총 비용**:") {
                currentCost = line.replacingOccurrences(of: "- **총 비용**:", with: "").trimmingCharacters(in: .whitespaces)
            }
            // 설명 수집
            else if !line.isEmpty && !line.hasPrefix("#") && !line.hasPrefix("---") && currentOption != nil {
                if !line.hasPrefix("#### ") && !line.hasPrefix("- **번역**:") && !line.hasPrefix("- **개발**:") {
                    currentDescription.append(line)
                }
            }
        }

        // 마지막 옵션 저장
        if let option = currentOption, let title = currentTitle {
            parsedOptions.append(PlanningOption(
                id: option,
                title: title,
                description: currentDescription.joined(separator: "\n"),
                period: currentPeriod ?? "",
                cost: currentCost ?? "",
                status: .pending
            ))
        }

        options = parsedOptions
        print("📋 [GeneratedDocumentCard] \(options.count)개 옵션 파싱 완료")
    }
}

// MARK: - Markdown Document Viewer

struct MarkdownDocumentViewer: View {
    let document: PlanningDocument
    @Environment(\.dismiss) var dismiss
    @State private var content: String = ""

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(document.title)
                        .font(.title2)
                        .bold()
                    Text(formatDate(document.createdAt))
                        .font(.body)
                        .foregroundColor(.secondary)
                }

                Spacer()

                HStack(spacing: 12) {
                    Button(action: {
                        openInEditor()
                    }) {
                        HStack(spacing: 4) {
                            Image(systemName: "pencil")
                            Text("편집")
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.blue.opacity(0.2))
                        .foregroundColor(.blue)
                        .cornerRadius(8)
                    }
                    .buttonStyle(.plain)

                    Button("닫기") {
                        dismiss()
                    }
                    .keyboardShortcut(.escape)
                }
            }
            .padding()
            .background(Color(NSColor.controlBackgroundColor))

            Divider()

            // Content
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    Text(.init(content))
                        .textSelection(.enabled)
                        .padding(24)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .frame(width: 900, height: 700)
        .onAppear {
            loadContent()
        }
    }

    private func loadContent() {
        if let loadedContent = try? String(contentsOf: URL(fileURLWithPath: document.filePath), encoding: .utf8) {
            content = loadedContent
        }
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy년 MM월 dd일 HH:mm"
        return formatter.string(from: date)
    }

    private func openInEditor() {
        let url = URL(fileURLWithPath: document.filePath)
        NSWorkspace.shared.open(url)
    }
}

// MARK: - App Decision Card

struct AppDecisionCard: View {
    let decision: PlanningDecision
    let isExpanded: Bool
    let selectedOption: String?
    let onToggleExpand: () -> Void
    let onSelectOption: (String) -> Void
    let onApprove: () -> Void
    let onDelete: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 헤더
            Button(action: onToggleExpand) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            DecisionPriorityBadge(priority: decision.priority)
                            DecisionUrgencyBadge(urgency: decision.urgency)
                        }

                        Text(decision.title)
                            .font(.headline)
                            .multilineTextAlignment(.leading)
                            .foregroundColor(.primary)
                    }

                    Spacer()

                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .foregroundColor(.secondary)
                }
            }
            .buttonStyle(.plain)

            // 요약 정보 (축소 시)
            if !isExpanded {
                Text(decision.description)
                    .font(.body)
                    .foregroundColor(.secondary)
                    .lineLimit(2)

                if let recommended = decision.implementationOptions.first(where: { $0.id == decision.aiRecommendation }) {
                    HStack {
                        Image(systemName: "sparkles")
                            .foregroundColor(.yellow)
                        Text("AI 추천: \(recommended.label)")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                }
            }

            // 상세 정보 (확장 시)
            if isExpanded {
                Divider()

                VStack(alignment: .leading, spacing: 16) {
                    // 설명
                    VStack(alignment: .leading, spacing: 8) {
                        Text("상황")
                            .font(.subheadline)
                            .bold()
                        Text(decision.description)
                            .font(.body)
                    }

                    // 비즈니스 임팩트
                    VStack(alignment: .leading, spacing: 8) {
                        Text("비즈니스 임팩트")
                            .font(.subheadline)
                            .bold()
                        Text(decision.businessImpact)
                            .font(.body)
                            .foregroundColor(.orange)
                    }

                    Divider()

                    // 구현 옵션들
                    VStack(alignment: .leading, spacing: 12) {
                        Text("구현 옵션")
                            .font(.subheadline)
                            .bold()

                        ForEach(decision.implementationOptions) { option in
                            DecisionOptionCard(
                                option: option,
                                isRecommended: option.id == decision.aiRecommendation,
                                isSelected: selectedOption == option.id,
                                onSelect: {
                                    onSelectOption(option.id)
                                }
                            )
                        }
                    }

                    // AI 추천 이유
                    if let recommended = decision.implementationOptions.first(where: { $0.id == decision.aiRecommendation }) {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Image(systemName: "sparkles")
                                    .foregroundColor(.yellow)
                                Text("AI 추천 이유")
                                    .font(.subheadline)
                                    .bold()
                            }
                            Text(decision.aiReasoning)
                                .font(.body)
                                .padding()
                                .background(Color.yellow.opacity(0.1))
                                .cornerRadius(8)
                        }
                    }

                    Divider()

                    // 액션 버튼
                    HStack(spacing: 12) {
                        Button(action: onDelete) {
                            HStack {
                                Image(systemName: "trash")
                                Text("삭제")
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 8)
                            .background(Color.red.opacity(0.1))
                            .foregroundColor(.red)
                            .cornerRadius(6)
                        }
                        .buttonStyle(.plain)

                        Button(action: onApprove) {
                            HStack {
                                Image(systemName: "checkmark.circle.fill")
                                Text("승인")
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 8)
                            .background(selectedOption != nil ? Color.green.opacity(0.1) : Color.gray.opacity(0.1))
                            .foregroundColor(selectedOption != nil ? .green : .gray)
                            .cornerRadius(6)
                        }
                        .buttonStyle(.plain)
                        .disabled(selectedOption == nil)
                    }
                }
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(selectedOption != nil ? Color.blue : Color.orange.opacity(0.3), lineWidth: 2)
        )
    }
}

struct DecisionOptionCard: View {
    let option: ImplementationOption
    let isRecommended: Bool
    let isSelected: Bool
    let onSelect: () -> Void

    var body: some View {
        Button(action: onSelect) {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text(option.label)
                        .font(.subheadline)
                        .bold()

                    if isRecommended {
                        Text("추천")
                            .font(.body)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color.yellow)
                            .cornerRadius(4)
                    }

                    Spacer()

                    Text(option.estimatedTime)
                        .font(.body)
                        .foregroundColor(.secondary)

                    if isSelected {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.blue)
                    } else {
                        Image(systemName: "circle")
                            .foregroundColor(.secondary)
                    }
                }

                Text(option.description)
                    .font(.body)
                    .foregroundColor(.secondary)

                // 장단점
                HStack(alignment: .top, spacing: 16) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("장점")
                            .font(.body)
                            .bold()
                            .foregroundColor(.green)
                        ForEach(option.pros, id: \.self) { pro in
                            HStack(alignment: .top, spacing: 4) {
                                Text("•")
                                Text(pro)
                            }
                            .font(.body)
                            .foregroundColor(.secondary)
                        }
                    }

                    VStack(alignment: .leading, spacing: 4) {
                        Text("단점")
                            .font(.body)
                            .bold()
                            .foregroundColor(.red)
                        ForEach(option.cons, id: \.self) { con in
                            HStack(alignment: .top, spacing: 4) {
                                Text("•")
                                Text(con)
                            }
                            .font(.body)
                            .foregroundColor(.secondary)
                        }
                    }
                }
            }
            .padding()
            .background(isSelected ? Color.blue.opacity(0.1) : Color(NSColor.textBackgroundColor))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(isSelected ? Color.blue : Color.gray.opacity(0.2), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }
}

struct DecisionPriorityBadge: View {
    let priority: String

    var body: some View {
        Text(priority.uppercased())
            .font(.body)
            .bold()
            .padding(.horizontal, 6)
            .padding(.vertical, 2)
            .background(priorityColor)
            .foregroundColor(.white)
            .cornerRadius(4)
    }

    private var priorityColor: Color {
        switch priority.lowercased() {
        case "critical": return .red
        case "high": return .orange
        case "medium": return .yellow
        case "low": return .green
        default: return .gray
        }
    }
}

struct DecisionUrgencyBadge: View {
    let urgency: String

    var body: some View {
        HStack(spacing: 2) {
            Image(systemName: urgencyIcon)
            Text(urgency.uppercased())
        }
        .font(.body)
        .padding(.horizontal, 6)
        .padding(.vertical, 2)
        .background(Color.gray.opacity(0.2))
        .cornerRadius(4)
    }

    private var urgencyIcon: String {
        switch urgency.lowercased() {
        case "high": return "exclamationmark.3"
        case "medium": return "exclamationmark.2"
        case "low": return "exclamationmark"
        default: return "minus"
        }
    }
}

// MARK: - Completed Decision History Card

struct CompletedDecisionHistoryCard: View {
    let decision: PlanningDecision
    let onRevert: () -> Void
    let onCreateTasks: () -> Void
    @State private var isExpanded = false
    @State private var tasksCreated = false

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
                        Text(decision.title)
                            .font(.headline)
                            .foregroundColor(.primary)

                        // 상태 배지들
                        HStack(spacing: 6) {
                            // 태스크 생성 완료 배지
                            if tasksCreated {
                                HStack(spacing: 4) {
                                    Image(systemName: "list.bullet.circle.fill")
                                        .font(.body)
                                    Text("태스크 생성 완료")
                                        .font(.body)
                                }
                                .padding(.horizontal, 8)
                                .padding(.vertical, 3)
                                .background(Color.blue.opacity(0.2))
                                .foregroundColor(.blue)
                                .cornerRadius(6)
                            }

                            // 의사결정 완료
                            HStack(spacing: 4) {
                                Image(systemName: "checkmark.circle.fill")
                                    .font(.body)
                                Text("의사결정 완료")
                                    .font(.body)
                            }
                            .padding(.horizontal, 8)
                            .padding(.vertical, 3)
                            .background(Color.green.opacity(0.2))
                            .foregroundColor(.green)
                            .cornerRadius(6)
                        }

                        if let selectedOptionId = decision.decision,
                           let selectedOption = decision.implementationOptions.first(where: { $0.id == selectedOptionId }) {
                            Text("선택: \(selectedOption.label)")
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                    }

                    Spacer()

                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .foregroundColor(.secondary)
                        .font(.body)
                }
            }
            .buttonStyle(.plain)

            // 상세 정보 (확장 시)
            if isExpanded {
                Divider()

                VStack(alignment: .leading, spacing: 12) {
                    // 선택된 옵션 상세
                    if let selectedOptionId = decision.decision,
                       let selectedOption = decision.implementationOptions.first(where: { $0.id == selectedOptionId }) {

                        VStack(alignment: .leading, spacing: 8) {
                            Text("선택된 구현 방안")
                                .font(.subheadline)
                                .bold()

                            VStack(alignment: .leading, spacing: 6) {
                                HStack {
                                    Text(selectedOption.label)
                                        .font(.body)
                                        .fontWeight(.medium)

                                    Spacer()

                                    Text(selectedOption.estimatedTime)
                                        .font(.body)
                                        .foregroundColor(.secondary)
                                }

                                Text(selectedOption.description)
                                    .font(.body)
                                    .foregroundColor(.secondary)

                                // 구현 내용
                                if let details = selectedOption.technicalDetails, !details.isEmpty {
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text("구현 내용")
                                            .font(.body)
                                            .bold()
                                            .foregroundColor(.blue)

                                        ForEach(Array(details.enumerated()), id: \.offset) { index, detail in
                                            HStack(alignment: .top, spacing: 4) {
                                                Text("\(index + 1).")
                                                Text(detail)
                                            }
                                            .font(.body)
                                            .foregroundColor(.secondary)
                                        }
                                    }
                                }
                            }
                            .padding()
                            .background(Color.green.opacity(0.05))
                            .cornerRadius(8)
                        }

                        // 비즈니스 임팩트
                        VStack(alignment: .leading, spacing: 6) {
                            Text("비즈니스 임팩트")
                                .font(.body)
                                .bold()
                            Text(decision.businessImpact)
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                    }

                    Divider()

                    // 태스크 생성 버튼
                    if !tasksCreated {
                        Button(action: {
                            onCreateTasks()
                            tasksCreated = true
                        }) {
                            HStack {
                                Image(systemName: "checklist")
                                Text("태스크 생성하기")
                            }
                            .font(.body)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 6)
                            .background(Color.blue.opacity(0.1))
                            .foregroundColor(.blue)
                            .cornerRadius(6)
                        }
                        .buttonStyle(.plain)
                    }

                    // 복귀 버튼
                    Button(action: onRevert) {
                        HStack {
                            Image(systemName: "arrow.uturn.backward")
                            Text("의사결정 되돌리기")
                        }
                        .font(.body)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                        .background(Color.orange.opacity(0.1))
                        .foregroundColor(.orange)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .padding()
        .background(Color.green.opacity(0.05))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.green.opacity(0.3), lineWidth: 1.5)
        )
    }
}
