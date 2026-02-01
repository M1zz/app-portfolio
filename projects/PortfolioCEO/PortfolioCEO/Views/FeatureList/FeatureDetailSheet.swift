import SwiftUI

/// 피처 상세 정보 시트
struct FeatureDetailSheet: View {
    let feature: AppTask
    let app: AppModel
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    // 헤더 정보
                    headerSection

                    Divider()

                    // 7가지 정보 표시 (guide lines 159-168)

                    // 1. 사용 시나리오 (언제 사용?)
                    if let usageScenario = feature.featureMetadata?.usageScenario {
                        detailSection(
                            title: "언제 사용하나요?",
                            icon: "calendar.badge.clock",
                            emoji: "📌",
                            content: usageScenario,
                            color: .blue
                        )
                    }

                    // 2. 문제 해결 (무엇 해결?)
                    if let problemSolved = feature.featureMetadata?.problemSolved {
                        detailSection(
                            title: "어떤 문제를 해결하나요?",
                            icon: "exclamationmark.triangle",
                            emoji: "❌",
                            content: problemSolved,
                            color: .red
                        )
                    }

                    // 3. 사용자 이득 (무엇 얻나?)
                    if let userBenefit = feature.featureMetadata?.userBenefit {
                        detailSection(
                            title: "무엇을 얻나요?",
                            icon: "star.fill",
                            emoji: "✨",
                            content: userBenefit,
                            color: .orange,
                            highlighted: true
                        )
                    }

                    // 4. 상세 설명 (무엇인가?)
                    if let description = feature.featureMetadata?.description {
                        detailSection(
                            title: "무엇인가요?",
                            icon: "lightbulb",
                            emoji: "💡",
                            content: description,
                            color: .yellow
                        )
                    }

                    // 5. 사용자 가치 (왜 유용?)
                    if let userValue = feature.featureMetadata?.userValue {
                        detailSection(
                            title: "왜 유용한가요?",
                            icon: "target",
                            emoji: "🎯",
                            content: userValue,
                            color: .purple
                        )
                    }

                    // 6. 기술 노트 (어떻게?)
                    if let technicalNotes = feature.featureMetadata?.technicalNotes {
                        detailSection(
                            title: "어떻게 구현하나요?",
                            icon: "gearshape.2",
                            emoji: "⚙️",
                            content: technicalNotes,
                            color: .gray
                        )
                    }

                    // 관련 태스크
                    if let relatedTasks = feature.featureMetadata?.relatedTasks, !relatedTasks.isEmpty {
                        relatedTasksSection(relatedTasks)
                    }

                    // 버전 및 일정 정보
                    metadataSection
                }
                .padding(20)
            }
            .navigationTitle(feature.name)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("닫기") {
                        dismiss()
                    }
                }
            }
        }
    }

    // MARK: - Header Section

    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 앱 정보
            HStack(spacing: 8) {
                Circle()
                    .fill(app.statusColor)
                    .frame(width: 8, height: 8)

                Text(app.name)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }

            // 피처명
            Text(feature.name)
                .font(.title2)
                .fontWeight(.bold)

            // 카테고리 + 상태
            HStack(spacing: 12) {
                if let category = feature.featureMetadata?.category {
                    HStack(spacing: 4) {
                        Image(systemName: "folder")
                            .font(.caption)
                        Text(category)
                            .font(.subheadline)
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color.blue.opacity(0.1))
                    .foregroundColor(.blue)
                    .cornerRadius(8)
                }

                HStack(spacing: 6) {
                    Circle()
                        .fill(feature.status.color)
                        .frame(width: 10, height: 10)
                    Text(feature.status.displayName)
                        .font(.subheadline)
                        .fontWeight(.medium)
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(feature.status.color.opacity(0.1))
                .foregroundColor(feature.status.color)
                .cornerRadius(8)
            }
        }
    }

    // MARK: - Detail Section

    private func detailSection(
        title: String,
        icon: String,
        emoji: String? = nil,
        content: String,
        color: Color = .primary,
        highlighted: Bool = false
    ) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 8) {
                if let emoji = emoji {
                    Text(emoji)
                        .font(.title3)
                }

                Image(systemName: icon)
                    .font(.headline)
                    .foregroundColor(color)

                Text(title)
                    .font(.headline)
                    .foregroundColor(color)
            }

            Text(content)
                .font(.body)
                .foregroundColor(.primary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(16)
        .background(highlighted ? color.opacity(0.1) : Color.gray.opacity(0.05))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(highlighted ? color.opacity(0.3) : Color.clear, lineWidth: 2)
        )
    }

    // MARK: - Related Tasks Section

    private func relatedTasksSection(_ tasks: [String]) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 8) {
                Image(systemName: "checklist")
                    .font(.headline)
                    .foregroundColor(.purple)

                Text("관련 태스크")
                    .font(.headline)
                    .foregroundColor(.purple)
            }

            VStack(alignment: .leading, spacing: 8) {
                ForEach(tasks, id: \.self) { task in
                    HStack(spacing: 8) {
                        Image(systemName: "circle.fill")
                            .font(.system(size: 6))
                            .foregroundColor(.secondary)

                        Text(task)
                            .font(.subheadline)
                            .foregroundColor(.primary)
                    }
                }
            }
            .padding(16)
            .background(Color.gray.opacity(0.05))
            .cornerRadius(8)
        }
    }

    // MARK: - Metadata Section

    private var metadataSection: some View {
        VStack(spacing: 0) {
            if let version = feature.targetVersion {
                metadataRow(
                    icon: "tag",
                    label: "목표 버전",
                    value: version
                )
                Divider()
            }

            if let date = feature.targetDate {
                metadataRow(
                    icon: "calendar",
                    label: "목표 날짜",
                    value: date
                )
                Divider()
            }

            metadataRow(
                icon: "info.circle",
                label: "현재 버전",
                value: app.currentVersion
            )
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(12)
    }

    private func metadataRow(icon: String, label: String, value: String) -> some View {
        HStack {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .frame(width: 20)

                Text(label)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }

            Spacer()

            Text(value)
                .font(.subheadline)
                .fontWeight(.medium)
        }
        .padding(.vertical, 8)
    }
}
