import Foundation
import SwiftUI

// MARK: - App Model
struct AppModel: Identifiable, Codable, Hashable {
    let id: String
    let name: String
    let nameEn: String
    let bundleId: String
    let currentVersion: String
    let status: AppStatus
    let priority: Priority
    let minimumOS: String?
    let sharedModules: [String]?
    let appStoreUrl: String?
    let githubRepo: String?
    let localProjectPath: String?  // 로컬 프로젝트 소스 경로
    let stats: TaskStats
    let nextTasks: [String]
    let recentlyCompleted: [String]?
    let allTasks: [AppTask]
    let notes: String?
    let team: TeamInfo?
    let categories: [String]?
    let price: AppPrice?  // 앱 가격 정보
    let releaseNotes: [ReleaseNote]?  // 릴리스 노트

    enum CodingKeys: String, CodingKey {
        case name, nameEn, bundleId, currentVersion
        case status, priority, minimumOS, sharedModules
        case appStoreUrl, githubRepo, localProjectPath, stats
        case nextTasks, recentlyCompleted, allTasks, notes, team, categories, price, releaseNotes
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)

        self.name = try container.decode(String.self, forKey: .name)
        self.nameEn = try container.decode(String.self, forKey: .nameEn)
        self.bundleId = try container.decode(String.self, forKey: .bundleId)

        // id는 bundleId를 사용 (고유성 보장)
        self.id = bundleId
        self.currentVersion = try container.decode(String.self, forKey: .currentVersion)
        self.status = try container.decode(AppStatus.self, forKey: .status)
        self.priority = try container.decode(Priority.self, forKey: .priority)
        self.minimumOS = try container.decodeIfPresent(String.self, forKey: .minimumOS)
        self.sharedModules = try container.decodeIfPresent([String].self, forKey: .sharedModules)
        self.appStoreUrl = try container.decodeIfPresent(String.self, forKey: .appStoreUrl)
        self.githubRepo = try container.decodeIfPresent(String.self, forKey: .githubRepo)
        self.localProjectPath = try container.decodeIfPresent(String.self, forKey: .localProjectPath)
        self.stats = try container.decode(TaskStats.self, forKey: .stats)
        self.nextTasks = try container.decode([String].self, forKey: .nextTasks)
        self.recentlyCompleted = try container.decodeIfPresent([String].self, forKey: .recentlyCompleted)
        self.allTasks = try container.decode([AppTask].self, forKey: .allTasks)
        self.notes = try container.decodeIfPresent(String.self, forKey: .notes)
        self.team = try container.decodeIfPresent(TeamInfo.self, forKey: .team)
        self.categories = try container.decodeIfPresent([String].self, forKey: .categories)
        self.price = try container.decodeIfPresent(AppPrice.self, forKey: .price)
        self.releaseNotes = try container.decodeIfPresent([ReleaseNote].self, forKey: .releaseNotes)
    }
}

// MARK: - Supporting Types
enum AppStatus: String, Codable {
    case active
    case planning
    case maintenance
    case archived

    var displayName: String {
        switch self {
        case .active: return "활성"
        case .planning: return "기획 중"
        case .maintenance: return "유지보수"
        case .archived: return "아카이브"
        }
    }

    var color: Color {
        switch self {
        case .active: return .green
        case .planning: return .yellow
        case .maintenance: return .blue
        case .archived: return .gray
        }
    }
}

enum Priority: String, Codable {
    case high
    case medium
    case low

    var displayName: String {
        switch self {
        case .high: return "높음"
        case .medium: return "중간"
        case .low: return "낮음"
        }
    }

    var color: Color {
        switch self {
        case .high: return .red
        case .medium: return .orange
        case .low: return .green
        }
    }
}

struct TaskStats: Codable, Hashable {
    let totalTasks: Int
    let done: Int
    let inProgress: Int
    let notStarted: Int

    var completionRate: Double {
        guard totalTasks > 0 else { return 0 }
        return Double(done) / Double(totalTasks) * 100
    }
}

struct AppTask: Identifiable, Codable, Hashable {
    let id = UUID()
    let name: String
    let status: TaskStatus
    let targetDate: String?
    let targetVersion: String?
    var labels: [String]?

    enum CodingKeys: String, CodingKey {
        case name, status, targetDate, targetVersion, labels
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.name = try container.decode(String.self, forKey: .name)
        self.status = try container.decode(TaskStatus.self, forKey: .status)
        self.targetDate = try container.decodeIfPresent(String.self, forKey: .targetDate)
        self.targetVersion = try container.decodeIfPresent(String.self, forKey: .targetVersion)
        self.labels = try container.decodeIfPresent([String].self, forKey: .labels)
    }

    init(name: String, status: TaskStatus, targetDate: String? = nil, targetVersion: String? = nil, labels: [String]? = nil) {
        self.name = name
        self.status = status
        self.targetDate = targetDate
        self.targetVersion = targetVersion
        self.labels = labels
    }
}

enum TaskStatus: String, Codable {
    case done
    case inProgress = "in-progress"
    case notStarted = "not-started"

    var displayName: String {
        switch self {
        case .done: return "완료"
        case .inProgress: return "진행 중"
        case .notStarted: return "대기"
        }
    }

    var color: Color {
        switch self {
        case .done: return .green
        case .inProgress: return .orange
        case .notStarted: return .gray
        }
    }
}

// MARK: - Computed Properties
extension AppModel {
    var completionRate: Double {
        stats.completionRate
    }

    var statusColor: Color {
        status.color
    }

    var priorityColor: Color {
        priority.color
    }

    var healthStatus: HealthStatus {
        switch completionRate {
        case 60...: return .healthy
        case 30..<60: return .warning
        default: return .critical
        }
    }

    var progressColor: Color {
        switch healthStatus {
        case .healthy: return .green
        case .warning: return .orange
        case .critical: return .red
        }
    }
}

enum HealthStatus {
    case healthy
    case warning
    case critical

    var icon: String {
        switch self {
        case .healthy: return "checkmark.circle.fill"
        case .warning: return "exclamationmark.triangle.fill"
        case .critical: return "xmark.circle.fill"
        }
    }

    var color: Color {
        switch self {
        case .healthy: return .green
        case .warning: return .orange
        case .critical: return .red
        }
    }
}

// MARK: - Project Info Validation

struct ProjectInfoFeedback: Identifiable {
    let id = UUID()
    let field: String
    let message: String
    let severity: FeedbackSeverity

    enum FeedbackSeverity {
        case required    // 필수 정보
        case recommended // 권장 정보
    }
}

extension AppModel {
    /// 프로젝트 필수 정보를 검증하고 피드백 반환
    var missingInfoFeedbacks: [ProjectInfoFeedback] {
        var feedbacks: [ProjectInfoFeedback] = []

        // 필수: 로컬 프로젝트 경로
        if localProjectPath == nil || localProjectPath?.isEmpty == true {
            feedbacks.append(ProjectInfoFeedback(
                field: "localProjectPath",
                message: "이 프로젝트의 소스 코드 경로가 필요합니다. 입력해주세요.",
                severity: .required
            ))
        }

        // 권장: GitHub 저장소
        if githubRepo == nil || githubRepo?.isEmpty == true {
            feedbacks.append(ProjectInfoFeedback(
                field: "githubRepo",
                message: "GitHub 저장소 URL을 입력하면 코드 관리가 더 편리합니다.",
                severity: .recommended
            ))
        }

        // 권장: App Store URL
        if appStoreUrl == nil || appStoreUrl?.isEmpty == true {
            if status == .active {
                feedbacks.append(ProjectInfoFeedback(
                    field: "appStoreUrl",
                    message: "App Store 링크를 입력하면 앱 상태를 자동으로 확인할 수 있습니다.",
                    severity: .recommended
                ))
            }
        }

        // 권장: 최소 OS 버전
        if minimumOS == nil || minimumOS?.isEmpty == true {
            feedbacks.append(ProjectInfoFeedback(
                field: "minimumOS",
                message: "최소 지원 OS 버전을 입력해주세요.",
                severity: .recommended
            ))
        }

        return feedbacks
    }

    var hasRequiredInfo: Bool {
        missingInfoFeedbacks.filter { $0.severity == .required }.isEmpty
    }
}

// MARK: - Planning Decision Queue Models

struct PlanningDecisionQueue: Codable {
    let lastUpdated: String
    var pendingDecisions: [PlanningDecision]
    var completedDecisions: [PlanningDecision]
}

struct PlanningDecision: Identifiable, Codable {
    let id: String
    let type: String
    let app: String
    let appFolder: String
    let title: String
    let description: String
    let relatedTask: String?
    let relatedFeedback: [String]
    let priority: String
    let urgency: String
    let businessImpact: String
    let currentState: String
    let proposedSolution: String
    let implementationOptions: [ImplementationOption]
    let aiRecommendation: String
    let aiReasoning: String
    var decision: String?
    let createdAt: String
}

struct ImplementationOption: Codable, Identifiable {
    var id: String { label }
    let label: String
    let description: String
    let estimatedTime: String
    let technicalDetails: [String]?
    let pros: [String]
    let cons: [String]
    let exampleTemplates: [String]?
    let exampleCategories: [String]?
    let costEstimate: String?
}

// MARK: - Priority Extension
extension PlanningDecision {
    var priorityLevel: Int {
        switch priority.lowercased() {
        case "critical": return 4
        case "high": return 3
        case "medium": return 2
        case "low": return 1
        default: return 0
        }
    }

    var urgencyLevel: Int {
        switch urgency.lowercased() {
        case "high": return 3
        case "medium": return 2
        case "low": return 1
        default: return 0
        }
    }

    var priorityColor: String {
        switch priority.lowercased() {
        case "critical": return "red"
        case "high": return "orange"
        case "medium": return "yellow"
        case "low": return "green"
        default: return "gray"
        }
    }
}

// MARK: - Workflow Status Models

struct AppWorkflowStatus {
    let appFolder: String
    let feedbackCount: Int
    let pendingDecisionCount: Int

    var currentStage: WorkflowStage {
        if pendingDecisionCount > 0 {
            return .decision
        } else if feedbackCount > 0 {
            return .feedback
        } else {
            return .ready
        }
    }

    var statusDescription: String {
        switch currentStage {
        case .ready:
            return "피드백 필요"
        case .feedback:
            return "피드백 \(feedbackCount)개"
        case .decision:
            return "의사결정 \(pendingDecisionCount)개 대기"
        }
    }
}

enum WorkflowStage: String {
    case ready = "준비"
    case feedback = "피드백"
    case decision = "의사결정"
}

// MARK: - Price Models

enum PricingModel: String, Codable, Hashable, CaseIterable {
    case free = "free"
    case oneTime = "oneTime"
    case subscription = "subscription"

    var displayName: String {
        switch self {
        case .free: return "무료"
        case .oneTime: return "일회성 결제"
        case .subscription: return "구독"
        }
    }
}

struct AppPrice: Codable, Hashable {
    var usd: Double?          // 일회성 달러 가격
    var krw: Int?             // 일회성 원화 가격
    var isFree: Bool          // 무료 앱 여부 (하위 호환)
    var pricingModel: PricingModel?  // 가격 모델
    var monthlyUSD: Double?   // 구독 월간 달러
    var monthlyKRW: Int?      // 구독 월간 원화
    var yearlyUSD: Double?    // 구독 연간 달러
    var yearlyKRW: Int?       // 구독 연간 원화

    init(usd: Double? = nil, krw: Int? = nil, isFree: Bool = true,
         pricingModel: PricingModel? = nil,
         monthlyUSD: Double? = nil, monthlyKRW: Int? = nil,
         yearlyUSD: Double? = nil, yearlyKRW: Int? = nil) {
        self.usd = usd
        self.krw = krw
        self.isFree = isFree
        self.pricingModel = pricingModel
        self.monthlyUSD = monthlyUSD
        self.monthlyKRW = monthlyKRW
        self.yearlyUSD = yearlyUSD
        self.yearlyKRW = yearlyKRW
    }

    /// 실제 가격 모델 (하위 호환: pricingModel이 nil이면 isFree로 판단)
    var resolvedPricingModel: PricingModel {
        if let model = pricingModel { return model }
        return isFree ? .free : .oneTime
    }

    var displayPrice: String {
        switch resolvedPricingModel {
        case .free:
            return "무료"
        case .oneTime:
            var parts: [String] = []
            if let usd = usd {
                parts.append("$\(String(format: "%.2f", usd))")
            }
            if let krw = krw {
                let formatter = NumberFormatter()
                formatter.numberStyle = .decimal
                if let formatted = formatter.string(from: NSNumber(value: krw)) {
                    parts.append("₩\(formatted)")
                }
            }
            return parts.isEmpty ? "가격 미정" : parts.joined(separator: " / ")
        case .subscription:
            let formatter = NumberFormatter()
            formatter.numberStyle = .decimal
            var parts: [String] = []
            if let mkrw = monthlyKRW, let formatted = formatter.string(from: NSNumber(value: mkrw)) {
                parts.append("월 ₩\(formatted)")
            } else if let musd = monthlyUSD {
                parts.append("월 $\(String(format: "%.2f", musd))")
            }
            if let ykrw = yearlyKRW, let formatted = formatter.string(from: NSNumber(value: ykrw)) {
                parts.append("연 ₩\(formatted)")
            } else if let yusd = yearlyUSD {
                parts.append("연 $\(String(format: "%.2f", yusd))")
            }
            return parts.isEmpty ? "구독 (가격 미정)" : parts.joined(separator: " / ")
        }
    }

    var usdDisplay: String {
        if resolvedPricingModel == .free { return "무료" }
        guard let usd = usd else { return "-" }
        return "$\(String(format: "%.2f", usd))"
    }

    var krwDisplay: String {
        if resolvedPricingModel == .free { return "무료" }
        guard let krw = krw else { return "-" }
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        return "₩\(formatter.string(from: NSNumber(value: krw)) ?? "\(krw)")"
    }
}

// MARK: - Team Models

struct TeamInfo: Codable, Hashable {
    let development: [TeamMember]
    let planning: [TeamMember]
    let design: [TeamMember]

    var allMembers: [TeamMember] {
        development + planning + design
    }

    var leadMembers: [TeamMember] {
        allMembers.filter { $0.isLead }
    }

    init(development: [TeamMember] = [], planning: [TeamMember] = [], design: [TeamMember] = []) {
        self.development = development
        self.planning = planning
        self.design = design
    }
}

struct TeamMember: Identifiable, Codable, Hashable {
    let id: String
    let name: String
    let role: String
    let responsibility: String
    let isLead: Bool
    let contact: String?

    init(id: String, name: String, role: String, responsibility: String, isLead: Bool = false, contact: String? = nil) {
        self.id = id
        self.name = name
        self.role = role
        self.responsibility = responsibility
        self.isLead = isLead
        self.contact = contact
    }
}

// MARK: - Release Note Models

struct ReleaseNote: Identifiable, Codable, Hashable {
    let id: String
    let version: String
    let date: Date
    var notesKo: String
    var notesEn: String

    init(id: String = UUID().uuidString, version: String, date: Date = Date(), notesKo: String = "", notesEn: String = "") {
        self.id = id
        self.version = version
        self.date = date
        self.notesKo = notesKo
        self.notesEn = notesEn
    }
}
