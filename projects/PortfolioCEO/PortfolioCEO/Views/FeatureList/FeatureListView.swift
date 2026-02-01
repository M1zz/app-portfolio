import SwiftUI

/// 피쳐리스트 메인 뷰
struct FeatureListView: View {
    @EnvironmentObject var portfolioService: PortfolioService
    @State private var selectedApp: AppModel?
    @State private var selectedCategories: Set<String> = []
    @State private var selectedStatuses: Set<TaskStatus> = [.done, .inProgress, .todo, .notStarted]
    @State private var searchText = ""
    @State private var showFilters = true

    var body: some View {
        VStack(spacing: 0) {
            // 앱 선택 바
            appSelectorBar

            // 필터 바
            if selectedApp != nil {
                filterBar
                Divider()
            }

            // 피처 그리드
            if let app = selectedApp {
                if filteredFeatures.isEmpty {
                    emptyStateView
                } else {
                    featureGrid(for: app)
                }
            } else {
                placeholderView
            }
        }
        .onAppear {
            // 첫 번째 앱을 기본 선택
            if selectedApp == nil, let firstApp = portfolioService.apps.first {
                selectedApp = firstApp
            }
        }
    }

    // MARK: - App Selector Bar

    private var appSelectorBar: some View {
        VStack(spacing: 0) {
            HStack(spacing: 12) {
                Image(systemName: "app.badge")
                    .font(.title3)
                    .foregroundColor(.blue)

                Text("앱 선택")
                    .font(.headline)

                Spacer()

                if let app = selectedApp {
                    Text("\(app.features.count)개 피처")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color.gray.opacity(0.08))

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(portfolioService.apps) { app in
                        appButton(for: app)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
            }
        }
        .background(Color.gray.opacity(0.05))
    }

    private func appButton(for app: AppModel) -> some View {
        Button {
            selectedApp = app
            selectedCategories = []
        } label: {
            VStack(spacing: 4) {
                HStack(spacing: 8) {
                    Circle()
                        .fill(app.statusColor)
                        .frame(width: 8, height: 8)

                    Text(app.name)
                        .font(.subheadline)
                        .fontWeight(selectedApp?.id == app.id ? .semibold : .regular)
                }

                Text("\(app.features.count)개 피처")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(selectedApp?.id == app.id ? Color.blue.opacity(0.15) : Color.clear)
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(selectedApp?.id == app.id ? Color.blue : Color.gray.opacity(0.2), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }

    // MARK: - Filter Bar

    private var filterBar: some View {
        VStack(spacing: 0) {
            // 헤더
            HStack(spacing: 12) {
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        showFilters.toggle()
                    }
                } label: {
                    HStack(spacing: 8) {
                        Image(systemName: showFilters ? "chevron.down" : "chevron.right")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("필터")
                            .font(.headline)
                    }
                }
                .buttonStyle(.plain)

                if !showFilters {
                    if !selectedCategories.isEmpty {
                        Text("\(selectedCategories.count)개 카테고리")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    if selectedStatuses.count != 4 {
                        Text("\(selectedStatuses.count)개 상태")
                            .font(.caption)
                            .foregroundColor(.secondary)
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
                    showFilters.toggle()
                }
            }

            // 필터 컨트롤
            if showFilters {
                VStack(spacing: 12) {
                    // 카테고리 필터
                    if let app = selectedApp, !app.featureCategories.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("카테고리")
                                .font(.caption)
                                .foregroundColor(.secondary)

                            ScrollView(.horizontal, showsIndicators: false) {
                                HStack(spacing: 8) {
                                    ForEach(app.featureCategories, id: \.self) { category in
                                        categoryFilterButton(category)
                                    }
                                }
                            }
                        }
                    }

                    // 상태 필터
                    VStack(alignment: .leading, spacing: 8) {
                        Text("상태")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        HStack(spacing: 8) {
                            ForEach([TaskStatus.done, .inProgress, .todo, .notStarted], id: \.self) { status in
                                statusFilterButton(status)
                            }
                        }
                    }

                    // 검색
                    HStack(spacing: 8) {
                        Image(systemName: "magnifyingglass")
                            .foregroundColor(.secondary)
                            .font(.caption)
                        TextField("피처 검색...", text: $searchText)
                            .textFieldStyle(.plain)
                        if !searchText.isEmpty {
                            Button {
                                searchText = ""
                            } label: {
                                Image(systemName: "xmark.circle.fill")
                                    .foregroundColor(.secondary)
                                    .font(.caption)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(8)
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(6)
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
            }
        }
    }

    private func categoryFilterButton(_ category: String) -> some View {
        let isSelected = selectedCategories.contains(category)
        return Button {
            if isSelected {
                selectedCategories.remove(category)
            } else {
                selectedCategories.insert(category)
            }
        } label: {
            Text(category)
                .font(.caption)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(isSelected ? Color.blue : Color.gray.opacity(0.1))
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(12)
        }
        .buttonStyle(.plain)
    }

    private func statusFilterButton(_ status: TaskStatus) -> some View {
        let isSelected = selectedStatuses.contains(status)
        return Button {
            if isSelected {
                selectedStatuses.remove(status)
            } else {
                selectedStatuses.insert(status)
            }
        } label: {
            HStack(spacing: 4) {
                Circle()
                    .fill(status.color)
                    .frame(width: 8, height: 8)
                Text(status.displayName)
                    .font(.caption)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(isSelected ? status.color.opacity(0.2) : Color.gray.opacity(0.1))
            .cornerRadius(12)
        }
        .buttonStyle(.plain)
    }

    // MARK: - Feature Grid

    private var filteredFeatures: [AppTask] {
        guard let app = selectedApp else { return [] }
        return app.features.filter { feature in
            // 카테고리 필터
            if !selectedCategories.isEmpty {
                guard let category = feature.featureMetadata?.category,
                      selectedCategories.contains(category) else {
                    return false
                }
            }

            // 상태 필터
            guard selectedStatuses.contains(feature.status) else {
                return false
            }

            // 검색
            if !searchText.isEmpty {
                let searchLower = searchText.lowercased()
                let matchesName = feature.name.lowercased().contains(searchLower)
                let matchesDescription = feature.featureMetadata?.description?.lowercased().contains(searchLower) ?? false
                return matchesName || matchesDescription
            }

            return true
        }
    }

    private func featureGrid(for app: AppModel) -> some View {
        ScrollView {
            if selectedCategories.isEmpty {
                // 카테고리별 섹션으로 그룹핑
                LazyVStack(spacing: 20, pinnedViews: [.sectionHeaders]) {
                    ForEach(app.featureCategories, id: \.self) { category in
                        Section {
                            let categoryFeatures = filteredFeatures.filter {
                                $0.featureMetadata?.category == category
                            }
                            if !categoryFeatures.isEmpty {
                                FeatureCategorySection(
                                    category: category,
                                    features: categoryFeatures,
                                    app: app
                                )
                            }
                        }
                    }

                    // "기타" 카테고리 (카테고리 없는 피처들)
                    let uncategorized = filteredFeatures.filter {
                        $0.featureMetadata?.category == nil
                    }
                    if !uncategorized.isEmpty {
                        Section {
                            FeatureCategorySection(
                                category: "기타",
                                features: uncategorized,
                                app: app
                            )
                        }
                    }
                }
                .padding()
            } else {
                // 선택된 카테고리만 표시 (플랫 리스트)
                LazyVStack(spacing: 12) {
                    ForEach(filteredFeatures) { feature in
                        FeatureCardView(feature: feature, app: app)
                    }
                }
                .padding()
            }
        }
    }

    // MARK: - Placeholder & Empty State

    private var placeholderView: some View {
        VStack(spacing: 16) {
            Image(systemName: "star.square.on.square")
                .font(.system(size: 60))
                .foregroundColor(.gray.opacity(0.5))

            Text("앱을 선택하세요")
                .font(.headline)
                .foregroundColor(.secondary)

            Text("위의 앱 목록에서 앱을 선택하면\n해당 앱의 피처 목록을 볼 수 있습니다")
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Image(systemName: "tray")
                .font(.system(size: 60))
                .foregroundColor(.gray.opacity(0.5))

            Text("피처가 없습니다")
                .font(.headline)
                .foregroundColor(.secondary)

            if !searchText.isEmpty {
                Text("검색 조건에 맞는 피처가 없습니다")
                    .font(.caption)
                    .foregroundColor(.secondary)
            } else if !selectedCategories.isEmpty || selectedStatuses.count != 4 {
                Text("필터 조건에 맞는 피처가 없습니다")
                    .font(.caption)
                    .foregroundColor(.secondary)
            } else {
                Text("이 앱에 아직 피처가 등록되지 않았습니다")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
