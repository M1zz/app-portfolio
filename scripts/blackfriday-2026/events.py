#!/usr/bin/env python3
"""
블랙프라이데이 앱 내 이벤트(App Store '이벤트' 카드)를 앱마다 만든다.

  python3 events.py [--only <appId>] [--media <폴더>]   # 만들기 · 채우기(이미 있는 건 건너뛰어 다시 돌려도 된다)
  python3 events.py --submit [--only <appId>]          # 심사 제출

  · 이름 · 설명: event-text.json (언어마다 [이름 ≤30, 짧은 설명 ≤50, 긴 설명 ≤120])
  · 그림: <media>/<appId>-card.png(1920×1080) · <appId>-detail.png(1080×1920)
  · 언어: 판매 중인 버전의 언어 전부
  · 앱으로 들어가는 링크: <번들 ID 소문자>://paywall (LeeoKit LeeoPaywallLink, v3.47)
  · 기간: 11/27 00:00 ~ 12/4 00:00 태평양 시간, 11/24 부터 '곧 시작' 으로 보인다
"""
import importlib.util, json, os, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ap", os.path.join(HERE, "..", "asc-products.py"))
ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)
sys.path.insert(0, HERE)
from promo import live_versions

REF = "Black Friday 2026"
TEXT = json.load(open(os.path.join(HERE, "event-text.json"), encoding="utf-8"))
SCHEDULE = {"publishStart": "2026-11-24T08:00:00Z", "eventStart": "2026-11-27T08:00:00Z", "eventEnd": "2026-12-04T08:00:00Z"}


def arg(flag, default=None):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def upload(asc, loc_id, path, kind):
    data = open(path, "rb").read()
    r = asc.call("POST", "/v1/appEventScreenshots", {"data": {"type": "appEventScreenshots",
        "attributes": {"fileName": os.path.basename(path), "fileSize": len(data), "appEventAssetType": kind},
        "relationships": {"appEventLocalization": {"data": {"type": "appEventLocalizations", "id": loc_id}}}}})
    sid = r["data"]["id"]
    for op in r["data"]["attributes"]["uploadOperations"]:
        req = urllib.request.Request(op["url"], data=data[op["offset"]:op["offset"] + op["length"]], method=op["method"],
                                     headers={h["name"]: h["value"] for h in op["requestHeaders"]})
        urllib.request.urlopen(req, timeout=120).read()
    asc.call("PATCH", f"/v1/appEventScreenshots/{sid}", {"data": {"type": "appEventScreenshots", "id": sid, "attributes": {"uploaded": True}}})


def find_event(asc, aid):
    for e in asc.all(f"/v1/apps/{aid}/appEvents?limit=50"):
        if e["attributes"]["referenceName"] in (REF, "BF2026 probe"):
            return e
    return None


def build(asc, name, aid, media, terr):
    a = asc.call("GET", f"/v1/apps/{aid}?fields[apps]=primaryLocale,bundleId")["data"]["attributes"]
    primary = a["primaryLocale"]
    locales = set()
    for vid, _ in live_versions(asc, aid).values():
        locales |= {l["attributes"]["locale"] for l in asc.all(f"/v1/appStoreVersions/{vid}/appStoreVersionLocalizations?limit=50&fields[appStoreVersionLocalizations]=locale")}
    locales = [l for l in sorted(locales) if l in TEXT]
    attrs = {"referenceName": REF, "badge": "SPECIAL_EVENT", "primaryLocale": primary, "priority": "HIGH",
             "purpose": "ATTRACT_NEW_USERS", "deepLink": f"{a['bundleId'].lower()}://paywall",
             "territorySchedules": [dict(territories=terr, **SCHEDULE)]}
    ev = find_event(asc, aid)
    if ev is None:
        ev = asc.call("POST", "/v1/appEvents", {"data": {"type": "appEvents", "attributes": attrs,
                      "relationships": {"app": {"data": {"type": "apps", "id": aid}}}}})["data"]
    elif ev["attributes"]["eventState"] == "DRAFT":
        asc.call("PATCH", f"/v1/appEvents/{ev['id']}", {"data": {"type": "appEvents", "id": ev["id"], "attributes": attrs}})
    eid = ev["id"]
    have = {l["attributes"]["locale"]: l for l in asc.all(f"/v1/appEvents/{eid}/localizations?limit=50")}
    for lc in locales:
        n, s, lg = TEXT[lc]
        t = {"name": n, "shortDescription": s, "longDescription": lg}
        if lc in have:
            loc = have[lc]
            if any(loc["attributes"].get(k) != v for k, v in t.items()):
                asc.call("PATCH", f"/v1/appEventLocalizations/{loc['id']}", {"data": {"type": "appEventLocalizations", "id": loc["id"], "attributes": t}})
        else:
            loc = asc.call("POST", "/v1/appEventLocalizations", {"data": {"type": "appEventLocalizations", "attributes": dict(locale=lc, **t),
                           "relationships": {"appEvent": {"data": {"type": "appEvents", "id": eid}}}}})["data"]
        shots = {x["attributes"]["appEventAssetType"] for x in asc.all(f"/v1/appEventLocalizations/{loc['id']}/appEventScreenshots?limit=10")}
        for kind, suffix in (("EVENT_CARD", "card"), ("EVENT_DETAILS_PAGE", "detail")):
            if kind not in shots:
                upload(asc, loc["id"], os.path.join(media, f"{aid}-{suffix}.png"), kind)
        print(f"  {lc} 끝", flush=True)
        time.sleep(0.3)
    print(f"── {name} 끝 · {len(locales)}개 언어 · {eid}", flush=True)
    return eid


LINK = json.load(open(os.path.join(HERE, "link-versions.json"), encoding="utf-8"))


def vkey(v):
    return [int(x) for x in v.split(".")]


def submit(asc, name, aid):
    live = live_versions(asc, aid)
    need = LINK.get(aid)
    # 링크가 든 버전이 나간 플랫폼에서만 낸다 — 링크가 없는 앱에서 이벤트를 누르면 아무 일도 안 생긴다.
    ok = [p for p, (_, v) in live.items() if need and vkey(v) >= vkey(need)]
    if not ok:
        return print(f"  · {name}: 링크 든 버전({need}) 아직 출시 전 — 지금 {dict((p, v) for p, (_, v) in live.items())}", flush=True)
    ev = find_event(asc, aid)
    if not ev:
        return print(f"  ! {name}: 이벤트 없음", flush=True)
    if ev["attributes"]["eventState"] != "READY_FOR_REVIEW" and ev["attributes"]["eventState"] != "DRAFT":
        return print(f"── {name} 이미 {ev['attributes']['eventState']}", flush=True)
    # 이벤트만 담은 새 제출을 만든다. 같은 플랫폼에 열린 초안이 있으면 거기에 섞이지 않게 건너뛴다.
    plat = "IOS" if "IOS" in ok else ok[0]
    drafts = asc.call("GET", f"/v1/reviewSubmissions?filter[app]={aid}&filter[platform]={plat}&filter[state]=READY_FOR_REVIEW")["data"]
    # 비어 있는 초안은 그대로 쓴다. 다른 것이 담긴 초안에는 섞지 않는다(그것까지 심사에 나간다).
    empty = [d for d in drafts if not asc.call("GET", f"/v1/reviewSubmissions/{d['id']}/items")["data"]]
    if drafts and not empty:
        return print(f"  ! {name}: {plat} 에 다른 것이 담긴 제출 초안이 있어 건너뜀 ({drafts[0]['id']})", flush=True)
    sub = empty[0] if empty else asc.call("POST", "/v1/reviewSubmissions", {"data": {"type": "reviewSubmissions", "attributes": {"platform": plat},
                   "relationships": {"app": {"data": {"type": "apps", "id": aid}}}}})["data"]
    asc.call("POST", "/v1/reviewSubmissionItems", {"data": {"type": "reviewSubmissionItems", "relationships": {
        "reviewSubmission": {"data": {"type": "reviewSubmissions", "id": sub["id"]}},
        "appEvent": {"data": {"type": "appEvents", "id": ev["id"]}}}}})
    asc.call("PATCH", f"/v1/reviewSubmissions/{sub['id']}", {"data": {"type": "reviewSubmissions", "id": sub["id"], "attributes": {"submitted": True}}})
    print(f"── {name} 제출 끝 · {plat} · {sub['id']}", flush=True)


def main():
    asc = ap.ASC()
    apps = {}
    for t in json.load(open(os.path.join(HERE, "targets.json"), encoding="utf-8")):
        apps.setdefault(t["app"], t["appId"])
    # 무지개 공방은 곧 App Store 에서 내려간다(SunsetNotice) — 새 구독을 부르지 않는다.
    apps.pop("무지개 공방", None)
    only = arg("--only")
    if only:
        apps = {n: a for n, a in apps.items() if a == only}
    if "--submit" in sys.argv:
        print(f"━━ {time.strftime('%m/%d %H:%M')} 제출 돌기", flush=True)
        for n, a in apps.items():
            try:
                submit(asc, n, a)
            except SystemExit as e:
                print(f"  ! {n}: {str(e)[:400]}", flush=True)
        # 다 냈거나 세일이 끝나면 30분마다 도는 예약(launchd)을 스스로 지운다.
        left = [n for n, a in apps.items() if (find_event(asc, a) or {}).get("attributes", {}).get("eventState") in (None, "DRAFT", "READY_FOR_REVIEW")]
        print(f"남은 앱 {len(left)}: {' · '.join(left)} · calls {asc.calls}", flush=True)
        plist = os.path.expanduser("~/Library/LaunchAgents/com.leeo.blackfriday-events.plist")
        if (not left or time.strftime("%Y-%m-%d") >= "2026-12-03") and os.path.exists(plist):
            os.system(f"launchctl unload '{plist}'; rm -f '{plist}'")
        return
    media = arg("--media", os.path.join(HERE, "media"))
    terr = [t["id"] for t in asc.all("/v1/territories?limit=200")]
    for n, a in apps.items():
        build(asc, n, a, media, terr)
    print(f"모두 끝 · calls {asc.calls}")


if __name__ == "__main__":
    main()
