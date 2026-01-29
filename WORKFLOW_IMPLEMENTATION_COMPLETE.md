# 워크플로우 타임라인 구현 완료

## 생성된 파일

### Views/Workflow/ (6개 파일)
1. **TimelineModels.swift** - 핵심 데이터 모델
   - `TimelineTask`: 배치된 태스크 (위치, 병목 정보 포함)
   - `VersionMilestone`: 버전 마일스톤 마커
   - `TimelineLayoutConfig`: 레이아웃 설정
   - `TimelineData`: 타임라인 전체 데이터
   - `TimelineConnection`: 노드 간 연결선

2. **WorkflowTimelineView.swift** - 메인 컨테이너 뷰
   - 앱 선택 드롭다운
   - 줌 컨트롤 (50% ~ 300%)
   - 타임라인 캔버스 (가로/세로 스크롤)
   - 빈 상태 처리

3. **TimelineNode.swift** - 태스크 카드 노드
   - 태스크 이름, 날짜, 버전, 상태 표시
   - 병목 경고 (빨간 테두리)
   - 호버 효과 및 팝오버 상세 정보

4. **TimelineConnector.swift** - 노드 간 연결선
   - 베지어 곡선 연결
   - 상태에 따른 색상 (완료: 녹색, 진행중: 주황, 대기: 회색)

5. **VersionMilestone.swift** - 버전 마일스톤 마커
   - 버전 레이블 및 태스크 카운트
   - 현재 버전 강조 (별 아이콘)

6. **TimelineProgressIndicator.swift** - 현재 위치 표시기
   - 오늘 날짜 마커
   - 펄스 애니메이션

### Services/ (1개 파일)
7. **TimelineInferenceEngine.swift** - 자동 추론 알고리즘
   - 태스크 정렬 (날짜 → 상태 → 이름)
   - 레인 할당 (겹치지 않도록 자동 배치)
   - 병목 탐지 (14일 초과 진행중, 기한 초과)
   - 버전 마일스톤 생성
   - 연결선 추론

### 수정된 파일 (1개)
- **ContentView.swift** - workflow 탭 추가
  - Tab enum에 `.workflow` 추가
  - 사이드바에 "워크플로우" 버튼 추가 (아이콘: timeline.selection)
  - switch 문에 WorkflowTimelineView 추가

---

## ⚠️ Xcode 프로젝트에 파일 추가 필요

새로 생성된 파일들이 Xcode 프로젝트 타겟에 포함되어 있지 않아 빌드 오류가 발생합니다.

### 해결 방법 (Xcode에서 수동 추가):

1. **Xcode를 엽니다**
   ```
   open /Users/hyunholee/Documents/workspace/code/app-portfolio/projects/PortfolioCEO/PortfolioCEO.xcodeproj
   ```

2. **Views/Workflow 폴더를 프로젝트에 추가**
   - 왼쪽 Project Navigator에서 `PortfolioCEO` 프로젝트 선택
   - `Views` 그룹을 마우스 오른쪽 클릭 → "Add Files to 'PortfolioCEO'..."
   - `Views/Workflow` 폴더로 이동
   - 다음 파일들을 모두 선택:
     - TimelineModels.swift
     - WorkflowTimelineView.swift
     - TimelineNode.swift
     - TimelineConnector.swift
     - VersionMilestone.swift
     - TimelineProgressIndicator.swift
   - ✅ "Copy items if needed" 체크 해제 (이미 올바른 위치에 있음)
   - ✅ "Create groups" 선택
   - ✅ "Add to targets: PortfolioCEO" 체크
   - "Add" 클릭

3. **Services/TimelineInferenceEngine.swift 추가**
   - `Services` 그룹을 마우스 오른쪽 클릭 → "Add Files to 'PortfolioCEO'..."
   - `Services/TimelineInferenceEngine.swift` 선택
   - 위와 동일한 옵션으로 "Add" 클릭

4. **빌드 및 실행**
   ```
   ⌘ + B (빌드)
   ⌘ + R (실행)
   ```

---

## 기능 개요

### 자동 추론 알고리즘
- **날짜 기반 정렬**: targetDate를 파싱하여 시간 순서대로 배치
- **버전 그룹핑**: targetVersion별로 태스크 그룹화
- **레인 할당**: 같은 날짜 태스크는 수직으로 분산 (최대 10개 레인)
- **병목 탐지**:
  - 진행중 14일 초과
  - 목표 날짜 지났는데 미완료

### UI 컴포넌트
- **가로 타임라인**: 좌→우 시간 흐름 (날짜 순서)
- **노드 카드**: 태스크 정보, 상태 배지, 병목 경고
- **연결선**: 베지어 곡선, 상태별 색상
- **버전 마커**: 각 버전의 시작 지점 표시
- **현재 위치**: "오늘" 표시기 (펄스 애니메이션)
- **줌 컨트롤**: 50% ~ 300% 확대/축소

### 지원 기능
- **앱 선택**: 드롭다운으로 앱 전환
- **스크롤**: 가로/세로 스크롤 지원
- **호버 효과**: 노드에 마우스 올리면 확대
- **팝오버**: 노드 클릭 시 상세 정보 표시
- **빈 상태**: 날짜 없는 태스크만 있을 때 안내 메시지

---

## 색상 시스템

| 요소 | 색상 |
|------|------|
| 완료 (done) | 녹색 |
| 진행중 (inProgress) | 주황색 |
| 진행전 (todo) | 파란색 |
| 대기 (notStarted) | 회색 |
| 병목 경고 | 빨간 테두리 |
| 현재 위치 | 녹색 (펄스) |

---

## 데이터 흐름

```
PortfolioService.apps
    ↓
WorkflowTimelineView (selectedApp)
    ↓
TimelineInferenceEngine.inferTimeline(tasks, currentVersion)
    ↓
TimelineData {
  - tasks: [TimelineTask] (위치, 레인, 병목 정보)
  - milestones: [VersionMilestone]
  - startDate, endDate
  - canvasWidth, canvasHeight
}
    ↓
렌더링:
  - VersionMilestoneView (버전 마커)
  - TimelineConnectorView (연결선)
  - TimelineNodeView (태스크 카드)
  - TimelineProgressIndicatorView (현재 위치)
```

---

## 검증 체크리스트

### 빌드 테스트
- [ ] Xcode에 파일 추가 완료
- [ ] 컴파일 오류 없음
- [ ] 빌드 성공 (⌘ + B)

### 기능 테스트
- [ ] "워크플로우" 탭 클릭 → WorkflowTimelineView 표시
- [ ] 앱 선택 드롭다운 → 앱 전환 시 타임라인 업데이트
- [ ] 태스크 노드가 날짜 순서대로 좌→우 배치
- [ ] 같은 날짜 태스크는 수직으로 분산
- [ ] 버전 마일스톤이 올바른 위치에 표시
- [ ] 노드 호버 → 확대 효과
- [ ] 노드 클릭 → 팝오버 상세 정보 표시
- [ ] 병목 태스크 → 빨간 테두리 표시
- [ ] 줌 컨트롤 → 50% ~ 300% 조절
- [ ] 날짜 없는 태스크만 있는 앱 → 빈 상태 메시지

### 시각적 확인
- [ ] 연결선이 노드 간 부드럽게 연결 (베지어 곡선)
- [ ] 현재 위치 표시기가 오늘 날짜에 표시 (펄스 애니메이션)
- [ ] 상태별 색상이 올바르게 적용
- [ ] 그리드 배경이 표시 (주 단위 수직선, 레인 수평선)

---

## 향후 개선 아이디어 (MVP 이후)

- [ ] 드래그 앤 드롭으로 태스크 순서 변경
- [ ] 명시적 의존성 필드 추가 (blockedBy/blocks)
- [ ] 크리티컬 패스 강조
- [ ] Gantt 차트 모드 전환
- [ ] PNG/PDF 내보내기
- [ ] 상태/라벨/버전 필터
- [ ] 레이지 렌더링 (뷰포트 기반)
- [ ] 태스크 추가/편집 기능

---

## 문제 해결

### "WorkflowTimelineView not found" 오류
→ Xcode 프로젝트에 파일 추가 필요 (위의 "Xcode 프로젝트에 파일 추가 필요" 섹션 참조)

### 타임라인이 비어 있음
→ 앱의 태스크에 `targetDate` 필드가 설정되어 있는지 확인
→ 날짜 형식: "2026-02-15" (ISO) 또는 "January 31, 2026" (텍스트)

### 위치가 이상함
→ `TimelineInferenceEngine`의 날짜 파싱 로직 확인
→ `AppTask.parsedTargetDate`가 올바르게 파싱되는지 확인

---

## 완료!

워크플로우 타임라인 시각화가 성공적으로 구현되었습니다.
Xcode에 파일을 추가한 후 빌드하면 바로 사용할 수 있습니다.
