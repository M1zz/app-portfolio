# 포트폴리오 디벨롭 현황 — 평가 기준

> `docs/portfolio-status.html` 을 만들 때 사용한 판정 규칙 문서.
> **비배포(로컬 전용)** 점검용. 기준일: 2026-07-25.

## 목적
포트폴리오에 올라간 앱들의 "디벨롭 정도"를 4가지 축 + 종합 성숙도로 점검한다.

1. 유료화 정도와 여부 (무료 / 유료 / 부분유료 / 구독)
2. 고객 피드백을 받고 **앱에서 바로 확인**할 수 있는 장치 유무
3. 앱 사용 현황(analytics) 수집 여부
4. 앱이 "잘 발달했는가"를 볼 수 있는 종합 성숙도

## 데이터 출처
- **메타데이터**: `projects/PortfolioCEO/PortfolioCEO/Data/apps/*.json`
  - `price` (유료화), `stats` (태스크 완료), `currentVersion`, `appStoreId`, `notes`(평점 캐시)
- **소스 코드 스캔**: `~/Documents/workspace/code/<repo>/**/*.swift`
  - 앱 JSON의 `localProjectPath` / `githubRepo` / `nameEn` 로 레포 폴더를 역매핑
  - **46개 중 21개만 로컬 소스가 연결됨** → 나머지 25개는 피드백/분석/리뷰 항목이 **"미확인"**

## 판정 규칙

### 1. 유료화 (`price.pricingModel` 그대로 사용)
| 값 | 표시 | 의미 |
|----|------|------|
| `free` | 무료 | 결제요소 없음 |
| `paid` | 유료 | 앱 자체 유료 구매 |
| `freemium` | 부분유료 | 무료 + 인앱결제(Pro 등) |
| `freemium-subscription` | 프리미엄+구독 | 무료 + 구독 |
| `paid+subscription` | 유료+구독 | 유료 구매 + 구독 |
| `null` | 미설정 | 가격정책 미기재 |

- **"수익모델 보유"** = 무료·미설정을 제외한 전부.
- `price.hasInAppPurchases == true` → 표에 `IAP` 칩 표시.

### 2. 피드백 장치 (소스 grep)
| 배지 | 조건 (정규식) | 의미 |
|------|------|------|
| 허브연동 | `FeedbackHub` \| `com.Ysoup.FeedbackHub` | CloudKit Public DB에 적재 → **FeedbackHubViewer(맥앱)로 앱내 확인**. 요구사항 완전충족 |
| 인앱UI | `피드백` \| `FeedbackView/Manager/Service` \| `sendFeedback` | 피드백 화면은 있으나 허브 미연동(주로 이메일 발송) |
| 없음 | 위 시그니처 미발견 | — |
| 미확인 | 로컬 소스 미연결 | 스캔 불가 |

> "받고 + 앱에서 바로 확인"까지 충족하는 건 **허브연동**뿐. 인앱UI는 받기까지만.

### 3. 사용현황 수집 (analytics, 소스 grep)
- 시그니처: `TelemetryDeck` `FirebaseAnalytics` `import Firebase` `Amplitude` `Mixpanel` `PostHog` `GoogleAnalytics` `AppsFlyer` `AnalyticsManager` `logEvent`
- 하나라도 탐지되면 **도입**, 아니면 **없음**(소스 미연결 시 미확인).

### 4. 리뷰요청 장치
- 시그니처: `SKStoreReviewController` `requestReview`

### 5. 성숙 서비스 견고성 (신규, 소스 grep — 표에 컬럼 추가)
성숙한 서비스가 갖춰야 할 "안정적 데이터 보관 / 기능 안정 보장" 관점의 점검.

| 항목 | 배지/기준 | 시그니처 |
|------|-----------|----------|
| **데이터 보관** | `클라우드` > `로컬DB` > `기본저장` 순 | 클라우드=`CloudKit·NSPersistentCloudKitContainer·iCloud·ubiquit` / 로컬DB=`CoreData·SwiftData·GRDB·Realm·SQLite` / 그 외=기본저장 |
| ┗ 백업 칩 | 백업/복원/내보내기 로직 | `백업·복원·backup·restore·export/import` |
| **테스트** | 있음/없음 | `import XCTest·import Testing·@Test·XCTAssert` 파일 존재 |
| **장애 대비** | 모니터링/없음 | `Crashlytics·Sentry·Bugsnag·FirebaseCrashlytics` |
| 보안·인증 (체크리스트) | 집계만 | `LocalAuthentication·LAContext·Keychain·SecItem·FaceID` |
| 개인정보 매니페스트 (체크리스트) | 집계만 | `PrivacyInfo.xcprivacy` 파일 |

> 이 신규 항목들은 **표/체크리스트에만 표시**하고 8축 성숙도 점수에는 아직 미반영(정보 제공용). 점수에 넣을지는 추후 결정.

**자동탐지가 어려워 수동 확인을 권장하는 항목** (HTML "추가로 점검하면 좋은 항목" 섹션):
스키마 마이그레이션 · 오프라인/동기화 충돌 처리 · 빈/에러 상태 UI · 계정·데이터 삭제 경로 · 개인정보 처리방침/약관 링크 · 접근성(VoiceOver·Dynamic Type) · CI/CD · 로그·관측성.

### 종합 발달 성숙도 (8축 가중합, 100점 만점)
| 배점 | 축 | 산정 |
|-----|----|------|
| 15 | 스토어 출시 | `appStoreId` 있으면 만점 |
| 15 | 태스크 완료율 | `stats.done / stats.totalTasks` × 15 |
| 15 | 앱스토어 평점 | `평점/5 × 15`, 리뷰 3개 미만이면 ×0.7 감점 |
| 15 | 수익모델 성숙도 | freemium/구독=15, paid=12, free=6, 미설정=0 |
| 15 | 피드백 루프 | 허브=15, 인앱UI=8, 없음=0 |
| 10 | 사용현황 수집 | 도입=10 |
| 8 | 리뷰요청 장치 | 있음=8 |
| 7 | 버전 성숙도 | 메이저≥2=7, 그 외 패치 깊이로 1~5 |

- 색: 60↑ 양호(초록) · 40–59 보통(주황) · 40↓ 초기(회색).
- **주의**: 소스 미연결 앱은 피드백·분석·리뷰 축이 0으로 계산되어 실제보다 낮게 나올 수 있음(과소평가 가능).

## 한계
- 피드백/분석/리뷰는 로컬에 클론된 21개 앱만 확실. 나머지는 소스를 받아와야 판정 가능.
- 평점은 `notes` 필드의 스토어 캐시값(수동 동기화 시점 기준)이라 최신이 아닐 수 있음.
- grep 기반이라 "코드에 존재"만 판정하며, 실제 런타임 작동/활성화 여부까지는 보장하지 않음.

## 재생성
1. 앱 JSON 집계 → 유료화/stats/버전/평점 파싱
2. 레포 매핑 후 `grep -rlIE <시그니처> <repo> --include=*.swift`
3. 8축 성숙도 계산 → 성숙도순 정렬
4. `docs/portfolio-status.html` 로 출력
