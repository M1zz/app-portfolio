# PortfolioCEO 프로젝트 가이드

이 레포지토리는 iOS/macOS 앱 포트폴리오를 관리하는 CEO 앱과 관련 데이터를 포함합니다.

---

## 📁 프로젝트 구조

```
app-portfolio/
├── .claude/
│   └── CLAUDE.md                    # 이 파일 - Claude 작업 가이드
│
├── docs/                            # 문서 및 가이드
│   ├── CEO-WORKFLOW.md              # CEO 워크플로우 문서
│   ├── CLAUDE-GUIDE.md              # Claude 사용 가이드
│   └── ...
│
├── projects/
│   └── PortfolioCEO/                # Xcode 프로젝트
│       ├── PortfolioCEO/            # macOS CEO 앱 소스
│       │   ├── Data/                # ⭐ 핵심 데이터 폴더
│       │   │   ├── apps/            # 각 앱별 메타데이터 JSON
│       │   │   ├── data/            # 공유 데이터
│       │   │   └── project-notes/   # 피드백 및 노트
│       │   │
│       │   ├── Models/              # 데이터 모델
│       │   ├── Views/               # SwiftUI 뷰
│       │   └── Services/            # 서비스 (PortfolioService 등)
│       │
│       ├── CEOfeedback/             # iOS 피드백 앱
│       └── Shared/                  # 공유 코드
│
├── claude-projects/                 # 각 앱별 Claude 프로젝트 컨텍스트
└── scripts/                         # 자동화 스크립트
```

---

## ⭐ 핵심 데이터 위치

### CEO 앱 데이터 경로
```
projects/PortfolioCEO/PortfolioCEO/Data/
```

### 주요 데이터 파일

| 경로 | 설명 |
|------|------|
| `Data/apps/*.json` | 각 앱의 메타데이터 (태스크, 버전, 상태 등) |
| `Data/data/decisions-queue.json` | 의사결정 대기열 |
| `Data/data/portfolio-summary.json` | 포트폴리오 요약 (대시보드용) |
| `Data/data/app-name-mapping.json` | 앱 이름 ↔ 폴더명 매핑 |
| `Data/project-notes/*.json` | 앱별 피드백 및 노트 |

---

## 🎯 Claude 작업 가이드

### 1. 앱 정보 조회/수정 시
```
# 앱 메타데이터 파일 위치
projects/PortfolioCEO/PortfolioCEO/Data/apps/{앱이름}.json

# 예시
projects/PortfolioCEO/PortfolioCEO/Data/apps/clip-keyboard.json
```

### 2. 태스크 상태 값
- `done`: 완료
- `in-progress`: 진행 중
- `todo`: 진행전 (계획됨)
- `not-started`: 대기 (백로그)

### 3. 의사결정 처리 시
```
# 의사결정 큐 파일
projects/PortfolioCEO/PortfolioCEO/Data/data/decisions-queue.json
```

### 4. 피드백 처리 시
```
# 피드백 폴더
projects/PortfolioCEO/PortfolioCEO/Data/project-notes/
```

---

## 📋 작업 워크플로우

### 피드백 → 태스크 변환

1. **피드백 읽기**
   ```
   Data/project-notes/{앱폴더명}/feedback.json
   ```

2. **분석 및 태스크 생성**
   - 피드백 내용 분석
   - 우선순위 결정
   - 앱 JSON에 태스크 추가

3. **앱 JSON 업데이트**
   ```json
   // Data/apps/{앱이름}.json
   {
     "allTasks": [
       {
         "name": "태스크 이름",
         "status": "todo",
         "targetVersion": "1.0.0",
         "targetDate": "January 31, 2026"
       }
     ]
   }
   ```

4. **stats 업데이트**
   - totalTasks, done, inProgress, todo, notStarted 갱신

---

## 🔧 CEO 앱 소스 코드

### 주요 파일

| 파일 | 설명 |
|------|------|
| `Models/AppModel.swift` | 앱, 태스크, 상태 모델 정의 |
| `Views/AppsGridView.swift` | 전체 앱 그리드 뷰 |
| `Views/KanbanView.swift` | 칸반 보드 |
| `Views/ProjectDetail/TasksSectionView.swift` | 태스크 섹션 |
| `Services/PortfolioService.swift` | 데이터 로드/저장 서비스 |

### TaskStatus enum
```swift
enum TaskStatus: String, Codable {
    case done           // 완료
    case inProgress     // 진행 중 ("in-progress")
    case todo           // 진행전
    case notStarted     // 대기 ("not-started")
}
```

---

## 📝 워크플로우 기록

### 2026-01-29: 폴더 구조 통합

**변경 사항:**
- `apps/`, `data/`, `project-notes/` 폴더를 CEO 앱 프로젝트 내 `Data/`로 통합
- PortfolioService 경로 업데이트
- CLAUDE.md 재작성

**새 구조:**
```
projects/Register Local Experience/PortfolioCEO/Data/
├── apps/              # 앱 메타데이터
├── data/              # 공유 데이터
└── project-notes/     # 피드백/노트
```

### 2026-01-29: TaskStatus에 todo 추가

**변경 사항:**
- `TaskStatus` enum에 `todo` case 추가 (진행전)
- 통계 카드에 "진행전" 추가
- 앱 카드 표시: 완료/전체 → 완료/진행전

---

## 💡 참고 사항

- CEO 앱은 `Data/` 폴더의 JSON 파일을 실시간 감시
- JSON 파일 수정 시 앱이 자동으로 새로고침
- 앱 이름과 폴더명 매핑은 `Data/data/app-name-mapping.json` 참조

### 여러 컴퓨터에서 사용

CEO 앱은 다음 순서로 데이터 폴더를 자동 감지:
1. 사용자가 설정한 경로 (Settings에서 변경 가능)
2. 앱 소스 코드 위치 기준 `../Data/` 폴더
3. 일반적인 경로들 (`~/Documents/code/app-portfolio/...` 등)

새 컴퓨터에서 설정:
1. 앱 실행 후 Settings → 데이터 경로
2. "자동 감지" 버튼 클릭 또는 "폴더 선택"으로 직접 지정
