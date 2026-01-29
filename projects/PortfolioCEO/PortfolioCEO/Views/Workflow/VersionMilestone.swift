import SwiftUI

/// 버전 마일스톤 마커 뷰
struct VersionMilestoneView: View {
    let milestone: VersionMilestone
    let config: TimelineLayoutConfig
    let zoomLevel: Double
    var timelineWidth: Double = 0 // 전체 타임라인 너비

    var body: some View {
        VStack(spacing: 4) {
            // 마일스톤 마커
            ZStack {
                Circle()
                    .fill(milestone.isCurrent ? Color.green : Color.blue)
                    .frame(width: 16 * zoomLevel, height: 16 * zoomLevel)

                if milestone.isCurrent {
                    Image(systemName: "star.fill")
                        .font(.system(size: 8 * zoomLevel))
                        .foregroundColor(.white)
                }
            }

            // 버전 레이블
            Text("v\(milestone.version)")
                .font(.system(size: 12 * zoomLevel, weight: .semibold))
                .foregroundColor(milestone.isCurrent ? .green : .blue)
                .padding(.horizontal, 8 * zoomLevel)
                .padding(.vertical, 4 * zoomLevel)
                .background(
                    RoundedRectangle(cornerRadius: 4)
                        .fill(milestone.isCurrent ? Color.green.opacity(0.1) : Color.blue.opacity(0.1))
                )

            // 태스크 카운트
            Text("\(milestone.tasks.count)개")
                .font(.system(size: 10 * zoomLevel))
                .foregroundColor(.secondary)
        }
        .position(milestonePosition)
    }

    private var milestonePosition: CGPoint {
        // X 위치는 타임라인 위치에 따라
        let effectiveWidth = timelineWidth > 0 ? timelineWidth : config.pixelsPerDay * 365 * zoomLevel
        let contentWidth = effectiveWidth - (config.leftMargin + config.rightMargin) * zoomLevel
        let x = config.leftMargin * zoomLevel + milestone.xPosition * contentWidth

        // Y 위치는 상단 마진 중간
        let y = (config.topMargin * zoomLevel) / 2

        return CGPoint(x: x, y: y)
    }
}
