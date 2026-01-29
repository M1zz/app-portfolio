import SwiftUI

struct FeedbackSectionView: View {
    let app: AppModel
    let appDetail: AppDetailInfo?
    @EnvironmentObject var portfolioService: PortfolioService

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
                        .font(.body)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(40)
            } else {
                VStack(spacing: 12) {
                    ForEach(notes.sorted { note1, note2 in
                        // 상태별 우선순위: pending > proposed > completed
                        let status1Priority = statusPriority(note1.status)
                        let status2Priority = statusPriority(note2.status)

                        if status1Priority != status2Priority {
                            return status1Priority < status2Priority
                        }

                        // 같은 상태면 날짜 기준 (최신순)
                        return note1.createdAt > note2.createdAt
                    }) { note in
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

    private func statusPriority(_ status: NoteStatus) -> Int {
        switch status {
        case .pending: return 0      // 처리 전 - 가장 먼저
        case .proposed: return 1     // 제안 완료 - 두 번째
        case .completed: return 2    // 처리 완료 - 가장 나중
        }
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

        // 여러 경로 시도 (우선순위 순)
        let possiblePaths = [
            home.appendingPathComponent("Documents/workspace/code/app-portfolio/project-notes"),
            home.appendingPathComponent("Documents/code/app-portfolio/project-notes")
        ]

        var notesDir: URL?
        for path in possiblePaths {
            if fileManager.fileExists(atPath: path.path) {
                notesDir = path
                break
            }
        }

        // 없으면 첫 번째 경로 생성
        if notesDir == nil {
            notesDir = possiblePaths[0]
            try? fileManager.createDirectory(at: notesDir!, withIntermediateDirectories: true)
        }

        let folderName = portfolioService.getFolderName(for: app.name)
        let filePath = notesDir!.appendingPathComponent("\(folderName).json")

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

        // 여러 경로 시도 (우선순위 순)
        let possiblePaths = [
            home.appendingPathComponent("Documents/workspace/code/app-portfolio/project-notes"),
            home.appendingPathComponent("Documents/code/app-portfolio/project-notes")
        ]

        var notesDir: URL?
        for path in possiblePaths {
            if fileManager.fileExists(atPath: path.path) {
                notesDir = path
                break
            }
        }

        // 없으면 첫 번째 경로 사용
        if notesDir == nil {
            notesDir = possiblePaths[0]
        }

        let folderName = portfolioService.getFolderName(for: app.name)
        let filePath = notesDir!.appendingPathComponent("\(folderName).json")

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
                        .font(.body)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Button(action: onDelete) {
                    Image(systemName: "trash")
                        .foregroundColor(.red)
                        .font(.body)
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
                            .font(.body)
                            .foregroundColor(note.status.color)
                        Image(systemName: "chevron.down")
                            .font(.body)
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
                        .font(.body)
                    Text("처리 완료: \(formatDate(completedAt))")
                        .font(.body)
                        .foregroundColor(.green)
                    if let version = note.completedVersion {
                        Text("(v\(version))")
                            .font(.body)
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

// ProjectNote and NoteStatus are defined in AppDetailInfo.swift

