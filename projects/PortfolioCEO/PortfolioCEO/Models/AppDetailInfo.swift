import Foundation
import SwiftUI

// MARK: - Project Note (피드백/메모)

struct ProjectNote: Identifiable, Codable {
    let id: String
    var content: String
    var status: NoteStatus
    var createdAt: Date
    var completedAt: Date?
    var completedVersion: String?

    init(id: String = UUID().uuidString, content: String, status: NoteStatus = .pending, createdAt: Date = Date(), completedAt: Date? = nil, completedVersion: String? = nil) {
        self.id = id
        self.content = content
        self.status = status
        self.createdAt = createdAt
        self.completedAt = completedAt
        self.completedVersion = completedVersion
    }
}

enum NoteStatus: String, Codable {
    case pending = "처리 전"
    case proposed = "제안 완료"
    case completed = "처리 완료"

    // 기존 데이터 호환성을 위한 커스텀 디코딩
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)

        // 기존 값들을 새로운 값으로 매핑
        switch rawValue {
        case "처리 전", "피드백 필요", "대기", "pending":
            self = .pending
        case "제안 완료", "분석중", "처리중", "의사결정", "테스트 중", "proposed":
            self = .proposed
        case "처리 완료", "배포완료", "처리됨", "완료", "completed":
            self = .completed
        default:
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Unknown status value: \(rawValue)"
            )
        }
    }

    var color: Color {
        switch self {
        case .pending: return .orange
        case .proposed: return .blue
        case .completed: return .green
        }
    }

    var icon: String {
        switch self {
        case .pending: return "exclamationmark.bubble.fill"
        case .proposed: return "lightbulb.fill"
        case .completed: return "checkmark.seal.fill"
        }
    }
}

// PlanningFeature is defined in PlanningSectionView.swift

// MARK: - App Detail Info (Claude 문서 생성용)

struct AppDetailInfo: Identifiable, Codable {
    var id: String { appFolder }

    let appFolder: String      // "double-reminder"
    var sourcePath: String     // "../DoubleReminder" 또는 "없음"
    var description: String    // 앱 설명
    var mainFeatures: [String] // 주요 기능 목록
    var techStack: TechStack   // 기술 스택
    var constraints: [String]  // 제약사항, 주의사항
    var notes: String          // 기타 메모

    init(appFolder: String) {
        self.appFolder = appFolder
        self.sourcePath = ""
        self.description = ""
        self.mainFeatures = []
        self.techStack = TechStack()
        self.constraints = []
        self.notes = ""
    }
}

struct TechStack: Codable {
    var ui: String              // "SwiftUI" or "UIKit"
    var dataStorage: String     // "SwiftData", "Core Data", "UserDefaults"
    var platforms: [String]     // ["iOS", "watchOS", "macOS"]
    var hasWidget: Bool
    var hasWatchApp: Bool
    var hasKeyboard: Bool
    var otherFrameworks: [String] // ["CloudKit", "WidgetKit", "Vision"]

    init() {
        self.ui = "SwiftUI"
        self.dataStorage = ""
        self.platforms = ["iOS"]
        self.hasWidget = false
        self.hasWatchApp = false
        self.hasKeyboard = false
        self.otherFrameworks = []
    }
}

// MARK: - Helper Extensions

extension AppDetailInfo {
    var isCompleted: Bool {
        !sourcePath.isEmpty &&
        !description.isEmpty &&
        !mainFeatures.isEmpty &&
        !techStack.ui.isEmpty
    }

    var completionRate: Double {
        var completed = 0
        let total = 7

        if !sourcePath.isEmpty { completed += 1 }
        if !description.isEmpty { completed += 1 }
        if !mainFeatures.isEmpty { completed += 1 }
        if !techStack.ui.isEmpty { completed += 1 }
        if !techStack.dataStorage.isEmpty { completed += 1 }
        if !techStack.platforms.isEmpty { completed += 1 }
        if !constraints.isEmpty || !notes.isEmpty { completed += 1 }

        return Double(completed) / Double(total) * 100
    }
}
