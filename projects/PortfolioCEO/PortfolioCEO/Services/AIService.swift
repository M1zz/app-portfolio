import Foundation

/// Claude Code SDK를 CLI를 통해 활용하는 AI 서비스
class AIService: ObservableObject {
    static let shared = AIService()

    @Published var isProcessing = false
    @Published var lastError: String?

    // 실시간 피드백용
    @Published var currentPhase: String = ""
    @Published var streamingOutput: String = ""
    @Published var logMessages: [LogMessage] = []

    struct LogMessage: Identifiable {
        let id = UUID()
        let timestamp: Date
        let type: LogType
        let message: String

        enum LogType {
            case info, progress, tool, result, error

            var icon: String {
                switch self {
                case .info: return "info.circle"
                case .progress: return "arrow.clockwise"
                case .tool: return "hammer"
                case .result: return "checkmark.circle"
                case .error: return "exclamationmark.triangle"
                }
            }

            var color: String {
                switch self {
                case .info: return "blue"
                case .progress: return "orange"
                case .tool: return "purple"
                case .result: return "green"
                case .error: return "red"
                }
            }
        }
    }

    private init() {}

    private func addLog(_ message: String, type: LogMessage.LogType) {
        Task { @MainActor in
            self.logMessages.append(LogMessage(timestamp: Date(), type: type, message: message))
            // 최대 100개 로그 유지
            if self.logMessages.count > 100 {
                self.logMessages.removeFirst()
            }
        }
    }

    private func clearLogs() {
        Task { @MainActor in
            self.logMessages.removeAll()
            self.streamingOutput = ""
            self.currentPhase = ""
        }
    }

    // MARK: - Claude Code SDK Integration

    /// Claude CLI 경로 찾기
    private func findClaudeCLI() -> String? {
        let possiblePaths = [
            "/usr/local/bin/claude",
            "/opt/homebrew/bin/claude",
            "\(NSHomeDirectory())/.local/bin/claude",
            "\(NSHomeDirectory())/.claude/local/claude"
        ]

        for path in possiblePaths {
            if FileManager.default.fileExists(atPath: path) {
                return path
            }
        }

        // which 명령으로 찾기
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/which")
        process.arguments = ["claude"]

        let pipe = Pipe()
        process.standardOutput = pipe

        do {
            try process.run()
            process.waitUntilExit()

            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            if let path = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines),
               !path.isEmpty {
                return path
            }
        } catch {
            print("which claude 실패: \(error)")
        }

        return nil
    }

    /// Claude Code SDK를 통한 쿼리 실행 (스트리밍 지원)
    /// - Parameters:
    ///   - prompt: 실행할 프롬프트
    ///   - allowedTools: 허용할 도구 목록 (nil이면 제한 없음)
    ///   - maxTurns: 최대 턴 수
    ///   - outputFormat: 출력 형식 (text, json, stream-json)
    func query(
        prompt: String,
        allowedTools: [String]? = nil,
        maxTurns: Int? = nil,
        outputFormat: OutputFormat = .streamJson
    ) async throws -> String {
        clearLogs()
        await MainActor.run {
            isProcessing = true
            currentPhase = "Claude CLI 검색 중..."
        }
        addLog("쿼리 시작", type: .info)

        defer {
            Task { @MainActor in
                isProcessing = false
                currentPhase = ""
            }
        }

        guard let claudePath = findClaudeCLI() else {
            addLog("Claude CLI를 찾을 수 없습니다", type: .error)
            throw AIServiceError.claudeCLINotFound
        }

        addLog("Claude CLI 발견: \(claudePath)", type: .info)
        await MainActor.run { currentPhase = "Claude 실행 중..." }

        return try await withCheckedThrowingContinuation { continuation in
            DispatchQueue.global(qos: .userInitiated).async {
                let process = Process()
                process.executableURL = URL(fileURLWithPath: claudePath)

                var arguments = ["-p", prompt]

                // 스트리밍 JSON 형식 사용
                arguments.append("--output-format")
                arguments.append(outputFormat.rawValue)

                // 허용 도구 설정
                if let tools = allowedTools, !tools.isEmpty {
                    arguments.append("--allowedTools")
                    arguments.append(tools.joined(separator: ","))
                }

                // 최대 턴 수 설정
                if let turns = maxTurns {
                    arguments.append("--max-turns")
                    arguments.append(String(turns))
                }

                process.arguments = arguments
                self.addLog("실행 명령: claude \(arguments.joined(separator: " ").prefix(100))...", type: .info)

                let outputPipe = Pipe()
                let errorPipe = Pipe()
                process.standardOutput = outputPipe
                process.standardError = errorPipe

                // 스트리밍 출력 처리
                var fullOutput = ""
                var resultText = ""

                outputPipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
                    let data = handle.availableData
                    if data.isEmpty { return }

                    if let line = String(data: data, encoding: .utf8) {
                        fullOutput += line

                        // stream-json 형식 파싱
                        for jsonLine in line.components(separatedBy: .newlines) where !jsonLine.isEmpty {
                            self?.parseStreamingJSON(jsonLine, resultText: &resultText)
                        }
                    }
                }

                do {
                    try process.run()
                    self.addLog("프로세스 시작됨 (PID: \(process.processIdentifier))", type: .progress)

                    Task { @MainActor in
                        self.currentPhase = "응답 생성 중..."
                    }

                    process.waitUntilExit()
                    outputPipe.fileHandleForReading.readabilityHandler = nil

                    let errorData = errorPipe.fileHandleForReading.readDataToEndOfFile()

                    if process.terminationStatus == 0 {
                        self.addLog("완료!", type: .result)

                        // 최종 결과 추출
                        let finalResult = resultText.isEmpty ? self.extractFinalResult(from: fullOutput) : resultText
                        continuation.resume(returning: finalResult)
                    } else {
                        let errorMessage = String(data: errorData, encoding: .utf8) ?? "Unknown error"
                        self.addLog("오류: \(errorMessage)", type: .error)
                        continuation.resume(throwing: AIServiceError.cliError(message: errorMessage))
                    }
                } catch {
                    self.addLog("실행 실패: \(error.localizedDescription)", type: .error)
                    continuation.resume(throwing: AIServiceError.cliError(message: error.localizedDescription))
                }
            }
        }
    }

    /// 스트리밍 JSON 라인 파싱
    private func parseStreamingJSON(_ jsonLine: String, resultText: inout String) {
        guard let data = jsonLine.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return
        }

        // 이벤트 타입 확인
        if let type = json["type"] as? String {
            switch type {
            case "system":
                if let message = json["message"] as? String {
                    addLog("시스템: \(message)", type: .info)
                    Task { @MainActor in
                        self.currentPhase = message
                    }
                }

            case "assistant":
                // assistant 메시지의 content 추출
                if let message = json["message"] as? [String: Any],
                   let content = message["content"] as? [[String: Any]] {
                    for block in content {
                        if let text = block["text"] as? String {
                            resultText = text
                            Task { @MainActor in
                                self.streamingOutput = text
                            }
                        }
                    }
                }

            case "tool_use", "tool_result":
                if let toolName = json["tool"] as? String ?? (json["name"] as? String) {
                    addLog("도구 사용: \(toolName)", type: .tool)
                    Task { @MainActor in
                        self.currentPhase = "도구 실행 중: \(toolName)"
                    }
                }

            case "result":
                if let result = json["result"] as? String {
                    resultText = result
                    addLog("결과 수신 완료", type: .result)
                }

            case "error":
                if let error = json["error"] as? String {
                    addLog("오류: \(error)", type: .error)
                }

            default:
                // 기타 이벤트 로깅
                if let subtype = json["subtype"] as? String {
                    Task { @MainActor in
                        self.currentPhase = "\(type): \(subtype)"
                    }
                }
            }
        }
    }

    /// 전체 출력에서 최종 결과 추출
    private func extractFinalResult(from output: String) -> String {
        // 마지막 result 타입 JSON 찾기
        let lines = output.components(separatedBy: .newlines).reversed()
        for line in lines {
            if let data = line.data(using: .utf8),
               let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                if let result = json["result"] as? String {
                    return result
                }
                // assistant 메시지에서 텍스트 추출
                if json["type"] as? String == "assistant",
                   let message = json["message"] as? [String: Any],
                   let content = message["content"] as? [[String: Any]] {
                    for block in content {
                        if let text = block["text"] as? String {
                            return text
                        }
                    }
                }
            }
        }
        return output
    }

    /// JSON 출력에서 결과 텍스트 추출
    private func extractResultFromJSON(_ json: String) -> String? {
        guard let data = json.data(using: .utf8) else { return nil }

        do {
            if let jsonObject = try JSONSerialization.jsonObject(with: data) as? [String: Any] {
                // result 필드에서 텍스트 추출
                if let result = jsonObject["result"] as? String {
                    return result
                }
                // messages 배열에서 assistant 메시지 추출
                if let messages = jsonObject["messages"] as? [[String: Any]] {
                    let assistantMessages = messages.compactMap { msg -> String? in
                        guard msg["role"] as? String == "assistant",
                              let content = msg["content"] as? String else { return nil }
                        return content
                    }
                    return assistantMessages.joined(separator: "\n")
                }
            }
        } catch {
            print("JSON 파싱 실패: \(error)")
        }

        return nil
    }

    /// 피드백을 기반으로 기능 제안 요청
    func requestFeatureSuggestion(appName: String, feedbacks: [String]) async throws -> String {
        let feedbackList = feedbacks.enumerated().map { "  \($0.offset + 1). \($0.element)" }.joined(separator: "\n")

        let prompt = """
        나는 '\(appName)' iOS 앱의 개발자야.
        사용자들로부터 받은 피드백을 분석하고, 구체적인 기능 개선 제안을 해줘.

        ## 받은 피드백:
        \(feedbackList)

        ## 요청사항:
        1. 각 피드백을 분석해서 핵심 요구사항 정리
        2. 구현 가능한 기능으로 변환
        3. 우선순위와 예상 난이도 제시
        4. 구현 방법 간략히 제안

        한국어로 답변해줘.
        """

        // 도구 없이 텍스트 생성만 수행
        return try await query(prompt: prompt, maxTurns: 1)
    }

    /// 기능을 태스크로 변환 요청
    func requestTaskGeneration(appName: String, featureDescription: String) async throws -> String {
        let prompt = """
        나는 '\(appName)' iOS 앱의 개발자야.
        다음 기능을 구현하기 위한 구체적인 개발 태스크들을 생성해줘.

        ## 구현할 기능:
        \(featureDescription)

        ## 요청사항:
        각 태스크에 대해 다음 정보를 포함해줘:
        1. 태스크 이름 (간결하게)
        2. 상세 설명
        3. 우선순위 (높음/중간/낮음)
        4. 예상 작업 시간
        5. 카테고리 (UI/로직/데이터/테스트/기타)

        ## 응답 형식:
        ### 태스크 1: [태스크명]
        - 설명: ...
        - 우선순위: ...
        - 예상 시간: ...
        - 카테고리: ...

        ### 태스크 2: [태스크명]
        ...

        한국어로 답변해줘.
        """

        return try await query(prompt: prompt, maxTurns: 1)
    }

    /// Claude CLI 연결 테스트
    func testClaudeCLI() async -> Bool {
        guard findClaudeCLI() != nil else { return false }

        do {
            let result = try await query(prompt: "Say OK", maxTurns: 1)
            return !result.isEmpty
        } catch {
            print("Claude CLI 테스트 실패: \(error)")
            return false
        }
    }
}

// MARK: - Types

enum OutputFormat: String {
    case text = "text"
    case json = "json"
    case streamJson = "stream-json"
}

// MARK: - Error Types

enum AIServiceError: Error, LocalizedError {
    case claudeCLINotFound
    case cliError(message: String)

    var errorDescription: String? {
        switch self {
        case .claudeCLINotFound:
            return "Claude CLI를 찾을 수 없습니다. Claude Code가 설치되어 있는지 확인하세요."
        case .cliError(let message):
            return "CLI 오류: \(message)"
        }
    }
}
