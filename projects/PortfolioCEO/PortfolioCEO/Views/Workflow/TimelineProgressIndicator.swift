import SwiftUI

/// 현재 위치 표시기 뷰
struct TimelineProgressIndicatorView: View {
    let currentDate: Date
    let startDate: Date
    let endDate: Date
    let config: TimelineLayoutConfig
    let zoomLevel: Double
    let canvasHeight: Double

    @State private var pulseAnimation = false

    var body: some View {
        if currentDate >= startDate && currentDate <= endDate {
            ZStack {
                // 수직선
                Rectangle()
                    .fill(Color.green.opacity(0.3))
                    .frame(width: 2 * zoomLevel)
                    .position(indicatorPosition)

                // 상단 마커 (펄스 애니메이션)
                Circle()
                    .fill(Color.green)
                    .frame(width: 12 * zoomLevel, height: 12 * zoomLevel)
                    .overlay(
                        Circle()
                            .stroke(Color.green, lineWidth: 2)
                            .scaleEffect(pulseAnimation ? 1.5 : 1.0)
                            .opacity(pulseAnimation ? 0.0 : 1.0)
                    )
                    .position(topMarkerPosition)

                // 날짜 레이블
                Text("오늘")
                    .font(.system(size: 11 * zoomLevel, weight: .medium))
                    .foregroundColor(.white)
                    .padding(.horizontal, 8 * zoomLevel)
                    .padding(.vertical, 4 * zoomLevel)
                    .background(
                        RoundedRectangle(cornerRadius: 4)
                            .fill(Color.green)
                    )
                    .position(labelPosition)
            }
            .onAppear {
                withAnimation(Animation.easeInOut(duration: 1.5).repeatForever(autoreverses: false)) {
                    pulseAnimation = true
                }
            }
        }
    }

    private var indicatorPosition: CGPoint {
        let dateRange = Calendar.current.dateComponents([.day], from: startDate, to: endDate).day ?? 1
        let daysFromStart = Calendar.current.dateComponents([.day], from: startDate, to: currentDate).day ?? 0
        let xPosition = dateRange > 0 ? Double(daysFromStart) / Double(dateRange) : 0

        let x = config.leftMargin * zoomLevel + xPosition * (calculateTimelineWidth() - config.leftMargin * zoomLevel - config.rightMargin * zoomLevel)
        let y = canvasHeight / 2

        return CGPoint(x: x, y: y)
    }

    private var topMarkerPosition: CGPoint {
        var pos = indicatorPosition
        pos.y = (config.topMargin * zoomLevel) / 2
        return pos
    }

    private var labelPosition: CGPoint {
        var pos = topMarkerPosition
        pos.y = pos.y - 20 * zoomLevel
        return pos
    }

    private func calculateTimelineWidth() -> Double {
        let dateRange = Calendar.current.dateComponents([.day], from: startDate, to: endDate).day ?? 1
        return Double(dateRange) * config.pixelsPerDay * zoomLevel + config.leftMargin * zoomLevel + config.rightMargin * zoomLevel
    }
}
