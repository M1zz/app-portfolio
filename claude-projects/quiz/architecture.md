# 앱 아키텍처

## 개요
<!-- 앱의 전반적인 구조와 목적 설명 -->

## 핵심 모델

### 주요 데이터 모델
```swift
// 예시
struct User: Codable, Identifiable {
    let id: String
    var name: String
    var email: String
}
```

## 뷰 구조

```
MainView
├── HomeView
│   ├── HeaderView
│   └── ContentListView
├── SettingsView
└── ProfileView
```

## 데이터 흐름

### 상태 관리
- SwiftData / Core Data
- UserDefaults (간단한 설정)
- Keychain (민감 정보)

### 네트워크
- URLSession
- API 엔드포인트:
- 인증 방식:

## 주요 기술 스택

- **UI**: SwiftUI
- **비동기**: async/await, Combine
- **로컬 저장**: SwiftData
- **알림**: UserNotifications
- **기타**:

## 타겟

- **iOS 최소 버전**: iOS 16.0+
- **디바이스**: iPhone, iPad
- **Watch 앱**: 있음/없음
- **Widget**: 있음/없음

## 서드파티 라이브러리

현재 사용 중인 라이브러리:
- 없음 (순수 SwiftUI)

## 폴더 구조

```
Sources/
├── Models/
├── Views/
├── ViewModels/
├── Services/
└── Utilities/
```

## 주의사항

- [ ]
- [ ]
- [ ]
