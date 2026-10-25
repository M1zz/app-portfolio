#!/usr/bin/env python3
"""앱별 서비스 숙성도(serviceMaturity)를 소스 코드와 지원 페이지에서 실측해 앱 JSON에 기록한다.

사용법:
  python3 scripts/sync-service-maturity.py             # 소스 스캔 + 지원 페이지 조회
  python3 scripts/sync-service-maturity.py --offline   # 지원 페이지 조회 생략 (이전 값 유지)

글로벌 지원(globalReach)이 '어디까지 닿나'라면, 숙성도는 '서비스로서 얼마나 갖췄나'다.
항목은 LeeoKit 의 완성도 계약(LeeoCapability)에서 앱 밖에서 확인할 수 있는 것만 골랐다.

  feedback   피드백 수집     인앱 피드백 · 메일 문의 · 인스타그램 DM · 리뷰 요청 · 리뷰 작성 바로가기
  ops        운영·안정성     사용 통계 · 크래시 진단 · 원격 킬스위치 · 자동 테스트 · LeeoKit 계약
  ux         사용 경험       위젯 · 단축어(App Intents) · iCloud 동기화 · 사용 팁(TipKit) · 온보딩
  a11y       접근성         VoiceOver 설명 · 읽는 순서·역할 · 큰 글씨 · 움직임 줄이기 · 대비·색 구분
  money      수익화         페이월 · 기능 등급 · 무료 문턱 · 구매 복원 · 할인 제안 · 후원 · 후원 부탁 · 선물
  more       더 갖출 것     마이그레이션 · 빈 상태 · 생체 잠금 · 알림 · 성능 · 로그 · 퍼널 · A/B · 햅틱 · 사전 점검 ·
                            완성도 계약 · 앱 가족 · 폴더블 · UI 테스트 · SwiftLint · CI
  comms      소통           새 기능 알림 · 로드맵 · 의견 답장
  guide      안내           단계적 공개 · 상황 맞춤 수업 · 직접 해 보는 첫 실행 · 안내 교통정리 · 배운 것 기록
  craft      다듬기         만족한 순간 세기 · 시트 다듬기 · 숫자 바뀜 효과 · 지역 맞춤 표기 · 긴 글자 처리 ·
                            입력 흐름 · 글자 복사 · 구매 흐름 시험 · 버전별 출시 기록 · 꾸준한 손질
  marketing  홍보           스토어 문구 원고 · 스크린샷 자동 촬영 · 문구 입힌 스크린샷 · 언어별 스크린샷 · 사용 영상 도구 ·
                            사용 영상 · 홍보 글 원고 (레포 파일) / 촬영용 데모 모드 · 앱 공유 · 공유 이미지 · 공유 영상 ·
                            딥링크 · 프로모션 코드 · 초대 · 설치 유도 (앱 소스)
  devices    기기           iPhone · iPad · Mac · Apple Watch · Vision Pro
  support    지원 페이지     등록 · 접속 · 개인정보 처리방침 · 영어 안내 · 문의 수단

값은 True(있음) / False(없음) / None(확인 불가: 소스를 못 찾음·페이지 조회 실패).
"안 했다"와 "모른다"를 섞지 않는다.

⚠️ 소스는 번들 ID로 찾는다 (~/Documents/workspace 아래 .xcodeproj 의 PRODUCT_BUNDLE_IDENTIFIER).
   다른 앱의 소스 폴더가 안에 들어 있으면 그 폴더는 건너뛴다.
"""
import argparse
import glob
import json
import os
import re
import ssl
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "projects/PortfolioCEO/PortfolioCEO/Data/apps")
SEARCH_ROOT = os.path.expanduser("~/Documents/workspace")
SKIP_DIRS = {"build", ".build", "DerivedData", "checkouts", "SourcePackages", "Pods",
             "node_modules", ".git", "LeeoKit"}

# ── 소스 패턴 ──
SRC = {
    "feedback": {
        "inAppFeedback": r"LeeoFeedbackView|LeeoSupportSection|struct FeedbackView\b",
        "mailContact": r"mailto:|scheme\s*=\s*\"mailto\"|MFMailComposeViewController|LeeoMailComposer",
        "instagram": r"instagram\.com/",
        "reviewPrompt": r"requestReview|SKStoreReviewController|leeoSatisfactionCheck|"
                        r"leeoReviewGate|LeeoReviewRequest",
        "writeReview": r"action=write-review|LeeoSupportSection|openWriteReview",
    },
    "ops": {
        "analytics": r"LeeoUsageAnalytics|LeeoUsageReporter|TelemetryDeck|FirebaseAnalytics|"
                     r"Analytics\.logEvent",
        "crash": r"LeeoDiagnostics|MXMetricManager|Crashlytics|SentrySDK",
        # RemoteFlagsService: 클립키보드가 LeeoRemoteFlags 이전에 만든 CloudKit 킬스위치(키보드·맥 앱과 레코드 공유)
        "killSwitch": r"LeeoRemoteFlags|RemoteFlagsService|RemoteConfig\.remoteConfig|bootstrap\([^)]*flags:",
        "leeoKit": r"^import LeeoKit",
        "crashLoop": r"LeeoCrashLoopGuard|crashLoop",
    },
    "ux": {
        "widgets": r"WidgetConfiguration|:\s*Widget\b|WidgetBundle",
        "shortcuts": r"AppShortcutsProvider|:\s*AppIntent\b|AppIntent\s*\{",
        "cloudSync": r"privateCloudDatabase|NSPersistentCloudKitContainer|"
                     r"cloudKitDatabase:\s*\.(?:private|automatic)|"
                     r"NSUbiquitousKeyValueStore|CKSyncEngine",
        "tips": r"import TipKit",
        "onboarding": r"(?:struct|class) \w*Onboarding\w*|hasSeenOnboarding|hasCompletedOnboarding",
        "backup": r"\.fileExporter\(|exportBackup|UIDocumentPickerViewController\(forExporting",
    },
    # 접근성 — App Store 접근성 정보 9개 항목(VoiceOver · 음성 제어 · 큰 텍스트 · 다크 인터페이스 · 색상 없이 구별 ·
    # 충분한 대비 · 동작 줄이기 · 자막 · 오디오 설명)에, 접근성이 좋은 앱이 더 갖추는 것을 덧붙였다.
    "a11y": {
        "voiceOver": r"\.accessibilityLabel|\.accessibilityHint|\.accessibilityValue|"
                     r"accessibilityElement",
        "voiceControl": r"accessibilityInputLabels|accessibilityUserInputLabels",
        "dynamicType": r"@ScaledMetric|\.dynamicTypeSize|UIFontMetrics|relativeTo:|"
                       r"adjustsFontForContentSizeCategory|preferredFont\(forTextStyle",
        "darkMode": r"@Environment\(\\\.colorScheme\)|colorScheme\s*==|userInterfaceStyle\s*==|"
                    r"preferredColorScheme\(\s*\.dark|\.preferredColorScheme\(\s*[a-z]",
        "differentiate": r"accessibilityDifferentiateWithoutColor|shouldDifferentiateWithoutColor",
        "contrast": r"colorSchemeContrast|isDarkerSystemColorsEnabled|accessibilityContrast",
        "reduceMotion": r"accessibilityReduceMotion|isReduceMotionEnabled",
        "captions": r"AVMediaCharacteristic\.(?:legible|describesVideoForAccessibility)|\.legible\b|"
                    r"closedCaption|AVPlayerViewController|describesVideoForAccessibility",
        "structure": r"accessibilityElement\(children|accessibilityAddTraits|accessibilitySortPriority|"
                     r"accessibilityHeading|accessibilityHidden\(true\)|accessibilityRepresentation",
        "actions": r"\.accessibilityAction|accessibilityAdjustableAction|accessibilityRotor|"
                   r"accessibilityCustomActions|accessibilityScrollAction",
        "announcements": r"AccessibilityNotification|UIAccessibility\.post\(|\.announcement\b",
        "largeLayout": r"isAccessibilitySize|isAccessibilityCategory|ViewThatFits|"
                       r"accessibilityShowsLargeContentViewer|>=\s*\.accessibility\d",
        "reduceTransparency": r"accessibilityReduceTransparency|isReduceTransparencyEnabled",
        "boldText": r"legibilityWeight|isBoldTextEnabled",
        "invertColors": r"accessibilityIgnoresInvertColors|accessibilityInvertColors",
        "keyboard": r"\.focusable\(|focusSection|keyboardShortcut\(|UIKeyCommand",
    },
    # 다듬기 — 종합 상위 앱들이 공통으로 갖췄는데 하위 앱에는 드문 것 (2026-10-17 상위 10 · 하위 20 비교)
    "craft": {
        "moments": r"LeeoEngagement|registerSignificantEvent",
        "sheets": r"presentationDragIndicator|presentationDetents",
        "liveNumbers": r"\.numericText",
        "localeFormat": r"setLocalizedDateFormatFromTemplate|\.formatted\(\.dateTime|Date\.FormatStyle|"
                        r"\.formatted\(\.number|\.currency\(code:",
        "textOverflow": r"truncationMode|allowsTightening",
        "inputFlow": r"submitLabel|scrollDismissesKeyboard",
        "textCopy": r"textSelection\(\.enabled\)",
    },
    # 수익화 — 클립키보드에서 다듬은 장치들(2026-09~10)을 다른 앱에도 같은 잣대로 본다
    "money": {
        "paywall": r"(?:struct|class) \w*Paywall\w*\s*:\s*View|LeeoPaywall",
        "tiers": r"\bcase plus\b",
        "freeGate": r"LeeoGatePolicy|FreeUsePaywall|freeUseLimit",
        "restore": r"AppStore\.sync\(|restoreCompletedTransactions|LeeoStore\b[^\n]*\.restore\(|"
                   r"\.restore\(\)|LeeoPaywallView",
        "discount": r"DiscountOffer|promotionalOffer|winBackOffer|offerCodeRedemption|presentOfferCodeRedeemSheet",
        "tipJar": r"LeeoTipJar|(?:struct|class) \w*TipJar\w*",
        "tipAsk": r"LeeoTipAsk",
        "gift": r"LeeoGift|(?:struct|class) \w*Gift\w*View",
    },
    # 소통 — 업데이트·계획·답장을 쓰는 사람에게 돌려주는 장치
    "comms": {
        "whatsNew": r"WhatsNew|whatsNew",
        "roadmap": r"LeeoRoadmap|(?:struct|class) \w*Roadmap\w*\s*:\s*View",
        # LeeoSupportSection 은 v3.15 부터 보낸 의견·답장 행(LeeoSentFeedbackRow)을 품는다
        "feedbackReply": r"LeeoFeedbackReplies|LeeoFeedbackInbox|LeeoSentFeedbackRow|LeeoSupportSection",
    },
    # 안내 — 첫 실행 '화면이 있다' 를 넘어, 무엇을 언제 어떻게 가르치나 (클립키보드 5.1.14 백지 첫 실행, 2026-10-25)
    "guide": {
        # 처음엔 단순하게 두고 기능은 필요할 때 켠다
        "progressive": r"isBlankStartUser|hasGraduated\(|FeatureSet\.(?:isOn|set)\(",
        # 쓰는 모습이 계기가 되어 그 순간 그 기능을 가르친다
        "contextualLesson": r"FeatureNudge|FeatureLessonView",
        # 보여 주기만 하지 않고 첫 실행에서 직접 눌러 보게 한다
        # (이름에 첫 실행 갈래가 든 Practice 만 센다. 언어 연습 화면 같은 Practice 는 첫 실행 안내가 아니다)
        "practice": r"(?:struct|class) \w*(?:BlankStart|Onboarding|FirstRun|Welcome)\w*Practice\w*\s*:\s*View",
        # 실행 때 저절로 뜨는 창을 하나만 골라, 서로 덮어 밀어내지 않게 한다
        "promptArbiter": r"PromptArbiter|LaunchSheetGate",
        # 무엇을 배웠는지 적어 두고 다시 가르치지 않는다
        "lessonLedger": r"LessonLedger",
    },
    # 더 갖출 것 — LeeoCapability 계약 항목 중 소스로 확인할 수 있는 것 + LeeoKit 모듈
    "more": {
        "schemaMigration": r"SchemaMigrationPlan|VersionedSchema|NSMigrationManager|MigrationStage",
        "emptyStates": r"ContentUnavailableView",
        "biometricLock": r"LAContext\(|import LocalAuthentication",
        "notifications": r"UNUserNotificationCenter|registerForRemoteNotifications",
        "performance": r"OSSignposter|os_signpost|MXMetricManager",
        "logging": r"Logger\(subsystem:|import OSLog|os\.Logger",
        "funnel": r"[Ff]unnel",
        "abTesting": r"ABTest|abTest|LeeoExperiment|abVariant",
        "haptics": r"UIImpactFeedbackGenerator|UINotificationFeedbackGenerator|\.sensoryFeedback\(|HapticManager",
        "preflight": r"LeeoPreflight",
        "appSpec": r"LeeoAppSpec",
        "family": r"LeeoFamily",
        "fold": r"LeeoFold|FoldCompanion",
    },
    # 홍보 — 앱 안의 장치. 레포의 홍보 파이프라인은 MKT_FILES, 공유 장치는 SHARE_* 로 따로 본다 (2026-10-24 앱 레포 39개 기준)
    "marketing": {
        # 스크린샷·영상 촬영 때 보기 좋은 데이터를 채우는 모드 (ScreenshotMode · DemoMode · DemoDataService · -screenshotSeed)
        "demoMode": r"\b(?:Screenshot|Demo)(?:Mode|DataService|DataSeeder|Seeder)\b|DemoData\.(?:activeKey|seed|enable)|"
                    r"arguments\.contains\(\"-(?:screenshot|demo|UITest_?Screenshots)\w*\"\)",
        "deepLink": r"\.onOpenURL\b|onContinueUserActivity|continueUserActivity|NSUserActivityTypeBrowsingWeb",
        "offerCode": r"offerCodeRedemption|presentCodeRedemptionSheet|presentOfferCodeRedeemSheet",
        "invite": r"inviteCode|inviteLink|InviteFriend|[Rr]eferral",
        # 앱 클립·다른 앱에서 본 앱을 설치하게 띄우는 배너
        "installNudge": r"SKOverlay|AppClipConfiguration",
    },
}
# 홍보 — 공유 장치는 한 파일 안에 '공유 시트'와 '공유할 것'이 함께 있어야 센다 (이미지 그리기만 하는 코드는 빼려고)
SHARE_SHEET = re.compile(r"ShareLink\(|UIActivityViewController")
SHARE_APP = re.compile(r"apps\.apple\.com/app/id|appStoreURL|\bappURL\b|shareApp")
SHARE_IMAGE = re.compile(r"\bImageRenderer\b|UIGraphicsImageRenderer\b")
SHARE_VIDEO = re.compile(r"AVAssetWriter\b")
# 홍보 — 레포에 함께 있는 홍보 파이프라인 (저장소 맨 위 기준 경로)
MKT_FILES = {
    "storeCopy": re.compile(r"(?i)(^|/)APPSTORE\.md$|(^|/)metadata/[^/]+/(description|promotional_text|keywords)\.txt$|"
                            r"appstore-metadata\.md$"),
    "screenshotCapture": re.compile(r"(?i)(^|/)[^/]*(capture|take)[^/]*\.(sh|py)$|(^|/)Snapfile$|"
                                    r"(^|/)make_(store_)?screenshots\.sh$"),
    "marketingScreens": re.compile(r"(?i)(^|/)screenshots/marketing[^/]*/.+\.(png|jpe?g)$|(^|/)make_marketing[^/]*\.py$|"
                                   r"compose_screenshots\.py$"),
    "videoAsset": re.compile(r"(?i)(^|/)(docs|marketing|appstore|screenshots|fastlane)/(.+/)?[^/]+\.(mp4|mov)$"),
    "promoKit": re.compile(r"(?i)(^|/)marketing/.+\.md$|(^|/)docs/marketing[^/]*(/.+)?\.md$|reddit[^/]*\.md$|"
                           r"marketing-kit|producthunt"),
}
# 소스 패턴(SRC["marketing"]) 밖에서 판정하는 홍보 항목
MKT_ITEMS = ("shareApp", "shareImage", "shareVideo", *MKT_FILES, "localizedScreens", "videoTool")
# 언어별 스크린샷 — 이 아래 언어 폴더에 그림이 있으면 그 언어로 친다. 3개 언어 이상이면 있음.
MKT_LOCALE_DIR = re.compile(r"(?i)(?:^|/)(?:screenshots/marketing/|screenshots/marketing-|appstore/screenshots/|"
                            r"fastlane/screenshots/)([a-z]{2}(?:[-_][A-Za-z]{2,4})?)/[^/]+\.(?:png|jpe?g)$")
MKT_LOCALES_MIN = 3
# 사용 영상 도구 — 시뮬레이터 화면 녹화, 또는 이름에 video 가 든 스크립트가 영상을 만든다 (ffmpeg 로 그림만 자르는 스크립트는 빼려고)
VIDEO_TOOL = re.compile(r"recordVideo")
VIDEO_MAKER = re.compile(r"ffmpeg|AVAssetWriter|moviepy|\.mp4")
# 파일로 판정하는 것 — 저장소 맨 위 기준 경로
RELEASE_TAGS_MIN = 3     # 버전 태그가 이만큼 있으면 출시마다 기록을 남긴다고 본다
STEADY_COMMITS_MIN = 20  # 최근 90일 커밋이 이만큼 있으면 꾸준히 손본다고 본다
REPO_FILES = {
    "swiftlint": re.compile(r"(^|/)\.swiftlint\.ya?ml$"),
    "ci": re.compile(r"^\.github/workflows/|(^|/)ci_scripts/"),
}
UI_TEST = re.compile(r"XCUIApplication")
A11Y_AUDIT = re.compile(r"performAccessibilityAudit")
VIDEO = re.compile(r"VideoPlayer\(|\bAVPlayer\b|AVPlayerLayer|AVPlayerViewController")
FORCED_LIGHT = re.compile(r"\.preferredColorScheme\(\s*\.light\s*\)")
PLIST_LIGHT = re.compile(r"UIUserInterfaceStyle\s*=\s*\"?Light|<key>UIUserInterfaceStyle</key>\s*<string>Light")
ACCESSIBILITY_MIN = 5  # VoiceOver 설명이 이 수 이상이면 '갖췄다'로 본다 (한두 개는 우연)
BOOTSTRAP = re.compile(r"LeeoKit\.bootstrap\(([^)]*)\)")


def find_projects():
    """번들 ID → (소스 루트, pbxproj 내용들)."""
    out = {}
    for dirpath, dirs, files in os.walk(SEARCH_ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.endswith(".xcodeproj")
                   and not d.startswith(".")]
        if dirpath.count(os.sep) - SEARCH_ROOT.count(os.sep) > 5:
            dirs[:] = []
        for d in os.listdir(dirpath):
            if not d.endswith(".xcodeproj"):
                continue
            pbx = os.path.join(dirpath, d, "project.pbxproj")
            try:
                text = open(pbx, errors="ignore").read()
            except OSError:
                continue
            for b in set(re.findall(r'PRODUCT_BUNDLE_IDENTIFIER = "?([^";]+)"?;', text)):
                out.setdefault(b.lower(), []).append((dirpath, text))
    return out


def swift_files(root, exclude_roots):
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")
                   and os.path.join(dirpath, d) not in exclude_roots]
        for f in files:
            if f.endswith(".swift"):
                yield os.path.join(dirpath, f)


def scan_source(root, exclude_roots):
    found = {k: {i: False for i in items} for k, items in SRC.items()}
    found["more"].update({"uiTests": False, **{k: False for k in REPO_FILES}})
    found["a11y"].update({"a11yAudit": False, "_video": False})
    found["craft"]["purchaseTest"] = False
    found["marketing"].update({k: False for k in MKT_ITEMS})
    forced_light = False
    pats = {(k, i): re.compile(p, re.M) for k, items in SRC.items() for i, p in items.items()}
    a11y = 0
    tests = 0
    crash_by_bootstrap = False
    for path in swift_files(root, exclude_roots):
        try:
            text = open(path, errors="ignore").read()
        except OSError:
            continue
        is_test = re.search(r"Tests?/|Tests?\.swift$|UITests", path) is not None
        if is_test:
            if re.search(r"XCTestCase|^\s*@Test\b|import Testing", text, re.M):
                tests += 1
            if UI_TEST.search(text):
                found["more"]["uiTests"] = True
            if A11Y_AUDIT.search(text):
                found["a11y"]["a11yAudit"] = True
            continue
        if VIDEO.search(text):
            found["a11y"]["_video"] = True
        if FORCED_LIGHT.search(text):
            forced_light = True
        # 줄 전체가 주석인 줄은 기능이 아니다 — 공유 사본에 따라온 주석 속 이름(`DiscountOfferManager`)이
        # 그 앱에 없는 기능을 있는 것으로 잡았다. 줄 끝 주석은 문자열 속 URL(https://)과 갈라낼 수 없어 둔다.
        code = COMMENT_LINE.sub("", text)
        for (k, i), p in pats.items():
            if i == "voiceOver":
                a11y += len(p.findall(code))
            elif not found[k][i] and p.search(code):
                found[k][i] = True
        mk = found["marketing"]
        if SHARE_SHEET.search(code):
            mk["shareApp"] = mk["shareApp"] or SHARE_APP.search(code) is not None
            mk["shareImage"] = mk["shareImage"] or SHARE_IMAGE.search(code) is not None
        mk["shareVideo"] = mk["shareVideo"] or SHARE_VIDEO.search(code) is not None
        for args in BOOTSTRAP.findall(text):
            if "diagnostics: false" not in args:
                crash_by_bootstrap = True
            if "flags:" in args:
                found["ops"]["killSwitch"] = True
    found["a11y"]["voiceOver"] = a11y >= ACCESSIBILITY_MIN
    scan_appearance(root, exclude_roots, found["a11y"], forced_light)
    found["ops"]["crash"] = found["ops"]["crash"] or crash_by_bootstrap
    found["ops"]["tests"] = tests > 0
    top = os.popen("git -C '%s' rev-parse --show-toplevel 2>/dev/null" % root).read().strip() or root
    locales = set()
    for dp, ds, fs in os.walk(top):
        ds[:] = [d for d in ds if d not in SKIP_DIRS and d != ".build"]
        for f in fs + ds:
            rel = os.path.relpath(os.path.join(dp, f), top)
            for k, p in REPO_FILES.items():
                if p.search(rel):
                    found["more"][k] = True
            for k, p in MKT_FILES.items():
                if p.search(rel):
                    found["marketing"][k] = True
            loc = MKT_LOCALE_DIR.search(rel)
            if loc:
                locales.add(loc.group(1).lower().replace("_", "-"))
            if f.endswith((".sh", ".py", ".rb")) and not found["marketing"]["videoTool"]:
                try:
                    t = open(os.path.join(dp, f), errors="ignore").read()
                except OSError:
                    t = ""
                found["marketing"]["videoTool"] = bool(
                    VIDEO_TOOL.search(t) or ("video" in f.lower() and VIDEO_MAKER.search(t)))
            if f.endswith(".storekit"):
                found["craft"]["purchaseTest"] = True
    found["marketing"]["localizedScreens"] = len(locales) >= MKT_LOCALES_MIN
    tags = os.popen("git -C '%s' tag 2>/dev/null" % top).read().split()
    found["craft"]["releaseTags"] = len(tags) >= RELEASE_TAGS_MIN
    recent = os.popen("git -C '%s' log --since=90.days --oneline 2>/dev/null" % top).read().splitlines()
    found["craft"]["steadyUpdates"] = len(recent) >= STEADY_COMMITS_MIN
    found["ops"]["privacyManifest"] = any(
        f == "PrivacyInfo.xcprivacy" for dp, ds, fs in os.walk(root)
        if not any(x in dp.split(os.sep) for x in SKIP_DIRS) for f in fs)
    return found, {"accessibilityLabels": a11y, "testFiles": tests}


COMMENT_LINE = re.compile(r"^[ \t]*//.*$", re.M)


def scan_appearance(root, exclude_roots, a11y, forced_light):
    """에셋 카탈로그의 어두운·고대비 모양과 Info.plist 의 밝은 모드 고정을 읽어 다크 모드·대비를 판정한다."""
    dark_asset = high_asset = False
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")
                   and os.path.join(dirpath, d) not in exclude_roots]
        for f in files:
            path = os.path.join(dirpath, f)
            if f == "Contents.json" and ".xcassets" in dirpath:
                try:
                    t = open(path, errors="ignore").read()
                except OSError:
                    continue
                dark_asset = dark_asset or re.search(r'"value"\s*:\s*"dark"', t) is not None
                high_asset = high_asset or re.search(r'"value"\s*:\s*"high"', t) is not None
            elif f.endswith((".plist", ".pbxproj")):
                try:
                    if PLIST_LIGHT.search(open(path, errors="ignore").read()):
                        forced_light = True
                except OSError:
                    pass
    # 밝은 모드로 고정하면 어두운 색을 준비해 둬도 쓰는 사람은 볼 수 없다
    a11y["darkMode"] = (a11y["darkMode"] or dark_asset) and not forced_light
    a11y["contrast"] = a11y["contrast"] or high_asset
    a11y["_forcedLight"] = forced_light


def scan_devices(pbx_texts, bundle_id):
    """번들 ID가 든 pbxproj 의 빌드 설정으로 기기를 판정한다."""
    text = "\n".join(pbx_texts)
    fam = set()
    for m in re.findall(r'TARGETED_DEVICE_FAMILY = "?([0-9,]+)"?;', text):
        fam.update(m.split(","))
    sdks = set(re.findall(r"SDKROOT = (\w+);", text))
    plats = " ".join(re.findall(r'SUPPORTED_PLATFORMS = "?([^";]+)"?;', text))
    catalyst = re.search(r"SUPPORTS_MACCATALYST = YES", text) is not None
    designed_for = re.search(r"SUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD = YES", text) is not None
    # 맥 SDK 만 쓰는 프로젝트에 남은 TARGETED_DEVICE_FAMILY 는 빌드에 쓰이지 않는다 — iOS SDK 가 있을 때만 믿는다
    ios = "iphoneos" in sdks or "iphone" in plats or (not sdks and not plats)
    return {
        "iphone": ios and ("1" in fam or "iphoneos" in plats),
        "ipad": ios and "2" in fam,
        "mac": "macosx" in sdks or "macosx" in plats or catalyst,
        "watch": "watchos" in sdks or "watchos" in plats or "4" in fam,
        "vision": "xros" in sdks or "xros" in plats or "7" in fam,
        "_macViaDesignedForIPad": designed_for and not catalyst,
    }


# ── 지원 페이지 ──
CTX = ssl.create_default_context()
HANGUL = re.compile(r"[가-힣]")
LATIN_WORD = re.compile(r"\b[A-Za-z]{3,}\b")


def fetch_page(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (portfolio-check)"})
    try:
        with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
            return r.status, r.read(600_000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return None, ""


def visible_text(html_text):
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html_text)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)


def scan_support(url):
    if not url:
        return {"registered": False, "reachable": None, "privacy": None,
                "english": None, "contact": None, "host": None}
    host = urllib.request.urlparse(url).netloc
    status, body = fetch_page(url)
    js_rendered = "notion" in host  # 노션은 본문을 스크립트로 그려 정적 HTML 로는 판정할 수 없다
    if status is None:
        return {"registered": True, "reachable": None, "privacy": None,
                "english": None, "contact": None, "host": host}
    ok = 200 <= status < 400
    text = visible_text(body)
    low = (body + text).lower()
    if not ok or js_rendered:
        verdict = None if js_rendered and ok else False
        return {"registered": True, "reachable": ok, "privacy": verdict, "english": verdict,
                "contact": verdict, "host": host, "status": status}
    english = (re.search(r'<html[^>]+lang="?en', body, re.I) is not None
               or re.search(r'data-lang="?en|lang-en|hreflang="?en', body, re.I) is not None
               or (len(LATIN_WORD.findall(text)) >= 80 and len(HANGUL.findall(text)) < 40)
               or len(LATIN_WORD.findall(text)) >= 150)
    return {
        "registered": True,
        "reachable": True,
        "privacy": bool(re.search(r"privacy|개인정보", low)),
        "english": english,
        "contact": bool(re.search(r"mailto:|@[a-z0-9-]+\.[a-z]{2,}|instagram\.com|문의|contact", low)),
        "host": host,
        "status": status,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="지원 페이지 조회 생략")
    args = ap.parse_args()

    projects = find_projects()
    apps = []
    for path in sorted(glob.glob(os.path.join(APPS, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            app = json.load(fh)
        if (app.get("lifecycle") or {}).get("stage") == 0 or not app.get("appStoreId"):
            continue
        hits = projects.get((app.get("bundleId") or "").lower(), [])
        root = min((h[0] for h in hits), key=len) if hits else None
        apps.append((path, app, root, [h[1] for h in hits]))
    roots = {r for _, _, r, _ in apps if r}

    for path, app, root, pbx in apps:
        prev = app.get("serviceMaturity") or {}
        m = {"source": bool(root)}
        if root:
            exclude = {r for r in roots if r != root and r.startswith(root + os.sep)}
            found, counts = scan_source(root, exclude)
            m.update(found)
            m["devices"] = scan_devices(pbx, app["bundleId"])
            m["counts"] = counts
        else:
            for k, items in SRC.items():
                m[k] = {i: None for i in items}
            m["ops"]["tests"] = None
            m["ops"]["privacyManifest"] = None
            m["a11y"]["a11yAudit"] = None
            m["craft"].update({"purchaseTest": None, "releaseTags": None, "steadyUpdates": None})
            m["marketing"].update({k: None for k in MKT_ITEMS})
            m["devices"] = None
        if args.offline and prev.get("support"):
            m["support"] = prev["support"]
        else:
            m["support"] = scan_support(app.get("supportUrl"))
        m["evaluatedAt"] = date.today().isoformat()
        app["serviceMaturity"] = m
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(app, fh, ensure_ascii=False, indent=2)
            fh.write("\n")

        def mark(d):
            return "".join("·" if v is None else ("●" if v else "○")
                           for k, v in (d or {}).items() if not k.startswith("_"))
        print("  %-24s 소스 %s  피드백 %s  운영 %s  경험 %s  접근성 %s  홍보 %s  기기 %s  지원 %s" % (
            os.path.basename(path)[:-5], "O" if root else "-", mark(m["feedback"]), mark(m["ops"]),
            mark(m["ux"]), mark(m["a11y"]), mark(m["marketing"]), mark(m["devices"]),
            mark({k: v for k, v in m["support"].items() if k in
                  ("registered", "reachable", "privacy", "english", "contact")})))


if __name__ == "__main__":
    main()
