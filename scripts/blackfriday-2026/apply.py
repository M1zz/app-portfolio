"""블랙프라이데이: 신규 구독 첫 기간 80% 할인 (2026-11-27 ~ 12-04).
기존 무기한 첫 구독 오퍼는 11-27 에 끝내고, 그 값은 restore.json 에 남긴다.
Apple 은 한 나라에 예약 오퍼를 하나만 받으므로 12-04 원복은 세일이 시작된 뒤 restore.py 가 건다.
다시 돌려도 이미 한 나라는 건너뛴다. 사용: bf_apply.py [--only <subId>] [--dry]"""
import importlib.util, os, sys, json, time
HERE=os.path.dirname(os.path.abspath(__file__))
root="/Users/hyunholee/Documents/workspace/웹페이지/app-portfolio"
spec=importlib.util.spec_from_file_location("ascp", os.path.join(root,"scripts/asc-products.py")); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
asc=m.ASC(); DRY="--dry" in sys.argv
ONLY=sys.argv[sys.argv.index("--only")+1] if "--only" in sys.argv else None
S,E="2026-11-27","2026-12-04"
MODE={"ONE_WEEK":("PAY_AS_YOU_GO","ONE_WEEK"),"ONE_MONTH":("PAY_AS_YOU_GO","ONE_MONTH"),"ONE_YEAR":("PAY_UP_FRONT","ONE_YEAR")}
_c=asc.call
def call(*a,**k):
    time.sleep(1.1)          # 시간당 ~3000 — 다른 세션(DeployBar) 몫을 남긴다
    return _c(*a,**k)
asc.call=call
def offer(sub,terr,pp,mode,dur,start,end):
    body={"data":{"type":"subscriptionIntroductoryOffers","attributes":{"duration":dur,"offerMode":mode,"numberOfPeriods":1,"startDate":start,"endDate":end},
      "relationships":{"subscription":{"data":{"type":"subscriptions","id":sub}},"territory":{"data":{"type":"territories","id":terr}}}}}
    if pp: body["data"]["relationships"]["subscriptionPricePoint"]={"data":{"type":"subscriptionPricePoints","id":pp}}
    if not DRY: asc.call("POST","/v1/subscriptionIntroductoryOffers",body)
targets=json.load(open(os.path.join(HERE,"targets.json")))
RP=os.path.join(HERE,"restore.json")
restore=json.load(open(RP)) if os.path.exists(RP) else {}
for t in targets:
    if ONLY and t["sub"]!=ONLY: continue
    sub=t["sub"]; mode,dur=MODE[t["period"]]
    # 11-27 에 실제로 매겨질 한국 가격
    pr=asc.call("GET",f"/v1/subscriptions/{sub}/prices?filter[territory]=KOR&include=subscriptionPricePoint&limit=50")
    pts={i["id"]:float(i["attributes"]["customerPrice"]) for i in pr.get("included",[])}
    rows=[(r["attributes"].get("startDate") or "0000",pts[r["relationships"]["subscriptionPricePoint"]["data"]["id"]]) for r in pr["data"]]
    krw=max((r for r in rows if r[0]<=S))[1]
    kp=asc.all(f"/v1/subscriptions/{sub}/pricePoints?filter[territory]=KOR&limit=8000")
    p=min(kp,key=lambda p:abs(float(p["attributes"]["customerPrice"])-krw*0.2))
    sale=float(p["attributes"]["customerPrice"])
    eq=asc.call("GET",f"/v1/subscriptionPricePoints/{p['id']}/equalizations?limit=200&include=territory")
    terr={"KOR":p["id"]}
    for e in eq["data"]: terr[e["relationships"]["territory"]["data"]["id"]]=e["id"]
    # 기존 오퍼
    offs=asc.all(f"/v1/subscriptions/{sub}/introductoryOffers?limit=200&include=territory,subscriptionPricePoint")
    have_bf={o["relationships"]["territory"]["data"]["id"] for o in offs if o["attributes"].get("startDate")==S}
    have_after={o["relationships"]["territory"]["data"]["id"] for o in offs if o["attributes"].get("startDate")==E}
    old=[o for o in offs if o["attributes"].get("startDate") not in (S,E) and (o["attributes"].get("endDate") in (None,"") or o["attributes"]["endDate"]>=S)]
    print(f"{t['app']} {t['pid']} ₩{krw:,.0f} → ₩{sale:,.0f} ({round(100-sale/krw*100)}% 할인) · 나라 {len(terr)} · 이미 {len(have_bf)} · 기존 오퍼 끝낼 것 {len(old)}",flush=True)
    keep=restore.setdefault(sub,{})
    for o in old:   # 원래 값을 남긴다 (원복용)
        a=o["attributes"]; pp=(o["relationships"].get("subscriptionPricePoint") or {}).get("data")
        keep[o["relationships"]["territory"]["data"]["id"]]={"mode":a["offerMode"],"dur":a["duration"],"n":a.get("numberOfPeriods") or 1,"pp":pp and pp["id"]}
    if keep and not DRY: json.dump(restore,open(RP,"w"),indent=1)
    for o in old:   # 1) 기존을 11-27 에 끝낸다
        if o["attributes"].get("endDate")==S: continue
        if not DRY: asc.call("PATCH",f"/v1/subscriptionIntroductoryOffers/{o['id']}",{"data":{"type":"subscriptionIntroductoryOffers","id":o["id"],"attributes":{"endDate":S}}})
    for c,pp in terr.items():   # 2) 세일
        if c not in have_bf: offer(sub,c,pp,mode,dur,S,E)
    print("  ✓ 끝 · calls",asc.calls,flush=True)
print("모두 끝 · calls",asc.calls)
