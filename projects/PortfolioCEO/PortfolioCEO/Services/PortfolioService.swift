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
    @Published var appFileModificationDates: [String: Date] = [:]  // bundleId -> 파일 수정 날짜
    @Published var availableCategories: [String] = []  // 전체 카테고리 목록

    // 버전 변경 감지
    @Published var versionChanges: [VersionChange] = []
    private var isUpdatingVersions = false  // 버전 업데이트 중 플래그

    struct VersionChange: Identifiable {
        let id = UUID()
        let appName: String
        let appFolder: String
        let currentVersion: String   // JSON에 저장된 버전
        let detectedVersion: String  // 프로젝트에서 감지된 버전
    }

    private var fileMonitor: DispatchSourceFileSystemObject?
    private let fileManager = FileManager.default

    // 포트폴리오 디렉토리 경로
    private var portfolioPath: URL {
        // 1. 사용자 설정 경로 확인 (Settings에서 설정)
        if let savedPath = UserDefaults.standard.string(forKey: "portfolioPath"),
           !savedPath.isEmpty {
            let expandedPath = NSString(string: savedPath).expandingTildeInPath
            let userPath = URL(fileURLWithPath: expandedPath)
            let userAppsDir = userPath.appendingPathComponent("apps")
            if fileManager.fileExists(atPath: userAppsDir.path) {
                print("📂 사용자 설정 경로 사용: \(userPath.path)")
                return userPath
            }
        }

        // 2. 소스 파일 기준 상대 경로 시도
        let sourceFile = URL(fileURLWithPath: #file)
        let relativePath = sourceFile
            .deletingLastPathComponent()  // Services
            .deletingLastPathComponent()  // PortfolioCEO (inner)
            .deletingLastPathComponent()  // PortfolioCEO (outer)
            .deletingLastPathComponent()  // projects

        let relativeAppsDir = relativePath.appendingPathComponent("apps")
        if fileManager.fileExists(atPath: relativeAppsDir.path) {
            print("📂 상대 경로 사용: \(relativePath.path)")
            return relativePath
        }

        // 3. Fallback: 홈 디렉토리 기반 절대 경로 (여러 경로 시도)
        let home = fileManager.homeDirectoryForCurrentUser
        let possiblePaths = [
            home.appendingPathComponent("Documents/workspace/code/app-portfolio"),
            home.appendingPathComponent("Documents/code/app-portfolio")
        ]

        for path in possiblePaths {
            let appsDir = path.appendingPathComponent("apps")
            if fileManager.fileExists(atPath: appsDir.path) {
                print("📂 절대 경로 사용: \(path.path)")
                return path
            }
        }

        // 기본값 (첫 번째 경로)
        print("📂 기본 경로 사용: \(possiblePaths[0].path)")
        return possiblePaths[0]
    }

    private var appsDirectory: URL {
        portfolioPath.appendingPathComponent("apps")
    }

    private var summaryFile: URL {
        portfolioPath.appendingPathComponent("data/portfolio-summary.json")
    }

    private var categoriesFile: URL {
        portfolioPath.appendingPathComponent("data/categories.json")
    }

    private init() {
        loadCategories()
        loadPortfolio()
        startMonitoring()
    }

    deinit {
        stopMonitoring()
    }

    // MARK: - Public Methods

    func loadPortfolio() {
        DispatchQueue.main.async {
            self.isLoading = true
            self.error = nil
        }

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

                    // 버전 변경 자동 체크 (업데이트 중이 아닐 때만)
                    if !self.isUpdatingVersions {
                        self.checkVersionChanges()
                    }

                    // iCloud 동기화 (iOS 앱용)
                    self.syncToiCloud()
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
            includingPropertiesForKeys: [.contentModificationDateKey]
        ).filter { $0.pathExtension == "json" }

        print("📄 발견된 JSON 파일 수: \(jsonFiles.count)")

        var loadedApps: [AppModel] = []
        var failedFiles: [String] = []
        var modificationDates: [String: Date] = [:]

        for file in jsonFiles {
            do {
                let data = try Data(contentsOf: file)
                let app = try JSONDecoder().decode(AppModel.self, from: data)
                loadedApps.append(app)

                // 파일 수정 날짜 저장
                if let attributes = try? fileManager.attributesOfItem(atPath: file.path),
                   let modDate = attributes[.modificationDate] as? Date {
                    modificationDates[app.bundleId] = modDate
                }

                print("  ✅ \(file.lastPathComponent) -> \(app.name)")
            } catch {
                failedFiles.append(file.lastPathComponent)
                print("  ❌ \(file.lastPathComponent): \(error)")
            }
        }

        // 메인 스레드에서 수정 날짜 업데이트
        DispatchQueue.main.async {
            self.appFileModificationDates = modificationDates
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

    private var feedbackDirectory: URL {
        // 1. portfolioPath 내의 project-notes 폴더 확인
        let inProjectPath = portfolioPath.appendingPathComponent("project-notes")
        if fileManager.fileExists(atPath: inProjectPath.path) {
            return inProjectPath
        }

        // 2. Fallback: 홈 디렉토리의 project-notes (레거시)
        let homePath = fileManager.homeDirectoryForCurrentUser
            .appendingPathComponent("Documents/code/app-portfolio/project-notes")
        return homePath
    }

    private func loadFeedbackCounts() -> [String: Int] {
        var counts: [String: Int] = [:]

        let notesDirectory = feedbackDirectory
        print("📝 피드백 경로: \(notesDirectory.path)")

        guard fileManager.fileExists(atPath: notesDirectory.path) else {
            print("⚠️ 피드백 폴더 없음")
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
                    // 활성 상태의 피드백 카운트 (처리 완료가 아닌 모든 피드백)
                    let activeStatuses = [
                        "처리 전", "피드백 필요", "대기", "pending",
                        "제안 완료", "분석중", "처리중", "의사결정", "테스트 중", "proposed"
                    ]
                    let activeFeedbacks = feedbacks.filter { feedback in
                        if let status = feedback["status"] as? String {
                            return activeStatuses.contains(status)
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

        let decisionsFile = portfolioPath.appendingPathComponent("data/decisions-queue.json")

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
        appStoreUrl: String? = nil,
        price: AppPrice? = nil
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

        // 가격 정보 추가
        if let price = price {
            var priceDict: [String: Any] = ["isFree": price.isFree]
            if let usd = price.usd {
                priceDict["usd"] = usd
            }
            if let krw = price.krw {
                priceDict["krw"] = krw
            }
            json["price"] = priceDict
        }

        do {
            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: jsonFile)
            print("✅ 새 앱 생성 완료: \(name)")

            // 포트폴리오 다시 로드 (파일 모니터가 자동으로 처리하지만 즉시 반영을 위해)
            loadPortfolio()

            // 대시보드 동기화를 위해 summary 업데이트
            updateSummary()

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

        // 파일 모니터 일시 중지
        fileMonitor?.suspend()

        do {
            // 파일 삭제
            try fileManager.removeItem(at: jsonFile)
            print("✅ 앱 삭제 완료: \(appName)")

            // UI에서 앱 제거
            DispatchQueue.main.async {
                self.apps.removeAll { $0.name == appName }
                // 파일 모니터 재개
                self.fileMonitor?.resume()
            }

            // 대시보드 동기화를 위해 summary 업데이트
            updateSummary()

            return true
        } catch {
            print("❌ 앱 삭제 실패: \(error)")
            // 파일 모니터 재개
            fileMonitor?.resume()
            return false
        }
    }

    // MARK: - Update Project Info

    func updateProjectInfo(
        appName: String,
        newName: String? = nil,
        newNameEn: String? = nil,
        currentVersion: String? = nil,
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
            if let currentVersion = currentVersion, !currentVersion.isEmpty {
                json["currentVersion"] = currentVersion
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

            // 5. 대시보드 동기화를 위해 summary 업데이트
            updateSummary()

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

    // MARK: - CloudKit Sync (iOS 앱 동기화)

    /// iOS 앱과 동기화를 위해 CloudKit에 앱 데이터 저장
    func syncToiCloud() {
        // AppModel을 AppSummary로 변환
        let appSummaries: [AppSummary] = apps.map { app in
            AppSummary(
                name: app.name,
                nameEn: app.nameEn,
                bundleId: app.bundleId,
                currentVersion: app.currentVersion,
                status: app.status.rawValue,
                priority: app.priority.rawValue,
                stats: AppSummary.TaskStatsSummary(
                    totalTasks: app.stats.totalTasks,
                    done: app.stats.done,
                    inProgress: app.stats.inProgress,
                    notStarted: app.stats.notStarted
                ),
                nextTasks: Array(app.nextTasks.prefix(5))
            )
        }

        // CloudKit에 저장
        CloudKitSyncService.shared.saveApps(appSummaries) { success, error in
            if success {
                print("☁️ CloudKit 동기화 완료: \(appSummaries.count)개 앱")
            } else {
                print("❌ CloudKit 동기화 실패: \(error ?? "알 수 없는 오류")")
            }
        }
    }

    // MARK: - Summary Update (대시보드 동기화)

    /// portfolio-summary.json 업데이트 (대시보드와 동기화)
    func updateSummary() {
        Task {
            do {
                let apps = try loadAllApps()

                // 통계 계산
                let activeCount = apps.filter { $0.status == .active }.count
                let planningCount = apps.filter { $0.status == .planning }.count
                let highPriorityCount = apps.filter { $0.priority == .high }.count

                let totalTasks = apps.reduce(0) { $0 + $1.stats.totalTasks }
                let totalDone = apps.reduce(0) { $0 + $1.stats.done }
                let totalInProgress = apps.reduce(0) { $0 + $1.stats.inProgress }
                let totalNotStarted = apps.reduce(0) { $0 + $1.stats.notStarted }

                // 앱 요약 생성
                let appsSummary: [[String: Any]] = apps.map { app in
                    [
                        "name": app.name,
                        "nameEn": app.nameEn,
                        "file": "\(getFolderName(for: app.name)).json",
                        "currentVersion": app.currentVersion,
                        "status": app.status.rawValue,
                        "priority": app.priority.rawValue,
                        "stats": [
                            "totalTasks": app.stats.totalTasks,
                            "done": app.stats.done,
                            "inProgress": app.stats.inProgress,
                            "notStarted": app.stats.notStarted
                        ],
                        "nextTasks": Array(app.nextTasks.prefix(2))
                    ]
                }

                // Summary JSON 생성
                let formatter = ISO8601DateFormatter()
                let summary: [String: Any] = [
                    "lastUpdated": formatter.string(from: Date()),
                    "totalApps": apps.count,
                    "overview": [
                        "active": activeCount,
                        "planning": planningCount,
                        "highPriority": highPriorityCount,
                        "totalTasks": totalTasks,
                        "totalDone": totalDone,
                        "totalInProgress": totalInProgress,
                        "totalNotStarted": totalNotStarted
                    ],
                    "apps": appsSummary
                ]

                // 파일 저장
                let jsonData = try JSONSerialization.data(withJSONObject: summary, options: [.prettyPrinted, .sortedKeys])
                try jsonData.write(to: summaryFile)

                print("✅ portfolio-summary.json 업데이트 완료")

            } catch {
                print("❌ Summary 업데이트 실패: \(error)")
            }
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

    // MARK: - Version Detection (프로젝트 버전 자동 감지)

    /// 모든 앱의 버전 변경 확인
    func checkVersionChanges() {
        var changes: [VersionChange] = []

        for app in apps {
            guard let localPath = app.localProjectPath, !localPath.isEmpty else { continue }

            if let detectedVersion = detectProjectVersion(localPath: localPath),
               detectedVersion != app.currentVersion {
                let appFolder = getFolderName(for: app.name)
                changes.append(VersionChange(
                    appName: app.name,
                    appFolder: appFolder,
                    currentVersion: app.currentVersion,
                    detectedVersion: detectedVersion
                ))
                print("🔄 버전 변경 감지: \(app.name) \(app.currentVersion) → \(detectedVersion)")
            }
        }

        DispatchQueue.main.async {
            self.versionChanges = changes
        }

        if changes.isEmpty {
            print("✅ 모든 앱 버전이 최신 상태입니다")
        } else {
            print("⚠️ \(changes.count)개 앱의 버전이 변경되었습니다")
        }
    }

    /// 로컬 프로젝트에서 버전 감지
    func detectProjectVersion(localPath: String) -> String? {
        // 상대 경로를 절대 경로로 변환
        let absolutePath: URL
        if localPath.hasPrefix("../") {
            absolutePath = portfolioPath.appendingPathComponent(localPath)
        } else if localPath.hasPrefix("/") {
            absolutePath = URL(fileURLWithPath: localPath)
        } else {
            absolutePath = portfolioPath.appendingPathComponent(localPath)
        }

        // .xcodeproj 폴더 찾기
        do {
            let contents = try fileManager.contentsOfDirectory(
                at: absolutePath,
                includingPropertiesForKeys: nil
            )

            for item in contents {
                if item.pathExtension == "xcodeproj" {
                    let pbxprojPath = item.appendingPathComponent("project.pbxproj")
                    if let version = extractMarketingVersion(from: pbxprojPath) {
                        return version
                    }
                }
            }
        } catch {
            print("❌ 프로젝트 폴더 접근 실패: \(absolutePath.path) - \(error)")
        }

        return nil
    }

    /// project.pbxproj에서 MARKETING_VERSION 추출
    private func extractMarketingVersion(from pbxprojPath: URL) -> String? {
        guard let content = try? String(contentsOf: pbxprojPath, encoding: .utf8) else {
            return nil
        }

        // MARKETING_VERSION = X.X.X; 패턴 찾기
        let pattern = "MARKETING_VERSION\\s*=\\s*([0-9]+\\.[0-9]+\\.?[0-9]*)\\s*;"
        guard let regex = try? NSRegularExpression(pattern: pattern, options: []) else {
            return nil
        }

        let range = NSRange(content.startIndex..., in: content)
        if let match = regex.firstMatch(in: content, options: [], range: range) {
            if let versionRange = Range(match.range(at: 1), in: content) {
                return String(content[versionRange])
            }
        }

        return nil
    }

    /// 앱 이름으로 실제 JSON 파일 경로 찾기
    private func findJsonFile(for appName: String) -> URL? {
        // 1. 먼저 매핑 테이블 시도
        let appFolder = getFolderName(for: appName)
        let mappedFile = appsDirectory.appendingPathComponent("\(appFolder).json")
        if fileManager.fileExists(atPath: mappedFile.path) {
            return mappedFile
        }

        // 2. 매핑에 없으면 apps/ 디렉토리에서 name 필드로 검색
        do {
            let jsonFiles = try fileManager.contentsOfDirectory(
                at: appsDirectory,
                includingPropertiesForKeys: nil
            ).filter { $0.pathExtension == "json" }

            for file in jsonFiles {
                if let data = try? Data(contentsOf: file),
                   let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let name = json["name"] as? String,
                   name == appName {
                    print("📂 JSON 파일 발견: \(file.lastPathComponent) for \(appName)")
                    return file
                }
            }
        } catch {
            print("❌ JSON 파일 검색 실패: \(error)")
        }

        print("⚠️ JSON 파일을 찾을 수 없음: \(appName)")
        return nil
    }

    /// 특정 앱의 버전을 프로젝트에서 감지된 버전으로 업데이트
    func updateVersionFromProject(appName: String, skipReload: Bool = false) {
        guard let app = apps.first(where: { $0.name == appName }),
              let localPath = app.localProjectPath,
              let detectedVersion = detectProjectVersion(localPath: localPath) else {
            print("❌ 버전 감지 실패: \(appName)")
            return
        }

        // 실제 JSON 파일 찾기
        guard let jsonFile = findJsonFile(for: appName) else {
            print("❌ JSON 파일을 찾을 수 없음: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as! [String: Any]

            json["currentVersion"] = detectedVersion

            let updatedData = try JSONSerialization.data(withJSONObject: json, options: .prettyPrinted)
            try updatedData.write(to: jsonFile)

            print("✅ 버전 업데이트 완료: \(appName) → \(detectedVersion)")

            // 버전 변경 목록에서 제거
            DispatchQueue.main.async {
                self.versionChanges.removeAll { $0.appName == appName }
            }

            // 일괄 업데이트가 아닌 경우에만 리로드
            if !skipReload {
                loadPortfolio()
                updateSummary()
            }

        } catch {
            print("❌ 버전 업데이트 실패: \(error)")
        }
    }

    /// 모든 변경된 버전 일괄 업데이트
    func updateAllVersionsFromProjects() {
        // 업데이트 시작 플래그
        isUpdatingVersions = true

        // 먼저 현재 변경 목록 복사 (루프 중 변경 방지)
        let changesToUpdate = versionChanges

        // 버전 변경 목록 먼저 초기화
        DispatchQueue.main.async {
            self.versionChanges.removeAll()
        }

        for change in changesToUpdate {
            updateVersionFromProject(appName: change.appName, skipReload: true)
        }

        // 모든 업데이트 완료 후 한 번만 리로드
        loadPortfolio()
        updateSummary()

        // 약간의 딜레이 후 플래그 해제 (loadPortfolio 비동기 완료 대기)
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            self.isUpdatingVersions = false
        }
    }

    // MARK: - Category Management

    func loadCategories() {
        guard fileManager.fileExists(atPath: categoriesFile.path) else {
            print("📂 categories.json 파일 없음 - 빈 카테고리 목록으로 시작")
            return
        }

        do {
            let data = try Data(contentsOf: categoriesFile)
            let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
            if let categories = json?["categories"] as? [String] {
                DispatchQueue.main.async {
                    self.availableCategories = categories
                    print("✅ 카테고리 \(categories.count)개 로드 완료")
                }
            }
        } catch {
            print("❌ 카테고리 로드 실패: \(error)")
        }
    }

    func saveCategories() {
        let json: [String: Any] = [
            "categories": availableCategories.sorted()
        ]

        do {
            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: categoriesFile)
            print("✅ 카테고리 저장 완료: \(availableCategories.count)개")
        } catch {
            print("❌ 카테고리 저장 실패: \(error)")
        }
    }

    func addCategory(_ name: String) {
        let trimmedName = name.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedName.isEmpty else { return }
        guard !availableCategories.contains(trimmedName) else {
            print("⚠️ 이미 존재하는 카테고리: \(trimmedName)")
            return
        }

        availableCategories.append(trimmedName)
        saveCategories()
    }

    func removeCategory(_ name: String) {
        // 사용 중인 카테고리인지 확인
        let isInUse = apps.contains { app in
            app.categories?.contains(name) ?? false
        }

        guard !isInUse else {
            print("⚠️ 사용 중인 카테고리는 삭제할 수 없습니다: \(name)")
            return
        }

        availableCategories.removeAll { $0 == name }
        saveCategories()
    }

    func renameCategory(old: String, new: String) {
        let trimmedNew = new.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedNew.isEmpty else { return }
        guard availableCategories.contains(old) else { return }
        guard !availableCategories.contains(trimmedNew) else {
            print("⚠️ 이미 존재하는 카테고리 이름: \(trimmedNew)")
            return
        }

        // 카테고리 목록 업데이트
        if let index = availableCategories.firstIndex(of: old) {
            availableCategories[index] = trimmedNew
        }

        // 모든 앱의 카테고리도 업데이트
        for app in apps {
            if let categories = app.categories, categories.contains(old) {
                var newCategories = categories
                if let catIndex = newCategories.firstIndex(of: old) {
                    newCategories[catIndex] = trimmedNew
                }
                updateAppCategories(appName: app.name, categories: newCategories)
            }
        }

        saveCategories()
    }

    func updateAppCategories(appName: String, categories: [String]) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            json["categories"] = categories

            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: jsonFile)
            print("✅ 앱 카테고리 업데이트 완료: \(appName)")

            // 포트폴리오 다시 로드
            loadPortfolio()
        } catch {
            print("❌ 앱 카테고리 업데이트 실패: \(error)")
        }
    }

    // MARK: - Update App Price

    func updateAppPrice(appName: String, price: AppPrice) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            // 가격 정보를 딕셔너리로 변환
            var priceDict: [String: Any] = ["isFree": price.isFree]
            if let model = price.pricingModel {
                priceDict["pricingModel"] = model.rawValue
            }
            if let usd = price.usd {
                priceDict["usd"] = usd
            }
            if let krw = price.krw {
                priceDict["krw"] = krw
            }
            if let monthlyUSD = price.monthlyUSD {
                priceDict["monthlyUSD"] = monthlyUSD
            }
            if let monthlyKRW = price.monthlyKRW {
                priceDict["monthlyKRW"] = monthlyKRW
            }
            if let yearlyUSD = price.yearlyUSD {
                priceDict["yearlyUSD"] = yearlyUSD
            }
            if let yearlyKRW = price.yearlyKRW {
                priceDict["yearlyKRW"] = yearlyKRW
            }
            json["price"] = priceDict

            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: jsonFile)
            print("✅ 앱 가격 업데이트 완료: \(appName) - \(price.displayPrice)")

            // 포트폴리오 다시 로드
            loadPortfolio()
        } catch {
            print("❌ 앱 가격 업데이트 실패: \(error)")
        }
    }

    // MARK: - Release Notes Management

    func addReleaseNote(appName: String, releaseNote: ReleaseNote) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            // 기존 릴리스 노트 가져오기
            var releaseNotes = json["releaseNotes"] as? [[String: Any]] ?? []

            // 새 릴리스 노트 추가
            let noteDict: [String: Any] = [
                "id": releaseNote.id,
                "version": releaseNote.version,
                "date": ISO8601DateFormatter().string(from: releaseNote.date),
                "notesKo": releaseNote.notesKo,
                "notesEn": releaseNote.notesEn
            ]
            releaseNotes.append(noteDict)
            json["releaseNotes"] = releaseNotes

            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: jsonFile)
            print("✅ 릴리스 노트 추가 완료: \(appName) - v\(releaseNote.version)")

            loadPortfolio()
        } catch {
            print("❌ 릴리스 노트 추가 실패: \(error)")
        }
    }

    func updateReleaseNote(appName: String, releaseNote: ReleaseNote) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            // 기존 릴리스 노트 가져오기
            var releaseNotes = json["releaseNotes"] as? [[String: Any]] ?? []

            // 해당 ID의 릴리스 노트 찾아서 업데이트
            if let index = releaseNotes.firstIndex(where: { ($0["id"] as? String) == releaseNote.id }) {
                let noteDict: [String: Any] = [
                    "id": releaseNote.id,
                    "version": releaseNote.version,
                    "date": ISO8601DateFormatter().string(from: releaseNote.date),
                    "notesKo": releaseNote.notesKo,
                    "notesEn": releaseNote.notesEn
                ]
                releaseNotes[index] = noteDict
                json["releaseNotes"] = releaseNotes

                let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
                try jsonData.write(to: jsonFile)
                print("✅ 릴리스 노트 업데이트 완료: \(appName) - v\(releaseNote.version)")

                loadPortfolio()
            }
        } catch {
            print("❌ 릴리스 노트 업데이트 실패: \(error)")
        }
    }

    func deleteReleaseNote(appName: String, releaseNoteId: String) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            // 기존 릴리스 노트 가져오기
            var releaseNotes = json["releaseNotes"] as? [[String: Any]] ?? []

            // 해당 ID의 릴리스 노트 삭제
            releaseNotes.removeAll { ($0["id"] as? String) == releaseNoteId }
            json["releaseNotes"] = releaseNotes

            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: jsonFile)
            print("✅ 릴리스 노트 삭제 완료: \(appName)")

            loadPortfolio()
        } catch {
            print("❌ 릴리스 노트 삭제 실패: \(error)")
        }
    }

    // MARK: - Deployment Checklist Management

    func addDeploymentChecklist(appName: String, checklist: DeploymentChecklist) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            var checklists = json["deploymentChecklists"] as? [[String: Any]] ?? []

            let checklistDict: [String: Any] = [
                "id": checklist.id,
                "version": checklist.version,
                "items": checklist.items.map { item in
                    var itemDict: [String: Any] = [
                        "id": item.id,
                        "title": item.title,
                        "isCompleted": item.isCompleted
                    ]
                    if let completedAt = item.completedAt {
                        itemDict["completedAt"] = ISO8601DateFormatter().string(from: completedAt)
                    }
                    if let notes = item.notes {
                        itemDict["notes"] = notes
                    }
                    return itemDict
                },
                "createdAt": ISO8601DateFormatter().string(from: checklist.createdAt)
            ]
            checklists.append(checklistDict)
            json["deploymentChecklists"] = checklists

            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: jsonFile)
            print("✅ 배포 체크리스트 추가 완료: \(appName) - v\(checklist.version)")

            loadPortfolio()
        } catch {
            print("❌ 배포 체크리스트 추가 실패: \(error)")
        }
    }

    func updateDeploymentChecklist(appName: String, checklist: DeploymentChecklist) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            var checklists = json["deploymentChecklists"] as? [[String: Any]] ?? []

            if let index = checklists.firstIndex(where: { ($0["id"] as? String) == checklist.id }) {
                var checklistDict: [String: Any] = [
                    "id": checklist.id,
                    "version": checklist.version,
                    "items": checklist.items.map { item in
                        var itemDict: [String: Any] = [
                            "id": item.id,
                            "title": item.title,
                            "isCompleted": item.isCompleted
                        ]
                        if let completedAt = item.completedAt {
                            itemDict["completedAt"] = ISO8601DateFormatter().string(from: completedAt)
                        }
                        if let notes = item.notes {
                            itemDict["notes"] = notes
                        }
                        return itemDict
                    },
                    "createdAt": ISO8601DateFormatter().string(from: checklist.createdAt)
                ]
                if let completedAt = checklist.completedAt {
                    checklistDict["completedAt"] = ISO8601DateFormatter().string(from: completedAt)
                }
                checklists[index] = checklistDict
                json["deploymentChecklists"] = checklists

                let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
                try jsonData.write(to: jsonFile)
                print("✅ 배포 체크리스트 업데이트 완료: \(appName) - v\(checklist.version)")

                loadPortfolio()
            }
        } catch {
            print("❌ 배포 체크리스트 업데이트 실패: \(error)")
        }
    }

    func deleteDeploymentChecklist(appName: String, checklistId: String) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            var checklists = json["deploymentChecklists"] as? [[String: Any]] ?? []
            checklists.removeAll { ($0["id"] as? String) == checklistId }
            json["deploymentChecklists"] = checklists

            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: jsonFile)
            print("✅ 배포 체크리스트 삭제 완료: \(appName)")

            loadPortfolio()
        } catch {
            print("❌ 배포 체크리스트 삭제 실패: \(error)")
        }
    }

    // MARK: - Version History Management

    func addVersionHistory(appName: String, history: VersionHistory) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            var histories = json["versionHistory"] as? [[String: Any]] ?? []

            var historyDict: [String: Any] = [
                "id": history.id,
                "version": history.version,
                "status": history.status.rawValue,
                "changelog": history.changelog
            ]
            if let releaseDate = history.releaseDate {
                historyDict["releaseDate"] = ISO8601DateFormatter().string(from: releaseDate)
            }
            if let appStoreUrl = history.appStoreUrl {
                historyDict["appStoreUrl"] = appStoreUrl
            }
            histories.append(historyDict)
            json["versionHistory"] = histories

            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: jsonFile)
            print("✅ 버전 히스토리 추가 완료: \(appName) - v\(history.version)")

            loadPortfolio()
        } catch {
            print("❌ 버전 히스토리 추가 실패: \(error)")
        }
    }

    func updateVersionHistory(appName: String, history: VersionHistory) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            var histories = json["versionHistory"] as? [[String: Any]] ?? []

            if let index = histories.firstIndex(where: { ($0["id"] as? String) == history.id }) {
                var historyDict: [String: Any] = [
                    "id": history.id,
                    "version": history.version,
                    "status": history.status.rawValue,
                    "changelog": history.changelog
                ]
                if let releaseDate = history.releaseDate {
                    historyDict["releaseDate"] = ISO8601DateFormatter().string(from: releaseDate)
                }
                if let appStoreUrl = history.appStoreUrl {
                    historyDict["appStoreUrl"] = appStoreUrl
                }
                histories[index] = historyDict
                json["versionHistory"] = histories

                let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
                try jsonData.write(to: jsonFile)
                print("✅ 버전 히스토리 업데이트 완료: \(appName) - v\(history.version)")

                loadPortfolio()
            }
        } catch {
            print("❌ 버전 히스토리 업데이트 실패: \(error)")
        }
    }

    func deleteVersionHistory(appName: String, historyId: String) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            var histories = json["versionHistory"] as? [[String: Any]] ?? []
            histories.removeAll { ($0["id"] as? String) == historyId }
            json["versionHistory"] = histories

            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: jsonFile)
            print("✅ 버전 히스토리 삭제 완료: \(appName)")

            loadPortfolio()
        } catch {
            print("❌ 버전 히스토리 삭제 실패: \(error)")
        }
    }

    // MARK: - App Store Metadata Management

    func updateAppStoreMetadata(appName: String, metadata: AppStoreMetadata) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            var metadataDict: [String: Any] = [
                "descriptionKo": metadata.descriptionKo,
                "descriptionEn": metadata.descriptionEn,
                "keywords": metadata.keywords,
                "promotionalText": metadata.promotionalText
            ]
            if let supportUrl = metadata.supportUrl {
                metadataDict["supportUrl"] = supportUrl
            }
            if let privacyUrl = metadata.privacyUrl {
                metadataDict["privacyUrl"] = privacyUrl
            }
            if let ageRating = metadata.ageRating {
                metadataDict["ageRating"] = ageRating
            }
            if let primaryCategory = metadata.primaryCategory {
                metadataDict["primaryCategory"] = primaryCategory
            }
            if let secondaryCategory = metadata.secondaryCategory {
                metadataDict["secondaryCategory"] = secondaryCategory
            }
            json["appStoreMetadata"] = metadataDict

            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: jsonFile)
            print("✅ 앱스토어 메타데이터 업데이트 완료: \(appName)")

            loadPortfolio()
        } catch {
            print("❌ 앱스토어 메타데이터 업데이트 실패: \(error)")
        }
    }

    // MARK: - Screenshot Management

    func updateScreenshotInfo(appName: String, screenshots: ScreenshotInfo) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            var screenshotsDict: [String: Any] = [
                "devices": screenshots.devices.map { device in
                    [
                        "id": device.id,
                        "deviceType": device.deviceType,
                        "isReady": device.isReady,
                        "count": device.count
                    ]
                }
            ]
            if let folderPath = screenshots.folderPath {
                screenshotsDict["folderPath"] = folderPath
            }
            json["screenshots"] = screenshotsDict

            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: jsonFile)
            print("✅ 스크린샷 정보 업데이트 완료: \(appName)")

            loadPortfolio()
        } catch {
            print("❌ 스크린샷 정보 업데이트 실패: \(error)")
        }
    }

    // MARK: - Deployment Reminder Management

    func updateDeploymentReminder(appName: String, reminder: DeploymentReminder) {
        let appFolder = getFolderName(for: appName)
        let jsonFile = appsDirectory.appendingPathComponent("\(appFolder).json")

        guard fileManager.fileExists(atPath: jsonFile.path) else {
            print("❌ 앱 파일을 찾을 수 없습니다: \(appName)")
            return
        }

        do {
            let data = try Data(contentsOf: jsonFile)
            var json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]

            var reminderDict: [String: Any] = [
                "enabled": reminder.enabled,
                "reminderDays": reminder.reminderDays,
                "updateCycle": reminder.updateCycle.rawValue
            ]
            if let lastDeploymentDate = reminder.lastDeploymentDate {
                reminderDict["lastDeploymentDate"] = ISO8601DateFormatter().string(from: lastDeploymentDate)
            }
            if let nextPlannedDate = reminder.nextPlannedDate {
                reminderDict["nextPlannedDate"] = ISO8601DateFormatter().string(from: nextPlannedDate)
            }
            json["deploymentReminder"] = reminderDict

            let jsonData = try JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys])
            try jsonData.write(to: jsonFile)
            print("✅ 배포 알림 설정 업데이트 완료: \(appName)")

            loadPortfolio()
        } catch {
            print("❌ 배포 알림 설정 업데이트 실패: \(error)")
        }
    }
}
