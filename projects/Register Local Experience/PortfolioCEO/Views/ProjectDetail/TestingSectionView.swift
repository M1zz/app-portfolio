import SwiftUI

struct TestingSectionView: View {
    let app: AppModel
    @State private var testCases: [TestCase] = []
    @State private var showingAddTest: Bool = false
    @State private var newTestName: String = ""
    @State private var newTestDescription: String = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            // 헤더
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Image(systemName: "checkmark.shield.fill")
                        .font(.title2)
                        .foregroundColor(.orange)
                    Text("테스트")
                        .font(.title2)
                        .bold()
                }
                Text("테스트 케이스를 관리하고 테스트 결과를 추적합니다")
                    .font(.body)
                    .foregroundColor(.secondary)
            }

            Divider()

            // 테스트 통계
            HStack(spacing: 16) {
                TestStatCard(
                    title: "전체",
                    count: testCases.count,
                    color: .orange
                )
                TestStatCard(
                    title: "통과",
                    count: testCases.filter { $0.status == .passed }.count,
                    color: .green
                )
                TestStatCard(
                    title: "실패",
                    count: testCases.filter { $0.status == .failed }.count,
                    color: .red
                )
                TestStatCard(
                    title: "대기",
                    count: testCases.filter { $0.status == .pending }.count,
                    color: .gray
                )
            }

            Divider()

            // 테스트 케이스 추가 버튼
            HStack {
                Text("테스트 케이스")
                    .font(.headline)
                Spacer()
                Button(action: { showingAddTest.toggle() }) {
                    HStack(spacing: 4) {
                        Image(systemName: "plus.circle.fill")
                        Text("테스트 추가")
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color.orange.opacity(0.2))
                    .foregroundColor(.orange)
                    .cornerRadius(8)
                }
                .buttonStyle(.plain)
            }

            // 테스트 추가 영역
            if showingAddTest {
                VStack(alignment: .leading, spacing: 12) {
                    TextField("테스트 이름", text: $newTestName)
                        .textFieldStyle(.roundedBorder)

                    TextEditor(text: $newTestDescription)
                        .frame(height: 80)
                        .padding(8)
                        .background(Color(NSColor.textBackgroundColor))
                        .cornerRadius(8)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color.orange, lineWidth: 2)
                        )

                    HStack {
                        Button("취소") {
                            newTestName = ""
                            newTestDescription = ""
                            showingAddTest = false
                        }
                        .keyboardShortcut(.escape)

                        Spacer()

                        Button("추가") {
                            addTestCase()
                        }
                        .keyboardShortcut(.return)
                        .disabled(newTestName.isEmpty)
                    }
                }
                .padding()
                .background(Color.orange.opacity(0.05))
                .cornerRadius(12)
            }

            // 테스트 케이스 목록
            if testCases.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "checkmark.shield")
                        .font(.system(size: 48))
                        .foregroundColor(.secondary)
                    Text("테스트 케이스가 없습니다")
                        .font(.headline)
                    Text("테스트 추가 버튼을 눌러 테스트를 작성하세요")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(40)
            } else {
                VStack(spacing: 12) {
                    ForEach($testCases) { $testCase in
                        TestCaseCard(testCase: $testCase, onDelete: {
                            deleteTestCase(testCase)
                        }, onSave: {
                            saveTestCases()
                        })
                    }
                }
            }
        }
        .onAppear {
            loadTestCases()
        }
    }

    // MARK: - Actions

    private func addTestCase() {
        guard !newTestName.isEmpty else { return }

        let testCase = TestCase(
            name: newTestName,
            description: newTestDescription,
            status: .pending
        )
        testCases.insert(testCase, at: 0)
        newTestName = ""
        newTestDescription = ""
        showingAddTest = false
        saveTestCases()
    }

    private func deleteTestCase(_ testCase: TestCase) {
        testCases.removeAll { $0.id == testCase.id }
        saveTestCases()
    }

    private func loadTestCases() {
        let fileManager = FileManager.default
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let testsDir = documentsPath.appendingPathComponent("project-tests")

        if !fileManager.fileExists(atPath: testsDir.path) {
            try? fileManager.createDirectory(at: testsDir, withIntermediateDirectories: true)
        }

        let folderName = app.name
            .lowercased()
            .replacingOccurrences(of: " ", with: "-")
        let filePath = testsDir.appendingPathComponent("\(folderName).json")

        guard let data = try? Data(contentsOf: filePath) else { return }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        if let loaded = try? decoder.decode([TestCase].self, from: data) {
            testCases = loaded
        }
    }

    private func saveTestCases() {
        let fileManager = FileManager.default
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let testsDir = documentsPath.appendingPathComponent("project-tests")

        let folderName = app.name
            .lowercased()
            .replacingOccurrences(of: " ", with: "-")
        let filePath = testsDir.appendingPathComponent("\(folderName).json")

        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601

        guard let data = try? encoder.encode(testCases) else { return }
        try? data.write(to: filePath, options: .atomic)
    }
}

// MARK: - Test Stat Card

struct TestStatCard: View {
    let title: String
    let count: Int
    let color: Color

    var body: some View {
        VStack(spacing: 8) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text("\(count)")
                .font(.system(size: 28, weight: .bold))
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(12)
    }
}

// MARK: - Test Case Card

struct TestCaseCard: View {
    @Binding var testCase: TestCase
    let onDelete: () -> Void
    let onSave: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(testCase.name)
                        .font(.headline)

                    if !testCase.description.isEmpty {
                        Text(testCase.description)
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    Text(formatDate(testCase.createdAt))
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Button(action: onDelete) {
                    Image(systemName: "trash")
                        .foregroundColor(.red)
                        .font(.caption)
                }
                .buttonStyle(.plain)
            }

            Divider()

            // 상태 메뉴
            HStack(spacing: 8) {
                Menu {
                    Button(action: {
                        testCase.status = .pending
                        testCase.testedAt = nil
                        onSave()
                    }) {
                        HStack {
                            Image(systemName: TestStatus.pending.icon)
                            Text(TestStatus.pending.rawValue)
                        }
                    }

                    Button(action: {
                        testCase.status = .passed
                        testCase.testedAt = Date()
                        onSave()
                    }) {
                        HStack {
                            Image(systemName: TestStatus.passed.icon)
                            Text(TestStatus.passed.rawValue)
                        }
                    }

                    Button(action: {
                        testCase.status = .failed
                        testCase.testedAt = Date()
                        onSave()
                    }) {
                        HStack {
                            Image(systemName: TestStatus.failed.icon)
                            Text(TestStatus.failed.rawValue)
                        }
                    }
                } label: {
                    HStack(spacing: 4) {
                        Image(systemName: testCase.status.icon)
                            .foregroundColor(testCase.status.color)
                        Text(testCase.status.rawValue)
                            .font(.caption)
                            .foregroundColor(testCase.status.color)
                        Image(systemName: "chevron.down")
                            .font(.caption2)
                            .foregroundColor(testCase.status.color)
                    }
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(testCase.status.color.opacity(0.1))
                    .cornerRadius(6)
                }
                .menuStyle(.borderlessButton)
                .buttonStyle(.plain)

                Spacer()
            }

            if let testedAt = testCase.testedAt {
                HStack(spacing: 4) {
                    Image(systemName: "clock.fill")
                        .foregroundColor(testCase.status.color)
                        .font(.caption2)
                    Text("테스트: \(formatDate(testedAt))")
                        .font(.caption2)
                        .foregroundColor(testCase.status.color)
                }
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(testCase.status.color.opacity(0.3), lineWidth: 1)
        )
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy.MM.dd HH:mm"
        return formatter.string(from: date)
    }
}

// MARK: - Test Case Model

struct TestCase: Identifiable, Codable {
    let id: String
    var name: String
    var description: String
    var status: TestStatus
    var createdAt: Date
    var testedAt: Date?

    init(id: String = UUID().uuidString, name: String, description: String, status: TestStatus = .pending, createdAt: Date = Date(), testedAt: Date? = nil) {
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.createdAt = createdAt
        self.testedAt = testedAt
    }
}

enum TestStatus: String, Codable {
    case pending = "대기"
    case passed = "통과"
    case failed = "실패"

    var color: Color {
        switch self {
        case .pending: return .gray
        case .passed: return .green
        case .failed: return .red
        }
    }

    var icon: String {
        switch self {
        case .pending: return "clock.fill"
        case .passed: return "checkmark.circle.fill"
        case .failed: return "xmark.circle.fill"
        }
    }
}
