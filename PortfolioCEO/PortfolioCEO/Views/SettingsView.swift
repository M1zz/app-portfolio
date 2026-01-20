import SwiftUI

struct SettingsView: View {
    @AppStorage("portfolioPath") private var portfolioPath = "~/Documents/workspace/code/app-portfolio"
    @AppStorage("enableNotifications") private var enableNotifications = true
    @AppStorage("dailyBriefingTime") private var dailyBriefingTime = 9

    // iCloud 서비스는 iCloudSyncService.swift 파일이 프로젝트에 추가되면 활성화됩니다
    // @StateObject private var iCloudService = iCloudSyncService.shared
    @EnvironmentObject var portfolioService: PortfolioService

    @State private var showingSyncAlert = false
    @State private var syncAlertMessage = ""
    @State private var isSyncing = false
    @State private var iCloudEnabled = false

    var body: some View {
        Form {
            Section("포트폴리오") {
                TextField("경로", text: $portfolioPath)
                    .textFieldStyle(.roundedBorder)

                Button("폴더 선택...") {
                    selectFolder()
                }
            }

            Section("iCloud 동기화") {
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Image(systemName: "info.circle.fill")
                            .foregroundColor(.blue)
                        Text("iCloud 동기화 준비 중")
                            .foregroundColor(.secondary)
                    }

                    Text("iCloud 동기화 기능을 사용하려면 다음 단계를 완료하세요:")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    VStack(alignment: .leading, spacing: 4) {
                        Text("1. Xcode에서 Apple Developer 계정 로그인")
                            .font(.caption2)
                        Text("2. Signing & Capabilities에서 iCloud 추가")
                            .font(.caption2)
                        Text("3. iCloud_Setup_Guide.md 파일 참고")
                            .font(.caption2)
                            .foregroundColor(.blue)
                    }
                    .padding(.leading, 8)

                    Text("iCloud를 사용하면 모든 기기에서 프로젝트 데이터가 자동으로 동기화됩니다.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.top, 4)
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
        .frame(width: 500, height: 450)
    }

    func selectFolder() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false

        if panel.runModal() == .OK {
            if let url = panel.url {
                portfolioPath = url.path
            }
        }
    }
}
