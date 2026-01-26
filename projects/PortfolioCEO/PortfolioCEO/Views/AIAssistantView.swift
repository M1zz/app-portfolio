import SwiftUI

struct AIAssistantView: View {
    @EnvironmentObject var portfolioService: PortfolioService
    @StateObject private var aiService = AIService.shared
    @State private var selectedApp: AppModel?
    @State private var selectedFeature: AIFeature = .feedbackAnalysis

    // 결과 상태
    @State private var result: String = ""

    // 입력 상태
    @State private var feedbackInput: String = ""
    @State private var featureInput: String = ""

    @State private var showingError = false
    @State private var errorMessage = ""

    enum AIFeature: String, CaseIterable {
        case feedbackAnalysis = "피드백 → 기능 제안"
        case taskGeneration = "기능 → 태스크 생성"

        var icon: String {
            switch self {
            case .feedbackAnalysis: return "text.bubble"
            case .taskGeneration: return "checklist"
            }
        }

        var description: String {
            switch self {
            case .feedbackAnalysis: return "피드백을 분석하여 기능 제안을 받습니다"
            case .taskGeneration: return "의사결정된 기능을 구체적인 개발 태스크로 변환합니다"
            }
        }
    }

    var body: some View {
        HSplitView {
            // 왼쪽: 기능 선택
            VStack(alignment: .leading, spacing: 0) {
                Text("AI 어시스턴트")
                    .font(.headline)
                    .padding()

                Text("Claude Code SDK")
                    .font(.caption)
                    .foregroundColor(.green)
                    .padding(.horizontal)
                    .padding(.bottom, 8)

                Divider()

                List(AIFeature.allCases, id: \.self, selection: $selectedFeature) { feature in
                    Label(feature.rawValue, systemImage: feature.icon)
                        .tag(feature)
                }
                .listStyle(.sidebar)
            }
            .frame(minWidth: 180, maxWidth: 200)

            // 오른쪽: 선택된 기능
            VStack(spacing: 0) {
                // 헤더
                HStack {
                    Label(selectedFeature.rawValue, systemImage: selectedFeature.icon)
                        .font(.title2)
                        .fontWeight(.bold)

                    Spacer()

                    if aiService.isProcessing {
                        ProgressView()
                            .scaleEffect(0.8)
                        Text("처리 중...")
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
                .background(Color(NSColor.controlBackgroundColor))

                Divider()

                // 컨텐츠
                ScrollView {
                    VStack(alignment: .leading, spacing: 20) {
                        Text(selectedFeature.description)
                            .foregroundColor(.secondary)

                        switch selectedFeature {
                        case .feedbackAnalysis:
                            feedbackAnalysisView
                        case .taskGeneration:
                            taskGenerationView
                        }

                        // 결과 표시
                        if !result.isEmpty {
                            resultView
                        }
                    }
                    .padding()
                }
            }
        }
        .frame(minWidth: 800, minHeight: 500)
        .alert("오류", isPresented: $showingError) {
            Button("확인", role: .cancel) {}
        } message: {
            Text(errorMessage)
        }
        .onChange(of: selectedFeature) { _, _ in
            result = ""
        }
    }

    // MARK: - Feedback Analysis View

    private var feedbackAnalysisView: some View {
        VStack(alignment: .leading, spacing: 16) {
            // 앱 선택
            Picker("앱 선택", selection: $selectedApp) {
                Text("앱을 선택하세요").tag(nil as AppModel?)
                ForEach(portfolioService.apps) { app in
                    Text(app.name).tag(app as AppModel?)
                }
            }

            // 피드백 입력
            VStack(alignment: .leading, spacing: 8) {
                Text("피드백 목록 (줄바꿈으로 구분)")
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                TextEditor(text: $feedbackInput)
                    .frame(minHeight: 120)
                    .border(Color.gray.opacity(0.3))
            }

            Button(action: analyzeFeedback) {
                HStack {
                    Image(systemName: "sparkles")
                    Text("수행하기")
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.accentColor)
                .foregroundColor(.white)
                .cornerRadius(8)
            }
            .buttonStyle(.plain)
            .disabled(selectedApp == nil || feedbackInput.isEmpty || aiService.isProcessing)
        }
        .onChange(of: selectedApp) { _, newApp in
            // 앱 선택 시 피드백 자동 로드
            if let app = newApp {
                loadFeedbackForApp(app)
            } else {
                feedbackInput = ""
            }
        }
    }

    // 선택된 앱의 피드백 로드
    private func loadFeedbackForApp(_ app: AppModel) {
        let fileManager = FileManager.default
        let home = fileManager.homeDirectoryForCurrentUser

        let possiblePaths = [
            home.appendingPathComponent("Documents/workspace/code/app-portfolio/project-notes"),
            home.appendingPathComponent("Documents/code/app-portfolio/project-notes")
        ]

        let folderName = portfolioService.getFolderName(for: app.name)

        for basePath in possiblePaths {
            let filePath = basePath.appendingPathComponent("\(folderName).json")

            if fileManager.fileExists(atPath: filePath.path),
               let data = try? Data(contentsOf: filePath) {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601

                if let notes = try? decoder.decode([ProjectNote].self, from: data) {
                    // pending 또는 proposed 상태의 피드백만 로드
                    let activeNotes = notes.filter { $0.status == .pending || $0.status == .proposed }
                    feedbackInput = activeNotes.map { $0.content }.joined(separator: "\n")
                    print("✅ \(app.name) 피드백 \(activeNotes.count)개 로드됨")
                    return
                }
            }
        }

        feedbackInput = ""
        print("⚠️ \(app.name) 피드백 파일 없음")
    }

    // MARK: - Task Generation View

    private var taskGenerationView: some View {
        VStack(alignment: .leading, spacing: 16) {
            Picker("앱 선택", selection: $selectedApp) {
                Text("앱을 선택하세요").tag(nil as AppModel?)
                ForEach(portfolioService.apps) { app in
                    Text(app.name).tag(app as AppModel?)
                }
            }

            VStack(alignment: .leading, spacing: 8) {
                Text("구현할 기능 설명")
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                TextEditor(text: $featureInput)
                    .frame(minHeight: 120)
                    .border(Color.gray.opacity(0.3))
            }

            Button(action: generateTasks) {
                HStack {
                    Image(systemName: "sparkles")
                    Text("태스크 생성")
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.accentColor)
                .foregroundColor(.white)
                .cornerRadius(8)
            }
            .buttonStyle(.plain)
            .disabled(selectedApp == nil || featureInput.isEmpty || aiService.isProcessing)
        }
    }

    // MARK: - Result View

    private var resultView: some View {
        VStack(alignment: .leading, spacing: 12) {
            Divider()

            HStack {
                Text("결과")
                    .font(.headline)
                Spacer()
                Button("복사") {
                    NSPasteboard.general.clearContents()
                    NSPasteboard.general.setString(result, forType: .string)
                }
                .buttonStyle(.bordered)
            }

            ScrollView {
                Text(result)
                    .textSelection(.enabled)
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(maxHeight: 400)
            .background(Color(NSColor.textBackgroundColor))
            .cornerRadius(8)
        }
    }

    // MARK: - Actions

    private func analyzeFeedback() {
        guard let app = selectedApp else { return }
        let feedbacks = feedbackInput.components(separatedBy: .newlines).filter { !$0.isEmpty }
        Task {
            do {
                let response = try await aiService.requestFeatureSuggestion(
                    appName: app.name,
                    feedbacks: feedbacks
                )
                await MainActor.run {
                    result = response
                }
            } catch {
                await MainActor.run {
                    showError(error)
                }
            }
        }
    }

    private func generateTasks() {
        guard let app = selectedApp else { return }
        Task {
            do {
                let response = try await aiService.requestTaskGeneration(
                    appName: app.name,
                    featureDescription: featureInput
                )
                await MainActor.run {
                    result = response
                }
            } catch {
                await MainActor.run {
                    showError(error)
                }
            }
        }
    }

    private func showError(_ error: Error) {
        errorMessage = error.localizedDescription
        showingError = true
    }
}
