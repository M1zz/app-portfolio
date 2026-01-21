//
//  SharedModels.swift
//  Shared between PortfolioCEO (macOS) and CEOfeedback (iOS)
//

import Foundation

// MARK: - App Summary (iOS에서 표시할 앱 정보)

struct AppSummary: Identifiable, Codable {
    var id: String { bundleId }
    let name: String
    let nameEn: String
    let bundleId: String
    let currentVersion: String
    let status: String
    let priority: String
    let stats: TaskStatsSummary
    let nextTasks: [String]

    struct TaskStatsSummary: Codable {
        let totalTasks: Int
        let done: Int
        let inProgress: Int
        let notStarted: Int

        var completionRate: Double {
            guard totalTasks > 0 else { return 0 }
            return Double(done) / Double(totalTasks) * 100
        }

        init(totalTasks: Int, done: Int, inProgress: Int, notStarted: Int) {
            self.totalTasks = totalTasks
            self.done = done
            self.inProgress = inProgress
            self.notStarted = notStarted
        }
    }

    init(name: String, nameEn: String, bundleId: String, currentVersion: String,
         status: String, priority: String, stats: TaskStatsSummary, nextTasks: [String]) {
        self.name = name
        self.nameEn = nameEn
        self.bundleId = bundleId
        self.currentVersion = currentVersion
        self.status = status
        self.priority = priority
        self.stats = stats
        self.nextTasks = nextTasks
    }
}

// MARK: - Feedback (iOS에서 작성, macOS에서 확인)

struct AppFeedback: Identifiable, Codable {
    var id: UUID
    let appBundleId: String
    let appName: String
    let content: String
    let category: FeedbackCategory
    let status: FeedbackStatus
    let createdAt: Date
    var updatedAt: Date

    enum FeedbackCategory: String, Codable, CaseIterable {
        case bug = "버그"
        case feature = "기능 제안"
        case improvement = "개선"
        case question = "질문"
        case other = "기타"
    }

    enum FeedbackStatus: String, Codable {
        case pending = "처리 전"
        case inProgress = "검토 중"
        case completed = "완료"
        case rejected = "반려"
    }

    init(appBundleId: String, appName: String, content: String, category: FeedbackCategory) {
        self.id = UUID()
        self.appBundleId = appBundleId
        self.appName = appName
        self.content = content
        self.category = category
        self.status = .pending
        self.createdAt = Date()
        self.updatedAt = Date()
    }
}

// MARK: - Sync Data Container (iCloud 동기화용)

struct SyncDataContainer: Codable {
    let lastUpdated: Date
    let apps: [AppSummary]
    var feedbacks: [AppFeedback]

    init(apps: [AppSummary], feedbacks: [AppFeedback]) {
        self.lastUpdated = Date()
        self.apps = apps
        self.feedbacks = feedbacks
    }

    // 커스텀 디코더: lastUpdated가 문자열(ISO8601)로 올 수 있음
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)

        // lastUpdated 파싱 (ISO8601 문자열 또는 Date)
        if let dateString = try? container.decode(String.self, forKey: .lastUpdated) {
            let formatter = ISO8601DateFormatter()
            self.lastUpdated = formatter.date(from: dateString) ?? Date()
        } else if let date = try? container.decode(Date.self, forKey: .lastUpdated) {
            self.lastUpdated = date
        } else {
            self.lastUpdated = Date()
        }

        self.apps = try container.decode([AppSummary].self, forKey: .apps)
        self.feedbacks = (try? container.decode([AppFeedback].self, forKey: .feedbacks)) ?? []
    }

    enum CodingKeys: String, CodingKey {
        case lastUpdated, apps, feedbacks
    }
}
