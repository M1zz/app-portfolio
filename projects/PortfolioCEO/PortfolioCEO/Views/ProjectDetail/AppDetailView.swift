import SwiftUI

struct AppDetailView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @EnvironmentObject var detailService: AppDetailService

    @State private var selectedSection: DetailSection = .feedback

    var appDetail: AppDetailInfo? {
        if let folder = getFolderName(for: app.name) {
            return detailService.loadDetail(for: folder)
        }
        return nil
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

                // 카테고리 및 가격 편집 버튼
                HStack(spacing: 8) {
                    CategoryEditButton(app: app)
                        .environmentObject(portfolioService)

                    PriceEditButton(app: app)
                        .environmentObject(portfolioService)
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

    // MARK: - Helper

    private func getFolderName(for appName: String) -> String? {
        let fileManager = FileManager.default
        let home = fileManager.homeDirectoryForCurrentUser
        let mappingPath = home
            .appendingPathComponent("Documents/code/app-portfolio/data")
            .appendingPathComponent("app-name-mapping.json")

        guard let data = try? Data(contentsOf: mappingPath),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let apps = json["apps"] as? [String: [String: String]],
              let appInfo = apps[appName],
              let folder = appInfo["folder"] else {
            return nil
        }

        return folder
    }
}

// MARK: - Detail Section Enum

enum DetailSection: String, CaseIterable {
    case feedback = "피드백"
    case planning = "기획 의사결정"
    case tasks = "태스크"
    case testing = "테스트"
    case deployment = "배포 준비"

    var icon: String {
        switch self {
        case .feedback: return "bubble.left.and.bubble.right.fill"
        case .planning: return "lightbulb.fill"
        case .tasks: return "checklist"
        case .testing: return "checkmark.shield.fill"
        case .deployment: return "arrow.up.doc.fill"
        }
    }

    var color: Color {
        switch self {
        case .feedback: return .blue
        case .planning: return .yellow
        case .tasks: return .purple
        case .testing: return .orange
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
                        loadCurrentCategories()
                    }
                    .keyboardShortcut(.cancelAction)

                    Spacer()

                    Button("저장") {
                        saveCategories()
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
                .frame(width: 320, height: 300)
        }
    }
}

// MARK: - Price Editor View

struct PriceEditorView: View {
    let app: AppModel
    @EnvironmentObject var portfolioService: PortfolioService
    @Environment(\.dismiss) var dismiss

    @State private var isFree: Bool = true
    @State private var priceUSD: String = ""
    @State private var priceKRW: String = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("가격 설정")
                .font(.headline)
                .padding(.horizontal)
                .padding(.top)

            Divider()

            VStack(alignment: .leading, spacing: 16) {
                Toggle("무료 앱", isOn: $isFree)

                if !isFree {
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
            }
            .padding(.horizontal)

            Spacer()

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
        .onAppear {
            loadCurrentPrice()
        }
    }

    private func loadCurrentPrice() {
        if let price = app.price {
            isFree = price.isFree
            if let usd = price.usd {
                priceUSD = String(format: "%.2f", usd)
            }
            if let krw = price.krw {
                priceKRW = String(krw)
            }
        }
    }

    private func savePrice() {
        let usd = Double(priceUSD)
        let krw = Int(priceKRW)
        let price = AppPrice(usd: usd, krw: krw, isFree: isFree)

        portfolioService.updateAppPrice(appName: app.name, price: price)
    }
}
