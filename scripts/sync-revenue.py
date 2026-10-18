#!/usr/bin/env python3
"""App Store Connect 판매 리포트로 앱별 월 매출(개발자 수익)을 모아 비공개 파일에 둔다.

사용법:
  python3 scripts/sync-revenue.py            # 지난 12개월(끝난 달) 조회 — 월 리포트는 Apple 이 12개월만 둔다
  python3 scripts/sync-revenue.py --months 6

5단계(자리 잡음) 관문 — 매출 발생 · 순수익 · 안정적 우상향 — 의 근거다.

⚠️ 이 레포는 공개다. 금액은 레포에 넣지 않는다.
   결과는 reports/revenue.json(.gitignore)에만 쓰고, 공개 페이지에는 관문 통과 여부만 나간다.
   앱별 비용은 reports/app-costs.json(.gitignore, 없으면 0)에 {"<slug>": {"monthlyKRW": 숫자}} 로 적는다.

세는 것 : Developer Proceeds × Units — 유료 다운로드·인앱·구독 모두, 환불(음수 Units) 포함.
          Apple 수수료를 뗀 뒤의 금액이다. 세금·환전 수수료는 빠지지 않은 판매 리포트 기준이다.
환율    : 나라마다 Currency of Proceeds 가 다르다. 그 달 마지막 날의 ECB 환율(frankfurter.dev, 유로 기준 교차 환율)로 원화로 바꾼다.
          ECB 가 환율을 내지 않는 통화는 건너뛰고 끝에 알린다.
앱 찾기 : 앱 줄은 Apple Identifier 가 앱 ID 다. 인앱·구독 줄은 Parent Identifier(부모 앱 SKU)라서
          앱 줄의 SKU → Apple Identifier 표로 부모 앱을 찾는다.

인증은 LeeoNote/scripts/update-app-downloads.py 와 같다:
  ~/Documents/workspace/fastlane-shared/asc.env 의 ASC_KEY_ID · ASC_ISSUER_ID · ASC_KEY_PATH · ASC_VENDOR_NUMBER
"""
import argparse
import base64
import gzip
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from calendar import monthrange
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "reports/revenue.json")
ENV_FILE = os.environ.get("ASC_ENV", "~/Documents/workspace/fastlane-shared/asc.env")
API = "https://api.appstoreconnect.apple.com/v1/salesReports"
FX = "https://api.frankfurter.dev/v1/%s?base=EUR"
APP_TYPE = re.compile(r"^(?:1[A-Z]*|F1|7[A-Z]*|F7)$")   # 앱 자체 줄(다운로드·업데이트)


# ── 인증 (update-app-downloads.py 와 같다) ──

def b64u(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=")


def read_env(path):
    out = {}
    try:
        f = open(os.path.expanduser(path), encoding="utf-8")
    except OSError:
        return out
    with f:
        for line in f:
            m = re.match(r"\s*(?:export\s+)?([A-Z_][A-Z0-9_]*)\s*=\s*(.*)", line)
            if m:
                out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return out


def der_to_raw(der):
    i = 2 if der[1] < 0x80 else 2 + (der[1] & 0x7F)
    out = b""
    for _ in range(2):
        ln = der[i + 1]
        out += der[i + 2:i + 2 + ln].lstrip(b"\x00").rjust(32, b"\x00")
        i += 2 + ln
    return out


def make_token(env):
    head = {"alg": "ES256", "kid": env["ASC_KEY_ID"], "typ": "JWT"}
    now = int(time.time())
    body = {"iss": env["ASC_ISSUER_ID"], "iat": now, "exp": now + 1200, "aud": "appstoreconnect-v1"}
    msg = (b64u(json.dumps(head, separators=(",", ":")).encode()) + b"." +
           b64u(json.dumps(body, separators=(",", ":")).encode()))
    der = subprocess.run(["openssl", "dgst", "-sha256", "-sign", os.path.expanduser(env["ASC_KEY_PATH"])],
                         input=msg, capture_output=True, check=True).stdout
    return (msg + b"." + b64u(der_to_raw(der))).decode()


def fetch(token, vendor, month):
    url = ("%s?filter[frequency]=MONTHLY&filter[reportType]=SALES&filter[reportSubType]=SUMMARY"
           "&filter[vendorNumber]=%s&filter[reportDate]=%s&filter[version]=1_0" % (API, vendor, month))
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token,
                                               "Accept": "application/a-gzip"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            blob = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None   # 그 달에 아무것도 안 팔렸다
        if e.code == 410:
            return None   # Apple 이 더는 두지 않는 달(월 리포트는 12개월)
        raise SystemExit("%s → HTTP %s %s" % (month, e.code, e.read()[:300].decode("utf-8", "replace")))
    try:
        return gzip.GzipFile(fileobj=io.BytesIO(blob)).read().decode("utf-8")
    except OSError:
        return blob.decode("utf-8", "replace")


def krw_rates(month):
    """그 달 마지막 날 기준 {통화: 1통화의 원화}."""
    y, m = map(int, month.split("-"))
    day = "%s-%02d" % (month, monthrange(y, m)[1])
    for attempt in range(4):
        try:
            # 기본 urllib User-Agent 는 Cloudflare 가 403 으로 막는다
            req = urllib.request.Request(FX % day, headers={"User-Agent": "app-portfolio/sync-revenue"})
            d = json.load(urllib.request.urlopen(req, timeout=30))
            # 원화 기준으로 받으면 소수 다섯째 자리에서 잘려 1% 안팎이 틀어진다 — 유로 기준으로 받아 교차한다
            rates = dict(d["rates"], EUR=1.0)
            krw = rates["KRW"]
            return {cur: krw / v for cur, v in rates.items() if v}, d.get("date")
        except Exception:
            time.sleep(5 * (attempt + 1))
    raise SystemExit("환율을 받지 못했습니다: " + day)


def last_months(n):
    t = date.today()
    y, m = t.year, t.month
    out = []
    for _ in range(n):
        m -= 1
        if m == 0:
            y, m = y - 1, 12
        out.append("%04d-%02d" % (y, m))
    return list(reversed(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=12)
    args = ap.parse_args()

    env = read_env(ENV_FILE)
    env.update({k: v for k, v in os.environ.items() if k.startswith("ASC_")})
    missing = [k for k in ("ASC_KEY_ID", "ASC_ISSUER_ID", "ASC_KEY_PATH", "ASC_VENDOR_NUMBER") if not env.get(k)]
    if missing:
        raise SystemExit("%s 에 %s 가 없습니다." % (ENV_FILE, " · ".join(missing)))
    token = make_token(env)

    months = last_months(args.months)
    rows_by_month, sku_to_id, names = {}, {}, {}
    for n, month in enumerate(months, 1):
        sys.stdout.write("\r  판매 리포트 %d/%d (%s)   " % (n, len(months), month))
        sys.stdout.flush()
        tsv = fetch(token, env["ASC_VENDOR_NUMBER"], month)
        lines = tsv.splitlines() if tsv else []
        if not lines:
            rows_by_month[month] = []
            continue
        head = lines[0].split("\t")
        ix = {k: head.index(k) for k in ("SKU", "Title", "Product Type Identifier", "Units",
                                         "Developer Proceeds", "Currency of Proceeds",
                                         "Apple Identifier", "Parent Identifier")}
        rows = []
        for line in lines[1:]:
            c = line.split("\t")
            if len(c) <= max(ix.values()):
                continue
            r = {k: c[i].strip() for k, i in ix.items()}
            if APP_TYPE.match(r["Product Type Identifier"]) and not r["Parent Identifier"]:
                sku_to_id[r["SKU"]] = r["Apple Identifier"]
                names[r["Apple Identifier"]] = r["Title"]
            rows.append(r)
        rows_by_month[month] = rows
    print()

    apps, fx_used, skipped, orphan = {}, {}, {}, {}
    for month in months:
        rates, fx_day = krw_rates(month)
        fx_used[month] = fx_day
        for r in rows_by_month[month]:
            try:
                amount = float(r["Developer Proceeds"]) * int(r["Units"])
            except ValueError:
                continue
            if not amount:
                continue
            cur = r["Currency of Proceeds"]
            krw = amount if cur == "KRW" else amount * rates[cur] if cur in rates else None
            if krw is None:
                skipped[cur] = skipped.get(cur, 0) + amount
                continue
            app_id = sku_to_id.get(r["Parent Identifier"]) if r["Parent Identifier"] else r["Apple Identifier"]
            if not app_id:
                orphan[r["Parent Identifier"]] = orphan.get(r["Parent Identifier"], 0) + krw
                continue
            per = apps.setdefault(app_id, {})
            per[month] = per.get(month, 0) + krw

    out = {"currency": "KRW", "basis": "Developer Proceeds × Units (Apple 수수료 뗀 뒤, 판매 리포트)",
           "months": months, "fxDates": fx_used, "evaluatedAt": date.today().isoformat(),
           "apps": {k: {"name": names.get(k, ""), "monthly": {m: round(v) for m, v in sorted(v.items())}}
                    for k, v in sorted(apps.items())}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print("  앱 %d개의 월 매출을 %s 에 썼습니다(커밋하지 않는 파일)." % (len(apps), os.path.relpath(OUT, ROOT)))
    if skipped:
        print("  환율이 없어 뺀 통화: %s" % ", ".join("%s %.2f" % kv for kv in sorted(skipped.items())))
    if orphan:
        print("  부모 앱을 못 찾은 인앱 매출(SKU): %s" % ", ".join("%s ₩%d" % (k, v) for k, v in orphan.items()))


if __name__ == "__main__":
    main()
