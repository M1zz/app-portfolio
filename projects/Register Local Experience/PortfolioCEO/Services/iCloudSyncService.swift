import Foundation
import Combine

class iCloudSyncService: ObservableObject {
    static let shared = iCloudSyncService()

    @Published var iCloudEnabled: Bool = false
    @Published var syncStatus: SyncStatus = .idle
    @Published var lastSyncDate: Date?

    private let fileManager = FileManager.default
    private let userDefaults = UserDefaults.standard
    private let iCloudEnabledKey = "iCloudSyncEnabled"

    enum SyncStatus {
        case idle
        case syncing
        case success
        case error(String)

        var description: String {
            switch self {
            case .idle: return "대기 중"
            case .syncing: return "동기화 중..."
            case .success: return "동기화 완료"
            case .error(let message): return "오류: \(message)"
            }
        }
    }

    private init() {
        // 저장된 설정 불러오기
        iCloudEnabled = userDefaults.bool(forKey: iCloudEnabledKey)

        // iCloud 상태 모니터링
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleiCloudChange),
            name: .NSUbiquityIdentityDidChange,
            object: nil
        )
    }

    // MARK: - iCloud 사용 가능 여부 확인

    var isiCloudAvailable: Bool {
        return fileManager.ubiquityIdentityToken != nil
    }

    // MARK: - 경로 관리

    func getDocumentsDirectory() -> URL {
        if iCloudEnabled, let iCloudURL = fileManager.url(forUbiquityContainerIdentifier: nil)?.appendingPathComponent("Documents") {
            // iCloud Documents 경로
            return iCloudURL
        } else {
            // 로컬 Documents 경로
            return fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        }
    }

    // MARK: - iCloud 활성화/비활성화

    func toggleiCloud(enable: Bool, completion: @escaping (Bool, String?) -> Void) {
        guard isiCloudAvailable else {
            completion(false, "iCloud가 사용 가능하지 않습니다. iCloud에 로그인했는지 확인하세요.")
            return
        }

        if enable == iCloudEnabled {
            completion(true, nil)
            return
        }

        syncStatus = .syncing

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }

            do {
                if enable {
                    // 로컬 → iCloud로 마이그레이션
                    try self.migrateToiCloud()
                } else {
                    // iCloud → 로컬로 마이그레이션
                    try self.migrateToLocal()
                }

                DispatchQueue.main.async {
                    self.iCloudEnabled = enable
                    self.userDefaults.set(enable, forKey: self.iCloudEnabledKey)
                    self.syncStatus = .success
                    self.lastSyncDate = Date()
                    completion(true, nil)
                }

            } catch {
                DispatchQueue.main.async {
                    self.syncStatus = .error(error.localizedDescription)
                    completion(false, error.localizedDescription)
                }
            }
        }
    }

    // MARK: - 마이그레이션

    private func migrateToiCloud() throws {
        let localURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        guard let iCloudURL = fileManager.url(forUbiquityContainerIdentifier: nil)?.appendingPathComponent("Documents") else {
            throw NSError(domain: "iCloudSync", code: -1, userInfo: [NSLocalizedDescriptionKey: "iCloud URL을 가져올 수 없습니다."])
        }

        // iCloud Documents 디렉토리 생성
        if !fileManager.fileExists(atPath: iCloudURL.path) {
            try fileManager.createDirectory(at: iCloudURL, withIntermediateDirectories: true)
        }

        // 로컬 데이터를 iCloud로 복사
        let foldersToSync = ["apps", "project-notes", "suggestions"]

        for folder in foldersToSync {
            let localFolder = localURL.appendingPathComponent(folder)
            let iCloudFolder = iCloudURL.appendingPathComponent(folder)

            if fileManager.fileExists(atPath: localFolder.path) {
                // iCloud에 이미 존재하면 삭제
                if fileManager.fileExists(atPath: iCloudFolder.path) {
                    try fileManager.removeItem(at: iCloudFolder)
                }

                // 복사
                try fileManager.copyItem(at: localFolder, to: iCloudFolder)
                print("✅ iCloud 마이그레이션: \(folder)")
            }
        }

        // app-name-mapping.json 복사
        let localMapping = localURL.appendingPathComponent("app-name-mapping.json")
        let iCloudMapping = iCloudURL.appendingPathComponent("app-name-mapping.json")

        if fileManager.fileExists(atPath: localMapping.path) {
            if fileManager.fileExists(atPath: iCloudMapping.path) {
                try fileManager.removeItem(at: iCloudMapping)
            }
            try fileManager.copyItem(at: localMapping, to: iCloudMapping)
            print("✅ iCloud 마이그레이션: app-name-mapping.json")
        }
    }

    private func migrateToLocal() throws {
        guard let iCloudURL = fileManager.url(forUbiquityContainerIdentifier: nil)?.appendingPathComponent("Documents") else {
            throw NSError(domain: "iCloudSync", code: -1, userInfo: [NSLocalizedDescriptionKey: "iCloud URL을 가져올 수 없습니다."])
        }

        let localURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]

        // iCloud 데이터를 로컬로 복사
        let foldersToSync = ["apps", "project-notes", "suggestions"]

        for folder in foldersToSync {
            let iCloudFolder = iCloudURL.appendingPathComponent(folder)
            let localFolder = localURL.appendingPathComponent(folder)

            if fileManager.fileExists(atPath: iCloudFolder.path) {
                // 로컬에 이미 존재하면 삭제
                if fileManager.fileExists(atPath: localFolder.path) {
                    try fileManager.removeItem(at: localFolder)
                }

                // 복사
                try fileManager.copyItem(at: iCloudFolder, to: localFolder)
                print("✅ 로컬 마이그레이션: \(folder)")
            }
        }

        // app-name-mapping.json 복사
        let iCloudMapping = iCloudURL.appendingPathComponent("app-name-mapping.json")
        let localMapping = localURL.appendingPathComponent("app-name-mapping.json")

        if fileManager.fileExists(atPath: iCloudMapping.path) {
            if fileManager.fileExists(atPath: localMapping.path) {
                try fileManager.removeItem(at: localMapping)
            }
            try fileManager.copyItem(at: iCloudMapping, to: localMapping)
            print("✅ 로컬 마이그레이션: app-name-mapping.json")
        }
    }

    // MARK: - 수동 동기화

    func syncNow(completion: @escaping (Bool, String?) -> Void) {
        guard iCloudEnabled, isiCloudAvailable else {
            completion(false, "iCloud가 활성화되지 않았습니다.")
            return
        }

        syncStatus = .syncing

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }

            // iCloud는 자동으로 동기화하므로 상태만 업데이트
            DispatchQueue.main.async {
                self.syncStatus = .success
                self.lastSyncDate = Date()
                completion(true, nil)
            }
        }
    }

    // MARK: - Notifications

    @objc private func handleiCloudChange(_ notification: Notification) {
        if !isiCloudAvailable && iCloudEnabled {
            // iCloud가 비활성화되면 로컬로 전환
            DispatchQueue.main.async {
                self.iCloudEnabled = false
                self.userDefaults.set(false, forKey: self.iCloudEnabledKey)
                self.syncStatus = .error("iCloud 연결이 끊어졌습니다.")
            }
        }
    }
}
