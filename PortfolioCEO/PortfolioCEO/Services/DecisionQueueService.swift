import Foundation
import Combine

/// CEO 결정사항 큐 관리 서비스
class DecisionQueueService: ObservableObject {
    static let shared = DecisionQueueService()

    @Published var pendingDecisions: [PlanningDecision] = []
    @Published var completedDecisions: [PlanningDecision] = []
    @Published var isLoading = false

    private let fileManager = FileManager.default
    private var queueFileURL: URL {
        let home = fileManager.homeDirectoryForCurrentUser
        return home
            .appendingPathComponent("Documents/workspace/code/app-portfolio")
            .appendingPathComponent("decisions-queue.json")
    }

    private init() {
        loadQueue()
    }

    // MARK: - Public Methods

    /// 큐 새로고침
    func loadQueue() {
        isLoading = true

        guard fileManager.fileExists(atPath: queueFileURL.path) else {
            print("⚠️ decisions-queue.json 파일이 없습니다: \(queueFileURL.path)")
            isLoading = false
            return
        }

        do {
            let data = try Data(contentsOf: queueFileURL)
            let queue = try JSONDecoder().decode(PlanningDecisionQueue.self, from: data)

            DispatchQueue.main.async {
                self.pendingDecisions = queue.pendingDecisions.sorted { d1, d2 in
                    if d1.priorityLevel != d2.priorityLevel {
                        return d1.priorityLevel > d2.priorityLevel
                    }
                    return d1.urgencyLevel > d2.urgencyLevel
                }
                self.completedDecisions = queue.completedDecisions
                self.isLoading = false
            }

            print("✅ 결정 큐 로드: \(queue.pendingDecisions.count)개 대기 중")

        } catch {
            print("❌ 결정 큐 로드 실패: \(error)")
            isLoading = false
        }
    }

    /// 의사결정 승인 (completed로 이동)
    func approveDecision(id: String, selectedOption: String) {
        guard let index = pendingDecisions.firstIndex(where: { $0.id == id }) else {
            return
        }

        var decision = pendingDecisions[index]
        decision.decision = selectedOption

        // pending에서 제거하고 completed에 추가
        pendingDecisions.remove(at: index)
        completedDecisions.append(decision)

        // 1. 관련 피드백 상태 업데이트
        updateRelatedFeedbackStatus(decision: decision)

        // 2. 태스크 생성
        createTasksFromDecision(decision: decision, selectedOption: selectedOption)

        // JSON 파일 업데이트
        saveQueue()
        print("✅ 의사결정 승인: \(id) -> \(selectedOption)")
    }

    /// 의사결정 거절 (pending으로 복귀)
    func rejectDecision(id: String) {
        guard let index = completedDecisions.firstIndex(where: { $0.id == id }) else {
            return
        }

        var decision = completedDecisions[index]
        decision.decision = nil

        // completed에서 제거하고 pending에 추가
        completedDecisions.remove(at: index)
        pendingDecisions.append(decision)

        // 우선순위로 정렬
        pendingDecisions.sort { d1, d2 in
            if d1.priorityLevel != d2.priorityLevel {
                return d1.priorityLevel > d2.priorityLevel
            }
            return d1.urgencyLevel > d2.urgencyLevel
        }

        // JSON 파일 업데이트
        saveQueue()
        print("⚠️ 의사결정 거절: \(id) - pending으로 복귀")
    }

    /// 의사결정 삭제
    func deleteDecision(id: String) {
        pendingDecisions.removeAll { $0.id == id }
        completedDecisions.removeAll { $0.id == id }

        // JSON 파일 업데이트
        saveQueue()
        print("🗑️ 의사결정 삭제: \(id)")
    }

    /// JSON 파일 저장
    private func saveQueue() {
        do {
            let queue = PlanningDecisionQueue(
                lastUpdated: ISO8601DateFormatter().string(from: Date()),
                pendingDecisions: pendingDecisions,
                completedDecisions: completedDecisions
            )

            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            let data = try encoder.encode(queue)
            try data.write(to: queueFileURL)

            print("💾 결정 큐 저장 완료")
        } catch {
            print("❌ 결정 큐 저장 실패: \(error)")
        }
    }

    // MARK: - Private Helper Methods

    /// 관련 피드백 상태를 "완료"로 업데이트
    private func updateRelatedFeedbackStatus(decision: PlanningDecision) {
        guard !decision.relatedFeedback.isEmpty else {
            print("📝 [DecisionQueueService] 관련 피드백 없음")
            return
        }

        let home = fileManager.homeDirectoryForCurrentUser
        let notesDir = home.appendingPathComponent("Documents/project-notes")

        // 앱 폴더 이름 가져오기
        let appFolder = decision.appFolder

        let feedbackFilePath = notesDir.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: feedbackFilePath.path) else {
            print("⚠️ [DecisionQueueService] 피드백 파일 없음: \(feedbackFilePath.path)")
            return
        }

        do {
            let data = try Data(contentsOf: feedbackFilePath)
            guard var feedbacksArray = try JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
                print("⚠️ [DecisionQueueService] 피드백 파일 파싱 실패")
                return
            }

            // 관련 피드백들의 상태를 "처리 완료"로 변경
            var updatedCount = 0
            for feedbackId in decision.relatedFeedback {
                if let index = feedbacksArray.firstIndex(where: { $0["id"] as? String == feedbackId }) {
                    feedbacksArray[index]["status"] = "처리 완료"
                    updatedCount += 1
                }
            }

            // 파일 저장
            let updatedData = try JSONSerialization.data(withJSONObject: feedbacksArray, options: [.prettyPrinted, .sortedKeys])
            try updatedData.write(to: feedbackFilePath)

            print("✅ [DecisionQueueService] \(updatedCount)개 피드백 상태 업데이트 완료")

        } catch {
            print("❌ [DecisionQueueService] 피드백 상태 업데이트 실패: \(error)")
        }
    }

    /// 의사결정을 기반으로 태스크 생성
    private func createTasksFromDecision(decision: PlanningDecision, selectedOption: String) {
        guard let option = decision.implementationOptions.first(where: { $0.id == selectedOption }) else {
            print("⚠️ [DecisionQueueService] 선택된 옵션을 찾을 수 없음: \(selectedOption)")
            return
        }

        let home = fileManager.homeDirectoryForCurrentUser
        let appsDir = home.appendingPathComponent("Documents/workspace/code/app-portfolio/apps")
        let appFolder = decision.appFolder
        let appFilePath = appsDir.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: appFilePath.path) else {
            print("⚠️ [DecisionQueueService] 앱 파일 없음: \(appFilePath.path)")
            return
        }

        do {
            let data = try Data(contentsOf: appFilePath)
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601

            var appData = try decoder.decode([String: AnyCodable].self, from: data)

            // tasks 배열 가져오기
            var tasks: [[String: AnyCodable]] = []
            if let existingTasks = appData["tasks"]?.value as? [[String: Any]] {
                tasks = existingTasks.map { ["string": AnyCodable($0)] }
            }

            // 새 태스크 생성
            let taskTitle = "[\(option.label)] \(decision.title)"

            let technicalDetailsText = (option.technicalDetails ?? []).enumerated().map { "\($0.offset + 1). \($0.element)" }.joined(separator: "\n")
            let prosText = (option.pros ?? []).map { "✅ \($0)" }.joined(separator: "\n")
            let consText = (option.cons ?? []).map { "⚠️ \($0)" }.joined(separator: "\n")

            let taskDescription = """
            **의사결정 결과**: \(decision.title)

            **선택된 방안**: \(option.label)
            **예상 기간**: \(option.estimatedTime)

            **설명**: \(option.description)

            **구현 내용**:
            \(technicalDetailsText)

            **장점**:
            \(prosText)

            **단점**:
            \(consText)
            """

            let newTask: [String: AnyCodable] = [
                "id": AnyCodable(UUID().uuidString),
                "title": AnyCodable(taskTitle),
                "description": AnyCodable(taskDescription),
                "status": AnyCodable("todo"),
                "priority": AnyCodable(decision.priority),
                "createdAt": AnyCodable(ISO8601DateFormatter().string(from: Date())),
                "decisionId": AnyCodable(decision.id),
                "selectedOption": AnyCodable(selectedOption)
            ]

            tasks.append(newTask)
            appData["tasks"] = AnyCodable(tasks.map { $0.mapValues { $0.value } })

            // 파일 저장
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            let updatedData = try encoder.encode(appData)
            try updatedData.write(to: appFilePath)

            print("✅ [DecisionQueueService] 태스크 생성 완료: \(taskTitle)")

        } catch {
            print("❌ [DecisionQueueService] 태스크 생성 실패: \(error)")
        }
    }
}

// MARK: - Helper Types

struct AnyCodable: Codable {
    let value: Any

    init(_ value: Any) {
        self.value = value
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()

        if let intValue = try? container.decode(Int.self) {
            value = intValue
        } else if let doubleValue = try? container.decode(Double.self) {
            value = doubleValue
        } else if let boolValue = try? container.decode(Bool.self) {
            value = boolValue
        } else if let stringValue = try? container.decode(String.self) {
            value = stringValue
        } else if let arrayValue = try? container.decode([AnyCodable].self) {
            value = arrayValue.map { $0.value }
        } else if let dictionaryValue = try? container.decode([String: AnyCodable].self) {
            value = dictionaryValue.mapValues { $0.value }
        } else {
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "Unsupported type")
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()

        if let intValue = value as? Int {
            try container.encode(intValue)
        } else if let doubleValue = value as? Double {
            try container.encode(doubleValue)
        } else if let boolValue = value as? Bool {
            try container.encode(boolValue)
        } else if let stringValue = value as? String {
            try container.encode(stringValue)
        } else if let arrayValue = value as? [Any] {
            try container.encode(arrayValue.map { AnyCodable($0) })
        } else if let dictionaryValue = value as? [String: Any] {
            try container.encode(dictionaryValue.mapValues { AnyCodable($0) })
        } else {
            throw EncodingError.invalidValue(value, EncodingError.Context(codingPath: container.codingPath, debugDescription: "Unsupported type"))
        }
    }
}
