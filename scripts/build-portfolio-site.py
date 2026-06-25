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


def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, encoding="utf-8") as fp:
            return json.load(fp)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as fp:
        json.dump(cache, fp, ensure_ascii=False, indent=2)


COUNTRIES = ("kr", "us", "jp")


def fetch_appstore(app_id):
    """여러 국가 스토어를 순차 조회 (KR → US → JP)."""
    r = None
    for country in COUNTRIES:
        url = f"https://itunes.apple.com/lookup?id={app_id}&country={country}"
        req = urllib.request.Request(url, headers={"User-Agent": "portfolio-site-builder"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
        if data.get("resultCount"):
            r = data["results"][0]
            break
    if r is None:
        return None
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


def render_card(app):
    store = app.get("_store") or {}
    name = app.get("name") or store.get("trackName") or app["_slug"]
    name_en = app.get("nameEn") or ""
    icon = store.get("icon")
    genre = store.get("genre") or (app.get("categories") or [""])[0]
    price = store.get("price")
    if price is None:
        p = app.get("price") or {}
        price = "무료" if p.get("isFree") else (f"₩{p['krw']:,}" if p.get("krw") else "")
    desc = first_sentence(store.get("description") or app.get("description") or app.get("notes"))
    rating = store.get("rating")
    rating_count = store.get("ratingCount") or 0
    appstore_url = store.get("url") or app.get("appStoreUrl")
    github = app.get("githubRepo")

    icon_html = (
        f'<img class="icon" src="{escape(icon)}" alt="{escape(name)}" loading="lazy">'
        if icon
        else f'<div class="icon icon-fallback">{escape(name[:1])}</div>'
    )

    meta = []
    if genre:
        meta.append(f'<span class="chip">{escape(genre)}</span>')
    if price:
        meta.append(f'<span class="chip chip-price">{escape(price)}</span>')
    meta_html = f'<div class="meta">{"".join(meta)}</div>' if meta else ""

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
            f'<a class="btn btn-store" href="{escape(appstore_url)}" target="_blank" rel="noopener">App Store</a>'
        )
    if github:
        links.append(
            f'<a class="btn btn-ghost" href="{escape(github)}" target="_blank" rel="noopener">GitHub</a>'
        )
    links_html = f'<div class="links">{"".join(links)}</div>' if links else ""

    name_en_html = f'<p class="name-en">{escape(name_en)}</p>' if name_en else ""
    desc_html = f'<p class="desc">{escape(desc)}</p>' if desc else ""

    return f"""
    <article class="card">
      <div class="card-head">
        {icon_html}
        <div class="card-title">
          <h3>{escape(name)}</h3>
          {name_en_html}
          {rating_html}
        </div>
      </div>
      {meta_html}
      {desc_html}
      {links_html}
    </article>"""


def render(apps):
    released = [a for a in apps if (a.get("_store") or {}).get("url")]
    upcoming = [a for a in apps if a not in released]

    # 출시작은 평점순 → 이름순으로 정렬
    released.sort(
        key=lambda a: (
            -(((a.get("_store") or {}).get("ratingCount")) or 0),
            a.get("name") or "",
        )
    )

    total = len(apps)
    released_n = len(released)
    rated = [a for a in released if (a.get("_store") or {}).get("rating")]
    avg_rating = (
        sum((a["_store"]["rating"]) for a in rated) / len(rated) if rated else 0
    )
    updated = datetime.now(KST).strftime("%Y-%m-%d")

    cards = "\n".join(render_card(a) for a in released)

    upcoming_html = ""
    if upcoming:
        chips = "".join(
            f'<span class="soon-chip">{escape(a.get("name") or a["_slug"])}</span>'
            for a in upcoming
        )
        upcoming_html = f"""
    <section class="soon">
      <h2>곧 출시</h2>
      <div class="soon-list">{chips}</div>
    </section>"""

    avg_stat = (
        f"""<div class="stat"><span class="stat-num">{avg_rating:.1f}</span><span class="stat-label">평균 평점</span></div>"""
        if avg_rating
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="ko">
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
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Apple SD Gothic Neo", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }}
  a {{ color: inherit; text-decoration: none; }}
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 0 20px; }}

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

  main {{ padding: 30px 0 80px; }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 18px;
  }}
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px;
    transition: transform .15s ease, border-color .15s ease;
  }}
  .card:hover {{ transform: translateY(-3px); border-color: var(--accent); }}
  .card-head {{ display: flex; gap: 14px; align-items: center; }}
  .icon {{ width: 62px; height: 62px; border-radius: 14px; flex-shrink: 0; object-fit: cover; box-shadow: 0 4px 14px rgba(0,0,0,.4); }}
  .icon-fallback {{
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem; font-weight: 800; color: #fff;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
  }}
  .card-title h3 {{ font-size: 1.15rem; font-weight: 700; }}
  .name-en {{ color: var(--muted); font-size: .82rem; }}
  .rating {{ margin-top: 4px; font-size: .8rem; display: flex; align-items: center; gap: 6px; }}
  .stars {{ color: #f5b301; letter-spacing: 1px; }}
  .rating-num {{ font-weight: 700; }}
  .rating-count {{ color: var(--muted); }}
  .meta {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 14px; }}
  .chip {{
    font-size: .73rem; color: var(--muted);
    background: var(--bg-soft); border: 1px solid var(--border);
    padding: 3px 10px; border-radius: 999px;
  }}
  .chip-price {{ color: var(--text); }}
  .desc {{ color: var(--muted); font-size: .9rem; margin-top: 12px; min-height: 1.2em; }}
  .links {{ display: flex; gap: 8px; margin-top: 16px; }}
  .btn {{
    flex: 1; text-align: center; font-size: .85rem; font-weight: 600;
    padding: 9px 12px; border-radius: 10px; transition: opacity .15s;
  }}
  .btn:hover {{ opacity: .85; }}
  .btn-store {{ background: linear-gradient(120deg, var(--accent), var(--accent-2)); color: #fff; }}
  .btn-ghost {{ background: var(--bg-soft); border: 1px solid var(--border); color: var(--text); }}

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
  <header class="hero">
    <div class="wrap">
      <h1>App Portfolio</h1>
      <p>hyunho lee 가 만든 iOS · macOS 앱들</p>
      <div class="stats">
        <div class="stat"><span class="stat-num">{released_n}</span><span class="stat-label">출시 앱</span></div>
        {avg_stat}
        <div class="stat"><span class="stat-num">{total}</span><span class="stat-label">전체 프로젝트</span></div>
      </div>
    </div>
  </header>

  <main>
    <div class="wrap">
      <div class="grid">
        {cards}
      </div>
      {upcoming_html}
    </div>
  </main>

  <footer>
    <p>마지막 업데이트 {updated} · <a href="https://github.com/M1zz/app-portfolio" target="_blank" rel="noopener">GitHub</a></p>
  </footer>
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

    if upcoming:
        names = ", ".join(a.get("name") or a["_slug"] for a in upcoming)
        lines += ["", f"> 🚧 **곧 출시**: {names}"]

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
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html = render(apps)
    OUT_FILE.write_text(html, encoding="utf-8")
    update_readme(apps)
    released = sum(1 for a in apps if (a.get("_store") or {}).get("url"))
    print(f"✅ 생성 완료: {OUT_FILE.relative_to(ROOT)} (출시 {released} / 전체 {len(apps)})")


if __name__ == "__main__":
    main()
