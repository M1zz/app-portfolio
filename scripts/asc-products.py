#!/usr/bin/env python3
"""
앱 레포의 .storekit 에 적힌 상품을 App Store Connect 에 만든다 (없는 것만).

  python3 scripts/asc-products.py <slug> <레포 경로>            # 무엇을 만들지 보기
  python3 scripts/asc-products.py <slug> <레포 경로> --apply    # 만들기

원본
  · 상품 ID · 종류 · 구독 그룹 · 기간 · 단계 · 가족 공유 · 표시 이름: 레포의 .storekit
  · 가격: scripts/paywall-plans.json 의 그 앱 설계안(칸 · 기간 → 원화 · 달러). 한국을 기준 가격으로 두고
    다른 나라는 Apple 환산값, 미국만 설계안 달러로 따로 맞춘다.
  · 심사용 스크린샷: 레포 docs/screenshots 의 한국어 iPhone(맥 앱이면 Mac) 그림 한 장
이미 있는 상품은 건드리지 않는다(이름 · 가격도). 팁(tip.*) · 선물(gift.*) · 언제나 평생 패스(forever*)는 만들지 않는다.
키: ~/Documents/workspace/fastlane-shared/asc.env (ASC_KEY_ID · ASC_ISSUER_ID · ASC_KEY_PATH)
"""
import base64, glob, json, os, re, subprocess, sys, time, urllib.error, urllib.request, hashlib, socket, http.client

API = "https://api.appstoreconnect.apple.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED = os.path.expanduser("~/Documents/workspace/fastlane-shared")
PERIOD = {"P1W": "ONE_WEEK", "P1M": "ONE_MONTH", "P1Y": "ONE_YEAR"}
SKIP = ("tip.", "gift.", "forever")
NAME_MAX, DESC_MAX = 30, 45


# ── 인증 · 호출 ───────────────────────────────────────────────
def env():
    out = {}
    for line in open(os.path.join(SHARED, "asc.env"), encoding="utf-8"):
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.strip().split("=", 1)
            out[k] = v.strip().strip('"')
    kp = os.path.expanduser(out["ASC_KEY_PATH"])
    out["ASC_KEY_PATH"] = kp if os.path.isabs(kp) else os.path.join(SHARED, kp)
    return out


def b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def der_to_raw(der):
    i, parts = (2 if der[1] < 0x80 else 3), []
    for _ in range(2):
        n = der[i + 1]
        parts.append(der[i + 2:i + 2 + n][-32:].rjust(32, b"\0"))
        i += 2 + n
    return b"".join(parts)


class ASC:
    def __init__(self):
        self.e, self.exp, self.calls = env(), 0, 0

    def token(self):
        if time.time() > self.exp - 60:
            now = int(time.time())
            head = {"alg": "ES256", "kid": self.e["ASC_KEY_ID"], "typ": "JWT"}
            body = {"iss": self.e["ASC_ISSUER_ID"], "iat": now, "exp": now + 1100, "aud": "appstoreconnect-v1"}
            sign = "%s.%s" % (b64url(json.dumps(head).encode()), b64url(json.dumps(body).encode()))
            der = subprocess.run(["openssl", "dgst", "-sha256", "-sign", self.e["ASC_KEY_PATH"]],
                                 input=sign.encode(), capture_output=True, check=True).stdout
            self._tok, self.exp = "%s.%s" % (sign, b64url(der_to_raw(der))), now + 1100
        return self._tok

    def call(self, method, path, body=None, tries=6):
        url = path if path.startswith("http") else API + path
        for n in range(tries):
            req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, method=method,
                                         headers={"Authorization": "Bearer " + self.token(), "Content-Type": "application/json"})
            try:
                self.calls += 1
                with urllib.request.urlopen(req, timeout=60) as r:
                    raw = r.read()
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                msg = e.read().decode()[:900]
                if e.code in (429, 500, 502, 503, 504) and n < tries - 1:
                    time.sleep(60 if e.code == 429 else 5 * (n + 1))
                    continue
                raise SystemExit("❌ %s %s → %d %s" % (method, path, e.code, msg))
            except (urllib.error.URLError, TimeoutError, socket.timeout, http.client.HTTPException, ConnectionError):
                if n < tries - 1:
                    time.sleep(5 * (n + 1))
                    continue
                raise

    def all(self, path):
        items, url = [], path
        while url:
            page = self.call("GET", url)
            items += page.get("data", [])
            url = (page.get("links") or {}).get("next")
        return items

    def post(self, typ, attrs, rels):
        data = {"type": typ, "attributes": attrs,
                "relationships": {k: {"data": v} for k, v in rels.items()}}
        if not attrs:
            data.pop("attributes")
        return self.call("POST", "/v1/" + typ if typ != "inAppPurchases" else "/v2/inAppPurchases", {"data": data})["data"]


# ── 원본 읽기 ────────────────────────────────────────────────
def load_storekit(repo, bundle):
    best = None
    for f in glob.glob(os.path.join(repo, "**", "*.storekit"), recursive=True):
        if "/build/" in f or "DerivedData" in f:
            continue
        d = json.load(open(f, encoding="utf-8"))
        ids = [p["productID"] for p in d.get("products", [])] + \
              [s["productID"] for g in d.get("subscriptionGroups", []) for s in g["subscriptions"]]
        pre = (bundle + ".", bundle.replace("-", ".") + ".")  # com.ysoup.TokenMemo-tap → com.ysoup.TokenMemo.tap.
        n = sum(1 for i in ids if i.startswith(pre) or not i.startswith("com."))
        if n and (not best or n > best[0]):
            best = (n, f, d)
    if not best:
        raise SystemExit("❌ %s 에서 %s 상품이 든 .storekit 을 못 찾았다" % (repo, bundle))
    return best[1], best[2]


def plan_price(plan, pid, override=None):
    """상품 ID → 설계안의 (원화, 달러). override(--prices 파일)가 있으면 그것이 먼저."""
    if override and pid in override:
        return tuple(override[pid])
    trims = [t for t in plan.get("trims") or [] if t.get("price")]
    low = pid.lower()
    if "upgrade" in low:
        return plan.get("upgrade"), plan.get("upgradeUS")
    if "graduate" in low:
        return plan.get("graduate"), plan.get("graduateUS")
    tr = next((t for t in trims if "plus" in low and re.search("plus|플러스", t.get("label") or "", re.I)), None) \
        or (trims[-1] if trims else None)
    if not tr:
        return None, None
    for key, words in (("weekly", ("weekly", ".week")), ("monthly", ("monthly", ".month")),
                       ("subscription", ("yearly", "annual", ".year"))):
        if any(w in low for w in words):
            v = tr.get(key) or {}
            return v.get("price"), v.get("priceUS")
    return tr.get("price"), tr.get("priceUS")


def ref_name(item):
    """참고 이름 — ASC 는 유니코드를 받지 않는다. 영어 표시 이름, 없으면 상품 ID 끝."""
    en = next((l.get("displayName") for l in item.get("localizations") or [] if l["locale"].startswith("en")), "")
    for cand in (item.get("referenceName") or "", en, item["productID"].split(".", 2)[-1]):
        if cand and all(ord(c) < 128 for c in cand):
            return cand[:64]
    return item["productID"][-64:]


def won(s):
    return float(re.sub(r"[^\d]", "", s or "") or 0)


def usd(s):
    return float(re.sub(r"[^\d.]", "", s or "") or 0)


def loc_text(item, kind, app, trim):
    """storekit 표시 이름 · 설명 → ASC (ko, en-US). 설명이 45자를 넘으면 짧은 정해진 문장으로."""
    out = {}
    per = {"P1W": ("주", "weekly"), "P1M": ("월", "monthly"), "P1Y": ("연", "yearly")}.get(item.get("recurringSubscriptionPeriod"))
    pid = item["productID"].lower()
    for l in item.get("localizations") or []:
        lang = "ko" if l["locale"].startswith("ko") else "en-US" if l["locale"].startswith("en") else None
        if not lang:
            continue
        name, desc = l.get("displayName") or "", l.get("description") or ""
        if "→" in name:  # ASC 는 화살표 같은 기호를 이름에 받지 않는다
            name = "Plus 평생에서 Pro 평생으로" if lang == "ko" else re.sub(r"\s*→\s*", " to ", name)
        name, desc = (re.sub(r"\s*[→⇒]\s*", " ", x).replace("—", "-").replace("–", "-") for x in (name, desc))
        if len(desc) > DESC_MAX or not desc:
            if lang == "ko":
                desc = ("Plus 평생에서 Pro 평생으로 올립니다" if "upgrade" in pid else
                        "구독하던 분께 드리는 %s 평생" % trim if "graduate" in pid else
                        "%s 기능을 %s 단위로 씁니다" % (trim, per[0]) if per else "%s 기능을 평생 씁니다" % trim)
            else:
                desc = ("Upgrade Plus Lifetime to Pro" if "upgrade" in pid else
                        "%s Lifetime for subscribers" % trim if "graduate" in pid else
                        "%s, billed %s" % (trim, per[1]) if per else "Unlock %s for good" % trim)
        out[lang] = {"name": name[:NAME_MAX], "description": desc[:DESC_MAX]}
    if "ko" not in out and "en-US" in out:
        out["ko"] = out["en-US"]
    return out


def review_shot(repo, mac):
    pats = ["docs/screenshots/raw/**/*.png", "docs/screenshots/**/*.png", "fastlane/screenshots/**/*.png"]
    cands = [f for p in pats for f in glob.glob(os.path.join(repo, p), recursive=True)]
    def score(f):
        lf = f.lower()
        return (("ko" in lf) * 2 + (("mac" in lf) == mac) * 3 + ("iphone" in lf or "6.9" in lf or "6.7" in lf) * (not mac)
                - ("creative" in lf or "marketing" in lf or "header" in lf) * 4 - ("watch" in lf or "ipad" in lf) * 6 + ("paywall" in lf or "pro" in os.path.basename(lf)) * 5)
    cands.sort(key=score, reverse=True)
    return cands[0] if cands else None


# ── 만들기 ───────────────────────────────────────────────────
def normalize_shot(path, mac):
    """심사용 그림을 규격 크기(iPhone 1290×2796 · Mac 2880×1800) JPEG 로 맞춘다. 비율은 지키고 남는 곳은 흰색으로 채운다."""
    w, h = (2880, 1800) if mac else (1290, 2796)
    out = os.path.join(os.environ.get("TMPDIR", "/tmp"), "asc-review-%s-%d.jpg" % (hashlib.md5(path.encode()).hexdigest()[:8], w))
    info = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path], capture_output=True, text=True).stdout
    cw, ch = (int(x) for x in re.findall(r"pixel(?:Width|Height): (\d+)", info))
    scale = min(w / cw, h / ch)
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "90",
                    "--resampleHeightWidth", str(int(ch * scale)), str(int(cw * scale)), path, "--out", out],
                   capture_output=True, check=True)
    subprocess.run(["sips", "--padToHeightWidth", str(h), str(w), "--padColor", "FFFFFF", out], capture_output=True, check=True)
    return out


def shot_ok(asc, path):
    """이미 올린 그림이 완료 상태면 True. 실패 · 올리다 만 그림은 지우고 False."""
    try:
        d = asc.call("GET", path).get("data")
    except SystemExit:
        return False
    if not d:
        return False
    if ((d["attributes"].get("assetDeliveryState") or {}).get("state")) == "COMPLETE":
        return True
    typ = d["type"]
    asc.call("DELETE", "/v1/%s/%s" % (typ, d["id"]))
    return False


def upload_shot(asc, typ, rel, owner_id, path):
    data = open(path, "rb").read()
    res = asc.post(typ, {"fileName": os.path.basename(path), "fileSize": len(data)}, {rel: {"type": rel + "s" if rel == "subscription" else "inAppPurchases", "id": owner_id}})
    for op in res["attributes"]["uploadOperations"]:
        chunk = data[op["offset"]:op["offset"] + op["length"]]
        req = urllib.request.Request(op["url"], data=chunk, method=op["method"],
                                     headers={h["name"]: h["value"] for h in op["requestHeaders"]})
        urllib.request.urlopen(req, timeout=120).read()
    asc.call("PATCH", "/v1/%s/%s" % (typ, res["id"]), {"data": {"type": typ, "id": res["id"], "attributes": {
        "uploaded": True, "sourceFileChecksum": hashlib.md5(data).hexdigest()}}})


def exists(asc, path):
    try:
        return bool(asc.call("GET", path).get("data"))
    except SystemExit:
        return False


def iap_price_point(asc, iap_id, territory, amount):
    pts = asc.all("/v2/inAppPurchases/%s/pricePoints?filter[territory]=%s&limit=8000" % (iap_id, territory))
    m = [p for p in pts if abs(float(p["attributes"]["customerPrice"]) - amount) < 0.001]
    if not m:
        raise SystemExit("❌ %s 에 %s 가격대가 없다" % (territory, amount))
    return m[0]["id"]


def sub_price_point(asc, sub_id, territory, amount):
    pts = asc.all("/v1/subscriptions/%s/pricePoints?filter[territory]=%s&limit=8000" % (sub_id, territory))
    m = [p for p in pts if abs(float(p["attributes"]["customerPrice"]) - amount) < 0.001]
    if not m:
        raise SystemExit("❌ %s 에 %s 가격대가 없다" % (territory, amount))
    return m[0]["id"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    ov = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--prices=")), None)
    override = json.load(open(ov, encoding="utf-8")) if ov else None
    slug, repo = args[0], os.path.abspath(args[1])
    plan = json.load(open(os.path.join(ROOT, "scripts", "paywall-plans.json"), encoding="utf-8"))["apps"][slug]
    meta = json.load(open(os.path.join(ROOT, "projects/PortfolioCEO/PortfolioCEO/Data/apps/%s.json" % slug), encoding="utf-8"))
    bundle = meta["bundleId"]
    skf, sk = load_storekit(repo, bundle)
    asc = ASC()
    # filter[bundleId] 는 앞부분만 맞아도 돌려준다(com.leeo.StickyPresenter → …Remote 도). 정확히 같은 것만.
    app = [x for x in asc.call("GET", "/v1/apps?filter[bundleId]=%s" % bundle)["data"] if x["attributes"]["bundleId"] == bundle]
    if not app:
        raise SystemExit("❌ App Store Connect 에 %s 앱이 없다" % bundle)
    app_id = app[0]["id"]
    have_iap = {x["attributes"]["productId"]: x for x in asc.all("/v1/apps/%s/inAppPurchasesV2?limit=200" % app_id)}
    groups = asc.all("/v1/apps/%s/subscriptionGroups?limit=200" % app_id)
    have_sub = {}
    for g in groups:
        for s in asc.all("/v1/subscriptionGroups/%s/subscriptions?limit=200" % g["id"]):
            have_sub[s["attributes"]["productId"]] = s
    pbx = " ".join(open(f, encoding="utf-8", errors="ignore").read() for f in glob.glob(os.path.join(repo, "*.xcodeproj", "project.pbxproj")))
    mac = "SDKROOT = macosx" in pbx and "SDKROOT = iphoneos" not in pbx
    shot = review_shot(repo, mac)
    if shot and apply:
        shot = normalize_shot(shot, mac)
    print("== %s (%s) · %s · 심사 스크린샷: %s" % (meta["name"], bundle, os.path.relpath(skf, repo),
                                             os.path.relpath(shot, repo) if shot else "없음"))
    half = lambda x: x and x["attributes"].get("state") == "MISSING_METADATA"  # 반쯤 만든 것 — 지우지 않고 빈 칸만 채운다
    todo_iap = [p for p in sk.get("products", []) if p["type"] == "NonConsumable" and not any(w in p["productID"] for w in SKIP)
                and (p["productID"] not in have_iap or half(have_iap.get(p["productID"])))]
    todo_sub = [(g, s) for g in sk.get("subscriptionGroups", []) for s in g["subscriptions"]
                if s["productID"] not in have_sub or half(have_sub.get(s["productID"]))]
    trims = [t for t in plan.get("trims") or [] if t.get("price")]
    trim_of = lambda pid: "Plus" if "plus" in pid.lower() and len(trims) > 1 else (trims[-1]["label"] if trims else "Pro")
    rows = []
    for p in todo_iap + [s for _, s in todo_sub]:
        krw, us = plan_price(plan, p["productID"], override)
        if not krw or not us:
            raise SystemExit("❌ %s 의 가격을 설계안에서 못 찾았다" % p["productID"])
        if abs(usd(us) - float(p.get("displayPrice") or 0)) > 0.001:
            print("  ⚠ %s: .storekit $%s ≠ 설계안 %s → 설계안을 쓴다" % (p["productID"], p.get("displayPrice"), us))
        rows.append((p, krw, us))
    for p, krw, us in rows:
        print("  %s %-48s %-10s %s %s" % ("새 구독" if p.get("recurringSubscriptionPeriod") else "새 평생",
                                         p["productID"], p.get("recurringSubscriptionPeriod") or "", krw, us))
    for pid in have_iap:
        if any(pid == p["productID"] for p in sk.get("products", [])):
            pass
    if not rows:
        print("  만들 상품 없음")
        return
    if not apply:
        print("  (미리 보기 — --apply 로 만든다)")
        return
    territories = [t["id"] for t in asc.all("/v1/territories?limit=200")]

    # 평생(비소모성)
    for p, krw, us in rows:
        if p.get("recurringSubscriptionPeriod"):
            continue
        trim = trim_of(p["productID"])
        iap = have_iap.get(p["productID"]) or asc.post("inAppPurchases", {
            "name": ref_name(p), "productId": p["productID"], "inAppPurchaseType": "NON_CONSUMABLE",
            "familySharable": bool(p.get("familyShareable"))}, {"app": {"type": "apps", "id": app_id}})
        has_loc = {x["attributes"]["locale"] for x in asc.all("/v2/inAppPurchases/%s/inAppPurchaseLocalizations" % iap["id"])}
        for lang, a in loc_text(p, "iap", meta["name"], trim).items():
            if lang not in has_loc:
                asc.post("inAppPurchaseLocalizations", dict(a, locale=lang), {"inAppPurchaseV2": {"type": "inAppPurchases", "id": iap["id"]}})
        try:
            priced = bool(asc.all("/v1/inAppPurchasePriceSchedules/%s/manualPrices?limit=1" % iap["id"]))
        except SystemExit:
            priced = False
        if not priced:
            kor = iap_price_point(asc, iap["id"], "KOR", won(krw))
            usa = iap_price_point(asc, iap["id"], "USA", usd(us))
            asc.call("POST", "/v1/inAppPurchasePriceSchedules", {
                "data": {"type": "inAppPurchasePriceSchedules", "relationships": {
                    "inAppPurchase": {"data": {"type": "inAppPurchases", "id": iap["id"]}},
                    "baseTerritory": {"data": {"type": "territories", "id": "KOR"}},
                    "manualPrices": {"data": [{"type": "inAppPurchasePrices", "id": "${kor}"}, {"type": "inAppPurchasePrices", "id": "${usa}"}]}}},
                "included": [
                    {"type": "inAppPurchasePrices", "id": "${kor}", "attributes": {"startDate": None},
                     "relationships": {"inAppPurchasePricePoint": {"data": {"type": "inAppPurchasePricePoints", "id": kor}}}},
                    {"type": "inAppPurchasePrices", "id": "${usa}", "attributes": {"startDate": None},
                     "relationships": {"inAppPurchasePricePoint": {"data": {"type": "inAppPurchasePricePoints", "id": usa}}}}]})
        if not exists(asc, "/v2/inAppPurchases/%s/inAppPurchaseAvailability" % iap["id"]):
          asc.call("POST", "/v1/inAppPurchaseAvailabilities", {"data": {
            "type": "inAppPurchaseAvailabilities", "attributes": {"availableInNewTerritories": True},
            "relationships": {"inAppPurchase": {"data": {"type": "inAppPurchases", "id": iap["id"]}},
                              "availableTerritories": {"data": [{"type": "territories", "id": t} for t in territories]}}}})
        if shot and not shot_ok(asc, "/v2/inAppPurchases/%s/appStoreReviewScreenshot" % iap["id"]):
            upload_shot(asc, "inAppPurchaseAppStoreReviewScreenshots", "inAppPurchaseV2", iap["id"], shot)
        print("  ✅ 평생 %s %s / %s" % (p["productID"], krw, us))

    # 구독
    gid = {}
    for g, s in todo_sub:
        if g["name"] not in gid:
            ex = next((x for x in groups if x["attributes"]["referenceName"] == g["name"]), None)
            if ex is None and groups and len(sk.get("subscriptionGroups", [])) == 1:
                ex = groups[0]
            if ex is None:
                ex = asc.post("subscriptionGroups", {"referenceName": g["name"]}, {"app": {"type": "apps", "id": app_id}})
                for lang, nm in (("ko", meta["name"]), ("en-US", meta.get("nameEn") or meta["name"])):
                    asc.post("subscriptionGroupLocalizations", {"name": nm[:75], "locale": lang},
                             {"subscriptionGroup": {"type": "subscriptionGroups", "id": ex["id"]}})
                groups.append(ex)
            gid[g["name"]] = ex["id"]
    for g, s in todo_sub:
        krw, us = plan_price(plan, s["productID"], override)
        trim = trim_of(s["productID"])
        sub = have_sub.get(s["productID"]) or asc.post("subscriptions", {"name": ref_name(s), "productId": s["productID"],
                                         "subscriptionPeriod": PERIOD[s["recurringSubscriptionPeriod"]],
                                         "groupLevel": int(s.get("groupNumber") or 1), "familySharable": bool(s.get("familyShareable"))},
                       {"group": {"type": "subscriptionGroups", "id": gid[g["name"]]}})
        has_loc = {x["attributes"]["locale"] for x in asc.all("/v1/subscriptions/%s/subscriptionLocalizations" % sub["id"])}
        for lang, a in loc_text(s, "sub", meta["name"], trim).items():
            if lang not in has_loc:
                asc.post("subscriptionLocalizations", dict(a, locale=lang), {"subscription": {"type": "subscriptions", "id": sub["id"]}})
        done_t = {x["relationships"]["territory"]["data"]["id"] for x in asc.all("/v1/subscriptions/%s/prices?limit=200&include=territory" % sub["id"])}
        try:
            has_av = bool(asc.call("GET", "/v1/subscriptions/%s/subscriptionAvailability" % sub["id"]).get("data"))
        except SystemExit:
            has_av = False
        if not has_av:
          asc.call("POST", "/v1/subscriptionAvailabilities", {"data": {
            "type": "subscriptionAvailabilities", "attributes": {"availableInNewTerritories": True},
            "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sub["id"]}},
                              "availableTerritories": {"data": [{"type": "territories", "id": t} for t in territories]}}}})
        kor = sub_price_point(asc, sub["id"], "KOR", won(krw))
        usa = sub_price_point(asc, sub["id"], "USA", usd(us))
        eq = asc.all("/v1/subscriptionPricePoints/%s/equalizations?limit=200&include=territory" % kor)
        points = {"KOR": kor, "USA": usa}
        for p in eq:
            t = p["relationships"]["territory"]["data"]["id"]
            points.setdefault(t, p["id"])
        for t, pp in points.items():
            if t in done_t:
                continue
            asc.post("subscriptionPrices", {"startDate": None, "preserveCurrentPrice": False},
                     {"subscription": {"type": "subscriptions", "id": sub["id"]},
                      "subscriptionPricePoint": {"type": "subscriptionPricePoints", "id": pp},
                      "territory": {"type": "territories", "id": t}})
        if shot and not shot_ok(asc, "/v1/subscriptions/%s/appStoreReviewScreenshot" % sub["id"]):
            upload_shot(asc, "subscriptionAppStoreReviewScreenshots", "subscription", sub["id"], shot)
        print("  ✅ 구독 %s %s / %s · %d개 나라" % (s["productID"], krw, us, len(points)))
    print("  API 호출 %d번" % asc.calls)


if __name__ == "__main__":
    main()
