# 🎯 통합 앱 관리 워크플로우

## 개요

**현재 세션(app-portfolio)에서 모든 앱을 통합 관리**합니다.
`cd`로 폴더 이동 없이 앱 이름만 말하면 자동으로 컨텍스트 로드!

## 🔧 시스템 구조

```
app-portfolio/                    ← 현재 위치 (통합 관리)
├── app-name-mapping.json         ← 앱 이름 매핑
├── apps/                          ← 앱 데이터
│   └── *.json
├── claude-projects/               ← 앱별 컨텍스트
│   ├── shared/                    ← 공통 리소스
│   ├── double-reminder/           ← 각 앱 프로젝트
│   └── ...
└── scripts/                       ← 자동화 스크립트
```

## 🚀 사용 방법

### 기본 워크플로우

#### 1. 앱 작업 시작

```
You: "두 번 알림 업데이트해줘"

Claude:
1. app-name-mapping.json 확인 → "두 번 알림" = double-reminder
2. claude-projects/double-reminder/ 파일 읽기:
   - context.md (현재 상태, 버전, 우선순위)
   - architecture.md (앱 구조)
   - conventions.md (코딩 규칙)
   - decisions-log.md (이전 결정)
3. apps/double-reminder.json 확인 (최신 데이터)
4. 컨텍스트 파악 후 작업 시작!
```

#### 2. 앱 정보 확인

```
You: "라포 맵 현재 상태 알려줘"

Claude:
1. app-name-mapping.json → rapport-map
2. claude-projects/rapport-map/context.md 읽기
3. apps/rapport-map.json 읽기
4. 요약 제공
```

#### 3. 여러 앱 비교

```
You: "두 번 알림이랑 라포 맵 진행률 비교해줘"

Claude:
1. apps/double-reminder.json 읽기
2. apps/rapport-map.json 읽기
3. 비교 분석
```

#### 4. 공통 작업

```
You: "모든 앱에 다크모드 지원 추가 계획 세워줘"

Claude:
1. claude-projects/shared/design-system.md 읽기
2. 각 앱의 architecture.md 확인
3. 통합 계획 제시
```

## 📝 자주 쓰는 명령어

### 앱 상태 확인

```
"[앱이름] 현재 상태 알려줘"
"[앱이름] 다음 태스크 뭐야?"
"[앱이름] 최근 완료한 작업 뭐야?"
```

### 앱 업데이트

```
"[앱이름]에 [기능] 추가해줘"
"[앱이름]의 [파일] 수정해줘"
"[앱이름] [버그] 고쳐줘"
```

### 결정 사항 기록

```
"[앱이름] 결정 사항 기록: [내용]"
"[앱이름] decisions-log.md 업데이트해줘"
```

### 비교 및 분석

```
"우선순위 높은 앱들 진행률 비교해줘"
"모든 앱의 완료율 요약해줘"
"정체된 앱 찾아줘"
```

## 🎯 실전 시나리오

### 시나리오 1: 새 기능 추가

```
You: "두 번 알림에 위젯 다크모드 지원 추가해줘"

Claude의 작업:
1. ✅ app-name-mapping.json → double-reminder
2. ✅ claude-projects/double-reminder/context.md 읽기
   - 현재 버전: 1.0.5
   - 상태: active
   - 우선순위: high
3. ✅ claude-projects/double-reminder/architecture.md 읽기
   - WidgetKit 사용 확인
   - 현재 구조 파악
4. ✅ claude-projects/shared/design-system.md 읽기
   - 다크모드 컬러 팔레트
5. ✅ apps/double-reminder.json 읽기
   - 현재 태스크 확인
6. ✅ 구현 계획 제시
7. ✅ 코드 작성
8. ✅ apps/double-reminder.json 업데이트 (새 태스크 추가)
9. ✅ decisions-log.md 업데이트
```

### 시나리오 2: 버그 수정

```
You: "라포 맵에서 사진 업로드 시 크래시 나는데 고쳐줘"

Claude의 작업:
1. ✅ app-name-mapping.json → rapport-map
2. ✅ claude-projects/rapport-map/architecture.md
   - 사진 업로드 로직 확인
3. ✅ claude-projects/rapport-map/conventions.md
   - 에러 핸들링 패턴 확인
4. ✅ 버그 분석 및 수정 제안
5. ✅ 수정 코드 작성
6. ✅ decisions-log.md 업데이트
```

### 시나리오 3: 전체 앱 관리

```
You: "이번 주에 집중할 앱 3개 추천해줘"

Claude의 작업:
1. ✅ portfolio-summary.json 읽기
2. ✅ 각 앱의 apps/*.json 읽기
3. ✅ 우선순위, 진행률, 다음 태스크 분석
4. ✅ 추천 리스트 제공:
   - 두 번 알림 (71% → 80% 목표)
   - 라포 맵 (6% → 20% 목표)
   - 세끼 (새 기능 추가)
```

## 🤖 Claude의 자동 작업 흐름

```mermaid
User 입력 "두 번 알림 업데이트"
    ↓
앱 이름 인식 (app-name-mapping.json)
    ↓
프로젝트 폴더 찾기 (claude-projects/double-reminder/)
    ↓
컨텍스트 파일 읽기
- context.md (빠른 상태)
- architecture.md (구조)
- conventions.md (규칙)
- decisions-log.md (결정 사항)
    ↓
앱 데이터 확인 (apps/double-reminder.json)
    ↓
공통 리소스 참조 (shared/)
    ↓
작업 수행
    ↓
결과 반영 (JSON 업데이트, 로그 기록)
```

## 📋 앱 이름 목록 (빠른 참조)

### 우선순위 높음
- 두 번 알림 (Double Reminder)
- 라포 맵 (Rapport Map)
- 일정비서 (Schedule Assistant)

### 전체 앱 (23개)
1. 바미로그 (Bami Log)
2. 클립키보드 (Clip Keyboard)
3. 쿨타임 (Cooltime)
4. 오늘의 주접 (Daily Compliment)
5. 돈꼬마트 (Donkko Mart)
6. 두 번 알림 (Double Reminder) ⭐
7. 잘 싸워보세 (Fight Well)
8. 외국어는 언어다 (Foreign Is Language)
9. 인생 맛집 (Life Restaurant)
10. 세끼 (Three Meals)
11. 나만의 버킷 (My Bucket)
12. 픽셀 미미 (Pixel Mimi)
13. 포항 어드벤쳐 (Pohang Adventure)
14. 확률계산기 (Probability Calculator)
15. 퀴즈 (Quiz)
16. 욕망의 무지개 (Rainbow of Desire)
17. 라포 맵 (Rapport Map) ⭐
18. 리바운드 저널 (Rebound Journal)
19. 릴렉스 온 (Relax On)
20. 내마음에저장 (Save In My Heart)
21. 일정비서 (Schedule Assistant) ⭐
22. 공유일 설계자 (Shared Day Designer)
23. 속삭 (Whisper)

## 💡 팁

### 1. 앱 이름만 말하기
```
✅ "두 번 알림 업데이트해줘"
✅ "라포 맵 상태 알려줘"
❌ "double-reminder 업데이트해줘" (영문 폴더명 필요 없음)
```

### 2. 자연스러운 대화
```
✅ "두 번 알림에 새 기능 추가하고 싶은데 뭐가 좋을까?"
✅ "라포 맵이랑 세끼 중에 어떤 거 먼저 해야 할까?"
```

### 3. 컨텍스트 명시
```
✅ "두 번 알림 context.md 확인해서 현재 상태 알려줘"
✅ "라포 맵 architecture.md 업데이트해줘"
```

### 4. 일괄 작업
```
✅ "모든 앱의 진행률 요약해줘"
✅ "우선순위 높은 앱들 다음 태스크 알려줘"
```

## 🔄 워크플로우 예시

### 아침 루틴

```
You: "오늘 작업할 앱 추천해줘"

Claude:
1. portfolio-summary.json 분석
2. 우선순위 높음 + 진행 가능한 앱 추천
3. 각 앱의 다음 태스크 제시

You: "두 번 알림부터 시작할게"

Claude:
1. claude-projects/double-reminder/ 컨텍스트 로드
2. 다음 태스크 상세 설명
3. 작업 시작 준비
```

### 작업 중

```
You: "두 번 알림에 위젯 추가해줘"

Claude:
[자동으로 컨텍스트 로드하고 구현]

You: "좋아, 이제 라포 맵 볼게"

Claude:
[컨텍스트 전환하고 라포 맵 정보 제공]
```

### 저녁 정리

```
You: "오늘 작업한 거 정리해줘"

Claude:
1. 변경된 apps/*.json 확인
2. 업데이트된 decisions-log.md 확인
3. 오늘 작업 요약 제공

You: "내일 할 일 추천해줘"

Claude:
[진행 상황 기반 내일 작업 제안]
```

## 📊 현재 상태 확인

### 빠른 명령어

```
"전체 앱 현황 요약해줘"
→ portfolio-summary.json 기반 요약

"우선순위 높은 앱들 상태 알려줘"
→ high priority 앱들 진행률 제공

"정체된 앱 찾아줘"
→ 진행률 낮거나 오래된 앱 분석

"이번 주 목표 세워줘"
→ 현재 상태 기반 목표 제안
```

## 🎊 핵심 장점

### Before (프로젝트 별로 이동)
```
❌ cd claude-projects/double-reminder
❌ claude chat
❌ "업데이트해줘"
❌ exit
❌ cd ../rapport-map
❌ claude chat
```

### After (통합 관리)
```
✅ "두 번 알림 업데이트해줘"
✅ "좋아, 이제 라포 맵 볼게"
✅ "세끼도 확인해줘"
✅ (한 세션에서 모든 앱 관리!)
```

## 🚀 시작하기

**지금 바로 시작하세요:**

```
"두 번 알림 현재 상태 알려줘"
```

제가 자동으로:
1. ✅ 앱 이름 매핑 확인
2. ✅ 프로젝트 컨텍스트 로드
3. ✅ 앱 데이터 분석
4. ✅ 현재 상태 제공

**더 이상 폴더 이동 필요 없습니다!** 🎉

---

**현재 위치**: `~/Documents/workspace/code/app-portfolio`
**관리 앱 수**: 23개
**프로젝트**: 24개 (23개 앱 + 1개 공통)
**상태**: 통합 관리 준비 완료
