# 📝 앱 상세 정보 입력 가이드

## 🎯 목적

PortfolioCEO 앱에서 각 앱의 상세 정보를 입력하면, Claude가 자동으로 `claude-projects/` 문서를 생성합니다.

## 🚀 사용 방법

### 1단계: Xcode에서 새 파일 추가

새로운 기능을 위해 3개의 파일을 추가했습니다:

```bash
cd /Users/hyunholee/Documents/workspace/code/app-portfolio/PortfolioCEO
open PortfolioCEO.xcodeproj
```

Xcode에서:

1. **Models 폴더** 우클릭 → "Add Files to PortfolioCEO"
   - `PortfolioCEO/Models/AppDetailInfo.swift` 선택
   - "Copy items if needed" 체크 해제
   - "Add to targets: PortfolioCEO" 체크
   - Add 클릭

2. **Services 폴더** 우클릭 → "Add Files to PortfolioCEO"
   - `PortfolioCEO/Services/AppDetailService.swift` 선택
   - 동일하게 설정 후 Add

3. **Views 폴더** 우클릭 → "Add Files to PortfolioCEO"
   - `PortfolioCEO/Views/AppDetailFormView.swift` 선택
   - 동일하게 설정 후 Add

4. **⌘ + B** 눌러서 빌드

### 2단계: 앱 실행

```bash
# Xcode에서 실행 (⌘ + R)
# 또는 터미널에서:
cd PortfolioCEO
xcodebuild -project PortfolioCEO.xcodeproj -scheme PortfolioCEO
open build/Release/PortfolioCEO.app
```

### 3단계: 앱에서 정보 입력

1. **사이드바에서 "앱 정보 입력" 클릭**

2. **앱 선택 드롭다운**에서 입력할 앱 선택
   - 우선순위 높은 앱: 두 번 알림, 라포 맵, 일정비서 추천

3. **정보 입력:**

#### 1. 기본 정보

- **소스 코드 경로**
  ```
  예: ../DoubleReminder
  또는: 없음 (기획 단계)
  ```

- **앱 설명**
  ```
  예:
  타이머와 함께 두 번 울리는 알림을 제공하는 앱.
  예비 알림 기능으로 알림을 놓치지 않도록 돕습니다.
  ```

#### 2. 주요 기능

"추가" 버튼으로 목록 작성:
```
- 두 번 알림 (메인 + 예비)
- 타이머 기록 저장
- 워치 앱 지원
- 커스텀 사운드
```

#### 3. 기술 스택

- **UI Framework**: SwiftUI / UIKit / 혼합
- **데이터 저장**: SwiftData, Core Data, UserDefaults 등
- **플랫폼**: iOS, watchOS, macOS 체크
- **익스텐션**: 위젯, 워치 앱, 키보드 체크
- **기타 프레임워크**: CloudKit, Vision, WidgetKit 등 추가

#### 4. 제약사항 / 주의사항

```
- 알림 권한 필수
- 백그라운드 작업 사용
- 워치 연결 필요
```

#### 5. 기타 메모

자유롭게 추가 정보 작성

4. **"저장하고 Claude에게 요청하기" 버튼 클릭**

### 4단계: 저장 확인

저장되면:
- `app-details/{앱폴더}.json` 파일 생성
- Alert 표시: "저장 완료. Claude에게 다음 단계를 요청하세요."

#### 저장된 파일 확인

```bash
ls -la app-details/
cat app-details/double-reminder.json
```

예시 JSON:
```json
{
  "appFolder": "double-reminder",
  "sourcePath": "../DoubleReminder",
  "description": "타이머와 두 번 알림을 제공하는 앱",
  "mainFeatures": [
    "두 번 알림 (메인 + 예비)",
    "타이머 기록 저장",
    "워치 앱 지원"
  ],
  "techStack": {
    "ui": "SwiftUI",
    "dataStorage": "SwiftData",
    "platforms": ["iOS", "watchOS"],
    "hasWidget": true,
    "hasWatchApp": true,
    "hasKeyboard": false,
    "otherFrameworks": ["CloudKit", "WidgetKit"]
  },
  "constraints": [
    "알림 권한 필수",
    "백그라운드 작업 사용"
  ],
  "notes": "워치 앱은 iOS 앱과 데이터 동기화"
}
```

## 📊 다음 단계 (Claude에게 요청)

앱 정보를 모두 입력한 후, Claude에게 다음과 같이 요청하세요:

```
앱 상세 정보를 모두 입력했어.
app-details/ 폴더의 JSON 파일들을 읽고
claude-projects/ 문서들을 생성해줘.
```

Claude가 자동으로:

1. **`app-details/*.json` 읽기**
2. **각 앱의 claude-projects 문서 생성**:
   - `context.md`: 빠른 컨텍스트 (업데이트)
   - `architecture.md`: 아키텍처 상세 문서
   - `conventions.md`: 코딩 컨벤션
   - `decisions-log.md`: 결정 사항 로그
3. **app-name-mapping.json 업데이트** (sourcePath 추가)

## 💡 팁

### 우선순위대로 입력

1. **두 번 알림** (진행률 71%, active)
2. **라포 맵** (진행률 6%, active)
3. **일정비서** (진행률 0%, planning)

### 정보가 불확실하면

- 소스 경로 모르면: "확인 필요"
- 기획 단계면: "없음 (기획 중)"
- 기술 미정이면: "TBD" 또는 빈 칸

### 여러 앱 한번에

3개 앱 정보를 모두 입력한 후, 한번에 Claude에게 요청하면 효율적입니다.

## 🔧 트러블슈팅

### 빌드 에러

```bash
# 클린 빌드
cd PortfolioCEO
xcodebuild clean -project PortfolioCEO.xcodeproj -scheme PortfolioCEO
xcodebuild -project PortfolioCEO.xcodeproj -scheme PortfolioCEO
```

### 파일이 프로젝트에 없음

Xcode Project Navigator에서 파일이 회색으로 보이면:
1. 파일 우클릭 → Delete
2. 다시 "Add Files to PortfolioCEO"

### 앱이 실행되지 않음

```bash
# 기존 앱 종료
pkill -f PortfolioCEO

# 다시 빌드 & 실행
cd PortfolioCEO
xcodebuild && open build/Release/PortfolioCEO.app
```

## 📂 파일 구조

```
app-portfolio/
├── PortfolioCEO/               # macOS 앱
│   ├── PortfolioCEO/
│   │   ├── Models/
│   │   │   └── AppDetailInfo.swift      # ✨ 새 파일
│   │   ├── Services/
│   │   │   └── AppDetailService.swift   # ✨ 새 파일
│   │   └── Views/
│   │       └── AppDetailFormView.swift  # ✨ 새 파일
│   └── PortfolioCEO.xcodeproj
│
├── app-details/                # ✨ 생성될 폴더
│   ├── double-reminder.json
│   ├── rapport-map.json
│   └── schedule-assistant.json
│
└── claude-projects/            # Claude가 업데이트할 폴더
    ├── double-reminder/
    │   ├── context.md
    │   ├── architecture.md
    │   └── ...
    └── ...
```

## ✅ 체크리스트

우선순위 높은 3개 앱:

- [ ] **두 번 알림**
  - [ ] 소스 경로 입력
  - [ ] 앱 설명 작성
  - [ ] 주요 기능 3개 이상 추가
  - [ ] 기술 스택 입력
  - [ ] 제약사항 입력
  - [ ] 저장 완료

- [ ] **라포 맵**
  - [ ] 소스 경로 입력
  - [ ] 앱 설명 작성
  - [ ] 주요 기능 3개 이상 추가
  - [ ] 기술 스택 입력
  - [ ] 제약사항 입력
  - [ ] 저장 완료

- [ ] **일정비서**
  - [ ] 소스 경로 입력 (없으면 "없음")
  - [ ] 앱 설명 작성
  - [ ] 주요 기능 작성
  - [ ] 기술 스택 입력
  - [ ] 저장 완료

- [ ] **Claude에게 다음 단계 요청**

---

**준비 완료!** 🎉

이제 PortfolioCEO 앱을 실행해서 앱 정보를 입력하세요.
입력이 완료되면 Claude에게 "문서 생성해줘"라고 요청하면 됩니다!
