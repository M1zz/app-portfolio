#!/bin/bash
# Claude 프로젝트 생성 스크립트

set -e

# 인자 확인
if [ $# -lt 2 ]; then
    echo "사용법: $0 <앱이름_한글> <앱이름_영문>"
    echo "예시: $0 '두 번 알림' 'Double Reminder'"
    exit 1
fi

APP_NAME_KO="$1"
APP_NAME_EN="$2"
FOLDER_NAME=$(echo "$APP_NAME_EN" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

echo "🔨 Claude 프로젝트 생성 중..."
echo "  한글 이름: $APP_NAME_KO"
echo "  영문 이름: $APP_NAME_EN"
echo "  폴더 이름: $FOLDER_NAME"
echo ""

# 프로젝트 폴더 생성
PROJECT_DIR="claude-projects/$FOLDER_NAME"
mkdir -p "$PROJECT_DIR/snippets"

# 1. .claude-project 파일 생성
cat > "$PROJECT_DIR/.claude-project" << EOF
{
  "name": "$APP_NAME_KO ($APP_NAME_EN)",
  "description": "iOS 앱 개발 프로젝트",
  "version": "1.0.0",
  "context": [
    "team.md",
    "architecture.md",
    "conventions.md",
    "decisions-log.md",
    "context.md",
    "../shared/design-system.md",
    "../shared/coding-standards.md"
  ],
  "customInstructions": "SwiftUI 기반 iOS 앱. 공통 디자인 시스템과 코딩 표준을 준수합니다."
}
EOF
echo "✅ .claude-project 생성 완료"

# 2. architecture.md 생성
cat > "$PROJECT_DIR/architecture.md" << 'EOF'
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
EOF
echo "✅ architecture.md 생성 완료"

# 3. conventions.md 생성
cat > "$PROJECT_DIR/conventions.md" << 'EOF'
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
EOF
echo "✅ conventions.md 생성 완료"

# 4. decisions-log.md 생성
cat > "$PROJECT_DIR/decisions-log.md" << 'EOF'
# 주요 결정 사항 로그

## 2026-01-18: 프로젝트 초기 설정

**결정**: Claude 프로젝트 구조 생성
**이유**: 앱별 컨텍스트 분리 및 효율적인 개발
**영향**: 모든 개발은 이 프로젝트 컨텍스트에서 진행

---

## 템플릿

### [날짜]: [결정 제목]

**상황**:
<!-- 무엇이 문제였는가? -->

**결정**:
<!-- 어떤 결정을 내렸는가? -->

**대안**:
<!-- 고려했던 다른 옵션들 -->

**이유**:
<!-- 왜 이 결정을 내렸는가? -->

**영향**:
<!-- 이 결정이 코드/아키텍처에 미치는 영향 -->

**추가 작업**:
<!-- 이 결정으로 인해 필요한 작업 -->

---
EOF
echo "✅ decisions-log.md 생성 완료"

# 5. context.md 생성 (앱 데이터에서 정보 가져오기)
APP_JSON_FILE="apps/${FOLDER_NAME}.json"

if [ -f "$APP_JSON_FILE" ]; then
    # JSON 파일에서 데이터 읽기
    BUNDLE_ID=$(grep '"bundleId"' "$APP_JSON_FILE" | sed 's/.*": "//; s/".*//')
    VERSION=$(grep '"currentVersion"' "$APP_JSON_FILE" | sed 's/.*": "//; s/".*//')
    STATUS=$(grep '"status"' "$APP_JSON_FILE" | sed 's/.*": "//; s/".*//')
    PRIORITY=$(grep '"priority"' "$APP_JSON_FILE" | sed 's/.*": "//; s/".*//')

    cat > "$PROJECT_DIR/context.md" << EOF
# $APP_NAME_KO - 빠른 컨텍스트

## 기본 정보

- **앱 이름**: $APP_NAME_KO ($APP_NAME_EN)
- **Bundle ID**: $BUNDLE_ID
- **현재 버전**: $VERSION
- **상태**: $STATUS
- **우선순위**: $PRIORITY

## 핵심 기능

1.
2.
3.

## 현재 진행 상황

<!-- apps/${FOLDER_NAME}.json 참조 -->

### 다음 태스크
- [ ]

### 최근 완료
- [x]

## 주요 기술

- SwiftUI
-
-

## 알아야 할 것

### 제약사항
-

### 특이사항
-

### 주의사항
-

## 빠른 참조

### 주요 파일
- \`MainView.swift\`:
- \`AppModel.swift\`:

### 자주 하는 작업
\`\`\`swift
// 예시 코드
\`\`\`

## 배포 정보

- **TestFlight**:
- **App Store**:
- **최근 배포**:

---

**마지막 업데이트**: $(date +"%Y-%m-%d")
EOF
else
    # 템플릿으로 생성
    cat > "$PROJECT_DIR/context.md" << 'EOF'
# 앱 - 빠른 컨텍스트

## 기본 정보

- **앱 이름**:
- **Bundle ID**:
- **현재 버전**:
- **상태**:
- **우선순위**:

## 핵심 기능

1.
2.
3.

## 현재 진행 상황

### 다음 태스크
- [ ]

### 최근 완료
- [x]

## 알아야 할 것

### 제약사항
-

### 특이사항
-

---

**마지막 업데이트**:
EOF
fi
echo "✅ context.md 생성 완료"

# 5.5. team.md 생성
cat > "$PROJECT_DIR/team.md" << 'EOF'
# 팀 구성

> 이 문서는 Claude가 프로젝트 작업 시 자동으로 로드하는 팀 컨텍스트입니다.

## 👨‍💻 개발팀 (Development Team)

### 이현호 (Lead Developer)
- **역할**: iOS 앱 전체 개발
- **담당**: SwiftUI, CoreData/SwiftData, API 통신
- **컨택**: @hyunholee
- **작업 범위**:
  - 앱 아키텍처 설계 및 구현
  - 코어 기능 개발
  - 버그 수정 및 성능 최적화
  - 코드 리뷰

## 📋 기획팀 (Planning Team)

### 이현호 (Product Manager)
- **역할**: 제품 기획 및 로드맵 관리
- **담당**: 기능 우선순위, 사용자 피드백 분석
- **컨택**: @hyunholee
- **작업 범위**:
  - 기능 요구사항 정의
  - 우선순위 결정
  - 사용자 피드백 수집 및 분석
  - 릴리즈 계획 수립

## 🎨 디자인팀 (Design Team)

### 이현호 (UI/UX Designer)
- **역할**: 디자인 시스템 구축 및 UI/UX 개선
- **담당**: UI 컴포넌트, 사용자 경험 개선
- **컨택**: @hyunholee
- **작업 범위**:
  - UI/UX 디자인
  - 디자인 시스템 유지보수
  - 사용성 테스트
  - 프로토타입 제작

---

## 🤝 협업 규칙

### 의사 결정 프로세스
1. **기획**: PM이 기능 요구사항 정의
2. **디자인 검토**: 새 기능 개발 전 디자인 검토 필수
3. **개발**: 개발팀이 구현
4. **코드 리뷰**: PR 머지 전 팀 리드 승인 필요

### 커뮤니케이션
- **주간 스프린트**: 매주 월요일 기획 회의
- **일일 스탠드업**: 매일 오전 10시 (선택)
- **긴급 이슈**: Slack/Discord 즉시 공유

### 문서화 규칙
- 주요 결정 사항은 `decisions-log.md`에 기록
- 아키텍처 변경은 `architecture.md` 업데이트
- 새로운 컨벤션은 `conventions.md`에 추가

---

## 📊 팀 현황

- **팀 규모**: 3개 팀 (개발/기획/디자인)
- **전체 인원**: 3명 (현재는 1인 다역할)
- **작업 방식**: 애자일, 2주 스프린트

---

**마지막 업데이트**: $(date +"%Y-%m-%d")

---

## 💡 Claude에게

이 문서를 읽고 있다면, 당신은 이 앱의 개발에 참여하고 있습니다.

- 코드를 작성할 때는 **개발팀의 컨벤션**을 따르세요
- 새 기능을 제안할 때는 **기획팀의 우선순위**를 고려하세요
- UI를 변경할 때는 **디자인팀의 디자인 시스템**을 준수하세요
- 중요한 결정을 내릴 때는 팀 리드에게 확인을 요청하세요

팀원 정보는 `apps/[app-name].json` 파일의 `team` 섹션에서 자세히 확인할 수 있습니다.
EOF
echo "✅ team.md 생성 완료"

# 6. README.md 생성
cat > "$PROJECT_DIR/README.md" << EOF
# $APP_NAME_KO ($APP_NAME_EN)

## 📱 프로젝트 정보

이 폴더는 **$APP_NAME_KO** 앱의 Claude 프로젝트입니다.

## 📁 파일 구조

- \`.claude-project\`: 프로젝트 설정
- \`team.md\`: 팀 구성 및 협업 규칙 ⭐
- \`architecture.md\`: 앱 아키텍처 문서
- \`conventions.md\`: 코딩 컨벤션
- \`decisions-log.md\`: 주요 결정 사항
- \`context.md\`: 빠른 컨텍스트 참조
- \`snippets/\`: 자주 쓰는 코드 스니펫

## 🚀 사용 방법

\`\`\`bash
cd claude-projects/$FOLDER_NAME
claude chat
\`\`\`

Claude가 자동으로 모든 컨텍스트를 로드합니다.

## 📚 참고

- 공통 디자인 시스템: \`../shared/design-system.md\`
- 공통 코딩 표준: \`../shared/coding-standards.md\`
EOF
echo "✅ README.md 생성 완료"

# 7. snippets 폴더에 예시 생성
cat > "$PROJECT_DIR/snippets/view-template.swift" << 'EOF'
// SwiftUI View 템플릿

import SwiftUI

struct [Name]View: View {
    @StateObject private var viewModel = [Name]ViewModel()

    var body: some View {
        content
    }

    private var content: some View {
        VStack {
            // Content here
        }
    }
}

#Preview {
    [Name]View()
}
EOF
echo "✅ snippets/ 폴더 생성 완료"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Claude 프로젝트 생성 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 위치: $PROJECT_DIR"
echo ""
echo "🚀 사용 방법:"
echo "  cd $PROJECT_DIR"
echo "  claude chat"
echo ""
echo "📝 다음 단계:"
echo "  1. architecture.md 작성"
echo "  2. context.md에 앱 정보 입력"
echo "  3. conventions.md에 앱별 규칙 추가"
echo ""
