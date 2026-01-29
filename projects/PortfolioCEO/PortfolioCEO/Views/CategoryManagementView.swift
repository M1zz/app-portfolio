import SwiftUI

struct CategoryManagementView: View {
    @EnvironmentObject var portfolio: PortfolioService
    @State private var newCategoryName = ""
    @State private var editingCategory: String?
    @State private var editedName = ""
    @State private var showingDeleteAlert = false
    @State private var categoryToDelete: String?
    @State private var deleteError: String?

    var body: some View {
        Form {
            Section("새 카테고리 추가") {
                HStack {
                    TextField("카테고리 이름", text: $newCategoryName)
                        .textFieldStyle(.roundedBorder)

                    Button("추가") {
                        addCategory()
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(newCategoryName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            }

            Section("카테고리 목록 (\(portfolio.availableCategories.count)개)") {
                if portfolio.availableCategories.isEmpty {
                    Text("카테고리가 없습니다")
                        .foregroundColor(.secondary)
                        .italic()
                } else {
                    ForEach(portfolio.availableCategories.sorted(), id: \.self) { category in
                        HStack {
                            if editingCategory == category {
                                TextField("카테고리 이름", text: $editedName)
                                    .textFieldStyle(.roundedBorder)

                                Button("저장") {
                                    saveEdit()
                                }
                                .buttonStyle(.bordered)

                                Button("취소") {
                                    cancelEdit()
                                }
                                .buttonStyle(.bordered)
                            } else {
                                Text(category)
                                    .font(.body)

                                Spacer()

                                Button(action: {
                                    startEditing(category)
                                }) {
                                    Image(systemName: "pencil")
                                }
                                .buttonStyle(.borderless)

                                Button(role: .destructive, action: {
                                    attemptDelete(category)
                                }) {
                                    Image(systemName: "trash")
                                }
                                .buttonStyle(.borderless)
                            }
                        }
                    }
                }
            }
        }
        .formStyle(.grouped)
        .frame(width: 500, height: 400)
        .alert("카테고리 삭제 불가", isPresented: $showingDeleteAlert) {
            Button("확인", role: .cancel) {
                deleteError = nil
            }
        } message: {
            if let error = deleteError {
                Text(error)
            }
        }
    }

    private func addCategory() {
        portfolio.addCategory(newCategoryName)
        newCategoryName = ""
    }

    private func startEditing(_ category: String) {
        editingCategory = category
        editedName = category
    }

    private func saveEdit() {
        guard let old = editingCategory else { return }
        portfolio.renameCategory(old: old, new: editedName)
        editingCategory = nil
        editedName = ""
    }

    private func cancelEdit() {
        editingCategory = nil
        editedName = ""
    }

    private func attemptDelete(_ category: String) {
        // 사용 중인지 확인
        let isInUse = portfolio.apps.contains { app in
            app.categories?.contains(category) ?? false
        }

        if isInUse {
            let usingApps = portfolio.apps.filter { app in
                app.categories?.contains(category) ?? false
            }.map { $0.name }.joined(separator: ", ")

            deleteError = "'\(category)' 카테고리는 다음 앱에서 사용 중입니다:\n\(usingApps)\n\n먼저 앱에서 카테고리를 제거해주세요."
            showingDeleteAlert = true
        } else {
            portfolio.removeCategory(category)
        }
    }
}
