//
//  CEOfeedbackApp.swift
//  CEOfeedback
//
//  Created by hyunho lee on 1/21/26.
//

import SwiftUI

@main
struct CEOfeedbackApp: App {
    @StateObject private var syncService = iCloudSyncService.shared

    var body: some Scene {
        WindowGroup {
            MainTabView()
                .environmentObject(syncService)
        }
    }
}

// MARK: - Main Tab View

struct MainTabView: View {
    var body: some View {
        TabView {
            AppListView()
                .tabItem {
                    Label("앱", systemImage: "square.grid.2x2.fill")
                }

            SettingsView()
                .tabItem {
                    Label("설정", systemImage: "gearshape.fill")
                }
        }
    }
}

// MARK: - Settings View

struct SettingsView: View {
    @EnvironmentObject var syncService: iCloudSyncService
    @AppStorage("autoSyncEnabled") private var autoSyncEnabled = true
    @State private var isSyncing = false
    @State private var showingSyncAlert = false
    @State private var syncAlertMessage = ""

    var body: some View {
        NavigationStack {
            List {
                // iCloud 상태
                Section("iCloud 연결") {
                    HStack {
                        Image(systemName: syncService.isICloudAvailable ? "checkmark.icloud.fill" : "xmark.icloud.fill")
                            .font(.title2)
                            .foregroundColor(syncService.isICloudAvailable ? .green : .red)

                        VStack(alignment: .leading, spacing: 2) {
                            Text(syncService.isICloudAvailable ? "iCloud 연결됨" : "iCloud에 로그인되지 않음")
                                .font(.headline)
                            Text("iCloud.com.leeo.PortfolioCEO")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(.vertical, 4)
                }

                // 동기화 설정
                Section("동기화") {
                    Toggle("자동 동기화", isOn: $autoSyncEnabled)
                        .disabled(!syncService.isICloudAvailable)

                    HStack {
                        Text("마지막 동기화")
                        Spacer()
                        if let lastSync = syncService.lastSyncDate {
                            Text(lastSync, style: .relative)
                                .foregroundColor(.secondary)
                        } else {
                            Text("없음")
                                .foregroundColor(.secondary)
                        }
                    }

                    Button(action: syncNow) {
                        HStack {
                            if isSyncing {
                                ProgressView()
                                    .scaleEffect(0.8)
                            } else {
                                Image(systemName: "arrow.triangle.2.circlepath")
                            }
                            Text(isSyncing ? "동기화 중..." : "지금 동기화")
                        }
                    }
                    .disabled(!syncService.isICloudAvailable || isSyncing)
                }

                // 동기화 정보
                Section("동기화 정보") {
                    LabeledContent("동기화된 앱", value: "\(syncService.apps.count)개")
                    LabeledContent("내 피드백", value: "\(syncService.feedbacks.count)개")

                    if let error = syncService.syncError {
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(.orange)
                            Text(error)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }

                // 앱 정보
                Section("앱 정보") {
                    LabeledContent("버전", value: "1.0.0")
                    LabeledContent("빌드", value: "1")

                    HStack {
                        Spacer()
                        Text("macOS PortfolioCEO와 연동됩니다")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Spacer()
                    }
                }
            }
            .navigationTitle("설정")
            .onAppear {
                if autoSyncEnabled {
                    syncNow()
                }
            }
            .alert("동기화", isPresented: $showingSyncAlert) {
                Button("확인", role: .cancel) {}
            } message: {
                Text(syncAlertMessage)
            }
        }
    }

    private func syncNow() {
        isSyncing = true
        syncService.loadSyncData()

        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            isSyncing = false
            if let error = syncService.syncError {
                syncAlertMessage = "동기화 실패: \(error)"
                showingSyncAlert = true
            }
        }
    }
}
