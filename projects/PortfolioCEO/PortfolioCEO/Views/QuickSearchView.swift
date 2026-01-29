import SwiftUI

struct QuickSearchView: View {
    @EnvironmentObject var portfolio: PortfolioService
    @State private var searchText = ""
    @Environment(\.dismiss) var dismiss

    var filteredApps: [AppModel] {
        if searchText.isEmpty {
            return portfolio.apps
        }
        return portfolio.apps.filter {
            $0.name.localizedCaseInsensitiveContains(searchText) ||
            $0.nameEn.localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // 검색 바
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.secondary)

                    TextField("앱 검색...", text: $searchText)
                        .textFieldStyle(.plain)

                    if !searchText.isEmpty {
                        Button {
                            searchText = ""
                        } label: {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.secondary)
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding()
                .background(Color(NSColor.controlBackgroundColor))

                Divider()

                // 결과 리스트
                List(filteredApps) { app in
                    Button {
                        // 앱 선택 시 동작
                        dismiss()
                    } label: {
                        HStack {
                            Circle()
                                .fill(app.statusColor)
                                .frame(width: 8, height: 8)

                            VStack(alignment: .leading) {
                                Text(app.name)
                                    .font(.body)
                                Text(app.nameEn)
                                    .font(.body)
                                    .foregroundColor(.secondary)
                            }

                            Spacer()

                            Text("\(Int(app.completionRate))%")
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                    }
                    .buttonStyle(.plain)
                }
            }
            .navigationTitle("앱 검색")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("닫기") {
                        dismiss()
                    }
                }
            }
            .frame(width: 500, height: 400)
        }
    }
}
