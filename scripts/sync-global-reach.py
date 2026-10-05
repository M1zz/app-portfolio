#!/usr/bin/env python3
"""앱별 글로벌 지원(globalReach) 축을 App Store에서 수집해 앱 JSON에 기록한다.

사용법:
  python3 scripts/sync-global-reach.py               # App Store 조회 후 기록
  python3 scripts/sync-global-reach.py --from x.json # 미리 받은 조회 결과로 기록 (재조회 생략)

수명주기(lifecycle)가 '시장에서 어디까지 왔나'라면, 글로벌 지원은 '어디까지 닿을 수 있나'다.
판정 근거는 App Store가 공개하는 사실만 쓴다.

  languages    앱 번들에 들어 있는 언어 (iTunes Lookup languageCodesISO2A)
  englishPage  미국 스토어 소개 문구가 영어로 쓰였는가 (한글이 없으면 영어로 본다)
  storefronts  주요 18개국 스토어 중 판매 중인 곳 수

단계 (level):
  3 Multilingual   앱이 3개 이상 언어 지원
  2 Bilingual      앱이 한국어·영어 지원
  1 English Store  앱은 한 언어지만 스토어 소개는 영어로 준비
  0 Korea First    한국어 사용자 중심

⚠️ 번들 언어가 EN 하나뿐이면 개발 기본 언어(en)일 뿐 영어 번역이 아닐 수 있다.
   그래서 EN 단독은 언어 수로 치지 않고 스토어 소개 문구로 판단한다.
"""
import argparse
import glob
import json
import os
import re
import time
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "projects/PortfolioCEO/PortfolioCEO/Data/apps")
STOREFRONTS = ["kr", "us", "jp", "gb", "de", "fr", "cn", "tw", "es",
               "br", "in", "ca", "au", "it", "vn", "th", "id", "mx"]
LABELS = {3: "multilingual", 2: "bilingual", 1: "english-store", 0: "korea-first"}
HANGUL = re.compile(r"[가-힣]")


def lookup(app_id, country):
    url = "https://itunes.apple.com/lookup?id=%s&country=%s" % (app_id, country)
    for attempt in range(6):
        try:
            res = json.load(urllib.request.urlopen(url, timeout=20))
            time.sleep(2.5)  # 조회 API는 분당 요청 수 제한이 빡빡하다
            return res["results"][0] if res["results"] else None
        except Exception:
            time.sleep(15 * (attempt + 1))
    raise RuntimeError("lookup 실패: %s %s" % (app_id, country))


def fetch(app_id):
    out = {"stores": []}
    for c in STOREFRONTS:
        r = lookup(app_id, c)
        if not r:
            continue
        out["stores"].append(c)
        out["langs"] = r.get("languageCodesISO2A")
        if c == "us":
            out["us_name"] = r.get("trackName")
            out["us_desc"] = r.get("description") or ""
    return out


def classify(raw):
    langs = sorted(set(raw.get("langs") or []))
    real = [l for l in langs if not (langs == ["EN"])]  # EN 단독은 기본 언어로 본다
    us_text = (raw.get("us_name") or "") + (raw.get("us_desc") or "")[:400]
    english_page = bool(us_text) and not HANGUL.search(us_text)
    if len(real) >= 3:
        level = 3
    elif "KO" in real and "EN" in real:
        level = 2
    elif english_page:
        level = 1
    else:
        level = 0
    stores = len(raw.get("stores") or [])
    basis = "앱 언어 %s · 미국 스토어 소개 %s · 주요 %d개국 중 %d곳 판매" % (
        ", ".join(langs) or "정보 없음",
        "영어" if english_page else "한국어",
        len(STOREFRONTS), stores)
    return {
        "level": level,
        "label": LABELS[level],
        "languages": langs,
        "languageCount": len(real) if real else 1,
        "englishPage": english_page,
        "storefronts": stores,
        "storefrontsChecked": len(STOREFRONTS),
        "basis": basis,
        "evaluatedAt": date.today().isoformat(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", help="미리 받은 조회 결과 JSON {slug: raw}")
    args = ap.parse_args()
    cached = json.load(open(args.src, encoding="utf-8")) if args.src else {}

    for path in sorted(glob.glob(os.path.join(APPS, "*.json"))):
        slug = os.path.basename(path)[:-5]
        with open(path, encoding="utf-8") as fh:
            app = json.load(fh)
        if not app.get("appStoreId") or (app.get("lifecycle") or {}).get("stage") == 0:
            continue
        raw = cached.get(slug) or fetch(app["appStoreId"])
        if not raw.get("stores"):
            print("  %-24s 스토어 조회 결과 없음 — 건너뜀" % slug)
            continue
        app["globalReach"] = classify(raw)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(app, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        g = app["globalReach"]
        print("  %-24s %d %-14s %s" % (slug, g["level"], g["label"], g["basis"]))


if __name__ == "__main__":
    main()
