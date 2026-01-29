import SwiftUI

struct SettingsView: View {
    @AppStorage("portfolioPath") private var portfolioPath = "~/Documents/code/app-portfolio"
    @AppStorage("enableNotifications") private var enableNotifications = true
    @AppStorage("dailyBriefingTime") private var dailyBriefingTime = 9
    @AppStorage("iCloudSyncEnabled") private var iCloudSyncEnabled = true

    @EnvironmentObject var portfolioService: PortfolioService

    @State private var showingSyncAlert = false
    @State private var syncAlertMessage = ""
    @State private var isSyncing = false
    @State private var isTestingCLI = false
    @State private var cliTestResult: String?
    @State private var lastSyncTime: Date?
    @State private var showingDeleteConfirmation = false
    @State private var isDeleting = false
    @State private var showingCategoryManagement = false
    @State private var showingProjectDiagnostics = false

    @StateObject private var cloudKitService = CloudKitSyncService.shared

    var body: some View {
        Form {
            Section("Claude CLI") {
                HStack {
                    Button(isTestingCLI ? "테스트 중..." : "CLI 연결 테스트") {
                        testCLIConnection()
                    }
                    .disabled(isTestingCLI)

                    if let result = cliTestResult {
                        Text(result)
                            .font(.body)
                            .foregroundColor(result.contains("성공") ? .green : .red)
                    }
                }

                Text("Claude Code Max 구독이 필요합니다. API 크레딧은 필요하지 않습니다.")
                    .font(.body)
                    .foregroundColor(.secondary)
            }

            Section("데이터 경로") {
                // 현재 경로 상태
                HStack {
                    Image(systemName: portfolioService.isPathValid ? "checkmark.circle.fill" : "xmark.circle.fill")
                        .foregroundColor(portfolioService.isPathValid ? .green : .red)
                    Text(portfolioService.isPathValid ? "데이터 폴더 연결됨" : "데이터 폴더를 찾을 수 없음")
                        .foregroundColor(portfolioService.isPathValid ? .primary : .red)
                }

                // 현재 사용 중인 경로
                VStack(alignment: .leading, spacing: 4) {
                    Text("현재 경로:")
                        .font(.body)
                        .foregroundColor(.secondary)
                    Text(portfolioService.currentDataPath.path)
                        .font(.system(.body, design: .monospaced))
                        .foregroundColor(.secondary)
                        .textSelection(.enabled)
                }

                Divider()

                // 경로 설정
                TextField("경로 (~/로 시작 가능)", text: $portfolioPath)
                    .textFieldStyle(.roundedBorder)

                HStack(spacing: 12) {
                    Button("폴더 선택...") {
                        selectFolder()
                    }

                    Button("자동 감지") {
                        autoDetectPath()
                    }
                    .disabled(portfolioService.isPathValid)
                }

                // 일반적인 경로 제안
                if !portfolioService.isPathValid {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("사용 가능한 경로:")
                            .font(.body)
                            .foregroundColor(.secondary)

                        ForEach(portfolioService.allPossiblePaths.prefix(3), id: \.path) { path in
                            let exists = FileManager.default.fileExists(atPath: path.appendingPathComponent("apps").path)
                            Button(action: {
                                portfolioPath = path.path
                                portfolioService.loadPortfolio()
                            }) {
                                HStack {
                                    Image(systemName: exists ? "folder.fill" : "folder")
                                        .foregroundColor(exists ? .green : .gray)
                                    Text(path.path.replacingOccurrences(of: FileManager.default.homeDirectoryForCurrentUser.path, with: "~"))
                                        .font(.system(.body, design: .monospaced))
                                        .lineLimit(1)
                                        .truncationMode(.middle)
                                    if exists {
                                        Text("✓")
                                            .foregroundColor(.green)
                                    }
                                }
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.top, 4)
                }
            }

            Section("프로젝트 경로") {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("로컬 프로젝트 연결 상태")
                            .font(.body)
                        Text("각 앱의 localProjectPath가 올바르게 설정되어 있는지 확인합니다")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    Spacer()

                    Button("진단 실행...") {
                        showingProjectDiagnostics = true
                    }
                    .buttonStyle(.bordered)
                }

                // 버전 변경 감지된 앱 표시
                if !portfolioService.versionChanges.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(.orange)
                            Text("\(portfolioService.versionChanges.count)개 앱의 버전이 변경됨")
                                .foregroundColor(.orange)
                        }

                        ForEach(portfolioService.versionChanges) { change in
                            HStack {
                                Text(change.appName)
                                    .font(.body)
                                Spacer()
                                Text("\(change.currentVersion) → \(change.detectedVersion)")
                                    .font(.system(.body, design: .monospaced))
                                    .foregroundColor(.orange)
                            }
                            .padding(.leading, 24)
                        }
                    }
                    .padding(.top, 4)
                }
            }

            Section("카테고리") {
                HStack {
                    Text("\(portfolioService.availableCategories.count)개 카테고리")
                        .foregroundColor(.secondary)

                    Spacer()

                    Button("관리...") {
                        showingCategoryManagement = true
                    }
                    .buttonStyle(.bordered)
                }
            }

            Section("iCloud 동기화 (iOS 앱 연동)") {
                // iCloud 연결 상태
                HStack {
                    Image(systemName: isICloudAvailable ? "checkmark.icloud.fill" : "xmark.icloud.fill")
                        .foregroundColor(isICloudAvailable ? .green : .red)
                    Text(isICloudAvailable ? "iCloud 연결됨" : "iCloud에 로그인되지 않음")
                        .foregroundColor(isICloudAvailable ? .primary : .red)
                    Spacer()
                }

                // 동기화 활성화 토글
                Toggle("자동 동기화", isOn: $iCloudSyncEnabled)
                    .disabled(!isICloudAvailable)

                // 마지막 동기화 시간
                HStack {
                    Text("마지막 동기화")
                        .foregroundColor(.secondary)
                    Spacer()
                    if let lastSync = lastSyncTime {
                        Text(lastSync, style: .relative)
                            .foregroundColor(.secondary)
                    } else {
                        Text("없음")
                            .foregroundColor(.secondary)
                    }
                }

                // 동기화 버튼들
                HStack(spacing: 12) {
                    // 지금 동기화
                    Button(action: syncNow) {
                        HStack {
                            if isSyncing {
                                ProgressView()
                                    .scaleEffect(0.7)
                            } else {
                                Image(systemName: "arrow.triangle.2.circlepath")
                            }
                            Text(isSyncing ? "동기화 중..." : "지금 동기화")
                        }
                    }
                    .disabled(!isICloudAvailable || isSyncing)

                    Spacer()

                    // 동기화 데이터 삭제
                    Button(role: .destructive, action: { showingDeleteConfirmation = true }) {
                        HStack {
                            if isDeleting {
                                ProgressView()
                                    .scaleEffect(0.7)
                            } else {
                                Image(systemName: "trash")
                            }
                            Text("데이터 삭제")
                        }
                    }
                    .disabled(!isICloudAvailable || isDeleting)
                }

                // 동기화 정보
                VStack(alignment: .leading, spacing: 4) {
                    Text("동기화 대상: \(portfolioService.apps.count)개 앱")
                        .font(.body)
                        .foregroundColor(.secondary)
                    Text("CEOfeedback iOS 앱과 데이터가 동기화됩니다.")
                        .font(.body)
                        .foregroundColor(.secondary)
                }
            }

            Section("알림") {
                Toggle("일일 브리핑 알림", isOn: $enableNotifications)

                if enableNotifications {
                    Stepper("알림 시간: \(dailyBriefingTime)시", value: $dailyBriefingTime, in: 0...23)
                }
            }

            Section("정보") {
                LabeledContent("버전", value: "1.0.0")
                LabeledContent("빌드", value: "1")
            }
        }
        .formStyle(.grouped)
        .padding()
        .frame(width: 550, height: 700)
        .sheet(isPresented: $showingCategoryManagement) {
            CategoryManagementView()
                .environmentObject(portfolioService)
        }
        .sheet(isPresented: $showingProjectDiagnostics) {
            ProjectDiagnosticsView()
                .environmentObject(portfolioService)
        }
        .onAppear {
            checkLastSyncTime()
        }
        .alert("동기화 데이터 삭제", isPresented: $showingDeleteConfirmation) {
            Button("취소", role: .cancel) {}
            Button("삭제", role: .destructive) {
                deleteSyncData()
            }
        } message: {
            Text("iCloud의 동기화 데이터를 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.")
        }
        .alert("동기화", isPresented: $showingSyncAlert) {
            Button("확인", role: .cancel) {}
        } message: {
            Text(syncAlertMessage)
        }
    }

    private var isICloudAvailable: Bool {
        cloudKitService.isCloudKitAvailable
    }

    private func checkLastSyncTime() {
        lastSyncTime = cloudKitService.lastSyncDate
    }

    private func syncNow() {
        isSyncing = true
        portfolioService.syncToiCloud()

        // CloudKit은 비동기이므로 상태 업데이트
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            isSyncing = false
            lastSyncTime = Date()
            syncAlertMessage = cloudKitService.syncError ?? "동기화가 완료되었습니다."
            showingSyncAlert = true
        }
    }

    private func deleteSyncData() {
        isDeleting = true

        CloudKitSyncService.shared.deleteAllData { success, error in
            DispatchQueue.main.async {
                isDeleting = false
                if success {
                    lastSyncTime = nil
                    syncAlertMessage = "동기화 데이터가 삭제되었습니다."
                } else {
                    syncAlertMessage = "삭제 실패: \(error ?? "알 수 없는 오류")"
                }
                showingSyncAlert = true
            }
        }
    }

    func selectFolder() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false
        panel.message = "apps 폴더가 있는 포트폴리오 디렉토리를 선택하세요"

        if panel.runModal() == .OK {
            if let url = panel.url {
                portfolioPath = url.path
                // 경로 변경 후 포트폴리오 다시 로드
                portfolioService.loadPortfolio()
            }
        }
    }

    func testCLIConnection() {
        isTestingCLI = true
        cliTestResult = nil

        Task {
            let result = await AIService.shared.testClaudeCLI()
            await MainActor.run {
                isTestingCLI = false
                cliTestResult = result ? "연결 성공" : "CLI를 찾을 수 없음"
            }
        }
    }

    func autoDetectPath() {
        if let detected = portfolioService.autoDetectPath() {
            portfolioPath = detected.path
            portfolioService.loadPortfolio()
        }
    }
}
