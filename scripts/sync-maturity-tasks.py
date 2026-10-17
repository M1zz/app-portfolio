#!/usr/bin/env python3
"""
서비스 숙성도에서 빠진 피처를 앱마다 '앞으로 할 일'(앱 JSON allTasks)에 넣는다.

- 판정 피처(CHECKLIST)는 기본·권장·선택 모두 — 모든 앱이 다 갖출 것이므로 선택도 할 일이다.
  값이 False(없음)이거나 None(아직 못 잼)이면 할 일. 해당 없음(NA, 예: 인앱 구입이 없는데 구매 복원)은 뺀다.
- 판정 방법이 없는 도입 예정 피처(PLANNED)는 모든 앱에 넣는다.
- 이미 넣은 숙성도 할 일은 이름으로 알아보고 다시 넣지 않는다. 판정이 True 가 되면 done 으로 옮긴다.
- 상태는 not-started(PortfolioCEO 에서 '대기' 백로그), 라벨은 ["숙성도", 등급, 분류].
- stats(totalTasks · done · inProgress · notStarted · todo)는 allTasks 에 맞춰 다시 센다.

기준은 build-portfolio-hub.py 의 CHECKLIST · PLANNED 를 그대로 가져다 쓴다.

사용:
  python3 scripts/sync-maturity-tasks.py          # 미리보기
  python3 scripts/sync-maturity-tasks.py --write  # 앱 JSON 에 저장
"""

import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("hub", os.path.join(ROOT, "scripts/build-portfolio-hub.py"))
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)

LABEL = "숙성도"
TIER_NAME = {t: n for t, n, _ in hub.CHECK_TIERS}
CAT_NAME = {c: n for c, n, _ in hub.CHECK_CATS}


def task(name, tier, cat, desc):
    return {"name": name, "status": "not-started", "targetDate": None, "targetVersion": None,
            "labels": [LABEL, tier, CAT_NAME.get(cat, cat)],
            "featureMetadata": {"category": "서비스 숙성도 · " + CAT_NAME.get(cat, cat), "description": desc}}


def wanted(app):
    """{이름: (할 일 dict 또는 None=이미 갖춤)}"""
    out = {}
    for tier, cat, key, name, _ in hub.CHECKLIST:
        v = hub.checklist(app)[key][3]
        if v == hub.NA:
            continue
        desc = hub.CHECK_HELP.get(key) or ""
        if v is None:
            desc = ("아직 판정하지 못한 항목입니다. 있는지 확인하고 없으면 갖춥니다. " + desc).strip()
        out[name] = None if v is True else task(name, TIER_NAME[tier], cat, desc)
    for cat, name, why in hub.PLANNED:
        out[name] = task(name, "도입 예정", cat, why)
    return out


def recount(app):
    ts = app.get("allTasks") or []
    st = app.setdefault("stats", {})
    st["totalTasks"] = len(ts)
    st["done"] = sum(1 for t in ts if t.get("status") == "done")
    st["inProgress"] = sum(1 for t in ts if t.get("status") == "in-progress")
    st["notStarted"] = sum(1 for t in ts if t.get("status") == "not-started")
    if "todo" in st:
        st["todo"] = sum(1 for t in ts if t.get("status") == "todo")


def main():
    write = "--write" in sys.argv
    total_add = total_done = 0
    for app in hub.load_apps():
        path = os.path.join(hub.APPS, app["_slug"] + ".json")
        raw = json.load(open(path, encoding="utf-8"))
        tasks = raw.setdefault("allTasks", [])
        have = {t["name"]: t for t in tasks if LABEL in (t.get("labels") or [])}
        add, done = [], []
        for name, t in wanted(app).items():
            old = have.get(name)
            if t is None:
                if old and old.get("status") != "done":
                    old["status"] = "done"
                    done.append(name)
            elif not old:
                tasks.append(t)
                add.append(name)
        total_add += len(add)
        total_done += len(done)
        print("%-26s +%-3d 완료 %d" % (raw.get("name") or app["_slug"], len(add), len(done)))
        if write and (add or done):
            recount(raw)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(raw, f, ensure_ascii=False, indent=2)
                f.write("\n")
    print("\n합계: 새 할 일 %d개 · 완료로 옮김 %d개%s" % (total_add, total_done, "" if write else " (미리보기 — --write 로 저장)"))


if __name__ == "__main__":
    main()
