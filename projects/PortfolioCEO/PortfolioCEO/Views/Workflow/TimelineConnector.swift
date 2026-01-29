import SwiftUI

/// 타임라인 노드 간 연결선 뷰
struct TimelineConnectorView: View {
    let connection: TimelineConnection
    let config: TimelineLayoutConfig
    let zoomLevel: Double
    var timelineWidth: Double = 0 // 전체 타임라인 너비

    var body: some View {
        Path { path in
            let from = calculateNodePosition(connection.from)
            let to = calculateNodePosition(connection.to)

            path.move(to: from)

            // 베지어 곡선 제어점
            let controlX = from.x + (to.x - from.x) * 0.6
            let control1 = CGPoint(x: controlX, y: from.y)
            let control2 = CGPoint(x: controlX, y: to.y)

            path.addCurve(to: to, control1: control1, control2: control2)
        }
        .stroke(
            lineColor,
            style: StrokeStyle(
                lineWidth: 2 * zoomLevel,
                lineCap: .round,
                lineJoin: .round
            )
        )
        .opacity(connection.isActive ? 0.6 : 0.2)
    }

    private var lineColor: Color {
        if connection.isActive {
            // 활성 연결선: 진행중이거나 완료된 태스크 간 연결
            if connection.to.task.status == .done {
                return .green
            } else if connection.to.task.status == .inProgress {
                return .orange
            } else {
                return .blue
            }
        } else {
            // 비활성 연결선: 아직 시작 안 한 태스크
            return .gray
        }
    }

    private func calculateNodePosition(_ timelineTask: TimelineTask) -> CGPoint {
        // 노드의 우측 중앙 지점 (연결선 시작/끝점)
        let effectiveWidth = timelineWidth > 0 ? timelineWidth : config.pixelsPerDay * 365 * zoomLevel
        let contentWidth = effectiveWidth - (config.leftMargin + config.rightMargin) * zoomLevel
        let x = config.leftMargin * zoomLevel + timelineTask.xPosition * contentWidth + (config.nodeWidth * zoomLevel / 2)
        let y = config.topMargin * zoomLevel + Double(timelineTask.yLane) * (config.laneHeight + config.laneSpacing) * zoomLevel + (config.laneHeight * zoomLevel / 2)
        return CGPoint(x: x, y: y)
    }
}
