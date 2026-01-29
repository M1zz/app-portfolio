import SwiftUI

struct DecisionCenterView: View {
    @EnvironmentObject var portfolio: PortfolioService
    @StateObject private var decisionQueue = DecisionQueueService.shared
    @State private var expandedDecisions: Set<String> = []
    @State private var selectedOptions: [String: String] = [:]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // 헤더
                HStack {
                    VStack(alignment: .leading) {
                        Text("기획 의사결정")
                            .font(.largeTitle)
                            .bold()
                        Text("\(decisionQueue.pendingDecisions.count)개의 의사결정 대기 중")
                            .foregroundColor(.secondary)
                    }

                    Spacer()

                    Button(action: {
                        decisionQueue.loadQueue()
                    }) {
                        Label("새로고침", systemImage: "arrow.clockwise")
                    }
                }
                .padding(.horizontal)
                .padding(.top)

                Divider()

                // 대기 중인 결정사항
                if decisionQueue.isLoading {
                    ProgressView("로딩 중...")
                        .frame(maxWidth: .infinity)
                        .padding()
                } else if decisionQueue.pendingDecisions.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "checkmark.circle")
                            .font(.system(size: 60))
                            .foregroundColor(.green)
                        Text("모든 의사결정이 완료되었습니다!")
                            .font(.headline)
                        Text("새로운 피드백을 작성하면 의사결정 항목이 생성됩니다")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(40)
                } else {
                    LazyVStack(spacing: 16) {
                        ForEach(decisionQueue.pendingDecisions) { decision in
                            DecisionCard(
                                decision: decision,
                                isExpanded: expandedDecisions.contains(decision.id),
                                selectedOption: selectedOptions[decision.id],
                                onToggleExpand: {
                                    toggleExpansion(for: decision.id)
                                },
                                onSelectOption: { optionId in
                                    selectedOptions[decision.id] = optionId
                                },
                                onApprove: {
                                    if let selectedOption = selectedOptions[decision.id] {
                                        decisionQueue.approveDecision(id: decision.id, selectedOption: selectedOption)
                                        selectedOptions.removeValue(forKey: decision.id)
                                        expandedDecisions.remove(decision.id)
                                    }
                                },
                                onDelete: {
                                    decisionQueue.deleteDecision(id: decision.id)
                                    selectedOptions.removeValue(forKey: decision.id)
                                    expandedDecisions.remove(decision.id)
                                }
                            )
                        }
                    }
                    .padding(.horizontal)
                }

                // 승인된 결정 표시
                if !decisionQueue.completedDecisions.isEmpty {
                    Divider()

                    VStack(alignment: .leading, spacing: 12) {
                        Text("✅ 승인된 의사결정 (\(decisionQueue.completedDecisions.count)개)")
                            .font(.headline)
                            .padding(.horizontal)

                        LazyVStack(spacing: 16) {
                            ForEach(decisionQueue.completedDecisions) { decision in
                                CompletedDecisionCard(
                                    decision: decision,
                                    onReject: {
                                        decisionQueue.rejectDecision(id: decision.id)
                                    },
                                    onDelete: {
                                        decisionQueue.deleteDecision(id: decision.id)
                                    }
                                )
                            }
                        }
                        .padding(.horizontal)
                    }
                }

                // 실행 버튼
                if !decisionQueue.completedDecisions.isEmpty {
                    Divider()

                    VStack(spacing: 12) {
                        Text("🤖 처리 실행")
                            .font(.headline)

                        Text("승인한 의사결정을 반영하여 태스크를 생성합니다")
                            .font(.body)
                            .foregroundColor(.secondary)

                        Button("승인된 결정 처리 및 태스크 생성") {
                            PortfolioService.shared.openInTerminal(script: "process-decisions.sh")
                        }
                        .buttonStyle(.borderedProminent)
                        .controlSize(.large)
                    }
                    .padding()
                }
            }
        }
    }

    private func toggleExpansion(for id: String) {
        if expandedDecisions.contains(id) {
            expandedDecisions.remove(id)
        } else {
            expandedDecisions.insert(id)
        }
    }
}

struct DecisionCard: View {
    let decision: PlanningDecision
    let isExpanded: Bool
    let selectedOption: String?
    let onToggleExpand: () -> Void
    let onSelectOption: (String) -> Void
    let onApprove: () -> Void
    let onDelete: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 헤더
            Button(action: onToggleExpand) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text(decision.app)
                                .font(.body)
                                .foregroundColor(.secondary)

                            Spacer()

                            PriorityBadge(priority: decision.priority)
                            UrgencyBadge(urgency: decision.urgency)
                        }

                        Text(decision.title)
                            .font(.headline)
                            .multilineTextAlignment(.leading)
                    }

                    Spacer()

                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .foregroundColor(.secondary)
                }
            }
            .buttonStyle(.plain)

            // 요약 정보 (항상 표시)
            if !isExpanded {
                Text(decision.description)
                    .font(.body)
                    .foregroundColor(.secondary)
                    .lineLimit(2)

                if let recommended = decision.implementationOptions.first(where: { $0.id == decision.aiRecommendation }) {
                    HStack {
                        Image(systemName: "sparkles")
                            .foregroundColor(.yellow)
                        Text("AI 추천: \(recommended.label)")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                }
            }

            // 상세 정보 (확장 시 표시)
            if isExpanded {
                Divider()

                VStack(alignment: .leading, spacing: 16) {
                    // 설명
                    VStack(alignment: .leading, spacing: 8) {
                        Text("상황")
                            .font(.subheadline)
                            .bold()
                        Text(decision.description)
                            .font(.body)
                    }

                    // 비즈니스 임팩트
                    VStack(alignment: .leading, spacing: 8) {
                        Text("비즈니스 임팩트")
                            .font(.subheadline)
                            .bold()
                        Text(decision.businessImpact)
                            .font(.body)
                            .foregroundColor(.orange)
                    }

                    Divider()

                    // 구현 옵션들
                    VStack(alignment: .leading, spacing: 12) {
                        Text("구현 옵션")
                            .font(.subheadline)
                            .bold()

                        ForEach(decision.implementationOptions) { option in
                            OptionCard(
                                option: option,
                                isRecommended: option.id == decision.aiRecommendation,
                                isSelected: selectedOption == option.id,
                                onSelect: {
                                    onSelectOption(option.id)
                                }
                            )
                        }
                    }

                    // AI 추천 이유
                    if let recommended = decision.implementationOptions.first(where: { $0.id == decision.aiRecommendation }) {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Image(systemName: "sparkles")
                                    .foregroundColor(.yellow)
                                Text("AI 추천 이유")
                                    .font(.subheadline)
                                    .bold()
                            }
                            Text(decision.aiReasoning)
                                .font(.body)
                                .padding()
                                .background(Color.yellow.opacity(0.1))
                                .cornerRadius(8)
                        }
                    }

                    Divider()

                    // 액션 버튼
                    HStack(spacing: 12) {
                        Button(action: onDelete) {
                            HStack {
                                Image(systemName: "trash")
                                Text("삭제")
                            }
                            .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)
                        .tint(.red)

                        Button(action: onApprove) {
                            HStack {
                                Image(systemName: "checkmark.circle.fill")
                                Text("승인")
                            }
                            .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(selectedOption == nil)
                    }
                }
            }
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(selectedOption != nil ? Color.blue : Color.clear, lineWidth: 2)
        )
    }
}

struct OptionCard: View {
    let option: ImplementationOption
    let isRecommended: Bool
    let isSelected: Bool
    let onSelect: () -> Void

    var body: some View {
        Button(action: onSelect) {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text(option.label)
                        .font(.subheadline)
                        .bold()

                    if isRecommended {
                        Text("추천")
                            .font(.body)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color.yellow)
                            .cornerRadius(4)
                    }

                    Spacer()

                    Text(option.estimatedTime)
                        .font(.body)
                        .foregroundColor(.secondary)

                    if isSelected {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.blue)
                    } else {
                        Image(systemName: "circle")
                            .foregroundColor(.secondary)
                    }
                }

                Text(option.description)
                    .font(.body)
                    .foregroundColor(.secondary)

                // 장단점
                HStack(alignment: .top, spacing: 16) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("장점")
                            .font(.body)
                            .bold()
                            .foregroundColor(.green)
                        ForEach(option.pros, id: \.self) { pro in
                            HStack(alignment: .top, spacing: 4) {
                                Text("•")
                                Text(pro)
                            }
                            .font(.body)
                            .foregroundColor(.secondary)
                        }
                    }

                    VStack(alignment: .leading, spacing: 4) {
                        Text("단점")
                            .font(.body)
                            .bold()
                            .foregroundColor(.red)
                        ForEach(option.cons, id: \.self) { con in
                            HStack(alignment: .top, spacing: 4) {
                                Text("•")
                                Text(con)
                            }
                            .font(.body)
                            .foregroundColor(.secondary)
                        }
                    }
                }
            }
            .padding()
            .background(isSelected ? Color.blue.opacity(0.1) : Color(NSColor.textBackgroundColor))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(isSelected ? Color.blue : Color.gray.opacity(0.2), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }
}

struct PriorityBadge: View {
    let priority: String

    var body: some View {
        Text(priority.uppercased())
            .font(.body)
            .bold()
            .padding(.horizontal, 6)
            .padding(.vertical, 2)
            .background(priorityColor)
            .foregroundColor(.white)
            .cornerRadius(4)
    }

    private var priorityColor: Color {
        switch priority.lowercased() {
        case "critical": return .red
        case "high": return .orange
        case "medium": return .yellow
        case "low": return .green
        default: return .gray
        }
    }
}

struct UrgencyBadge: View {
    let urgency: String

    var body: some View {
        HStack(spacing: 2) {
            Image(systemName: urgencyIcon)
            Text(urgency.uppercased())
        }
        .font(.body)
        .padding(.horizontal, 6)
        .padding(.vertical, 2)
        .background(Color.gray.opacity(0.2))
        .cornerRadius(4)
    }

    private var urgencyIcon: String {
        switch urgency.lowercased() {
        case "high": return "exclamationmark.3"
        case "medium": return "exclamationmark.2"
        case "low": return "exclamationmark"
        default: return "minus"
        }
    }
}

// MARK: - Completed Decision Card
struct CompletedDecisionCard: View {
    let decision: PlanningDecision
    let onReject: () -> Void
    let onDelete: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 헤더
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text(decision.app)
                            .font(.body)
                            .foregroundColor(.secondary)

                        Spacer()

                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                        Text("승인됨")
                            .font(.body)
                            .foregroundColor(.green)
                    }

                    Text(decision.title)
                        .font(.headline)
                }
            }

            Divider()

            // 선택된 옵션
            if let selectedOptionId = decision.decision,
               let selectedOption = decision.implementationOptions.first(where: { $0.id == selectedOptionId }) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("선택된 구현 방안")
                        .font(.subheadline)
                        .bold()

                    HStack {
                        Image(systemName: "star.fill")
                            .foregroundColor(.yellow)
                        Text(selectedOption.label)
                            .font(.body)
                            .fontWeight(.medium)
                    }
                    .padding()
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(8)

                    Text(selectedOption.description)
                        .font(.body)
                        .foregroundColor(.secondary)
                }
            }

            Divider()

            // 액션 버튼
            HStack(spacing: 12) {
                Button(action: onReject) {
                    HStack {
                        Image(systemName: "arrow.uturn.backward")
                        Text("거절")
                    }
                    .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .tint(.orange)

                Button(action: onDelete) {
                    HStack {
                        Image(systemName: "trash")
                        Text("삭제")
                    }
                    .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .tint(.red)
            }
        }
        .padding()
        .background(Color.green.opacity(0.05))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.green, lineWidth: 2)
        )
    }
}
