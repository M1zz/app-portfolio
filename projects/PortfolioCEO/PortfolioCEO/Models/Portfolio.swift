import Foundation

struct Portfolio: Codable {
    let lastUpdated: String
    let totalApps: Int
    let overview: Overview
    let apps: [PortfolioApp]
}

struct Overview: Codable {
    let active: Int
    let planning: Int
    let highPriority: Int
    let totalTasks: Int
    let totalDone: Int
    let totalInProgress: Int
    let totalNotStarted: Int

    var completionRate: Double {
        guard totalTasks > 0 else { return 0 }
        return Double(totalDone) / Double(totalTasks) * 100
    }
}

struct PortfolioApp: Codable, Identifiable {
    let id = UUID()
    let name: String
    let nameEn: String
    let file: String
    let currentVersion: String
    let status: String
    let priority: String
    let stats: TaskStats
    let nextTasks: [String]

    enum CodingKeys: String, CodingKey {
        case name, nameEn, file, currentVersion
        case status, priority, stats, nextTasks
    }
}

// MARK: - CEO Briefing Models
struct CEOBriefing: Identifiable, Codable {
    let id = UUID()
    let date: Date
    let summary: ExecutiveSummary
    let urgentDecisions: [Decision]
    let topPriorityApps: [AppBriefingStatus]
    let suggestions: [Suggestion]
    let risks: [Risk]
    let kpi: KPI

    enum CodingKeys: String, CodingKey {
        case date, summary, urgentDecisions
        case topPriorityApps, suggestions, risks, kpi
    }
}

struct ExecutiveSummary: Codable {
    let completedYesterday: Int
    let focusToday: String
    let attentionNeeded: String
}

struct Decision: Identifiable, Codable {
    let id = UUID()
    let appName: String
    let issue: String
    let options: [DecisionOption]
    let recommendation: String
    var selected: String?

    enum CodingKeys: String, CodingKey {
        case appName, issue, options, recommendation, selected
    }
}

struct DecisionOption: Identifiable, Codable {
    let id = UUID()
    let label: String
    let description: String
    let estimatedTime: String?
    let pros: [String]?
    let cons: [String]?

    enum CodingKeys: String, CodingKey {
        case label, description, estimatedTime, pros, cons
    }
}

struct Suggestion: Identifiable, Codable {
    let id = UUID()
    let title: String
    let description: String
    let expectedEffect: String
    var approved: Bool?

    enum CodingKeys: String, CodingKey {
        case title, description, expectedEffect, approved
    }
}

struct Risk: Identifiable, Codable {
    let id = UUID()
    let appName: String
    let issue: String
    let solution: String
    var resolved: Bool?

    enum CodingKeys: String, CodingKey {
        case appName, issue, solution, resolved
    }
}

struct KPI: Codable {
    let completionRate: Double
    let inProgress: Int
    let deploymentsThisWeek: Int
    let changeFromYesterday: Double
}

struct AppBriefingStatus: Identifiable, Codable {
    let id = UUID()
    let name: String
    let completionRate: Double
    let status: String
    let nextAction: String

    enum CodingKeys: String, CodingKey {
        case name, completionRate, status, nextAction
    }
}
