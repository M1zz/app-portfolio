#!/usr/bin/env python3
"""앱별 소개 페이지(introPage)를 App Store 마케팅 URL에서 찾아 판정하고 앱 JSON에 기록한다.

사용법:
  python3 scripts/sync-intro-pages.py

소개 페이지 = App Store '마케팅 URL'(iTunes Lookup sellerUrl)에 걸린 페이지. 지원 페이지(supportUrl)와 따로 본다.
한국 스토어 주소를 기준으로 보고, 미국 스토어 주소가 다르면 그쪽을 영어 소개로 본다.

  있음        set        마케팅 URL 이 등록되어 있다
              reachable  그 주소가 열린다
              intro      지원·문의만 있는 페이지가 아니라 앱을 소개한다 (support.html · 노션 · 블로그 주소, 문의·FAQ·개인정보 제목뿐이면 아님)
  경험 상상   screens    앱 화면 그림 2장 이상 (아이콘·배지·로고는 빼고 센다)
              video      사용 영상 (video 태그 · mp4 · 유튜브/비메오)
              tryIt      페이지에서 직접 눌러 보는 체험 (긴 스크립트 + '직접 눌러보세요 · Try it' 같은 안내)
              scenario   쓰는 장면 이야기 ('이럴 때 · 이런 분 · 실제로 쓰면 · for example')
              steps      쓰는 순서 안내 ('이렇게 써요 · 사용 방법 · How it works')
              proof      쓰는 사람의 목소리 (후기 · 리뷰 · 평점)
  이어 주기   storeLink  App Store 로 가는 링크
              ogImage    링크를 공유하면 뜨는 미리보기 그림 (og:image)
              english    영어 소개

값은 True / False / None(확인 불가: 주소가 안 열리거나 노션처럼 본문을 스크립트로 그리는 페이지).
마케팅 URL 이 없으면 App Store 에서 닿는 소개가 없으므로 경험 항목도 모두 False 로 둔다.
"""
import glob
import json
import os
import re
import ssl
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "projects/PortfolioCEO/PortfolioCEO/Data/apps")
CTX = ssl.create_default_context()

SUPPORT_URL = re.compile(r"support|notion\.(?:site|so)|blogspot\.", re.I)
JS_RENDERED = re.compile(r"notion\.(?:site|so)", re.I)
SUPPORT_HEADING = re.compile(r"문의|지원|support|자주\s*묻는|FAQ|개인정보|privacy|약관|법적|terms|contact|도움|"
                             r"in english|english\)|정보$", re.I)
NOT_SCREEN = re.compile(r"icon|logo|badge|favicon|notion|avatar", re.I)
VIDEO = re.compile(r"<video|<iframe[^>]+(?:youtube|vimeo)|\.(?:mp4|mov|webm)\b", re.I)
TRY_TEXT = re.compile(r"직접\s*눌러|직접\s*해\s*보|체험|눌러\s*보세요|try it|try the|playground|interactive demo", re.I)
TRY_SCRIPT_MIN = 800  # 이보다 짧은 인라인 스크립트는 메뉴·언어 전환 정도로 본다
SCENARIO = re.compile(r"이럴\s*때|이런\s*(?:순간|분|때|날)|예를\s*들어|실제로\s*쓰면|하루|아침|출근|퇴근|일상|"
                      r"for example|imagine|perfect for|use case|scenario|when you", re.I)
STEPS = re.compile(r"이렇게\s*(?:써요|씁니다|쓰세요)|사용\s*방법|사용법|시작하기|how it works|how to use|getting started|"
                   r"step\s*\d|\d\s*단계", re.I)
PROOF = re.compile(r"후기|리뷰|사용자\s*(?:이야기|평)|★|⭐|\btestimonials?\b|\breviews?\b|\bratings?\b|평점", re.I)
HANGUL = re.compile(r"[가-힣]")
LATIN_WORD = re.compile(r"\b[A-Za-z]{3,}\b")


def lookup(ids):
    """{앱 ID: {kr: 주소, us: 주소}}"""
    out = {}
    for c in ("kr", "us"):
        url = "https://itunes.apple.com/lookup?id=%s&country=%s" % (",".join(ids), c)
        with urllib.request.urlopen(url, timeout=30, context=CTX) as r:
            for x in json.load(r).get("results", []):
                out.setdefault(str(x["trackId"]), {})[c] = x.get("sellerUrl")
    return out


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (portfolio-check)"})
    try:
        with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
            return r.status, r.read(3_000_000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return None, ""


def visible(body):
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", body)
    return re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", t))


def headings(body):
    return [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"(?is)<h2[^>]*>(.*?)</h2>", body)]


def is_english(body):
    text = visible(body)
    # 소개 페이지는 짧다 — 영어 단어 30개면 충분하고, 한글은 언어 메뉴의 '한국어' 정도만 허용한다
    return len(LATIN_WORD.findall(text)) >= 30 and len(HANGUL.findall(text)) < 40


def judge(url, url_en):
    blank = {k: None for k in ("intro", "screens", "video", "tryIt", "scenario", "steps", "proof",
                               "storeLink", "ogImage", "english")}
    if not url:
        return {"url": None, "set": False, "reachable": None, **{k: False for k in blank}}
    status, body = fetch(url)
    ok = status is not None and 200 <= status < 400
    m = {"url": url, "set": True, "reachable": None if status is None else ok, **blank}
    if url_en and url_en != url:
        m["urlEn"] = url_en
    if not ok or JS_RENDERED.search(url):
        if ok:  # 노션 — 열리지만 본문을 읽을 수 없다
            m["intro"] = False
        return m
    text = visible(body)
    hs = headings(body)
    m["intro"] = not SUPPORT_URL.search(url) and not (hs and all(SUPPORT_HEADING.search(h) for h in hs))
    imgs = re.findall(r'(?i)<(?:img|source)[^>]+(?:src|srcset)="([^"]+)"', body)
    imgs += re.findall(r"(?i)url\(['\"]?([^'\")]+\.(?:png|jpe?g|webp))", body)
    m["screens"] = len({i for i in imgs if not NOT_SCREEN.search(i)}) >= 2
    m["video"] = VIDEO.search(body) is not None
    long_script = any(len(s) >= TRY_SCRIPT_MIN for s in re.findall(r"(?is)<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", body))
    m["tryIt"] = long_script and TRY_TEXT.search(body) is not None
    m["scenario"] = SCENARIO.search(text) is not None
    m["steps"] = STEPS.search(text) is not None
    m["proof"] = PROOF.search(text) is not None
    m["storeLink"] = re.search(r"apps\.apple\.com", body) is not None
    m["ogImage"] = re.search(r"""property=["']og:image""", body) is not None
    if url_en and url_en != url:
        st, en = fetch(url_en)
        m["english"] = None if st is None else (200 <= st < 400 and is_english(en))
    else:
        m["english"] = is_english(body) or re.search(r'(?i)href="[^"]*(?:/en/|-en\.html|lang=en)', body) is not None
    return m


def main():
    apps = []
    for path in sorted(glob.glob(os.path.join(APPS, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            app = json.load(fh)
        if (app.get("lifecycle") or {}).get("stage") == 0 or not app.get("appStoreId"):
            continue
        apps.append((path, app))
    urls = lookup([str(a["appStoreId"]) for _, a in apps])

    def mark(m, keys):
        return "".join("·" if m.get(k) is None else ("●" if m[k] else "○") for k in keys)

    for path, app in apps:
        u = urls.get(str(app["appStoreId"]), {})
        m = judge(u.get("kr") or u.get("us"), u.get("us"))
        m["evaluatedAt"] = date.today().isoformat()
        app["introPage"] = m
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(app, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print("  %-24s 있음 %s  경험 %s  이어 주기 %s  %s" % (
            os.path.basename(path)[:-5], mark(m, ("set", "reachable", "intro")),
            mark(m, ("screens", "video", "tryIt", "scenario", "steps", "proof")),
            mark(m, ("storeLink", "ogImage", "english")), m.get("url") or "-"))


if __name__ == "__main__":
    main()
