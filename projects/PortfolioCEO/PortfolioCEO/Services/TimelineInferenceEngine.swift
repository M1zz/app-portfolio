import Foundation
import SwiftUI

/// 타임라인 자동 추론 엔진
/// targetDate와 targetVersion을 기반으로 태스크 순서를 자동으로 결정하고 병목을 탐지합니다.
class TimelineInferenceEngine {

    // MARK: - Main Inference Method

    /// 태스크 배열을 타임라인 데이터로 변환
    /// - Parameters:
    ///   - tasks: 앱의 모든 태스크
    ///   - currentVersion: 현재 버전
    ///   - config: 레이아웃 설정
    /// - Returns: 배치된 타임라인 데이터
    static func inferTimeline(
        tasks: [AppTask],
        currentVersion: String,
        config: TimelineLayoutConfig = .default
    ) -> TimelineData {

        // 1. 날짜가 있는 태스크만 필터링
        let tasksWithDate = tasks.filter { $0.parsedTargetDate != nil }

        guard !tasksWithDate.isEmpty else {
            // 날짜가 없으면 빈 타임라인 반환
            return TimelineData(config: config)
        }

        // 2. 날짜 파싱 및 정렬
        let sortedTasks = sortTasksByDateAndStatus(tasksWithDate)

        // 3. 시작/종료 날짜 계산
        let dates = tasksWithDate.compactMap { $0.parsedTargetDate }
        let startDate = dates.min() ?? Date()
        let endDate = max(dates.max() ?? Date(), Date()) // 최소한 오늘까지

        // 4. 버전별 그룹핑
        let versionGroups = groupTasksByVersion(sortedTasks, currentVersion: currentVersion)

        // 5. 레인 할당 및 위치 계산
        let timelineTasks = assignLanesAndPositions(
            tasks: sortedTasks,
            startDate: startDate,
            endDate: endDate,
            config: config
        )

        // 6. 병목 탐지
        let tasksWithBottleneck = detectBottlenecks(
            timelineTasks: timelineTasks,
            config: config
        )

        // 7. 버전 마일스톤 생성
        let milestones = createVersionMilestones(
            versionGroups: versionGroups,
            currentVersion: currentVersion,
            startDate: startDate,
            endDate: endDate
        )

        // 8. 캔버스 크기 계산
        let dateRangeDays = Calendar.current.dateComponents([.day], from: startDate, to: endDate).day ?? 1
        let canvasWidth = Double(dateRangeDays) * config.pixelsPerDay + config.leftMargin + config.rightMargin
        let usedLanes = (tasksWithBottleneck.map { $0.yLane }.max() ?? 0) + 1
        let canvasHeight = Double(usedLanes) * (config.laneHeight + config.laneSpacing) + config.topMargin + config.bottomMargin

        return TimelineData(
            tasks: tasksWithBottleneck,
            milestones: milestones,
            startDate: startDate,
            endDate: endDate,
            canvasWidth: canvasWidth,
            canvasHeight: canvasHeight,
            config: config
        )
    }

    // MARK: - Sorting

    /// 태스크를 날짜와 상태 기준으로 정렬
    private static func sortTasksByDateAndStatus(_ tasks: [AppTask]) -> [AppTask] {
        return tasks.sorted { task1, task2 in
            // 1. 날짜 우선 (오래된 것부터)
            if let date1 = task1.parsedTargetDate, let date2 = task2.parsedTargetDate {
                if date1 != date2 {
                    return date1 < date2
                }
            }

            // 2. 같은 날짜면 상태 순서 (done > inProgress > todo > notStarted)
            let statusOrder: [TaskStatus: Int] = [
                .done: 0,
                .inProgress: 1,
                .todo: 2,
                .notStarted: 3
            ]
            let order1 = statusOrder[task1.status] ?? 4
            let order2 = statusOrder[task2.status] ?? 4
            if order1 != order2 {
                return order1 < order2
            }

            // 3. 같은 상태면 이름 순
            return task1.name < task2.name
        }
    }

    // MARK: - Version Grouping

    /// 태스크를 버전별로 그룹핑
    private static func groupTasksByVersion(
        _ tasks: [AppTask],
        currentVersion: String
    ) -> [String: [AppTask]] {
        var groups: [String: [AppTask]] = [:]

        for task in tasks {
            let version = task.targetVersion ?? "미정"
            if groups[version] == nil {
                groups[version] = []
            }
            groups[version]?.append(task)
        }

        return groups
    }

    // MARK: - Lane Assignment

    /// 레인 할당 및 위치 계산 (노드 겹침 방지)
    private static func assignLanesAndPositions(
        tasks: [AppTask],
        startDate: Date,
        endDate: Date,
        config: TimelineLayoutConfig
    ) -> [TimelineTask] {

        var timelineTasks: [TimelineTask] = []

        // 각 레인의 마지막 노드 끝 X 위치 (0.0 ~ 1.0 정규화된 값)
        var laneLastX: [Int: Double] = [:]

        let dateRange = Calendar.current.dateComponents([.day], from: startDate, to: endDate).day ?? 1
        guard dateRange > 0 else { return [] }

        // 노드 너비를 타임라인 전체 너비의 비율로 계산
        // 노드 너비 180px, 여백 20px = 총 200px 점유
        let totalWidth = Double(dateRange) * config.pixelsPerDay
        let nodeWidthRatio = (config.nodeWidth + 20.0) / totalWidth // 20px 여백 추가

        for task in tasks {
            guard let taskDate = task.parsedTargetDate else { continue }

            // X 위치 계산 (0.0 ~ 1.0)
            let daysFromStart = Calendar.current.dateComponents([.day], from: startDate, to: taskDate).day ?? 0
            let xPosition = Double(daysFromStart) / Double(dateRange)

            // 사용 가능한 레인 찾기 (X 위치 기반으로 겹치지 않도록)
            var assignedLane = 0
            var foundLane = false

            for lane in 0..<config.maxLanes {
                if let lastX = laneLastX[lane] {
                    // 이전 노드의 끝 위치보다 충분히 뒤에 있으면 사용 가능
                    if xPosition >= lastX {
                        assignedLane = lane
                        foundLane = true
                        break
                    }
                } else {
                    // 빈 레인이면 바로 사용
                    assignedLane = lane
                    foundLane = true
                    break
                }
            }

            // 모든 레인이 꽉 찼으면 가장 빨리 비는 레인 선택
            if !foundLane {
                assignedLane = laneLastX.min(by: { $0.value < $1.value })?.key ?? 0
            }

            // 레인 점유 업데이트 (현재 노드의 끝 X 위치)
            laneLastX[assignedLane] = xPosition + nodeWidthRatio

            let timelineTask = TimelineTask(
                task: task,
                xPosition: xPosition,
                yLane: assignedLane
            )
            timelineTasks.append(timelineTask)
        }

        return timelineTasks
    }

    // MARK: - Bottleneck Detection

    /// 병목 태스크 탐지
    private static func detectBottlenecks(
        timelineTasks: [TimelineTask],
        config: TimelineLayoutConfig
    ) -> [TimelineTask] {

        return timelineTasks.map { timelineTask in
            var updated = timelineTask
            let task = timelineTask.task

            // 병목 조건 1: 진행중 상태가 14일 이상
            if task.status == .inProgress,
               let targetDate = task.parsedTargetDate {
                let daysSince = Calendar.current.dateComponents([.day], from: targetDate, to: Date()).day ?? 0
                if daysSince > config.bottleneckThresholdDays {
                    updated.isBottleneck = true
                    updated.bottleneckReason = "진행중 \(daysSince)일 경과"
                }
            }

            // 병목 조건 2: 목표 날짜를 지났는데 미완료
            if task.status != .done,
               let targetDate = task.parsedTargetDate,
               targetDate < Date() {
                let daysOverdue = Calendar.current.dateComponents([.day], from: targetDate, to: Date()).day ?? 0
                updated.isBottleneck = true
                updated.bottleneckReason = "기한 \(daysOverdue)일 초과"
            }

            return updated
        }
    }

    // MARK: - Version Milestones

    /// 버전 마일스톤 생성
    private static func createVersionMilestones(
        versionGroups: [String: [AppTask]],
        currentVersion: String,
        startDate: Date,
        endDate: Date
    ) -> [VersionMilestone] {

        let dateRange = Calendar.current.dateComponents([.day], from: startDate, to: endDate).day ?? 1
        var milestones: [VersionMilestone] = []

        for (version, tasks) in versionGroups {
            // 해당 버전의 첫 번째 태스크 날짜로 마일스톤 위치 결정
            guard let firstTask = tasks.first,
                  let firstDate = firstTask.parsedTargetDate else {
                continue
            }

            let daysFromStart = Calendar.current.dateComponents([.day], from: startDate, to: firstDate).day ?? 0
            let xPosition = dateRange > 0 ? Double(daysFromStart) / Double(dateRange) : 0

            let milestone = VersionMilestone(
                version: version,
                xPosition: xPosition,
                tasks: tasks,
                isCurrent: version == currentVersion
            )
            milestones.append(milestone)
        }

        return milestones.sorted { $0.xPosition < $1.xPosition }
    }

    // MARK: - Utility Methods

    /// 두 태스크 간 연결 관계 추론 (순차적 의존성)
    static func inferConnections(timelineTasks: [TimelineTask]) -> [TimelineConnection] {
        var connections: [TimelineConnection] = []

        // 같은 버전의 태스크들을 시간 순으로 연결
        let sortedByDate = timelineTasks.sorted { t1, t2 in
            guard let d1 = t1.task.parsedTargetDate, let d2 = t2.task.parsedTargetDate else {
                return false
            }
            return d1 < d2
        }

        var versionGroups: [String: [TimelineTask]] = [:]
        for task in sortedByDate {
            let version = task.task.targetVersion ?? "미정"
            if versionGroups[version] == nil {
                versionGroups[version] = []
            }
            versionGroups[version]?.append(task)
        }

        // 각 버전 그룹 내에서 연속된 태스크 연결
        for (_, tasks) in versionGroups {
            for i in 0..<tasks.count - 1 {
                let connection = TimelineConnection(
                    from: tasks[i],
                    to: tasks[i + 1]
                )
                connections.append(connection)
            }
        }

        return connections
    }
}
