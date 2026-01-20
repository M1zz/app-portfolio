# 클립키보드 (Token Memo) - 빠른 컨텍스트

## 기본 정보

- **프로젝트명**: Token Memo (앱 이름: ClipKeyboard)
- **실제 소스 경로**: `../Token-memo/`
- **Bundle ID**: com.Ysoup.TokenMemo
- **현재 버전**: 3.0.1
- **상태**: active
- **우선순위**: medium (다국어 지원 완료, 안정화 단계)
- **최소 지원**: iOS 17+
- **플랫폼**: iOS, macOS (Mac Catalyst)

## 핵심 기능

1. **스마트 클립보드 히스토리**: 15가지 타입 자동 분류 (이메일, 전화번호, 주소, URL, 카드번호 등)
2. **메모 관리**: 텍스트/이미지 메모, 템플릿 시스템 (플레이스홀더 지원)
3. **커스텀 키보드 (TokenKeyboard)**: iOS 키보드 익스텐션으로 메모 빠르게 입력
4. **macOS 메뉴바 앱**: Mac Catalyst 기반, 전역 단축키 지원
5. **Combo 시스템**: 여러 메모를 순서대로 자동 입력
6. **CloudKit 백업**: iCloud 동기화, 이미지 포함
7. **OCR 지원**: Vision Framework로 텍스트 인식 (한국어 + 영어)

## 현재 진행 상황

<!-- apps/clip-keyboard.json 참조 -->

### 다음 태스크
- [ ] Phase 2 Combo 시스템 고도화
- [ ] 클립보드 분류 정확도 개선
- [ ] macOS 전용 기능 추가

### 최근 완료
- [x] 다국어 지원 (v3.0.1)
- [x] 스마트 클립보드 자동 분류
- [x] Mac Catalyst 앱 출시

## 주요 기술

- **UI**: SwiftUI
- **아키텍처**: Manager/Service 패턴 (MVVM 유사)
- **데이터**: JSONEncoder/Decoder + App Group
- **App Group**: `group.com.Ysoup.TokenMemo`
- **동기화**: CloudKit
- **OCR**: Vision Framework
- **인증**: LocalAuthentication (생체인증)

## 알아야 할 것

### 제약사항
- iOS 17+ 전용 (최신 SwiftUI 기능 사용)
- App Group 필수 (키보드 익스텐션과 데이터 공유)
- 클립보드 히스토리 최대 100개 유지
- 임시 항목은 7일 후 자동 삭제

### 특이사항
- **다국어 지원 필수**: 모든 UI 텍스트는 NSLocalizedString 사용
- **클립보드 분류 우선순위**: 구체적인 패턴 먼저 (주민번호 → 사업자번호 → 카드번호 → 계좌번호)
- **App Group 공유**: 메인 앱 ↔ 키보드 ↔ macOS 앱 데이터 실시간 공유

### 주의사항
- App Group 경로 반드시 사용 (표준 Documents 폴더 X)
- 이미지는 1024px 제한, JPEG 0.7 압축
- Mac Catalyst 조건부 컴파일 필수
- 하위 호환성 유지 (데이터 마이그레이션)

## 빠른 참조

### 주요 파일
- `Token memo/Token_memoApp.swift`: 앱 진입점
- `Model/Memo.swift`: 메모, 클립보드, Combo 모델
- `Service/MemoStore.swift`: 메모/클립보드 저장소 (싱글톤)
- `Service/CloudKitBackupService.swift`: iCloud 백업
- `Service/ComboExecutionService.swift`: Combo 실행
- `Manager/DataManager.swift`: 전역 데이터 관리
- `TokenKeyboard/KeyboardViewController.swift`: 키보드 익스텐션

### 자주 하는 작업
```swift
// App Group 컨테이너 접근
guard let containerURL = FileManager.default.containerURL(
    forSecurityApplicationGroupIdentifier: "group.com.Ysoup.TokenMemo"
) else { return }

// App Group UserDefaults
UserDefaults(suiteName: "group.com.Ysoup.TokenMemo")

// 다국어 문자열
Text(NSLocalizedString("Add Memo", comment: "Button to add a new memo"))

// MemoStore 사용
MemoStore.shared.memos
```

## 배포 정보

- **App Store**: 출시 완료
- **버전**: 3.0.1 (다국어 지원)
- **최근 배포**: 2025년
- **노션 튜토리얼**: https://leeo75.notion.site/ClipKeyboard-tutorial-70624fccc524465f99289c89bd0261a4

---

**마지막 업데이트**: 2026-01-18
**문서 출처**: ../Token-memo/CLAUDE.md

## 소스코드 위치

`/Users/hyunholee/Documents/workspace/code/Token-memo`

**주의**: 이 경로의 실제 코드를 수정합니다. 작업 전 백업 권장.
