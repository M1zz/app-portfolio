#!/usr/bin/env python3
"""주간 ASO 점검표 — 매주 일요일.

허브(FeedbackHubViewer)가 모아 둔 기록만 읽는다(네트워크 없음, 아무것도 고치지 않음).
앱마다 지난 7일과 그 전 7일을 견주고, 이번 주에 손댈 곳을 판정해 한 장으로 낸다.

    python3 scripts/aso_weekly.py            # reports/aso/<오늘>.md 를 쓴다
"""
import collections, datetime as dt, json, os, re, subprocess, sys

HUB = os.path.expanduser("~/Library/Containers/com.Ysoup.FeedbackHubViewer.prod/Data/Library/"
                         "Application Support/FeedbackHubViewer")
REPOS = [os.path.expanduser(p) for p in ("~/Documents/workspace/Auto", "~/Documents/workspace/개발중")]
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "aso")
REF = 978307200  # Apple 기준 시각(2001-01-01)
SETTLE_DAYS = 14  # 바꾼 뒤 이만큼은 판정하지 않는다(순위가 자리 잡는 시간)


def rate(a, b):
    return f"{a / b * 100:.1f}%" if b else "-"


def load(name):
    with open(os.path.join(HUB, name)) as f:
        return json.load(f)


def day(s):
    return dt.date.fromisoformat(s)


def repo_for(bundle):
    """번들 ID 로 레포를 찾는다(pbxproj 의 PRODUCT_BUNDLE_IDENTIFIER)."""
    pat = re.compile(r"PRODUCT_BUNDLE_IDENTIFIER = \"?" + re.escape(bundle) + r"\"?;")
    for root in REPOS:
        for name in sorted(os.listdir(root)):
            path = os.path.join(root, name)
            if not os.path.isdir(path):
                continue
            for entry in os.listdir(path):
                if entry.endswith(".xcodeproj"):
                    pbx = os.path.join(path, entry, "project.pbxproj")
                    try:
                        if pat.search(open(pbx, errors="ignore").read()):
                            return path
                    except OSError:
                        pass
    return None


def appstore_changed(repo):
    """APPSTORE.md 를 마지막으로 바꾼 날, 그리고 그 뒤 배포(DeployBar 배포분 커밋)가 있었나."""
    def git(*args):
        return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True).stdout.strip()
    changed = git("log", "-1", "--format=%cs", "--", "APPSTORE.md")
    deployed = git("log", "-1", "--format=%cs", "--grep=DeployBar 배포분")
    return (day(changed) if changed else None), (day(deployed) if deployed else None)


def main():
    today = dt.date.today()
    names = {b: v["name"] for b, v in load("connect-apps-v2.json").items()}
    store = load("store-metadata.json")
    funnels = load("analytics-results.json")["funnels"]
    kw = load("keywords.json")
    links = kw["links"]  # 번들 → 앱 id
    fields = load("keyword-fields.json")

    # 키워드: 번들 → [(검색어, 오늘 순위, 7일 전 순위)]
    by_app = collections.defaultdict(list)
    for key, entry in kw["keywords"].items():
        checks = kw["checks"].get(key, {})
        if not checks:
            continue
        days = sorted(checks)
        latest = days[-1]
        week_ago = [d for d in days if day(d) <= day(latest) - dt.timedelta(days=6)]
        for bundle in entry["projects"]:
            app_id = str(links.get(bundle, ""))
            now = checks[latest].get("ranks", {}).get(app_id)
            before = checks[week_ago[-1]].get("ranks", {}).get(app_id) if week_ago else None
            by_app[bundle].append((entry["term"], now, before))

    rows, actions = [], collections.defaultdict(list)
    for bundle in sorted(set(names) | set(funnels), key=lambda b: names.get(b, b)):
        name = names.get(bundle, bundle)
        # 퍼널: 받은 날짜 중 마지막 7일 대 그 전 7일
        daily = funnels.get(bundle, {}).get("daily", {})
        dates = sorted(daily)
        def total(ds):
            t = collections.Counter()
            for d in ds:
                t.update(daily[d])
            return t
        this, prev = total(dates[-7:]), total(dates[-14:-7])

        terms = by_app.get(bundle, [])
        top10 = sum(1 for _, n, _ in terms if n and n <= 10)
        top50 = sum(1 for _, n, _ in terms if n and n <= 50)
        top10_before = sum(1 for _, _, b in terms if b and b <= 10)
        entered = [t for t, n, b in terms if n and n <= 10 and not (b and b <= 10)]
        dropped = [t for t, n, b in terms if b and b <= 10 and not (n and n <= 10)]

        # 키워드 칸 나이(스토어에 실제로 나가 있는 값 기준) — 한국어
        seen = fields.get(f"{bundle}|ko") or []
        live_age = (today - dt.date.fromtimestamp(seen[-1]["seenAt"] + REF)).days if seen and not seen[-1].get("isBaseline") else None

        repo = repo_for(bundle)
        changed, deployed = appstore_changed(repo) if repo else (None, None)
        pending = bool(changed and (not deployed or changed > deployed))

        # 이름 · 부제와 겹치는 키워드(언어 수)
        dup_locales = []
        for loc, x in store.get(bundle, {}).get("live", {}).get("locales", {}).items():
            words = {w.lower() for w in re.findall(r"\w+", f"{x.get('name', '')} {x.get('subtitle', '')}") if len(w) > 2}
            if any(k.strip().lower() in words for k in (x.get("keywords") or "").split(",") if k.strip()):
                dup_locales.append(loc)

        # 판정
        if pending:
            actions[bundle].append(f"레포에 바꾼 스토어 문구가 아직 안 나감({changed}) — 배포해야 효과를 잰다")
        if changed and (today - changed).days < SETTLE_DAYS:
            actions[bundle].append(f"키워드는 {changed} 에 바꿈 — {SETTLE_DAYS}일이 지난 {changed + dt.timedelta(days=SETTLE_DAYS)} 이후에 판정")
        elif terms and top50 < max(3, len(terms) // 4):
            actions[bundle].append(f"50위 안 검색어가 {top50}/{len(terms)}개뿐 — 키워드 다시 짜기")
        if dropped:
            actions[bundle].append("10위 밖으로 밀린 말: " + ", ".join(dropped[:5]))
        # 검색 결과에서 바로 받는 사람이 많아 "조회 → 다운로드" 는 100% 를 넘는다. 노출 대비 다운로드로 본다.
        if this["impressions"] >= 300 and this["firstDownloads"] / this["impressions"] < 0.01:
            actions[bundle].append(f"노출 {this['impressions']}번에 다운로드 {this['firstDownloads']} ({rate(this['firstDownloads'], this['impressions'])}) "
                                   "— 검색 결과에서 지나친다: 아이콘 · 스크린샷 1~3장 · 부제")
        if dup_locales:
            actions[bundle].append(f"이름 · 부제와 겹치는 키워드 {len(dup_locales)}개 언어 — 빼고 다른 말로")

        rows.append((name, this, prev, top10, top10_before, top50, len(terms), entered, live_age))

    lines = [f"# ASO 주간 점검 — {today}", "",
             "허브 기록만 읽어 만든 표. 퍼널은 App Store 분석이 2~3일 늦게 와서 받은 날짜 중 마지막 7일 대 그 전 7일이다.",
             "키워드 순위는 한국 스토어 기준(허브가 추적하는 나라).", "",
             "## 이번 주에 손댈 곳", ""]
    for bundle, items in sorted(actions.items(), key=lambda x: names.get(x[0], x[0])):
        lines.append(f"### {names.get(bundle, bundle)}")
        lines += [f"- {i}" for i in items] + [""]
    lines += ["## 전체 표", "",
              "| 앱 | 노출 | (전주) | 다운로드 | (전주) | 노출→다운로드 | 10위 안 | (전주) | 50위 안 | 추적 |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, this, prev, t10, t10b, t50, n, entered, _ in sorted(rows, key=lambda r: -r[1]["impressions"]):
        lines.append(f"| {name} | {this['impressions']} | {prev['impressions']} | {this['firstDownloads']} | {prev['firstDownloads']} | "
                     f"{rate(this['firstDownloads'], this['impressions'])} | {t10} | {t10b} | {t50} | {n} |")
    entered_all = [(name, e) for name, *_, entered, _ in rows for e in entered]
    if entered_all:
        lines += ["", "## 이번 주 10위 안에 새로 든 말", ""]
        lines += [f"- {name}: {e}" for name, e in entered_all]

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{today}.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(path)


if __name__ == "__main__":
    sys.exit(main())
