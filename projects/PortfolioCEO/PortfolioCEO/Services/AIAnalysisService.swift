import Foundation

class AIAnalysisService {
    static let shared = AIAnalysisService()

    private init() {}

    // 피드백 메모들을 분석하여 기능 제안 생성
    func generateFeatureSuggestionsFromFeedback(appName: String, notes: [ProjectNote]) -> [PlanningFeature] {
        guard !notes.isEmpty else { return [] }

        var suggestions: [PlanningFeature] = []

        // 메모 내용을 분석
        for note in notes.prefix(10) { // 최대 10개 메모 분석
            // 메모 상태가 pending이거나 proposed인 것만 분석
            guard note.status == .pending || note.status == .proposed else { continue }

            let content = note.content.lowercased()

            // 키워드 기반 분석 및 제안 생성
            if content.contains("버그") || content.contains("오류") || content.contains("에러") || content.contains("crash") {
                suggestions.append(PlanningFeature(
                    title: "버그 수정: \(extractKeywords(from: note.content))",
                    description: note.content,
                    priority: "높음",
                    status: .pending
                ))
            }

            if content.contains("ui") || content.contains("디자인") || content.contains("화면") || content.contains("레이아웃") {
                suggestions.append(PlanningFeature(
                    title: "UI 개선: \(extractKeywords(from: note.content))",
                    description: note.content,
                    priority: determinePriority(from: content),
                    status: .pending
                ))
            }

            if content.contains("기능") || content.contains("추가") || content.contains("새로운") {
                suggestions.append(PlanningFeature(
                    title: "신규 기능: \(extractKeywords(from: note.content))",
                    description: note.content,
                    priority: determinePriority(from: content),
                    status: .pending
                ))
            }

            if content.contains("성능") || content.contains("느림") || content.contains("빠르게") || content.contains("최적화") {
                suggestions.append(PlanningFeature(
                    title: "성능 최적화: \(extractKeywords(from: note.content))",
                    description: note.content,
                    priority: "중간",
                    status: .pending
                ))
            }

            if content.contains("보안") || content.contains("인증") || content.contains("권한") {
                suggestions.append(PlanningFeature(
                    title: "보안 개선: \(extractKeywords(from: note.content))",
                    description: note.content,
                    priority: "높음",
                    status: .pending
                ))
            }

            if content.contains("데이터") || content.contains("저장") || content.contains("동기화") {
                suggestions.append(PlanningFeature(
                    title: "데이터 관리: \(extractKeywords(from: note.content))",
                    description: note.content,
                    priority: determinePriority(from: content),
                    status: .pending
                ))
            }

            // 키워드 매칭이 없는 경우 일반 개선사항으로 분류
            if suggestions.isEmpty || !suggestions.contains(where: { $0.description == note.content }) {
                suggestions.append(PlanningFeature(
                    title: "개선사항: \(extractKeywords(from: note.content))",
                    description: note.content,
                    priority: determinePriority(from: content),
                    status: .pending
                ))
            }
        }

        return suggestions
    }

    // Claude API를 사용한 고급 분석 (향후 구현)
    func generateAdvancedSuggestions(appName: String, notes: [ProjectNote], appContext: AppDetailInfo?) async throws -> [PlanningFeature] {
        // TODO: Claude API 통합
        // 1. 프로젝트 컨텍스트 수집 (앱 설명, 기술 스택, 현재 상태)
        // 2. 모든 피드백 메모 통합
        // 3. Claude API 호출하여 종합적인 분석 및 제안 생성
        // 4. 구조화된 제안 반환

        return []
    }

    // MARK: - Helper Methods

    private func extractKeywords(from text: String) -> String {
        // 첫 문장이나 핵심 키워드 추출 (최대 40자)
        let sentences = text.components(separatedBy: CharacterSet(charactersIn: ".。\n"))
        if let first = sentences.first?.trimmingCharacters(in: .whitespacesAndNewlines), !first.isEmpty {
            return String(first.prefix(40))
        }
        return String(text.prefix(40))
    }

    private func determinePriority(from content: String) -> String {
        let highPriorityKeywords = ["긴급", "심각", "중요", "급", "빨리", "urgent", "critical", "asap"]
        let lowPriorityKeywords = ["나중", "여유", "천천히", "later", "nice to have"]

        for keyword in highPriorityKeywords {
            if content.contains(keyword) {
                return "높음"
            }
        }

        for keyword in lowPriorityKeywords {
            if content.contains(keyword) {
                return "낮음"
            }
        }

        return "중간"
    }

    // 여러 프로젝트의 피드백을 한번에 분석
    func analyzeMutipleProjects(apps: [AppModel]) -> [String: [PlanningFeature]] {
        var results: [String: [PlanningFeature]] = [:]

        for app in apps {
            let notes = loadNotes(for: app.name)
            if !notes.isEmpty {
                let suggestions = generateFeatureSuggestionsFromFeedback(appName: app.name, notes: notes)
                if !suggestions.isEmpty {
                    results[app.name] = suggestions
                }
            }
        }

        return results
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
}
