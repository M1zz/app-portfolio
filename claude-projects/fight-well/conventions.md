# 코딩 컨벤션

> 공통 코딩 표준은 `../shared/coding-standards.md` 참조

## 앱별 특수 규칙

### 네이밍

#### 이 앱만의 네이밍 규칙
```swift
// 예시: 타이머 관련 타입은 접미사 "Timer" 사용
struct CountdownTimer { }
class IntervalTimer { }
```

### 파일 조직

```
Views/
├── Main/
├── Settings/
└── Components/
```

### 주요 패턴

#### ViewModel 패턴
```swift
@MainActor
class [Feature]ViewModel: ObservableObject {
    @Published var items: [Item] = []
    @Published var isLoading = false

    func loadData() async { }
}
```

#### View 구조
```swift
struct [Feature]View: View {
    @StateObject private var viewModel = [Feature]ViewModel()

    var body: some View {
        content
    }

    private var content: some View {
        // ...
    }
}
```

## 스니펫

자주 사용하는 코드는 `snippets/` 폴더에 저장

## 금지 사항

- [ ] 하드코딩된 문자열 (Localizable.strings 사용)
- [ ] Force unwrap (!) 남용
- [ ] 복잡한 중첩 if문 (guard 사용)
