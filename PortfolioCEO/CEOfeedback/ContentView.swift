//
//  ContentView.swift
//  CEOfeedback
//
//  Created by hyunho lee on 1/21/26.
//

import SwiftUI

// MARK: - App List View

struct AppListView: View {
    @EnvironmentObject var syncService: iCloudSyncService
    @State private var searchText = ""

    var filteredApps: [AppSummary] {
        if searchText.isEmpty {
            return syncService.apps
        }
        return syncService.apps.filter {
            $0.name.localizedCaseInsensitiveContains(searchText) ||
            $0.nameEn.localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        NavigationStack {
            Group {
                if syncService.isLoading {
                    ProgressView("동기화 중...")
                } else if syncService.apps.isEmpty {
                    emptyStateView
                } else {
                    appListContent
                }
            }
            .navigationTitle("내 앱")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: { syncService.loadSyncData() }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
            .searchable(text: $searchText, prompt: "앱 검색")
        }
    }

    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Image(systemName: "icloud.slash")
                .font(.system(size: 60))
                .foregroundColor(.secondary)

            Text("동기화된 앱이 없습니다")
                .font(.headline)

            Text("macOS의 PortfolioCEO에서\n동기화를 시작해주세요")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)

            if !syncService.isICloudAvailable {
                Text("iCloud가 활성화되지 않았습니다")
                    .font(.caption)
                    .foregroundColor(.red)
            }

            Button("새로고침") {
                syncService.loadSyncData()
            }
            .buttonStyle(.bordered)
        }
        .padding()
    }

    private var appListContent: some View {
        List {
            // iCloud 상태
            Section {
                HStack {
                    Image(systemName: syncService.isICloudAvailable ? "checkmark.icloud.fill" : "xmark.icloud")
                        .foregroundColor(syncService.isICloudAvailable ? .green : .red)
                    Text(syncService.isICloudAvailable ? "iCloud 연결됨" : "iCloud 연결 안됨")
                        .font(.subheadline)
                    Spacer()
                    if let date = syncService.lastSyncDate {
                        Text(date, style: .relative)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }

            // 앱 목록
            Section("앱 목록 (\(filteredApps.count)개)") {
                ForEach(filteredApps) { app in
                    NavigationLink(destination: AppDetailView(app: app)) {
                        AppRowView(app: app)
                    }
                }
            }
        }
    }
}

// MARK: - App Row View

struct AppRowView: View {
    let app: AppSummary
    @EnvironmentObject var syncService: iCloudSyncService

    var feedbackCount: Int {
        syncService.feedbacks(for: app.bundleId).count
    }

    var body: some View {
        HStack(spacing: 12) {
            // 앱 아이콘 플레이스홀더
            RoundedRectangle(cornerRadius: 12)
                .fill(statusColor.opacity(0.2))
                .frame(width: 50, height: 50)
                .overlay(
                    Text(String(app.name.prefix(1)))
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(statusColor)
                )

            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(app.name)
                        .font(.headline)

                    if feedbackCount > 0 {
                        Text("\(feedbackCount)")
                            .font(.caption2)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color.orange)
                            .clipShape(Capsule())
                    }
                }

                Text("v\(app.currentVersion)")
                    .font(.caption)
                    .foregroundColor(.secondary)

                // 진행률
                HStack(spacing: 4) {
                    ProgressView(value: app.stats.completionRate, total: 100)
                        .frame(width: 60)

                    Text("\(Int(app.stats.completionRate))%")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }

            Spacer()

            // 상태 배지
            Text(app.status)
                .font(.caption2)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(statusColor.opacity(0.2))
                .foregroundColor(statusColor)
                .clipShape(Capsule())
        }
        .padding(.vertical, 4)
    }

    private var statusColor: Color {
        switch app.status {
        case "active": return .green
        case "planning": return .orange
        case "maintenance": return .blue
        default: return .gray
        }
    }
}

// MARK: - App Detail View

struct AppDetailView: View {
    let app: AppSummary
    @EnvironmentObject var syncService: iCloudSyncService
    @State private var showingFeedbackForm = false

    var feedbacks: [AppFeedback] {
        syncService.feedbacks(for: app.bundleId)
    }

    var body: some View {
        List {
            // 앱 정보
            Section("앱 정보") {
                LabeledContent("버전", value: app.currentVersion)
                LabeledContent("상태", value: app.status)
                LabeledContent("우선순위", value: app.priority)
            }

            // 진행 현황
            Section("진행 현황") {
                HStack {
                    VStack(alignment: .leading) {
                        Text("완료")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("\(app.stats.done)")
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(.green)
                    }
                    Spacer()
                    VStack(alignment: .leading) {
                        Text("진행 중")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("\(app.stats.inProgress)")
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(.orange)
                    }
                    Spacer()
                    VStack(alignment: .leading) {
                        Text("대기")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("\(app.stats.notStarted)")
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(.gray)
                    }
                }
                .padding(.vertical, 8)

                ProgressView(value: app.stats.completionRate, total: 100) {
                    Text("전체 진행률: \(Int(app.stats.completionRate))%")
                        .font(.caption)
                }
            }

            // 다음 할 일
            if !app.nextTasks.isEmpty {
                Section("다음 할 일") {
                    ForEach(app.nextTasks, id: \.self) { task in
                        HStack {
                            Image(systemName: "circle")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text(task)
                                .font(.subheadline)
                        }
                    }
                }
            }

            // 피드백
            Section {
                Button(action: { showingFeedbackForm = true }) {
                    Label("피드백 남기기", systemImage: "plus.bubble.fill")
                }

                if feedbacks.isEmpty {
                    Text("아직 피드백이 없습니다")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                } else {
                    ForEach(feedbacks) { feedback in
                        FeedbackRowView(feedback: feedback)
                    }
                    .onDelete(perform: deleteFeedback)
                }
            } header: {
                Text("피드백 (\(feedbacks.count))")
            }
        }
        .navigationTitle(app.name)
        .sheet(isPresented: $showingFeedbackForm) {
            FeedbackFormView(app: app)
        }
    }

    private func deleteFeedback(at offsets: IndexSet) {
        for index in offsets {
            syncService.deleteFeedback(id: feedbacks[index].id)
        }
    }
}

// MARK: - Feedback Row View

struct FeedbackRowView: View {
    let feedback: AppFeedback

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(feedback.category.rawValue)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 2)
                    .background(categoryColor.opacity(0.2))
                    .foregroundColor(categoryColor)
                    .clipShape(Capsule())

                Spacer()

                Text(feedback.status.rawValue)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }

            Text(feedback.content)
                .font(.subheadline)
                .lineLimit(3)

            Text(feedback.createdAt, style: .relative)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 4)
    }

    private var categoryColor: Color {
        switch feedback.category {
        case .bug: return .red
        case .feature: return .blue
        case .improvement: return .purple
        case .question: return .orange
        case .other: return .gray
        }
    }
}

// MARK: - Feedback Form View

struct FeedbackFormView: View {
    let app: AppSummary
    @EnvironmentObject var syncService: iCloudSyncService
    @Environment(\.dismiss) var dismiss

    @State private var content = ""
    @State private var category: AppFeedback.FeedbackCategory = .feature

    var body: some View {
        NavigationStack {
            Form {
                Section("카테고리") {
                    Picker("카테고리", selection: $category) {
                        ForEach(AppFeedback.FeedbackCategory.allCases, id: \.self) { cat in
                            Text(cat.rawValue).tag(cat)
                        }
                    }
                    .pickerStyle(.segmented)
                }

                Section("피드백 내용") {
                    TextEditor(text: $content)
                        .frame(minHeight: 150)
                }

                Section {
                    Text("이 피드백은 \(app.name)에 대한 것입니다")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("피드백 작성")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("취소") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("저장") {
                        saveFeedback()
                    }
                    .disabled(content.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            }
        }
    }

    private func saveFeedback() {
        let feedback = AppFeedback(
            appBundleId: app.bundleId,
            appName: app.name,
            content: content.trimmingCharacters(in: .whitespacesAndNewlines),
            category: category
        )
        syncService.addFeedback(feedback)
        dismiss()
    }
}

#Preview {
    AppListView()
        .environmentObject(iCloudSyncService.shared)
}
