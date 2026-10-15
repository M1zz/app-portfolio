#!/usr/bin/env python3
"""미국 App Store 에서 앱별 판매 상태(usStore)를 수집해 앱 JSON 에 기록한다.

사용법:
  python3 scripts/sync-us-store.py               # 미국 스토어 페이지 조회 후 기록
  python3 scripts/sync-us-store.py --from x.json # 미리 받은 조회 결과로 기록 (재조회 생략)

레딧 같은 영어권 채널로 사람을 데려왔을 때 그 사람이 보는 것은 미국 스토어다.
그래서 '레딧에 올릴 만한가'는 미국 스토어에서 본 사실로 판정한다.

  available   미국 스토어에서 팔고 있는가 (페이지가 열리는가)
  price       미국 다운로드 가격 (USD)
  iap         인앱 구입 목록 [{name, price}] — 스토어 페이지 'In-App Purchases' 칸
  iapEnglish  인앱 구입 이름에 한글이 없는가 (미국 사용자가 결제 화면에서 보는 이름)
  rating      미국 스토어 평점 · 평가 수

price 블록은 손대지 않는다 — 한국 스토어 기준 유료화 모델은 sync-pricing.py 가 맡는다.
⚠️ 앱 JSON을 고쳐 쓰므로 다른 sync-* 스크립트와 동시에 돌리지 말 것.
"""
import argparse
import glob
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "projects/PortfolioCEO/PortfolioCEO/Data/apps")
HANGUL = re.compile(r"[가-힣]")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/605.1.15"


def fetch_page(app_id):
    url = "https://apps.apple.com/us/app/id%s" % app_id
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
            time.sleep(1.5)
            return body
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None  # 미국에서 안 판다
            time.sleep(10 * (attempt + 1))
        except Exception:
            time.sleep(10 * (attempt + 1))
    raise RuntimeError("조회 실패: %s" % app_id)


def parse(body):
    if body is None:
        return {"available": False}
    out = {"available": True}
    m = re.search(r'"offers":\{"@type":"Offer","price":([0-9.]+),"priceCurrency":"(\w+)"', body)
    if m:
        out["price"] = float(m.group(1))
    m = re.search(r'"aggregateRating":\{"@type":"AggregateRating","ratingValue":([0-9.]+),'
                  r'"reviewCount":(\d+)', body)
    if m:
        out["rating"] = float(m.group(1))
        out["ratingCount"] = int(m.group(2))
    iap = []
    m = re.search(r'In-App Purchases","summary":"Yes","items":\[(.*?)\],"shouldAlwaysPresent', body)
    if m:
        for name, price in re.findall(
                r'"leadingText":"((?:[^"\\]|\\.)*)","trailingText":"((?:[^"\\]|\\.)*)"', m.group(1)):
            iap.append({"name": json.loads('"%s"' % name), "price": json.loads('"%s"' % price)})
    out["iap"] = iap
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", help="미리 받은 조회 결과 JSON {slug: parsed}")
    ap.add_argument("--dump", help="조회 결과를 이 파일에 저장")
    args = ap.parse_args()
    cached = json.load(open(args.src, encoding="utf-8")) if args.src else {}
    dump = {}

    for path in sorted(glob.glob(os.path.join(APPS, "*.json"))):
        slug = os.path.basename(path)[:-5]
        with open(path, encoding="utf-8") as fh:
            app = json.load(fh)
        if not app.get("appStoreId") or (app.get("lifecycle") or {}).get("stage") == 0:
            continue
        raw = cached.get(slug) or parse(fetch_page(app["appStoreId"]))
        dump[slug] = raw

        us = dict(raw)
        if us["available"]:
            us["iapEnglish"] = not any(HANGUL.search(i["name"]) for i in us["iap"])
        us["evaluatedAt"] = date.today().isoformat()
        app["usStore"] = us

        with open(path, "w", encoding="utf-8") as fh:
            json.dump(app, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        if us["available"]:
            print("  %-24s $%-5s IAP %d개%s  평가 %s" % (
                slug, us.get("price"), len(us["iap"]),
                "" if us["iapEnglish"] else " (한글 이름)", us.get("ratingCount", 0)))
        else:
            print("  %-24s 미국 스토어에 없음" % slug)

    if args.dump:
        json.dump(dump, open(args.dump, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
