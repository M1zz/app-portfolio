import SwiftUI

struct ContentView: View {
    @EnvironmentObject var portfolioService: PortfolioService
    @State private var selectedTab: Tab = .dashboard
    @State private var searchText = ""
    @State private var showingSearch = false
    @State private var showingAIAssistant = false

    enum Tab {
        case dashboard
        case apps
        case kanban
        case workflow
        case featureList
        case vision
        case aiAssistant
    }

    var body: some View {
        NavigationSplitView {
            // 사이드바
            List(selection: $selectedTab) {
                Button(action: { selectedTab = .dashboard }) {
                    Label("대시보드", systemImage: "chart.bar.fill")
                }
                .tag(Tab.dashboard)

                Button(action: { selectedTab = .apps }) {
                    Label("전체 앱", systemImage: "square.grid.2x2.fill")
                }
                .tag(Tab.apps)

                Button(action: { selectedTab = .kanban }) {
                    Label("칸반 보드", systemImage: "rectangle.split.3x1")
                }
                .tag(Tab.kanban)

                Button(action: { selectedTab = .workflow }) {
                    Label("워크플로우", systemImage: "timeline.selection")
                }
                .tag(Tab.workflow)

                Button(action: { selectedTab = .featureList }) {
                    Label("피쳐리스트", systemImage: "star.square.on.square.fill")
                }
                .tag(Tab.featureList)

                Button(action: { selectedTab = .vision }) {
                    Label("비전/컨셉", systemImage: "lightbulb.fill")
                }
                .tag(Tab.vision)

                Button(action: { selectedTab = .aiAssistant }) {
                    Label("AI 어시스턴트", systemImage: "sparkles")
                }
                .tag(Tab.aiAssistant)

                Divider()

                Section("우선순위 높음") {
                    ForEach(portfolioService.highPriorityApps) { app in
                        NavigationLink(value: app) {
                            AppRowView(app: app)
                        }
                    }
                }
            }
            .listStyle(.sidebar)
            .frame(minWidth: 250)
            .searchable(text: $searchText, prompt: "앱 검색 (⌘K)")

        } detail: {
            // 메인 컨텐츠
            Group {
                switch selectedTab {
                case .dashboard:
                    DashboardView()
                case .apps:
                    AppsGridView()
                case .kanban:
                    KanbanView()
                case .workflow:
                    WorkflowTimelineView()
                case .featureList:
                    FeatureListView()
                case .vision:
                    VisionView()
                case .aiAssistant:
                    AIAssistantView()
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .navigationTitle(selectedTab.title)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    portfolioService.loadPortfolio()
                } label: {
                    Label("새로고침", systemImage: "arrow.clockwise")
                }
                .keyboardShortcut("r", modifiers: .command)
            }

            ToolbarItem(placement: .primaryAction) {
                Button {
                    showingSearch.toggle()
                } label: {
                    Label("검색", systemImage: "magnifyingglass")
                }
                .keyboardShortcut("k", modifiers: .command)
            }
        }
        .sheet(isPresented: $showingSearch) {
            QuickSearchView()
                .environmentObject(portfolioService)
        }
    }
}

extension ContentView.Tab {
    var title: String {
        switch self {
        case .dashboard: return "Portfolio Dashboard"
        case .apps: return "전체 앱"
        case .kanban: return "칸반 보드"
        case .workflow: return "워크플로우 타임라인"
        case .featureList: return "피쳐리스트"
        case .vision: return "비전/컨셉"
        case .aiAssistant: return "AI 어시스턴트"
        }
    }
}

struct AppRowView: View {
    let app: AppModel

    var body: some View {
        HStack {
            Circle()
                .fill(app.statusColor)
                .frame(width: 8, height: 8)

            VStack(alignment: .leading, spacing: 2) {
                Text(app.name)
                    .font(.body)

                Text("\(app.stats.done)/\(app.stats.totalTasks)")
                    .font(.body)
                    .foregroundColor(.secondary)
            }
        }
    }
}
