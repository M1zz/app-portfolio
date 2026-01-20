import Foundation
import Combine

/// Portfolio 데이터를 관리하는 서비스
/// JSON 파일을 읽고 실시간으로 감시
class PortfolioService: ObservableObject {
    static let shared = PortfolioService()

    @Published var apps: [AppModel] = []
    @Published var portfolio: Portfolio?
    @Published var isLoading = false
    @Published var error: Error?
    @Published var lastUpdated: Date?

    private var fileMonitor: DispatchSourceFileSystemObject?
    private let fileManager = FileManager.default

    // 포트폴리오 디렉토리 경로 (실제 프로젝트 폴더)
    private var portfolioPath: URL {
        let home = fileManager.homeDirectoryForCurrentUser
        let projectPath = home
            .appendingPathComponent("Documents/workspace/code/app-portfolio")

        // 초기화 시 필요한 폴더 생성
        let appsDir = projectPath.appendingPathComponent("apps")
        if !fileManager.fileExists(atPath: appsDir.path) {
            try? fileManager.createDirectory(at: appsDir, withIntermediateDirectories: true)
            print("📁 apps 폴더 생성: \(appsDir.path)")
        }
        return projectPath
    }

    private var appsDirectory: URL {
        portfolioPath.appendingPathComponent("apps")
    }

    private var summaryFile: URL {
        portfolioPath.appendingPathComponent("portfolio-summary.json")
    }

    private init() {
        loadPortfolio()
        startMonitoring()
    }

    deinit {
        stopMonitoring()
    }

    // MARK: - Public Methods

    func loadPortfolio() {
        isLoading = true
        error = nil

        Task {
            do {
                // 1. apps/ 폴더의 모든 JSON 파일 로드 (우선)
                let apps = try loadAllApps()

                // 2. portfolio-summary.json 로드 (옵션)
                var portfolio: Portfolio? = nil
                if fileManager.fileExists(atPath: summaryFile.path) {
                    let summaryData = try Data(contentsOf: summaryFile)
                    portfolio = try JSONDecoder().decode(Portfolio.self, from: summaryData)
                }

                await MainActor.run {
                    self.portfolio = portfolio
                    self.apps = apps
                    self.lastUpdated = Date()
                    self.isLoading = false
                }

                print("✅ 포트폴리오 로드 완료: \(apps.count)개 앱")

            } catch {
                await MainActor.run {
                    self.error = error
                    self.isLoading = false
                }
                print("❌ 포트폴리오 로드 실패: \(error)")
            }
        }
    }

    /// 모든 앱 JSON 파일 로드
    private func loadAllApps() throws -> [AppModel] {
        print("📂 앱 디렉토리 경로: \(appsDirectory.path)")

        let jsonFiles = try fileManager.contentsOfDirectory(
            at: appsDirectory,
            includingPropertiesForKeys: nil
        ).filter { $0.pathExtension == "json" }

        print("📄 발견된 JSON 파일 수: \(jsonFiles.count)")

        var loadedApps: [AppModel] = []
        var failedFiles: [String] = []

        for file in jsonFiles {
            do {
                let data = try Data(contentsOf: file)
                let app = try JSONDecoder().decode(AppModel.self, from: data)
                loadedApps.append(app)
                print("  ✅ \(file.lastPathComponent) -> \(app.name)")
            } catch {
                failedFiles.append(file.lastPathComponent)
                print("  ❌ \(file.lastPathComponent): \(error)")
            }
        }

        if !failedFiles.isEmpty {
            print("⚠️ 로드 실패한 파일들: \(failedFiles.joined(separator: ", "))")
        }

        print("📦 성공적으로 로드된 앱 수: \(loadedApps.count)")

        // 우선순위와 완료율로 정렬
        return loadedApps.sorted { app1, app2 in
            if app1.priority != app2.priority {
                // 우선순위: high > medium > low
                let priorities: [Priority: Int] = [.high: 3, .medium: 2, .low: 1]
                return (priorities[app1.priority] ?? 0) > (priorities[app2.priority] ?? 0)
            }
            // 같은 우선순위면 완료율 높은 순
            return app1.completionRate > app2.completionRate
        }
    }

    // MARK: - File Monitoring

    /// 파일 변경 감지 시작
    private func startMonitoring() {
        let appsDirectoryPath = appsDirectory.path
        let fileDescriptor = open(appsDirectoryPath, O_EVTONLY)

        guard fileDescriptor >= 0 else {
            print("❌ 파일 모니터링 시작 실패")
            return
        }

        let source = DispatchSource.makeFileSystemObjectSource(
            fileDescriptor: fileDescriptor,
            eventMask: [.write, .extend, .delete, .rename],
            queue: DispatchQueue.global(qos: .background)
        )

        source.setEventHandler { [weak self] in
            print("📁 파일 변경 감지 - 포트폴리오 새로고침")
            self?.loadPortfolio()
        }

        source.setCancelHandler {
            close(fileDescriptor)
        }

        source.resume()
        self.fileMonitor = source

        print("👀 파일 감시 시작: \(appsDirectoryPath)")
    }

    private func stopMonitoring() {
        fileMonitor?.cancel()
        fileMonitor = nil
    }

    // MARK: - Computed Properties

    var highPriorityApps: [AppModel] {
        apps.filter { $0.priority == .high }
    }

    var activeApps: [AppModel] {
        apps.filter { $0.status == .active }
    }

    var pendingDecisions: Int {
        // 진행률이 낮거나 정체된 앱 개수
        apps.filter { $0.healthStatus == .critical || $0.healthStatus == .warning }.count
    }

    var totalCompletionRate: Double {
        guard !apps.isEmpty else { return 0 }
        let totalRate = apps.reduce(0.0) { $0 + $1.completionRate }
        return totalRate / Double(apps.count)
    }

    // MARK: - Workflow Status

    @Published var appWorkflowStatus: [String: AppWorkflowStatus] = [:]

    func loadWorkflowStatus() {
        var statusMap: [String: AppWorkflowStatus] = [:]

        // 1. 피드백 로드
        let feedbackCounts = loadFeedbackCounts()

        // 2. 의사결정 로드
        let decisionCounts = loadDecisionCounts()

        // 3. 모든 앱에 대해 상태 생성 (중요: 피드백/의사결정 없어도 생성)
        for app in apps {
            let appFolder = getFolderName(for: app.name)
            let feedbackCount = feedbackCounts[appFolder] ?? 0
            let decisionCount = decisionCounts[appFolder] ?? 0

            statusMap[appFolder] = AppWorkflowStatus(
                appFolder: appFolder,
                feedbackCount: feedbackCount,
                pendingDecisionCount: decisionCount
            )
        }

        DispatchQueue.main.async {
            self.appWorkflowStatus = statusMap
        }

        print("📊 워크플로우 상태 로드 완료: \(statusMap.count)개 앱")
        print("   - 피드백 필요: \(statusMap.filter { $0.value.feedbackCount == 0 && $0.value.pendingDecisionCount == 0 }.count)개")
        print("   - 피드백 분석중: \(statusMap.filter { $0.value.feedbackCount > 0 && $0.value.pendingDecisionCount == 0 }.count)개")
        print("   - 의사결정 대기: \(statusMap.filter { $0.value.pendingDecisionCount > 0 }.count)개")
    }

    func getFolderName(for appName: String) -> String {
        let mapping: [String: String] = [
            "클립키보드": "clip-keyboard",
            "나만의 버킷": "my-bucket",
            "버킷 클라임": "bucket-climb",
            "데일리 트래커": "daily-tracker",
            "포트폴리오 CEO": "portfolioceo",
            "바미로그": "bami-log",
            "쿨타임": "cooltime",
            "오늘의 주접": "daily-compliment",
            "돈꼬마트": "donkko-mart",
            "두 번 알림": "double-reminder",
            "잘 싸워보세": "fight-well",
            "외국어는 언어다": "foreign-is-language",
            "인생 맛집": "life-restaurant",
            "세끼": "three-meals",
            "픽셀 미미": "pixel-mimi",
            "포항 어드벤쳐": "pohang-adventure",
            "확률계산기": "probability-calculator",
            "퀴즈": "quiz",
            "욕망의 무지개": "rainbow-of-desire",
            "라포 맵": "rapport-map",
            "리바운드 저널": "rebound-journal",
            "릴렉스 온": "relax-on",
            "내마음에저장": "save-in-my-heart",
            "일정비서": "schedule-assistant",
            "공유일 설계자": "shared-day-designer",
            "속삭": "whisper"
        ]
        return mapping[appName] ?? appName.lowercased()
    }

    private func loadFeedbackCounts() -> [String: Int] {
        var counts: [String: Int] = [:]

        let notesDirectory = fileManager.homeDirectoryForCurrentUser
            .appendingPathComponent("Documents/project-notes")

        guard fileManager.fileExists(atPath: notesDirectory.path) else {
            return counts
        }

        do {
            let files = try fileManager.contentsOfDirectory(
                at: notesDirectory,
                includingPropertiesForKeys: nil
            ).filter { $0.pathExtension == "json" }

            for file in files {
                let appFolder = file.deletingPathExtension().lastPathComponent
                let data = try Data(contentsOf: file)

                if let feedbacks = try JSONSerialization.jsonObject(with: data) as? [[String: Any]] {
                    let activeFeedbacks = feedbacks.filter { feedback in
                        if let status = feedback["status"] as? String {
                            return status == "대기" || status == "처리중"
                        }
                        return false
                    }
                    counts[appFolder] = activeFeedbacks.count
                }
            }
        } catch {
            print("❌ 피드백 로드 실패: \(error)")
        }

        return counts
    }

    private func loadDecisionCounts() -> [String: Int] {
        var counts: [String: Int] = [:]

        let decisionsFile = portfolioPath.appendingPathComponent("decisions-queue.json")

        guard fileManager.fileExists(atPath: decisionsFile.path) else {
            return counts
        }

        do {
            let data = try Data(contentsOf: decisionsFile)
            let queue = try JSONDecoder().decode(PlanningDecisionQueue.self, from: data)

            for decision in queue.pendingDecisions {
                counts[decision.appFolder, default: 0] += 1
            }
        } catch {
            print("❌ 의사결정 로드 실패: \(error)")
        }

        return counts
    }

    func appsNeedingFeedback() -> [String] {
        return appWorkflowStatus.filter { $0.value.feedbackCount == 0 }
            .map { $0.key }
            .sorted()
    }

    func appsNeedingDecision() -> [String] {
        return appWorkflowStatus.filter { $0.value.pendingDecisionCount > 0 }
            .map { $0.key }
            .sorted()
    }

    func appsWithActiveFeedback() -> [String] {
        return appWorkflowStatus.filter { $0.value.feedbackCount > 0 && $0.value.pendingDecisionCount == 0 }
            .map { $0.key }
            .sorted()
    }

    // MARK: - Helper Methods

    func app(named name: String) -> AppModel? {
        apps.first { $0.name == name }
    }

    // MARK: - Create App

    func createApp(
        name: String,
        nameEn: String,
        bundleId: String,
        currentVersion: String,
        status: AppStatus,
        priority: Priority,
        minimumOS: String? = nil,
        localProjectPath: String? = nil,
        githubRepo: String? = nil,
        appStoreUrl: String? = nil
    ) -> Bool {
        let appFolder = getFolderName(for: name)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        // 이미 존재하는 앱인지 확인
        if fileManager.fileExists(atPath: jsonFile.path) {
            print("❌ 이미 존재하는 앱입니다: \(name)")
            return false
        }

        // 새 앱 JSON 생성
        var json: [String: Any] = [
            "name": name,
            "nameEn": nameEn,
            "bundleId": bundleId,
            "currentVersion": currentVersion,
            "status": status.rawValue,
            "priority": priority.rawValue,
            "stats": [
                "totalTasks": 0,
                "done": 0,
                "inProgress": 0,
                "notStarted": 0
            ],
            "nextTasks": [],
            "allTasks": [],
            "sharedModules": [],
            "notes": "",
            "recentlyCompleted": []
        ]

        // 옵셔널 필드 추가
        if let minimumOS = minimumOS, !minimumOS.isEmpty {
            json["minimumOS"] = minimumOS
        }
        if let localProjectPath = localProjectPath, !localProjectPath.isEmpty {
            json["localProjectPath"] = localProjectPath
        }
        if let githubRepo = githubRepo, !githubRepo.isEmpty {
            json["githubRepo"] = githubRepo
        }
        if let appStoreUrl = appStoreUrl, !appStoreUrl.isEmpty {
            json["appStoreUrl"] = appStoreUrl
        }

        do {
            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: jsonFile)
            print("✅ 새 앱 생성 완료: \(name)")

            // 포트폴리오 다시 로드 (파일 모니터가 자동으로 처리하지만 즉시 반영을 위해)
            loadPortfolio()
            return true
        } catch {
            print("❌ 앱 생성 실패: \(error)")
            return false
        }
    }

    // MARK: - Delete App

    func deleteApp(appName: String) -> Bool {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 삭제할 앱을 찾을 수 없습니다: \(appName)")
            return false
        }

        do {
            try fileManager.removeItem(at: jsonFile)
            print("✅ 앱 삭제 완료: \(appName)")

            // 포트폴리오 다시 로드
            loadPortfolio()
            return true
        } catch {
            print("❌ 앱 삭제 실패: \(error)")
            return false
        }
    }

    // MARK: - Update Project Info

    func updateProjectInfo(
        appName: String,
        newName: String? = nil,
        newNameEn: String? = nil,
        localProjectPath: String?,
        githubRepo: String?,
        appStoreUrl: String?,
        minimumOS: String?
    ) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ JSON 파일을 찾을 수 없습니다: \(jsonFile.path)")
            return
        }

        do {
            // 1. 기존 JSON 읽기
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as! [String: Any]

            // 2. 필드 업데이트
            if let newName = newName, !newName.isEmpty {
                json["name"] = newName
            }
            if let newNameEn = newNameEn, !newNameEn.isEmpty {
                json["nameEn"] = newNameEn
            }
            if let localProjectPath = localProjectPath, !localProjectPath.isEmpty {
                json["localProjectPath"] = localProjectPath
            }
            if let githubRepo = githubRepo, !githubRepo.isEmpty {
                json["githubRepo"] = githubRepo
            }
            if let appStoreUrl = appStoreUrl, !appStoreUrl.isEmpty {
                json["appStoreUrl"] = appStoreUrl
            }
            if let minimumOS = minimumOS, !minimumOS.isEmpty {
                json["minimumOS"] = minimumOS
            }

            // 3. JSON 파일에 저장
            let updatedData = try JSONSerialization.data(withJSONObject: json, options: .prettyPrinted)
            try updatedData.write(to: jsonFile)

            print("✅ 프로젝트 정보 저장 완료: \(appName)")

            // 4. 포트폴리오 다시 로드
            loadPortfolio()

        } catch {
            print("❌ 프로젝트 정보 저장 실패: \(error)")
        }
    }

    func generateBriefing() {
        // CEO 브리핑 생성 (Claude CLI 호출)
        let task = Process()
        task.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        task.arguments = ["bash", "-c", "cd '\(portfolioPath.path)' && ./scripts/ceo-daily-briefing.sh"]

        do {
            try task.run()
            print("📊 브리핑 생성 시작...")
        } catch {
            print("❌ 브리핑 생성 실패: \(error)")
        }
    }

    func openInTerminal(script: String) {
        // 터미널에서 스크립트 실행
        let command = "cd '\(portfolioPath.path)' && ./scripts/\(script)"
        let appleScript = """
        tell application "Terminal"
            activate
            do script "\(command)"
        end tell
        """

        if let script = NSAppleScript(source: appleScript) {
            var error: NSDictionary?
            script.executeAndReturnError(&error)

            if let error = error {
                print("❌ 터미널 실행 실패: \(error)")
            }
        }
    }
}
