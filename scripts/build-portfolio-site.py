#!/usr/bin/env python3
"""
포트폴리오 공개 쇼케이스 사이트 빌더.

- projects/PortfolioCEO/PortfolioCEO/Data/apps/*.json 에서 앱 메타데이터를 읽고
- 앱스토어(iTunes Lookup API)에서 아이콘 / 평점 / 장르 / 가격 / 설명을 자동 수집(+캐시)
- docs/index.html 에 반응형 쇼케이스를 생성한다.

사용:
    python3 scripts/build-portfolio-site.py
    python3 scripts/build-portfolio-site.py --no-fetch   # 캐시만 사용 (오프라인)
"""

import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = ROOT / "projects/PortfolioCEO/PortfolioCEO/Data/apps"
OUT_DIR = ROOT / "docs"
OUT_FILE = OUT_DIR / "index.html"
CACHE_FILE = ROOT / "scripts" / ".appstore-cache.json"
CONTENT_FILE = ROOT / "scripts" / "showcase-content.json"
CONTENT_EN_FILE = ROOT / "scripts" / "showcase-content.en.json"
SHOTS_DIR = OUT_DIR / "screenshots"

KST = timezone(timedelta(hours=9))
APPSTORE_ID_RE = re.compile(r"/id(\d+)")


def load_apps():
    apps = []
    for f in sorted(APPS_DIR.glob("*.json")):
        with open(f, encoding="utf-8") as fp:
            data = json.load(fp)
        data["_slug"] = f.stem
        apps.append(data)
    return apps


def extract_appstore_id(app):
    if app.get("appStoreId"):
        return str(app["appStoreId"])
    url = app.get("appStoreUrl") or ""
    m = APPSTORE_ID_RE.search(url)
    return m.group(1) if m else None


def local_shots(slug):
    """docs/screenshots/<slug>.png (+ <slug>-2.png …) 이 있으면 상대경로로 반환."""
    if not SHOTS_DIR.exists():
        return []
    files = sorted(SHOTS_DIR.glob(f"{slug}.png")) + sorted(SHOTS_DIR.glob(f"{slug}-*.png"))
    return [f"screenshots/{f.name}" for f in files]


def load_content():
    """카테고리 그룹 + 앱별 누가/언제/어떻게 큐레이션 카피."""
    if CONTENT_FILE.exists():
        with open(CONTENT_FILE, encoding="utf-8") as fp:
            return json.load(fp)
    return {"groups": [], "apps": {}}


def load_content_en():
    """showcase-content.json 의 영어 번역본 (groups 는 배열 인덱스, apps 는 slug 로 매칭)."""
    if CONTENT_EN_FILE.exists():
        with open(CONTENT_EN_FILE, encoding="utf-8") as fp:
            return json.load(fp)
    return {"groups": [], "apps": {}}


def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, encoding="utf-8") as fp:
            return json.load(fp)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as fp:
        json.dump(cache, fp, ensure_ascii=False, indent=2)


COUNTRIES = ("kr", "us", "jp")


def lookup_country(app_id, country):
    url = f"https://itunes.apple.com/lookup?id={app_id}&country={country}"
    req = urllib.request.Request(url, headers={"User-Agent": "portfolio-site-builder"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    return data["results"][0] if data.get("resultCount") else None


def fetch_appstore(app_id):
    """여러 국가 스토어를 순차 조회 (KR → US → JP). US 스토어에서 영어 카피도 함께 수집."""
    r = None
    found = None
    for country in COUNTRIES:
        r = lookup_country(app_id, country)
        if r:
            found = country
            break
    if r is None:
        return None
    # 영어(EN) 표시용: US 스토어 설명·장르·가격 (미출시면 None → 렌더 시 폴백)
    r_en = r if found == "us" else None
    if r_en is None:
        try:
            r_en = lookup_country(app_id, "us")
        except (urllib.error.URLError, TimeoutError):
            r_en = None
    return {
        "trackName": r.get("trackName"),
        "icon": r.get("artworkUrl512") or r.get("artworkUrl100"),
        "rating": r.get("averageUserRating"),
        "ratingCount": r.get("userRatingCount"),
        "genre": r.get("primaryGenreName"),
        "price": r.get("formattedPrice"),
        "description": r.get("description"),
        "seller": r.get("sellerName"),
        "version": r.get("trackViewUrl") and r.get("version"),
        "url": r.get("trackViewUrl"),
        "screenshots": (r.get("screenshotUrls") or [])[:3],
        "trackName_en": r_en.get("trackName") if r_en else None,
        "description_en": r_en.get("description") if r_en else None,
        "genre_en": r_en.get("primaryGenreName") if r_en else None,
        "price_en": r_en.get("formattedPrice") if r_en else None,
    }


def enrich(apps, fetch=True):
    cache = load_cache()
    for app in apps:
        app_id = extract_appstore_id(app)
        app["_appStoreId"] = app_id
        store = cache.get(app_id) if app_id else None
        if app_id and fetch:
            try:
                fresh = fetch_appstore(app_id)
                if fresh:
                    store = fresh
                    cache[app_id] = fresh
                    print(f"  ✓ {app.get('name')} ({app_id})")
                else:
                    print(f"  · {app.get('name')} ({app_id}) — 앱스토어 미발견")
            except (urllib.error.URLError, TimeoutError) as e:
                print(f"  ! {app.get('name')} ({app_id}) — fetch 실패: {e} (캐시 사용)")
        app["_store"] = store
    save_cache(cache)
    return apps


# ---------------------------------------------------------------- 렌더링

# KR 스토어 장르명 → 영어 (US 스토어 미출시 앱 폴백용)
GENRE_EN = {
    "생산성": "Productivity",
    "유틸리티": "Utilities",
    "라이프스타일": "Lifestyle",
    "음악": "Music",
    "교육": "Education",
    "건강 및 피트니스": "Health & Fitness",
    "엔터테인먼트": "Entertainment",
    "그래픽 및 디자인": "Graphics & Design",
    "여행": "Travel",
    "음식 및 음료": "Food & Drink",
    "금융": "Finance",
    "내비게이션": "Navigation",
    "소셜 네트워킹": "Social Networking",
    "사진 및 비디오": "Photo & Video",
    "개발자 도구": "Developer Tools",
    "비즈니스": "Business",
    "의학": "Medical",
    "날씨": "Weather",
    "게임": "Games",
    "도서": "Books",
    "뉴스": "News",
    "스포츠": "Sports",
    "쇼핑": "Shopping",
    "참고": "Reference",
}

PRICE_EN = {"무료": "Free"}


def bi(ko, en=None):
    """한/영 병기 span 쌍. html[data-lang=en] 일 때 .le 만 보인다. en 이 없으면 ko 를 그대로 사용."""
    ko = ko or ""
    en = en or ko
    return f'<span class="lk">{escape(ko)}</span><span class="le">{escape(en)}</span>'


def first_sentence(text, limit=110):
    if not text:
        return ""
    text = text.strip().split("\n")[0]
    if len(text) > limit:
        text = text[:limit].rstrip() + "…"
    return text


def stars(rating):
    if not rating:
        return ""
    full = int(round(rating))
    return "★" * full + "☆" * (5 - full)


def render_card(app, copy=None, copy_en=None):
    copy = copy or {}
    copy_en = copy_en or {}
    store = app.get("_store") or {}
    name = app.get("name") or store.get("trackName") or app["_slug"]
    name_en = app.get("nameEn") or store.get("trackName_en") or ""
    icon = store.get("icon")
    genre = store.get("genre") or (app.get("categories") or [""])[0]
    genre_en = store.get("genre_en") or GENRE_EN.get(genre, genre)
    price = store.get("price")
    if price is None:
        p = app.get("price") or {}
        price = "무료" if p.get("isFree") else (f"₩{p['krw']:,}" if p.get("krw") else "")
    price_en = store.get("price_en") or PRICE_EN.get(price, price)
    desc = first_sentence(store.get("description") or app.get("description") or app.get("notes"))
    desc_en = first_sentence(store.get("description_en")) or desc
    rating = store.get("rating")
    rating_count = store.get("ratingCount") or 0
    appstore_url = store.get("url") or app.get("appStoreUrl")
    support = app.get("supportUrl")

    released = bool(appstore_url)
    tagline = copy.get("tagline") or ""

    head_icon_html = (
        f'<img class="ex-head-icon" src="{escape(icon)}" alt="{escape(name)}" loading="lazy">'
        if icon
        else f'<div class="ex-head-icon icon-fallback">{escape(name[:1])}</div>'
    )

    # 비주얼 패널: 로컬(시뮬레이터) 스크린샷 우선 → 스토어 스크린샷 → 아이콘 포스터
    local = local_shots(app["_slug"])
    shots = local[:3] if local else [s for s in (store.get("screenshots") or []) if s][:3]
    if shots:
        shots_html = "".join(
            f'<img class="shot" src="{escape(s)}" alt="{escape(name)} 스크린샷" loading="lazy">'
            for s in shots
        )
        visual_html = f'<div class="ex-visual ex-shots shots-{len(shots)}">{shots_html}</div>'
    else:
        big_icon = (
            f'<img class="ex-icon" src="{escape(icon)}" alt="{escape(name)}" loading="lazy">'
            if icon
            else f'<div class="ex-icon icon-fallback">{escape(name[:1])}</div>'
        )
        hook = copy.get("hook")
        poster_tag = (
            f'<p class="poster-tagline">{bi(hook, copy_en.get("hook"))}</p>' if hook else ""
        )
        price_badge = (
            f'<span class="poster-price">{bi(price, price_en)}</span>' if price else ""
        )
        hue = 0
        for ch in app["_slug"]:
            hue = (hue * 31 + ord(ch)) % 360
        visual_html = f"""<div class="ex-visual ex-poster" style="--booth-h:{hue}">
        <div class="poster-icon-wrap">{big_icon}</div>
        <p class="poster-name">{bi(name, name_en or name)}</p>
        {poster_tag}
        {price_badge}
      </div>"""

    meta = []
    if genre:
        meta.append(f'<span class="chip">{bi(genre, genre_en)}</span>')
    if price:
        meta.append(f'<span class="chip chip-price">{bi(price, price_en)}</span>')
    if not released:
        meta.append(f'<span class="chip chip-soon">{bi("준비 중", "Coming soon")}</span>')
    meta_html = f'<div class="meta">{"".join(meta)}</div>' if meta else ""

    tagline_html = (
        f'<p class="tagline">{bi(tagline, copy_en.get("tagline"))}</p>' if tagline else ""
    )

    highlight = copy.get("highlight")
    highlight_html = (
        f'<p class="highlight"><span class="highlight-star">✦</span>{bi(highlight, copy_en.get("highlight"))}</p>'
        if highlight
        else ""
    )

    # 스토리: 문제 → 솔루션
    story_parts = []
    if copy.get("problem"):
        story_parts.append(
            f'<div class="story-item story-problem"><span class="story-tag">{bi("문제", "Problem")}</span>'
            f'<p>{bi(copy["problem"], copy_en.get("problem"))}</p></div>'
        )
    if copy.get("solution"):
        story_parts.append(
            f'<div class="story-item story-solution"><span class="story-tag">{bi("솔루션", "Solution")}</span>'
            f'<p>{bi(copy["solution"], copy_en.get("solution"))}</p></div>'
        )
    story_html = f'<div class="story">{"".join(story_parts)}</div>' if story_parts else ""

    # 대상 · 맥락 스트립
    who_rows = []
    for label, label_en, key in (
        ("페르소나", "Persona", "persona"),
        ("상황", "Context", "context"),
        ("스테이크홀더", "Stakeholders", "stakeholders"),
    ):
        val = copy.get(key)
        if val:
            who_rows.append(
                f'<div class="who-item"><dt>{bi(label, label_en)}</dt>'
                f'<dd>{bi(val, copy_en.get(key))}</dd></div>'
            )
    who_html = f'<div class="who">{"".join(who_rows)}</div>' if who_rows else ""

    rating_html = ""
    if rating:
        rating_html = (
            f'<div class="rating"><span class="stars">{stars(rating)}</span>'
            f'<span class="rating-num">{rating:.1f}</span>'
            f'<span class="rating-count">({rating_count:,})</span></div>'
        )

    links = []
    if appstore_url:
        links.append(
            f'<a class="btn btn-store" href="{escape(appstore_url)}" target="_blank" rel="noopener">{bi("App Store에서 보기", "View on the App Store")}</a>'
        )
    if support:
        links.append(
            f'<a class="btn btn-ghost" href="{escape(support)}" target="_blank" rel="noopener">{bi("자세한 설명 보기", "Learn more")}</a>'
        )
    links_html = f'<div class="links">{"".join(links)}</div>' if links else ""

    # 부제: 한국어 모드에서는 영어 이름, 영어 모드에서는 한국어 이름
    name_en_html = (
        f'<p class="name-en">{bi(name_en, name)}</p>' if name_en and name_en != name else ""
    )
    desc_html = f'<p class="desc">{bi(desc, desc_en)}</p>' if desc else ""

    return f"""
    <article class="exhibit" id="app-{app['_slug']}">
      {visual_html}
      <div class="ex-content">
        <div class="ex-head">
          {head_icon_html}
          <div class="ex-title">
            <h3>{bi(name, name_en or name)}</h3>
            {name_en_html}
            {rating_html}
          </div>
        </div>
        {meta_html}
        {tagline_html}
        {highlight_html}
        {desc_html}
        {story_html}
        {who_html}
        {links_html}
      </div>
    </article>"""


def render(apps, content=None, content_en=None):
    content = content or {"groups": [], "apps": {}}
    content_en = content_en or {"groups": [], "apps": {}}
    copy_map = content.get("apps", {})
    copy_map_en = content_en.get("apps", {})
    groups_en = content_en.get("groups", [])
    by_slug = {a["_slug"]: a for a in apps}

    released = [a for a in apps if (a.get("_store") or {}).get("url")]

    def showable(app):
        # 스토어에 있거나, 큐레이션 카피가 있는 앱(예: 준비 중인 개발자 도구)만 노출
        return bool((app.get("_store") or {}).get("url")) or bool(
            copy_map.get(app["_slug"])
        )

    # 카테고리 그룹 순서대로 섹션 구성 (+ 문제 목차 수집)
    section_blocks = []
    toc_blocks = []
    grouped_slugs = set()
    for gi, group in enumerate(content.get("groups", [])):
        group_en = groups_en[gi] if gi < len(groups_en) else {}
        cards = []
        toc_items = []
        for slug in group.get("slugs", []):
            app = by_slug.get(slug)
            if not app or not showable(app):
                continue
            grouped_slugs.add(slug)
            copy = copy_map.get(slug) or {}
            copy_en = copy_map_en.get(slug) or {}
            cards.append(render_card(app, copy, copy_en))
            name = app.get("name") or (app.get("_store") or {}).get("trackName") or slug
            name_en = app.get("nameEn") or (app.get("_store") or {}).get("trackName_en") or name
            hook = copy.get("hook") or copy.get("problem") or name
            hook_en = copy_en.get("hook") or copy_en.get("problem") or name_en
            toc_items.append(
                f'<a class="toc-item" href="#app-{slug}">'
                f'<span class="toc-hook">{bi(hook, hook_en)}</span>'
                f'<span class="toc-app">{bi(name, name_en)} →</span></a>'
            )
        if not cards:
            continue
        intro = group.get("intro", "")
        intro_html = (
            f'<p class="cat-intro">{bi(intro, group_en.get("intro"))}</p>' if intro else ""
        )
        title_html = bi(group.get("title", ""), group_en.get("title"))
        section_blocks.append(
            f"""
    <section class="category">
      <div class="cat-head">
        <h2>{title_html}</h2>
        {intro_html}
        <span class="cat-count">{len(cards)}</span>
      </div>
      <div class="exhibits">{"".join(cards)}</div>
    </section>"""
        )
        toc_blocks.append(
            f"""
      <div class="toc-group">
        <h3>{title_html}</h3>
        <div class="toc-list">{"".join(toc_items)}</div>
      </div>"""
        )

    toc_html = (
        f"""
    <section class="toc">
      <div class="toc-head">
        <h2>{bi("이런 고민, 없으세요?", "Sound familiar?")}</h2>
        <p>{bi("공감 가는 문제를 누르면 그걸 푸는 앱으로 바로 이동합니다.", "Tap a problem you relate to and jump straight to the app that solves it.")}</p>
      </div>
      <div class="toc-groups">{"".join(toc_blocks)}</div>
    </section>"""
        if toc_blocks
        else ""
    )

    # 그룹에 빠진 출시작이 있으면 '그 외' 섹션으로 보강 (누락 방지)
    leftovers = [
        a
        for a in released
        if a["_slug"] not in grouped_slugs
    ]
    leftovers.sort(key=lambda a: a.get("name") or "")
    if leftovers:
        cards = "".join(
            render_card(a, copy_map.get(a["_slug"]), copy_map_en.get(a["_slug"]))
            for a in leftovers
        )
        section_blocks.append(
            f"""
    <section class="category">
      <div class="cat-head">
        <h2>{bi("✨ 그 외", "✨ More")}</h2>
        <span class="cat-count">{len(leftovers)}</span>
      </div>
      <div class="exhibits">{cards}</div>
    </section>"""
        )

    sections_html = "\n".join(section_blocks)

    total = len(apps)
    released_n = len(released)
    category_n = len([b for b in content.get("groups", []) if b.get("slugs")])
    rated = [a for a in released if (a.get("_store") or {}).get("rating")]
    avg_rating = (
        sum((a["_store"]["rating"]) for a in rated) / len(rated) if rated else 0
    )
    updated = datetime.now(KST).strftime("%Y-%m-%d")

    avg_stat = (
        f"""<div class="stat"><span class="stat-num">{avg_rating:.1f}</span><span class="stat-label">{bi("평균 평점", "Avg. Rating")}</span></div>"""
        if avg_rating
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="ko" data-lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>App Portfolio — hyunho lee</title>
<meta name="description" content="hyunho lee 가 만든 iOS / macOS 앱 포트폴리오">
<meta property="og:title" content="App Portfolio — hyunho lee">
<meta property="og:description" content="iOS / macOS 앱 {released_n}종을 소개합니다.">
<meta property="og:type" content="website">
<style>
  :root {{
    --bg: #0b0d12;
    --bg-soft: #151821;
    --card: #1a1e29;
    --border: #262b38;
    --text: #e8eaf0;
    --muted: #8b90a0;
    --accent: #5b8def;
    --accent-2: #a78bfa;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html {{ -webkit-text-size-adjust: 100%; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Apple SD Gothic Neo", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
  }}
  img {{ max-width: 100%; }}
  a {{ color: inherit; text-decoration: none; }}
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 0 20px; }}

  /* 언어 전환: 기본 한국어(.lk), data-lang=en 이면 영어(.le) */
  .le {{ display: none; }}
  html[data-lang="en"] .lk {{ display: none; }}
  html[data-lang="en"] .le {{ display: inline; }}

  .lang-toggle {{
    position: fixed; top: 14px; right: 14px; z-index: 60;
    display: flex; gap: 2px; padding: 3px; border-radius: 999px;
    background: rgba(21,24,33,.88); border: 1px solid var(--border);
    backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 6px 20px rgba(0,0,0,.35);
  }}
  .lang-btn {{
    font-family: inherit; font-size: .78rem; font-weight: 700; color: var(--muted);
    background: transparent; border: 0; padding: 5px 13px; border-radius: 999px; cursor: pointer;
    transition: color .15s;
  }}
  .lang-btn:hover {{ color: var(--text); }}
  html[data-lang="ko"] .lang-btn[data-set-lang="ko"],
  html[data-lang="en"] .lang-btn[data-set-lang="en"] {{
    background: linear-gradient(120deg, var(--accent), var(--accent-2)); color: #fff;
  }}

  header.hero {{
    text-align: center;
    padding: 80px 20px 50px;
    background:
      radial-gradient(800px 400px at 50% -10%, rgba(91,141,239,.25), transparent),
      radial-gradient(600px 300px at 80% 0%, rgba(167,139,250,.18), transparent);
  }}
  .hero h1 {{
    font-size: clamp(2.2rem, 5vw, 3.4rem);
    font-weight: 800;
    letter-spacing: -.02em;
    background: linear-gradient(120deg, var(--accent), var(--accent-2));
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .hero p {{ color: var(--muted); margin-top: 14px; font-size: 1.1rem; }}

  .stats {{ display: flex; justify-content: center; gap: 40px; margin-top: 36px; flex-wrap: wrap; }}
  .stat {{ display: flex; flex-direction: column; align-items: center; }}
  .stat-num {{ font-size: 2rem; font-weight: 800; color: var(--text); }}
  .stat-label {{ font-size: .85rem; color: var(--muted); }}

  main {{ padding: 30px 0 90px; }}

  /* 문제 목차 */
  .toc {{
    background: linear-gradient(160deg, var(--card), var(--bg-soft));
    border: 1px solid var(--border); border-radius: 24px;
    padding: 34px 30px; margin-top: 8px;
  }}
  .toc-head h2 {{ font-size: 1.5rem; font-weight: 800; letter-spacing: -.01em; }}
  .toc-head p {{ color: var(--muted); font-size: .95rem; margin-top: 6px; }}
  .toc-groups {{ margin-top: 24px; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px 30px; }}
  .toc-group h3 {{ font-size: 1rem; font-weight: 800; color: var(--text); padding-bottom: 8px; margin-bottom: 8px; border-bottom: 1px solid var(--border); }}
  .toc-list {{ display: flex; flex-direction: column; }}
  .toc-item {{
    display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;
    padding: 8px 8px; border-radius: 9px; transition: background .12s;
  }}
  .toc-item:hover {{ background: rgba(91,141,239,.10); }}
  .toc-hook {{ font-size: .9rem; color: var(--text); line-height: 1.4; }}
  .toc-item:hover .toc-hook {{ color: var(--accent); }}
  .toc-app {{ flex-shrink: 0; font-size: .74rem; font-weight: 700; color: var(--muted); white-space: nowrap; }}

  .exhibit {{ scroll-margin-top: 20px; }}

  .category {{ margin-top: 72px; }}
  .category:first-child {{ margin-top: 16px; }}
  .cat-head {{ display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; margin-bottom: 26px; padding-bottom: 14px; border-bottom: 1px solid var(--border); }}
  .cat-head h2 {{ font-size: 1.6rem; font-weight: 800; letter-spacing: -.01em; }}
  .cat-intro {{ color: var(--muted); font-size: .95rem; }}
  .cat-count {{ margin-left: auto; font-size: .8rem; font-weight: 700; color: var(--muted); background: var(--bg-soft); border: 1px solid var(--border); padding: 2px 11px; border-radius: 999px; }}

  .exhibits {{ display: flex; flex-direction: column; gap: 34px; }}

  .exhibit {{
    display: grid;
    grid-template-columns: 0.9fr 1.1fr;
    gap: 34px;
    align-items: center;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 30px;
    transition: border-color .2s ease, transform .2s ease, box-shadow .2s ease;
  }}
  .exhibit:hover {{ border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 18px 50px rgba(0,0,0,.35); }}
  .exhibit:nth-child(even) .ex-visual {{ order: 2; }}

  /* 비주얼 */
  .ex-visual {{ align-self: stretch; border-radius: 18px; overflow: hidden; display: flex; min-height: 300px; }}
  .ex-shots {{
    gap: 12px; padding: 22px; justify-content: center; align-items: center; flex-wrap: nowrap;
    background: radial-gradient(120% 120% at 50% 0%, rgba(91,141,239,.14), transparent), var(--bg-soft);
  }}
  .ex-shots .shot {{ min-width: 0; max-height: 360px; max-width: 100%; border-radius: 16px; box-shadow: 0 14px 36px rgba(0,0,0,.5); border: 1px solid var(--border); object-fit: contain; }}
  .shots-1 .shot {{ max-height: 400px; }}

  .ex-poster {{
    flex-direction: column; align-items: center; justify-content: center; text-align: center;
    gap: 16px; padding: 46px 28px;
    background:
      radial-gradient(130% 110% at 50% 0%, hsl(var(--booth-h, 220) 72% 58% / .30), transparent),
      radial-gradient(90% 90% at 80% 100%, hsl(calc(var(--booth-h, 220) + 40) 70% 55% / .16), transparent),
      linear-gradient(160deg, var(--bg-soft), var(--card));
  }}
  .poster-icon-wrap {{ position: relative; padding: 6px; border-radius: 32px; }}
  .poster-icon-wrap::before {{ content: ""; position: absolute; inset: -18px; border-radius: 50%;
    background: radial-gradient(circle, hsl(var(--booth-h, 220) 80% 65% / .35), transparent 70%); z-index: 0; }}
  .ex-poster .ex-icon {{ position: relative; z-index: 1; width: 116px; height: 116px; border-radius: 27px; object-fit: cover; box-shadow: 0 18px 44px rgba(0,0,0,.6); }}
  .poster-name {{ font-size: 1.5rem; font-weight: 800; letter-spacing: -.01em; }}
  .poster-tagline {{ color: var(--muted); font-size: .95rem; max-width: 320px; }}
  .poster-price {{ margin-top: 4px; font-size: .74rem; font-weight: 700; color: var(--text);
    background: rgba(255,255,255,.08); border: 1px solid var(--border); padding: 3px 12px; border-radius: 999px; }}

  .icon-fallback {{
    display: flex; align-items: center; justify-content: center;
    font-size: 2.4rem; font-weight: 800; color: #fff;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
  }}

  /* 콘텐츠 */
  .ex-content {{ min-width: 0; }}
  .ex-head {{ display: flex; gap: 14px; align-items: center; }}
  .ex-head-icon {{ width: 56px; height: 56px; border-radius: 14px; flex-shrink: 0; object-fit: cover; box-shadow: 0 4px 14px rgba(0,0,0,.4); font-size: 1.6rem; }}
  .ex-title h3 {{ font-size: 1.5rem; font-weight: 800; letter-spacing: -.01em; }}
  .name-en {{ color: var(--muted); font-size: .84rem; }}
  .rating {{ margin-top: 7px; font-size: .8rem; display: inline-flex; align-items: center; gap: 6px;
    background: rgba(245,179,1,.12); border: 1px solid rgba(245,179,1,.3); color: #f5b301;
    padding: 3px 10px; border-radius: 999px; }}
  .stars {{ color: #f5b301; letter-spacing: 1px; }}
  .rating-num {{ font-weight: 800; color: #f5c542; }}
  .rating-count {{ color: rgba(245,179,1,.7); }}

  .meta {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 16px; }}
  .chip {{
    font-size: .73rem; color: var(--muted);
    background: var(--bg-soft); border: 1px solid var(--border);
    padding: 3px 10px; border-radius: 999px;
  }}
  .chip-price {{ color: var(--text); }}
  .chip-soon {{ color: var(--accent-2); border-color: rgba(167,139,250,.4); }}

  .tagline {{ margin-top: 16px; font-size: 1.32rem; font-weight: 800; color: var(--text); letter-spacing: -.015em; line-height: 1.32; }}
  .highlight {{ margin-top: 10px; display: inline-flex; align-items: baseline; gap: 7px;
    font-size: .92rem; font-weight: 700; line-height: 1.4;
    color: var(--accent-2);
    background: linear-gradient(90deg, rgba(167,139,250,.14), rgba(91,141,239,.06));
    border: 1px solid rgba(167,139,250,.28); border-radius: 10px; padding: 8px 13px; }}
  .highlight-star {{ color: var(--accent-2); font-size: .85rem; }}
  .desc {{ color: var(--muted); font-size: .88rem; margin-top: 12px; }}

  /* 스토리: 문제 → 솔루션 */
  .story {{ margin-top: 20px; display: flex; flex-direction: column; gap: 10px; }}
  .story-item {{ padding: 13px 16px; border-radius: 13px; }}
  .story-item p {{ font-size: .93rem; line-height: 1.55; color: var(--text); margin-top: 5px; }}
  .story-tag {{ display: inline-block; font-size: .68rem; font-weight: 800; letter-spacing: .06em; padding: 2px 9px; border-radius: 6px; }}
  .story-problem {{ background: rgba(240,119,106,.08); border: 1px solid rgba(240,119,106,.22); }}
  .story-problem .story-tag {{ background: rgba(240,119,106,.16); color: #f0776a; }}
  .story-solution {{ background: rgba(79,209,165,.08); border: 1px solid rgba(79,209,165,.22); }}
  .story-solution .story-tag {{ background: rgba(79,209,165,.16); color: #4fd1a5; }}

  /* 대상 · 맥락 스트립 */
  .who {{ margin-top: 18px; display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 14px; padding-top: 18px; border-top: 1px solid var(--border); }}
  .who-item dt {{ font-size: .7rem; font-weight: 700; color: var(--accent-2); letter-spacing: .03em; margin-bottom: 4px; }}
  .who-item dd {{ margin: 0; font-size: .82rem; color: var(--text); line-height: 1.45; }}

  .links {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 22px; }}
  .btn {{
    text-align: center; font-size: .86rem; font-weight: 700;
    padding: 11px 22px; border-radius: 11px; transition: opacity .15s, transform .15s;
  }}
  .btn:hover {{ opacity: .9; transform: translateY(-1px); }}
  .btn-store {{ background: linear-gradient(120deg, var(--accent), var(--accent-2)); color: #fff; }}
  .btn-ghost {{ background: var(--bg-soft); border: 1px solid var(--border); color: var(--text); }}

  @media (max-width: 780px) {{
    header.hero {{ padding: 56px 18px 36px; }}
    .hero p {{ font-size: 1rem; }}
    .stats {{ gap: 22px; margin-top: 26px; }}
    .stat-num {{ font-size: 1.6rem; }}

    .toc {{ padding: 24px 18px; }}
    .toc-head h2 {{ font-size: 1.3rem; }}
    .toc-head p {{ font-size: .9rem; }}
    .toc-groups {{ gap: 20px 24px; margin-top: 20px; }}

    .category {{ margin-top: 48px; }}
    .cat-head {{ margin-bottom: 20px; }}
    .cat-head h2 {{ font-size: 1.35rem; }}
    .exhibits {{ gap: 24px; }}

    .exhibit {{ grid-template-columns: 1fr; gap: 18px; padding: 18px; border-radius: 20px; }}
    .exhibit:nth-child(even) .ex-visual {{ order: 0; }}
    .ex-visual {{ min-height: 0; }}
    .ex-poster {{ padding: 36px 20px; }}
    .ex-poster .ex-icon {{ width: 92px; height: 92px; }}
    /* 스크린샷 여러 장은 가로 스와이프 */
    .ex-shots {{ padding: 16px; gap: 10px; justify-content: flex-start; overflow-x: auto; -webkit-overflow-scrolling: touch; }}
    .ex-shots .shot {{ max-height: 340px; flex: 0 0 auto; }}
    .shots-1 {{ justify-content: center; }}
    .shots-1 .shot {{ max-height: 380px; }}

    .tagline {{ font-size: 1.12rem; }}
    .ex-title h3 {{ font-size: 1.28rem; }}
    .who {{ grid-template-columns: 1fr 1fr; gap: 10px 16px; }}
    .links .btn {{ flex: 1 1 auto; }}
  }}

  @media (max-width: 440px) {{
    .wrap {{ padding: 0 14px; }}
    header.hero {{ padding: 44px 14px 28px; }}
    .hero h1 {{ font-size: 2rem; }}
    .stats {{ gap: 14px; }}
    .toc {{ padding: 20px 15px; border-radius: 18px; }}
    .toc-groups {{ grid-template-columns: 1fr; }}
    .toc-app {{ font-size: .7rem; }}
    .exhibit {{ padding: 15px; }}
    .who {{ grid-template-columns: 1fr; }}
    .btn {{ padding: 11px 14px; font-size: .82rem; }}
  }}

  .soon {{ margin-top: 56px; text-align: center; }}
  .soon h2 {{ font-size: 1.2rem; color: var(--muted); font-weight: 600; margin-bottom: 16px; }}
  .soon-list {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }}
  .soon-chip {{
    font-size: .85rem; color: var(--muted);
    background: var(--bg-soft); border: 1px dashed var(--border);
    padding: 6px 14px; border-radius: 999px;
  }}

  footer {{ text-align: center; color: var(--muted); font-size: .82rem; padding: 40px 20px 60px; border-top: 1px solid var(--border); }}
  footer a {{ color: var(--accent); }}
</style>
</head>
<body>
  <div class="lang-toggle" role="group" aria-label="언어 선택 / Language">
    <button type="button" class="lang-btn" data-set-lang="ko">한국어</button>
    <button type="button" class="lang-btn" data-set-lang="en">EN</button>
  </div>
  <header class="hero">
    <div class="wrap">
      <h1>App Portfolio</h1>
      <p>{bi("hyunho lee 가 만든 iOS · macOS 앱 — 누가 · 언제 · 어떻게 쓰면 좋은지 카테고리별로 소개합니다.", "iOS · macOS apps built by hyunho lee — organized by category, with who, when, and how to use each one.")}</p>
      <div class="stats">
        <div class="stat"><span class="stat-num">{released_n}</span><span class="stat-label">{bi("출시 앱", "Released Apps")}</span></div>
        <div class="stat"><span class="stat-num">{category_n}</span><span class="stat-label">{bi("카테고리", "Categories")}</span></div>
        {avg_stat}
        <div class="stat"><span class="stat-num">{total}</span><span class="stat-label">{bi("전체 프로젝트", "Total Projects")}</span></div>
      </div>
    </div>
  </header>

  <main>
    <div class="wrap">
      {toc_html}
      {sections_html}
    </div>
  </main>

  <footer>
    <p>{bi(f"마지막 업데이트 {updated}", f"Last updated {updated}")} · <a href="https://github.com/M1zz/app-portfolio" target="_blank" rel="noopener">GitHub</a></p>
  </footer>

  <script>
  (function () {{
    var root = document.documentElement;
    function apply(lang) {{
      root.setAttribute('data-lang', lang);
      root.setAttribute('lang', lang === 'en' ? 'en' : 'ko');
    }}
    var saved = null;
    try {{ saved = localStorage.getItem('portfolio-lang'); }} catch (e) {{}}
    var lang = (saved === 'ko' || saved === 'en')
      ? saved
      : ((navigator.language || '').toLowerCase().indexOf('ko') === 0 ? 'ko' : 'en');
    apply(lang);
    var btns = document.querySelectorAll('.lang-btn');
    for (var i = 0; i < btns.length; i++) {{
      btns[i].addEventListener('click', function () {{
        var l = this.getAttribute('data-set-lang');
        apply(l);
        try {{ localStorage.setItem('portfolio-lang', l); }} catch (e) {{}}
      }});
    }}
  }})();
  </script>
</body>
</html>
"""


README_FILE = ROOT / "README.md"
APPS_START = "<!-- APPS:START -->"
APPS_END = "<!-- APPS:END -->"


def render_readme_section(apps):
    released = [a for a in apps if (a.get("_store") or {}).get("url")]
    released.sort(
        key=lambda a: (
            -(((a.get("_store") or {}).get("ratingCount")) or 0),
            a.get("name") or "",
        )
    )
    upcoming = [a for a in apps if a not in released]

    lines = [
        APPS_START,
        "<!-- 이 섹션은 `python3 scripts/build-portfolio-site.py` 실행 시 자동 생성됩니다. -->",
        "",
        "| | 앱 | 분류 | 평점 | 가격 |",
        "|:--:|---|---|---|---|",
    ]
    for a in released:
        s = a["_store"]
        icon = s.get("icon")
        icon_md = (
            f'<img src="{icon}" width="44" height="44" style="border-radius:10px">'
            if icon
            else ""
        )
        name = a.get("name") or s.get("trackName") or a["_slug"]
        name_en = a.get("nameEn")
        name_cell = f"**[{name}]({s['url']})**"
        if name_en and name_en != name:
            name_cell += f"<br><sub>{name_en}</sub>"
        genre = s.get("genre") or "-"
        rating = s.get("rating")
        rating_cell = (
            f"⭐ {rating:.1f} ({s.get('ratingCount') or 0:,})" if rating else "–"
        )
        price = s.get("price") or "-"
        lines.append(f"| {icon_md} | {name_cell} | {genre} | {rating_cell} | {price} |")

    lines += [
        "",
        f"> 🌐 전체 쇼케이스 보기 → **https://M1zz.github.io/app-portfolio/**",
        APPS_END,
    ]
    return "\n".join(lines)


def update_readme(apps):
    if not README_FILE.exists():
        return
    text = README_FILE.read_text(encoding="utf-8")
    if APPS_START not in text or APPS_END not in text:
        print("   ⚠️ README 마커 없음 — 건너뜀")
        return
    pre = text.split(APPS_START)[0]
    post = text.split(APPS_END)[1]
    new_text = pre + render_readme_section(apps) + post
    if new_text != text:
        README_FILE.write_text(new_text, encoding="utf-8")
        print("   ✓ README.md 앱 목록 갱신")


def main():
    fetch = "--no-fetch" not in sys.argv
    print("📦 앱 데이터 로드 중...")
    apps = load_apps()
    print(f"   {len(apps)}개 앱 발견")
    print("🌐 앱스토어 정보 수집 중..." if fetch else "💾 캐시 사용 (--no-fetch)")
    apps = enrich(apps, fetch=fetch)
    content = load_content()
    content_en = load_content_en()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html = render(apps, content, content_en)
    OUT_FILE.write_text(html, encoding="utf-8")
    update_readme(apps)
    released = sum(1 for a in apps if (a.get("_store") or {}).get("url"))
    print(f"✅ 생성 완료: {OUT_FILE.relative_to(ROOT)} (출시 {released} / 전체 {len(apps)})")


if __name__ == "__main__":
    main()
