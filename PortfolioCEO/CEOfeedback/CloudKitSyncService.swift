//
//  CloudKitSyncService.swift
//  Shared between PortfolioCEO (macOS) and CEOfeedback (iOS)
//

import Foundation
import CloudKit
import Combine

class CloudKitSyncService: ObservableObject {
    static let shared = CloudKitSyncService()

    @Published var isSyncing = false
    @Published var lastSyncDate: Date?
    @Published var syncError: String?
    @Published var isCloudKitAvailable = false

    private let containerIdentifier = "iCloud.com.leeo.PortfolioCEO"
    private let recordType = "SyncData"
    private let recordID = CKRecord.ID(recordName: "portfolio-sync-data")

    private var container: CKContainer
    private var privateDatabase: CKDatabase

    private init() {
        container = CKContainer(identifier: containerIdentifier)
        privateDatabase = container.privateCloudDatabase
        checkCloudKitAvailability()
    }

    // MARK: - CloudKit 사용 가능 여부 확인

    func checkCloudKitAvailability() {
        container.accountStatus { [weak self] status, error in
            DispatchQueue.main.async {
                self?.isCloudKitAvailable = (status == .available)
                if let error = error {
                    print("❌ CloudKit 상태 확인 실패: \(error.localizedDescription)")
                }
            }
        }
    }

    // MARK: - 데이터 저장 (macOS → CloudKit)

    func saveApps(_ apps: [AppSummary], completion: @escaping (Bool, String?) -> Void) {
        guard isCloudKitAvailable else {
            completion(false, "CloudKit을 사용할 수 없습니다. iCloud에 로그인했는지 확인하세요.")
            return
        }

        DispatchQueue.main.async {
            self.isSyncing = true
            self.syncError = nil
        }

        // 기존 레코드 가져오기 (피드백 유지를 위해)
        privateDatabase.fetch(withRecordID: recordID) { [weak self] existingRecord, error in
            guard let self = self else { return }

            let record: CKRecord
            if let existing = existingRecord {
                record = existing
            } else {
                record = CKRecord(recordType: self.recordType, recordID: self.recordID)
            }

            // 앱 데이터 인코딩
            do {
                let encoder = JSONEncoder()
                encoder.dateEncodingStrategy = .iso8601
                let appsData = try encoder.encode(apps)
                let appsJSON = String(data: appsData, encoding: .utf8) ?? "[]"

                record["apps"] = appsJSON as CKRecordValue
                record["lastUpdated"] = Date() as CKRecordValue
                record["appCount"] = apps.count as CKRecordValue

                // 저장
                self.privateDatabase.save(record) { savedRecord, saveError in
                    DispatchQueue.main.async {
                        self.isSyncing = false

                        if let error = saveError {
                            self.syncError = error.localizedDescription
                            print("❌ CloudKit 저장 실패: \(error.localizedDescription)")
                            completion(false, error.localizedDescription)
                        } else {
                            self.lastSyncDate = Date()
                            print("✅ CloudKit 동기화 완료: \(apps.count)개 앱")
                            completion(true, nil)
                        }
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    self.isSyncing = false
                    self.syncError = error.localizedDescription
                    completion(false, error.localizedDescription)
                }
            }
        }
    }

    // MARK: - 데이터 로드 (CloudKit → iOS)

    func loadSyncData(completion: @escaping (SyncDataContainer?, String?) -> Void) {
        guard isCloudKitAvailable else {
            completion(nil, "CloudKit을 사용할 수 없습니다.")
            return
        }

        DispatchQueue.main.async {
            self.isSyncing = true
            self.syncError = nil
        }

        privateDatabase.fetch(withRecordID: recordID) { [weak self] record, error in
            DispatchQueue.main.async {
                self?.isSyncing = false

                if let error = error as? CKError, error.code == .unknownItem {
                    // 레코드가 없음 (아직 동기화된 적 없음)
                    completion(nil, nil)
                    return
                }

                if let error = error {
                    self?.syncError = error.localizedDescription
                    print("❌ CloudKit 로드 실패: \(error.localizedDescription)")
                    completion(nil, error.localizedDescription)
                    return
                }

                guard let record = record else {
                    completion(nil, "데이터를 찾을 수 없습니다.")
                    return
                }

                // 데이터 파싱
                do {
                    let decoder = JSONDecoder()
                    decoder.dateDecodingStrategy = .iso8601

                    var apps: [AppSummary] = []
                    var feedbacks: [AppFeedback] = []
                    var lastUpdated = Date()

                    if let appsJSON = record["apps"] as? String,
                       let appsData = appsJSON.data(using: .utf8) {
                        apps = try decoder.decode([AppSummary].self, from: appsData)
                    }

                    if let feedbacksJSON = record["feedbacks"] as? String,
                       let feedbacksData = feedbacksJSON.data(using: .utf8) {
                        feedbacks = try decoder.decode([AppFeedback].self, from: feedbacksData)
                    }

                    if let updated = record["lastUpdated"] as? Date {
                        lastUpdated = updated
                    }

                    self?.lastSyncDate = lastUpdated

                    let container = SyncDataContainer(
                        lastUpdated: lastUpdated,
                        apps: apps,
                        feedbacks: feedbacks
                    )

                    print("✅ CloudKit 로드 완료: \(apps.count)개 앱, \(feedbacks.count)개 피드백")
                    completion(container, nil)

                } catch {
                    self?.syncError = error.localizedDescription
                    print("❌ CloudKit 데이터 파싱 실패: \(error)")
                    completion(nil, error.localizedDescription)
                }
            }
        }
    }

    // MARK: - 피드백 저장 (iOS → CloudKit)

    func saveFeedback(_ feedback: AppFeedback, completion: @escaping (Bool, String?) -> Void) {
        guard isCloudKitAvailable else {
            completion(false, "CloudKit을 사용할 수 없습니다.")
            return
        }

        DispatchQueue.main.async {
            self.isSyncing = true
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
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                let encoder = JSONEncoder()
                encoder.dateEncodingStrategy = .iso8601

                // 기존 피드백 로드
                var feedbacks: [AppFeedback] = []
                if let feedbacksJSON = record["feedbacks"] as? String,
                   let feedbacksData = feedbacksJSON.data(using: .utf8) {
                    feedbacks = (try? decoder.decode([AppFeedback].self, from: feedbacksData)) ?? []
                }

                // 새 피드백 추가 또는 업데이트
                if let index = feedbacks.firstIndex(where: { $0.id == feedback.id }) {
                    feedbacks[index] = feedback
                } else {
                    feedbacks.append(feedback)
                }

                // 저장
                let feedbacksData = try encoder.encode(feedbacks)
                let feedbacksJSON = String(data: feedbacksData, encoding: .utf8) ?? "[]"
                record["feedbacks"] = feedbacksJSON as CKRecordValue
                record["lastUpdated"] = Date() as CKRecordValue

                self.privateDatabase.save(record) { savedRecord, saveError in
                    DispatchQueue.main.async {
                        self.isSyncing = false

                        if let error = saveError {
                            print("❌ 피드백 저장 실패: \(error.localizedDescription)")
                            completion(false, error.localizedDescription)
                        } else {
                            self.lastSyncDate = Date()
                            print("✅ 피드백 저장 완료")
                            completion(true, nil)
                        }
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    self.isSyncing = false
                    completion(false, error.localizedDescription)
                }
            }
        }
    }

    // MARK: - 데이터 삭제

    func deleteAllData(completion: @escaping (Bool, String?) -> Void) {
        guard isCloudKitAvailable else {
            completion(false, "CloudKit을 사용할 수 없습니다.")
            return
        }

        privateDatabase.delete(withRecordID: recordID) { [weak self] recordID, error in
            DispatchQueue.main.async {
                if let error = error as? CKError, error.code == .unknownItem {
                    // 이미 없음
                    self?.lastSyncDate = nil
                    completion(true, nil)
                    return
                }

                if let error = error {
                    print("❌ CloudKit 데이터 삭제 실패: \(error.localizedDescription)")
                    completion(false, error.localizedDescription)
                } else {
                    self?.lastSyncDate = nil
                    print("✅ CloudKit 데이터 삭제 완료")
                    completion(true, nil)
                }
            }
        }
    }
}

// MARK: - SyncDataContainer 확장 (CloudKit용 초기화)

extension SyncDataContainer {
    init(lastUpdated: Date, apps: [AppSummary], feedbacks: [AppFeedback]) {
        self.lastUpdated = lastUpdated
        self.apps = apps
        self.feedbacks = feedbacks
    }
}
