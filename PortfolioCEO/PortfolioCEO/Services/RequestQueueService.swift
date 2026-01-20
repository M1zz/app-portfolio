import Foundation
import Combine

/// CEO 요구사항 큐 관리 서비스
class RequestQueueService: ObservableObject {
    static let shared = RequestQueueService()

    @Published var requests: [CEORequest] = []

    private let fileManager = FileManager.default
    private var queueFileURL: URL {
        let home = fileManager.homeDirectoryForCurrentUser
        return home
            .appendingPathComponent("Documents/workspace/code/app-portfolio")
            .appendingPathComponent("requests-queue.json")
    }

    private init() {
        loadQueue()
    }

    // MARK: - Public Methods

    /// 새 요청 추가
    func addRequest(_ request: CEORequest) {
        var newRequest = request
        newRequest.id = "req-\(UUID().uuidString.prefix(8))"
        newRequest.timestamp = Date()
        newRequest.status = "pending"

        requests.append(newRequest)
        saveQueue()

        print("✅ 요청 저장됨: \(newRequest.id ?? "unknown") - \(newRequest.title ?? "제목 없음")")
    }

    /// 빠른 메모 추가
    func addQuickNote(appName: String, content: String) {
        let note = CEORequest(
            type: "note",
            appName: appName,
            title: nil,
            description: content,
            priority: nil
        )
        addRequest(note)
    }

    /// 큐 새로고침
    func loadQueue() {
        guard fileManager.fileExists(atPath: queueFileURL.path) else {
            createEmptyQueue()
            return
        }

        do {
            let data = try Data(contentsOf: queueFileURL)
            let queue = try JSONDecoder().decode(RequestQueue.self, from: data)

            DispatchQueue.main.async {
                self.requests = queue.requests
            }

            let pending = queue.requests.filter { $0.status == "pending" }.count
            print("✅ 요청 큐 로드: \(pending)개 대기 중")

        } catch {
            print("❌ 요청 큐 로드 실패: \(error)")
        }
    }

    // MARK: - Private Methods

    private func saveQueue() {
        let queue = RequestQueue(requests: requests)

        do {
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            encoder.dateEncodingStrategy = .iso8601

            let data = try encoder.encode(queue)
            try data.write(to: queueFileURL, options: [.atomic])

            print("✅ 요청 큐 저장 완료")

        } catch {
            print("❌ 요청 큐 저장 실패: \(error)")
        }
    }

    private func createEmptyQueue() {
        let emptyQueue = RequestQueue(requests: [])

        do {
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted]
            let data = try encoder.encode(emptyQueue)
            try data.write(to: queueFileURL, options: [.atomic])

            print("✅ 빈 요청 큐 생성")

        } catch {
            print("❌ 요청 큐 생성 실패: \(error)")
        }
    }
}

// MARK: - Models

struct RequestQueue: Codable {
    var lastUpdated: Date = Date()
    var requests: [CEORequest]
}

struct CEORequest: Identifiable, Codable {
    var id: String?
    var timestamp: Date?
    var type: String // "new-task", "bug-report", "note"
    var appName: String
    var title: String?
    var description: String?
    var priority: String? // "high", "medium", "low"
    var targetVersion: String?
    var severity: String? // for bug-report: "high", "medium", "low"
    var status: String? // "pending", "processed"

    // Processing info
    var processedAt: Date?
}
