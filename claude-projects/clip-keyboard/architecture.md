# Token Memo (ClipKeyboard) 아키텍처

## 개요

Token Memo는 스마트 클립보드 히스토리와 메모 관리를 제공하는 iOS/macOS 앱입니다.
- **아키텍처 패턴**: Manager/Service 패턴 (MVVM 유사)
- **멀티 타겟**: iOS 메인 앱, 키보드 익스텐션, macOS 앱 (Mac Catalyst)
- **데이터 공유**: App Group을 통한 타겟 간 실시간 데이터 동기화

## 핵심 모델

### 주요 데이터 모델

```swift
// 메모 모델
struct Memo: Codable, Identifiable {
    let id: UUID
    var content: String
    var title: String?
    var category: String  // 테마
    var isFavorite: Bool
    var isSecure: Bool     // 생체인증 필요 여부
    var createdAt: Date
    var usageCount: Int
    var imagePath: String? // 이미지 파일명
    var placeholders: [String]? // 템플릿 플레이스홀더 {변수}
}

// 스마트 클립보드 히스토리
struct SmartClipboardItem: Codable, Identifiable {
    let id: UUID
    var content: String
    var detectedType: ClipboardType  // 자동 분류된 타입
    var confidence: Double           // 분류 신뢰도 0.0~1.0
    var timestamp: Date
    var isPinned: Bool              // 고정 여부
    var expiresAt: Date             // 7일 후 자동 삭제
}

// 클립보드 타입 (15가지)
enum ClipboardType: String, Codable {
    case email, phoneNumber, url, address
    case creditCard, bankAccount, rrn, businessNumber
    case birthDate, zipCode, ipAddress
    case color, price, time, custom
}

// Combo 시스템 (Phase 2)
struct Combo: Codable, Identifiable {
    let id: UUID
    var name: String
    var steps: [ComboStep]  // 순서대로 실행될 메모들
    var delayBetweenSteps: Double  // 스텝 간 시간 간격
}

struct ComboStep: Codable {
    var memoId: UUID?
    var customText: String?
    var delay: Double
}

// 템플릿 플레이스홀더 값
struct PlaceholderValue: Codable {
    let value: String
    let timestamp: Date
}
```

## 뷰 구조

```
Token_memoApp (iOS)
├── ContentView (탭 기반)
│   ├── Screens/List/
│   │   ├── MemoListView
│   │   ├── ClipboardHistoryView
│   │   └── ComboListView
│   ├── Screens/Memo/
│   │   ├── AddMemoView
│   │   ├── EditMemoView
│   │   └── SecureMemoView (생체인증)
│   ├── Screens/Template/
│   │   ├── TemplateListView
│   │   ├── PlaceholderInputView
│   │   └── TemplateMemoView
│   ├── Screens/Component/
│   │   ├── MemoCard
│   │   ├── ClipboardCard
│   │   ├── ThemeSelector
│   │   └── ImagePicker
│   └── SettingsView
│       ├── BackupSettingsView (CloudKit)
│       ├── KeyboardSettingsView
│       └── AppearanceSettingsView

TokenKeyboard (키보드 익스텐션)
├── KeyboardViewController
└── KeyboardView
    ├── MemoButtonsView
    ├── CategoryFilterView
    └── SearchView

TokenMemo.tap (macOS - Mac Catalyst)
├── MenuBarManager (메뉴바 아이콘)
├── GlobalHotkeyManager (전역 단축키)
└── ClipboardMonitorView
```

## 데이터 흐름

### 상태 관리

#### 1. MemoStore (핵심 싱글톤)
```swift
class MemoStore: ObservableObject {
    static let shared = MemoStore()

    @Published var memos: [Memo] = []
    @Published var clipboardHistory: [SmartClipboardItem] = []
    @Published var combos: [Combo] = []

    // App Group 컨테이너에 JSON으로 저장
    // - memos.data
    // - smart.clipboard.history.data
    // - combos.data
    // - Images/ 폴더
}
```

#### 2. DataManager (전역 데이터 관리)
```swift
class DataManager: ObservableObject {
    @Published var currentTheme: String
    @Published var isKeyboardEnabled: Bool
    // UserDefaults (App Group) 기반
}
```

#### 3. App Group 데이터 공유
```
iOS 메인 앱 → App Group → 키보드 익스텐션
     ↓                          ↓
  macOS 앱  ←   App Group   ←   CloudKit

App Group ID: group.com.Ysoup.TokenMemo
```

### 저장 방식

#### 로컬 저장
- **위치**: App Group 컨테이너
- **방식**: JSONEncoder/Decoder
- **파일**:
  ```
  group.com.Ysoup.TokenMemo/
  ├── memos.data
  ├── smart.clipboard.history.data
  ├── combos.data
  └── Images/
      └── {UUID}.jpg
  ```

#### UserDefaults
```swift
// App Group UserDefaults (타겟 간 공유)
UserDefaults(suiteName: "group.com.Ysoup.TokenMemo")

// 저장 항목:
// - placeholder_values_{이름}: [PlaceholderValue]
// - current_theme: String
// - keyboard_enabled: Bool
// - onboarding_completed: Bool
```

#### CloudKit 백업
- **서비스**: CloudKitBackupService
- **백업 대상**: 메모 + 이미지
- **동기화**: 수동 백업/복원 (자동 동기화 아님)

### 클립보드 자동 분류 시스템

```swift
// ClipboardClassificationService (싱글톤)
class ClipboardClassificationService {
    static let shared = ClipboardClassificationService()

    // 정규식 기반 패턴 매칭
    func classify(_ text: String) -> (type: ClipboardType, confidence: Double) {
        // 우선순위 순서로 검사:
        // 1. 주민등록번호 (rrn)
        // 2. 사업자등록번호 (businessNumber)
        // 3. 신용카드 (creditCard)
        // 4. 생년월일 (birthDate)
        // 5. 계좌번호 (bankAccount) - 마지막 (통관부호 P 필터링)
        // ...
    }
}
```

## 서비스 아키텍처

### 주요 서비스

1. **MemoStore**: 메모/클립보드/Combo 저장소
2. **CloudKitBackupService**: iCloud 백업/복원
3. **ComboExecutionService**: Combo 자동 실행
4. **ClipboardClassificationService**: 클립보드 자동 분류
5. **BiometricAuthManager**: 생체인증 (보안 메모)
6. **GlobalHotkeyManager**: macOS 전역 단축키
7. **MenuBarManager**: macOS 메뉴바 관리

### OCR 시스템

```swift
// Vision Framework 기반
import Vision

// 이미지 → 텍스트 인식
// 지원 언어: 한국어, 영어
// 자동 파싱: 카드번호, 주소 등
```

## 주요 기술 스택

- **UI**: SwiftUI
- **비동기**: async/await, Combine
- **로컬 저장**: JSONEncoder/Decoder + App Group
- **클라우드**: CloudKit
- **인증**: LocalAuthentication (Face ID / Touch ID)
- **OCR**: Vision Framework
- **클립보드**: UIPasteboard (iOS), NSPasteboard (macOS)
- **다국어**: NSLocalizedString + String Catalog

## 타겟

### 1. Token memo (iOS 메인 앱)
- **최소 버전**: iOS 17.0+
- **디바이스**: iPhone, iPad
- **Capabilities**:
  - App Groups ✅
  - iCloud (CloudKit) ✅
  - Keychain Sharing ✅

### 2. TokenKeyboard (키보드 익스텐션)
- **타입**: Keyboard Extension
- **데이터 공유**: App Group
- **제약**: 네트워크 제한, 풀 키보드 접근 권한 필요

### 3. TokenMemo.tap (macOS 앱)
- **플랫폼**: macOS (Mac Catalyst)
- **기능**: 메뉴바 아이콘, 전역 단축키, 클립보드 모니터링
- **조건부 컴파일**: `#if targetEnvironment(macCatalyst)`

## 서드파티 라이브러리

**없음** - 순수 SwiftUI + Apple 프레임워크만 사용

## 폴더 구조

```
Token-memo/
├── Token memo/                  # iOS 메인 앱
│   ├── Token_memoApp.swift     # 앱 진입점
│   ├── Model/
│   │   └── Memo.swift          # 데이터 모델
│   ├── Screens/                # 화면 (SwiftUI Views)
│   │   ├── List/               # 리스트 뷰
│   │   ├── Memo/               # 메모 추가/편집
│   │   ├── Template/           # 템플릿
│   │   └── Component/          # 재사용 컴포넌트
│   ├── Service/                # 비즈니스 로직
│   │   ├── MemoStore.swift
│   │   ├── CloudKitBackupService.swift
│   │   └── ComboExecutionService.swift
│   ├── Manager/                # 시스템 관리
│   │   ├── DataManager.swift
│   │   ├── BiometricAuthManager.swift
│   │   ├── GlobalHotkeyManager.swift
│   │   └── MenuBarManager.swift
│   ├── Extensions/             # Swift 확장
│   └── Constants.swift         # 상수, 다국어
├── TokenKeyboard/              # 키보드 익스텐션
│   ├── KeyboardViewController.swift
│   └── KeyboardView.swift
├── TokenMemo.tap/              # macOS 앱
│   └── TokenMemo_macApp.swift
├── Shared/                     # 공통 코드
└── Token memo.xcodeproj
```

## 주요 패턴

### 1. App Group 데이터 공유
```swift
// 모든 타겟에서 동일한 컨테이너 사용
guard let containerURL = FileManager.default.containerURL(
    forSecurityApplicationGroupIdentifier: "group.com.Ysoup.TokenMemo"
) else { return }

let memosURL = containerURL.appendingPathComponent("memos.data")
```

### 2. 싱글톤 패턴
```swift
// MemoStore, ClipboardClassificationService 등
class MemoStore: ObservableObject {
    static let shared = MemoStore()
    private init() {}
}
```

### 3. 데이터 마이그레이션
```swift
// 하위 호환성 유지
if let newMemos = try? JSONDecoder().decode([Memo].self, from: data) {
    return newMemos
} else if let oldMemos = try? JSONDecoder().decode([OldMemo].self, from: data) {
    print("🔄 [MemoStore] 마이그레이션: OldMemo → Memo")
    return oldMemos.map { Memo(from: $0) }
}
```

### 4. 조건부 컴파일
```swift
#if targetEnvironment(macCatalyst)
// macOS 전용 코드
setupMenuBar()
#endif

#if os(iOS)
import UIKit
import Vision
#endif
```

## 주의사항

- ✅ 모든 데이터 저장은 App Group 컨테이너 사용 필수
- ✅ UI 문자열은 100% NSLocalizedString 처리
- ✅ 클립보드 분류는 구체적인 패턴부터 검사 (주민번호 → 사업자번호 → 카드번호 → 계좌번호)
- ✅ 이미지는 1024px 제한, JPEG 0.7 압축
- ✅ 하위 호환성 유지 (마이그레이션 로직 필수)
- ✅ Published 변수는 메인 스레드에서 업데이트
- ✅ Mac Catalyst 조건부 컴파일 사용

## 참고

- **노션 문서**: https://leeo75.notion.site/ClipKeyboard-tutorial-70624fccc524465f99289c89bd0261a4
- **개발자**: leeo@kakao.com
- **상세 문서**: ../Token-memo/CLAUDE.md
