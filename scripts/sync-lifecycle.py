#!/usr/bin/env python3
"""App Store 실데이터로 앱 JSON 의 수명주기(lifecycle) 근거 값과 현재 버전을 최신화한다.

사용법:
  python3 scripts/sync-lifecycle.py

판정 기준 (2026-08-30 사용자 확정):
  · 1 vs 2 는 '출시 후 실제로 다듬은 기간'(첫 출시 → 최종 업데이트)으로 가른다. 90일 이하면 1단계.
  · 3단계 이상은 사람이 정한다. 평점 같은 기계적 지표로 자동 승격하지 않는다.
  · 사람이 정한 판정(manual 이면서 90일 규칙 문구가 아닌 것)과 의도적 유지(intent)는
    숫자만 갱신하고 단계는 건드리지 않는다.
  · 2단계 하위 등급(tier)은 최종 업데이트 경과일로 매긴다: 30일 이하 A, 90일 이하 B, 그 위 C.
    (내부 트리아지 용어라 공개 페이지에는 내보내지 않는다)

조회: 개발자 artistId 로 KR 스토어 앱을 일괄 조회하고, 없는 앱은 US 스토어에서 하나씩 찾는다.
"""
import glob
import json
import os
import time
import urllib.request
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "projects/PortfolioCEO/PortfolioCEO/Data/apps")
ARTIST_ID = "1502508537"
RULE_DAYS = 90
RULE_MARK = "90일 이하 → 1단계"   # 규칙으로 1단계에 둔 앱의 basis 에 들어 있는 문구
TIER = [(30, "A", "개선 중"), (90, "B", "소강"), (10 ** 6, "C", "정지")]


def get(url):
    for attempt in range(5):
        try:
            return json.load(urllib.request.urlopen(url, timeout=30))
        except Exception:
            time.sleep(10 * (attempt + 1))
    raise RuntimeError("조회 실패: " + url)


def store_index():
    out = {}
    res = get("https://itunes.apple.com/lookup?id=%s&entity=software&country=kr&limit=200" % ARTIST_ID)
    for r in res.get("results", []):
        if r.get("wrapperType") == "software":
            out[str(r["trackId"])] = r
    return out


def parse(d):
    return datetime.strptime(d[:10], "%Y-%m-%d").date() if d else None


def main():
    today = date.today()
    idx = store_index()
    changes = []
    for path in sorted(glob.glob(os.path.join(APPS, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            app = json.load(fh)
        lc = app.get("lifecycle") or {}
        sid = str(app.get("appStoreId") or "")
        if not sid or lc.get("stage") == 0:
            continue
        r = idx.get(sid)
        if r is None:
            res = get("https://itunes.apple.com/lookup?id=%s&country=us" % sid)
            r = res["results"][0] if res.get("results") else None
            time.sleep(2)
        slug = os.path.basename(path)[:-5]
        if r is None:
            print("  %-24s 스토어에 없음 — 건너뜀" % slug)
            continue

        released = parse(r.get("releaseDate"))
        updated = parse(r.get("currentVersionReleaseDate"))
        polish = (updated - released).days if released and updated else None
        since = (today - updated).days if updated else None
        rc = r.get("userRatingCount") or 0
        ver = r.get("version")

        before = (lc.get("stage"), app.get("currentVersion"))
        if ver and ver != app.get("currentVersion"):
            app["currentVersion"] = ver
        lc.update({"ratingCount": rc, "daysSinceUpdate": since, "polishDays": polish,
                   "releasedAt": released.isoformat() if released else None,
                   "updatedAt": updated.isoformat() if updated else None,
                   "evaluatedAt": today.isoformat()})

        rule_based = RULE_MARK in (lc.get("basis") or "") or not lc.get("manual")
        if lc.get("intent") or not rule_based:
            pass  # 사람이 정한 단계 — 숫자만 갱신
        elif lc.get("stage") in (1, 2):
            if polish is not None and polish <= RULE_DAYS:
                lc.update({"stage": 1, "label": "pre-mvp", "tier": None, "manual": True,
                           "basis": "출시 후 다듬은 기간 %d일 — 출시만으로는 MVP 완성으로 보지 않는다는 "
                                    "기준(%s, 사용자 확인)에 따라 Pre-MVP. v%s · 최종 업데이트 %d일 경과"
                                    % (polish, RULE_MARK, ver, since)})
            else:
                tier, word = next((t, w) for lim, t, w in TIER if (since or 0) <= lim)
                lc.update({"stage": 2, "label": "problem-solution-fit", "tier": tier,
                           "basis": "출시 후 다듬은 기간 %s일 · 외부 평점 %d개 · 최종 업데이트 %d일 경과 → %s"
                                    % (polish, rc, since, word)})
                lc.pop("manual", None)
        app["lifecycle"] = lc
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(app, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        after = (lc.get("stage"), app.get("currentVersion"))
        mark = ""
        if before[0] != after[0]:
            mark += "  ★ 단계 %s→%s" % (before[0], after[0])
            changes.append((slug, before[0], after[0]))
        if before[1] != after[1]:
            mark += "  버전 %s→%s" % (before[1], after[1])
        print("  %-24s %s단계 v%-7s 다듬은 %4s일 · 업데이트 %4s일 전 · 평점 %d%s"
              % (slug, lc.get("stage"), ver, polish, since, rc, mark))
    if changes:
        print("단계 변경:", ", ".join("%s %s→%s" % c for c in changes))


if __name__ == "__main__":
    main()
