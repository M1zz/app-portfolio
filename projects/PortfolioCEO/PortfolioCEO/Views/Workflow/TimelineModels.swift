import Foundation
import SwiftUI

// MARK: - Timeline Task

/// 타임라인에 배치된 태스크 (위치 및 병목 정보 포함)
struct TimelineTask: Identifiable {
    let id = UUID()
    let task: AppTask

    /// X축 위치 (0.0 ~ 1.0, 정규화된 시간)
    var xPosition: Double

    /// Y축 레인 인덱스 (0, 1, 2...)
    var yLane: Int

    /// 병목 태스크 여부
    var isBottleneck: Bool

    /// 병목 이유
    var bottleneckReason: String?

    init(task: AppTask, xPosition: Double = 0, yLane: Int = 0, isBottleneck: Bool = false, bottleneckReason: String? = nil) {
        self.task = task
        self.xPosition = xPosition
        self.yLane = yLane
        self.isBottleneck = isBottleneck
        self.bottleneckReason = bottleneckReason
    }
}

// MARK: - Version Milestone

/// 버전 마일스톤 마커
struct VersionMilestone: Identifiable {
    let id = UUID()
    let version: String

    /// X축 위치 (0.0 ~ 1.0)
    var xPosition: Double

    /// 해당 버전에 속한 태스크들
    var tasks: [AppTask]

    /// 현재 버전 여부
    var isCurrent: Bool

    init(version: String, xPosition: Double = 0, tasks: [AppTask] = [], isCurrent: Bool = false) {
        self.version = version
        self.xPosition = xPosition
        self.tasks = tasks
        self.isCurrent = isCurrent
    }
}

// MARK: - Timeline Layout Configuration

/// 타임라인 레이아웃 설정
struct TimelineLayoutConfig {
    /// 하루당 픽셀 수 (줌 레벨)
    var pixelsPerDay: Double = 8.0

    /// 레인 높이
    var laneHeight: Double = 120.0

    /// 레인 간격
    var laneSpacing: Double = 20.0

    /// 노드 너비
    var nodeWidth: Double = 180.0

    /// 노드 높이
    var nodeHeight: Double = 100.0

    /// 상단 여백 (버전 마일스톤 공간)
    var topMargin: Double = 100.0

    /// 좌측 여백
    var leftMargin: Double = 50.0

    /// 우측 여백
    var rightMargin: Double = 100.0

    /// 하단 여백
    var bottomMargin: Double = 50.0

    /// 최대 레인 수 (이후 수직 스크롤)
    var maxLanes: Int = 10

    /// 병목 탐지 임계값 (일)
    var bottleneckThresholdDays: Int = 14

    static let `default` = TimelineLayoutConfig()
}

// MARK: - Timeline Data

/// 타임라인 전체 데이터
struct TimelineData {
    /// 배치된 태스크들
    var tasks: [TimelineTask]

    /// 버전 마일스톤들
    var milestones: [VersionMilestone]

    /// 시작 날짜
    var startDate: Date

    /// 종료 날짜
    var endDate: Date

    /// 캔버스 너비
    var canvasWidth: Double

    /// 캔버스 높이
    var canvasHeight: Double

    /// 레이아웃 설정
    var config: TimelineLayoutConfig

    init(tasks: [TimelineTask] = [], milestones: [VersionMilestone] = [], startDate: Date = Date(), endDate: Date = Date(), canvasWidth: Double = 0, canvasHeight: Double = 0, config: TimelineLayoutConfig = .default) {
        self.tasks = tasks
        self.milestones = milestones
        self.startDate = startDate
        self.endDate = endDate
        self.canvasWidth = canvasWidth
        self.canvasHeight = canvasHeight
        self.config = config
    }

    /// 날짜 범위 (일 수)
    var dateRangeDays: Int {
        Calendar.current.dateComponents([.day], from: startDate, to: endDate).day ?? 0
    }

    /// 사용된 레인 수
    var usedLanes: Int {
        guard !tasks.isEmpty else { return 0 }
        return (tasks.map { $0.yLane }.max() ?? 0) + 1
    }
}

// MARK: - Timeline Connection

/// 타임라인 노드 간 연결선
struct TimelineConnection: Identifiable {
    let id = UUID()
    let from: TimelineTask
    let to: TimelineTask

    /// 활성 연결선 여부 (두 태스크가 모두 진행중/완료)
    var isActive: Bool {
        from.task.status != .notStarted && to.task.status != .notStarted
    }
}
