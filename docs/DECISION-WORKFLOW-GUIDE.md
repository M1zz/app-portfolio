# Portfolio CEO - 의사결정 워크플로우 가이드

**작성일**: 2026년 01월 19일
**버전**: 1.0.0
**상태**: 활성

---

## 📋 개요

PortfolioCEO 앱의 의사결정 워크플로우는 CEO가 앱에 대한 피드백을 받아 의사결정을 내리고, 자동으로 태스크로 변환하여 실행하는 전체 프로세스입니다.

### 핵심 가치

- 🤖 **AI 기반 분석**: 피드백을 분석하여 3가지 구현 옵션 자동 생성
- ⚡ **빠른 의사결정**: 앱별로 의사결정을 확인하고 즉시 승인
- 🔄 **자동화**: 승인 시 피드백 상태 업데이트, 태스크 생성 자동화
- 📊 **히스토리 관리**: 모든 의사결정 이력 추적 및 복구 가능

---

## 🔄 전체 워크플로우

```
1. 피드백 작성 (앱 상세 → 피드백 탭)
   ↓
2. AI 기획서 생성 (피드백 분석)
   ↓
3. 의사결정 옵션 추가 (decisions-queue.json)
   ↓
4. CEO 의사결정 (기획 의사결정 탭)
   ├─ 옵션 A, B, C 중 선택
   ├─ 승인 버튼 클릭
   └─ 또는 삭제/거절
   ↓
5. 자동 처리 (DecisionQueueService)
   ├─ 관련 피드백 상태 → "처리 완료"
   ├─ 선택한 옵션 기반 태스크 생성
   └─ 의사결정 히스토리에 기록
   ↓
6. 태스크 실행 (태스크 탭)
   └─ 생성된 태스크 확인 및 진행
```

---

## 📁 파일 구조

### 1. 의사결정 큐 파일
**위치**: `~/Documents/workspace/code/app-portfolio/decisions-queue.json`

**구조**:
```json
{
  "lastUpdated": "2026-01-19T...",
  "pendingDecisions": [
    {
      "id": "dec-double-reminder-001",
      "type": "feature-decision",
      "app": "두 번 알림",
      "appFolder": "double-reminder",
      "title": "다국어 지원을 추가하여 글로벌 시장에 진출할까요?",
      "description": "...",
      "relatedFeedback": ["FA7BF9A9-ADC7-466B-BAA7-445499F7DFFE"],
      "priority": "high",
      "urgency": "medium",
      "businessImpact": "...",
      "implementationOptions": [
        {
          "id": "A",
          "label": "영어만 추가 (추천)",
          "description": "...",
          "estimatedTime": "3-4일",
          "technicalDetails": [...],
          "pros": [...],
          "cons": [...]
        }
      ],
      "aiRecommendation": "A",
      "aiReasoning": "...",
      "decision": null
    }
  ],
  "completedDecisions": []
}
```

### 2. 피드백 파일
**위치**: `~/Documents/project-notes/{app-folder}.json`

**예시**: `~/Documents/project-notes/double-reminder.json`
```json
[
  {
    "id": "FA7BF9A9-ADC7-466B-BAA7-445499F7DFFE",
    "content": "다국어를 지원해야 해",
    "createdAt": "2026-01-18T16:18:07Z",
    "status": "처리 전"  // 승인 후 → "처리 완료"
  }
]
```

### 3. 앱 데이터 파일
**위치**: `~/Documents/workspace/code/app-portfolio/apps/{app-folder}.json`

**태스크 구조**:
```json
{
  "tasks": [
    {
      "id": "...",
      "title": "[영어만 추가 (추천)] 다국어 지원을 추가하여 글로벌 시장에 진출할까요?",
      "description": "**의사결정 결과**: ...",
      "status": "todo",
      "priority": "high",
      "createdAt": "2026-01-19T...",
      "decisionId": "dec-double-reminder-001",
      "selectedOption": "A"
    }
  ]
}
```

---

## 🛠️ 구현 상세

### 1. 의사결정 승인 프로세스

**파일**: `PortfolioCEO/Services/DecisionQueueService.swift`

**메서드**: `approveDecision(id: String, selectedOption: String)`

**처리 순서**:
```swift
1. pendingDecisions에서 해당 의사결정 찾기
2. decision.decision = selectedOption 설정
3. pending → completed로 이동
4. updateRelatedFeedbackStatus() 호출
   ├─ relatedFeedback 배열의 각 ID 확인
   ├─ project-notes/{app-folder}.json 파일 로드
   ├─ 해당 피드백의 status를 "처리 완료"로 변경
   └─ 파일 저장
5. createTasksFromDecision() 호출
   ├─ 선택된 옵션 찾기
   ├─ apps/{app-folder}.json 파일 로드
   ├─ 태스크 객체 생성 (제목, 설명, 구현내용, 장단점 포함)
   ├─ tasks 배열에 추가
   └─ 파일 저장
6. saveQueue() 호출 (decisions-queue.json 업데이트)
```

### 2. UI 구조

**PlanningSectionView** (각 앱의 기획 의사결정 탭)

**섹션 구성**:
1. **의사결정 대기 중** (appPendingDecisions)
   - 해당 앱의 pending 의사결정만 표시
   - 각 카드 클릭 시 확장
   - 옵션 선택 및 승인/삭제 버튼

2. **의사결정 히스토리** (appCompletedDecisions)
   - 해당 앱의 completed 의사결정만 표시
   - 선택된 옵션 및 구현 내용 표시
   - 되돌리기 버튼 (rejectDecision)

3. **기획서 목록**
   - AI 생성 마크다운 기획서
   - 옵션 파싱 및 표시

4. **기능 제안**
   - 승인/거절 가능한 제안 목록

---

## 🎯 사용 가이드

### CEO 입장에서 의사결정 하기

1. **PortfolioCEO 앱 실행**

2. **앱 선택**
   - 좌측 사이드바에서 앱 클릭
   - 또는 앱 목록에서 선택

3. **기획 의사결정 탭 이동**
   - 상단 탭에서 "기획 의사결정" (전구 아이콘) 클릭
   - "N개 대기 중" 배지 확인

4. **의사결정 카드 확인**
   - 카드 클릭하여 확장
   - 제목, 설명, 비즈니스 임팩트 확인
   - 3가지 구현 옵션 비교

5. **옵션 선택**
   - 각 옵션의 장단점 확인
   - AI 추천 이유 확인
   - 원하는 옵션 클릭 (체크마크 표시)

6. **승인**
   - "승인" 버튼 클릭
   - 자동으로:
     - 피드백 상태 "처리 완료"로 변경
     - 태스크 자동 생성
     - 히스토리에 기록

7. **태스크 확인**
   - "태스크" 탭으로 이동
   - 생성된 태스크 확인
   - 구현 내용, 장단점 상세 정보 확인

8. **히스토리 확인** (선택사항)
   - "기획 의사결정" 탭 하단의 "의사결정 히스토리" 섹션
   - 과거 결정 내용 확인
   - 필요시 되돌리기 가능

---

## 🤖 AI 기획서 생성 프로세스

### 트리거
- 피드백 작성 후
- "AI 기획서 생성" 버튼 클릭

### 생성 프로세스
1. 피드백 로드 (`loadNotes()`)
2. Claude CLI 호출
3. 마크다운 기획서 생성
   - 개요
   - 3가지 구현 방안
   - AI 추천
   - ROI 분석
4. `~/Documents/planning-documents/` 에 저장
5. 기획서 목록에 표시

### 의사결정 큐 추가
- 기획서 생성 후
- 수동으로 `decisions-queue.json` 에 추가
- 또는 스크립트 자동화

---

## 📊 데이터 흐름

```
[피드백 작성]
    ↓
project-notes/{app}.json
    ↓
[AI 분석]
    ↓
planning-documents/{app}-{title}-기획서.md
    ↓
[의사결정 추가]
    ↓
decisions-queue.json (pendingDecisions)
    ↓
[CEO 승인]
    ↓
DecisionQueueService.approveDecision()
    ├─ project-notes/{app}.json (status: "처리 완료")
    ├─ apps/{app}.json (tasks 추가)
    └─ decisions-queue.json (completedDecisions)
```

---

## 🔧 확장 가능성

### 현재 구현
- ✅ 의사결정 승인/거절/삭제
- ✅ 피드백 상태 자동 업데이트
- ✅ 태스크 자동 생성
- ✅ 의사결정 히스토리
- ✅ 앱별 필터링

### 향후 추가 가능
- [ ] 의사결정 알림 (푸시)
- [ ] 의사결정 통계 대시보드
- [ ] 태스크 자동 할당 (팀원)
- [ ] 의사결정 승인 워크플로우 (다단계)
- [ ] AI 자동 의사결정 제안 (주간)
- [ ] 의사결정 템플릿 (자주 사용하는 패턴)

---

## 🐛 트러블슈팅

### 의사결정이 표시되지 않음
1. `decisions-queue.json` 파일 존재 확인
2. 앱 이름이 정확한지 확인 (`app` 필드)
3. 로그 확인: "결정 큐 로드: N개 대기 중"
4. DecisionQueueService.loadQueue() 수동 호출

### 피드백 상태가 업데이트되지 않음
1. `relatedFeedback` 배열에 올바른 ID 확인
2. `project-notes/{app-folder}.json` 파일 존재 확인
3. 로그 확인: "N개 피드백 상태 업데이트 완료"

### 태스크가 생성되지 않음
1. `apps/{app-folder}.json` 파일 존재 확인
2. 선택한 옵션 ID 확인
3. 로그 확인: "태스크 생성 완료: ..."
4. tasks 배열이 JSON에 있는지 확인

---

## 📝 베스트 프랙티스

### 의사결정 작성 시
1. **명확한 제목**: 질문 형태로 작성
2. **3가지 옵션**: 간단, 중간, 완전한 방안
3. **AI 추천**: 가장 효율적인 옵션 명시
4. **비즈니스 임팩트**: 수치화 가능한 효과
5. **technicalDetails**: 구현 단계 명시

### CEO 의사결정 시
1. **AI 추천 확인**: 우선 AI 추천 이유 읽기
2. **장단점 비교**: 시간, 비용, 효과 비교
3. **리스크 평가**: 단점이 수용 가능한지 확인
4. **단계적 접근**: 작은 옵션부터 시작

### 태스크 생성 후
1. **즉시 확인**: 태스크 탭에서 내용 확인
2. **우선순위 조정**: 필요시 우선순위 변경
3. **담당자 할당**: 팀원이 있다면 할당
4. **마일스톤 설정**: 중요 태스크는 마일스톤 추가

---

## 🎓 학습 포인트

### 이 워크플로우에서 배운 것
1. **자동화의 가치**: 반복 작업 자동화로 시간 절약
2. **명확한 옵션**: 3가지 선택지로 의사결정 가속화
3. **추적 가능성**: 모든 의사결정 이력 보존
4. **피드백 루프**: 의사결정 → 태스크 → 실행 → 피드백

### 다른 프로젝트에 적용 가능
- 제품 로드맵 관리
- 기능 우선순위 결정
- 기술 부채 관리
- 팀 의사결정 프로세스

---

## 📚 관련 문서

- [CEO-WORKFLOW.md](./CEO-WORKFLOW.md) - 전체 CEO 워크플로우
- [QUICK-COMMANDS.md](./QUICK-COMMANDS.md) - 빠른 명령어 가이드
- [API 문서](./docs/API.md) - 서비스 API 상세

---

**작성자**: Claude Sonnet 4.5 & 이현호
**최종 업데이트**: 2026년 01월 19일
**버전**: 1.0.0
