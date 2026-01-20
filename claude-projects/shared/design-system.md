# 🎨 디자인 시스템 (공통)

## 컬러 팔레트

### Primary Colors
```swift
// Primary
static let primary = Color(hex: "#007AFF")      // iOS Blue
static let primaryDark = Color(hex: "#0051D5")
static let primaryLight = Color(hex: "#4DA2FF")

// Semantic Colors
static let success = Color(hex: "#34C759")     // Green
static let warning = Color(hex: "#FF9500")     // Orange
static let error = Color(hex: "#FF3B30")       // Red
static let info = Color(hex: "#5AC8FA")        // Cyan
```

### Neutral Colors
```swift
static let background = Color(UIColor.systemBackground)
static let secondaryBackground = Color(UIColor.secondarySystemBackground)
static let tertiaryBackground = Color(UIColor.tertiarySystemBackground)

static let label = Color(UIColor.label)
static let secondaryLabel = Color(UIColor.secondaryLabel)
static let tertiaryLabel = Color(UIColor.tertiaryLabel)
```

## 타이포그래피

### Typography Scale
```swift
// Titles
static let largeTitle = Font.system(size: 34, weight: .bold, design: .default)
static let title1 = Font.system(size: 28, weight: .bold)
static let title2 = Font.system(size: 22, weight: .bold)
static let title3 = Font.system(size: 20, weight: .semibold)

// Body
static let headline = Font.system(size: 17, weight: .semibold)
static let body = Font.system(size: 17, weight: .regular)
static let callout = Font.system(size: 16, weight: .regular)

// Small
static let subheadline = Font.system(size: 15, weight: .regular)
static let footnote = Font.system(size: 13, weight: .regular)
static let caption1 = Font.system(size: 12, weight: .regular)
static let caption2 = Font.system(size: 11, weight: .regular)
```

### Font Family
- **기본**: SF Pro (시스템 폰트)
- **숫자**: SF Pro Rounded (선택적)
- **코드**: SF Mono (필요시)

## 간격 (Spacing)

```swift
enum Spacing {
    static let xxxs: CGFloat = 2
    static let xxs: CGFloat = 4
    static let xs: CGFloat = 8
    static let sm: CGFloat = 12
    static let md: CGFloat = 16
    static let lg: CGFloat = 24
    static let xl: CGFloat = 32
    static let xxl: CGFloat = 48
    static let xxxl: CGFloat = 64
}
```

## 컴포넌트

### Buttons

#### Primary Button
```swift
struct LeeoButton: View {
    let title: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.headline)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.primary)
                .cornerRadius(12)
        }
    }
}
```

#### Secondary Button
```swift
struct LeeoSecondaryButton: View {
    let title: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.headline)
                .foregroundColor(.primary)
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.primary.opacity(0.1))
                .cornerRadius(12)
        }
    }
}
```

### Cards

```swift
struct LeeoCard<Content: View>: View {
    let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.md) {
            content
        }
        .padding(Spacing.md)
        .background(Color.secondaryBackground)
        .cornerRadius(16)
        .shadow(color: .black.opacity(0.1), radius: 8, y: 4)
    }
}
```

### Input Fields

```swift
struct LeeoTextField: View {
    let placeholder: String
    @Binding var text: String

    var body: some View {
        TextField(placeholder, text: $text)
            .padding()
            .background(Color.secondaryBackground)
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
            )
    }
}
```

## 아이콘

### SF Symbols 사용
```swift
// 공통 아이콘
static let checkmark = "checkmark.circle.fill"
static let xmark = "xmark.circle.fill"
static let warning = "exclamationmark.triangle.fill"
static let info = "info.circle.fill"

static let add = "plus.circle.fill"
static let delete = "trash.fill"
static let edit = "pencil"
static let share = "square.and.arrow.up"

static let timer = "timer"
static let bell = "bell.fill"
static let calendar = "calendar"
static let person = "person.fill"
```

### 아이콘 크기
```swift
enum IconSize {
    static let small: CGFloat = 16
    static let medium: CGFloat = 24
    static let large: CGFloat = 32
    static let xlarge: CGFloat = 48
}
```

## 애니메이션

### 기본 애니메이션
```swift
// 표준 애니메이션
static let standard = Animation.easeInOut(duration: 0.3)
static let quick = Animation.easeInOut(duration: 0.2)
static let slow = Animation.easeInOut(duration: 0.5)

// 스프링 애니메이션
static let spring = Animation.spring(response: 0.3, dampingFraction: 0.7)
static let bouncy = Animation.spring(response: 0.5, dampingFraction: 0.6)
```

### 트랜지션
```swift
// 페이지 전환
.transition(.asymmetric(
    insertion: .move(edge: .trailing),
    removal: .move(edge: .leading)
))

// 모달 표시
.transition(.opacity.combined(with: .scale))
```

## 그림자

```swift
enum Shadow {
    // 작은 그림자
    static let small = (color: Color.black.opacity(0.1), radius: 4.0, x: 0.0, y: 2.0)

    // 중간 그림자
    static let medium = (color: Color.black.opacity(0.15), radius: 8.0, x: 0.0, y: 4.0)

    // 큰 그림자
    static let large = (color: Color.black.opacity(0.2), radius: 16.0, x: 0.0, y: 8.0)
}
```

## Corner Radius

```swift
enum CornerRadius {
    static let small: CGFloat = 8
    static let medium: CGFloat = 12
    static let large: CGFloat = 16
    static let xlarge: CGFloat = 24
}
```

## 레이아웃 가이드

### Safe Area
- 모든 주요 콘텐츠는 Safe Area 내에 배치
- 배경색/이미지는 Safe Area 무시 가능

### 그리드
- 기본 간격: 16pt
- 카드 간격: 12pt
- 섹션 간격: 24pt

### 최소 터치 영역
- 버튼: 최소 44x44pt
- 탭: 최소 48x48pt

## 다크 모드

### 자동 지원
- `Color(UIColor.systemBackground)` 사용 시 자동
- 커스텀 컬러는 Asset Catalog에서 Light/Dark 정의

### 다크 모드 체크
```swift
@Environment(\.colorScheme) var colorScheme

if colorScheme == .dark {
    // 다크 모드 전용 로직
}
```

## 접근성

### Dynamic Type
```swift
// 자동으로 텍스트 크기 조절
Text("Hello")
    .font(.body)  // Dynamic Type 지원
```

### VoiceOver
```swift
Button("삭제") {
    // action
}
.accessibilityLabel("항목 삭제")
.accessibilityHint("이 항목을 영구적으로 삭제합니다")
```

### 최소 대비율
- WCAG AA 기준: 4.5:1 (일반 텍스트)
- WCAG AA 기준: 3:1 (큰 텍스트)

## 사용 예시

```swift
struct ExampleView: View {
    @State private var text = ""

    var body: some View {
        VStack(spacing: Spacing.lg) {
            LeeoCard {
                VStack(alignment: .leading, spacing: Spacing.md) {
                    Text("카드 타이틀")
                        .font(.title3)

                    Text("카드 내용입니다.")
                        .font(.body)
                        .foregroundColor(.secondaryLabel)
                }
            }

            LeeoTextField(placeholder: "입력하세요", text: $text)

            LeeoButton(title: "확인") {
                print("버튼 클릭")
            }
        }
        .padding(Spacing.lg)
    }
}
```

---

**모든 앱에서 이 디자인 시스템을 따릅니다.**
