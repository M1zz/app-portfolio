import Foundation

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
