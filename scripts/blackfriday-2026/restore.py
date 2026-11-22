"""세일이 시작된 뒤(11-27 PT 이후) 돌린다: restore.json 의 원래 첫 구독 오퍼를 12-04 부터 무기한으로 다시 건다.
이미 건 나라는 건너뛴다. 끝나면 launchd 예약을 스스로 지운다."""
import importlib.util, os, sys, json, time, subprocess
HERE=os.path.dirname(os.path.abspath(__file__))
root="/Users/hyunholee/Documents/workspace/웹페이지/app-portfolio"
spec=importlib.util.spec_from_file_location("ascp", os.path.join(root,"scripts/asc-products.py")); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
asc=m.ASC(); E="2026-12-04"
restore=json.load(open(os.path.join(HERE,"restore.json")))
for sub,terrs in restore.items():
    offs=asc.all(f"/v1/subscriptions/{sub}/introductoryOffers?limit=200&include=territory")
    done={o["relationships"]["territory"]["data"]["id"] for o in offs if o["attributes"].get("startDate")==E}
    for c,o in terrs.items():
        if c in done: continue
        rel={"subscription":{"data":{"type":"subscriptions","id":sub}},"territory":{"data":{"type":"territories","id":c}}}
        if o["pp"]: rel["subscriptionPricePoint"]={"data":{"type":"subscriptionPricePoints","id":o["pp"]}}
        time.sleep(1.1)
        asc.call("POST","/v1/subscriptionIntroductoryOffers",{"data":{"type":"subscriptionIntroductoryOffers",
            "attributes":{"duration":o["dur"],"offerMode":o["mode"],"numberOfPeriods":o["n"],"startDate":E},"relationships":rel}})
    print(sub,"원복",len(terrs)-len(done),"개 나라",flush=True)
print("✅ 원복 끝 · calls",asc.calls)
plist=os.path.expanduser("~/Library/LaunchAgents/com.leeo.blackfriday-restore.plist")
if os.path.exists(plist):
    subprocess.run(["launchctl","unload",plist]); os.remove(plist)
