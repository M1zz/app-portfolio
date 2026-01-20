# Token Memo (ClipKeyboard) 코딩 컨벤션

> 공통 코딩 표준은 `../shared/coding-standards.md` 참조

## 앱별 특수 규칙

### 네이밍

#### 싱글톤은 항상 `.shared` 사용
```swift
// ✅ GOOD
class MemoStore: ObservableObject {
    static let shared = MemoStore()
    private init() {}
}

// ❌ BAD
class MemoStore: ObservableObject {
    static let instance = MemoStore()  // ❌
}
```

#### 한글 사용 제한
```swift
// ✅ GOOD - rawValue, 로그, 주석에만 한글 허용
enum Theme: String, Codable {
    case business = "비즈니스"  // ✅ rawValue
    case personal = "개인"
}

print("✅ [MemoStore] 메모 로드 완료")  // ✅ 로그

// 클립보드 히스토리에서 7일 이상 지난 항목 삭제  // ✅ 주석

// ❌ BAD - 변수/함수명에 한글 사용 금지
let 메모목록 = []  // ❌
func 메모저장() { }  // ❌
```

### 로깅 규칙

이모지로 로그 구분:

```swift
print("✅ [MemoStore.load] 메모 \(count)개 로드 완료")
print("❌ [MemoStore.save] 저장 실패: \(error)")
print("🔄 [MemoStore] 마이그레이션: OldMemo → Memo")
print("📁 [MemoStore] 파일 경로: \(url.path)")
print("📝 [MemoStore.update] 메모 ID \(id) 업데이트")
print("🚀 [APP INIT] 앱 초기화 완료")
```

이모지 의미:
- 📁: 파일 작업
- ✅: 성공
- ❌: 실패
- 🔄: 마이그레이션
- 📝: 변경사항
- 🚀: 초기화

### 파일 조직

```
Token memo/
├── Model/
│   └── Memo.swift
├── Screens/
│   ├── List/
│   ├── Memo/
│   ├── Template/
│   └── Component/
├── Service/
│   ├── MemoStore.swift
│   ├── CloudKitBackupService.swift
│   └── ComboExecutionService.swift
├── Manager/
│   ├── DataManager.swift
│   ├── BiometricAuthManager.swift
│   └── MenuBarManager.swift
└── Extensions/
```

### 주요 패턴

#### Manager/Service 패턴
```swift
// Service: 비즈니스 로직, 데이터 저장소
class MemoStore: ObservableObject {
    static let shared = MemoStore()

    @Published var memos: [Memo] = []
    @Published var clipboardHistory: [SmartClipboardItem] = []

    func loadMemos() { }
    func saveMemos() { }
}

// Manager: 시스템 레벨 기능
class BiometricAuthManager {
    static let shared = BiometricAuthManager()

    func authenticate() async -> Bool { }
}
```

#### View 구조
```swift
struct MemoListView: View {
    @EnvironmentObject var memoStore: MemoStore
    @State private var searchText = ""

    var body: some View {
        content
    }

    private var content: some View {
        List {
            ForEach(filteredMemos) { memo in
                MemoCard(memo: memo)
            }
        }
    }

    private var filteredMemos: [Memo] {
        // ...
    }
}
```

#### 싱글톤 패턴
```swift
class MemoStore: ObservableObject {
    static let shared = MemoStore()

    @Published var memos: [Memo] = []

    private init() {
        loadMemos()
    }
}
```

## App Group 필수 사용

⚠️ **매우 중요**: 모든 데이터는 App Group 컨테이너에 저장

```swift
// ✅ GOOD - App Group 컨테이너
guard let containerURL = FileManager.default.containerURL(
    forSecurityApplicationGroupIdentifier: "group.com.Ysoup.TokenMemo"
) else { return }

let memosURL = containerURL.appendingPathComponent("memos.data")

// ✅ GOOD - App Group UserDefaults
UserDefaults(suiteName: "group.com.Ysoup.TokenMemo")

// ❌ BAD - 표준 Documents 폴더 (키보드와 공유 안 됨)
FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first

// ❌ BAD - 표준 UserDefaults (키보드와 공유 안 됨)
UserDefaults.standard
```

## 다국어 지원 (필수!)

⚠️ **모든 UI 텍스트는 NSLocalizedString 필수**

```swift
// ✅ GOOD
Text(NSLocalizedString("Add Memo", comment: "Button to add a new memo"))
Button(NSLocalizedString("Confirm", comment: "Confirm button")) { }

// ✅ GOOD - enum에 localizedName
enum Theme: String, Codable {
    case business = "비즈니스"

    var localizedName: String {
        NSLocalizedString(self.rawValue, comment: "Theme name")
    }
}

Text(theme.localizedName)  // ✅

// ❌ BAD - 하드코딩
Text("메모 추가")
Text(theme.rawValue)  // ❌ 다국어 지원 안 됨
```

작성 전 체크리스트:
- [ ] UI 텍스트인가? → NSLocalizedString
- [ ] String Catalog에 추가했는가?
- [ ] 한국어 + 영어 번역 있는가?

## 클립보드 분류 우선순위

구체적인 패턴부터 검사:

```swift
func classify(_ text: String) -> (type: ClipboardType, confidence: Double) {
    // 1. 주민등록번호 (가장 구체적)
    if let result = detectRRN(text) { return result }

    // 2. 사업자등록번호
    if let result = detectBusinessNumber(text) { return result }

    // 3. 신용카드
    if let result = detectCreditCard(text) { return result }

    // 4. 생년월일
    if let result = detectBirthDate(text) { return result }

    // 5. 계좌번호 (마지막 - 통관부호 P 필터링)
    if let result = detectBankAccount(text) { return result }

    // ...
}
```

## 데이터 마이그레이션

하위 호환성 필수:

```swift
func loadMemos() -> [Memo] {
    guard let data = try? Data(contentsOf: memosURL) else { return [] }

    // 1. 최신 형식
    if let newMemos = try? JSONDecoder().decode([Memo].self, from: data) {
        return newMemos
    }

    // 2. 이전 형식 폴백
    else if let oldMemos = try? JSONDecoder().decode([OldMemo].self, from: data) {
        print("🔄 [MemoStore] 마이그레이션: OldMemo → Memo")
        let migrated = oldMemos.map { Memo(from: $0) }
        saveMemos(migrated)  // 자동 저장
        return migrated
    }

    return []
}
```

## Mac Catalyst 조건부 컴파일

```swift
#if targetEnvironment(macCatalyst)
setupMenuBar()
setupGlobalHotkey()
#endif

#if os(iOS)
import UIKit
import Vision
#endif
```

## Published 변수 업데이트

메인 스레드에서 업데이트:

```swift
// ✅ GOOD
DispatchQueue.main.async {
    self.memos = newMemos
}

// ❌ BAD - 백그라운드에서 업데이트
DispatchQueue.global().async {
    self.memos = newMemos  // ❌ UI 업데이트 오류
}
```

## 이미지 처리

```swift
// ✅ GOOD - 1024px 리사이즈 + JPEG 0.7 압축
let resized = image.resized(toWidth: 1024)
guard let imageData = resized.jpegData(compressionQuality: 0.7) else { return }

// App Group Images 폴더에 저장
let imagesDirectory = containerURL.appendingPathComponent("Images")
let imagePath = imagesDirectory.appendingPathComponent("\(UUID().uuidString).jpg")
try? imageData.write(to: imagePath)
```

## 스니펫

자주 사용하는 코드는 `snippets/` 폴더에 저장:

```
snippets/
├── app-group-setup.swift
├── localized-string.swift
├── memostore-usage.swift
└── clipboard-classification.swift
```

## 금지 사항

- ❌ 하드코딩된 UI 문자열 (NSLocalizedString 필수)
- ❌ 표준 Documents/UserDefaults (App Group 필수)
- ❌ Force unwrap (!) 남용
- ❌ 클립보드 분류 우선순위 무시
- ❌ 데이터 마이그레이션 없이 모델 변경
- ❌ Published 변수를 백그라운드에서 업데이트
- ❌ Mac Catalyst 조건부 컴파일 누락

## MARK 주석 사용

```swift
class MemoStore: ObservableObject {
    // MARK: - Properties
    static let shared = MemoStore()
    @Published var memos: [Memo] = []

    // MARK: - Initialization
    private init() { }

    // MARK: - Public Methods
    func loadMemos() { }
    func saveMemos() { }

    // MARK: - Private Helpers
    private func validateMemo(_ memo: Memo) -> Bool { }

    // MARK: - Migration
    private func migrateIfNeeded() { }
}
```

## 파일 크기 권장

- SwiftUI View: **300줄 이하**
- 큰 파일: MARK 주석으로 섹션 구분
- 재사용 컴포넌트: 별도 파일로 분리

## 참고

- **상세 문서**: ../Token-memo/CLAUDE.md
- **공통 표준**: ../shared/coding-standards.md
- **디자인 시스템**: ../shared/design-system.md
