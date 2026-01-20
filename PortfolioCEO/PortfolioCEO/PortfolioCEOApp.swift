//
//  PortfolioCEOApp.swift
//  Portfolio CEO - 23개 앱을 CEO처럼 관리
//
//  Created by Leeo
//

import SwiftUI
import UserNotifications

@main
struct PortfolioCEOApp: App {
    @StateObject private var portfolioService = PortfolioService.shared
    @StateObject private var notificationService = NotificationService.shared
    @StateObject private var decisionQueueService = DecisionQueueService.shared

    init() {
        // 알림 권한 요청
        NotificationService.shared.requestAuthorization()

        // 매일 아침 9시 브리핑 스케줄링
        NotificationService.shared.scheduleDailyBriefing()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(portfolioService)
                .environmentObject(notificationService)
                .environmentObject(decisionQueueService)
                .frame(minWidth: 1200, minHeight: 800)
                .onAppear {
                    // 앱 시작 시 데이터 로드
                    portfolioService.loadPortfolio()
                }
        }
        .commands {
            CommandGroup(after: .newItem) {
                Button("새로고침") {
                    portfolioService.loadPortfolio()
                }
                .keyboardShortcut("r", modifiers: .command)

                Button("브리핑 생성") {
                    portfolioService.generateBriefing()
                }
                .keyboardShortcut("b", modifiers: [.command, .shift])

                Divider()

                Button("데이터 백업하기") {
                    BackupManager.backupData(portfolioService: portfolioService)
                }
                .keyboardShortcut("s", modifiers: [.command, .shift])

                Button("데이터 복원하기") {
                    BackupManager.restoreData(portfolioService: portfolioService)
                }
                .keyboardShortcut("o", modifiers: [.command, .shift])
            }

            CommandGroup(replacing: .help) {
                Button("Portfolio CEO 가이드") {
                    NSWorkspace.shared.open(URL(string: "https://github.com/M1zz/app-portfolio")!)
                }
            }
        }

        Settings {
            SettingsView()
                .environmentObject(portfolioService)
        }
    }

}

// MARK: - Backup Manager

class BackupManager {
    static func backupData(portfolioService: PortfolioService) {
        let panel = NSSavePanel()
        panel.allowedContentTypes = [.zip]
        panel.nameFieldStringValue = "PortfolioCEO_Backup_\(formattedDate()).zip"
        panel.message = "모든 프로젝트 데이터를 백업합니다"

        panel.begin { response in
            if response == .OK, let url = panel.url {
                performBackup(to: url)
            }
        }
    }

    static func restoreData(portfolioService: PortfolioService) {
        let panel = NSOpenPanel()
        panel.allowedContentTypes = [.zip]
        panel.allowsMultipleSelection = false
        panel.message = "백업 파일을 선택하여 복원합니다"

        panel.begin { response in
            if response == .OK, let url = panel.urls.first {
                performRestore(from: url, portfolioService: portfolioService)
            }
        }
    }

    private static func performBackup(to destinationURL: URL) {
        let fileManager = FileManager.default
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]

        // 임시 백업 디렉토리 생성
        let tempBackupDir = fileManager.temporaryDirectory.appendingPathComponent("PortfolioCEO_Backup_\(UUID().uuidString)")

        do {
            try fileManager.createDirectory(at: tempBackupDir, withIntermediateDirectories: true)

            // 백업할 폴더들
            let foldersToBackup = ["apps", "app-details", "project-notes", "suggestions", "app-name-mapping.json"]

            for folder in foldersToBackup {
                let sourcePath = documentsPath.appendingPathComponent(folder)
                let destPath = tempBackupDir.appendingPathComponent(folder)

                if fileManager.fileExists(atPath: sourcePath.path) {
                    try fileManager.copyItem(at: sourcePath, to: destPath)
                    print("✅ 백업 완료: \(folder)")
                }
            }

            // ZIP 파일 생성 (shell command 사용)
            let zipProcess = Process()
            zipProcess.executableURL = URL(fileURLWithPath: "/usr/bin/zip")
            zipProcess.arguments = ["-r", "-q", destinationURL.path, "."]
            zipProcess.currentDirectoryURL = tempBackupDir

            try zipProcess.run()
            zipProcess.waitUntilExit()

            // 임시 폴더 삭제
            try fileManager.removeItem(at: tempBackupDir)

            if zipProcess.terminationStatus == 0 {
                // 성공 알림
                showAlert(title: "백업 완료", message: "모든 데이터가 성공적으로 백업되었습니다.\n\n위치: \(destinationURL.path)")
            } else {
                showAlert(title: "백업 실패", message: "ZIP 파일 생성 중 오류가 발생했습니다.")
            }

        } catch {
            showAlert(title: "백업 실패", message: "백업 중 오류가 발생했습니다: \(error.localizedDescription)")
        }
    }

    private static func performRestore(from sourceURL: URL, portfolioService: PortfolioService) {
        let fileManager = FileManager.default
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]

        // 임시 압축 해제 디렉토리
        let tempRestoreDir = fileManager.temporaryDirectory.appendingPathComponent("PortfolioCEO_Restore_\(UUID().uuidString)")

        do {
            try fileManager.createDirectory(at: tempRestoreDir, withIntermediateDirectories: true)

            // ZIP 압축 해제 (shell command 사용)
            let unzipProcess = Process()
            unzipProcess.executableURL = URL(fileURLWithPath: "/usr/bin/unzip")
            unzipProcess.arguments = ["-q", "-o", sourceURL.path, "-d", tempRestoreDir.path]

            try unzipProcess.run()
            unzipProcess.waitUntilExit()

            guard unzipProcess.terminationStatus == 0 else {
                throw NSError(domain: "BackupManager", code: -1, userInfo: [NSLocalizedDescriptionKey: "ZIP 파일 압축 해제에 실패했습니다."])
            }

            // 복원할 폴더들
            let foldersToRestore = ["apps", "app-details", "project-notes", "suggestions", "app-name-mapping.json"]

            for folder in foldersToRestore {
                let sourcePath = tempRestoreDir.appendingPathComponent(folder)
                let destPath = documentsPath.appendingPathComponent(folder)

                if fileManager.fileExists(atPath: sourcePath.path) {
                    // 기존 데이터 삭제 (덮어쓰기 전)
                    if fileManager.fileExists(atPath: destPath.path) {
                        try fileManager.removeItem(at: destPath)
                    }

                    try fileManager.copyItem(at: sourcePath, to: destPath)
                    print("✅ 복원 완료: \(folder)")
                }
            }

            // 임시 폴더 삭제
            try fileManager.removeItem(at: tempRestoreDir)

            // 데이터 리로드
            DispatchQueue.main.async {
                portfolioService.loadPortfolio()
            }

            // 성공 알림
            showAlert(title: "복원 완료", message: "모든 데이터가 성공적으로 복원되었습니다.")

        } catch {
            showAlert(title: "복원 실패", message: "복원 중 오류가 발생했습니다: \(error.localizedDescription)")
        }
    }

    private static func formattedDate() -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyyMMdd_HHmmss"
        return formatter.string(from: Date())
    }

    private static func showAlert(title: String, message: String) {
        DispatchQueue.main.async {
            let alert = NSAlert()
            alert.messageText = title
            alert.informativeText = message
            alert.alertStyle = .informational
            alert.addButton(withTitle: "확인")
            alert.runModal()
        }
    }
}
