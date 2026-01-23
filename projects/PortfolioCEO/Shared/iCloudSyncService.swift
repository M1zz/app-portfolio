//
//  iCloudSyncService.swift
//  Shared between PortfolioCEO (macOS) and CEOfeedback (iOS)
//

import Foundation
import Combine

class iCloudSyncService: ObservableObject {
    static let shared = iCloudSyncService()

    @Published var apps: [AppSummary] = []
    @Published var feedbacks: [AppFeedback] = []
    @Published var isLoading = false
    @Published var lastSyncDate: Date?
    @Published var syncError: Error?

    private let fileManager = FileManager.default
    private let syncFileName = "ceo-sync-data.json"

    // iCloud Documents URL
    private let containerIdentifier = "iCloud.com.leeo.PortfolioCEO"

    private var iCloudDocumentsURL: URL? {
        fileManager.url(forUbiquityContainerIdentifier: containerIdentifier)?
            .appendingPathComponent("Documents")
    }

    // 로컬 폴백 URL
    private var localDocumentsURL: URL {
        fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }

    private var syncFileURL: URL {
        if let iCloudURL = iCloudDocumentsURL {
            // iCloud Documents 폴더가 없으면 생성
            if !fileManager.fileExists(atPath: iCloudURL.path) {
                try? fileManager.createDirectory(at: iCloudURL, withIntermediateDirectories: true)
            }
            return iCloudURL.appendingPathComponent(syncFileName)
        }
        return localDocumentsURL.appendingPathComponent(syncFileName)
    }

    var isICloudAvailable: Bool {
        iCloudDocumentsURL != nil
    }

    private init() {
        setupiCloudObserver()
        loadSyncData()
    }

    // MARK: - iCloud Observer

    private func setupiCloudObserver() {
        // iCloud 변경 알림 구독
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(iCloudDataDidChange),
            name: NSNotification.Name.NSUbiquityIdentityDidChange,
            object: nil
        )
    }

    @objc private func iCloudDataDidChange() {
        loadSyncData()
    }

    // MARK: - Load Data

    func loadSyncData() {
        isLoading = true
        syncError = nil

        let url = syncFileURL

        // 파일이 iCloud에 있으면 다운로드 요청
        if isICloudAvailable {
            do {
                try fileManager.startDownloadingUbiquitousItem(at: url)
            } catch {
                print("⚠️ iCloud 다운로드 시작 실패: \(error)")
            }
        }

        // 약간의 딜레이 후 읽기 (다운로드 대기)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            self?.readSyncFile()
        }
    }

    private func readSyncFile() {
        let url = syncFileURL

        guard fileManager.fileExists(atPath: url.path) else {
            print("📂 동기화 파일 없음: \(url.path)")
            isLoading = false
            return
        }

        do {
            let data = try Data(contentsOf: url)
            let container = try JSONDecoder().decode(SyncDataContainer.self, from: data)

            DispatchQueue.main.async {
                self.apps = container.apps
                self.feedbacks = container.feedbacks
                self.lastSyncDate = container.lastUpdated
                self.isLoading = false
            }

            print("✅ 동기화 데이터 로드: \(container.apps.count)개 앱, \(container.feedbacks.count)개 피드백")

        } catch {
            print("❌ 동기화 데이터 로드 실패: \(error)")
            DispatchQueue.main.async {
                self.syncError = error
                self.isLoading = false
            }
        }
    }

    // MARK: - Save Data

    func saveSyncData() {
        let container = SyncDataContainer(apps: apps, feedbacks: feedbacks)

        do {
            let encoder = JSONEncoder()
            encoder.dateEncodingStrategy = .iso8601
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]

            let data = try encoder.encode(container)
            try data.write(to: syncFileURL)

            lastSyncDate = Date()
            print("✅ 동기화 데이터 저장: \(syncFileURL.path)")

        } catch {
            print("❌ 동기화 데이터 저장 실패: \(error)")
            syncError = error
        }
    }

    // MARK: - Feedback Operations

    func addFeedback(_ feedback: AppFeedback) {
        feedbacks.append(feedback)
        saveSyncData()
    }

    func updateFeedback(_ feedback: AppFeedback) {
        if let index = feedbacks.firstIndex(where: { $0.id == feedback.id }) {
            var updated = feedback
            updated.updatedAt = Date()
            feedbacks[index] = updated
            saveSyncData()
        }
    }

    func deleteFeedback(id: UUID) {
        feedbacks.removeAll { $0.id == id }
        saveSyncData()
    }

    func feedbacks(for appBundleId: String) -> [AppFeedback] {
        feedbacks.filter { $0.appBundleId == appBundleId }
    }

    // MARK: - Update Apps (macOS에서 호출)

    func updateApps(_ newApps: [AppSummary]) {
        apps = newApps
        saveSyncData()
    }
}
