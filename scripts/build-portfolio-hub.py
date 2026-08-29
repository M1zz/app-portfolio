#!/usr/bin/env python3
"""포트폴리오 허브·수명주기 페이지 생성.

사용법:
  python3 scripts/build-portfolio-hub.py

출력 3종:
  docs/hub.html               공개 허브 — 쇼케이스·수명주기·앱별 지원페이지 (GitHub Pages 배포)
  docs/lifecycle.html         공개 수명주기 — 제품 여정 5단계 (GitHub Pages 배포)
  reports/portfolio-hub.html  내부 허브 — 위 + 아티팩트·로컬 파일 링크 (비배포)

⚠️ docs/ 는 통째로 공개된다. 공개 페이지에는 다음을 넣지 않는다:
  · 아티팩트 URL (기본 비공개지만 링크를 알면 열리므로 사실상 전체 공개가 된다)
  · 수명주기 하위 등급 A/B/C(개선 중·소강·정지) — 내부 트리아지 표현
  · 폐기(stage 0) 앱
  · file:// 로컬 경로

데이터 출처:
  scripts/hub-links.json          수동 관리 링크(개요·아티팩트)
  Data/apps/*.json                supportUrl · lifecycle (자동 수집)
"""
import glob
import html
import json
import os
from datetime import date
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "projects/PortfolioCEO/PortfolioCEO/Data/apps")
REPORTS = os.path.join(ROOT, "reports")
DOCS = os.path.join(ROOT, "docs")
SITE = "https://m1zz.github.io/app-portfolio/"

HOSTS = {
    "m1zz.github.io": ("GitHub Pages", "#5b8def"),
    "leeo75.notion.site": ("Notion", "#a78bfa"),
    "www.notion.so": ("Notion", "#a78bfa"),
    "dev200ok.blogspot.com": ("Blogspot", "#d6a01e"),
    "www.blogger.com": ("Blogspot", "#d6a01e"),
    "developeracademy-postech.github.io": ("POSTECH Pages", "#1fa878"),
}

# 공개용 단계 설명 — 내부 트리아지 어휘(정지·소강·방치)를 쓰지 않는다.
STAGES = [
    (5, "Maturity", "안정적으로 자리 잡은 단계",
     "사용자와 매출이 안정적으로 유지되어, 새로 만들기보다 다듬고 지키는 데 집중합니다."),
    (4, "Growth", "사용자를 넓히는 단계",
     "제품이 통한다는 확신 위에서, 알리는 채널에 힘을 싣습니다."),
    (3, "Product–Market Fit 탐색", "반응을 받아 다듬는 단계",
     "실제 사용자의 반응이 도착했고, 그 반응을 근거로 제품을 고쳐 나갑니다."),
    (2, "Problem–Solution Fit", "제 몫을 하기 시작한 단계",
     "출시 뒤에도 오래 손봐서, 문제를 푸는 도구로 자리를 잡았습니다. 이제 쓰는 사람의 반응을 기다립니다."),
    (1, "Pre-MVP", "완성해 가는 단계",
     "App Store에 올려 두고 다듬는 중입니다. 올렸다고 다 만든 것은 아니라서, "
     "‘이만하면 됐다’ 싶은 모습까지는 아직 손볼 곳이 남아 있습니다."),
]
TIER_KR = {"A": "개선 중", "B": "소강", "C": "정지"}

CSS_TOKENS = """
  :root{--bg:#0b0d12;--bg-soft:#151821;--card:#1a1e29;--border:#262b38;--text:#e8eaf0;
    --muted:#8b90a0;--accent:#5b8def;--accent-2:#a78bfa;--ok:#34c48a;--warn:#e0a53a;
    color-scheme:dark}
  html[data-theme=light]{--bg:#f6f7fb;--bg-soft:#edeff6;--card:#fff;--border:#e2e5ee;
    --text:#1c2030;--muted:#5d6474;color-scheme:light}
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Apple SD Gothic Neo",Roboto,sans-serif;
    background:var(--bg);color:var(--text);line-height:1.65;-webkit-font-smoothing:antialiased}
  .wrap{max-width:1000px;margin:0 auto;padding:0 22px}
  .theme-btn{position:fixed;top:14px;right:14px;z-index:9;background:var(--card);color:var(--text);
    border:1px solid var(--border);border-radius:999px;padding:7px 13px;font-size:13px;cursor:pointer}
  header.hero{padding:66px 0 34px;background:
    radial-gradient(120% 130% at 50% 0%,rgba(91,141,239,.15),transparent),var(--bg-soft);
    border-bottom:1px solid var(--border)}
  .eyebrow{font-size:.72rem;letter-spacing:.13em;text-transform:uppercase;color:var(--muted);font-weight:700}
  h1{margin:9px 0 8px;font-size:2.1rem;letter-spacing:-.02em;line-height:1.2;
    background:linear-gradient(120deg,var(--accent),var(--accent-2));
    -webkit-background-clip:text;background-clip:text;color:transparent}
  .hero p{color:var(--muted);font-size:1rem;max-width:640px}
  nav.bar{display:flex;gap:8px;flex-wrap:wrap;margin-top:20px}
  nav.bar a{font-size:.83rem;font-weight:700;text-decoration:none;color:var(--text);
    background:var(--card);border:1px solid var(--border);padding:7px 13px;border-radius:999px}
  nav.bar a:hover{border-color:var(--accent);color:var(--accent)}
  nav.bar a.on{background:linear-gradient(120deg,var(--accent),var(--accent-2));color:#fff;border-color:transparent}
  main{padding:44px 0 30px}
  section{margin-bottom:46px}
  h2{font-size:1.18rem;display:flex;align-items:center;gap:9px;margin-bottom:5px}
  .lead{color:var(--muted);font-size:.9rem;margin-bottom:17px;max-width:680px}
  .hc{margin-left:auto;font-size:.72rem;font-weight:700;color:var(--muted);
    background:var(--bg-soft);border:1px solid var(--border);padding:2px 10px;border-radius:999px}
  footer{border-top:1px solid var(--border);padding:26px 0 54px;color:var(--muted);font-size:.8rem}
  footer a{color:var(--muted)}
  @media(max-width:640px){header.hero{padding:44px 0 26px}h1{font-size:1.6rem}}
"""

THEME_JS = """
<script>
(function(){var k='leeo-theme';try{var t=localStorage.getItem(k);if(t)document.documentElement.setAttribute('data-theme',t);}catch(e){}
document.addEventListener('click',function(e){var b=e.target.closest('#themeBtn');if(!b)return;
var r=document.documentElement,n=r.getAttribute('data-theme')==='light'?'dark':'light';
r.setAttribute('data-theme',n);try{localStorage.setItem(k,n);}catch(e){}});})();
</script>
"""


def esc(s):
    return html.escape(str(s or ""), quote=True)


def load_icons():
    """build-portfolio-site.py 가 남긴 App Store 캐시에서 앱 아이콘 URL을 가져온다."""
    path = os.path.join(ROOT, "scripts/.appstore-cache.json")
    if not os.path.exists(path):
        return {}
    cache = json.load(open(path, encoding="utf-8"))
    return {k: v.get("icon") for k, v in cache.items() if isinstance(v, dict) and v.get("icon")}


def load_apps():
    icons = load_icons()
    out = []
    for f in sorted(glob.glob(os.path.join(APPS, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        d["_slug"] = os.path.basename(f)[:-5]
        d["_icon"] = icons.get(str(d.get("appStoreId") or ""))
        out.append(d)
    return out


def icon_img(app, cls="ic"):
    """앱 아이콘. 캐시에 없으면 이름 첫 글자로 대체한다."""
    if app.get("_icon"):
        return ('<img class="%s" src="%s" alt="" loading="lazy" decoding="async">'
                % (cls, esc(app["_icon"])))
    return '<span class="%s fb">%s</span>' % (cls, esc((app.get("name") or "?")[:1]))


def intro_link(app):
    """쇼케이스 안의 앱 소개 카드로 가는 앵커."""
    return "index.html#app-%s" % esc(app["_slug"])


def live(apps):
    """폐기(stage 0)를 제외한 앱."""
    return [a for a in apps if (a.get("lifecycle") or {}).get("stage") != 0]


def host_of(url):
    return HOSTS.get(urlparse(url).netloc, (urlparse(url).netloc or "기타", "#8b90a0"))


def page(title, desc, body, active, extra_css=""):
    nav = "".join(
        '<a href="%s"%s>%s</a>' % (h, ' class="on"' if k == active else "", t)
        for k, h, t in [("home", "index.html", "쇼케이스"),
                        ("life", "lifecycle.html", "제품 여정"),
                        ("hub", "hub.html", "페이지 모음")]
    )
    return (
        '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>%s</title><meta name="description" content="%s">'
        '<style>%s%s</style></head><body>'
        '<button class="theme-btn" id="themeBtn" aria-label="테마 전환">◐</button>'
        '<header class="hero"><div class="wrap">%s<nav class="bar">%s</nav></div></header>'
        '<main><div class="wrap">%s</div></main>'
        '<footer><div class="wrap">리이오(Leeo) · <a href="%s">쇼케이스</a> · '
        '갱신 %s</div></footer>%s</body></html>'
        % (esc(title), esc(desc), CSS_TOKENS, extra_css, body["head"], nav,
           body["main"], SITE, date.today().isoformat(), THEME_JS)
    )


# ── 공개: 수명주기 ────────────────────────────────────────────────
LIFE_CSS = """
  .st{padding:24px 0;border-top:1px solid var(--border)}
  .st:first-of-type{border-top:0;padding-top:6px}
  .sth{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
  .sth>b{display:inline-grid;place-items:center;width:38px;height:38px;border-radius:11px;flex:none;
    background:linear-gradient(140deg,var(--accent),var(--accent-2));color:#fff;font-size:1.1rem;font-weight:800}
  .sth strong{font-size:1.02rem}
  .sth em{font-style:normal;font-size:.83rem;color:var(--muted)}
  .stc{margin-left:auto;font-size:.72rem;font-weight:700;color:var(--muted);
    background:var(--bg-soft);border:1px solid var(--border);padding:2px 11px;border-radius:999px}
  .stq{color:var(--muted);font-size:.88rem;margin:9px 0 14px;max-width:660px}
  .apps{display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:9px}
  .ac{aspect-ratio:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
    gap:8px;text-align:center;text-decoration:none;color:var(--text);
    background:var(--card);border:1px solid var(--border);border-radius:15px;
    padding:9px 7px;transition:.14s}
  .ac:hover{border-color:var(--accent);color:var(--accent);transform:translateY(-2px)}
  .ac span{font-size:.76rem;font-weight:600;line-height:1.3;word-break:keep-all;
    display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
  .ac em{font-style:normal;font-size:.66rem;font-weight:700;color:var(--muted);margin-top:-4px}
  .ic{width:44px;height:44px;border-radius:11px;flex:none;object-fit:cover;
    background:var(--bg-soft);border:1px solid var(--border)}
  .ic.fb{display:inline-grid;place-items:center;font-size:1.1rem;font-weight:800;color:var(--muted)}
  @media(max-width:560px){.apps{grid-template-columns:repeat(auto-fill,minmax(84px,1fr));gap:7px}
    .ic{width:38px;height:38px}.ac span{font-size:.71rem}}
  .barwrap{display:flex;height:12px;border-radius:999px;overflow:hidden;margin:22px 0 8px;
    border:1px solid var(--border)}
  .barwrap i{display:block}
  .barleg{display:flex;flex-wrap:wrap;gap:14px;font-size:.78rem;color:var(--muted);margin-bottom:8px}
  .barleg b{color:var(--text)}
  .dot{display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:5px;vertical-align:-1px}
"""


def lifecycle_page(apps):
    ls = live(apps)
    buckets = {}
    for a in ls:
        buckets.setdefault((a.get("lifecycle") or {}).get("stage", 1), []).append(a)
    total = len(ls)
    colors = {5: "#34c48a", 4: "#7fd4a8", 3: "#a78bfa", 2: "#5b8def", 1: "#8b90a0"}

    bar, leg = "", ""
    for st, en, _, _ in STAGES:
        n = len(buckets.get(st, []))
        if not n:
            continue
        c = colors.get(st, "#8b90a0")
        bar += '<i style="flex:%d;background:%s"></i>' % (n, c)
        leg += ('<span><span class="dot" style="background:%s"></span>%d %s <b>%d</b></span>'
                % (c, st, esc(en), n))

    def chip(a):
        rc = (a.get("lifecycle") or {}).get("ratingCount") or 0
        note = "<em>리뷰 %d</em>" % rc if rc else ""
        return ('<a class="ac" href="%s">%s<span>%s</span>%s</a>'
                % (intro_link(a), icon_img(a), esc(a["name"]), note))

    # 해당 앱이 없는 단계는 아예 내보내지 않는다 — 빈 칸이 남으면 미완성처럼 보인다
    rows = []
    for st, en, kr, why in STAGES:
        items = sorted(buckets.get(st, []), key=lambda a: a["name"])
        if not items:
            continue
        rows.append(
            '<div class="st"><div class="sth"><b>%d</b><strong>%s</strong><em>%s</em>'
            '<span class="stc">%d개</span></div><p class="stq">%s</p>'
            '<div class="apps">%s</div></div>'
            % (st, esc(en), esc(kr), len(items), esc(why),
               "".join(chip(a) for a in items)))

    head = ('<div class="eyebrow">Product Lifecycle</div><h1>제품 여정</h1>'
            '<p>만든 앱 %d개가 지금 어느 단계에 있는지. 아이디어에서 출시로, 출시에서 '
            '사용자의 반응으로 — 제품이 자리 잡기까지의 단계로 나눠 봤습니다.</p>' % total)
    main = ('<section><div class="barwrap">%s</div><div class="barleg">%s</div>'
            '<p class="lead">아래로 갈수록 이른 단계입니다. 앱을 누르면 소개를 볼 수 있습니다.</p>'
            '%s</section>' % (bar, leg, "".join(rows)))
    return page("제품 여정 — 리이오의 앱 포트폴리오",
                "만든 앱 %d개가 제품 여정의 어느 단계에 있는지 5단계로 정리했습니다." % total,
                {"head": head, "main": main}, "life", LIFE_CSS)


# ── 공개: 허브 ────────────────────────────────────────────────────
HUB_CSS = """
  .ovgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:13px}
  .ov{display:block;background:var(--card);border:1px solid var(--border);border-radius:13px;
    padding:17px 18px;text-decoration:none;color:inherit;transition:.14s}
  .ov:hover{border-color:var(--accent);transform:translateY(-2px)}
  .ov b{font-size:.97rem;display:block;margin-bottom:6px}
  .ov p{color:var(--muted);font-size:.85rem}
  .hostblk{background:var(--card);border:1px solid var(--border);border-radius:13px;
    padding:16px 18px;margin-bottom:12px}
  .hosth{font-size:.9rem;font-weight:700;display:flex;align-items:center;gap:9px;
    margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid var(--border)}
  .hosth::before{content:"";width:9px;height:9px;border-radius:3px;background:var(--c)}
  .hc{margin-left:auto}
  .suplist{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:6px}
  .sup{display:flex;align-items:center;gap:8px;padding:7px 10px;border-radius:8px;
    text-decoration:none;color:inherit;font-size:.86rem}
  .sup:hover{background:var(--bg-soft);color:var(--accent)}
  .sup b{font-weight:600}
  .sup i{margin-left:auto;font-style:normal;font-size:.72rem;color:var(--muted)}
  .ic{width:24px;height:24px;border-radius:6px;flex:none;object-fit:cover;
    background:var(--bg-soft);border:1px solid var(--border)}
  .ic.fb{display:inline-grid;place-items:center;font-size:.75rem;font-weight:800;color:var(--muted)}
  .ic.sm{width:22px;height:22px;border-radius:6px}
"""


def support_blocks(apps, public=True):
    ls = [a for a in live(apps) if a.get("supportUrl")]
    groups = {}
    for a in ls:
        groups.setdefault(host_of(a["supportUrl"]), []).append(a)
    out = ""
    for (name, color), items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        rows = "".join(
            '<a class="sup" href="%s" target="_blank" rel="noopener">%s<b>%s</b><i>%s</i></a>'
            % (esc(a["supportUrl"]), icon_img(a, "ic sm"), esc(a["name"]),
               esc("" if public else (a.get("lifecycle") or {}).get("tier") or ""))
            for a in sorted(items, key=lambda a: a["name"])
        )
        out += ('<div class="hostblk"><div class="hosth" style="--c:%s">%s'
                '<span class="hc">%d</span></div><div class="suplist">%s</div></div>'
                % (color, esc(name), len(items), rows))
    return out, len(ls), len(groups)


def hub_page(apps):
    sup, n_sup, n_host = support_blocks(apps)
    n_live = len(live(apps))
    head = ('<div class="eyebrow">Portfolio Hub</div><h1>페이지 모음</h1>'
            '<p>앱 %d개에 딸린 페이지들이 여러 곳에 흩어져 있어 한자리에 모았습니다. '
            '찾던 앱의 지원 페이지를 여기서 바로 열 수 있습니다.</p>' % n_live)
    main = (
        '<section><h2>포트폴리오 둘러보기</h2>'
        '<p class="lead">전체를 한눈에 보는 두 페이지입니다.</p><div class="ovgrid">'
        '<a class="ov" href="index.html"><b>쇼케이스</b>'
        '<p>출시한 앱 전체를 문제 → 해결 방식의 이야기로 소개합니다. 한국어·영어 전환과 '
        '문제 해결 지도를 함께 제공합니다.</p></a>'
        '<a class="ov" href="lifecycle.html"><b>제품 여정</b>'
        '<p>만든 앱들이 제품 여정의 어느 단계에 있는지 다섯 단계로 정리했습니다.</p></a>'
        '</div></section>'
        '<section><h2>앱별 지원 페이지<span class="hc">%d</span></h2>'
        '<p class="lead">App Store에 등록된 문의·안내 페이지입니다. 만든 시기에 따라 '
        '호스팅한 곳이 %d군데로 나뉘어 있어, 서비스별로 묶어 두었습니다.</p>%s</section>'
        % (n_sup, n_host, sup))
    return page("페이지 모음 — 리이오의 앱 포트폴리오",
                "앱 %d개의 지원 페이지와 포트폴리오 페이지를 한자리에 모았습니다." % n_live,
                {"head": head, "main": main}, "hub", HUB_CSS)


# ── 내부: 전체 허브 ───────────────────────────────────────────────
def internal_hub(apps, links):
    sup, n_sup, n_host = support_blocks(apps, public=False)
    by_slug = {a["_slug"]: a for a in apps}
    arts = ""
    n_art = 0
    for g in links.get("artifacts", []):
        app = by_slug.get(g.get("app") or "")
        title = ("%s 관련" % app["name"]) if app else "그 외 · 앱 미지정"
        n_art += len(g["items"])
        rows = "".join(
            '<a class="sup" href="%s" target="_blank" rel="noopener"><b>%s</b><i>%s</i></a>'
            % (esc(i["u"]), esc(i["t"]), esc(i.get("d", "")))
            for i in g["items"])
        arts += ('<div class="hostblk"><div class="hosth" style="--c:#a78bfa">%s'
                 '<span class="hc">%d</span></div><div class="suplist">%s</div></div>'
                 % (esc(title), len(g["items"]), rows))

    def chips(pattern, base):
        items = sorted(os.path.basename(f) for f in glob.glob(os.path.join(ROOT, pattern)))
        return len(items), "".join(
            '<a class="sup" href="file://%s"><b>%s</b></a>'
            % (esc(os.path.join(ROOT, base, i)), esc(i)) for i in items)

    n_kit, kit = chips("marketing/apps/*.md", "marketing/apps")
    n_doc, doc = chips("docs/*.md", "docs")

    head = ('<div class="eyebrow">Portfolio Hub · 내부용 (비배포)</div><h1>포트폴리오 허브</h1>'
            '<p>흩어진 페이지를 한 곳에서 찾는 색인. 공개 허브(<code>docs/hub.html</code>)에는 '
            '아티팩트와 로컬 링크를 뺀 안전 버전이 올라갑니다.</p>')
    main = (
        '<section><h2>공개 페이지</h2><p class="lead">GitHub Pages로 배포되는 페이지.</p>'
        '<div class="ovgrid">'
        '<a class="ov" href="%(site)sindex.html"><b>쇼케이스</b><p>출시작 전체 케이스 스터디. '
        '재생성: <code>build-portfolio-site.py</code></p></a>'
        '<a class="ov" href="%(site)slifecycle.html"><b>제품 여정</b><p>수명주기 5단계 공개판. '
        '재생성: <code>build-portfolio-hub.py</code></p></a>'
        '<a class="ov" href="%(site)shub.html"><b>페이지 모음</b><p>공개 허브(안전 버전). '
        '재생성: <code>build-portfolio-hub.py</code></p></a>'
        '</div></section>'
        '<section><h2>앱별 지원 페이지<span class="hc">%(ns)d</span></h2>'
        '<p class="lead">호스트 %(nh)d곳에 분산 — 일괄 수정이 어려우니 이 목록이 지도 역할.</p>%(sup)s</section>'
        '<section><h2>디자인 · QA 아티팩트<span class="hc">%(na)d</span></h2>'
        '<p class="lead">⚠️ 비공개 링크. 공개 페이지에 절대 넣지 말 것.</p>%(art)s</section>'
        '<section><h2>제작물 · 문서</h2><p class="lead">클릭하면 로컬 파일이 열립니다.</p>'
        '<div class="hostblk"><div class="hosth" style="--c:#d6a01e">마케팅 킷'
        '<span class="hc">%(nk)d</span></div><div class="suplist">%(kit)s</div></div>'
        '<div class="hostblk"><div class="hosth" style="--c:#8b90a0">운영 가이드'
        '<span class="hc">%(nd)d</span></div><div class="suplist">%(doc)s</div></div></section>'
        % {"site": SITE, "ns": n_sup, "nh": n_host, "sup": sup, "na": n_art, "art": arts,
           "nk": n_kit, "kit": kit, "nd": n_doc, "doc": doc})
    return page("앱 포트폴리오 허브 (내부)", "내부 색인", {"head": head, "main": main},
                "", HUB_CSS)


def main():
    links = json.load(open(os.path.join(ROOT, "scripts/hub-links.json"), encoding="utf-8"))
    apps = load_apps()
    os.makedirs(REPORTS, exist_ok=True)
    outs = [
        (os.path.join(DOCS, "lifecycle.html"), lifecycle_page(apps), "공개"),
        (os.path.join(DOCS, "hub.html"), hub_page(apps), "공개"),
        (os.path.join(REPORTS, "portfolio-hub.html"), internal_hub(apps, links), "내부"),
    ]
    for path, content, kind in outs:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print("  [%s] %s" % (kind, os.path.relpath(path, ROOT)))
    ls = live(apps)
    print("앱 %d개(폐기 제외) · 지원페이지 %d · 아티팩트 %d(내부 전용)"
          % (len(ls), sum(1 for a in ls if a.get("supportUrl")),
             sum(len(g["items"]) for g in links.get("artifacts", []))))


if __name__ == "__main__":
    main()
