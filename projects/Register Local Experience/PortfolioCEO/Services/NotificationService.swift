import Foundation
import UserNotifications

/// 알림 서비스
/// 일일 브리핑 알림 등을 관리
class NotificationService: NSObject, ObservableObject {
    static let shared = NotificationService()

    private let center = UNUserNotificationCenter.current()

    override private init() {
        super.init()
        center.delegate = self
    }

    // MARK: - Authorization

    func requestAuthorization() {
        center.requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if granted {
                print("✅ 알림 권한 승인됨")
            } else if let error = error {
                print("❌ 알림 권한 요청 실패: \(error)")
            }
        }
    }

    // MARK: - Daily Briefing

    /// 매일 아침 9시 브리핑 알림 스케줄링
    func scheduleDailyBriefing() {
        let content = UNMutableNotificationContent()
        content.title = "☀️ CEO 브리핑 준비 완료"
        content.body = "오늘의 포트폴리오 현황을 확인하세요"
        content.sound = .default
        content.categoryIdentifier = "DAILY_BRIEFING"

        // 매일 아침 9시
        var dateComponents = DateComponents()
        dateComponents.hour = 9
        dateComponents.minute = 0

        let trigger = UNCalendarNotificationTrigger(
            dateMatching: dateComponents,
            repeats: true
        )

        let request = UNNotificationRequest(
            identifier: "daily-briefing",
            content: content,
            trigger: trigger
        )

        center.add(request) { error in
            if let error = error {
                print("❌ 알림 스케줄링 실패: \(error)")
            } else {
                print("✅ 일일 브리핑 알림 설정 완료 (매일 9:00)")
            }
        }
    }

    /// 즉시 브리핑 알림 보내기
    func sendBriefingNotification() {
        let content = UNMutableNotificationContent()
        content.title = "📊 CEO 브리핑"
        content.body = "긴급 의사결정이 필요합니다"
        content.sound = .default

        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: nil
        )

        center.add(request)
    }

    /// 특정 앱 위험 알림
    func sendRiskAlert(appName: String, issue: String) {
        let content = UNMutableNotificationContent()
        content.title = "⚠️ \(appName) 주의 필요"
        content.body = issue
        content.sound = .defaultCritical
        content.categoryIdentifier = "RISK_ALERT"

        let request = UNNotificationRequest(
            identifier: "risk-\(appName)",
            content: content,
            trigger: nil
        )

        center.add(request)
    }

    /// 배포 완료 알림
    func sendDeploymentNotification(appName: String, version: String) {
        let content = UNMutableNotificationContent()
        content.title = "🚀 \(appName) 배포 완료"
        content.body = "버전 \(version)이 성공적으로 배포되었습니다"
        content.sound = .default

        let request = UNNotificationRequest(
            identifier: "deploy-\(appName)",
            content: content,
            trigger: nil
        )

        center.add(request)
    }

    // MARK: - Testing

    func sendTestNotification() {
        let content = UNMutableNotificationContent()
        content.title = "🧪 테스트 알림"
        content.body = "Portfolio CEO 알림이 정상 작동합니다"
        content.sound = .default

        let request = UNNotificationRequest(
            identifier: "test",
            content: content,
            trigger: nil
        )

        center.add(request)
    }
}

// MARK: - UNUserNotificationCenterDelegate

extension NotificationService: UNUserNotificationCenterDelegate {
    /// 앱이 포그라운드에 있을 때도 알림 표시
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        completionHandler([.banner, .sound])
    }

    /// 알림 클릭 시 처리
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let identifier = response.notification.request.identifier

        if identifier == "daily-briefing" {
            // 브리핑 화면으로 이동
            NotificationCenter.default.post(name: .showBriefing, object: nil)
        }

        completionHandler()
    }
}

// MARK: - Notification Names

extension Notification.Name {
    static let showBriefing = Notification.Name("showBriefing")
    static let showDashboard = Notification.Name("showDashboard")
}
