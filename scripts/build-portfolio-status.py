#!/usr/bin/env python3
"""포트폴리오 디벨롭 현황 페이지 재생성.

  python3 scripts/build-portfolio-status.py            # 라이브 App Store 조회 후 재생성
  python3 scripts/build-portfolio-status.py --cached    # 캐시된 스토어 응답 재사용

출력:
  reports/portfolio-status.html    전체 분석 리포트 (KPI·앱별 표·8영역 체크리스트·인사이트)
  reports/portfolio-explorer.html  앱별 완성도 탐색기 (DATA 블록만 교체)

주의: 이 리포트는 내부 평가(앱별 약점·수익모델·우선순위)라 공개하지 않는다.
`docs/` 는 GitHub Pages 로 전량 공개되므로 절대 그쪽에 두지 말 것 — 그래서 `reports/` 에 둔다.

데이터 소스
  1) projects/PortfolioCEO/PortfolioCEO/Data/apps/*.json  — 유료화·태스크·지원페이지
  2) 로컬 소스 스캔 — ~/Documents/workspace/{code,Auto} 의 레포를 bundleId로 역매핑
  3) iTunes Lookup API — 버전·평점·가격 (artistId 1502508537)

판정 규칙은 reports/portfolio-status-criteria.md 와 일치해야 한다.
이 저장소는 public 이므로 reports/ 는 .gitignore 로 추적에서 제외한다.
"""
import argparse, glob, html, json, os, re, subprocess, sys, unicodedata, urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.path.join(ROOT, "projects/PortfolioCEO/PortfolioCEO/Data/apps")
REPORTS = os.path.join(ROOT, "reports")  # 비공개 — docs/ 는 Pages 로 공개되므로 쓰지 않는다
CACHE = os.path.join(ROOT, ".cache/appstore-lookup.json")
ARTIST_ID = "1502508537"
WS_ROOTS = [os.path.expanduser("~/Documents/workspace/code"), os.path.expanduser("~/Documents/workspace/Auto")]
SKIP_DIRS = ("/.build/", "/DerivedData/", "/SourcePackages/", "/Pods/", "/.git/", "/build/")

# ── 코드(주석 제거 후)에서 찾는 시그니처 ────────────────────────────────
CODE_SIGS = {
    "feedbackHubCode": r"iCloud\.com\.Ysoup\.FeedbackHub|FeedbackHubClient|FeedbackHubService",
    "feedbackSoft": r"FeedbackView|FeedbackManager|FeedbackService|sendFeedback|피드백",
    "analytics3rd": (r"import TelemetryDeck|TelemetryDeck\.|import FirebaseAnalytics|Analytics\.logEvent|"
                     r"import Amplitude|Amplitude\.|import Mixpanel|Mixpanel\.|import PostHog|PostHog|"
                     r"import AppsFlyer|AppsFlyerLib|GoogleAnalytics"),
    "analyticsLocal": r"AnalyticsManager|AnalyticsService|AnalyticsLogger|EventLogger",
    "reviewPrompt": r"SKStoreReviewController|requestReview|AppStore\.requestReview",
    "cloudCode": r"CloudKit|NSPersistentCloudKitContainer|NSUbiquitousKeyValueStore|ubiquityIdentityToken|CKContainer",
    "localdb": r"import CoreData|import SwiftData|@Model\b|import GRDB|import RealmSwift|sqlite3_open|import SQLite",
    "server": r"import FirebaseFirestore|import FirebaseDatabase|Firestore\.|Database\.database\(|import Supabase|import Amplify",
    "backup": r"백업|복원|exportData|importData|restoreFrom|backupTo|\.fileExporter|\.fileImporter",
    "testsCode": r"import XCTest|import Testing|@Test\b|XCTAssert|#expect\(",
    "crash": r"import FirebaseCrashlytics|Crashlytics\.|import Sentry|SentrySDK|import Bugsnag|Bugsnag\.",
    "security": r"import LocalAuthentication|LAContext|kSecClass|SecItemAdd|SecItemCopyMatching|\.biometry",
    "i18nCode": r"NSLocalizedString|LocalizedStringKey|String\(localized:",
    "darkmode": r"preferredColorScheme|@Environment\(\\.colorScheme|colorScheme ==",
    "a11y": (r"accessibilityLabel|accessibilityHint|accessibilityIdentifier|accessibilityValue|"
             r"dynamicTypeSize|accessibilityAddTraits"),
    "onboarding": r"Onboarding|WelcomeView|IntroView|튜토리얼|권한 안내",
    "widget": r"import WidgetKit|TimelineProvider|StaticConfiguration|AppIntentConfiguration",
    "receipt": r"Transaction\.currentEntitlements|Transaction\.updates|AppTransaction|VerificationResult|verifyReceipt",
    "retry": r"maxRetries|retryCount|exponentialBackoff|retry\(|withRetry|재시도",
    "emptyState": r"ContentUnavailableView|EmptyStateView|emptyState|EmptyPlaceholder",
    "push": r"UNUserNotificationCenter|UNMutableNotificationContent|registerForRemoteNotifications|UNAuthorizationOptions",
}
M_KEYS = ["cloud", "server", "localdb", "backup", "tests", "crash", "security", "privacyManifest", "i18n",
          "darkmode", "a11y", "onboarding", "widget", "receipt", "retry", "emptyState", "push",
          "swiftlint", "ci"]
MODEL_KR = {"free": "무료", "paid": "유료", "freemium": "부분유료",
            "freemium-subscription": "프리미엄+구독", "paid+subscription": "유료+구독", None: "미설정"}
MODEL_CLS = {"free": "m-free-b", "paid": "m-paid-b", "freemium": "m-freemium-b",
             "freemium-subscription": "m-sub-b", "paid+subscription": "m-sub-b", None: "m-none-b"}
MODEL_SEG = {"free": "m-free", "paid": "m-paid", "freemium": "m-freemium",
             "freemium-subscription": "m-sub", "paid+subscription": "m-sub", None: "m-none"}

_INDEX = {"bundle": {}, "remote": {}, "name": {}}


# ── 레포 역매핑 ──────────────────────────────────────────────────────
def _norm(s):
    return unicodedata.normalize("NFC", (s or "")).lower().replace("-", "").replace("_", "").replace(" ", "")


def build_index():
    for root in WS_ROOTS:
        if not os.path.isdir(root):
            continue
        for d in sorted(os.listdir(root)):
            p = os.path.join(root, d)
            if not os.path.isdir(p):
                continue
            _INDEX["name"].setdefault(_norm(d), p)
            for pb in glob.glob(os.path.join(p, "**/*.xcodeproj/project.pbxproj"), recursive=True)[:8]:
                try:
                    txt = open(pb, errors="ignore").read()
                except OSError:
                    continue
                for bid in re.findall(r"PRODUCT_BUNDLE_IDENTIFIER = ([^;]+);", txt):
                    _INDEX["bundle"].setdefault(bid.strip().strip('"').lower(), p)
            cfg = os.path.join(p, ".git/config")
            if os.path.exists(cfg):
                for url in re.findall(r"url = (\S+)", open(cfg, errors="ignore").read()):
                    _INDEX["remote"].setdefault(_norm(url.rstrip("/").removesuffix(".git").split("/")[-1]), p)


def repo_path(app):
    """bundleId → git remote → 폴더명 → localProjectPath 순으로 로컬 레포를 찾는다."""
    bid = (app.get("bundleId") or "").lower()
    if bid and bid in _INDEX["bundle"]:
        return _INDEX["bundle"][bid]
    gh = app.get("githubRepo") or ""
    if gh:
        key = _norm(gh.rstrip("/").removesuffix(".git").split("/")[-1])
        for src in ("remote", "name"):
            if key in _INDEX[src]:
                return _INDEX[src][key]
    for k in ("nameEn", "name", "folderId"):
        key = _norm(app.get(k))
        if key and key in _INDEX["name"]:
            return _INDEX["name"][key]
    lp = app.get("localProjectPath")
    if lp:
        p = os.path.normpath(os.path.join(ROOT, lp))
        if os.path.isdir(p):
            return p
    return None


# ── 소스 스캔 ────────────────────────────────────────────────────────
def strip_comments(src):
    """주석을 제거한다 — Spec/문서 파일의 설명문이 기능으로 오판되는 것을 막는다."""
    return re.sub(r"//[^\n]*", " ", re.sub(r"/\*.*?\*/", " ", src, flags=re.S))


def _files(repo, pattern):
    return [f for f in glob.glob(os.path.join(repo, pattern), recursive=True)
            if not any(s in f for s in SKIP_DIRS)]


def scan(repo):
    files = _files(repo, "**/*.swift")
    code = strip_comments("\n".join(open(f, errors="ignore").read() for f in files))
    r = {k: bool(re.search(p, code)) for k, p in CODE_SIGS.items()}
    ents = " ".join(open(f, errors="ignore").read() for f in _files(repo, "**/*.entitlements"))
    r["feedbackHub"] = r.pop("feedbackHubCode") or ("FeedbackHub" in ents)
    r["cloud"] = r.pop("cloudCode") or ("iCloud" in ents or "CloudKit" in ents)
    r["tests"] = r.pop("testsCode") or any(re.search(r"Tests?/", f) for f in files)
    r["i18n"] = r.pop("i18nCode") or bool(_files(repo, "**/*.lproj/*.strings") or _files(repo, "**/*.xcstrings"))
    r["swiftlint"] = bool(_files(repo, "**/.swiftlint.yml")) or os.path.exists(os.path.join(repo, ".swiftlint.yml"))
    r["ci"] = os.path.isdir(os.path.join(repo, ".github/workflows"))
    r["privacyManifest"] = bool(_files(repo, "**/PrivacyInfo.xcprivacy"))
    # 분석은 외부 SDK 실사용만 '도입' — no-op/로컬 래퍼는 따로 표시한다
    r["analytics"] = r["analytics3rd"]
    r["analyticsLocalOnly"] = (not r["analytics3rd"]) and r["analyticsLocal"]
    r["swiftFiles"] = len(files)
    return r


# ── App Store ───────────────────────────────────────────────────────
def fetch_store(cached=False):
    if cached and os.path.exists(CACHE):
        return json.load(open(CACHE))
    url = ("https://itunes.apple.com/lookup?id=%s&entity=software,macSoftware&country=kr&limit=200" % ARTIST_ID)
    with urllib.request.urlopen(url, timeout=30) as resp:
        results = [x for x in json.load(resp)["results"] if x.get("wrapperType") == "software"]
    idx = {str(x["trackId"]): x for x in results}
    # KR 미판매 앱은 다른 스토어에서 개별 확인 (스토어 등록 자체는 살아있음)
    known = {d.get("appStoreId") for d in load_apps() if d.get("appStoreId")}
    for sid in sorted(known - set(idx)):
        for country in ("us", "jp"):
            try:
                with urllib.request.urlopen(
                        "https://itunes.apple.com/lookup?id=%s&country=%s" % (sid, country), timeout=20) as r2:
                    res = json.load(r2)["results"]
            except OSError:
                continue
            if res:
                res[0]["_kr"] = False
                idx[str(sid)] = res[0]
                break
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(idx, open(CACHE, "w"), ensure_ascii=False)
    return idx


def load_apps():
    return [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(APPS_DIR, "*.json")))]


# ── 성숙도 ──────────────────────────────────────────────────────────
def version_score(ver):
    """메이저≥2 → 7, 패치 0 → 1, 1~2 → 3, 3+ → 5."""
    n = [int(x) for x in re.findall(r"\d+", ver or "")]
    if not n:
        return 0
    if n[0] >= 2:
        return 7
    patch = n[2] if len(n) > 2 else 0
    return 1 if patch == 0 else (3 if patch <= 2 else 5)


def model_score(m):
    return {"freemium": 15, "freemium-subscription": 15, "paid+subscription": 15,
            "subscription": 15, "paid": 12, "free": 6}.get(m, 0)


def collect(cached=False):
    build_index()
    store = fetch_store(cached)
    out = []
    for d in load_apps():
        price, stats = d.get("price") or {}, d.get("stats") or {}
        sid = d.get("appStoreId")
        s = store.get(str(sid)) if sid else None
        repo = repo_path(d)
        fl = scan(repo) if repo else {}
        ver = (s or {}).get("version") or d.get("currentVersion") or ""
        rating = round(s["averageUserRating"], 1) if s and s.get("userRatingCount") else None
        rcount = (s or {}).get("userRatingCount") or None
        done, total = stats.get("done", 0), stats.get("totalTasks", 0)
        model = price.get("pricingModel")
        parts = {
            "출시": 15 if sid else 0,
            "완료율": round(done / total * 15) if total else 0,
            "평점": round(rating / 5 * 15 * (0.7 if (rcount or 0) < 3 else 1)) if rating else 0,
            "수익화": model_score(model),
            "피드백": 15 if fl.get("feedbackHub") else (8 if fl.get("feedbackSoft") else 0),
            "분석": 10 if fl.get("analytics") else 0,
            "리뷰요청": 8 if fl.get("reviewPrompt") else 0,
            "버전": version_score(ver),
        }
        out.append({
            "name": d.get("name"), "nameEn": d.get("nameEn") or "", "ver": ver,
            "verJson": d.get("currentVersion") or "", "status": d.get("status"), "priority": d.get("priority"),
            "model": model, "iap": bool(price.get("hasInAppPurchases")),
            "iapItems": ["%s/%s" % (i.get("name"), i.get("price")) for i in price.get("iapItems") or []],
            "rating": rating, "ratingCount": rcount,
            "stats": {"done": done, "inProgress": stats.get("inProgress", 0), "todo": stats.get("todo", 0),
                      "notStarted": stats.get("notStarted", 0), "totalTasks": total},
            "maturity": sum(parts.values()), "parts": parts,
            "feedbackHub": fl.get("feedbackHub", False), "feedbackSoft": fl.get("feedbackSoft", False),
            "analytics": fl.get("analytics", False), "analyticsLocalOnly": fl.get("analyticsLocalOnly", False),
            "reviewPrompt": fl.get("reviewPrompt", False),
            "repoFound": repo is not None, "scanned": repo is not None,
            "repo": (repo or "").replace(os.path.expanduser("~"), "~"), "swiftFiles": fl.get("swiftFiles", 0),
            "appStoreId": sid or "", "tagline": (d.get("vision") or {}).get("tagline") or "",
            "supportUrl": d.get("supportUrl") or "", "appStoreUrl": d.get("appStoreUrl") or "",
            "targetUsers": (d.get("vision") or {}).get("targetUsers") or "", "minOS": d.get("minimumOS") or "",
            "storePrice": (s or {}).get("formattedPrice"), "onStore": bool(s),
            "storeRelease": (s or {}).get("currentVersionReleaseDate", "")[:10] if s else "",
            "storeKR": bool(s) and s.get("_kr", True),
            "m": {k: fl.get(k, False) for k in M_KEYS},
        })
    out.sort(key=lambda a: (-a["maturity"], a["name"]))
    return out


# ── 렌더링 헬퍼 ──────────────────────────────────────────────────────
def cnt(apps, pred):
    return sum(1 for a in apps if pred(a))


def cov(n, total):
    pct = (n / total * 100) if total else 0
    cls = "cok" if pct >= 60 else ("cmid" if pct >= 35 else "clo")
    return '<span class="cov %s">%d/%d</span>' % (cls, n, total)


def badge(kind, text, title=""):
    t = ' title="%s"' % html.escape(title) if title else ""
    return '<span class="b b-%s"%s>%s</span>' % (kind, t, text)


def esc(s):
    return html.escape(s or "", quote=True)


def status_rows(apps):
    rows = []
    for a in apps:
        sc = a["scanned"]
        # 피드백
        if not sc:
            fb = badge("unk", "미확인")
        elif a["feedbackHub"]:
            fb = badge("ok", "허브연동", "FeedbackHub CloudKit 컨테이너 연동")
        elif a["feedbackSoft"]:
            fb = badge("mid", "인앱UI")
        else:
            fb = badge("no", "없음")
        # 사용수집
        if not sc:
            an = badge("unk", "미확인")
        elif a["analytics"]:
            an = badge("ok", "도입")
        elif a["analyticsLocalOnly"]:
            an = badge("mid", "로컬만", "이벤트 래퍼는 있으나 외부로 전송하지 않음(콘솔·no-op)")
        else:
            an = badge("no", "없음")
        rv = badge("unk", "미확인") if not sc else (badge("ok", "있음") if a["reviewPrompt"] else badge("no", "없음"))
        # 데이터 보관
        if not sc:
            store_cell = badge("unk", "미확인")
        elif a["m"]["cloud"]:
            store_cell = badge("ok", "클라우드")
        elif a["m"]["server"]:
            store_cell = badge("ok", "서버DB", "Firebase·Supabase 등 원격 백엔드에 보관")
        elif a["m"]["localdb"]:
            store_cell = badge("mid", "로컬DB")
        else:
            store_cell = badge("no", "기본저장")
        if sc and a["m"]["backup"]:
            store_cell += '<span class="chip ok" title="백업/복원/내보내기">백업</span>'
        ts = badge("unk", "미확인") if not sc else (badge("ok", "있음") if a["m"]["tests"] else badge("no", "없음"))
        cr = badge("unk", "미확인") if not sc else (badge("ok", "모니터링") if a["m"]["crash"] else badge("no", "없음"))
        rating = ('<span class="star">★ %s</span><span class="muted"> (%d)</span>' % (a["rating"], a["ratingCount"])
                  if a["rating"] else '<span class="muted">—</span>')
        chips = ""
        if not a["repoFound"]:
            chips += '<span class="chip warn" title="로컬 소스 미연결">소스없음</span>'
        if a["appStoreId"] and not a["storeKR"]:
            chips += '<span class="chip warn" title="한국 스토어에서 조회되지 않음 — 판매 국가 확인 필요">KR미판매</span>'
        if not a["appStoreId"]:
            chips += '<span class="chip" title="App Store 미등록">미출시</span>'
        m = a["maturity"]
        mt = "mt-hi" if m >= 60 else ("mt-mid" if m >= 40 else "mt-lo")
        iap = '<span class="chip">IAP</span>' if a["iap"] else ""
        rows.append(
            '<tr><td class="name"><b>%s</b><span class="en">%s %s</span></td>'
            '<td class="ctr">%s</td>'
            '<td class="ctr"><span class="b %s">%s</span>%s</td>'
            '<td class="ctr">%s</td><td class="ctr">%d/%d</td>'
            '<td class="ctr">%s</td><td class="ctr">%s</td><td class="ctr">%s</td>'
            '<td class="ctr grp">%s</td><td class="ctr">%s</td><td class="ctr">%s</td>'
            '<td class="mtd"><div class="mat"><div class="mat-fill %s" style="width:%d%%"></div>'
            '<span class="mat-num">%d</span></div></td></tr>' % (
                esc(a["name"]), esc(a["nameEn"]), chips, esc(a["ver"] or "—"),
                MODEL_CLS[a["model"]], MODEL_KR[a["model"]], iap, rating,
                a["stats"]["done"], a["stats"]["totalTasks"], fb, an, rv,
                store_cell, ts, cr, mt, m, m))
    return "\n    ".join(rows)


def monetization(apps):
    order = ["free", "paid", "freemium", "freemium-subscription", "paid+subscription", None]
    counts = [(m, cnt(apps, lambda a, m=m: a["model"] == m)) for m in order]
    counts = [(m, c) for m, c in counts if c]
    segs = "".join('<div class="seg %s" style="flex:%d" title="%s %d"><span>%d</span></div>'
                   % (MODEL_SEG[m], c, MODEL_KR[m], c, c) for m, c in counts)
    legend = "".join('<span class="lg"><i class="dot %s"></i>%s <b>%d</b></span>'
                     % (MODEL_SEG[m], MODEL_KR[m], c) for m, c in counts)
    rev = cnt(apps, lambda a: a["model"] not in (None, "free"))
    return segs, legend, rev


CATEGORIES = [
    ("🗄️", "데이터 안정성", [
        ("m", "cloud", "클라우드 동기화", "기기 분실·교체에도 보존"),
        ("m", "backup", "백업·복원/내보내기", "사용자가 직접 데이터 이관"),
        ("m", "localdb", "구조적 로컬 DB", "CoreData·SwiftData"),
        ("man", None, "스키마 마이그레이션", "업데이트 시 기존 데이터 무손실 이전"),
        ("man", None, "동기화 충돌 처리", "다기기 동시수정·오프라인 병합"),
        ("man", None, "트랜잭션 원자성", "부분 저장·중간 실패 방지"),
        ("man", None, "데이터 무결성 검증", "손상 감지·자가복구"),
        ("man", None, "자동저장·작업 복구", "강제종료 시 입력 유실 방지")]),
    ("🛟", "장애 대응·복원력", [
        ("m", "crash", "크래시·장애 모니터링", "Sentry·Crashlytics"),
        ("m", "emptyState", "빈/에러/로딩 상태 UI", "실패 시 안내·재시도"),
        ("m", "retry", "네트워크 재시도·타임아웃", "백오프·지연 대비"),
        ("man", None, "전역 에러 핸들링·폴백 화면", "앱이 죽지 않고 회복"),
        ("man", None, "기능 플래그·원격 킬스위치", "문제 기능 즉시 차단"),
        ("man", None, "롤백 전략", "불량 릴리스 되돌리기")]),
    ("🧪", "품질 보증(QA)", [
        ("m", "tests", "자동화 테스트", "XCTest·Swift Testing"),
        ("m", "swiftlint", "정적 분석(SwiftLint)", "코드 일관성·결함 예방"),
        ("m", "ci", "CI/CD 파이프라인", "빌드·테스트·배포 자동화"),
        ("man", None, "베타 테스트(TestFlight)", "출시 전 실사용 검증"),
        ("man", None, "회귀 테스트 루틴", "기존 기능 재검증"),
        ("man", None, "코드 리뷰 프로세스", "머지 전 검토")]),
    ("🔭", "관측성(Observability)", [
        ("t", "analytics", "사용현황 분석", "외부 수집 SDK 실사용"),
        ("t", "feedbackHub", "피드백 허브 연동", "받고 앱내 확인"),
        ("man", None, "성능 모니터링", "시작시간·프레임·메모리"),
        ("man", None, "구조적 로그·원격 진단", "문제 재현 추적"),
        ("man", None, "핵심지표 대시보드", "리텐션·전환 상시 관측")]),
    ("🔐", "보안·개인정보", [
        ("m", "security", "보안·생체 인증", "Keychain·FaceID"),
        ("m", "privacyManifest", "개인정보 매니페스트", "PrivacyInfo.xcprivacy"),
        ("man", None, "계정·데이터 삭제 경로", "앱스토어 필수"),
        ("man", None, "개인정보 처리방침·약관 링크", "앱 내 접근"),
        ("man", None, "전송·저장 암호화", "ATS·at-rest"),
        ("man", None, "최소 권한 요청", "필요한 권한만")]),
    ("✨", "UX 완성도", [
        ("m", "a11y", "접근성", "VoiceOver·Dynamic Type"),
        ("m", "i18n", "다국어·현지화", "글로벌 노출"),
        ("m", "darkmode", "다크모드 대응", "시스템 테마"),
        ("m", "onboarding", "온보딩·권한 사전안내", "첫 경험 이탈 방지"),
        ("man", None, "다양한 기기·화면", "iPad·노치·Dynamic Island"),
        ("man", None, "햅틱·로딩 스켈레톤·마이크로카피", "마감 디테일")]),
    ("📈", "성장·리텐션", [
        ("t", "reviewPrompt", "리뷰요청 장치", "StoreReview"),
        ("m", "push", "푸시 알림·재참여", "UserNotifications"),
        ("m", "receipt", "결제·구독 안정성", "영수증검증·복원"),
        ("m", "widget", "위젯·확장 표면", "WidgetKit"),
        ("man", None, "온보딩 완료·전환 퍼널", "가입→활성 전환율"),
        ("man", None, "리텐션·코호트 분석", "재방문·이탈 추적"),
        ("man", None, "A/B 테스트", "가설 검증")]),
    ("📣", "마케팅·홍보", [
        ("kit", None, "마케팅 킷 제작", "앱별 콘텐츠 세트"),
        ("sup", None, "지원·랜딩 페이지", "supportUrl 확보"),
        ("has", None, "공개 쇼케이스 사이트", "docs/index.html"),
        ("man", None, "실제 발행·게시", "제작 완료·발행 대기"),
        ("man", None, "홍보 채널 다변화", "X·스레드·인스타·커뮤니티"),
        ("man", None, "이벤트·캠페인 진행", "런칭·시즌·리텐션 이벤트"),
        ("man", None, "ASO 키워드 최적화", "검색 노출"),
        ("man", None, "커뮤니티·제휴·인플루언서", "유입 채널 확장")]),
]


def checklist(apps, kit_count):
    scanned = [a for a in apps if a["scanned"]]
    ns, nt = len(scanned), len(apps)
    cards = []
    for icon, title, items in CATEGORIES:
        auto = sum(1 for k, *_ in items if k != "man")
        manual = sum(1 for k, *_ in items if k == "man")
        lis = []
        for kind, key, label, note in items:
            if kind == "man":
                val = '<span class="cov manual">수동 확인</span>'
            elif kind == "m":
                val = cov(cnt(scanned, lambda a, key=key: a["m"][key]), ns)
            elif kind == "t":
                val = cov(cnt(apps, lambda a, key=key: a[key]), nt)
            elif kind == "kit":
                val = cov(kit_count, nt)
            elif kind == "sup":
                val = cov(cnt(apps, lambda a: bool(a["supportUrl"])), nt)
            else:
                val = '<span class="cov cok">있음</span>'
            lis.append('<li><span class="ci-l">%s<i>%s</i></span>%s</li>' % (label, note, val))
        cards.append('<div class="catcard"><div class="cathd"><span class="cicon">%s</span><b>%s</b>'
                     '<span class="cameta">%d개 · 자동측정 %d / 수동 %d</span></div>'
                     '<ul class="cilist">%s</ul></div>'
                     % (icon, title, len(items), auto, manual, "".join(lis)))
    return "".join(cards)


def insights(apps, kit_count):
    scanned = [a for a in apps if a["scanned"]]
    ns, nt = len(scanned), len(apps)
    hub = cnt(apps, lambda a: a["feedbackHub"])
    soft = cnt(apps, lambda a: a["feedbackSoft"] and not a["feedbackHub"])
    an3 = cnt(apps, lambda a: a["analytics"])
    anl = cnt(apps, lambda a: a["analyticsLocalOnly"])
    tests = cnt(scanned, lambda a: a["m"]["tests"])
    crash = cnt(scanned, lambda a: a["m"]["crash"])
    ci = cnt(scanned, lambda a: a["m"]["ci"])
    lint = cnt(scanned, lambda a: a["m"]["swiftlint"])
    cloud = cnt(scanned, lambda a: a["m"]["cloud"])
    backup = cnt(scanned, lambda a: a["m"]["backup"])
    priv = cnt(scanned, lambda a: a["m"]["privacyManifest"])
    rev = cnt(apps, lambda a: a["model"] not in (None, "free"))
    review = cnt(apps, lambda a: a["reviewPrompt"])
    out = [
        ('good', '<b>피드백 인프라는 이미 넓게 깔렸다</b> — FeedbackHub 연동 %d/%d개(인앱UI만 %d). '
                 '클라우드 보관 %d/%d · 백업 %d/%d 로 데이터 보존도 다수 확보.'
                 % (hub, nt, soft, cloud, ns, backup, ns)),
        ('warn', '<b>사용현황 수집이 사실상 없다</b> — 외부 분석 SDK 실사용 %d/%d개. '
                 '이벤트 래퍼만 있고 전송하지 않는(no-op·콘솔) 앱이 %d개 — 데이터 기반 판단 불가.'
                 % (an3, nt, anl)),
        ('warn', '<b>안정성 안전망이 가장 얇다</b> — 자동화 테스트 %d/%d, 장애 모니터링 %d/%d, '
                 'CI/CD %d/%d, SwiftLint %d/%d. 개인정보 매니페스트도 %d/%d.'
                 % (tests, ns, crash, ns, ci, ns, lint, ns, priv, ns)),
        ('', '<b>성장 장치 미비</b> — 리뷰요청 %d/%d개. 수익모델 보유 %d/%d개이나 무료 다수가 전환 경로 없음.'
             % (review, nt, rev, nt)),
        ('', '<b>마케팅은 자산은 있으나 실행 대기</b> — 킷 %d종·지원페이지 %d종·쇼케이스는 준비됐지만 '
             '실제 발행/이벤트/캠페인은 미진행.'
             % (kit_count, cnt(apps, lambda a: bool(a["supportUrl"])))),
        ('', '권고 순서: ① 크래시 모니터링 + 실제 분석 SDK 공통모듈 전 앱 이식(no-op 래퍼 교체) → '
             '② 핵심 로직 테스트 + CI 1개 앱 파일럿 → ③ 리뷰요청 장치 일괄 삽입 → '
             '④ 마케팅 킷 발행 개시 + 런칭 이벤트 → ⑤ 무료 앱 중 리텐션 높은 것 수익화.'),
    ]
    return "".join('<div class="insight%s">%s</div>' % ((" " + c) if c else "", t) for c, t in out)


def build_status(apps, kit_count, today, head):
    scanned = [a for a in apps if a["scanned"]]
    ns, nt = len(scanned), len(apps)
    on_store = cnt(apps, lambda a: bool(a["appStoreId"]))
    kr_only = cnt(apps, lambda a: a["appStoreId"] and not a["storeKR"])
    rev = cnt(apps, lambda a: a["model"] not in (None, "free"))
    segs, legend, _ = monetization(apps)
    hub = cnt(apps, lambda a: a["feedbackHub"])
    an3 = cnt(apps, lambda a: a["analytics"])
    anl = cnt(apps, lambda a: a["analyticsLocalOnly"])
    cloud = cnt(scanned, lambda a: a["m"]["cloud"])
    backup = cnt(scanned, lambda a: a["m"]["backup"])
    tests = cnt(scanned, lambda a: a["m"]["tests"])
    crash = cnt(scanned, lambda a: a["m"]["crash"])
    avg = round(sum(a["maturity"] for a in apps) / nt)

    kpis = [
        (str(nt), "등록 앱", "App Store 등록 %d%s" % (on_store, " · KR미판매 %d" % kr_only if kr_only else "")),
        ("%d<span style=\"font-size:14px;color:var(--muted)\">/%d</span>" % (rev, nt), "수익모델 보유", "유료·부분유료·구독"),
        ("%d<span style=\"font-size:14px;color:var(--muted)\">/%d</span>" % (hub, nt), "피드백 허브", "인앱UI만 %d" % cnt(apps, lambda a: a["feedbackSoft"] and not a["feedbackHub"])),
        ("%d<span style=\"font-size:14px;color:var(--muted)\">/%d</span>" % (an3, nt), "사용현황 수집", "로컬 래퍼만 %d" % anl),
        ("%d<span style=\"font-size:14px;color:var(--muted)\">/%d</span>" % (tests, ns), "자동화 테스트", "장애 모니터 %d/%d" % (crash, ns)),
        ("%d<span style=\"font-size:14px;color:var(--muted)\">/%d</span>" % (ns, nt), "소스 스캔 가능", "평균 성숙도 %d점" % avg),
    ]
    kpi_html = "\n  ".join('<div class="kpi"><div class="v">%s</div><div class="l">%s</div><div class="s">%s</div></div>'
                           % k for k in kpis)

    body = """<div class="wrap">
  <button class="toggle" onclick="var r=document.documentElement;r.setAttribute('data-theme',r.getAttribute('data-theme')==='dark'?'light':'dark')">◐ 테마</button>
  <header>
  <div class="eyebrow">Portfolio Development Status · 내부용 (비배포)</div>
  <h1>앱 포트폴리오 디벨롭 현황 점검</h1>
  <div class="sub">전체 %(nt)d개 앱 · 기준일 %(today)s · 출처: <code>Data/apps/*.json</code> + 로컬 소스 스캔(%(ns)d/%(nt)d) + 라이브 App Store 조회</div>
  <div class="local-note">🔒 어디에도 배포하지 않는 로컬 점검용 문서. 목표: <b>완성도 높은 서비스</b>. 판정 기준은 하단 「평가 기준」.</div>
  <div style="margin-top:12px"><a href="portfolio-explorer.html" style="display:inline-block;font-size:13px;font-weight:600;color:#fff;background:var(--accent);padding:8px 14px;border-radius:9px;text-decoration:none">🔍 앱별 완성도 탐색기 열기 →</a></div>
  </header>

<section><div class="kpis">
  %(kpis)s
</div></section>

<section>
  <h2><span class="hn">1</span>유료화 정도 · 여부</h2>
  <div class="panel"><div class="bar">%(segs)s</div><div class="legend">%(legend)s</div>
  <p style="margin:14px 0 0;font-size:12.5px;color:var(--muted)">수익모델 보유 <b style="color:var(--ink)">%(rev)d개</b>(%(revpct)d%%). IAP 탑재는 표의 <span class="chip">IAP</span> 표시.</p></div>
</section>

<section>
  <h2><span class="hn">2</span>앱별 상세 현황 <span style="font-weight:400;color:var(--muted);font-size:12px">· 성숙도순 · 파란선 오른쪽 = 서비스 견고성</span></h2>
  <div class="tbl-scroll"><table>
    <thead><tr><th>앱</th><th class="ctr">버전</th><th class="ctr">유료화</th><th class="ctr">평점</th><th class="ctr">완료</th>
    <th class="ctr">피드백</th><th class="ctr">사용수집</th><th class="ctr">리뷰요청</th>
    <th class="ctr grphdr grp">데이터 보관</th><th class="ctr grphdr">테스트</th><th class="ctr grphdr">장애 대비</th><th>발달 성숙도</th></tr></thead>
    <tbody>%(rows)s</tbody>
  </table></div>
  <p style="margin:12px 0 0;font-size:12px;color:var(--muted)">버전·평점·가격은 조회 시점의 App Store 실데이터. <span class="b b-mid">로컬만</span>=이벤트 래퍼는 있으나 외부 전송 없음. <span class="chip warn">소스없음</span>=로컬 레포 미연결로 코드 판정 불가.</p>
</section>

<section>
  <h2><span class="hn">3</span>완성도 체크리스트 <span style="font-weight:400;color:var(--muted);font-size:12px">· 탄탄한 서비스가 갖출 8개 영역 · 소스 %(ns)d개 / 포트폴리오 %(nt)d개 기준</span></h2>
  <div class="cats">%(cats)s</div>
  <div class="covlegend">
    <span><span class="cov cok" style="margin:0">n/n</span> 커버리지 60%%↑</span>
    <span><span class="cov cmid" style="margin:0">n/n</span> 35–59%%</span>
    <span><span class="cov clo" style="margin:0">n/n</span> 35%%↓</span>
    <span><span class="cov manual" style="margin:0">수동 확인</span> 코드로 자동판정 불가 — 앱을 직접 열어 확인 필요</span>
  </div>
</section>

<section>
  <h2><span class="hn">4</span>주요 인사이트 · 우선순위</h2>
  <div class="panel">
    %(insights)s
  </div>
</section>

<section>
  <h2><span class="hn">✓</span>평가 기준 <span style="font-weight:400;color:var(--muted);font-size:12px">· 이 HTML을 만들 때 사용한 판정 규칙</span></h2>
  <div class="panel crit">
    <div>
      <h3 style="margin:0 0 6px;font-size:13.5px">유료화 / 피드백 / 사용수집</h3>
      <ul><li>유료화=<code>price.pricingModel</code> 5분류, 수익모델=무료·미설정 제외</li>
      <li>피드백 <span class="b b-ok">허브연동</span>=entitlements의 <code>iCloud.com.Ysoup.FeedbackHub</code> 또는 허브 클라이언트 코드, <span class="b b-mid">인앱UI</span>=피드백 화면만</li>
      <li>사용수집 <span class="b b-ok">도입</span>=<code>TelemetryDeck·FirebaseAnalytics·Amplitude</code> 등 외부 SDK 실사용, <span class="b b-mid">로컬만</span>=자체 래퍼만(전송 없음)</li>
      <li>리뷰요청=<code>requestReview·SKStoreReviewController</code></li></ul>
      <h3 style="margin:14px 0 6px;font-size:13.5px">서비스 견고성 (표 컬럼)</h3>
      <ul><li>데이터보관 <span class="b b-ok">클라우드</span> <code>CloudKit·iCloud</code> &gt; <span class="b b-ok">서버DB</span> <code>Firebase·Supabase</code> &gt; <span class="b b-mid">로컬DB</span> <code>CoreData·SwiftData</code> &gt; <span class="b b-no">기본저장</span>, <span class="chip ok">백업</span>=<code>백업·export/import</code></li>
      <li>테스트=<code>XCTest·@Test</code> 또는 테스트 타깃, 장애대비=<code>Crashlytics·Sentry</code> 실 import</li>
      <li>모든 코드 판정은 <b>주석 제거 후</b> 매칭 — 설명·기획 문서의 언급은 제외</li></ul>
    </div>
    <div>
      <h3 style="margin:0 0 6px;font-size:13.5px">완성도 체크리스트 (8영역) 측정 방식</h3>
      <ul style="font-size:12.5px">
        <li><b>자동측정(코드 스캔, /%(ns)d)</b>: 클라우드·백업·로컬DB·테스트·정적분석·CI·크래시·빈에러UI·재시도·보안·개인정보매니페스트·접근성·다국어·다크모드·온보딩·푸시·결제안정성·위젯</li>
        <li><b>포트폴리오 데이터(/%(nt)d)</b>: 사용수집·피드백허브·리뷰요청·마케팅킷·지원페이지·쇼케이스</li>
        <li><b>수동 확인</b>: 마이그레이션·동기화충돌·트랜잭션·무결성·자동복구·킬스위치·롤백·베타·성능모니터링·삭제경로·약관링크·암호화·리텐션분석·A/B·이벤트/캠페인·ASO·제휴 등</li>
      </ul>
      <h3 style="margin:12px 0 6px;font-size:13.5px">발달 성숙도 = 8축 가중합(100)</h3>
      <ul style="columns:2;font-size:12.5px">
        <li><span class="weight">15</span> 출시</li><li><span class="weight">15</span> 완료율</li><li><span class="weight">15</span> 평점</li><li><span class="weight">15</span> 수익모델</li>
        <li><span class="weight">15</span> 피드백</li><li><span class="weight">10</span> 사용수집</li><li><span class="weight">8</span> 리뷰요청</li><li><span class="weight">7</span> 버전</li>
      </ul>
      <p style="font-size:12px;color:var(--muted);margin:8px 0 0">체크리스트 항목은 <b>정보 제공용</b>이며 성숙도 점수엔 미반영. 커버리지 %%는 스캔된 %(ns)d개 앱 기준.</p>
    </div>
  </div>
</section>

<footer>생성: <code>scripts/build-portfolio-status.py</code> · 기준일 %(today)s · 로컬 전용(비배포)<br>
데이터: <code>Data/apps/*.json</code> · 코드 스캔 %(ns)d/%(nt)d · 라이브 App Store 조회 · 마케팅: <code>marketing/</code><br>
상세 기준: <code>docs/portfolio-status-criteria.md</code></footer>
</div></body></html>
""" % {
        "nt": nt, "ns": ns, "today": today, "kpis": kpi_html, "segs": segs, "legend": legend,
        "rev": rev, "revpct": round(rev / nt * 100), "rows": status_rows(apps),
        "cats": checklist(apps, kit_count), "insights": insights(apps, kit_count),
    }
    head = re.sub(r"<title>[^<]*</title>", "<title>포트폴리오 디벨롭 현황 · %s</title>" % today, head)
    return head + "<body>\n" + body


def build_explorer(apps, today, existing):
    data = json.dumps(apps, ensure_ascii=False)
    out = re.sub(r"const DATA = \[.*?\];\n", "const DATA = %s;\n" % data, existing, count=1, flags=re.S)
    out = re.sub(r"기준일 \d{4}-\d{2}-\d{2}", "기준일 %s" % today, out)
    out = re.sub(r"소스 스캔\(\d+/\d+\)", "소스 스캔(%d/%d)"
                 % (cnt(apps, lambda a: a["scanned"]), len(apps)), out)
    out = re.sub(r"<title>[^<]*</title>", "<title>앱 완성도 탐색기 · %s</title>" % today, out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cached", action="store_true", help="캐시된 App Store 응답 사용")
    args = ap.parse_args()

    apps = collect(cached=args.cached)
    kit_count = len(glob.glob(os.path.join(ROOT, "marketing/apps/*.md")))
    today = date.today().isoformat()

    status_path = os.path.join(REPORTS, "portfolio-status.html")
    explorer_path = os.path.join(REPORTS, "portfolio-explorer.html")
    # 기존 파일의 <head>/스타일과 탐색기 스크립트는 그대로 재사용하므로 먼저 전부 읽어둔다
    # (읽기 전에 쓰기 핸들을 열면 파일이 잘려 내용이 사라진다)
    status_head = open(status_path, encoding="utf-8").read().split("<body>")[0]
    explorer_src = open(explorer_path, encoding="utf-8").read()

    status_html = build_status(apps, kit_count, today, status_head)
    explorer_html = build_explorer(apps, today, explorer_src)
    if "const DATA = [" not in explorer_html:
        sys.exit("탐색기 DATA 블록 교체 실패 — portfolio-explorer.html 구조를 확인하세요")

    with open(status_path, "w", encoding="utf-8") as fh:
        fh.write(status_html)
    with open(explorer_path, "w", encoding="utf-8") as fh:
        fh.write(explorer_html)

    ns = cnt(apps, lambda a: a["scanned"])
    print("앱 %d개 · 소스 연결 %d · 스토어 %d · 허브 %d · 분석(외부) %d · 마케팅킷 %d"
          % (len(apps), ns, cnt(apps, lambda a: a["onStore"]),
             cnt(apps, lambda a: a["feedbackHub"]), cnt(apps, lambda a: a["analytics"]), kit_count))
    print("→ %s\n→ %s" % (status_path, explorer_path))


if __name__ == "__main__":
    main()
