import SwiftUI

/// 워크플로우 타임라인 메인 뷰
struct WorkflowTimelineView: View {
    @EnvironmentObject var portfolioService: PortfolioService
    @State private var selectedApp: AppModel?
    @State private var timelineData: TimelineData = TimelineData()
    @State private var zoomLevel: Double = 1.0

    // 필터 바 표시/숨김
    @State private var showAppFilters: Bool = true
    @State private var showTaskFilters: Bool = true

    // 앱 카드 필터 및 정렬
    @State private var appSortOrder: AppSortOrder = .default
    @State private var showOnlyWithBottleneck: Bool = false
    @State private var showOnlyWithSchedule: Bool = false
    @State private var showOnlyHighPriority: Bool = false

    enum AppSortOrder: String, CaseIterable {
        case `default` = "기본"
        case bottleneck = "병목 많은 순"
        case inProgress = "진행중 많은 순"
        case schedule = "일정 많은 순"
        case priority = "우선순위 높은 순"
    }

    // 태스크 필터 및 정렬
    @State private var selectedStatuses: Set<TaskStatus> = [.done, .inProgress, .todo, .notStarted]
    @State private var showBottleneckOnly: Bool = false
    @State private var selectedVersion: String? = nil
    @State private var sortOrder: SortOrder = .date

    enum SortOrder: String, CaseIterable {
        case date = "날짜순"
        case status = "상태별"
        case version = "버전별"
    }

    var body: some View {
        VStack(spacing: 0) {
            // 앱 선택 필터/정렬 바
            appFilterSortBar

            // 상단 컨트롤
            topControlBar

            // 태스크 필터 및 정렬 바
            if selectedApp != nil {
                taskFilterSortBar
                Divider()
            }

            // 타임라인 캔버스
            if let app = selectedApp {
                if timelineData.tasks.isEmpty {
                    emptyStateView
                } else {
                    timelineCanvas
                }
            } else {
                placeholderView
            }
        }
        .onChange(of: selectedApp) { _, newApp in
            updateTimeline(for: newApp)
        }
        .onChange(of: selectedStatuses) { _, _ in
            updateTimeline(for: selectedApp)
        }
        .onChange(of: showBottleneckOnly) { _, _ in
            updateTimeline(for: selectedApp)
        }
        .onChange(of: selectedVersion) { _, _ in
            updateTimeline(for: selectedApp)
        }
        .onChange(of: sortOrder) { _, _ in
            updateTimeline(for: selectedApp)
        }
        .onAppear {
            // 첫 번째 앱을 기본 선택
            if selectedApp == nil, let firstApp = portfolioService.apps.first {
                selectedApp = firstApp
                updateTimeline(for: firstApp)
            }
        }
    }

    // MARK: - App Filter and Sort Bar

    private var appFilterSortBar: some View {
        VStack(spacing: 0) {
            // 헤더 (항상 표시)
            HStack(spacing: 12) {
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        showAppFilters.toggle()
                    }
                } label: {
                    HStack(spacing: 8) {
                        Image(systemName: showAppFilters ? "chevron.down" : "chevron.right")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("앱 선택")
                            .font(.headline)
                    }
                }
                .buttonStyle(.plain)

                if !showAppFilters {
                    Text("\(filteredAndSortedApps.count)개 앱")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    if isAppFilterActive {
                        Image(systemName: "line.3.horizontal.decrease.circle.fill")
                            .font(.caption)
                            .foregroundColor(.blue)
                    }
                }

                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .background(Color.gray.opacity(0.08))
            .contentShape(Rectangle())
            .onTapGesture {
                withAnimation(.easeInOut(duration: 0.2)) {
                    showAppFilters.toggle()
                }
            }

            // 필터/정렬 컨트롤 (접을 수 있음)
            if showAppFilters {
                HStack(spacing: 16) {
                    // 정렬
                    HStack(spacing: 8) {
                        Text("정렬:")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        Picker("앱 정렬", selection: $appSortOrder) {
                            ForEach(AppSortOrder.allCases, id: \.self) { order in
                                Text(order.rawValue).tag(order)
                            }
                        }
                        .pickerStyle(.menu)
                        .frame(width: 140)
                    }

                    Divider()
                        .frame(height: 20)

                    // 필터
                    HStack(spacing: 8) {
                        Text("필터:")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        Toggle(isOn: $showOnlyWithBottleneck) {
                            HStack(spacing: 4) {
                                Image(systemName: "exclamationmark.triangle.fill")
                                    .font(.caption2)
                                Text("병목")
                                    .font(.caption)
                            }
                        }
                        .toggleStyle(.button)
                        .tint(.red)

                        Toggle(isOn: $showOnlyWithSchedule) {
                            HStack(spacing: 4) {
                                Image(systemName: "calendar")
                                    .font(.caption2)
                                Text("일정")
                                    .font(.caption)
                            }
                        }
                        .toggleStyle(.button)
                        .tint(.blue)

                        Toggle(isOn: $showOnlyHighPriority) {
                            HStack(spacing: 4) {
                                Image(systemName: "star.fill")
                                    .font(.caption2)
                                Text("우선순위")
                                    .font(.caption)
                            }
                        }
                        .toggleStyle(.button)
                        .tint(.orange)
                    }

                    Spacer()

                    // 앱 카운트
                    Text("\(filteredAndSortedApps.count)개 앱")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    // 초기화
                    if isAppFilterActive {
                        Button {
                            appSortOrder = .default
                            showOnlyWithBottleneck = false
                            showOnlyWithSchedule = false
                            showOnlyHighPriority = false
                        } label: {
                            HStack(spacing: 4) {
                                Image(systemName: "arrow.counterclockwise")
                                    .font(.caption)
                                Text("초기화")
                                    .font(.caption)
                            }
                        }
                        .buttonStyle(.bordered)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(Color.gray.opacity(0.05))
            }
        }
    }

    // MARK: - Top Control Bar

    private var topControlBar: some View {
        VStack(spacing: 0) {
            // 앱 선택 가로 스크롤 카드
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(filteredAndSortedApps) { app in
                        appCardView(for: app)
                            .onTapGesture {
                                withAnimation(.easeInOut(duration: 0.2)) {
                                    selectedApp = app
                                }
                            }
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
            }
            .background(Color.gray.opacity(0.05))

            Divider()

            // 줌 및 통계 컨트롤
            HStack(spacing: 16) {
                // 줌 컨트롤
                HStack(spacing: 8) {
                    Text("줌:")
                        .foregroundColor(.secondary)
                    Button {
                        zoomLevel = max(0.5, zoomLevel - 0.25)
                    } label: {
                        Image(systemName: "minus.magnifyingglass")
                    }
                    .disabled(zoomLevel <= 0.5)

                    Text("\(Int(zoomLevel * 100))%")
                        .frame(width: 50)
                        .foregroundColor(.secondary)

                    Button {
                        zoomLevel = min(3.0, zoomLevel + 0.25)
                    } label: {
                        Image(systemName: "plus.magnifyingglass")
                    }
                    .disabled(zoomLevel >= 3.0)

                    Button {
                        zoomLevel = 1.0
                    } label: {
                        Text("초기화")
                    }
                }

                Spacer()

                // 통계
                if let app = selectedApp {
                    HStack(spacing: 16) {
                        HStack(spacing: 4) {
                            Image(systemName: "calendar")
                                .font(.caption)
                                .foregroundColor(.blue)
                            Text("\(timelineData.tasks.count)개 태스크")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }

                        if timelineData.tasks.contains(where: { $0.isBottleneck }) {
                            HStack(spacing: 4) {
                                Image(systemName: "exclamationmark.triangle.fill")
                                    .font(.caption)
                                    .foregroundColor(.red)
                                Text("\(timelineData.tasks.filter { $0.isBottleneck }.count)개 병목")
                                    .font(.caption)
                                    .fontWeight(.semibold)
                                    .foregroundColor(.red)
                            }
                        }
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
        }
    }

    // MARK: - Task Filter and Sort Bar

    private var taskFilterSortBar: some View {
        VStack(spacing: 0) {
            // 헤더 (항상 표시)
            HStack(spacing: 12) {
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        showTaskFilters.toggle()
                    }
                } label: {
                    HStack(spacing: 8) {
                        Image(systemName: showTaskFilters ? "chevron.down" : "chevron.right")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("태스크 필터/정렬")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.secondary)
                    }
                }
                .buttonStyle(.plain)

                if !showTaskFilters {
                    Text("\(timelineData.tasks.count)개 태스크")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    if isTaskFilterActive {
                        Image(systemName: "line.3.horizontal.decrease.circle.fill")
                            .font(.caption)
                            .foregroundColor(.blue)
                    }
                }

                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(Color.gray.opacity(0.05))
            .contentShape(Rectangle())
            .onTapGesture {
                withAnimation(.easeInOut(duration: 0.2)) {
                    showTaskFilters.toggle()
                }
            }

            // 필터/정렬 컨트롤 (접을 수 있음)
            if showTaskFilters {
                HStack(spacing: 16) {
                    // 정렬
                    HStack(spacing: 8) {
                        Text("정렬:")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        Picker("정렬", selection: $sortOrder) {
                            ForEach(SortOrder.allCases, id: \.self) { order in
                                Text(order.rawValue).tag(order)
                            }
                        }
                        .pickerStyle(.segmented)
                        .frame(width: 200)
                    }

                    Divider()
                        .frame(height: 20)

                    // 상태 필터
                    HStack(spacing: 8) {
                        Text("상태:")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        statusFilterButton(status: .done, label: "완료", color: .green)
                        statusFilterButton(status: .inProgress, label: "진행중", color: .orange)
                        statusFilterButton(status: .todo, label: "진행전", color: .blue)
                        statusFilterButton(status: .notStarted, label: "대기", color: .gray)
                    }

                    Divider()
                        .frame(height: 20)

                    // 병목 필터
                    Toggle(isOn: $showBottleneckOnly) {
                        HStack(spacing: 4) {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .font(.caption)
                                .foregroundColor(.red)
                            Text("병목만")
                                .font(.caption)
                                .fontWeight(.medium)
                        }
                    }
                    .toggleStyle(.button)
                    .tint(.red)

                    // 버전 필터
                    if let app = selectedApp {
                        let versions = getUniqueVersions(from: app)
                        if versions.count > 1 {
                            Divider()
                                .frame(height: 20)

                            Menu {
                                Button("전체 버전") {
                                    selectedVersion = nil
                                }
                                Divider()
                                ForEach(versions, id: \.self) { version in
                                    Button("v\(version)") {
                                        selectedVersion = version
                                    }
                                }
                            } label: {
                                HStack(spacing: 4) {
                                    Image(systemName: "number.circle")
                                        .font(.caption)
                                    Text(selectedVersion.map { "v\($0)" } ?? "전체 버전")
                                        .font(.caption)
                                    Image(systemName: "chevron.down")
                                        .font(.caption2)
                                }
                                .foregroundColor(.secondary)
                            }
                        }
                    }

                    Spacer()

                    // 태스크 필터 초기화
                    if isTaskFilterActive {
                        Button {
                            selectedStatuses = [.done, .inProgress, .todo, .notStarted]
                            showBottleneckOnly = false
                            selectedVersion = nil
                            sortOrder = .date
                        } label: {
                            HStack(spacing: 4) {
                                Image(systemName: "arrow.counterclockwise")
                                    .font(.caption)
                                Text("초기화")
                                    .font(.caption)
                            }
                        }
                        .buttonStyle(.bordered)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(Color.gray.opacity(0.03))
            }
        }
    }

    private func statusFilterButton(status: TaskStatus, label: String, color: Color) -> some View {
        let isSelected = selectedStatuses.contains(status)

        return Button {
            if isSelected {
                selectedStatuses.remove(status)
            } else {
                selectedStatuses.insert(status)
            }
        } label: {
            Text(label)
                .font(.caption)
                .fontWeight(isSelected ? .semibold : .regular)
                .foregroundColor(isSelected ? .white : color)
                .padding(.horizontal, 10)
                .padding(.vertical, 5)
                .background(isSelected ? color : Color.clear)
                .cornerRadius(6)
                .overlay(
                    RoundedRectangle(cornerRadius: 6)
                        .strokeBorder(color, lineWidth: 1)
                )
        }
        .buttonStyle(.plain)
    }

    // MARK: - App Card View

    /// 앱 선택 카드 뷰
    private func appCardView(for app: AppModel) -> some View {
        let isSelected = selectedApp?.id == app.id
        let tasksWithDate = app.allTasks.filter { $0.parsedTargetDate != nil }
        let bottleneckCount = countBottlenecks(in: app)

        return VStack(alignment: .leading, spacing: 8) {
            // 앱 이름 + 우선순위
            HStack(spacing: 8) {
                Text(app.name)
                    .font(.headline)
                    .foregroundColor(isSelected ? .white : .primary)
                    .lineLimit(1)

                if app.priority == .high {
                    Image(systemName: "exclamationmark.circle.fill")
                        .font(.caption)
                        .foregroundColor(isSelected ? .white : .red)
                }

                Spacer()
            }

            // 통계 배지들
            HStack(spacing: 8) {
                // 일정 태스크
                if !tasksWithDate.isEmpty {
                    Label("\(tasksWithDate.count)", systemImage: "calendar")
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(isSelected ? .white : .blue)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(isSelected ? Color.white.opacity(0.3) : Color.blue.opacity(0.15))
                        .cornerRadius(6)
                } else {
                    Label("일정없음", systemImage: "calendar.badge.exclamationmark")
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(isSelected ? .white.opacity(0.7) : .gray)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(isSelected ? Color.white.opacity(0.2) : Color.gray.opacity(0.15))
                        .cornerRadius(6)
                }

                // 진행중
                if app.stats.inProgress > 0 {
                    Label("\(app.stats.inProgress)", systemImage: "arrow.right.circle.fill")
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(isSelected ? .white : .orange)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(isSelected ? Color.white.opacity(0.3) : Color.orange.opacity(0.15))
                        .cornerRadius(6)
                }

                // 병목
                if bottleneckCount > 0 {
                    Label("\(bottleneckCount)", systemImage: "exclamationmark.triangle.fill")
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.red)
                        .cornerRadius(6)
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .frame(width: 200)
        .background(
            RoundedRectangle(cornerRadius: 10)
                .fill(isSelected ? Color.blue : Color.white)
                .shadow(color: Color.black.opacity(isSelected ? 0.2 : 0.1), radius: isSelected ? 8 : 4)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .strokeBorder(isSelected ? Color.blue.opacity(0.5) : Color.clear, lineWidth: 2)
        )
        .scaleEffect(isSelected ? 1.05 : 1.0)
    }

    // MARK: - Timeline Canvas

    private var timelineCanvas: some View {
        ScrollView([.horizontal, .vertical], showsIndicators: true) {
            GeometryReader { geometry in
                ZStack(alignment: .topLeading) {
                    // 배경 그리드
                    timelineGrid

                    // 버전 마일스톤
                    ForEach(timelineData.milestones) { milestone in
                        VersionMilestoneView(
                            milestone: milestone,
                            config: timelineData.config,
                            zoomLevel: zoomLevel,
                            timelineWidth: timelineData.canvasWidth
                        )
                    }

                    // 연결선
                    let connections = TimelineInferenceEngine.inferConnections(timelineTasks: timelineData.tasks)
                    ForEach(connections) { connection in
                        TimelineConnectorView(
                            connection: connection,
                            config: timelineData.config,
                            zoomLevel: zoomLevel,
                            timelineWidth: timelineData.canvasWidth
                        )
                    }

                    // 태스크 노드
                    ForEach(timelineData.tasks) { timelineTask in
                        TimelineNodeView(
                            timelineTask: timelineTask,
                            config: timelineData.config,
                            zoomLevel: zoomLevel,
                            timelineWidth: timelineData.canvasWidth
                        )
                    }

                    // 현재 위치 표시기
                    TimelineProgressIndicatorView(
                        currentDate: Date(),
                        startDate: timelineData.startDate,
                        endDate: timelineData.endDate,
                        config: timelineData.config,
                        zoomLevel: zoomLevel,
                        canvasHeight: timelineData.canvasHeight
                    )
                }
                .frame(
                    width: timelineData.canvasWidth * zoomLevel,
                    height: timelineData.canvasHeight * zoomLevel
                )
            }
            .frame(
                width: timelineData.canvasWidth * zoomLevel,
                height: timelineData.canvasHeight * zoomLevel
            )
        }
    }

    // MARK: - Timeline Grid

    private var timelineGrid: some View {
        GeometryReader { geometry in
            Path { path in
                let config = timelineData.config
                let width = timelineData.canvasWidth * zoomLevel
                let height = timelineData.canvasHeight * zoomLevel

                // 수평선 (레인 구분)
                for lane in 0...timelineData.usedLanes {
                    let y = config.topMargin * zoomLevel + Double(lane) * (config.laneHeight + config.laneSpacing) * zoomLevel
                    path.move(to: CGPoint(x: 0, y: y))
                    path.addLine(to: CGPoint(x: width, y: y))
                }

                // 수직선 (주 단위)
                let dateRange = timelineData.dateRangeDays
                let weekInterval = 7
                for week in stride(from: 0, through: dateRange, by: weekInterval) {
                    let x = config.leftMargin * zoomLevel + Double(week) * config.pixelsPerDay * zoomLevel
                    path.move(to: CGPoint(x: x, y: 0))
                    path.addLine(to: CGPoint(x: x, y: height))
                }
            }
            .stroke(Color.gray.opacity(0.1), lineWidth: 1)
        }
    }

    // MARK: - Empty & Placeholder States

    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Image(systemName: isTaskFilterActive ? "line.3.horizontal.decrease.circle" : "calendar.badge.exclamationmark")
                .font(.system(size: 48))
                .foregroundColor(.secondary)

            if isTaskFilterActive {
                Text("필터 조건에 맞는 태스크가 없습니다")
                    .font(.title2)
                    .foregroundColor(.secondary)
                Text("필터를 조정하거나 초기화 버튼을 눌러주세요")
                    .font(.body)
                    .foregroundColor(.secondary)

                Button {
                    selectedStatuses = [.done, .inProgress, .todo, .notStarted]
                    showBottleneckOnly = false
                    selectedVersion = nil
                    sortOrder = .date
                } label: {
                    HStack(spacing: 8) {
                        Image(systemName: "arrow.counterclockwise")
                        Text("필터 초기화")
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                }
                .buttonStyle(.borderedProminent)
                .padding(.top, 8)
            } else {
                Text("날짜가 설정된 태스크가 없습니다")
                    .font(.title2)
                    .foregroundColor(.secondary)
                Text("태스크에 targetDate를 추가하면 타임라인에 표시됩니다")
                    .font(.body)
                    .foregroundColor(.secondary)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    /// 태스크 필터가 활성화되어 있는지 확인
    private var isTaskFilterActive: Bool {
        selectedStatuses.count < 4 ||
        showBottleneckOnly ||
        selectedVersion != nil ||
        sortOrder != .date
    }

    private var placeholderView: some View {
        VStack(spacing: 16) {
            if filteredAndSortedApps.isEmpty {
                // 필터로 인해 앱이 없음
                Image(systemName: "line.3.horizontal.decrease.circle")
                    .font(.system(size: 48))
                    .foregroundColor(.secondary)
                Text("필터 조건에 맞는 앱이 없습니다")
                    .font(.title2)
                    .foregroundColor(.secondary)
                Text("필터를 조정하거나 초기화 버튼을 눌러주세요")
                    .font(.body)
                    .foregroundColor(.secondary)

                Button {
                    appSortOrder = .default
                    showOnlyWithBottleneck = false
                    showOnlyWithSchedule = false
                    showOnlyHighPriority = false
                } label: {
                    HStack(spacing: 8) {
                        Image(systemName: "arrow.counterclockwise")
                        Text("앱 필터 초기화")
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                }
                .buttonStyle(.borderedProminent)
                .padding(.top, 8)
            } else {
                // 앱은 있지만 선택 안 됨
                Image(systemName: "timeline.selection")
                    .font(.system(size: 48))
                    .foregroundColor(.secondary)
                Text("앱을 선택하세요")
                    .font(.title2)
                    .foregroundColor(.secondary)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    // MARK: - Helper Methods

    /// 앱의 병목 태스크 개수 계산
    private func countBottlenecks(in app: AppModel) -> Int {
        let now = Date()
        var count = 0

        for task in app.allTasks {
            // 조건 1: 진행중 14일 초과
            if task.status == .inProgress, let targetDate = task.parsedTargetDate {
                let daysSince = Calendar.current.dateComponents([.day], from: targetDate, to: now).day ?? 0
                if daysSince > 14 {
                    count += 1
                    continue
                }
            }

            // 조건 2: 기한 초과
            if task.status != .done, let targetDate = task.parsedTargetDate, targetDate < now {
                count += 1
            }
        }

        return count
    }

    // MARK: - Update Timeline

    private func updateTimeline(for app: AppModel?) {
        guard let app = app else {
            timelineData = TimelineData()
            return
        }

        // 필터링
        var filteredTasks = app.allTasks

        // 1. 상태 필터
        filteredTasks = filteredTasks.filter { selectedStatuses.contains($0.status) }

        // 2. 병목 필터
        if showBottleneckOnly {
            let now = Date()
            filteredTasks = filteredTasks.filter { task in
                // 진행중 14일 초과
                if task.status == .inProgress, let targetDate = task.parsedTargetDate {
                    let daysSince = Calendar.current.dateComponents([.day], from: targetDate, to: now).day ?? 0
                    if daysSince > 14 {
                        return true
                    }
                }
                // 기한 초과
                if task.status != .done, let targetDate = task.parsedTargetDate, targetDate < now {
                    return true
                }
                return false
            }
        }

        // 3. 버전 필터
        if let version = selectedVersion {
            filteredTasks = filteredTasks.filter { $0.targetVersion == version }
        }

        // 정렬
        switch sortOrder {
        case .date:
            // 날짜순 (기본) - TimelineInferenceEngine이 자동 정렬
            break
        case .status:
            // 상태별 정렬
            let statusOrder: [TaskStatus: Int] = [.done: 0, .inProgress: 1, .todo: 2, .notStarted: 3]
            filteredTasks.sort { task1, task2 in
                let order1 = statusOrder[task1.status] ?? 4
                let order2 = statusOrder[task2.status] ?? 4
                if order1 != order2 {
                    return order1 < order2
                }
                // 같은 상태면 날짜순
                if let date1 = task1.parsedTargetDate, let date2 = task2.parsedTargetDate {
                    return date1 < date2
                }
                return task1.name < task2.name
            }
        case .version:
            // 버전별 정렬
            filteredTasks.sort { task1, task2 in
                let v1 = task1.targetVersion ?? "zzz" // 버전 없으면 맨 뒤
                let v2 = task2.targetVersion ?? "zzz"
                if v1 != v2 {
                    return v1 < v2
                }
                // 같은 버전이면 날짜순
                if let date1 = task1.parsedTargetDate, let date2 = task2.parsedTargetDate {
                    return date1 < date2
                }
                return task1.name < task2.name
            }
        }

        var config = TimelineLayoutConfig.default
        config.pixelsPerDay = 8.0 // 기본 줌 레벨

        timelineData = TimelineInferenceEngine.inferTimeline(
            tasks: filteredTasks,
            currentVersion: app.currentVersion,
            config: config
        )
    }

    /// 앱의 고유 버전 목록 추출
    private func getUniqueVersions(from app: AppModel) -> [String] {
        let versions = Set(app.allTasks.compactMap { $0.targetVersion })
        return versions.sorted()
    }

    // MARK: - App Filtering and Sorting

    /// 필터링 및 정렬된 앱 리스트
    private var filteredAndSortedApps: [AppModel] {
        var apps = portfolioService.apps

        // 필터링
        if showOnlyWithBottleneck {
            apps = apps.filter { countBottlenecks(in: $0) > 0 }
        }

        if showOnlyWithSchedule {
            apps = apps.filter { !$0.allTasks.filter({ $0.parsedTargetDate != nil }).isEmpty }
        }

        if showOnlyHighPriority {
            apps = apps.filter { $0.priority == .high }
        }

        // 정렬
        switch appSortOrder {
        case .default:
            // 기본 순서 유지
            break

        case .bottleneck:
            apps.sort { countBottlenecks(in: $0) > countBottlenecks(in: $1) }

        case .inProgress:
            apps.sort { $0.stats.inProgress > $1.stats.inProgress }

        case .schedule:
            apps.sort {
                let count1 = $0.allTasks.filter { $0.parsedTargetDate != nil }.count
                let count2 = $1.allTasks.filter { $0.parsedTargetDate != nil }.count
                return count1 > count2
            }

        case .priority:
            let priorityOrder: [Priority: Int] = [.high: 0, .medium: 1, .low: 2]
            apps.sort {
                let order1 = priorityOrder[$0.priority] ?? 3
                let order2 = priorityOrder[$1.priority] ?? 3
                return order1 < order2
            }
        }

        return apps
    }

    /// 앱 필터가 활성화되어 있는지 확인
    private var isAppFilterActive: Bool {
        appSortOrder != .default ||
        showOnlyWithBottleneck ||
        showOnlyWithSchedule ||
        showOnlyHighPriority
    }
}
