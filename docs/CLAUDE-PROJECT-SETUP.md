# 🎯 Claude 프로젝트 기반 개발 환경 구축 가이드

## 📋 개요

각 앱마다 독립적인 Claude 프로젝트를 만들어 앱별 컨텍스트를 완벽히 분리합니다.

## 🏗️ 폴더 구조

```
app-portfolio/
├── apps/                           # 앱 데이터
│   └── *.json
│
├── claude-projects/                # 🆕 Claude 프로젝트들
│   ├── shared/                     # 공통 프로젝트
│   │   ├── .claude-project
│   │   ├── design-system.md
│   │   ├── swift-packages.md
│   │   ├── app-store-templates.md
│   │   └── coding-standards.md
│   │
│   ├── double-reminder/            # 앱별 프로젝트
│   │   ├── .claude-project
│   │   ├── architecture.md
│   │   ├── conventions.md
│   │   ├── snippets/
│   │   ├── decisions-log.md
│   │   └── context.md
│   │
│   ├── rapport-map/
│   │   ├── .claude-project
│   │   ├── architecture.md
│   │   └── ...
│   │
│   └── ... (23개 앱)
│
└── scripts/
    └── create-claude-project.sh   # 프로젝트 생성 스크립트
```

## 📝 각 프로젝트에 포함될 파일

### 1. `.claude-project` (프로젝트 설정)
```json
{
  "name": "두 번 알림 (Double Reminder)",
  "description": "타이머 기반 다중 알림 iOS 앱",
  "context": [
    "architecture.md",
    "conventions.md",
    "decisions-log.md",
    "../shared/design-system.md",
    "../shared/coding-standards.md"
  ],
  "customInstructions": "SwiftUI 기반 iOS 앱. 알림 타이밍과 UX가 핵심."
}
```

### 2. `architecture.md` (앱 아키텍처)
```markdown
# 앱 아키텍처

## 핵심 모델
- Timer, Notification, UserSettings

## 뷰 구조
- MainView → TimerListView → TimerDetailView

## 데이터 흐름
- SwiftData 로컬 저장
- iCloud 동기화 (예정)

## 주요 기술 스택
- SwiftUI, Combine
- UserNotifications
- WidgetKit
```

### 3. `conventions.md` (코딩 컨벤션)
```markdown
# 코딩 컨벤션

## 네이밍
- View: `xxxView`
- ViewModel: `xxxViewModel`
- Model: 단수형 명사

## 파일 구조
```
Sources/
  Models/
  Views/
  ViewModels/
  Services/
```

## 4. `snippets/` (자주 쓰는 코드)
```swift
// SwiftUI View 템플릿
// Notification 설정 코드
// 등
```

### 5. `decisions-log.md` (주요 결정 사항)
```markdown
# 결정 사항 로그

## 2025-12-03: 알림 레이블 추가
- **결정**: 각 알림마다 커스텀 레이블 지원
- **이유**: 사용자가 여러 타이머를 구분하기 어려움
- **구현**: NotificationLabel 프로퍼티 추가

## 2025-11-25: SwiftData 마이그레이션
...
```

### 6. `context.md` (빠른 컨텍스트)
```markdown
# 두 번 알림 - 빠른 컨텍스트

## 현재 상태
- 버전: 1.0.5
- 우선순위: 높음
- 진행률: 71% (10/14)

## 핵심 기능
1. 다중 타이머 설정
2. 예비 알림 (pre-notification)
3. Apple Watch 지원

## 다음 작업
- [ ] 1.0.5 배포
- [ ] iCloud 동기화
- [ ] 접근성 개선

## 알아야 할 것
- 알림 권한 필수
- 백그라운드 제한 있음
- Watch 앱 별도 타겟
```

## 🌐 공통 프로젝트 (Shared)

### `design-system.md`
```markdown
# 디자인 시스템

## 컬러 팔레트
- Primary: #007AFF
- Success: #34C759
- Warning: #FF9500
- Error: #FF3B30

## 타이포그래피
- Title: SF Pro Display, Bold, 34pt
- Headline: SF Pro Text, Semibold, 17pt
- Body: SF Pro Text, Regular, 17pt

## 컴포넌트
- PrimaryButton
- SecondaryButton
- Card
...
```

### `swift-packages.md`
```markdown
# 공유 Swift 패키지

## LeeoKit (공통 UI 컴포넌트)
```swift
import LeeoKit

LeeoButton(title: "확인", style: .primary) {
    // action
}
```

## LeeoAnalytics (분석)
## LeeoCore (유틸리티)
```

### `coding-standards.md`
```markdown
# 공통 코딩 표준

## Swift 스타일 가이드
- SwiftLint 설정 사용
- 들여쓰기: 4 spaces
- 최대 줄 길이: 120자

## Git 커밋 메시지
```
feat: 새 기능
fix: 버그 수정
docs: 문서 수정
refactor: 리팩토링
```

## 테스트
- 단위 테스트 필수
- UI 테스트 권장
```

## 🚀 사용 방법

### 1. 특정 앱 작업 시
```bash
cd claude-projects/double-reminder
claude chat
```

Claude가 자동으로:
- `.claude-project` 읽음
- `architecture.md`, `conventions.md` 로드
- 공통 파일 (`../shared/*`) 참조

### 2. 빠른 업데이트
```
"두 번 알림 업데이트해줘"
→ Claude가 해당 프로젝트 컨텍스트 자동 로드
→ 아키텍처, 컨벤션 준수
→ 결정 사항 로그 업데이트
```

### 3. 새 앱 추가
```bash
./scripts/create-claude-project.sh "새앱이름" "New App Name"
```

## 🎯 장점

### 1. 컨텍스트 분리
- 각 앱의 고유한 아키텍처 유지
- 혼선 방지

### 2. 일관성 유지
- 공통 표준 준수
- 디자인 시스템 통일

### 3. 빠른 재개
- 프로젝트 열면 즉시 컨텍스트 파악
- 이전 결정 사항 확인 가능

### 4. 협업 용이
- 문서화된 아키텍처
- 명확한 컨벤션

### 5. 지식 축적
- 결정 사항 로그
- 베스트 프랙티스 수집

## 📊 예상 효과

### 개발 시간
- **컨텍스트 전환 시간**: 5분 → 30초
- **코딩 컨벤션 확인**: 매번 검색 → 자동 적용
- **이전 결정 사항 찾기**: 10분 → 즉시

### 코드 품질
- **일관성**: 앱마다 다름 → 통일된 패턴
- **문서화**: 부족 → 항상 최신 상태
- **유지보수성**: ↑↑↑

## 🔧 자동화

### 프로젝트 생성 스크립트
```bash
#!/bin/bash
# create-claude-project.sh

APP_NAME_KO="$1"
APP_NAME_EN="$2"
FOLDER_NAME=$(echo "$APP_NAME_EN" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

mkdir -p "claude-projects/$FOLDER_NAME"
cd "claude-projects/$FOLDER_NAME"

# .claude-project 생성
# architecture.md 템플릿 생성
# conventions.md 템플릿 생성
# 등...
```

### 컨텍스트 동기화
```bash
# 앱 데이터 → Claude 프로젝트 동기화
./scripts/sync-app-context.sh double-reminder
```

## 🎊 시작하기

다음 명령어로 모든 프로젝트를 생성합니다:
```bash
./scripts/setup-all-claude-projects.sh
```

그 다음:
```bash
cd claude-projects/double-reminder
claude chat
"현재 앱 상태 요약해줘"
```

---

**이제 각 앱의 컨텍스트를 완벽히 분리하여 관리할 수 있습니다!** 🚀
