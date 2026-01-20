# 🔄 CEO 양방향 워크플로우

완전한 순환 구조: **Claude → macOS 앱 → 결정/요구사항 → Claude → ...**

---

## 🎯 완전한 워크플로우

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  1. Claude CLI                                  │
│     ./scripts/ceo-daily-briefing.sh             │
│     → JSON 생성 (briefing.json)                 │
│                                                 │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│                                                 │
│  2. macOS 앱 (자동 감지)                         │
│     파일 변경 감지 → 화면 업데이트               │
│     브리핑, 의사결정 항목 표시                    │
│                                                 │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│                                                 │
│  3. CEO 결정/요구사항 작성 (macOS 앱에서)         │
│     ✅ A/B 선택 버튼 클릭                        │
│     ✅ 메모/요구사항 입력                        │
│     ✅ 우선순위 조정                             │
│     → decisions-queue.json 저장                 │
│                                                 │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│                                                 │
│  4. Claude CLI (큐 처리)                         │
│     ./scripts/process-decisions.sh              │
│     decisions-queue.json 읽기                   │
│     → 실행 → 완료 표시                          │
│     → apps/*.json 업데이트                      │
│                                                 │
└────────────────┬────────────────────────────────┘
                 │
                 ↓ (1번으로 순환)
```

---

## 📁 새로운 데이터 구조

### 1. decisions-queue.json (결정사항 큐)

```json
{
  "lastUpdated": "2026-01-17T21:00:00Z",
  "pendingDecisions": [
    {
      "id": "dec-001",
      "timestamp": "2026-01-17T10:30:00Z",
      "type": "feature-decision",
      "appName": "세끼",
      "issue": "식단 피드백 기능 구현 방식",
      "selectedOption": "A",
      "status": "pending",
      "createdBy": "CEO",
      "notes": "빠르게 출시해서 사용자 반응 보고 싶음"
    },
    {
      "id": "dec-002",
      "timestamp": "2026-01-17T10:35:00Z",
      "type": "priority-change",
      "appName": "라포 맵",
      "action": "pause",
      "reason": "리소스를 완료 임박한 앱에 집중",
      "status": "pending"
    }
  ],
  "completedDecisions": [
    {
      "id": "dec-000",
      "completedAt": "2026-01-17T09:00:00Z",
      "result": "success",
      "executedCommand": "./scripts/ceo-decision.sh briefing approve"
    }
  ]
}
```

### 2. requests-queue.json (요구사항 큐)

```json
{
  "lastUpdated": "2026-01-17T21:00:00Z",
  "requests": [
    {
      "id": "req-001",
      "timestamp": "2026-01-17T11:00:00Z",
      "type": "new-task",
      "appName": "두 번 알림",
      "title": "위젯에 다크모드 지원 추가",
      "description": "사용자 요청이 많음. iOS 18 위젯 가이드라인 참고",
      "priority": "medium",
      "targetVersion": "1.0.6",
      "status": "pending"
    },
    {
      "id": "req-002",
      "timestamp": "2026-01-17T11:15:00Z",
      "type": "bug-report",
      "appName": "욕망의 무지개",
      "title": "공유 기능 크래시",
      "severity": "high",
      "status": "pending"
    },
    {
      "id": "req-003",
      "timestamp": "2026-01-17T14:00:00Z",
      "type": "note",
      "appName": "인생 맛집",
      "content": "다음 주에 인스타그램 광고 캠페인 시작 예정. 앱스토어 스크린샷 업데이트 필요",
      "status": "noted"
    }
  ]
}
```

### 3. ceo-feedback.json (CEO 피드백)

```json
{
  "date": "2026-01-17",
  "generalFeedback": "이번 주는 완료 임박한 앱들에 집중하자",
  "appFeedback": {
    "두 번 알림": {
      "priority": "increase",
      "note": "배포 준비 완료되면 즉시 알려줘",
      "targetDate": "2026-01-20"
    },
    "라포 맵": {
      "priority": "decrease",
      "note": "일단 보류. 다른 앱 배포 후 다시 시작",
      "action": "pause"
    }
  },
  "weeklyGoals": [
    "두 번 알림, 욕망의 무지개 배포",
    "세끼 식단 피드백 기능 개발 시작",
    "인생 맛집 마케팅 준비"
  ]
}
```

---

## 🔧 macOS 앱 업데이트

### 새로운 기능들

#### 1. 의사결정 UI

```swift
// DecisionCard.swift
struct DecisionCard: View {
    let decision: Decision
    @State private var notes = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(decision.issue)
                .font(.headline)

            // 옵션 버튼들
            HStack {
                ForEach(decision.options) { option in
                    Button(option.label) {
                        saveDecision(option: option.label)
                    }
                    .buttonStyle(.bordered)
                }
            }

            // 메모 입력
            TextField("메모 (선택사항)", text: $notes)
                .textFieldStyle(.roundedBorder)

            Button("결정 저장") {
                saveDecisionWithNotes()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
        .background(Color.blue.opacity(0.1))
        .cornerRadius(12)
    }

    func saveDecision(option: String) {
        let decision = CEODecision(
            type: "feature-decision",
            appName: decision.appName,
            issue: decision.issue,
            selectedOption: option,
            notes: notes.isEmpty ? nil : notes
        )

        DecisionQueueService.shared.addDecision(decision)
    }
}
```

#### 2. 요구사항 입력 UI

```swift
// NewRequestView.swift
struct NewRequestView: View {
    @State private var appName = ""
    @State private var requestType = "new-task"
    @State private var title = ""
    @State private var description = ""
    @State private var priority = "medium"

    var body: some View {
        Form {
            Section("앱 선택") {
                Picker("앱", selection: $appName) {
                    ForEach(apps) { app in
                        Text(app.name).tag(app.name)
                    }
                }
            }

            Section("요청 유형") {
                Picker("유형", selection: $requestType) {
                    Text("새 태스크").tag("new-task")
                    Text("버그 리포트").tag("bug-report")
                    Text("메모").tag("note")
                }
            }

            Section("내용") {
                TextField("제목", text: $title)
                TextEditor(text: $description)
                    .frame(height: 100)
            }

            Section("우선순위") {
                Picker("우선순위", selection: $priority) {
                    Text("높음").tag("high")
                    Text("중간").tag("medium")
                    Text("낮음").tag("low")
                }
            }

            Button("요청 저장") {
                saveRequest()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }

    func saveRequest() {
        let request = CEORequest(
            type: requestType,
            appName: appName,
            title: title,
            description: description,
            priority: priority
        )

        RequestQueueService.shared.addRequest(request)
    }
}
```

#### 3. 빠른 메모

```swift
// QuickNoteButton.swift
// 앱 카드마다 메모 버튼 추가
Button {
    showQuickNote = true
} label: {
    Image(systemName: "note.text.badge.plus")
}
.popover(isPresented: $showQuickNote) {
    QuickNoteView(appName: app.name)
        .frame(width: 300, height: 200)
}
```

---

## 🤖 Claude CLI 업데이트

### 새로운 스크립트들

#### 1. process-decisions.sh

```bash
#!/bin/bash
# CEO 결정사항 처리

QUEUE_FILE="decisions-queue.json"

echo "📋 결정사항 큐 처리 중..."

claude << EOF
decisions-queue.json 파일을 읽어서 pending 상태인 결정들을 처리해줘:

각 결정에 대해:
1. type에 따라 적절한 작업 실행
   - feature-decision: 선택된 옵션으로 개발 시작
   - priority-change: 우선순위 조정
   - task-update: 태스크 상태 변경

2. apps/*.json 파일 업데이트

3. 결정을 completedDecisions로 이동
   - status: "completed"
   - completedAt: 현재 시간
   - result: "success" or "failed"

4. 실행 결과를 간단히 요약

처리 후 decisions-queue.json 저장
EOF

echo "✅ 결정사항 처리 완료"
```

#### 2. process-requests.sh

```bash
#!/bin/bash
# CEO 요구사항 처리

echo "📝 요구사항 큐 처리 중..."

claude << EOF
requests-queue.json 파일을 읽어서 처리해줘:

각 요청에 대해:
1. type에 따라 처리
   - new-task: apps/*.json에 새 태스크 추가
   - bug-report: 버그 태스크로 추가, priority 높게
   - note: 해당 앱의 notes 필드에 추가

2. apps/*.json 업데이트

3. 처리된 요청은 status를 "processed"로 변경

처리 결과 요약
EOF
```

#### 3. sync-ceo-feedback.sh

```bash
#!/bin/bash
# CEO 피드백 동기화

echo "🔄 CEO 피드백 반영 중..."

claude << EOF
ceo-feedback.json을 읽어서 포트폴리오에 반영해줘:

1. generalFeedback을 다음 브리핑에 포함

2. appFeedback을 apps/*.json에 반영:
   - priority 변경
   - notes 추가
   - action (pause/resume/focus) 처리

3. weeklyGoals를 다음 주간 리포트에 포함

4. 반영 완료 후 ceo-feedback.json 아카이브
EOF
```

#### 4. ceo-process-all.sh (마스터 스크립트)

```bash
#!/bin/bash
# 모든 CEO 입력을 한 번에 처리

echo "🤖 CEO 워크플로우 전체 처리 시작..."
echo ""

# 1. 결정사항 처리
./scripts/process-decisions.sh

# 2. 요구사항 처리
./scripts/process-requests.sh

# 3. 피드백 반영
./scripts/sync-ceo-feedback.sh

# 4. 포트폴리오 요약 재생성
python3 scripts/generate-portfolio-summary.py

# 5. 다음 브리핑 준비
./scripts/ceo-daily-briefing.sh

echo ""
echo "✅ 모든 CEO 입력 처리 완료!"
echo "   macOS 앱에서 결과를 확인하세요."
```

---

## 🔄 완전한 사용 시나리오

### 시나리오 1: 아침 루틴 → 의사결정 → 실행

```
[09:00] 알림 도착
↓
[09:05] macOS 앱 열기
- 브리핑 확인
- "세끼 식단 피드백 기능 구현 방식?"
  → 옵션 A 클릭
  → 메모: "1주 안에 MVP 완성"
  → 저장

- "라포 맵 정체 중"
  → "일시 중단" 선택
  → 저장
↓
[09:10] 터미널에서 실행
$ ./scripts/ceo-process-all.sh

→ Claude가 자동으로:
  - 세끼 앱에 태스크 추가
  - 라포 맵 우선순위 낮춤
  - 포트폴리오 업데이트
↓
[09:12] macOS 앱 자동 새로고침
- 세끼: 새 태스크 "식단 피드백 MVP" 추가됨
- 라포 맵: 우선순위 → Low, 메모 추가됨
```

### 시나리오 2: 중간에 아이디어 떠오름

```
[14:30] macOS 앱에서
- "두 번 알림" 앱 카드 클릭
- 메모 버튼 (note.text.badge.plus) 클릭
- "위젯 다크모드 지원 추가하면 좋을 듯"
- 우선순위: Medium
- 저장
↓
requests-queue.json에 추가됨
↓
[저녁] ./scripts/ceo-process-all.sh 실행
→ "두 번 알림"에 새 태스크 추가
→ targetVersion: 1.0.6
```

### 시나리오 3: 주말 전략 회의

```
[일요일 저녁]
- macOS 앱에서 "주간 피드백 작성" 버튼
- 이번 주 회고 입력
- 다음 주 목표 설정:
  ✓ 두 번 알림, 욕망의 무지개 배포
  ✓ 세끼 MVP 개발 시작
  ✓ 인생 맛집 마케팅 준비
- 저장
↓
ceo-feedback.json 생성
↓
./scripts/sync-ceo-feedback.sh
→ 모든 앱의 우선순위 재조정
→ 다음 주 브리핑에 목표 포함
```

---

## 🎯 핵심 개선사항

### Before (단방향)
```
Claude → JSON → macOS 앱 (읽기만)
```

### After (양방향)
```
Claude → JSON → macOS 앱 (읽기)
                    ↓
              결정/요구사항 입력
                    ↓
              Queue JSON 저장
                    ↓
Claude ← Queue 읽기 ← 실행
```

---

## 💡 구현 우선순위

### Phase 1: 최소 기능 (1일)
- ✅ DecisionCard UI (A/B 버튼)
- ✅ decisions-queue.json 저장
- ✅ process-decisions.sh 스크립트

### Phase 2: 요구사항 (2일)
- ✅ NewRequestView UI
- ✅ requests-queue.json 저장
- ✅ process-requests.sh 스크립트

### Phase 3: 피드백 (1일)
- ✅ QuickNote 기능
- ✅ ceo-feedback.json
- ✅ sync-ceo-feedback.sh

### Phase 4: 통합 (1일)
- ✅ ceo-process-all.sh 마스터 스크립트
- ✅ 자동화 및 테스트

---

## 🚀 시작하기

```bash
# 1. 새 JSON 파일 생성
touch decisions-queue.json
touch requests-queue.json
touch ceo-feedback.json

# 2. 초기 데이터 설정
echo '{"pendingDecisions":[],"completedDecisions":[]}' > decisions-queue.json
echo '{"requests":[]}' > requests-queue.json
echo '{}' > ceo-feedback.json

# 3. 스크립트 생성
# (위의 스크립트들을 scripts/ 폴더에 생성)

# 4. macOS 앱 업데이트
# (DecisionCard, NewRequestView 등 추가)

# 5. 테스트
./scripts/ceo-process-all.sh
```

---

**이제 진정한 CEO 모드입니다!**
**명령하고, 확인하고, 결정하고, 다시 실행하는 완전한 순환!** 👔🔄