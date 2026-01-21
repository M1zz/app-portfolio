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
            AppListView()
                .environmentObject(syncService)
        }
    }
}
