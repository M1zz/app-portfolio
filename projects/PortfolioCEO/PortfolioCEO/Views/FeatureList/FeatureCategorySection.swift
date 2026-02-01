import SwiftUI

/// 카테고리별 피처 섹션
struct FeatureCategorySection: View {
    let category: String
    let features: [AppTask]
    let app: AppModel

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 카테고리 헤더
            HStack {
                HStack(spacing: 8) {
                    Image(systemName: categoryIcon)
                        .font(.title3)
                        .foregroundColor(categoryColor)

                    Text(category)
                        .font(.title3)
                        .fontWeight(.semibold)
                        .foregroundColor(categoryColor)
                }

                Spacer()

                // 피처 수 + 상태별 카운트
                HStack(spacing: 12) {
                    Text("\(features.count)개")
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(categoryColor)

                    // 상태별 카운트
                    HStack(spacing: 8) {
                        statusCount(.done)
                        statusCount(.inProgress)
                        statusCount(.todo)
                        statusCount(.notStarted)
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(categoryColor.opacity(0.08))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(categoryColor.opacity(0.2), lineWidth: 1)
            )

            // 피처 카드들
            LazyVStack(spacing: 12) {
                ForEach(features) { feature in
                    FeatureCardView(feature: feature, app: app)
                }
            }
        }
    }

    private func statusCount(_ status: TaskStatus) -> some View {
        let count = features.filter { $0.status == status }.count
        return Group {
            if count > 0 {
                HStack(spacing: 3) {
                    Circle()
                        .fill(status.color)
                        .frame(width: 6, height: 6)
                    Text("\(count)")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
        }
    }

    private var categoryIcon: String {
        switch category {
        case "핵심기능", "Core Features":
            return "star.fill"
        case "보안", "Security":
            return "lock.shield.fill"
        case "커스터마이징", "Customization":
            return "slider.horizontal.3"
        case "향후 기능", "Planned":
            return "lightbulb.fill"
        case "UI/UX":
            return "paintbrush.fill"
        case "성능", "Performance":
            return "speedometer"
        case "통합", "Integration":
            return "link"
        default:
            return "square.grid.2x2.fill"
        }
    }

    private var categoryColor: Color {
        // 카테고리별 색상 코딩 (guide lines 172-182)
        let categoryLower = category.lowercased()
        if categoryLower.contains("입력") {
            return .blue
        } else if categoryLower.contains("연동") || categoryLower.contains("동기") {
            return .green
        } else if categoryLower.contains("안전") || categoryLower.contains("보안") || categoryLower.contains("백업") {
            return .red
        } else if categoryLower.contains("시간") || categoryLower.contains("절약") {
            return .orange
        } else if categoryLower.contains("건강") {
            return .mint
        } else if categoryLower.contains("감정") || categoryLower.contains("표현") {
            return .purple
        } else if categoryLower.contains("관리") {
            return .indigo
        } else if categoryLower.contains("분석") || categoryLower.contains("통계") {
            return .cyan
        } else if categoryLower.contains("핵심") || categoryLower.contains("기능") {
            return .yellow
        } else if categoryLower.contains("확인") || categoryLower.contains("모니터링") {
            return .teal
        } else {
            return .gray
        }
    }
}
