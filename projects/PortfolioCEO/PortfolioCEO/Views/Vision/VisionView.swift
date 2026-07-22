import SwiftUI

/// 앱 비전/컨셉 뷰
struct VisionView: View {
    @EnvironmentObject var portfolioService: PortfolioService
    @State private var selectedApp: AppModel?
    @State private var searchText = ""

    var body: some View {
        VStack(spacing: 0) {
            // 앱 선택 바
            appSelectorBar

            // 검색 바
            if selectedApp != nil {
                searchBar
                Divider()
            }

            // 비전/컨셉 내용
            if let app = selectedApp {
                visionContent(for: app)
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
                Image(systemName: "lightbulb.fill")
                    .font(.title3)
                    .foregroundColor(.yellow)

                Text("앱 선택")
                    .font(.headline)

                Spacer()

                if let app = selectedApp {
                    Text(app.name)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color.gray.opacity(0.08))

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(filteredApps) { app in
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

                if let vision = app.vision, let tagline = vision.tagline {
                    Text(tagline)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(selectedApp?.id == app.id ? Color.yellow.opacity(0.15) : Color.clear)
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(selectedApp?.id == app.id ? Color.yellow : Color.gray.opacity(0.2), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }

    // MARK: - Search Bar

    private var searchBar: some View {
        HStack(spacing: 8) {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)
                .font(.caption)
            TextField("앱 검색...", text: $searchText)
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
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(Color.gray.opacity(0.05))
    }

    private var filteredApps: [AppModel] {
        if searchText.isEmpty {
            return portfolioService.apps
        } else {
            return portfolioService.apps.filter { app in
                app.name.localizedCaseInsensitiveContains(searchText) ||
                app.nameEn.localizedCaseInsensitiveContains(searchText)
            }
        }
    }

    // MARK: - Vision Content

    private func visionContent(for app: AppModel) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                if let vision = app.vision {
                    // 헤더: 앱 이름 + 태그라인
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Circle()
                                .fill(app.statusColor)
                                .frame(width: 12, height: 12)

                            Text(app.name)
                                .font(.title)
                                .fontWeight(.bold)
                        }

                        if let tagline = vision.tagline {
                            Text(tagline)
                                .font(.title3)
                                .foregroundColor(.yellow)
                                .fontWeight(.semibold)
                        }
                    }
                    .padding(.bottom, 8)

                    Divider()

                    // 핵심 가치
                    if let coreValue = vision.coreValue {
                        visionSection(
                            title: "핵심 가치",
                            icon: "heart.fill",
                            color: .red,
                            content: coreValue
                        )
                    }

                    // 타겟 사용자
                    if let targetUsers = vision.targetUsers {
                        visionSection(
                            title: "타겟 사용자",
                            icon: "person.3.fill",
                            color: .blue,
                            content: targetUsers
                        )
                    }

                    // 차별화 포인트
                    if let usp = vision.uniqueSellingPoint {
                        visionSection(
                            title: "차별화 포인트",
                            icon: "star.fill",
                            color: .orange,
                            content: usp
                        )
                    }

                    // 컨셉 상세 설명
                    if let description = vision.conceptDescription {
                        VStack(alignment: .leading, spacing: 12) {
                            HStack(spacing: 8) {
                                Image(systemName: "doc.text.fill")
                                    .foregroundColor(.purple)
                                Text("컨셉 상세")
                                    .font(.headline)
                                    .foregroundColor(.purple)
                            }

                            Text(description)
                                .font(.body)
                                .foregroundColor(.primary)
                        }
                        .padding(16)
                        .background(Color.purple.opacity(0.05))
                        .cornerRadius(12)
                    }

                    // 디자인 원칙
                    if let principles = vision.designPrinciples, !principles.isEmpty {
                        principlesSection(
                            title: "디자인 원칙",
                            icon: "paintbrush.fill",
                            color: .pink,
                            items: principles
                        )
                    }

                    // 사용자 경험 목표
                    if let goals = vision.userExperienceGoals, !goals.isEmpty {
                        principlesSection(
                            title: "사용자 경험 목표",
                            icon: "target",
                            color: .green,
                            items: goals
                        )
                    }

                    // 마지막 업데이트
                    if let lastUpdated = vision.lastUpdated {
                        HStack {
                            Spacer()
                            Text("마지막 업데이트: \(lastUpdated, formatter: dateFormatter)")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }

                } else {
                    emptyVisionView(for: app)
                }
            }
            .padding(20)
        }
    }

    private func visionSection(title: String, icon: String, color: Color, content: String) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .foregroundColor(color)
                Text(title)
                    .font(.headline)
                    .foregroundColor(color)
            }

            Text(content)
                .font(.body)
                .foregroundColor(.primary)
        }
        .padding(16)
        .background(color.opacity(0.05))
        .cornerRadius(12)
    }

    private func principlesSection(title: String, icon: String, color: Color, items: [String]) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .foregroundColor(color)
                Text(title)
                    .font(.headline)
                    .foregroundColor(color)
            }

            VStack(alignment: .leading, spacing: 8) {
                ForEach(items, id: \.self) { item in
                    HStack(alignment: .top, spacing: 8) {
                        Text("•")
                            .foregroundColor(color)
                            .fontWeight(.bold)
                        Text(item)
                            .font(.body)
                            .foregroundColor(.primary)
                    }
                }
            }
        }
        .padding(16)
        .background(color.opacity(0.05))
        .cornerRadius(12)
    }

    private func emptyVisionView(for app: AppModel) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "lightbulb.slash")
                .font(.system(size: 60))
                .foregroundColor(.gray.opacity(0.5))

            Text("비전/컨셉이 아직 작성되지 않았습니다")
                .font(.headline)
                .foregroundColor(.secondary)

            Text("'\(app.name)'의 핵심 가치와 방향성을 정의해보세요")
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)

            VStack(alignment: .leading, spacing: 8) {
                Text("다음 항목들을 고민해보세요:")
                    .font(.caption)
                    .fontWeight(.semibold)

                Text("• 한 줄 요약 (태그라인)")
                Text("• 핵심 가치")
                Text("• 타겟 사용자")
                Text("• 차별화 포인트")
                Text("• 사용자 경험 목표")
            }
            .font(.caption)
            .foregroundColor(.secondary)
            .padding(12)
            .background(Color.gray.opacity(0.1))
            .cornerRadius(8)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(40)
    }

    // MARK: - Placeholder

    private var placeholderView: some View {
        VStack(spacing: 16) {
            Image(systemName: "lightbulb")
                .font(.system(size: 60))
                .foregroundColor(.gray.opacity(0.5))

            Text("앱을 선택하세요")
                .font(.headline)
                .foregroundColor(.secondary)

            Text("위의 앱 목록에서 앱을 선택하면\n해당 앱의 비전과 컨셉을 볼 수 있습니다")
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private var dateFormatter: DateFormatter {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        formatter.locale = Locale(identifier: "ko_KR")
        return formatter
    }
}
