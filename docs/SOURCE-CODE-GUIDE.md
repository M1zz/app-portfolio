# 🔗 소스코드 연동 가이드

## ✅ 설정 완료!

각 Claude 프로젝트가 로컬 소스코드와 연결되었습니다.

## 📊 연결된 프로젝트 (9개)

| 앱 이름 | Claude 프로젝트 | 소스코드 위치 |
|--------|----------------|--------------|
| 바미로그 | `claude-projects/bami-log` | `~/Documents/workspace/code/BamiLog` |
| 클립키보드 | `claude-projects/clip-keyboard` | `~/Documents/workspace/code/Token-memo` |
| 라포 맵 | `claude-projects/rapport-map` | `~/Documents/workspace/code/RapportMap` |
| 리바운드 저널 | `claude-projects/rebound-journal` | `~/Documents/workspace/code/Rebound-Journal` |
| 돈꼬마트 | `claude-projects/donkko-mart` | `~/Documents/workspace/code/DontGoMart` |
| 달빛 | `claude-projects/relax-on` | `~/Documents/workspace/Auto/달빛` |
| 인생 맛집 | `claude-projects/life-restaurant` | `~/Documents/workspace/code/RestaurantMap` |
| 속삭 | `claude-projects/whisper` | `~/Documents/workspace/code/Soksak` |
| 일정비서 | `claude-projects/schedule-assistant` | `~/Documents/workspace/code/ScheduleDensity` |

## 🚀 사용 방법

### 1. 기본 사용법

```bash
# 1. 프로젝트 폴더로 이동
cd claude-projects/rapport-map

# 2. Claude 실행
claude chat

# 3. 작업 지시
"현재 코드 구조 분석해줘"
"UserProfile 모델에 birthday 필드 추가해줘"
"MapView의 성능 개선해줘"
```

### 2. 작업 흐름

**분석 단계:**
```bash
cd claude-projects/rapport-map
claude chat
```

```
"현재 앱 구조 분석해줘"
→ Claude가 ~/Documents/workspace/code/RapportMap 코드 분석

"MapView.swift 파일 읽어줘"
→ 실제 소스코드 읽음

"MVVM 패턴 잘 적용되어 있는지 확인해줘"
→ 아키텍처 분석
```

**수정 단계:**
```
"MapView에 다크모드 지원 추가해줘"
→ Claude가 실제 파일 수정

"UserViewModel에 로그아웃 기능 추가해줘"
→ 실제 코드 업데이트
```

**검증 단계:**
```
"방금 수정한 내용 요약해줘"
"변경사항을 git diff로 확인해줘"
```

### 3. 실전 시나리오

#### 시나리오 A: 버그 수정

```bash
cd claude-projects/clip-keyboard
claude chat
```

```
User: "복사한 텍스트가 저장 안 되는 버그 고쳐줘"

Claude:
1. ClipboardManager.swift 분석
2. 문제 파악: UserDefaults 저장 로직 누락
3. 코드 수정
4. 변경사항 설명

→ 실제 파일이 수정됨
```

#### 시나리오 B: 새 기능 추가

```bash
cd claude-projects/rapport-map
claude chat
```

```
User: "사진에 필터 기능 추가해줘"

Claude:
1. 현재 아키텍처 확인 (architecture.md)
2. 코딩 컨벤션 확인 (conventions.md)
3. PhotoFilterService.swift 생성
4. MapView에 통합
5. 테스트 코드 작성

→ 새 파일 생성 + 기존 파일 수정
```

#### 시나리오 C: 리팩토링

```bash
cd claude-projects/rebound-journal
claude chat
```

```
User: "ViewModel 구조 개선해줘"

Claude:
1. 현재 ViewModel 구조 분석
2. MVVM 패턴 재적용
3. 코드 리팩토링
4. decisions-log.md에 결정사항 기록

→ 코드 + 문서 업데이트
```

## 🔒 안전장치

### 1. 작업 전 백업

```bash
# 수동 백업
cd ~/Documents/workspace/code/RapportMap
git add .
git commit -m "작업 전 백업"

# 또는 Time Machine 사용
```

### 2. 변경사항 확인

```bash
cd ~/Documents/workspace/code/RapportMap
git diff
git status
```

### 3. 롤백

```bash
# 마지막 커밋으로 되돌리기
git reset --hard HEAD

# 특정 파일만 되돌리기
git checkout -- MapView.swift
```

## 📝 주요 명령어 예시

### 코드 분석

```
"현재 프로젝트 구조 설명해줘"
"Models 폴더의 모든 파일 나열해줘"
"UserViewModel의 역할 설명해줘"
"의존성 관계도 그려줘"
```

### 코드 수정

```
"MapView에 줌 기능 추가해줘"
"User 모델에 profileImage 필드 추가"
"버튼 색상을 #007AFF로 변경"
"네트워킹 로직 개선해줘"
```

### 코드 생성

```
"새로운 SettingsView 만들어줘"
"NotificationService 클래스 생성"
"Unit Test 작성해줘"
```

### 문서 업데이트

```
"architecture.md 업데이트해줘"
"오늘 결정사항 decisions-log.md에 기록"
"README 작성해줘"
```

## 🎯 각 프로젝트별 특징

### 라포 맵 (rapport-map)
- **소스**: `~/Documents/workspace/code/RapportMap`
- **특징**: MapKit 기반, 사진 + 위치
- **주의**: 위치 권한 관련 코드 주의

### 클립키보드 (clip-keyboard)
- **소스**: `~/Documents/workspace/code/Token-memo`
- **특징**: Clipboard 히스토리 관리
- **주의**: 백그라운드 동작 제한

### 리바운드 저널 (rebound-journal)
- **소스**: `~/Documents/workspace/code/Rebound-Journal`
- **특징**: 일기 + 감정 분석
- **주의**: CoreData 마이그레이션

### 달빛 (relax-on)
- **소스**: `~/Documents/workspace/Auto/달빛`
- **특징**: 명상 타이머
- **주의**: 오디오 세션 관리

## 🔧 추가 프로젝트 연결

새로운 앱의 소스코드를 연결하려면:

```bash
# 1. scripts/link-source-code.sh 편집
nano scripts/link-source-code.sh

# 2. MAPPINGS 배열에 추가
"새앱폴더:$HOME/Documents/workspace/code/새앱경로"

# 3. 스크립트 실행
./scripts/link-source-code.sh
```

## 📊 작업 흐름 요약

```
1. cd claude-projects/{앱이름}
   ↓
2. claude chat
   ↓
3. 작업 지시 (분석, 수정, 생성)
   ↓
4. Claude가 실제 소스코드 수정
   ↓
5. git diff로 변경사항 확인
   ↓
6. 필요시 커밋
```

## 🎉 이제 가능한 것들

- ✅ **실제 코드 읽기**: 로컬 소스코드 분석
- ✅ **실제 코드 수정**: 파일 직접 편집
- ✅ **새 파일 생성**: 필요한 파일 추가
- ✅ **컨텍스트 유지**: 앱별 아키텍처/컨벤션 자동 적용
- ✅ **문서 동기화**: 코드 수정 시 문서도 업데이트
- ✅ **Git 통합**: 변경사항 추적 및 커밋

## ⚠️ 주의사항

1. **백업 필수**: 중요한 작업 전 반드시 git commit
2. **변경사항 확인**: 작업 후 git diff로 확인
3. **단계별 진행**: 큰 작업은 단계별로 나눠서
4. **테스트**: 수정 후 반드시 빌드 & 테스트

---

**설정 완료 시간**: 2026-01-19
**연결된 프로젝트**: 9개
**상태**: 즉시 사용 가능 ✅
