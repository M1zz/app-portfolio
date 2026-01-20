import SwiftUI

struct FeedbackSectionView: View {
    let app: AppModel
    let appDetail: AppDetailInfo?

    @State private var notes: [ProjectNote] = []
    @State private var newNoteText: String = ""
    @State private var showingAddNote: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            // 헤더
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Image(systemName: "bubble.left.and.bubble.right.fill")
                        .font(.title2)
                        .foregroundColor(.blue)
                    Text("프로젝트 메모")
                        .font(.title2)
                        .bold()
                }
                Text("프로젝트 개선사항과 피드백을 메모로 작성합니다")
                    .font(.body)
                    .foregroundColor(.secondary)
            }

            Divider()

            // 메모 추가 버튼
            HStack {
                Text("전체 메모")
                    .font(.headline)
                Spacer()
                Button(action: { showingAddNote.toggle() }) {
                    HStack(spacing: 4) {
                        Image(systemName: "plus.circle.fill")
                        Text("메모 추가")
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color.blue.opacity(0.2))
                    .foregroundColor(.blue)
                    .cornerRadius(8)
                }
                .buttonStyle(.plain)
            }

            // 메모 입력 영역
            if showingAddNote {
                VStack(alignment: .leading, spacing: 12) {
                    TextEditor(text: $newNoteText)
                        .frame(height: 100)
                        .padding(8)
                        .background(Color(NSColor.textBackgroundColor))
                        .cornerRadius(8)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color.blue, lineWidth: 2)
                        )

                    HStack {
                        Button("취소") {
                            newNoteText = ""
                            showingAddNote = false
                        }
                        .keyboardShortcut(.escape)

                        Spacer()

                        Button("저장") {
                            addNote()
                        }
                        .keyboardShortcut(.return)
                        .disabled(newNoteText.isEmpty)
                    }
                }
                .padding()
                .background(Color.blue.opacity(0.05))
                .cornerRadius(12)
            }

            // 메모 목록
            if notes.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "note.text")
                        .font(.system(size: 48))
                        .foregroundColor(.secondary)
                    Text("아직 메모가 없습니다")
                        .font(.headline)
                    Text("메모 추가 버튼을 눌러 피드백을 작성하세요")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(40)
            } else {
                VStack(spacing: 12) {
                    ForEach(notes.sorted { $0.createdAt > $1.createdAt }) { note in
                        if let index = notes.firstIndex(where: { $0.id == note.id }) {
                            NoteCard(note: $notes[index], onDelete: {
                                deleteNote(note)
                            }, onSave: {
                                saveNotes()
                            })
                        }
                    }
                }
            }
        }
        .onAppear {
            loadNotes()
        }
    }

    // MARK: - Actions

    private func getFolderName(for appName: String) -> String {
        let mapping: [String: String] = [
            "클립키보드": "clip-keyboard",
            "나만의 버킷": "my-bucket",
            "버킷 클라임": "bucket-climb",
            "데일리 트래커": "daily-tracker",
            "포트폴리오 CEO": "portfolioceo",
            "바미로그": "bami-log",
            "쿨타임": "cooltime",
            "오늘의 주접": "daily-compliment",
            "돈꼬마트": "donkko-mart",
            "두 번 알림": "double-reminder",
            "잘 싸워보세": "fight-well",
            "외국어는 언어다": "foreign-is-language",
            "인생 맛집": "life-restaurant",
            "세끼": "three-meals",
            "픽셀 미미": "pixel-mimi",
            "포항 어드벤쳐": "pohang-adventure",
            "확률계산기": "probability-calculator",
            "퀴즈": "quiz",
            "욕망의 무지개": "rainbow-of-desire",
            "라포 맵": "rapport-map",
            "리바운드 저널": "rebound-journal",
            "릴렉스 온": "relax-on",
            "내마음에저장": "save-in-my-heart",
            "일정비서": "schedule-assistant",
            "공유일 설계자": "shared-day-designer",
            "속삭": "whisper"
        ]
        return mapping[appName] ?? appName.lowercased()
    }

    private func addNote() {
        guard !newNoteText.isEmpty else { return }

        let note = ProjectNote(
            content: newNoteText,
            status: .pending
        )
        notes.insert(note, at: 0)
        newNoteText = ""
        showingAddNote = false
        saveNotes()
    }

    private func deleteNote(_ note: ProjectNote) {
        notes.removeAll { $0.id == note.id }
        saveNotes()
    }

    private func loadNotes() {
        let fileManager = FileManager.default
        let home = fileManager.homeDirectoryForCurrentUser
        let notesDir = home.appendingPathComponent("Documents/project-notes")

        if !fileManager.fileExists(atPath: notesDir.path) {
            try? fileManager.createDirectory(at: notesDir, withIntermediateDirectories: true)
        }

        let folderName = getFolderName(for: app.name)
        let filePath = notesDir.appendingPathComponent("\(folderName).json")

        print("📥 [FeedbackSection] 피드백 로드 시도: \(filePath.path)")

        guard let data = try? Data(contentsOf: filePath) else {
            print("❌ [FeedbackSection] 파일을 찾을 수 없음: \(filePath.path)")
            return
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        if let loaded = try? decoder.decode([ProjectNote].self, from: data) {
            notes = loaded
            print("✅ [FeedbackSection] \(loaded.count)개 피드백 로드 완료")
        }
    }

    private func saveNotes() {
        let fileManager = FileManager.default
        let home = fileManager.homeDirectoryForCurrentUser
        let notesDir = home.appendingPathComponent("Documents/project-notes")

        let folderName = getFolderName(for: app.name)
        let filePath = notesDir.appendingPathComponent("\(folderName).json")

        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601

        guard let data = try? encoder.encode(notes) else { return }
        try? data.write(to: filePath, options: .atomic)

        print("💾 [FeedbackSection] 피드백 저장 완료: \(filePath.path)")
    }
}

// MARK: - Note Card

struct NoteCard: View {
    @Binding var note: ProjectNote
    let onDelete: () -> Void
    let onSave: () -> Void

    @State private var showingVersionInput = false
    @State private var versionInput = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(note.content)
                        .font(.body)
                        .foregroundColor(.primary)

                    Text(formatDate(note.createdAt))
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

            // 상태 표시
            HStack(spacing: 8) {
                Menu {
                    Button(action: {
                        note.status = .pending
                        note.completedAt = nil
                        note.completedVersion = nil
                        onSave()
                    }) {
                        HStack {
                            Image(systemName: NoteStatus.pending.icon)
                            Text(NoteStatus.pending.rawValue)
                        }
                    }

                    Button(action: {
                        note.status = .proposed
                        note.completedAt = nil
                        note.completedVersion = nil
                        onSave()
                    }) {
                        HStack {
                            Image(systemName: NoteStatus.proposed.icon)
                            Text(NoteStatus.proposed.rawValue)
                        }
                    }

                    Button(action: {
                        showingVersionInput = true
                    }) {
                        HStack {
                            Image(systemName: NoteStatus.completed.icon)
                            Text(NoteStatus.completed.rawValue)
                        }
                    }
                } label: {
                    HStack(spacing: 4) {
                        Image(systemName: note.status.icon)
                            .foregroundColor(note.status.color)
                        Text(note.status.rawValue)
                            .font(.caption)
                            .foregroundColor(note.status.color)
                        Image(systemName: "chevron.down")
                            .font(.caption2)
                            .foregroundColor(note.status.color)
                    }
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(note.status.color.opacity(0.1))
                    .cornerRadius(6)
                }
                .menuStyle(.borderlessButton)
                .buttonStyle(.plain)

                Spacer()
            }

            if let completedAt = note.completedAt {
                HStack(spacing: 4) {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                        .font(.caption2)
                    Text("처리 완료: \(formatDate(completedAt))")
                        .font(.caption2)
                        .foregroundColor(.green)
                    if let version = note.completedVersion {
                        Text("(v\(version))")
                            .font(.caption2)
                            .foregroundColor(.green)
                    }
                }
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(note.status.color.opacity(0.3), lineWidth: 1)
        )
        .sheet(isPresented: $showingVersionInput) {
            VersionInputSheet(
                versionInput: $versionInput,
                onSave: {
                    note.status = .completed
                    note.completedAt = Date()
                    note.completedVersion = versionInput.isEmpty ? nil : versionInput
                    showingVersionInput = false
                    onSave()
                }
            )
        }
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy.MM.dd HH:mm"
        return formatter.string(from: date)
    }
}

// MARK: - Version Input Sheet

struct VersionInputSheet: View {
    @Binding var versionInput: String
    let onSave: () -> Void
    @Environment(\.dismiss) var dismiss

    var body: some View {
        VStack(spacing: 20) {
            Text("완료 버전 입력")
                .font(.headline)

            VStack(alignment: .leading, spacing: 8) {
                Text("이 피드백이 완료된 버전을 입력하세요")
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                TextField("예: 1.2.0", text: $versionInput)
                    .textFieldStyle(.roundedBorder)
                    .font(.body)
            }

            HStack(spacing: 12) {
                Button("취소") {
                    dismiss()
                }
                .keyboardShortcut(.escape)

                Button("완료 처리") {
                    onSave()
                    dismiss()
                }
                .keyboardShortcut(.return)
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(24)
        .frame(width: 400)
    }
}

// MARK: - Project Note Model

struct ProjectNote: Identifiable, Codable {
    let id: String
    var content: String
    var status: NoteStatus
    var createdAt: Date
    var completedAt: Date?
    var completedVersion: String?

    init(id: String = UUID().uuidString, content: String, status: NoteStatus = .pending, createdAt: Date = Date(), completedAt: Date? = nil, completedVersion: String? = nil) {
        self.id = id
        self.content = content
        self.status = status
        self.createdAt = createdAt
        self.completedAt = completedAt
        self.completedVersion = completedVersion
    }
}

enum NoteStatus: String, Codable {
    case pending = "처리 전"
    case proposed = "제안 완료"
    case completed = "처리 완료"

    // 기존 데이터 호환성을 위한 커스텀 디코딩
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)

        // 기존 값들을 새로운 값으로 매핑
        switch rawValue {
        case "처리 전", "피드백 필요", "대기":
            self = .pending
        case "제안 완료", "분석중", "처리중", "의사결정", "테스트 중":
            self = .proposed
        case "처리 완료", "배포완료", "처리됨", "완료":
            self = .completed
        default:
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Unknown status value: \(rawValue)"
            )
        }
    }

    var color: Color {
        switch self {
        case .pending: return .orange
        case .proposed: return .blue
        case .completed: return .green
        }
    }

    var icon: String {
        switch self {
        case .pending: return "exclamationmark.bubble.fill"
        case .proposed: return "lightbulb.fill"
        case .completed: return "checkmark.seal.fill"
        }
    }
}

