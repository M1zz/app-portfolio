import Foundation
import Combine

class AppDetailService: ObservableObject {
    static let shared = AppDetailService()

    @Published var appDetails: [String: AppDetailInfo] = [:]  // appFolder: detail

    private let fileManager = FileManager.default

    // app-details 저장 경로 (앱 Documents 폴더)
    private var appDetailsDirectory: URL {
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        return documentsPath.appendingPathComponent("app-details")
    }

    private init() {
        // app-details 폴더 생성
        if !fileManager.fileExists(atPath: appDetailsDirectory.path) {
            try? fileManager.createDirectory(at: appDetailsDirectory, withIntermediateDirectories: true)
        }

        loadAllDetails()
        print("📁 [AppDetailService] app-details 경로: \(appDetailsDirectory.path)")
    }

    // MARK: - Public Methods

    func saveDetail(_ detail: AppDetailInfo) {
        print("\n💾 [AppDetailService] saveDetail 호출:")
        print("   - appFolder: \(detail.appFolder)")
        print("   - appDetailsDirectory: \(appDetailsDirectory.path)")

        // JSON 파일 저장
        let filePath = appDetailsDirectory.appendingPathComponent("\(detail.appFolder).json")
        print("   - 저장 파일 경로: \(filePath.path)")

        do {
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            let jsonData = try encoder.encode(detail)
            print("   - JSON 인코딩 성공: \(jsonData.count) bytes")

            try jsonData.write(to: filePath, options: [.atomic])
            print("   ✅ 파일 쓰기 성공")

            // 저장 확인
            if fileManager.fileExists(atPath: filePath.path) {
                if let attrs = try? fileManager.attributesOfItem(atPath: filePath.path),
                   let size = attrs[FileAttributeKey.size] as? UInt64 {
                    print("   ✅ 저장 확인: \(size) bytes")
                }
            }

            // 메모리 업데이트
            self.appDetails[detail.appFolder] = detail
            print("   ✅ 메모리 업데이트 완료 (총 \(self.appDetails.count)개)")

        } catch {
            print("   ❌ [AppDetailService] 파일 저장 실패: \(error.localizedDescription)")
            print("   ❌ 에러 상세: \(error)")
        }
    }

    func loadDetail(for appFolder: String) -> AppDetailInfo {
        if let existing = appDetails[appFolder] {
            return existing
        }

        // 파일에서 로드
        let filePath = appDetailsDirectory.appendingPathComponent("\(appFolder).json")

        if let data = try? Data(contentsOf: filePath),
           let detail = try? JSONDecoder().decode(AppDetailInfo.self, from: data) {
            appDetails[appFolder] = detail
            return detail
        }

        // 없으면 새로 생성
        let newDetail = AppDetailInfo(appFolder: appFolder)
        appDetails[appFolder] = newDetail
        return newDetail
    }

    func deleteDetail(for appFolder: String) {
        let filePath = appDetailsDirectory.appendingPathComponent("\(appFolder).json")

        try? fileManager.removeItem(at: filePath)

        DispatchQueue.main.async {
            self.appDetails.removeValue(forKey: appFolder)
        }
    }

    // MARK: - Private Methods

    private func loadAllDetails() {
        guard fileManager.fileExists(atPath: appDetailsDirectory.path) else {
            print("📁 [AppDetailService] app-details 폴더 없음 (첫 실행)")
            return
        }

        guard let files = try? fileManager.contentsOfDirectory(at: appDetailsDirectory, includingPropertiesForKeys: nil) else {
            return
        }

        for file in files where file.pathExtension == "json" {
            if let data = try? Data(contentsOf: file),
               let detail = try? JSONDecoder().decode(AppDetailInfo.self, from: data) {
                appDetails[detail.appFolder] = detail
            }
        }

        print("✅ [AppDetailService] 앱 상세 정보 \(appDetails.count)개 로드")
    }
}
