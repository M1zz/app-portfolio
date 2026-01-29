import SwiftUI

/// 프로젝트 파일 감지 상태를 보여주는 진단 화면
struct ProjectDiagnosticsView: View {
    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) var dismiss

    @State private var diagnostics: [ProjectDiagnostic] = []
    @State private var isLoading = true

    struct ProjectDiagnostic: Identifiable {
        let id = UUID()
        let appName: String
        let bundleId: String
        let localPath: String?
        let pathStatus: PathStatus
        let jsonVersion: String
        let detectedVersion: String?
        let xcodeProjectName: String?

        enum PathStatus {
            case valid           // 경로 존재, xcodeproj 발견
            case noXcodeProject  // 경로 존재, xcodeproj 없음
            case pathNotFound    // 경로 없음
            case notConfigured   // localProjectPath 미설정

            var icon: String {
                switch self {
                case .valid: return "checkmark.circle.fill"
                case .noXcodeProject: return "exclamationmark.triangle.fill"
                case .pathNotFound: return "xmark.circle.fill"
                case .notConfigured: return "minus.circle"
                }
            }

            var color: Color {
                switch self {
                case .valid: return .green
                case .noXcodeProject: return .orange
                case .pathNotFound: return .red
                case .notConfigured: return .gray
                }
            }

            var description: String {
                switch self {
                case .valid: return "정상"
                case .noXcodeProject: return "xcodeproj 없음"
                case .pathNotFound: return "경로 없음"
                case .notConfigured: return "미설정"
                }
            }
        }
    }

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("프로젝트 경로 진단")
                        .font(.title2)
                        .fontWeight(.bold)
                    Text("각 앱의 로컬 프로젝트 경로 및 버전 감지 상태를 확인합니다")
                        .font(.body)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Button(action: runDiagnostics) {
                    Label("다시 검사", systemImage: "arrow.clockwise")
                }
                .disabled(isLoading)

                Button("닫기") {
                    dismiss()
                }
            }
            .padding()
            .background(Color(NSColor.controlBackgroundColor))

            Divider()

            // 요약 통계
            summaryView

            Divider()

            // 앱 목록
            if isLoading {
                VStack(spacing: 16) {
                    ProgressView()
                    Text("경로 검사 중...")
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                ScrollView {
                    LazyVStack(spacing: 8) {
                        ForEach(diagnostics) { diagnostic in
                            DiagnosticRowView(diagnostic: diagnostic)
                        }
                    }
                    .padding()
                }
            }
        }
        .frame(width: 800, height: 600)
        .onAppear {
            runDiagnostics()
        }
    }

    private var summaryView: some View {
        HStack(spacing: 24) {
            StatBox(
                title: "전체",
                count: diagnostics.count,
                color: .primary
            )
            StatBox(
                title: "정상",
                count: diagnostics.filter { $0.pathStatus == .valid }.count,
                color: .green
            )
            StatBox(
                title: "버전 불일치",
                count: diagnostics.filter {
                    $0.pathStatus == .valid &&
                    $0.detectedVersion != nil &&
                    $0.detectedVersion != $0.jsonVersion
                }.count,
                color: .orange
            )
            StatBox(
                title: "경로 문제",
                count: diagnostics.filter {
                    $0.pathStatus == .pathNotFound || $0.pathStatus == .noXcodeProject
                }.count,
                color: .red
            )
            StatBox(
                title: "미설정",
                count: diagnostics.filter { $0.pathStatus == .notConfigured }.count,
                color: .gray
            )
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor).opacity(0.5))
    }

    private func runDiagnostics() {
        isLoading = true
        diagnostics = []

        DispatchQueue.global(qos: .userInitiated).async {
            var results: [ProjectDiagnostic] = []

            for app in portfolioService.apps {
                let diagnostic = checkProject(app: app)
                results.append(diagnostic)
            }

            // 상태별, 이름순 정렬
            results.sort { d1, d2 in
                if d1.pathStatus != d2.pathStatus {
                    return statusPriority(d1.pathStatus) < statusPriority(d2.pathStatus)
                }
                return d1.appName < d2.appName
            }

            DispatchQueue.main.async {
                self.diagnostics = results
                self.isLoading = false
            }
        }
    }

    private func statusPriority(_ status: ProjectDiagnostic.PathStatus) -> Int {
        switch status {
        case .pathNotFound: return 0
        case .noXcodeProject: return 1
        case .valid: return 2
        case .notConfigured: return 3
        }
    }

    private func checkProject(app: AppModel) -> ProjectDiagnostic {
        guard let localPath = app.localProjectPath, !localPath.isEmpty else {
            return ProjectDiagnostic(
                appName: app.name,
                bundleId: app.bundleId,
                localPath: nil,
                pathStatus: .notConfigured,
                jsonVersion: app.currentVersion,
                detectedVersion: nil,
                xcodeProjectName: nil
            )
        }

        // 절대 경로 계산
        let absolutePath: URL
        if localPath.hasPrefix("/") {
            absolutePath = URL(fileURLWithPath: localPath)
        } else {
            absolutePath = portfolioService.currentDataPath.appendingPathComponent(localPath)
        }

        let fileManager = FileManager.default

        // 경로 존재 확인
        guard fileManager.fileExists(atPath: absolutePath.path) else {
            return ProjectDiagnostic(
                appName: app.name,
                bundleId: app.bundleId,
                localPath: localPath,
                pathStatus: .pathNotFound,
                jsonVersion: app.currentVersion,
                detectedVersion: nil,
                xcodeProjectName: nil
            )
        }

        // xcodeproj 찾기
        do {
            let contents = try fileManager.contentsOfDirectory(at: absolutePath, includingPropertiesForKeys: nil)
            for item in contents where item.pathExtension == "xcodeproj" {
                let pbxprojPath = item.appendingPathComponent("project.pbxproj")
                if let version = extractMarketingVersion(from: pbxprojPath) {
                    return ProjectDiagnostic(
                        appName: app.name,
                        bundleId: app.bundleId,
                        localPath: localPath,
                        pathStatus: .valid,
                        jsonVersion: app.currentVersion,
                        detectedVersion: version,
                        xcodeProjectName: item.lastPathComponent
                    )
                }
            }
        } catch {
            // 폴더 읽기 실패
        }

        return ProjectDiagnostic(
            appName: app.name,
            bundleId: app.bundleId,
            localPath: localPath,
            pathStatus: .noXcodeProject,
            jsonVersion: app.currentVersion,
            detectedVersion: nil,
            xcodeProjectName: nil
        )
    }

    private func extractMarketingVersion(from pbxprojPath: URL) -> String? {
        guard let content = try? String(contentsOf: pbxprojPath, encoding: .utf8) else {
            return nil
        }

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
}

// MARK: - Subviews

struct StatBox: View {
    let title: String
    let count: Int
    let color: Color

    var body: some View {
        VStack(spacing: 4) {
            Text("\(count)")
                .font(.system(size: 24, weight: .bold))
                .foregroundColor(color)
            Text(title)
                .font(.body)
                .foregroundColor(.secondary)
        }
        .frame(minWidth: 80)
    }
}

struct DiagnosticRowView: View {
    let diagnostic: ProjectDiagnosticsView.ProjectDiagnostic

    @State private var isExpanded = false

    var versionMismatch: Bool {
        diagnostic.pathStatus == .valid &&
        diagnostic.detectedVersion != nil &&
        diagnostic.detectedVersion != diagnostic.jsonVersion
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // 메인 행
            HStack(spacing: 12) {
                // 상태 아이콘
                Image(systemName: diagnostic.pathStatus.icon)
                    .foregroundColor(diagnostic.pathStatus.color)
                    .frame(width: 24)

                // 앱 정보
                VStack(alignment: .leading, spacing: 2) {
                    HStack {
                        Text(diagnostic.appName)
                            .font(.headline)

                        if versionMismatch {
                            HStack(spacing: 4) {
                                Image(systemName: "exclamationmark.triangle.fill")
                                    .foregroundColor(.orange)
                                Text("버전 불일치")
                                    .font(.body)
                            }
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color.orange.opacity(0.2))
                            .cornerRadius(4)
                        }
                    }

                    if let path = diagnostic.localPath {
                        Text(path)
                            .font(.system(.body, design: .monospaced))
                            .foregroundColor(.secondary)
                            .lineLimit(1)
                    } else {
                        Text("경로 미설정")
                            .font(.body)
                            .foregroundColor(.gray)
                            .italic()
                    }
                }

                Spacer()

                // 버전 정보
                VStack(alignment: .trailing, spacing: 2) {
                    HStack(spacing: 4) {
                        Text("JSON:")
                            .foregroundColor(.secondary)
                        Text("v\(diagnostic.jsonVersion)")
                            .fontWeight(.medium)
                    }
                    .font(.body)

                    if let detected = diagnostic.detectedVersion {
                        HStack(spacing: 4) {
                            Text("실제:")
                                .foregroundColor(.secondary)
                            Text("v\(detected)")
                                .fontWeight(.medium)
                                .foregroundColor(versionMismatch ? .orange : .green)
                        }
                        .font(.body)
                    }
                }

                // 상태 배지
                Text(diagnostic.pathStatus.description)
                    .font(.body)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(diagnostic.pathStatus.color.opacity(0.2))
                    .foregroundColor(diagnostic.pathStatus.color)
                    .cornerRadius(4)

                // 확장 버튼
                Button(action: { isExpanded.toggle() }) {
                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .foregroundColor(.secondary)
                }
                .buttonStyle(.plain)
            }
            .padding()

            // 확장 영역
            if isExpanded {
                Divider()
                    .padding(.horizontal)

                VStack(alignment: .leading, spacing: 8) {
                    DetailRow(label: "Bundle ID", value: diagnostic.bundleId)

                    if let path = diagnostic.localPath {
                        DetailRow(label: "설정된 경로", value: path)
                    }

                    if let xcodeProj = diagnostic.xcodeProjectName {
                        DetailRow(label: "Xcode 프로젝트", value: xcodeProj)
                    }

                    if diagnostic.pathStatus == .pathNotFound {
                        HStack {
                            Image(systemName: "lightbulb.fill")
                                .foregroundColor(.yellow)
                            Text("이 컴퓨터에 프로젝트가 없거나 경로가 잘못되었습니다.")
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                        .padding(.top, 4)
                    }

                    if versionMismatch {
                        HStack {
                            Image(systemName: "arrow.triangle.2.circlepath")
                                .foregroundColor(.orange)
                            Text("프로젝트 버전이 변경되었습니다. 대시보드에서 업데이트하세요.")
                                .font(.body)
                                .foregroundColor(.orange)
                        }
                        .padding(.top, 4)
                    }
                }
                .padding()
                .background(Color(NSColor.controlBackgroundColor).opacity(0.5))
            }
        }
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(8)
    }
}

struct DetailRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack(alignment: .top) {
            Text(label + ":")
                .foregroundColor(.secondary)
                .frame(width: 100, alignment: .trailing)
            Text(value)
                .textSelection(.enabled)
                .font(.system(.body, design: .monospaced))
            Spacer()
        }
        .font(.body)
    }
}
