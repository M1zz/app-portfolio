#!/usr/bin/env python3
"""
블랙프라이데이 동안 판매 중인 버전의 프로모션 텍스트를 세일 문구로 바꾸고, 끝나면 되돌린다.
프로모션 텍스트는 심사 없이 바로 바뀐다.

  python3 promo.py --sale [--dry]     # 11/27 17:00 KST(태평양 0시): 원래 문구를 promo-originals.json 에 적고 세일 문구로
  python3 promo.py --restore [--dry]  # 12/4 17:00 KST: 지금 세일 문구인 칸만 원래 문구로

판매 중인 버전은 실행하는 그 순간에 찾는다 — 그 사이 새 버전이 나가도 그 버전에 건다.
되돌릴 때는 세일 문구가 그대로인 칸만 되돌린다(그 사이 사람이 고친 칸은 건드리지 않는다).
"""
import importlib.util, json, os, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ap", os.path.join(HERE, "..", "asc-products.py"))
ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)

SALE = json.load(open(os.path.join(HERE, "sale-text.json"), encoding="utf-8"))
ORIG = os.path.join(HERE, "promo-originals.json")
LABEL = {"com.leeo.blackfriday-promo-sale", "com.leeo.blackfriday-promo-restore"}


def vkey(s):
    return [int(x) for x in re.findall(r"\d+", s)]


def live_versions(asc, aid):
    """플랫폼마다 판매 중인 버전 중 가장 높은 것."""
    best = {}
    for v in asc.all(f"/v1/apps/{aid}/appStoreVersions?limit=50&fields[appStoreVersions]=versionString,appStoreState,platform"):
        a = v["attributes"]
        if a["appStoreState"] != "READY_FOR_SALE":
            continue
        p = a["platform"]
        if p not in best or vkey(a["versionString"]) > vkey(best[p][1]):
            best[p] = (v["id"], a["versionString"])
    return best


def main():
    mode = "sale" if "--sale" in sys.argv else "restore" if "--restore" in sys.argv else None
    if not mode:
        sys.exit(__doc__)
    dry = "--dry" in sys.argv
    asc = ap.ASC()
    apps = {}
    for t in json.load(open(os.path.join(HERE, "targets.json"), encoding="utf-8")):
        apps.setdefault(t["app"], t["appId"])
    # 무지개 공방은 곧 App Store 에서 내려간다(SunsetNotice) — 새 구독을 부르지 않는다.
    apps.pop("무지개 공방", None)
    orig = json.load(open(ORIG, encoding="utf-8")) if os.path.exists(ORIG) else {}
    sale_values = set(SALE.values())
    changed = skipped = 0
    for name, aid in apps.items():
        for plat, (vid, vs) in live_versions(asc, aid).items():
            for loc in asc.all(f"/v1/appStoreVersions/{vid}/appStoreVersionLocalizations?limit=50&fields[appStoreVersionLocalizations]=locale,promotionalText"):
                lc, cur = loc["attributes"]["locale"], loc["attributes"]["promotionalText"] or ""
                key = f"{aid}|{plat}|{lc}"
                if mode == "sale":
                    new = SALE.get(lc) or SALE["en-US"]
                    if cur == new:
                        continue
                    if cur not in sale_values:
                        orig[key] = cur
                else:
                    if cur not in sale_values:
                        skipped += 1
                        continue
                    new = orig.get(key)
                    if new is None:
                        print(f"  ! {name} {plat} {lc}: 원래 문구 없음 — 그대로 둠", flush=True)
                        continue
                if not dry:
                    asc.call("PATCH", f"/v1/appStoreVersionLocalizations/{loc['id']}",
                             {"data": {"type": "appStoreVersionLocalizations", "id": loc["id"], "attributes": {"promotionalText": new}}})
                    time.sleep(0.5)
                changed += 1
            print(f"── {name} {plat} {vs} 끝", flush=True)
            if mode == "sale" and not dry:
                json.dump(orig, open(ORIG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"모두 끝 · {mode} · 바꾼 칸 {changed} · 건너뜀 {skipped} · calls {asc.calls}", flush=True)
    if not dry:
        label = f"com.leeo.blackfriday-promo-{mode}"
        plist = os.path.expanduser(f"~/Library/LaunchAgents/{label}.plist")
        if os.path.exists(plist):
            os.system(f"launchctl unload '{plist}'; rm -f '{plist}'")


if __name__ == "__main__":
    main()
