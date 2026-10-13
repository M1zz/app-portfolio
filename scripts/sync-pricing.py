#!/usr/bin/env python3
"""앱별 유료화 모델(price)을 App Store 실데이터와 소스 코드에서 확인해 앱 JSON에 기록한다.

사용법:
  python3 scripts/sync-pricing.py

스토어가 진실이다. 코드는 '준비돼 있지만 아직 스토어에 없는 것'을 찾는 데만 쓴다.

  store  iTunes Lookup 의 가격 + 제품 페이지의 titleOfferDisplayProperties(hasInAppPurchases)
         + 정보 칸 '앱 내 구입'(<dt>) 아래의 상품명·가격 목록
         ⚠️ 페이지에는 관련 앱 카드도 '앱 내 구입'을 달고 나오므로, 앱 자신의 값은
            titleOfferDisplayProperties 에서만 읽는다.
         ⚠️ apps.apple.com/kr/app/id… 는 301 로 넘어가므로 리다이렉트를 따라가야 한다.
  code   번들 ID 로 찾은 소스에서 .storekit 상품 · StoreKit 결제 API · 구독/스토어 화면 · 광고 SDK

pricingModel:
  free · paid · freemium(무료+인앱결제) · freemium-subscription(무료+구독 포함)
  · paid+iap · paid+subscription
구독 여부는 스토어 상품명(weekly·monthly·yearly·주간·월간·연간·구독)으로 판단한다.
상품 목록을 못 읽었을 때만 .storekit 구독 그룹·구독 화면으로 짐작한다.

⚠️ 앱 JSON을 고쳐 쓰므로 sync-lifecycle · sync-global-reach · sync-service-maturity 와 동시에 돌리지 말 것.
"""
import glob
import html
import importlib.util
import json
import os
import re
import time
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "projects/PortfolioCEO/PortfolioCEO/Data/apps")
ARTIST_ID = "1502508537"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.4 Safari/605.1.15")
SUB_WORDS = re.compile(r"week|month|year|annual|subscri|주간|월간|연간|구독|1개월|12개월", re.I)
ADS = re.compile(r"\bimport (GoogleMobileAds|AppLovinSDK|UnityAds|FBAudienceNetwork)\b|GADMobileAds")
STOREKIT = re.compile(r"Product\.products\(for|\.purchase\(|Transaction\.(currentEntitlements|updates)"
                      r"|SKPaymentQueue|Purchases\.(shared|configure)")
SUB_UI = re.compile(r"SubscriptionStoreView|\.subscriptionStatus|Product\.SubscriptionInfo")
STORE_UI = re.compile(r"\bStoreView\(|\bProductView\(")

# 소스 찾기는 서비스 숙성도 스크립트와 같은 규칙을 쓴다.
_spec = importlib.util.spec_from_file_location(
    "maturity", os.path.join(ROOT, "scripts/sync-service-maturity.py"))
maturity = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(maturity)


def get_json(url):
    for attempt in range(5):
        try:
            return json.load(urllib.request.urlopen(url, timeout=30))
        except Exception:
            time.sleep(10 * (attempt + 1))
    raise RuntimeError("조회 실패: " + url)


def get_page(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9"})
    for attempt in range(4):
        try:
            return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
        except Exception:
            time.sleep(5 * (attempt + 1))
    return None


def store_page(app_id, country):
    """제품 페이지 → (hasInAppPurchases, [{name, price}]) · 실패하면 (None, [])."""
    page = get_page("https://apps.apple.com/%s/app/id%s" % (country, app_id))
    if not page:
        return None, []
    i = page.find('"titleOfferDisplayProperties"')
    m = re.search(r'"hasInAppPurchases":(true|false)', page[i:i + 1500]) if i >= 0 else None
    has = (m.group(1) == "true") if m else None
    items = []
    for block in re.findall(r"<dt[^>]*>\s*앱 내 구입\s*</dt>\s*<dd>(.*?)</dd>", page, re.S):
        for name, price in re.findall(
                r'class="text-pair[^"]*"><span>(.*?)</span>\s*<span>(.*?)</span>', block, re.S):
            items.append({"name": html.unescape(name).strip(), "price": html.unescape(price).strip()})
    return has, items


def scan_code(root, exclude_roots):
    """소스에서 결제 준비 상태를 읽는다."""
    products = []
    for path in glob.glob(os.path.join(root, "**/*.storekit"), recursive=True):
        if any(path.startswith(x) for x in exclude_roots):
            continue
        try:
            sk = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for p in sk.get("products", []):
            products.append({"id": p.get("productID"), "type": p.get("type", "").lower()})
        for g in sk.get("subscriptionGroups", []):
            for p in g.get("subscriptions", []):
                products.append({"id": p.get("productID"), "type": "subscription",
                                 "period": p.get("recurringSubscriptionPeriod")})
    flags = {"storeKit": False, "subscriptionUI": False, "storeUI": False, "ads": False}
    for path in maturity.swift_files(root, exclude_roots):
        try:
            text = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        flags["storeKit"] |= bool(STOREKIT.search(text))
        flags["subscriptionUI"] |= bool(SUB_UI.search(text))
        flags["storeUI"] |= bool(STORE_UI.search(text))
        flags["ads"] |= bool(ADS.search(text))
    seen, uniq = set(), []
    for p in products:
        if p["id"] and p["id"] not in seen:
            seen.add(p["id"])
            uniq.append(p)
    return dict(flags, products=uniq)


def model(is_free, has_iap, subscription):
    if not has_iap:
        return "free" if is_free else "paid"
    if is_free:
        return "freemium-subscription" if subscription else "freemium"
    return "paid+subscription" if subscription else "paid+iap"


def main():
    today = date.today().isoformat()
    kr = {}
    res = get_json("https://itunes.apple.com/lookup?id=%s&entity=software&country=kr&limit=200" % ARTIST_ID)
    for r in res.get("results", []):
        if r.get("wrapperType") == "software":
            kr[str(r["trackId"])] = r
    projects = maturity.find_projects()

    def source_root(app):
        hits = projects.get((app.get("bundleId") or "").lower(), [])
        return min((h[0] for h in hits), key=len) if hits else None

    app_roots = set()
    for path in glob.glob(os.path.join(APPS, "*.json")):
        root = source_root(json.load(open(path, encoding="utf-8")))
        if root:
            app_roots.add(root)

    for path in sorted(glob.glob(os.path.join(APPS, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            app = json.load(fh)
        slug = os.path.basename(path)[:-5]
        sid = str(app.get("appStoreId") or "")
        if not sid or (app.get("lifecycle") or {}).get("stage") == 0:
            continue
        country, r = "kr", kr.get(sid)
        if r is None:
            us = get_json("https://itunes.apple.com/lookup?id=%s&country=us" % sid)
            r = us["results"][0] if us.get("results") else None
            country = "us"
        if r is None:
            print("  %-24s 스토어에 없음 — 건너뜀" % slug)
            continue

        has_iap, items = store_page(sid, country)
        time.sleep(1)
        price = r.get("price") or 0
        is_free = price == 0

        code = None
        root = source_root(app)
        if root:
            exclude = {x for x in app_roots if x != root and x.startswith(root + os.sep)}
            code = scan_code(root, exclude)

        if has_iap is None:  # 페이지 조회 실패 — 이전 값 유지
            has_iap = (app.get("price") or {}).get("hasInAppPurchases", False)
            items = (app.get("price") or {}).get("iapItems", [])
        # 스토어 상품명이 기준. 상품 목록을 못 읽었을 때만 코드로 짐작한다
        # (코드에는 아직 스토어에 올리지 않은 구독 상품이 남아 있는 경우가 많다).
        if items:
            subscription = any(SUB_WORDS.search(it["name"]) for it in items)
        else:
            subscription = bool(code and has_iap and (
                code["subscriptionUI"] or any(p["type"] == "subscription" for p in code["products"])))

        p = {"isFree": is_free}
        if not is_free:
            p["priceKRW" if country == "kr" else "priceUSD"] = int(price) if country == "kr" else price
        p.update({"pricingModel": model(is_free, has_iap, subscription),
                  "hasInAppPurchases": has_iap})
        if items:
            p["iapItems"] = items
        if code is not None:
            p["code"] = code
            ready = bool(code["products"] or code["storeKit"])
            if ready and not has_iap:
                p["gap"] = "코드에 결제가 있지만 스토어에 인앱결제 상품이 없음"
            elif has_iap and not ready:
                p["gap"] = "스토어에 인앱결제가 있지만 소스에서 결제 코드를 찾지 못함"
        p["store"] = country
        p["evaluatedAt"] = today

        before = (app.get("price") or {}).get("pricingModel")
        app["price"] = p
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(app, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        mark = "" if before == p["pricingModel"] else "  ★ %s→%s" % (before, p["pricingModel"])
        print("  %-24s %-22s %-8s IAP %d%s%s" % (
            slug, p["pricingModel"], r.get("formattedPrice"), len(items),
            "  ⚠ " + p["gap"] if p.get("gap") else "", mark))


if __name__ == "__main__":
    main()
