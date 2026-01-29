import SwiftUI
import AppKit

struct PlanningDocumentView: View {
    let document: String
    let title: String
    @Environment(\.dismiss) var dismiss

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.title2)
                        .bold()
                    Text("\(document.components(separatedBy: "\n").count) 줄")
                        .font(.body)
                        .foregroundColor(.secondary)
                }

                Spacer()

                HStack(spacing: 12) {
                    Button(action: copyToClipboard) {
                        HStack(spacing: 4) {
                            Image(systemName: "doc.on.doc")
                            Text("복사")
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.blue.opacity(0.2))
                        .foregroundColor(.blue)
                        .cornerRadius(8)
                    }
                    .buttonStyle(.plain)

                    Button(action: saveToFile) {
                        HStack(spacing: 4) {
                            Image(systemName: "square.and.arrow.down")
                            Text("저장")
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.green.opacity(0.2))
                        .foregroundColor(.green)
                        .cornerRadius(8)
                    }
                    .buttonStyle(.plain)

                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.title3)
                            .foregroundColor(.secondary)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding()
            .background(Color(NSColor.windowBackgroundColor))

            Divider()

            // 문서 내용
            ScrollView {
                Text(document)
                    .font(.system(size: 13, design: .monospaced))
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
            }
            .background(Color(NSColor.textBackgroundColor))
        }
        .frame(width: 900, height: 700)
    }

    private func copyToClipboard() {
        let pasteboard = NSPasteboard.general
        pasteboard.clearContents()
        pasteboard.setString(document, forType: .string)

        // TODO: 사용자에게 복사 완료 알림
    }

    private func saveToFile() {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd-HHmm"
        let timestamp = dateFormatter.string(from: Date())

        let filename = title.replacingOccurrences(of: " ", with: "-") + "-" + timestamp

        if let url = PlanningDocumentGenerator.shared.savePlanToFile(content: document, filename: filename) {
            // 파일 저장 성공 - Finder에서 보여주기
            NSWorkspace.shared.activateFileViewerSelecting([url])
        }
    }
}

// MARK: - 미리보기용 래퍼

struct PlanningDocumentPreview: View {
    @Binding var isPresented: Bool
    let document: String
    let title: String

    var body: some View {
        if isPresented {
            Color.black.opacity(0.3)
                .ignoresSafeArea()
                .overlay(
                    PlanningDocumentView(document: document, title: title)
                        .background(Color(NSColor.windowBackgroundColor))
                        .cornerRadius(12)
                        .shadow(radius: 20)
                )
                .onTapGesture {
                    // 배경 클릭 시 닫기
                }
        }
    }
}
