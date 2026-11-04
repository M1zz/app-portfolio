#!/usr/bin/env python3
"""모든 앱의 데이터 안전 점검 — 구조 이전(마이그레이션)과 백업을 한 프로세스에서 차례로 본다.

    python3 scripts/data-safety-audit.py            # 표 + reports/data-safety.md
    python3 scripts/data-safety-audit.py 밑줄 하늘색  # 몇 개만

앱마다 네 가지를 묻는다.
  1. 저장소를 못 열면 앱이 죽는가          (fatalError · try! · .modelContainer(for:))  🔴
  2. 저장 구조가 바뀌면 기록이 사라지는가   (try? decode 실패 → 빈 값 → 다음 저장에 덮어씀) 🔴
  3. 구조 이전이 계획돼 있는가             (SwiftData VersionedSchema · Core Data 자동 이전) 🟡
  4. 기록이 백업되는가                    (Caches · 백업 제외 표시)                  🔴
                                         (기기 백업 말고 내보내기 · iCloud 도 있는가) 🟡

grep 기반이라 놓치거나 지나치게 잡을 수 있다. 🔴 은 사람이 그 줄을 읽고 판단한다.
끝 코드: 🔴 가 하나라도 있으면 1.
"""
import re
import unicodedata
import sys
from pathlib import Path

ROOT = Path.home() / "Documents/workspace/Auto"
REPORT = Path(__file__).resolve().parent.parent / "reports/data-safety.md"
SKIP_REPOS = {"LeeoKit", "TrainBoardKit", "DeployBar"}
SKIP_DIRS = {".build", "build", "DerivedData", "Pods", ".git", "Tests", "UITests"}
# 미리보기 · 데모 · 스크린샷용 코드는 사용자 데이터가 아니다
SKIP_FILE = re.compile(r"(Preview|Demo|Screenshot|Mock|Sample|Seed|Tests?)\w*\.swift$")

CONTAINER_OPEN = re.compile(r"ModelContainer\(|loadPersistentStores")
CRASH = re.compile(r"fatalError\(|try! ")
LOSSY_DECODE = re.compile(r"try\? *[\w.()]*[Dd]ecoder\w*\(?\)?\.decode\(")
# 실패한 원본을 어딘가에 남기는가 — 남기면 '손실'이 아니라 '보류'다
KEEPS_ORIGINAL = re.compile(r"unreadable|recover|quarantine|corrupt|preserve|보존|격리", re.I)
# 앱 설정·캐시처럼 잃어도 되는 것 — 사용자가 만든 기록만 센다
DISPOSABLE = re.compile(r"setting|prefer|cache|config|onboard|seed|remote|flag|network|station|rail|bundle\.|forResource|URLSession|response|widget|snapshot", re.I)

PERSISTED = re.compile(r"\.data\(forKey|Data\(contentsOf|contents\(atPath|NSUbiquitousKeyValueStore|\.object\(forKey")
EXPORT = re.compile(r"fileExporter|ShareLink\(item: *\w*(url|file|export|backup)|exportData|func export\w*\(|UIDocumentPickerViewController\(forExporting", re.I)
IMPORT = re.compile(r"fileImporter|UIDocumentPickerViewController\(forOpening|func import\w*\(|func restore\w*\(|importData", re.I)
# 기기 백업(iCloud·컴퓨터)에서 빠지는 자리 — 캐시가 아닌 파일이 여기 있으면 기록이 백업되지 않는다
NOT_BACKED_UP = re.compile(r"isExcludedFromBackup *= *true|\.cachesDirectory")
# LeeoKit 3.30 금고(LeeoVault) — bootstrap 이나 LeeoVault.start 를 부르면 매일·업데이트 직전 백업 + 파일 + iCloud
VAULT_CALL = re.compile(r"LeeoKit\.bootstrap\(|LeeoVault\.start\(")
ICLOUD = re.compile(r"cloudKitDatabase: *\.(automatic|private)|NSPersistentCloudKitContainer|CKContainer|NSUbiquitousKeyValueStore|LeeoCloud")

# 어느 타깃에도 들지 않아 빌드되지 않는 폴더 — 앱에 들어가지 않는 코드다
UNBUILT = {"RapportMap/macOS"}

# 읽어 보고 '유실 아님'으로 판정한 자리. 키는 "앱", "앱/경로", 또는 "앱/경로|그 줄에 든 글자".
# 줄 번호 대신 글자로 짚어서, 코드가 움직여도 맞고 같은 파일에 새 위험이 생기면 다시 잡힌다.
REVIEWED = {
    "FeedbackHubViewer": "개발자 본인용 도구 — 앱 사용자의 기록이 아니다",
    # 위젯·키보드·스티커 — 읽기만 한다. 덮어쓰는 쪽은 앱이고, 앱은 따로 본다
    "밑줄/BookmarkShotWidget/SharedQuote.swift": "위젯 읽기 전용",
    "불타는내인생/BurningParchmentWidgets/DeadlineWidget.swift": "위젯 읽기 전용",
    "세끼/SekkiWidget/SekkiWidgetStore.swift": "위젯 읽기 전용",
    "이어생각/widget/widget.swift": "위젯 읽기 전용",
    "펀칭/sticker/MessagesViewController.swift": "스티커 읽기 전용",
    "펀칭/keyboard/KeyboardViewController.swift": "키보드 읽기 전용",
    "클립키보드/ClipKeyboardExtension/KeyboardView.swift": "키보드 읽기 전용",
    "불타는내인생/BurningParchment/Models/BedtimeIntents.swift|func all() -> [DeadlineEntity]": "Siri · Spotlight 읽기 전용",
    "우리집 가정법원/FamilyCourt/Store.swift|func savedCases()": "Siri · Spotlight 읽기 전용",
    "펀칭/StampCamera/OpenKkukCameraIntent.swift|appendingPathExtension(\"json\")": "Siri · Spotlight 읽기 전용",
    # 다시 만들 수 있는 것 — 사본 · 캐시 · 집계 · 동기화 메타데이터
    "밑줄/BookmarkShot/Services/SharedQuoteStore.swift": "위젯용 사본 — 원본은 SwiftData",
    "벅뚜벅뚜/FootprintDiary/TerrainCache.swift": "지형 캐시",
    "욕망의 무지개/ScheduleDensityApp/Shared/WeekLedger.swift": "주간 집계",
    "퇴사각/FireTracker/FireSummary.swift": "위젯용 요약",
    "아이일정/CalendarSnap/FamilySharing/SyncStateStore.swift": "동기화 상태",
    "장표스냅/SlideSnap/CloudSync.swift": "동기화 메타데이터",
    "세끼/RoutineCamera/Manager/MealCloudSync.swift|visionAnalysis": "iCloud 레코드에서 온 분석값 — 다시 받는다",
    "세끼/RoutineCamera/Manager/MealCloudSync.swift|func loadState()": "동기화 진행 표식 — 잃으면 다시 맞춘다",
    "햇빛바라기/SunlightTracker/SunlightIntents.swift": "Siri 답 — 읽기만 한다",
    "장표스냅/SlideSnap/SlideIntents.swift|func read() -> [Presentation]": "Siri·Spotlight 색인 — 읽기만 하고 저장하지 않는다",
    "세끼/RoutineCamera/Manager/AchievementManager.swift": "업적 — 기록에서 다시 센다",
    "세끼/RoutineCamera/Model/Models.swift|PendingAteAll": "위젯이 쌓은 대기열",
    "오늘의 주접/Jujob/Managers/UserPreferencesManager.swift|QuoteFeedback": "추천용 반응",
    "오늘의 주접/Jujob/Managers/UserPreferencesManager.swift|DailyStreak": "연속 기록 — 다시 센다",
    "오늘의 주접/Jujob/Managers/UserPreferencesManager.swift|[Achievement]": "업적",
    "햇빛바라기/SunlightTracker/SunlightManager.swift|PetalFadePersisted": "꽃잎 연출 상태",
    "햇빛바라기/SunlightTracker/SunlightManager.swift|BatteryStatus": "오늘 상태 — 기록에서 다시 계산",
    "햇빛바라기/SunlightTracker/SunlightManager.swift|SunflowerHealth": "오늘 상태 — 기록에서 다시 계산",
    "골드위크/Goldweek/Models/Models.swift|[String: Int]": "요일별 근무시간 설정",
    "돈꼬마트/DontGoMart/Manager/UsageReporter.swift": "사용 통계",
    "두번알림/Shared/Modules/QuickStartShelf.swift": "위젯용 사본 — 원본은 SwiftData 템플릿",
    "두번알림/Rereminder/Modules/RepeatDetector.swift": "반복 감지 기록 — 다시 쌓인다",
    "두번알림/Rereminder/Modules/NextOccasionReminder.swift": "다음 일정 알림 한 건",
    "펀칭/StampCamera/ContentView.swift|StampMeta": "도장 한 장의 부가 정보 — 도장 그림은 따로 있다",
    # 의도된 동작
    "무지개 공방/WeekBlocks/TodoShareInbox.swift": "공유 상자 — 깨진 건 버리는 게 의도(주석)",
    "욕망의 무지개/ScheduleDensityApp/Shared/TodoShareInbox.swift": "공유 상자 — 같은 의도",
    "장표스냅/Shared/ShareInbox.swift": "공유 상자",
    "팔랑북/RotoscopeiPad/Models/RotoProject.swift": "프로젝트 열기 — 실패해도 덮어쓰지 않는다",
    # 옛 형식 이전 — 실패하면 옛 키를 지우지 않고 둔다
    "뇌모리/Shared/MemoRepository.swift|LegacyMemo": "옛 형식 이전",
    "불타는내인생/BurningParchment/Models/ReflectionManager.swift|LegacyUrn": "옛 형식 이전",
    "세끼/RoutineCamera/Model/Models.swift|oldData": "옛 형식 이전",
    "펀칭/StampCamera/ContentView.swift|LegacyCollectionsFile": "옛 형식 이전 — 파일은 이름만 바꾼다",
    "실수100/JuniorDevMistakes/ChecklistManager.swift": "UserDefaults → Core Data 이전, 옛 키는 남긴다",
    "클립키보드/ClipKeyboard/App/ClipKeyboardApp.swift|LegacyMemoFields": "옛 형식 이전",
    # 클립키보드 · 탭클립키보드 — 메모 본체는 격리 장치가 지킨다. 나머지는 학습 기록 · 동기화 메타데이터 · 개수 읽기
    "클립키보드/ClipKeyboard/Extensions/TemplateVariableProcessor.swift": "[String] — 구조가 바뀔 일이 없다",
    "클립키보드/ClipKeyboard/Screens/CloudBackupView.swift": "백업 미리보기 읽기",
    "클립키보드/ClipKeyboard/Service/EditPattern.swift": "학습 기록",
    "클립키보드/ClipKeyboard/Service/CursorMemory.swift": "학습 기록",
    "클립키보드/ClipKeyboard/Service/RepeatCopyLedger.swift": "학습 기록",
    "클립키보드/ClipKeyboard/Service/KeyboardSessionLedger.swift": "사용 기록",
    "클립키보드/ClipKeyboard/Service/MemoSyncEngine.swift": "동기화 메타데이터",
    "클립키보드/ClipKeyboard/Service/CloudKitBackupService.swift": "백업 개수 읽기",
    "클립키보드/ClipKeyboard/Service/CategorySnapshot.swift": "구버전·신버전 호환으로 설계됨(머리말)",
    "클립키보드/ClipKeyboard/Service/MemoStore.swift|ClipboardHistory": "복사 기록 — 지나가는 것",
    "클립키보드/ClipKeyboard/Service/MemoStore.swift|PlaceholderValue": "자리표시 값 제안",
    "탭클립키보드/Shared/MemoSyncEngine.swift": "동기화 메타데이터",
    "탭클립키보드/Shared/CategorySnapshot.swift": "구버전·신버전 호환으로 설계됨(머리말)",
    "탭클립키보드/ClipKeyboard.tap/CloudKitBackupService.swift": "백업 개수 읽기",
    "탭클립키보드/ClipKeyboard.tap/CloudBackupView.swift": "백업 미리보기 읽기",
    "탭클립키보드/ClipKeyboard.tap/Models.swift|ClipboardHistory": "복사 기록 — 지나가는 것",
    "탭클립키보드/ClipKeyboard.tap/Models.swift|MacShotMode": "촬영 모드 데모",
}


def reviewed(repo: Path, rel: Path, line: str) -> bool:
    # macOS 는 한글 파일 이름을 NFD 로 준다 — 표의 글자(NFC)와 맞춰 비교한다
    name, path = (unicodedata.normalize("NFC", x) for x in (repo.name, f"{repo.name}/{rel}"))
    return name in REVIEWED or path in REVIEWED or any(
        k.startswith(path + "|") and k.split("|", 1)[1] in line for k in REVIEWED)


def swift_files(repo: Path):
    for p in repo.rglob("*.swift"):
        parts = p.relative_to(repo).parts
        if (SKIP_DIRS.intersection(parts) or SKIP_FILE.search(p.name)
                or any(x.startswith("_backup") for x in parts)
                or f"{unicodedata.normalize('NFC', repo.name)}/{parts[0]}" in UNBUILT):
            continue
        yield p


def vault(repo: Path):
    """(켜졌나, iCloud 도 쓰나). LeeoKit 3.30 이상을 쓰고 금고를 켜는 호출이 있어야 켜진 것이다."""
    ok = False
    for r in repo.rglob("Package.resolved"):
        if ".build" in r.parts or "build" in r.parts:
            continue
        m = re.search(r'LeeoKit\.git".*?"version" : "(\d+)\.(\d+)', r.read_text(errors="ignore"), re.S)
        if m and (int(m.group(1)), int(m.group(2))) >= (3, 30):
            ok = True
    if not ok:
        return False, False
    texts = [f.read_text(errors="ignore") for f in swift_files(repo)]
    on = any(VAULT_CALL.search(t) for t in texts)
    return on, on and not any(re.search(r"vaultUsesICloud\s*(?::\s*Bool)?\s*[={]\s*false", t) for t in texts)


def in_preview(lines, i):
    """그 줄이 #Preview · PreviewProvider · 메모리 전용 컨테이너 안이면 사용자 데이터가 아니다"""
    window = "\n".join(lines[max(0, i - 8): i + 3])
    return any(k in window for k in ("#Preview", "PreviewProvider", "isStoredInMemoryOnly: true", "/dev/null", "메모리 저장소"))


def audit(repo: Path):
    r = {"name": repo.name, "store": set(), "crash": [], "lossy": [], "versioned": False,
         "cd_auto": False, "export": False, "import": False, "icloud": False, "unbacked": []}
    for f in swift_files(repo):
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        rel = f.relative_to(repo)
        lines = text.splitlines()
        if "@Model" in text or "ModelContainer" in text:
            r["store"].add("SwiftData")
        if "NSPersistentContainer" in text or "NSPersistentCloudKitContainer" in text:
            r["store"].add("CoreData")
        if re.search(r"JSONEncoder\(\)\.encode|PropertyListEncoder", text):
            r["store"].add("Codable")
        r["versioned"] |= "VersionedSchema" in text and "SchemaMigrationPlan" in text
        r["cd_auto"] |= bool(re.search(r"shouldMigrateStoreAutomatically|shouldInferMappingModelAutomatically|NSPersistentCloudKitContainer", text))
        r["export"] |= bool(EXPORT.search(text))
        r["import"] |= bool(IMPORT.search(text))
        r["icloud"] |= bool(ICLOUD.search(text))
        if NOT_BACKED_UP.search(text) and "cache" not in f.name.lower():
            r["unbacked"].append(str(rel))

        for i, line in enumerate(lines):
            if CONTAINER_OPEN.search(line) and "Fallback" not in f.name:
                # 컨테이너를 여는 줄부터 15줄 안의 fatalError · try! = 열기 실패가 곧 앱 종료
                for j in range(i, min(i + 15, len(lines))):
                    if CRASH.search(lines[j]) and not in_preview(lines, j) and "InMemory" not in lines[j]:
                        r["crash"].append(f"{rel}:{j + 1}")
                        break
            # `.modelContainer(for:)` 수정자는 저장소를 못 열면 그 자리에서 앱을 죽인다
            if ".modelContainer(for:" in line and not line.lstrip().startswith("//") and "inMemory: true" not in line and not in_preview(lines, i):
                r["crash"].append(f"{rel}:{i + 1}")
            if LOSSY_DECODE.search(line) and not DISPOSABLE.search(line) and not reviewed(repo, rel, "\n".join(lines[max(0, i - 3): i + 1])):
                around = "\n".join(lines[max(0, i - 3): i + 8])
                # 디스크·UserDefaults 에서 읽은 것만 — 네트워크 응답은 다시 받으면 된다
                if PERSISTED.search(around) and not KEEPS_ORIGINAL.search(around) and not DISPOSABLE.search(around):
                    r["lossy"].append(f"{rel}:{i + 1}")
    r["crash"] = sorted(set(r["crash"]))
    r["vault"], vault_cloud = vault(repo)
    if r["vault"]:
        r["export"] = r["import"] = True
        r["icloud"] |= vault_cloud
    return r


def verdict(r):
    red, yellow = [], []
    if r["unbacked"]:
        red.append(f"기기 백업에서 빠지는 자리에 저장 {len(r['unbacked'])}곳")
    if r["crash"]:
        red.append(f"저장소를 못 열면 종료 {len(r['crash'])}곳")
    if r["lossy"]:
        red.append(f"해독 실패 시 원본 유실 가능 {len(r['lossy'])}곳")
    if "SwiftData" in r["store"] and not r["versioned"]:
        yellow.append("스키마 버전 없음(필드 추가만 안전)")
    if "CoreData" in r["store"] and not r["cd_auto"]:
        yellow.append("Core Data 자동 이전 설정 없음")
    if r["store"] and not (r["export"] and r["import"]) and not r["icloud"]:
        yellow.append("기기 백업에만 의존(내보내기·iCloud 없음 — 앱을 지우면 복구 길 없음)")
    return red, yellow


def main(names):
    repos = sorted(p for p in ROOT.iterdir()
                   if p.is_dir() and p.name not in SKIP_REPOS and (p / ".git").exists()
                   and (not names or unicodedata.normalize("NFC", p.name) in names))
    rows, details, reds = [], [], 0
    for repo in repos:  # 한 프로세스에서 한 앱씩 차례로
        r = audit(repo)
        red, yellow = verdict(r)
        reds += bool(red)
        mark = "🔴" if red else "🟡" if yellow else "✅"
        backup = "/".join(x for x, ok in (("금고", r["vault"]), ("내보내기", r["export"]), ("가져오기", r["import"]), ("iCloud", r["icloud"])) if ok) or "—"
        store = "+".join(sorted(r["store"])) or "저장 없음"
        rows.append(f"| {mark} | {r['name']} | {store} | {'버전관리' if r['versioned'] else '—'} | {backup} | {' · '.join(red + yellow) or '이상 없음'} |")
        print(f"{mark} {r['name']:<14} {store:<22} {' · '.join(red + yellow) or '이상 없음'}")
        if r["crash"] or r["lossy"] or r["unbacked"]:
            details.append(f"### {r['name']}\n" + "".join(f"- 종료: `{x}`\n" for x in r["crash"])
                           + "".join(f"- 유실: `{x}`\n" for x in r["lossy"])
                           + "".join(f"- 백업 제외: `{x}`\n" for x in r["unbacked"]))

    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(
        "# 데이터 안전 점검\n\n`python3 scripts/data-safety-audit.py` 가 만든다. 손으로 고치지 않는다.\n\n"
        "| | 앱 | 저장 | 구조 이전 | 백업 | 판정 |\n|---|---|---|---|---|---|\n" + "\n".join(rows)
        + "\n\n## 🔴 고칠 자리\n\n" + ("\n".join(details) or "없음\n"))
    print(f"\n{len(repos)}개 앱 · 🔴 {reds}개 · 보고서 {REPORT}")
    return 1 if reds else 0


if __name__ == "__main__":
    sys.exit(main({unicodedata.normalize("NFC", a) for a in sys.argv[1:]}))
