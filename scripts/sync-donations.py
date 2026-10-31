#!/usr/bin/env python3
"""앱 소스에서 후원(팁) 정보를 모아 scripts/donations.json 의 apps 를 새로 쓴다.

사용법:
  python3 scripts/sync-donations.py

소스는 sync-service-maturity.py 와 같은 방법(번들 ID → .xcodeproj)으로 찾는다. 앱마다 본다:
  상품   Swift 문자열 속 팁 상품 ID(…tip.small 등) + .storekit 의 표시 이름 · 가격(달러)
  가격   App Store 실데이터(앱 JSON price.iapItems)에 팁 상품이 보이면 그 원화 가격
  부탁   LeeoTipAsk · 직접 만든 부탁 카드가 있는가
  이름   팁 화면에 '고마운 사람들'(LeeoTipJarConfig thanksPage)을 넘겼는가
⚠️ 손으로 적은 설명(where · ask · cadence · gives 에 manual: true)은 덮어쓰지 않는다 — 상품만 새로 맞춘다.
   rewardPlan · checkedAt 외의 맨 위 키도 그대로 둔다.
"""
import glob
import importlib.util
import json
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "scripts/donations.json")
spec = importlib.util.spec_from_file_location("smm", os.path.join(ROOT, "scripts/sync-service-maturity.py"))
smm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smm)

TIP_ID = re.compile(r'"((?:[A-Za-z0-9_-]+\.){2,}(?:tip|Coffee)(?:\.[A-Za-z0-9_]+)?|(?:[A-Za-z0-9_-]+\.){2,}tip[A-Za-z0-9]*)"')
ASK = re.compile(r"LeeoTipAsk|TipAsk\w*|tipCardDismissedAt")
THANKS = re.compile(r"thanksPage\s*:")
PLACEHOLDER = re.compile(r"com\.example\.|yourcompany")
SIZE_KR = {"small": "커피 한 잔", "medium": "간식 한 번", "large": "든든한 한 끼"}
ORDER = {"small": 0, "medium": 1, "large": 2}


def size_of(pid):
    tail = pid.rsplit(".", 1)[-1].lower()
    return tail if tail in SIZE_KR else None


def storekit_products(root):
    out = {}
    for dp, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in smm.SKIP_DIRS and not d.startswith(".")]
        for fn in fs:
            if not fn.endswith(".storekit"):
                continue
            try:
                j = json.load(open(os.path.join(dp, fn), encoding="utf-8"))
            except (OSError, ValueError):
                continue
            for p in j.get("products", []):
                ko = next((l.get("displayName") for l in p.get("localizations", []) if l.get("locale", "").startswith("ko")), None)
                out[p.get("productID")] = {"type": p.get("type"), "price": p.get("displayPrice"), "ko": ko}
    return out


def store_price(app, size):
    """App Store 에 보이는 팁 상품의 원화 가격. 이름에 small/medium/large 나 LeeoKit 칸 이름이 들어 있으면 짝짓는다."""
    for it in (app.get("price") or {}).get("iapItems") or []:
        n = it["name"].lower()
        if ("tip" in n or "응원" in n or "커피" in n or "간식" in n or "한 끼" in n) and (size in n or SIZE_KR[size] in it["name"]):
            return it["price"]
    return None


def scan(root, exclude):
    ids, ask, thanks = set(), False, False
    for path in smm.swift_files(root, exclude):
        if re.search(r"Tests?/|UITests", path):
            continue
        text = open(path, errors="ignore").read()
        for m in TIP_ID.findall(text):
            if not m.lower().startswith("tip."):
                ids.add(m)
        ask = ask or bool(ASK.search(text))
        thanks = thanks or bool(THANKS.search(text))
    return ids, ask, thanks


def main():
    data = json.load(open(PATH, encoding="utf-8"))
    old = data.get("apps") or {}
    projects = smm.find_projects()
    apps = []
    for path in sorted(glob.glob(os.path.join(smm.APPS, "*.json"))):
        a = json.load(open(path, encoding="utf-8"))
        if (a.get("lifecycle") or {}).get("stage") == 0 or not a.get("appStoreId"):
            continue
        hits = projects.get((a.get("bundleId") or "").lower(), [])
        apps.append((os.path.basename(path)[:-5], a, min((h[0] for h in hits), key=len) if hits else None))
    roots = {r for _, _, r in apps if r}

    new = {}
    for slug, a, root in apps:
        if not root:
            continue
        ids, ask, thanks = scan(root, {r for r in roots if r != root and r.startswith(root + os.sep)})
        if not ids:
            continue
        sk = storekit_products(root)
        products = []
        for pid in sorted(ids, key=lambda p: (ORDER.get(size_of(p) or "", 9), p)):
            info = sk.get(pid) or {}
            if info.get("type") == "NonConsumable":
                continue  # 옛 비소모성 '커피'(돈꼬마트) 같은 것 — 팁이 아니라 옛 상품이다
            size = size_of(pid)
            krw = store_price(a, size) if size else None
            usd = info.get("price")
            products.append({
                "productId": pid,
                "label": info.get("ko") or SIZE_KR.get(size) or pid.rsplit(".", 1)[-1],
                "price": krw,
                "usd": ("$%s" % usd) if usd and not str(usd).isdigit() else None,
                "inStore": bool(krw),
            })
            if usd and str(usd).isdigit() and not krw:
                products[-1]["price"] = "￦{:,}".format(int(usd))  # .storekit 에 원화로 적힌 앱(두번알림)
        placeholder = any(PLACEHOLDER.search(p["productId"]) for p in products)
        prev = old.get(slug) or {}
        entry = {
            "status": "code-only" if placeholder else "live",
            "products": products,
            "where": ["설정 ▸ 개발자 응원하기"],
            "ask": "앱으로 얻은 것이 숫자로 보이는 순간에 드물게 (LeeoKit 부탁 규칙)" if ask else None,
            "cadence": "물으면 60일 쉬고, 낸 사람은 180일, '다음에' 세 번이면 다시 묻지 않음" if ask else None,
            "gives": "상품 ID 가 예시 값(com.example)이라 스토어에 올릴 수 없음" if placeholder else "기능은 열지 않음 — 순수 응원",
            "thanksButton": thanks,
        }
        if prev.get("manual"):
            for k in ("where", "ask", "cadence", "gives", "manual"):
                entry[k] = prev.get(k)
            if prev.get("products") and slug == "donkko-mart":
                entry["products"] = prev["products"]  # 돈꼬마트는 스토어 원화 가격을 손으로 맞춰 두었다
        new[slug] = entry

    data["apps"] = new
    data["checkedAt"] = date.today().isoformat()
    with open(PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    live = sum(1 for e in new.values() if e["status"] == "live")
    print("후원 앱 %d개 (받는 중 %d · 코드만 %d) · 부탁 %d · 고마운 사람들 버튼 %d" % (
        len(new), live, len(new) - live, sum(1 for e in new.values() if e["ask"]),
        sum(1 for e in new.values() if e["thanksButton"])))


if __name__ == "__main__":
    main()
