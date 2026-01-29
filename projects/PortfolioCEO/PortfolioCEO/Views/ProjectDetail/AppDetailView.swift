import SwiftUI

struct AppDetailView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @EnvironmentObject var detailService: AppDetailService

    @State private var selectedSection: DetailSection = .feedback

    var appDetail: AppDetailInfo? {
        let folder = portfolioService.getFolderName(for: app.name)
        return detailService.loadDetail(for: folder)
    }

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            headerSection
                .padding()
                .background(Color(NSColor.windowBackgroundColor))

            Divider()

            // 섹션 탭
            sectionTabs
                .padding(.horizontal)
                .padding(.vertical, 12)
                .background(Color(NSColor.windowBackgroundColor))

            Divider()

            // 선택된 섹션 컨텐츠
            ScrollView {
                Group {
                    switch selectedSection {
                    case .feedback:
                        FeedbackSectionView(app: app, appDetail: appDetail)
                    case .planning:
                        PlanningSectionView(app: app)
                    case .tasks:
                        TasksSectionView(app: app)
                    case .testing:
                        TestingSectionView(app: app)
                    case .releaseNotes:
                        ReleaseNotesView(app: app)
                            .environmentObject(portfolioService)
                    case .deployment:
                        DeploymentSectionView(app: app)
                    }
                }
                .padding()
            }
        }
        .navigationTitle(app.name)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                NavigationLink(destination: ProjectDetailView(app: app)) {
                    Label("프로젝트 정보", systemImage: "info.circle")
                }
            }
        }
    }

    // MARK: - Header

    private var headerSection: some View {
        HStack(alignment: .top, spacing: 16) {
            // 상태 아이콘
            Circle()
                .fill(app.statusColor)
                .frame(width: 12, height: 12)
                .padding(.top, 8)

            VStack(alignment: .leading, spacing: 8) {
                Text(app.name)
                    .font(.system(size: 24, weight: .bold))

                if let detail = appDetail, !detail.description.isEmpty {
                    Text(detail.description)
                        .font(.body)
                        .foregroundColor(.secondary)
                }

                HStack(spacing: 16) {
                    Label("v\(app.currentVersion)", systemImage: "number.circle")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    Label(app.status.displayName, systemImage: "circle.fill")
                        .font(.caption)
                        .foregroundColor(app.statusColor)

                    // 가격 정보 표시
                    if let price = app.price {
                        Label(price.displayPrice, systemImage: price.isFree ? "gift.fill" : "dollarsign.circle.fill")
                            .font(.caption)
                            .foregroundColor(price.isFree ? .green : .blue)
                    }

                    if let detail = appDetail {
                        Label(detail.techStack.platforms.joined(separator: ", "), systemImage: "iphone")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                // 카테고리
                if let categories = app.categories, !categories.isEmpty {
                    HStack(spacing: 6) {
                        ForEach(categories.sorted(), id: \.self) { category in
                            Text(category)
                                .font(.caption)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 3)
                                .background(Color.blue.opacity(0.2))
                                .foregroundColor(.blue)
                                .cornerRadius(8)
                        }
                    }
                }

                // 카테고리, 가격 편집 및 링크 버튼
                HStack(spacing: 8) {
                    CategoryEditButton(app: app)
                        .environmentObject(portfolioService)

                    PriceEditButton(app: app)
                        .environmentObject(portfolioService)

                    // App Store 링크 복사 버튼
                    if let appStoreUrl = app.appStoreUrl, !appStoreUrl.isEmpty {
                        AppStoreLinkButton(url: appStoreUrl)
                    }
                }
            }

            Spacer()
        }
    }

    // MARK: - Section Tabs

    private var sectionTabs: some View {
        HStack(spacing: 0) {
            ForEach(DetailSection.allCases, id: \.self) { section in
                Button(action: {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        selectedSection = section
                    }
                }) {
                    VStack(spacing: 8) {
                        Image(systemName: section.icon)
                            .font(.system(size: 20))
                            .foregroundColor(selectedSection == section ? .white : section.color)

                        Text(section.rawValue)
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(selectedSection == section ? .white : .primary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(selectedSection == section ? section.color : Color(NSColor.controlBackgroundColor))
                    .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
            }
        }
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.gray.opacity(0.2), lineWidth: 1)
        )
    }

}

// MARK: - Detail Section Enum

enum DetailSection: String, CaseIterable {
    case feedback = "피드백"
    case planning = "기획 의사결정"
    case tasks = "태스크"
    case testing = "테스트"
    case releaseNotes = "릴리스 노트"
    case deployment = "배포 준비"

    var icon: String {
        switch self {
        case .feedback: return "bubble.left.and.bubble.right.fill"
        case .planning: return "lightbulb.fill"
        case .tasks: return "checklist"
        case .testing: return "checkmark.shield.fill"
        case .releaseNotes: return "doc.text.fill"
        case .deployment: return "arrow.up.doc.fill"
        }
    }

    var color: Color {
        switch self {
        case .feedback: return .blue
        case .planning: return .yellow
        case .tasks: return .purple
        case .testing: return .orange
        case .releaseNotes: return .cyan
        case .deployment: return .green
        }
    }
}

// MARK: - Category Edit Button

struct CategoryEditButton: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @State private var showingCategorySelector = false

    var body: some View {
        Button(action: {
            showingCategorySelector = true
        }) {
            Label("카테고리", systemImage: "tag")
                .font(.caption)
        }
        .buttonStyle(.bordered)
        .controlSize(.small)
        .popover(isPresented: $showingCategorySelector) {
            CategorySelectorView(app: app)
                .environmentObject(portfolioService)
                .frame(width: 300, height: 400)
        }
    }
}

// MARK: - Category Selector

struct CategorySelectorView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) var dismiss
    @State private var selectedCategories: Set<String> = []

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("카테고리 선택")
                .font(.headline)
                .padding()

            if portfolioService.availableCategories.isEmpty {
                VStack(spacing: 12) {
                    Text("카테고리가 없습니다")
                        .foregroundColor(.secondary)

                    Text("Settings에서 카테고리를 먼저 생성해주세요")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                ScrollView {
                    VStack(alignment: .leading, spacing: 8) {
                        ForEach(portfolioService.availableCategories.sorted(), id: \.self) { category in
                            Toggle(isOn: Binding(
                                get: { selectedCategories.contains(category) },
                                set: { isSelected in
                                    if isSelected {
                                        selectedCategories.insert(category)
                                    } else {
                                        selectedCategories.remove(category)
                                    }
                                }
                            )) {
                                Text(category)
                            }
                            .toggleStyle(.checkbox)
                        }
                    }
                    .padding()
                }

                Divider()

                HStack {
                    Button("취소") {
                        dismiss()
                    }
                    .keyboardShortcut(.cancelAction)

                    Spacer()

                    Button("저장") {
                        saveCategories()
                        dismiss()
                    }
                    .keyboardShortcut(.defaultAction)
                    .buttonStyle(.borderedProminent)
                }
                .padding()
            }
        }
        .onAppear {
            loadCurrentCategories()
        }
    }

    private func loadCurrentCategories() {
        selectedCategories = Set(app.categories ?? [])
    }

    private func saveCategories() {
        portfolioService.updateAppCategories(
            appName: app.name,
            categories: Array(selectedCategories)
        )
    }
}

// MARK: - Price Edit Button

struct PriceEditButton: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @State private var showingPriceEditor = false

    var body: some View {
        Button(action: {
            showingPriceEditor = true
        }) {
            Label("가격", systemImage: "dollarsign.circle")
                .font(.caption)
        }
        .buttonStyle(.bordered)
        .controlSize(.small)
        .popover(isPresented: $showingPriceEditor) {
            PriceEditorView(app: app)
                .environmentObject(portfolioService)
        }
    }
}

// MARK: - Price Editor View

struct PriceEditorView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) var dismiss

    @State private var selectedPricingModel: PricingModel = .free
    @State private var priceUSD: String = ""
    @State private var priceKRW: String = ""
    @State private var monthlyUSD: String = ""
    @State private var monthlyKRW: String = ""
    @State private var yearlyUSD: String = ""
    @State private var yearlyKRW: String = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text("가격 설정")
                .font(.headline)
                .padding(.horizontal)
                .padding(.top)
                .padding(.bottom, 12)

            Divider()

            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Picker("가격 모델", selection: $selectedPricingModel) {
                        ForEach(PricingModel.allCases, id: \.self) { model in
                            Text(model.displayName).tag(model)
                        }
                    }

                    if selectedPricingModel == .oneTime {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("USD 가격")
                                .font(.subheadline)
                                .foregroundColor(.secondary)

                            HStack {
                                Text("$")
                                    .foregroundColor(.secondary)
                                TextField("0.99", text: $priceUSD)
                                    .textFieldStyle(.roundedBorder)
                            }
                        }

                        VStack(alignment: .leading, spacing: 8) {
                            Text("KRW 가격")
                                .font(.subheadline)
                                .foregroundColor(.secondary)

                            HStack {
                                Text("₩")
                                    .foregroundColor(.secondary)
                                TextField("1500", text: $priceKRW)
                                    .textFieldStyle(.roundedBorder)
                            }
                        }

                        Text("App Store에 표시되는 가격을 입력하세요")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    if selectedPricingModel == .subscription {
                        Group {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("월간 구독료")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)

                                HStack {
                                    Text("$")
                                        .foregroundColor(.secondary)
                                    TextField("2.99", text: $monthlyUSD)
                                        .textFieldStyle(.roundedBorder)
                                }

                                HStack {
                                    Text("₩")
                                        .foregroundColor(.secondary)
                                    TextField("3900", text: $monthlyKRW)
                                        .textFieldStyle(.roundedBorder)
                                }
                            }

                            VStack(alignment: .leading, spacing: 8) {
                                Text("연간 구독료")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)

                                HStack {
                                    Text("$")
                                        .foregroundColor(.secondary)
                                    TextField("29.99", text: $yearlyUSD)
                                        .textFieldStyle(.roundedBorder)
                                }

                                HStack {
                                    Text("₩")
                                        .foregroundColor(.secondary)
                                    TextField("29000", text: $yearlyKRW)
                                        .textFieldStyle(.roundedBorder)
                                }
                            }
                        }

                        Text("App Store에 표시되는 구독 가격을 입력하세요")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.horizontal)
                .padding(.vertical, 16)
            }

            Divider()

            HStack {
                Button("취소") {
                    dismiss()
                }
                .keyboardShortcut(.cancelAction)

                Spacer()

                Button("저장") {
                    savePrice()
                    dismiss()
                }
                .keyboardShortcut(.defaultAction)
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
        .frame(width: 400, height: 500)
        .onAppear {
            loadCurrentPrice()
        }
    }

    private func loadCurrentPrice() {
        if let price = app.price {
            selectedPricingModel = price.resolvedPricingModel
            if let usd = price.usd {
                priceUSD = String(format: "%.2f", usd)
            }
            if let krw = price.krw {
                priceKRW = String(krw)
            }
            if let musd = price.monthlyUSD {
                monthlyUSD = String(format: "%.2f", musd)
            }
            if let mkrw = price.monthlyKRW {
                monthlyKRW = String(mkrw)
            }
            if let yusd = price.yearlyUSD {
                yearlyUSD = String(format: "%.2f", yusd)
            }
            if let ykrw = price.yearlyKRW {
                yearlyKRW = String(ykrw)
            }
        }
    }

    private func savePrice() {
        let price = AppPrice(
            usd: selectedPricingModel == .oneTime ? Double(priceUSD) : nil,
            krw: selectedPricingModel == .oneTime ? Int(priceKRW) : nil,
            isFree: selectedPricingModel == .free,
            pricingModel: selectedPricingModel,
            monthlyUSD: selectedPricingModel == .subscription ? Double(monthlyUSD) : nil,
            monthlyKRW: selectedPricingModel == .subscription ? Int(monthlyKRW) : nil,
            yearlyUSD: selectedPricingModel == .subscription ? Double(yearlyUSD) : nil,
            yearlyKRW: selectedPricingModel == .subscription ? Int(yearlyKRW) : nil
        )

        portfolioService.updateAppPrice(appName: app.name, price: price)
    }
}

// MARK: - App Store Link Button

struct AppStoreLinkButton: View {
    let url: String
    @State private var showCopied = false

    var body: some View {
        Button(action: {
            copyToClipboard()
        }) {
            HStack(spacing: 4) {
                Image(systemName: showCopied ? "checkmark" : "link")
                Text(showCopied ? "복사됨" : "App Store")
            }
            .font(.caption)
        }
        .buttonStyle(.bordered)
        .controlSize(.small)
        .tint(showCopied ? .green : .blue)
    }

    private func copyToClipboard() {
        let pasteboard = NSPasteboard.general
        pasteboard.clearContents()
        pasteboard.setString(url, forType: .string)

        withAnimation {
            showCopied = true
        }

        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            withAnimation {
                showCopied = false
            }
        }
    }
}
import SwiftUI
import AppKit

struct ReleaseNotesView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService

    @State private var showingAddNote = false
    @State private var selectedNote: ReleaseNote?
    @State private var showingEditNote = false

    private var sortedNotes: [ReleaseNote] {
        (app.releaseNotes ?? []).sorted { note1, note2 in
            compareVersions(note1.version, note2.version) > 0
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            // 헤더
            HStack {
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Image(systemName: "doc.text.fill")
                            .font(.title2)
                            .foregroundColor(.blue)
                        Text("릴리스 노트")
                            .font(.title2)
                            .bold()
                    }
                    Text("버전별 릴리스 노트를 관리합니다")
                        .font(.body)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Button(action: { showingAddNote = true }) {
                    HStack(spacing: 4) {
                        Image(systemName: "plus.circle.fill")
                        Text("새 릴리스 노트")
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color.blue.opacity(0.2))
                    .foregroundColor(.blue)
                    .cornerRadius(8)
                }
                .buttonStyle(.plain)
            }

            Divider()

            // 릴리스 노트 목록
            if sortedNotes.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "doc.text")
                        .font(.system(size: 48))
                        .foregroundColor(.secondary)
                    Text("릴리스 노트가 없습니다")
                        .font(.headline)
                    Text("새 릴리스 노트를 작성하여 버전별 변경사항을 관리하세요")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity)
                .padding(40)
                .background(Color(NSColor.controlBackgroundColor))
                .cornerRadius(12)
            } else {
                ScrollView {
                    VStack(spacing: 16) {
                        ForEach(sortedNotes) { note in
                            ReleaseNoteCard(
                                note: note,
                                onEdit: {
                                    selectedNote = note
                                    showingEditNote = true
                                },
                                onDelete: {
                                    portfolioService.deleteReleaseNote(appName: app.name, releaseNoteId: note.id)
                                }
                            )
                        }
                    }
                }
            }
        }
        .sheet(isPresented: $showingAddNote) {
            ReleaseNoteEditorView(app: app, existingNote: nil)
                .environmentObject(portfolioService)
        }
        .sheet(isPresented: $showingEditNote) {
            if let note = selectedNote {
                ReleaseNoteEditorView(app: app, existingNote: note)
                    .environmentObject(portfolioService)
            }
        }
    }

    private func compareVersions(_ v1: String, _ v2: String) -> Int {
        let parts1 = v1.split(separator: ".").compactMap { Int($0) }
        let parts2 = v2.split(separator: ".").compactMap { Int($0) }

        for i in 0..<max(parts1.count, parts2.count) {
            let part1 = i < parts1.count ? parts1[i] : 0
            let part2 = i < parts2.count ? parts2[i] : 0

            if part1 != part2 {
                return part1 - part2
            }
        }
        return 0
    }
}

// MARK: - Release Note Card

struct ReleaseNoteCard: View {
    let note: ReleaseNote
    let onEdit: () -> Void
    let onDelete: () -> Void

    @State private var showCopiedKo = false
    @State private var showCopiedEn = false
    @State private var isExpanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 헤더
            HStack {
                HStack(spacing: 8) {
                    Image(systemName: "number.circle.fill")
                        .foregroundColor(.blue)
                    Text("v\(note.version)")
                        .font(.headline)
                }

                Spacer()

                Text(formatDate(note.date))
                    .font(.caption)
                    .foregroundColor(.secondary)

                Button(action: onEdit) {
                    Image(systemName: "pencil.circle.fill")
                        .foregroundColor(.blue)
                }
                .buttonStyle(.plain)

                Button(action: onDelete) {
                    Image(systemName: "trash.circle.fill")
                        .foregroundColor(.red)
                }
                .buttonStyle(.plain)
            }

            Divider()

            // 한글 릴리스 노트
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text("한글")
                        .font(.subheadline)
                        .bold()

                    Spacer()

                    Button(action: { copyToClipboard(note.notesKo, language: "ko") }) {
                        HStack(spacing: 4) {
                            Image(systemName: showCopiedKo ? "checkmark" : "doc.on.doc")
                            Text(showCopiedKo ? "복사됨" : "복사")
                        }
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.blue.opacity(0.2))
                        .foregroundColor(.blue)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)
                }

                if !note.notesKo.isEmpty {
                    Text(note.notesKo)
                        .font(.body)
                        .foregroundColor(.primary)
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color(NSColor.textBackgroundColor))
                        .cornerRadius(8)
                } else {
                    Text("릴리스 노트가 작성되지 않았습니다")
                        .font(.body)
                        .foregroundColor(.secondary)
                        .italic()
                }
            }

            Divider()

            // 영문 릴리스 노트
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text("English")
                        .font(.subheadline)
                        .bold()

                    Spacer()

                    Button(action: { copyToClipboard(note.notesEn, language: "en") }) {
                        HStack(spacing: 4) {
                            Image(systemName: showCopiedEn ? "checkmark" : "doc.on.doc")
                            Text(showCopiedEn ? "Copied" : "Copy")
                        }
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.green.opacity(0.2))
                        .foregroundColor(.green)
                        .cornerRadius(6)
                    }
                    .buttonStyle(.plain)
                }

                if !note.notesEn.isEmpty {
                    Text(note.notesEn)
                        .font(.body)
                        .foregroundColor(.primary)
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color(NSColor.textBackgroundColor))
                        .cornerRadius(8)
                } else {
                    Text("Release notes not written")
                        .font(.body)
                        .foregroundColor(.secondary)
                        .italic()
                }
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy.MM.dd"
        return formatter.string(from: date)
    }

    private func copyToClipboard(_ text: String, language: String) {
        let pasteboard = NSPasteboard.general
        pasteboard.clearContents()
        pasteboard.setString(text, forType: .string)

        if language == "ko" {
            showCopiedKo = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                showCopiedKo = false
            }
        } else {
            showCopiedEn = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                showCopiedEn = false
            }
        }
    }
}

// MARK: - Release Note Editor

struct ReleaseNoteEditorView: View {
    let app: AppModel
    let existingNote: ReleaseNote?

    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) var dismiss

    @State private var version: String = ""
    @State private var notesKo: String = ""
    @State private var notesEn: String = ""
    @State private var date: Date = Date()

    var body: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack {
                Text(existingNote == nil ? "새 릴리스 노트" : "릴리스 노트 편집")
                    .font(.headline)

                Spacer()

                Button("취소") {
                    dismiss()
                }
                .keyboardShortcut(.cancelAction)
            }
            .padding()

            Divider()

            // 입력 폼
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // 버전 및 날짜
                    HStack(spacing: 20) {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("버전")
                                .font(.subheadline)
                                .bold()
                            TextField("1.0.0", text: $version)
                                .textFieldStyle(.roundedBorder)
                        }

                        VStack(alignment: .leading, spacing: 8) {
                            Text("날짜")
                                .font(.subheadline)
                                .bold()
                            DatePicker("", selection: $date, displayedComponents: .date)
                                .labelsHidden()
                        }
                    }

                    Divider()

                    // 한글 릴리스 노트
                    VStack(alignment: .leading, spacing: 8) {
                        Text("한글 릴리스 노트")
                            .font(.subheadline)
                            .bold()

                        TextEditor(text: $notesKo)
                            .frame(minHeight: 150)
                            .padding(8)
                            .background(Color(NSColor.textBackgroundColor))
                            .cornerRadius(8)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                            )

                        Text("예시:\n• 새로운 기능 추가\n• 성능 개선\n• 버그 수정")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    Divider()

                    // 영문 릴리스 노트
                    VStack(alignment: .leading, spacing: 8) {
                        Text("English Release Notes")
                            .font(.subheadline)
                            .bold()

                        TextEditor(text: $notesEn)
                            .frame(minHeight: 150)
                            .padding(8)
                            .background(Color(NSColor.textBackgroundColor))
                            .cornerRadius(8)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                            )

                        Text("Example:\n• New features added\n• Performance improvements\n• Bug fixes")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
            }

            Divider()

            // 하단 버튼
            HStack {
                Spacer()

                Button("저장") {
                    saveReleaseNote()
                    dismiss()
                }
                .keyboardShortcut(.defaultAction)
                .buttonStyle(.borderedProminent)
                .disabled(version.isEmpty)
            }
            .padding()
        }
        .frame(width: 600, height: 700)
        .onAppear {
            if let note = existingNote {
                version = note.version
                notesKo = note.notesKo
                notesEn = note.notesEn
                date = note.date
            } else {
                version = app.currentVersion
            }
        }
    }

    private func saveReleaseNote() {
        let note = ReleaseNote(
            id: existingNote?.id ?? UUID().uuidString,
            version: version,
            date: date,
            notesKo: notesKo,
            notesEn: notesEn
        )

        if existingNote != nil {
            portfolioService.updateReleaseNote(appName: app.name, releaseNote: note)
        } else {
            portfolioService.addReleaseNote(appName: app.name, releaseNote: note)
        }
    }
}
