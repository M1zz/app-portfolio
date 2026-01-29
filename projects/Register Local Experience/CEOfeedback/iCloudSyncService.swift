//
//  iCloudSyncService.swift
//  CEOfeedback - CloudKit 기반 동기화 서비스
//

import Foundation
import CloudKit
import Combine

class iCloudSyncService: ObservableObject {
    static let shared = iCloudSyncService()

    @Published var apps: [AppSummary] = []
    @Published var feedbacks: [AppFeedback] = []
    @Published var isLoading = false
    @Published var lastSyncDate: Date?
    @Published var syncError: String?
    @Published var isICloudAvailable = false

    private let containerIdentifier = "iCloud.com.leeo.PortfolioCEO"
    private let recordType = "SyncData"
    private let recordID = CKRecord.ID(recordName: "portfolio-sync-data")

    private var container: CKContainer
    private var privateDatabase: CKDatabase

    private init() {
        container = CKContainer(identifier: containerIdentifier)
        privateDatabase = container.privateCloudDatabase
        checkCloudKitAvailability()
        loadSyncData()
    }

    // MARK: - CloudKit 사용 가능 여부 확인

    private func checkCloudKitAvailability() {
        container.accountStatus { [weak self] status, error in
            DispatchQueue.main.async {
                self?.isICloudAvailable = (status == .available)
                if let error = error {
                    print("❌ CloudKit 상태 확인 실패: \(error.localizedDescription)")
                } else {
                    print("☁️ CloudKit 상태: \(status == .available ? "사용 가능" : "사용 불가")")
                }
            }
        }
    }

    // MARK: - Load Data (CloudKit에서 로드)

    func loadSyncData() {
        isLoading = true
        syncError = nil

        privateDatabase.fetch(withRecordID: recordID) { [weak self] record, error in
            DispatchQueue.main.async {
                self?.isLoading = false

                if let error = error as? CKError, error.code == .unknownItem {
                    // 레코드가 없음 (아직 동기화된 적 없음)
                    print("📂 CloudKit: 동기화 데이터 없음")
                    return
                }

                if let error = error {
                    self?.syncError = error.localizedDescription
                    print("❌ CloudKit 로드 실패: \(error.localizedDescription)")
                    return
                }

                guard let record = record else {
                    print("📂 CloudKit: 레코드 없음")
                    return
                }

                // 데이터 파싱
                self?.parseRecord(record)
            }
        }
    }

    private func parseRecord(_ record: CKRecord) {
        do {
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601

            if let appsJSON = record["apps"] as? String,
               let appsData = appsJSON.data(using: .utf8) {
                self.apps = try decoder.decode([AppSummary].self, from: appsData)
            }

            if let feedbacksJSON = record["feedbacks"] as? String,
               let feedbacksData = feedbacksJSON.data(using: .utf8) {
                self.feedbacks = try decoder.decode([AppFeedback].self, from: feedbacksData)
            }

            if let updated = record["lastUpdated"] as? Date {
                self.lastSyncDate = updated
            }

            print("✅ CloudKit 로드 완료: \(self.apps.count)개 앱, \(self.feedbacks.count)개 피드백")

        } catch {
            self.syncError = error.localizedDescription
            print("❌ CloudKit 데이터 파싱 실패: \(error)")
        }
    }

    // MARK: - Save Data (CloudKit에 저장)

    private func saveSyncData() {
        guard isICloudAvailable else {
            print("⚠️ CloudKit 사용 불가 - 저장 스킵")
            return
        }

        // 기존 레코드 가져오기
        privateDatabase.fetch(withRecordID: recordID) { [weak self] existingRecord, error in
            guard let self = self else { return }

            let record: CKRecord
            if let existing = existingRecord {
                record = existing
            } else {
                record = CKRecord(recordType: self.recordType, recordID: self.recordID)
            }

            do {
                let encoder = JSONEncoder()
                encoder.dateEncodingStrategy = .iso8601

                // 앱 데이터 유지 (기존 것)
                if let appsJSON = record["apps"] as? String, self.apps.isEmpty {
                    // 앱 데이터가 이미 있고 로컬이 비어있으면 유지
                } else if !self.apps.isEmpty {
                    let appsData = try encoder.encode(self.apps)
                    record["apps"] = String(data: appsData, encoding: .utf8) as? CKRecordValue
                }

                // 피드백 저장
                let feedbacksData = try encoder.encode(self.feedbacks)
                record["feedbacks"] = String(data: feedbacksData, encoding: .utf8) as? CKRecordValue
                record["lastUpdated"] = Date() as CKRecordValue

                self.privateDatabase.save(record) { savedRecord, saveError in
                    DispatchQueue.main.async {
                        if let error = saveError {
                            self.syncError = error.localizedDescription
                            print("❌ CloudKit 저장 실패: \(error.localizedDescription)")
                        } else {
                            self.lastSyncDate = Date()
                            print("✅ CloudKit 저장 완료")
                        }
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    self.syncError = error.localizedDescription
                    print("❌ CloudKit 인코딩 실패: \(error)")
                }
            }
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
