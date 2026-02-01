import Foundation
import SwiftUI

// MARK: - App Model
struct AppModel: Identifiable, Codable, Hashable {
    let id: String
    let name: String
    let nameEn: String
    let bundleId: String
    let folderId: String?  // JSON 파일명 (예: clip-keyboard)
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
    let deploymentChecklists: [DeploymentChecklist]?  // 배포 체크리스트
    let versionHistory: [VersionHistory]?  // 버전 히스토리
    let appStoreMetadata: AppStoreMetadata?  // 앱스토어 메타데이터
    let screenshots: ScreenshotInfo?  // 스크린샷 정보
    let deploymentReminder: DeploymentReminder?  // 배포 알림 설정
    let buildAutomation: BuildAutomation?  // 빌드 자동화 설정
    let vision: AppVision?  // 앱 비전 및 컨셉

    enum CodingKeys: String, CodingKey {
        case name, nameEn, bundleId, folderId, currentVersion
        case status, priority, minimumOS, sharedModules
        case appStoreUrl, githubRepo, localProjectPath, stats
        case nextTasks, recentlyCompleted, allTasks, notes, team, categories, price, releaseNotes, deploymentChecklists, versionHistory, appStoreMetadata, screenshots, deploymentReminder, buildAutomation, vision
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)

        self.name = try container.decode(String.self, forKey: .name)
        self.nameEn = try container.decode(String.self, forKey: .nameEn)
        self.bundleId = try container.decode(String.self, forKey: .bundleId)
        self.folderId = try container.decodeIfPresent(String.self, forKey: .folderId)

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
        self.deploymentChecklists = try container.decodeIfPresent([DeploymentChecklist].self, forKey: .deploymentChecklists)
        self.versionHistory = try container.decodeIfPresent([VersionHistory].self, forKey: .versionHistory)
        self.appStoreMetadata = try container.decodeIfPresent(AppStoreMetadata.self, forKey: .appStoreMetadata)
        self.screenshots = try container.decodeIfPresent(ScreenshotInfo.self, forKey: .screenshots)
        self.deploymentReminder = try container.decodeIfPresent(DeploymentReminder.self, forKey: .deploymentReminder)
        self.buildAutomation = try container.decodeIfPresent(BuildAutomation.self, forKey: .buildAutomation)
        self.vision = try container.decodeIfPresent(AppVision.self, forKey: .vision)
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
    let todo: Int
    let notStarted: Int

    var completionRate: Double {
        guard totalTasks > 0 else { return 0 }
        return Double(done) / Double(totalTasks) * 100
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        totalTasks = try container.decode(Int.self, forKey: .totalTasks)
        done = try container.decode(Int.self, forKey: .done)
        inProgress = try container.decode(Int.self, forKey: .inProgress)
        todo = try container.decodeIfPresent(Int.self, forKey: .todo) ?? 0
        notStarted = try container.decode(Int.self, forKey: .notStarted)
    }
}

// MARK: - Feature Metadata
struct FeatureMetadata: Codable, Hashable {
    let description: String?        // 상세 설명
    let category: String?           // 카테고리 (핵심기능, 보안, 커스터마이징 등)
    let userValue: String?          // 사용자 가치
    let technicalNotes: String?     // 기술 노트
    let relatedTasks: [String]?     // 관련 태스크

    // 추가 필드 (20년차 기획자 관점)
    let usageScenario: String?      // 언제 사용하는가
    let problemSolved: String?      // 어떤 문제 해결
    let userBenefit: String?        // 구체적 이득

    init(
        description: String? = nil,
        category: String? = nil,
        userValue: String? = nil,
        technicalNotes: String? = nil,
        relatedTasks: [String]? = nil,
        usageScenario: String? = nil,
        problemSolved: String? = nil,
        userBenefit: String? = nil
    ) {
        self.description = description
        self.category = category
        self.userValue = userValue
        self.technicalNotes = technicalNotes
        self.relatedTasks = relatedTasks
        self.usageScenario = usageScenario
        self.problemSolved = problemSolved
        self.userBenefit = userBenefit
    }
}

struct AppTask: Identifiable, Codable, Hashable {
    let id = UUID()
    let name: String
    let status: TaskStatus
    let targetDate: String?
    let targetVersion: String?
    var labels: [String]?
    var featureMetadata: FeatureMetadata?

    enum CodingKeys: String, CodingKey {
        case name, status, targetDate, targetVersion, labels, featureMetadata
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.name = try container.decode(String.self, forKey: .name)
        self.status = try container.decode(TaskStatus.self, forKey: .status)
        self.targetDate = try container.decodeIfPresent(String.self, forKey: .targetDate)
        self.targetVersion = try container.decodeIfPresent(String.self, forKey: .targetVersion)
        self.labels = try container.decodeIfPresent([String].self, forKey: .labels)
        self.featureMetadata = try container.decodeIfPresent(FeatureMetadata.self, forKey: .featureMetadata)
    }

    init(name: String, status: TaskStatus, targetDate: String? = nil, targetVersion: String? = nil, labels: [String]? = nil, featureMetadata: FeatureMetadata? = nil) {
        self.name = name
        self.status = status
        self.targetDate = targetDate
        self.targetVersion = targetVersion
        self.labels = labels
        self.featureMetadata = featureMetadata
    }

    /// targetDate 문자열을 Date로 파싱 (ISO "2026-02-15" 또는 텍스트 "November 28, 2025" 형식 지원)
    var parsedTargetDate: Date? {
        guard let dateStr = targetDate else { return nil }

        // ISO 형식: "2026-02-15"
        let isoFormatter = DateFormatter()
        isoFormatter.dateFormat = "yyyy-MM-dd"
        if let date = isoFormatter.date(from: dateStr) {
            return date
        }

        // 텍스트 형식: "November 28, 2025"
        let textFormatter = DateFormatter()
        textFormatter.dateFormat = "MMMM d, yyyy"
        textFormatter.locale = Locale(identifier: "en_US")
        if let date = textFormatter.date(from: dateStr) {
            return date
        }

        // 다른 텍스트 형식: "November 28, 2025" 변형들
        textFormatter.dateFormat = "MMMM dd, yyyy"
        if let date = textFormatter.date(from: dateStr) {
            return date
        }

        return nil
    }
}

enum TaskStatus: String, Codable {
    case done
    case inProgress = "in-progress"
    case todo
    case notStarted = "not-started"

    var displayName: String {
        switch self {
        case .done: return "완료"
        case .inProgress: return "진행 중"
        case .todo: return "진행전"
        case .notStarted: return "대기"
        }
    }

    var color: Color {
        switch self {
        case .done: return .green
        case .inProgress: return .orange
        case .todo: return .blue
        case .notStarted: return .gray
        }
    }
}

// MARK: - Computed Properties
extension AppModel {
    var completionRate: Double {
        stats.completionRate
    }

    /// 진행전 태스크 수 (todo 상태 + 하위 호환: not-started 중 목표가 있는 태스크)
    var todoCount: Int {
        allTasks.filter { task in
            task.status == .todo ||
            (task.status == .notStarted && (task.targetDate != nil || task.targetVersion != nil))
        }.count
    }

    /// 대기(백로그) 태스크 수
    var backlogCount: Int {
        allTasks.filter { task in
            task.status == .notStarted && task.targetDate == nil && task.targetVersion == nil
        }.count
    }

    /// 이번 빌드 완료 태스크 수 (currentVersion과 같은 targetVersion)
    var currentBuildDoneCount: Int {
        currentBuildDoneTasks.count
    }

    /// 이번 빌드 완료 태스크 목록
    var currentBuildDoneTasks: [AppTask] {
        allTasks.filter { task in
            guard task.status == .done else { return false }
            // targetVersion이 현재 버전과 같으면 이번 빌드 완료
            if let targetVersion = task.targetVersion {
                return targetVersion == currentVersion
            }
            // targetVersion 없으면 이번 빌드로 간주
            return true
        }
    }

    /// 이전 완료 태스크 수 (이전 버전의 완료 태스크)
    var previousDoneCount: Int {
        previousDoneTasks.count
    }

    /// 이전 완료 태스크 목록 (currentVersion보다 이전 targetVersion)
    var previousDoneTasks: [AppTask] {
        allTasks.filter { task in
            guard task.status == .done else { return false }
            guard let targetVersion = task.targetVersion else {
                return false  // 버전 없으면 이전 완료 아님
            }
            // targetVersion이 현재 버전과 다르면 이전 완료
            return targetVersion != currentVersion
        }
    }

    /// 전체 완료 수 (필터 없음)
    var totalDoneCount: Int {
        allTasks.filter { $0.status == .done }.count
    }

    // 하위 호환성을 위한 별칭
    var recentDoneCount: Int { currentBuildDoneCount }
    var recentDoneTasks: [AppTask] { currentBuildDoneTasks }
    var archivedDoneCount: Int { previousDoneCount }
    var archivedDoneTasks: [AppTask] { previousDoneTasks }

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

    /// 피쳐로 라벨링된 태스크만 필터
    var features: [AppTask] {
        allTasks.filter { $0.labels?.contains("feature") ?? false }
    }

    /// 카테고리별 피처 그룹핑
    var featuresByCategory: [String: [AppTask]] {
        Dictionary(grouping: features) {
            $0.featureMetadata?.category ?? "기타"
        }
    }

    /// 사용 가능한 모든 피처 카테고리
    var featureCategories: [String] {
        Array(Set(features.compactMap { $0.featureMetadata?.category })).sorted()
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

// MARK: - Deployment Reminder Models

struct DeploymentReminder: Codable, Hashable {
    var enabled: Bool
    var reminderDays: Int  // N일마다 알림
    var lastDeploymentDate: Date?
    var nextPlannedDate: Date?
    var updateCycle: UpdateCycle

    init(enabled: Bool = false, reminderDays: Int = 30, lastDeploymentDate: Date? = nil, nextPlannedDate: Date? = nil, updateCycle: UpdateCycle = .monthly) {
        self.enabled = enabled
        self.reminderDays = reminderDays
        self.lastDeploymentDate = lastDeploymentDate
        self.nextPlannedDate = nextPlannedDate
        self.updateCycle = updateCycle
    }

    var daysSinceLastDeployment: Int? {
        guard let lastDate = lastDeploymentDate else { return nil }
        return Calendar.current.dateComponents([.day], from: lastDate, to: Date()).day
    }

    var daysUntilNextPlanned: Int? {
        guard let nextDate = nextPlannedDate else { return nil }
        return Calendar.current.dateComponents([.day], from: Date(), to: nextDate).day
    }

    var shouldRemind: Bool {
        guard enabled else { return false }
        guard let days = daysSinceLastDeployment else { return false }
        return days >= reminderDays
    }
}

enum UpdateCycle: String, Codable, CaseIterable {
    case weekly = "주간"
    case biweekly = "격주"
    case monthly = "월간"
    case quarterly = "분기별"
    case adhoc = "비정기"

    var days: Int {
        switch self {
        case .weekly: return 7
        case .biweekly: return 14
        case .monthly: return 30
        case .quarterly: return 90
        case .adhoc: return 0
        }
    }
}

// MARK: - Screenshot Models

struct ScreenshotInfo: Codable, Hashable {
    var folderPath: String?
    var devices: [DeviceScreenshot]

    init(folderPath: String? = nil, devices: [DeviceScreenshot] = DeviceScreenshot.defaultDevices()) {
        self.folderPath = folderPath
        self.devices = devices
    }
}

struct DeviceScreenshot: Identifiable, Codable, Hashable {
    let id: String
    var deviceType: String
    var isReady: Bool
    var count: Int

    init(id: String = UUID().uuidString, deviceType: String, isReady: Bool = false, count: Int = 0) {
        self.id = id
        self.deviceType = deviceType
        self.isReady = isReady
        self.count = count
    }

    static func defaultDevices() -> [DeviceScreenshot] {
        [
            DeviceScreenshot(deviceType: "6.7\" iPhone"),
            DeviceScreenshot(deviceType: "6.5\" iPhone"),
            DeviceScreenshot(deviceType: "5.5\" iPhone"),
            DeviceScreenshot(deviceType: "12.9\" iPad Pro"),
            DeviceScreenshot(deviceType: "11\" iPad Pro")
        ]
    }
}

// MARK: - App Store Metadata Models

struct AppStoreMetadata: Codable, Hashable {
    var descriptionKo: String
    var descriptionEn: String
    var keywords: [String]
    var promotionalText: String
    var supportUrl: String?
    var privacyUrl: String?
    var ageRating: String?
    var primaryCategory: String?
    var secondaryCategory: String?

    init(descriptionKo: String = "", descriptionEn: String = "", keywords: [String] = [], promotionalText: String = "", supportUrl: String? = nil, privacyUrl: String? = nil, ageRating: String? = nil, primaryCategory: String? = nil, secondaryCategory: String? = nil) {
        self.descriptionKo = descriptionKo
        self.descriptionEn = descriptionEn
        self.keywords = keywords
        self.promotionalText = promotionalText
        self.supportUrl = supportUrl
        self.privacyUrl = privacyUrl
        self.ageRating = ageRating
        self.primaryCategory = primaryCategory
        self.secondaryCategory = secondaryCategory
    }
}

// MARK: - Version History Models

enum DeploymentStatus: String, Codable, CaseIterable {
    case preparing = "준비중"
    case testflight = "TestFlight"
    case review = "심사중"
    case released = "배포완료"

    var color: Color {
        switch self {
        case .preparing: return .orange
        case .testflight: return .blue
        case .review: return .purple
        case .released: return .green
        }
    }

    var icon: String {
        switch self {
        case .preparing: return "wrench.and.screwdriver"
        case .testflight: return "airplane"
        case .review: return "hourglass"
        case .released: return "checkmark.circle.fill"
        }
    }
}

struct VersionHistory: Identifiable, Codable, Hashable {
    let id: String
    let version: String
    let releaseDate: Date?
    var status: DeploymentStatus
    var changelog: String
    var appStoreUrl: String?

    init(id: String = UUID().uuidString, version: String, releaseDate: Date? = nil, status: DeploymentStatus = .preparing, changelog: String = "", appStoreUrl: String? = nil) {
        self.id = id
        self.version = version
        self.releaseDate = releaseDate
        self.status = status
        self.changelog = changelog
        self.appStoreUrl = appStoreUrl
    }
}

// MARK: - Deployment Checklist Models

struct DeploymentChecklist: Identifiable, Codable, Hashable {
    let id: String
    let version: String
    var items: [ChecklistItem]
    let createdAt: Date
    var completedAt: Date?

    init(id: String = UUID().uuidString, version: String, items: [ChecklistItem] = [], createdAt: Date = Date(), completedAt: Date? = nil) {
        self.id = id
        self.version = version
        self.items = items
        self.createdAt = createdAt
        self.completedAt = completedAt
    }

    var isCompleted: Bool {
        !items.isEmpty && items.allSatisfy { $0.isCompleted }
    }

    var progress: Double {
        guard !items.isEmpty else { return 0 }
        let completedCount = items.filter { $0.isCompleted }.count
        return Double(completedCount) / Double(items.count)
    }
}

struct ChecklistItem: Identifiable, Codable, Hashable {
    let id: String
    var title: String
    var isCompleted: Bool
    var completedAt: Date?
    var notes: String?

    init(id: String = UUID().uuidString, title: String, isCompleted: Bool = false, completedAt: Date? = nil, notes: String? = nil) {
        self.id = id
        self.title = title
        self.isCompleted = isCompleted
        self.completedAt = completedAt
        self.notes = notes
    }

    static func defaultItems() -> [ChecklistItem] {
        [
            ChecklistItem(title: "버전 번호 업데이트"),
            ChecklistItem(title: "빌드 번호 증가"),
            ChecklistItem(title: "릴리스 노트 작성 (한글/영문)"),
            ChecklistItem(title: "스크린샷 업데이트"),
            ChecklistItem(title: "앱스토어 설명 업데이트"),
            ChecklistItem(title: "TestFlight 업로드"),
            ChecklistItem(title: "내부 테스트 완료"),
            ChecklistItem(title: "베타 테스트 완료"),
            ChecklistItem(title: "App Store 심사 제출"),
            ChecklistItem(title: "최종 검토")
        ]
    }
}

// MARK: - Build Automation Models

struct BuildAutomation: Codable, Hashable {
    var buildNumber: Int
    var autoincrementEnabled: Bool
    var xcodeProjectPath: String?
    var buildScripts: [BuildScript]
    var lastBuildDate: Date?

    init(buildNumber: Int = 1, autoincrementEnabled: Bool = false, xcodeProjectPath: String? = nil, buildScripts: [BuildScript] = [], lastBuildDate: Date? = nil) {
        self.buildNumber = buildNumber
        self.autoincrementEnabled = autoincrementEnabled
        self.xcodeProjectPath = xcodeProjectPath
        self.buildScripts = buildScripts
        self.lastBuildDate = lastBuildDate
    }

    var hasRecentBuild: Bool {
        guard let lastBuild = lastBuildDate else { return false }
        let daysSince = Calendar.current.dateComponents([.day], from: lastBuild, to: Date()).day ?? 0
        return daysSince < 7
    }
}

struct BuildScript: Identifiable, Codable, Hashable {
    let id: String
    var name: String
    var script: String
    var phase: BuildPhase
    var enabled: Bool

    init(id: String = UUID().uuidString, name: String, script: String, phase: BuildPhase, enabled: Bool = true) {
        self.id = id
        self.name = name
        self.script = script
        self.phase = phase
        self.enabled = enabled
    }

    static func defaultScripts() -> [BuildScript] {
        [
            BuildScript(
                name: "빌드 번호 자동 증가",
                script: """
                # 빌드 번호 자동 증가
                buildNumber=$(/usr/libexec/PlistBuddy -c "Print CFBundleVersion" "${INFOPLIST_FILE}")
                buildNumber=$(($buildNumber + 1))
                /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $buildNumber" "${INFOPLIST_FILE}"
                echo "Build number: $buildNumber"
                """,
                phase: .preBuild
            ),
            BuildScript(
                name: "빌드 완료 알림",
                script: """
                # 빌드 완료 알림
                osascript -e 'display notification "빌드가 완료되었습니다." with title "Xcode"'
                """,
                phase: .postBuild
            )
        ]
    }
}

enum BuildPhase: String, Codable, CaseIterable {
    case preBuild = "빌드 전"
    case postBuild = "빌드 후"

    var description: String {
        switch self {
        case .preBuild:
            return "Xcode 빌드 시작 전에 실행됩니다"
        case .postBuild:
            return "Xcode 빌드 완료 후에 실행됩니다"
        }
    }
}

// MARK: - App Vision Models

struct AppVision: Codable, Hashable {
    var tagline: String?          // 한 줄 요약 (예: "원탭의 힘")
    var coreValue: String?        // 핵심 가치 (예: "시간 절약을 숫자로 보여주는 성취감")
    var targetUsers: String?      // 타겟 사용자 (예: "반복적인 텍스트를 자주 입력하는 직장인")
    var uniqueSellingPoint: String?  // 차별화 포인트
    var conceptDescription: String?  // 컨셉 상세 설명 (마크다운 지원)
    var designPrinciples: [String]?  // 디자인 원칙들
    var userExperienceGoals: [String]?  // 사용자 경험 목표
    var lastUpdated: Date?

    init(tagline: String? = nil, coreValue: String? = nil, targetUsers: String? = nil,
         uniqueSellingPoint: String? = nil, conceptDescription: String? = nil,
         designPrinciples: [String]? = nil, userExperienceGoals: [String]? = nil,
         lastUpdated: Date? = nil) {
        self.tagline = tagline
        self.coreValue = coreValue
        self.targetUsers = targetUsers
        self.uniqueSellingPoint = uniqueSellingPoint
        self.conceptDescription = conceptDescription
        self.designPrinciples = designPrinciples
        self.userExperienceGoals = userExperienceGoals
        self.lastUpdated = lastUpdated
    }
}
