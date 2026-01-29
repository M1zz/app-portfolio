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
                    .font(.body)
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
                        HStack(spacing: 8) {
                            ProgressView()
                                .scaleEffect(0.8)
                            Text(aiService.currentPhase.isEmpty ? "처리 중..." : aiService.currentPhase)
                                .foregroundColor(.secondary)
                                .font(.body)
                                .lineLimit(1)
                        }
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

                        // 실시간 로그 표시 (처리 중일 때)
                        if aiService.isProcessing || !aiService.logMessages.isEmpty {
                            logPanelView
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
        let notesDir = portfolioService.projectNotesDirectory
        let folderName = portfolioService.getFolderName(for: app.name)
        let filePath = notesDir.appendingPathComponent("\(folderName).json")

        print("📥 [AIAssistant] 피드백 로드 시도: \(filePath.path)")

        guard let data = try? Data(contentsOf: filePath) else {
            feedbackInput = ""
            print("⚠️ \(app.name) 피드백 파일 없음")
            return
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        if let notes = try? decoder.decode([ProjectNote].self, from: data) {
            // pending 또는 proposed 상태의 피드백만 로드
            let activeNotes = notes.filter { $0.status == .pending || $0.status == .proposed }
            feedbackInput = activeNotes.map { $0.content }.joined(separator: "\n")
            print("✅ \(app.name) 피드백 \(activeNotes.count)개 로드됨")
        } else {
            feedbackInput = ""
        }
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

    // MARK: - Log Panel View

    private var logPanelView: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "terminal")
                    .foregroundColor(.secondary)
                Text("실행 로그")
                    .font(.headline)

                Spacer()

                if aiService.isProcessing {
                    HStack(spacing: 4) {
                        Circle()
                            .fill(Color.green)
                            .frame(width: 8, height: 8)
                        Text("실행 중")
                            .font(.body)
                            .foregroundColor(.green)
                    }
                }

                Button(action: {
                    // 로그 지우기
                }) {
                    Image(systemName: "trash")
                        .foregroundColor(.secondary)
                }
                .buttonStyle(.plain)
                .disabled(aiService.isProcessing)
            }

            // 로그 메시지 목록
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 4) {
                        ForEach(aiService.logMessages) { log in
                            HStack(alignment: .top, spacing: 8) {
                                Image(systemName: log.type.icon)
                                    .foregroundColor(colorForLogType(log.type))
                                    .frame(width: 16)

                                Text(formatTime(log.timestamp))
                                    .font(.system(.body, design: .monospaced))
                                    .foregroundColor(.secondary)
                                    .frame(width: 70, alignment: .leading)

                                Text(log.message)
                                    .font(.system(.body, design: .monospaced))
                                    .foregroundColor(colorForLogType(log.type))
                                    .textSelection(.enabled)
                            }
                            .id(log.id)
                        }
                    }
                    .padding(8)
                }
                .onChange(of: aiService.logMessages.count) { _, _ in
                    if let lastLog = aiService.logMessages.last {
                        withAnimation {
                            proxy.scrollTo(lastLog.id, anchor: .bottom)
                        }
                    }
                }
            }
            .frame(height: 150)
            .background(Color(NSColor.textBackgroundColor))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
            )

            // 스트리밍 출력 미리보기 (있을 경우)
            if !aiService.streamingOutput.isEmpty && aiService.isProcessing {
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Image(systemName: "text.bubble")
                            .foregroundColor(.blue)
                        Text("응답 미리보기")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }

                    Text(String(aiService.streamingOutput.suffix(500)))
                        .font(.system(.body, design: .monospaced))
                        .foregroundColor(.primary)
                        .padding(8)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(6)
                }
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor).opacity(0.5))
        .cornerRadius(12)
    }

    private func colorForLogType(_ type: AIService.LogMessage.LogType) -> Color {
        switch type {
        case .info: return .blue
        case .progress: return .orange
        case .tool: return .purple
        case .result: return .green
        case .error: return .red
        }
    }

    private func formatTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter.string(from: date)
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
