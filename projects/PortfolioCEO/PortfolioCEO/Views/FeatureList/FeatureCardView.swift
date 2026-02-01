import SwiftUI

/// 개별 피처 카드
struct FeatureCardView: View {
    let feature: AppTask
    let app: AppModel
    @State private var showDetail = false

    var body: some View {
        Button {
            showDetail = true
        } label: {
            HStack(spacing: 12) {
                // 상태 인디케이터
                VStack {
                    Circle()
                        .fill(feature.status.color)
                        .frame(width: 12, height: 12)
                    Spacer()
                }

                // 피처 정보
                VStack(alignment: .leading, spacing: 8) {
                    // 상태 + 카테고리
                    HStack(spacing: 8) {
                        // 상태 배지
                        HStack(spacing: 4) {
                            Circle()
                                .fill(feature.status.color)
                                .frame(width: 8, height: 8)
                            Text(feature.status.displayName)
                                .font(.caption)
                                .fontWeight(.medium)
                        }
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(feature.status.color.opacity(0.15))
                        .foregroundColor(feature.status.color)
                        .cornerRadius(6)

                        Spacer()

                        // 카테고리 태그
                        if let category = feature.featureMetadata?.category {
                            Text(category)
                                .font(.caption)
                                .fontWeight(.medium)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 5)
                                .background(categoryColor(for: category).opacity(0.15))
                                .foregroundColor(categoryColor(for: category))
                                .cornerRadius(6)
                        }
                    }

                    // 피처명 (Bold, 18pt)
                    Text(feature.name)
                        .font(.system(size: 18, weight: .bold))
                        .foregroundColor(.primary)
                        .lineLimit(2)

                    // 한줄 요약 (usageScenario 첫 문장)
                    if let usageScenario = feature.featureMetadata?.usageScenario {
                        Text(firstSentence(from: usageScenario))
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .lineLimit(2)
                    }

                    // 사용자 이득 (강조)
                    if let userBenefit = feature.featureMetadata?.userBenefit {
                        Label(userBenefit, systemImage: "star.fill")
                            .font(.caption)
                            .foregroundColor(.orange)
                            .lineLimit(1)
                    }
                }

                // 화살표
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding(16)
            .background(Color.gray.opacity(0.05))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.gray.opacity(0.2), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
        .sheet(isPresented: $showDetail) {
            FeatureDetailSheet(feature: feature, app: app)
        }
    }

    // MARK: - Helpers

    private func categoryColor(for category: String) -> Color {
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
        } else {
            return .gray
        }
    }

    private func firstSentence(from text: String) -> String {
        // 첫 문장 추출 (마침표, 느낌표, 물음표로 구분)
        let sentences = text.components(separatedBy: CharacterSet(charactersIn: ".!?"))
        return sentences.first?.trimmingCharacters(in: .whitespacesAndNewlines) ?? text
    }
}
