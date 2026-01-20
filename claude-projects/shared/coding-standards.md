# 📐 코딩 표준 (공통)

## Swift 스타일 가이드

### 네이밍 컨벤션

#### 타입 (Types)
```swift
// ✅ 올바른 예
struct User { }
class NetworkManager { }
enum AppState { }
protocol Loadable { }

// ❌ 잘못된 예
struct user { }          // 소문자 시작
class networkManager { } // 소문자 시작
```

#### 변수 및 함수
```swift
// ✅ 올바른 예
let userName = "John"
var isLoading = false
func fetchUserData() { }

// ❌ 잘못된 예
let UserName = "John"    // 대문자 시작
var is_loading = false   // 스네이크 케이스
```

#### Bool 변수
```swift
// ✅ 올바른 예
var isEnabled = true
var hasData = false
var canEdit = true
var shouldRefresh = false

// ❌ 잘못된 예
var enabled = true       // 명확하지 않음
var data = false         // Bool임이 불분명
```

### 파일 구조

```
Sources/
├── Models/
│   ├── User.swift
│   ├── Task.swift
│   └── Settings.swift
│
├── Views/
│   ├── MainView.swift
│   ├── SettingsView.swift
│   └── Components/
│       ├── CardView.swift
│       └── ButtonView.swift
│
├── ViewModels/
│   ├── MainViewModel.swift
│   └── SettingsViewModel.swift
│
├── Services/
│   ├── NetworkService.swift
│   ├── DataService.swift
│   └── NotificationService.swift
│
└── Utilities/
    ├── Extensions/
    │   ├── Color+Extensions.swift
    │   └── Date+Extensions.swift
    └── Constants.swift
```

### MARK 사용

```swift
struct UserView: View {
    // MARK: - Properties
    @State private var username = ""
    @StateObject private var viewModel = UserViewModel()

    // MARK: - Body
    var body: some View {
        VStack {
            // ...
        }
    }

    // MARK: - Private Methods
    private func validateInput() -> Bool {
        // ...
    }

    // MARK: - Actions
    private func handleSubmit() {
        // ...
    }
}
```

### 들여쓰기 및 포맷팅

```swift
// ✅ 올바른 예
func processData(
    user: User,
    items: [Item],
    completion: @escaping (Result<Data, Error>) -> Void
) {
    // 4 spaces 들여쓰기
    if user.isValid {
        // ...
    }
}

// 최대 줄 길이: 120자
```

### SwiftLint 설정

```.swiftlint.yml
disabled_rules:
  - trailing_whitespace
opt_in_rules:
  - empty_count
  - closure_spacing
  - explicit_init

line_length:
  warning: 120
  error: 200

identifier_name:
  min_length:
    warning: 2
  max_length:
    warning: 40
```

## SwiftUI 패턴

### View 구조

```swift
// ✅ 권장 패턴
struct UserProfileView: View {
    // Properties
    @StateObject private var viewModel: UserProfileViewModel

    // Initializer
    init(userId: String) {
        _viewModel = StateObject(wrappedValue: UserProfileViewModel(userId: userId))
    }

    // Body
    var body: some View {
        content
    }

    // Extracted Views
    private var content: some View {
        VStack {
            headerSection
            profileSection
            actionsSection
        }
    }

    private var headerSection: some View {
        // ...
    }
}
```

### State Management

```swift
// ✅ 상태 관리 원칙
@State private var text = ""           // View 로컬 상태
@StateObject private var vm = VM()     // ViewModel 소유
@ObservedObject var manager: Manager   // 외부에서 전달받은 객체
@EnvironmentObject var settings: Settings  // 환경 객체
@Binding var isPresented: Bool         // 부모와 양방향 바인딩
```

### View Modifiers 순서

```swift
// ✅ 권장 순서
Text("Hello")
    .font(.title)              // 1. 텍스트 스타일
    .foregroundColor(.primary) // 2. 색상
    .padding()                 // 3. 패딩
    .background(Color.blue)    // 4. 배경
    .cornerRadius(8)           // 5. 모양
    .shadow(radius: 4)         // 6. 그림자
    .onTapGesture { }          // 7. 제스처
```

## MVVM 패턴

### ViewModel 예시

```swift
@MainActor
class UserViewModel: ObservableObject {
    // MARK: - Published Properties
    @Published var user: User?
    @Published var isLoading = false
    @Published var errorMessage: String?

    // MARK: - Private Properties
    private let service: UserService

    // MARK: - Initialization
    init(service: UserService = UserService()) {
        self.service = service
    }

    // MARK: - Public Methods
    func loadUser(id: String) async {
        isLoading = true
        errorMessage = nil

        do {
            user = try await service.fetchUser(id: id)
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    // MARK: - Private Methods
    private func validateUser(_ user: User) -> Bool {
        // ...
    }
}
```

## 에러 핸들링

### 커스텀 에러

```swift
enum AppError: LocalizedError {
    case networkError
    case invalidData
    case unauthorized

    var errorDescription: String? {
        switch self {
        case .networkError:
            return "네트워크 연결을 확인해주세요"
        case .invalidData:
            return "데이터 형식이 올바르지 않습니다"
        case .unauthorized:
            return "권한이 없습니다"
        }
    }
}
```

### 에러 처리

```swift
// ✅ 올바른 예
func fetchData() async throws -> Data {
    guard let url = URL(string: endpoint) else {
        throw AppError.invalidData
    }

    let (data, response) = try await URLSession.shared.data(from: url)

    guard (response as? HTTPURLResponse)?.statusCode == 200 else {
        throw AppError.networkError
    }

    return data
}
```

## 비동기 처리

### async/await 사용

```swift
// ✅ 권장
func loadData() async throws -> [Item] {
    let data = try await networkService.fetchItems()
    let items = try JSONDecoder().decode([Item].self, from: data)
    return items
}

// View에서 사용
.task {
    do {
        items = try await viewModel.loadData()
    } catch {
        errorMessage = error.localizedDescription
    }
}
```

## Git 커밋 메시지

### 형식

```
<type>: <subject>

<body>

<footer>
```

### Type
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드, 패키지 관련

### 예시

```
feat: 사용자 프로필 이미지 업로드 기능 추가

- ImagePicker를 사용한 이미지 선택
- Firebase Storage 업로드
- 프로필 이미지 캐싱

Closes #123
```

## 주석

### 문서 주석

```swift
/// 사용자 데이터를 로드합니다.
///
/// - Parameter id: 사용자 고유 ID
/// - Returns: 사용자 객체
/// - Throws: `AppError.networkError` 네트워크 오류 시
///           `AppError.invalidData` 데이터 파싱 실패 시
func loadUser(id: String) async throws -> User {
    // ...
}
```

### 인라인 주석

```swift
// ✅ 올바른 예 - 명확한 이유 설명
// FIXME: iOS 16에서 크래시 발생, 임시 workaround
// TODO: API v2로 마이그레이션 필요
// NOTE: 이 로직은 백그라운드에서만 실행됨

// ❌ 잘못된 예 - 코드 자체가 설명
// 변수에 값을 할당
let name = user.name
```

## 테스트

### 네이밍

```swift
// ✅ 권장
func testUserLoginWithValidCredentials() { }
func testFetchDataThrowsErrorWhenNetworkFails() { }

// 패턴: test[UnitOfWork]_[StateUnderTest]_[ExpectedBehavior]
```

### 구조

```swift
func testCalculateTotalPrice() {
    // Given (준비)
    let cart = ShoppingCart()
    cart.add(item: Item(price: 100))
    cart.add(item: Item(price: 200))

    // When (실행)
    let total = cart.calculateTotal()

    // Then (검증)
    XCTAssertEqual(total, 300)
}
```

## 성능 최적화

### LazyStack 사용

```swift
// ✅ 많은 아이템 표시 시
LazyVStack {
    ForEach(items) { item in
        ItemRow(item: item)
    }
}

// ❌ 적은 아이템(< 10)일 때는 VStack으로 충분
VStack {
    ForEach(items) { item in
        ItemRow(item: item)
    }
}
```

### 이미지 최적화

```swift
// ✅ 적절한 크기로 리사이징
AsyncImage(url: url) { image in
    image
        .resizable()
        .aspectRatio(contentMode: .fill)
        .frame(width: 100, height: 100)
        .clipped()
}
```

## 보안

### 민감 정보 처리

```swift
// ✅ Keychain 사용
KeychainHelper.save(token: authToken)

// ❌ UserDefaults 사용 금지
UserDefaults.standard.set(authToken, forKey: "token")  // 위험!
```

### API Key 관리

```swift
// ✅ Config.plist 사용 (gitignore에 추가)
// ❌ 코드에 하드코딩 금지
```

---

**모든 코드는 이 표준을 따릅니다.**
