# 🎬 빠른 예제: 실제 코드 수정하기

## 시나리오: 라포 맵에 새 기능 추가

### 1. 프로젝트로 이동

```bash
cd ~/Documents/workspace/code/app-portfolio
cd claude-projects/rapport-map
```

### 2. Claude 실행

```bash
claude chat
```

### 3. 현재 상태 확인

```
User: "현재 앱 구조 분석해줘"

Claude:
- architecture.md 확인
- 실제 소스코드 스캔 (~/Documents/workspace/code/RapportMap)
- 주요 파일 구조 분석
- 현재 사용 중인 기술 스택 확인

→ 분석 결과 제공
```

### 4. 코드 읽기

```
User: "MapView.swift 파일 읽어줘"

Claude:
- ~/Documents/workspace/code/RapportMap/Sources/Views/MapView.swift 읽음
- 코드 구조 설명
- 주요 기능 요약

→ 코드 내용 표시
```

### 5. 기능 추가

```
User: "지도에 검색 기능 추가해줘"

Claude:
1. 현재 아키텍처 확인 (MVVM 패턴)
2. conventions.md의 네이밍 규칙 확인
3. SearchViewModel.swift 생성
4. MapView.swift에 검색 UI 추가
5. 변경사항 요약

→ 실제 파일들이 수정됨!
```

### 6. 변경사항 확인

```bash
cd ~/Documents/workspace/code/RapportMap
git status
git diff
```

출력 예시:
```diff
modified:   Sources/Views/MapView.swift
new file:   Sources/ViewModels/SearchViewModel.swift

+ import SwiftUI
+ 
+ struct SearchBar: View {
+     @Binding var searchText: String
+     
+     var body: some View {
+         HStack {
+             TextField("검색...", text: $searchText)
+         }
+     }
+ }
```

### 7. 결정사항 기록

```
User: "오늘 결정사항 decisions-log.md에 기록해줘"

Claude:
- decisions-log.md에 추가:
  - 날짜: 2026-01-19
  - 결정: 검색 기능 추가
  - 이유: 사용자 요청
  - 구현: SearchViewModel + SearchBar

→ 문서 자동 업데이트
```

### 8. 커밋

```bash
cd ~/Documents/workspace/code/RapportMap
git add .
git commit -m "feat: 지도 검색 기능 추가

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

## 전체 흐름 요약

```
📍 위치 이동
   ↓
🤖 Claude 실행
   ↓
📊 상태 분석
   ↓
📝 코드 읽기
   ↓
✏️ 기능 추가 (실제 파일 수정!)
   ↓
✅ 변경사항 확인
   ↓
📚 문서 업데이트
   ↓
💾 커밋
```

## 다른 예제들

### 예제 A: 버그 수정

```bash
cd claude-projects/clip-keyboard
claude chat
"클립보드 저장 버그 고쳐줘"
→ Token-memo 소스코드 수정
```

### 예제 B: 리팩토링

```bash
cd claude-projects/rebound-journal
claude chat
"ViewModel 구조 개선해줘"
→ Rebound-Journal 소스코드 리팩토링
```

### 예제 C: 새 화면 추가

```bash
cd claude-projects/relax-on
claude chat
"설정 화면 만들어줘"
→ RelaxOn에 SettingsView.swift 추가
```

## 작동 원리

```
claude-projects/rapport-map/
├── .claude-project
│   └── "sourcePath": "~/Documents/workspace/code/RapportMap"
│
└── claude chat 실행
    ↓
    Claude가 자동으로:
    1. architecture.md 로드
    2. conventions.md 로드
    3. sourcePath의 실제 코드 접근
    4. 지시사항 실행
    5. 실제 파일 수정/생성
```

## 핵심 요점

- ✅ **실제 코드 수정**: 시뮬레이션이 아닌 진짜 파일 편집
- ✅ **컨텍스트 유지**: 앱별 아키텍처/컨벤션 자동 적용
- ✅ **문서 동기화**: 코드 변경 시 문서도 함께 업데이트
- ✅ **Git 통합**: 변경사항 추적 가능

---

**더 자세한 내용**: [SOURCE-CODE-GUIDE.md](SOURCE-CODE-GUIDE.md)
