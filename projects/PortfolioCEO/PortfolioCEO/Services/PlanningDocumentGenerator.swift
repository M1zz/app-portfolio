import Foundation

class PlanningDocumentGenerator {
    static let shared = PlanningDocumentGenerator()

    private init() {}

    // 전체 프로젝트 종합 기획서 생성
    func generateComprehensivePlan(for apps: [AppModel]) -> String {
        var document = ""

        // 헤더
        document += "# 프로젝트 종합 기획서\n\n"
        document += "**작성일**: \(formatDate(Date()))\n\n"
        document += "---\n\n"

        // 요약
        document += "## 📋 전체 요약\n\n"
        document += "- **총 프로젝트 수**: \(apps.count)개\n"

        let activeApps = apps.filter { $0.status != .archived }
        document += "- **활성 프로젝트**: \(activeApps.count)개\n"

        let totalFeedbackCount = apps.reduce(0) { count, app in
            let notes = loadNotes(for: app.name)
            return count + notes.count
        }
        document += "- **총 피드백 수**: \(totalFeedbackCount)개\n\n"

        document += "---\n\n"

        // 각 프로젝트별 상세 기획
        document += "## 📱 프로젝트별 상세 기획\n\n"

        for (index, app) in apps.enumerated() {
            document += generateProjectSection(for: app, index: index + 1)
            document += "\n---\n\n"
        }

        // 우선순위 정리
        document += generatePrioritySummary(for: apps)

        // 다음 액션 아이템
        document += generateNextActions(for: apps)

        return document
    }

    // 개별 프로젝트 기획서 생성
    func generateProjectPlan(for app: AppModel) -> String {
        var document = ""

        document += "# \(app.name) 기획서\n\n"
        document += "**작성일**: \(formatDate(Date()))\n"
        document += "**현재 버전**: v\(app.currentVersion)\n"
        document += "**상태**: \(app.status.displayName)\n\n"

        document += "---\n\n"

        // 프로젝트 개요
        if let detail = loadAppDetail(for: app.name) {
            document += "## 📖 프로젝트 개요\n\n"
            document += "\(detail.description)\n\n"

            document += "### 기술 스택\n\n"
            document += "- **플랫폼**: \(detail.techStack.platforms.joined(separator: ", "))\n"
            document += "- **UI**: \(detail.techStack.ui)\n"
            document += "- **데이터 저장**: \(detail.techStack.dataStorage)\n"
            if !detail.techStack.otherFrameworks.isEmpty {
                document += "- **프레임워크**: \(detail.techStack.otherFrameworks.joined(separator: ", "))\n"
            }
            document += "\n"
        }

        document += "---\n\n"

        // 피드백 분석
        let notes = loadNotes(for: app.name)
        document += "## 💬 피드백 분석 (\(notes.count)건)\n\n"

        if !notes.isEmpty {
            let pendingNotes = notes.filter { $0.status == .pending }
            let inProgressNotes = notes.filter { $0.status == .proposed }
            let completedNotes = notes.filter { $0.status == .completed }

            document += "- **대기**: \(pendingNotes.count)건\n"
            document += "- **처리중**: \(inProgressNotes.count)건\n"
            document += "- **완료**: \(completedNotes.count)건\n\n"

            if !pendingNotes.isEmpty {
                document += "### 처리 대기 중인 피드백\n\n"
                for (index, note) in pendingNotes.prefix(10).enumerated() {
                    document += "\(index + 1). \(note.content)\n"
                    document += "   - 작성일: \(formatDate(note.createdAt))\n\n"
                }
            }
        } else {
            document += "피드백이 아직 없습니다.\n\n"
        }

        document += "---\n\n"

        // AI 기능 제안
        let suggestions = loadSuggestions(for: app.name)
        document += "## 💡 기능 제안 (\(suggestions.count)건)\n\n"

        if !suggestions.isEmpty {
            let pending = suggestions.filter { $0.status == .pending }
            let approved = suggestions.filter { $0.status == .approved }
            let rejected = suggestions.filter { $0.status == .rejected }

            if !pending.isEmpty {
                document += "### 검토 대기중\n\n"
                for (index, suggestion) in pending.enumerated() {
                    document += "\(index + 1). **\(suggestion.title)** (우선순위: \(suggestion.priority))\n"
                    document += "   - \(suggestion.description)\n\n"
                }
            }

            if !approved.isEmpty {
                document += "### 승인됨\n\n"
                for (index, suggestion) in approved.enumerated() {
                    document += "- [x] \(suggestion.title)\n"
                }
                document += "\n"
            }

            if !rejected.isEmpty {
                document += "### 거절됨\n\n"
                for (index, suggestion) in rejected.enumerated() {
                    document += "- [ ] ~~\(suggestion.title)~~\n"
                }
                document += "\n"
            }
        } else {
            document += "기능 제안이 아직 없습니다. '기획 의사결정' 섹션에서 AI 제안을 생성하세요.\n\n"
        }

        document += "---\n\n"

        // 태스크 현황
        document += "## ✅ 태스크 현황\n\n"
        document += "- **전체**: \(app.stats.totalTasks)개\n"
        document += "- **완료**: \(app.stats.done)개\n"
        document += "- **진행중**: \(app.stats.inProgress)개\n"
        document += "- **진행전**: \(app.todoCount)개\n"
        document += "- **대기**: \(app.backlogCount)개\n"
        document += "- **완료율**: \(Int(app.completionRate))%\n\n"

        document += "---\n\n"

        // 다음 액션
        document += "## 🎯 다음 액션 아이템\n\n"

        let nextActions = generateProjectNextActions(for: app, notes: notes, suggestions: suggestions)
        for (index, action) in nextActions.enumerated() {
            document += "\(index + 1). \(action)\n"
        }

        document += "\n"

        return document
    }

    // MARK: - Private Helpers

    private func generateProjectSection(for app: AppModel, index: Int) -> String {
        var section = ""

        section += "### \(index). \(app.name)\n\n"
        section += "**버전**: v\(app.currentVersion) | **상태**: \(app.status.displayName)\n\n"

        let notes = loadNotes(for: app.name)
        let suggestions = loadSuggestions(for: app.name)

        section += "#### 현황\n\n"
        section += "- 피드백: \(notes.count)건\n"
        section += "- 기능 제안: \(suggestions.count)건\n"
        section += "- 태스크 완료율: \(Int(app.completionRate))%\n\n"

        if !notes.isEmpty {
            let pendingNotes = notes.filter { $0.status == .pending }
            if !pendingNotes.isEmpty {
                section += "#### 주요 피드백\n\n"
                for note in pendingNotes.prefix(3) {
                    section += "- \(note.content.prefix(100))\n"
                }
                section += "\n"
            }
        }

        if !suggestions.isEmpty {
            let pendingSuggestions = suggestions.filter { $0.status == .pending }
            if !pendingSuggestions.isEmpty {
                section += "#### 제안된 기능\n\n"
                for suggestion in pendingSuggestions.prefix(3) {
                    section += "- [\(suggestion.priority)] \(suggestion.title)\n"
                }
                section += "\n"
            }
        }

        return section
    }

    private func generatePrioritySummary(for apps: [AppModel]) -> String {
        var section = ""

        section += "## 🎯 우선순위 정리\n\n"

        var highPriority: [(app: String, items: [String])] = []
        var mediumPriority: [(app: String, items: [String])] = []

        for app in apps {
            let suggestions = loadSuggestions(for: app.name)
            let pending = suggestions.filter { $0.status == .pending }

            let high = pending.filter { $0.priority == "높음" }
            let medium = pending.filter { $0.priority == "중간" }

            if !high.isEmpty {
                highPriority.append((app: app.name, items: high.map { $0.title }))
            }
            if !medium.isEmpty {
                mediumPriority.append((app: app.name, items: medium.map { $0.title }))
            }
        }

        if !highPriority.isEmpty {
            section += "### 🔴 높음\n\n"
            for (app, items) in highPriority {
                section += "**\(app)**\n"
                for item in items {
                    section += "- \(item)\n"
                }
                section += "\n"
            }
        }

        if !mediumPriority.isEmpty {
            section += "### 🟡 중간\n\n"
            for (app, items) in mediumPriority {
                section += "**\(app)**\n"
                for item in items {
                    section += "- \(item)\n"
                }
                section += "\n"
            }
        }

        section += "---\n\n"

        return section
    }

    private func generateNextActions(for apps: [AppModel]) -> String {
        var section = ""

        section += "## 📌 전체 다음 액션\n\n"

        for app in apps {
            let notes = loadNotes(for: app.name)
            let suggestions = loadSuggestions(for: app.name)
            let actions = generateProjectNextActions(for: app, notes: notes, suggestions: suggestions)

            if !actions.isEmpty {
                section += "### \(app.name)\n\n"
                for (index, action) in actions.enumerated() {
                    section += "\(index + 1). \(action)\n"
                }
                section += "\n"
            }
        }

        return section
    }

    private func generateProjectNextActions(for app: AppModel, notes: [ProjectNote], suggestions: [PlanningFeature]) -> [String] {
        var actions: [String] = []

        // 대기 중인 피드백이 있으면
        let pendingNotes = notes.filter { $0.status == .pending }
        if !pendingNotes.isEmpty {
            actions.append("피드백 \(pendingNotes.count)건 검토 및 분류")
        }

        // 검토 대기 중인 제안이 있으면
        let pendingSuggestions = suggestions.filter { $0.status == .pending }
        if !pendingSuggestions.isEmpty {
            actions.append("기능 제안 \(pendingSuggestions.count)건 의사결정 필요")
        }

        // 승인된 제안이 있으면
        let approvedSuggestions = suggestions.filter { $0.status == .approved }
        if !approvedSuggestions.isEmpty {
            actions.append("승인된 기능 \(approvedSuggestions.count)건 개발 계획 수립")
        }

        // 완료율이 낮으면
        if app.completionRate < 50 {
            actions.append("태스크 진행 상황 점검 (현재 완료율: \(Int(app.completionRate))%)")
        }

        // 처리 중인 피드백이 오래된 경우
        let inProgressNotes = notes.filter { $0.status == .proposed }
        if inProgressNotes.count > 3 {
            actions.append("처리 중인 피드백 \(inProgressNotes.count)건 완료 확인")
        }

        return actions
    }

    private func loadNotes(for appName: String) -> [ProjectNote] {
        let notesDir = PortfolioService.shared.projectNotesDirectory
        let folderName = PortfolioService.shared.getFolderName(for: appName)
        let filePath = notesDir.appendingPathComponent("\(folderName).json")

        guard let data = try? Data(contentsOf: filePath) else { return [] }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        if let loaded = try? decoder.decode([ProjectNote].self, from: data) {
            return loaded
        }

        return []
    }

    private func loadSuggestions(for appName: String) -> [PlanningFeature] {
        let planningDir = PortfolioService.shared.planningDirectory
        let folderName = PortfolioService.shared.getFolderName(for: appName)
        let filePath = planningDir.appendingPathComponent("\(folderName)-suggestions.json")

        guard let data = try? Data(contentsOf: filePath) else { return [] }

        let decoder = JSONDecoder()

        if let loaded = try? decoder.decode([PlanningFeature].self, from: data) {
            return loaded
        }

        return []
    }

    private func loadAppDetail(for appName: String) -> AppDetailInfo? {
        let fileManager = FileManager.default
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let mappingPath = documentsPath.appendingPathComponent("app-name-mapping.json")

        guard let data = try? Data(contentsOf: mappingPath),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let apps = json["apps"] as? [String: [String: String]],
              let appInfo = apps[appName],
              let folder = appInfo["folder"] else {
            return nil
        }

        return AppDetailService.shared.loadDetail(for: folder)
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy년 MM월 dd일 HH:mm"
        return formatter.string(from: date)
    }

    // 파일로 저장
    func savePlanToFile(content: String, filename: String) -> URL? {
        let fileManager = FileManager.default
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let plansDir = documentsPath.appendingPathComponent("planning-documents")

        if !fileManager.fileExists(atPath: plansDir.path) {
            try? fileManager.createDirectory(at: plansDir, withIntermediateDirectories: true)
        }

        let filePath = plansDir.appendingPathComponent("\(filename).md")

        do {
            try content.write(to: filePath, atomically: true, encoding: .utf8)
            return filePath
        } catch {
            print("Failed to save plan: \(error)")
            return nil
        }
    }
}
