import SwiftUI

/// 타임라인 태스크 노드 뷰
struct TimelineNodeView: View {
    let timelineTask: TimelineTask
    let config: TimelineLayoutConfig
    let zoomLevel: Double
    var timelineWidth: Double = 0 // 전체 타임라인 너비

    @State private var isHovered = false
    @State private var showingPopover = false

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            // 태스크 이름
            Text(timelineTask.task.name)
                .font(.system(size: 13, weight: .medium))
                .lineLimit(2)
                .foregroundColor(.primary)

            // 날짜 및 버전 정보
            HStack(spacing: 8) {
                if let date = timelineTask.task.targetDate {
                    Label(date, systemImage: "calendar")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }

                if let version = timelineTask.task.targetVersion {
                    Label("v\(version)", systemImage: "number.circle")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }

            Spacer()

            // 상태 배지
            HStack(spacing: 4) {
                Circle()
                    .fill(statusColor)
                    .frame(width: 6, height: 6)

                Text(timelineTask.task.status.displayName)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }

            // 병목 경고
            if timelineTask.isBottleneck, let reason = timelineTask.bottleneckReason {
                HStack(spacing: 4) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.caption2)
                        .foregroundColor(.red)
                    Text(reason)
                        .font(.caption2)
                        .foregroundColor(.red)
                }
            }
        }
        .padding(12)
        .frame(width: config.nodeWidth * zoomLevel, height: config.nodeHeight * zoomLevel)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(statusColor.opacity(0.1))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .strokeBorder(
                    timelineTask.isBottleneck ? Color.red : statusColor.opacity(0.3),
                    lineWidth: timelineTask.isBottleneck ? 2 : 1
                )
        )
        .shadow(color: Color.black.opacity(isHovered ? 0.2 : 0.1), radius: isHovered ? 8 : 4)
        .scaleEffect(isHovered ? 1.05 : 1.0)
        .animation(.easeInOut(duration: 0.2), value: isHovered)
        .position(nodePosition)
        .onHover { hovering in
            isHovered = hovering
        }
        .onTapGesture {
            showingPopover.toggle()
        }
        .popover(isPresented: $showingPopover) {
            taskDetailPopover
                .frame(width: 300)
                .padding()
        }
    }

    // MARK: - Position Calculation

    private var nodePosition: CGPoint {
        let effectiveWidth = timelineWidth > 0 ? timelineWidth : config.pixelsPerDay * 365 * zoomLevel
        let contentWidth = effectiveWidth - (config.leftMargin + config.rightMargin) * zoomLevel
        let x = config.leftMargin * zoomLevel + timelineTask.xPosition * contentWidth
        let y = config.topMargin * zoomLevel + Double(timelineTask.yLane) * (config.laneHeight + config.laneSpacing) * zoomLevel + (config.laneHeight * zoomLevel / 2)
        return CGPoint(x: x, y: y)
    }

    private var statusColor: Color {
        timelineTask.task.status.color
    }

    // MARK: - Task Detail Popover

    private var taskDetailPopover: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(timelineTask.task.name)
                .font(.headline)

            Divider()

            if let date = timelineTask.task.targetDate {
                HStack {
                    Label("목표 날짜", systemImage: "calendar")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text(date)
                        .font(.caption)
                }
            }

            if let version = timelineTask.task.targetVersion {
                HStack {
                    Label("목표 버전", systemImage: "number.circle")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text(version)
                        .font(.caption)
                }
            }

            HStack {
                Label("상태", systemImage: "flag.fill")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
                Text(timelineTask.task.status.displayName)
                    .font(.caption)
                    .foregroundColor(statusColor)
            }

            if let labels = timelineTask.task.labels, !labels.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Label("라벨", systemImage: "tag.fill")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    HStack {
                        ForEach(labels, id: \.self) { label in
                            Text(label)
                                .font(.caption2)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(Color.blue.opacity(0.2))
                                .cornerRadius(4)
                        }
                    }
                }
            }

            if timelineTask.isBottleneck {
                Divider()
                HStack(alignment: .top, spacing: 8) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(.red)
                    VStack(alignment: .leading, spacing: 4) {
                        Text("병목 경고")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.red)
                        if let reason = timelineTask.bottleneckReason {
                            Text(reason)
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                    }
                }
            }
        }
    }

}
