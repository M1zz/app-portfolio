#!/usr/bin/env python3
"""포트폴리오 허브·수명주기 페이지 생성.

사용법:
  python3 scripts/build-portfolio-hub.py

출력 3종:
  docs/hub.html               공개 허브 — 쇼케이스·수명주기·앱별 지원페이지 (GitHub Pages 배포)
  docs/apps.html              옛 주소 — 서비스 숙성도 할 일 탭으로 넘긴다
  docs/lifecycle.html         공개 수명주기 — 제품 여정 5단계 (GitHub Pages 배포)
  docs/maturity.html          공개 서비스 숙성도 — 피처 체크리스트 한눈에 · 할 일 · 국가별 언어 · 분류별 · 기기 탭
  docs/business.html          공개 비즈니스 모델 — 결제 시점 × 방식 · 페이월 · 앱별 Lean Canvas
  docs/paywalls.html          공개 페이월 모음 — 앱별 가격 사다리 비교표 · 페이월 카드
  reports/portfolio-hub.html  내부 허브 — 위 + 아티팩트·로컬 파일 링크 (비배포)
  docs/reddit-launch.html     공개 레딧 출격 — 영어권 유입을 받아도 되는 앱 판정 (상단 메뉴·페이지 모음에 연결)

⚠️ docs/ 는 통째로 공개된다. 공개 페이지에는 다음을 넣지 않는다:
  · 아티팩트 URL (기본 비공개지만 링크를 알면 열리므로 사실상 전체 공개가 된다)
  · 수명주기 하위 등급 A/B/C(개선 중·소강·정지) — 내부 트리아지 표현
  · 폐기(stage 0) 앱
  · file:// 로컬 경로

데이터 출처:
  scripts/hub-links.json          수동 관리 링크(개요·아티팩트)
  Data/apps/*.json                supportUrl · lifecycle · globalReach · serviceMaturity · price (자동 수집)
  scripts/paywalls.json           앱별 페이월(문구·혜택·무료 몫·시점) — 소스를 읽어 정리
"""
import glob
import html
import json
import os
import re
from datetime import date, timedelta
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
STAGE_SHORT = {5: "자리 잡음", 4: "넓히는 중", 3: "PMF 탐색", 2: "PS Fit", 1: "Pre-MVP"}
TIER_KR = {"A": "개선 중", "B": "소강", "C": "정지"}

# 글로벌 지원 축 — sync-global-reach.py 가 앱 JSON globalReach 에 기록한다.
GLOBAL = [
    (3, "다국어", "앱이 3개 이상 언어를 지원합니다.", "#34c48a"),
    (2, "한·영", "앱 안에서 한국어와 영어를 모두 지원합니다.", "#5b8def"),
    (1, "영문 스토어", "앱은 한 언어지만, 스토어 소개는 영어로 준비했습니다.", "#e0a53a"),
    (0, "한국어만", "앱과 스토어 소개 모두 한국어로만 준비했습니다.", "#8b90a0"),
]
# 두 축 지도 열 이름 밑에 붙이는 짧은 뜻 — 칸이 서로 겹치지 않는다는 걸 드러낸다
GLOBAL_SUB = {3: "3개 이상 언어", 2: "한국어+영어", 1: "앱 1개 언어 · 영어 소개", 0: "한국어로만"}

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


def page(title, desc, body, active, extra_css="", extra_js=""):
    nav = "".join(
        '<a href="%s"%s>%s</a>' % (h, ' class="on"' if k == active else "", t)
        for k, h, t in [("home", "index.html", "쇼케이스"),
                        ("life", "lifecycle.html", "제품 여정"),
                        ("maturity", "maturity.html", "서비스 숙성도"),
                        ("biz", "business.html", "비즈니스 모델"),
                        ("pw", "paywalls.html", "페이월"),
                        ("cat", "category.html", "범주 · 언어"),
                        ("reddit", "reddit-launch.html", "레딧 출격"),
                        ("shop", "shop.html", "생활도구점"),
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
        '갱신 %s</div></footer>%s%s</body></html>'
        % (esc(title), esc(desc), CSS_TOKENS, extra_css, body["head"], nav,
           body["main"], SITE, date.today().isoformat(), THEME_JS, extra_js)
    )


# ── 공개: 수명주기 ────────────────────────────────────────────────
# 앱 이름 칩 — 왼쪽 색 띠는 글로벌 지원 수준. 제품 여정·서비스 숙성도가 같이 쓴다.
NAMES_CSS = """
  .lnames{display:flex;flex-wrap:wrap;gap:5px;text-align:left}
  .lnames a{display:inline-flex;align-items:center;gap:5px;padding:3px 9px 3px 3px;border-radius:999px;
    background:var(--bg-soft);border:1px solid var(--border);border-left:3px solid var(--c);
    color:var(--text);text-decoration:none;font-size:.74rem;font-weight:600;white-space:nowrap}
  .lnames a:hover{border-color:var(--accent);color:var(--accent)}
  .lnames .ic{width:20px;height:20px;border-radius:5px}
  .lnames .ic.fb{font-size:.6rem}
  .lnames .none{font-size:.76rem;color:var(--muted)}
  @media(max-width:560px){.lnames a{white-space:normal}}
"""

LIFE_CSS = NAMES_CSS + """
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
  .ac{position:relative}
  .gb{position:absolute;top:6px;right:6px;font-style:normal;font-size:.6rem;font-weight:800;
    line-height:1;padding:3px 6px;border-radius:999px;color:#fff;background:var(--c)}
  .axes{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:8px}
  .axis{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px 18px}
  .axis h3{font-size:.95rem;margin-bottom:2px}
  .axis p{color:var(--muted);font-size:.8rem}
  .axis .barwrap{margin:12px 0 8px}
  @media(max-width:700px){.axes{grid-template-columns:1fr}}
  .mx{width:100%;border-collapse:separate;border-spacing:5px;table-layout:fixed}
  .mxw{overflow-x:auto;margin:0 -5px}
  .mx th{font-size:.74rem;font-weight:700;color:var(--muted);text-align:left;padding:2px 6px}
  .mx thead th{border-bottom:3px solid var(--c);padding-bottom:6px}
  .mx thead th:first-child{border:0;width:116px}
  .mx thead th em{display:block;font-style:normal;font-weight:600;font-size:.66rem;opacity:.8}
  .mx td.z::after{content:"없음";font-size:.68rem;color:var(--muted);opacity:.6}
  .mx tbody th{vertical-align:top;padding-top:10px;color:var(--text)}
  .mx tbody th b{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:7px;
    margin-right:6px;font-size:.75rem;color:#fff;background:linear-gradient(140deg,var(--accent),var(--accent-2))}
  .mx td{background:var(--card);border:1px solid var(--border);border-radius:11px;padding:8px;
    vertical-align:top;min-width:96px}
  .mx td.z{background:transparent;border-style:dashed}
  .mx td a{display:inline-block;margin:2px;border-radius:9px;transition:.12s}
  .mx td a:hover{transform:translateY(-2px)}
  .mx .ic{width:34px;height:34px;border-radius:9px}
  .mx .ic.fb{font-size:.85rem}
  .mx td .n{display:block;font-size:.7rem;font-weight:700;color:var(--muted);margin-bottom:3px}
  .mx td::before{display:none;content:attr(data-l);font-size:.7rem;font-weight:700;
    color:var(--muted);border-left:3px solid var(--c);padding-left:6px;margin-bottom:4px}
  @media(max-width:560px){
    .mx,.mx tbody{display:block}.mx thead{display:none}
    .mx tr{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:14px}
    .mx tbody th{grid-column:1/-1;padding:0}
    .mx td{min-width:0}.mx td::before{display:block}
    .mx td.z{display:none}
    .mx .ic{width:30px;height:30px;border-radius:8px}}
  .mx td a.nx{position:relative;box-shadow:0 0 0 2px var(--warn)}
  .mx td a.nx::after{content:"↗";position:absolute;top:-6px;right:-6px;width:15px;height:15px;
    border-radius:50%;background:var(--warn);color:#fff;font-size:.6rem;font-weight:800;
    display:grid;place-items:center;line-height:1}
  .nxk{font-style:normal;display:inline-grid;place-items:center;width:16px;height:16px;border-radius:50%;
    background:var(--warn);color:#fff;font-size:.62rem;font-weight:800;vertical-align:1px}
  .lg.nxt th,.lg.nxt td{text-align:left;white-space:normal;vertical-align:middle}
  .lg.nxt td.wy{width:100%}
  .lg.nxt td.nw,.lg.nxt td.nx-to,.lg.nxt td.rd{white-space:nowrap}
  .nxt tr.grp th{position:static;background:var(--bg-soft);font-size:.74rem;color:var(--muted);
    font-weight:800;padding:8px 12px}
  .nxt tr.grp b{color:var(--text);margin-left:4px}
  .nxt tbody th{min-width:150px}
  .nxt td.nw{color:var(--muted);white-space:nowrap}
  .nxt td.ar{color:var(--warn);font-weight:800;width:14px;padding:0}
  .nxt td.nx-to{font-weight:800;white-space:nowrap}
  .nxt td.wy{color:var(--muted);font-size:.74rem;min-width:200px}
  .nxt .pg{display:block;height:5px;max-width:220px;border-radius:999px;background:var(--bg-soft);
    overflow:hidden;margin-top:5px}
  .nxt .pg i{display:block;height:100%;background:var(--warn)}
  .nxt td.rd{white-space:nowrap;font-size:.74rem;color:var(--muted);min-width:120px}
  .nxt td.rd b{font-size:.76rem}
  .nxt .grpn{font-weight:800;font-size:.8rem}
  .axt{display:inline-flex;gap:4px;padding:4px;border-radius:999px;background:var(--card);
    border:1px solid var(--border);margin:6px 0 12px}
  .axt button{font:inherit;font-size:.8rem;font-weight:700;cursor:pointer;color:var(--muted);
    background:none;border:0;padding:6px 14px;border-radius:999px}
  .axt button[aria-selected=true]{background:var(--text);color:var(--bg)}
  [data-axp][hidden]{display:none}
  .gts{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}
  .gt{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:13px 15px}
  .gt b{display:block;font-size:.9rem}
  .gt em{font-style:normal;font-size:.74rem;color:var(--accent);font-weight:700}
  .gt p{font-size:.76rem;color:var(--muted);margin:6px 0}
  .gt span{font-size:.76rem;line-height:1.7}
  .tip{position:fixed;z-index:20;max-width:300px;padding:10px 12px;border-radius:11px;
    background:var(--text);color:var(--bg);font-size:.76rem;line-height:1.5;white-space:pre-line;
    box-shadow:0 8px 24px rgba(0,0,0,.28);pointer-events:none}
  .tip b{display:block;font-size:.82rem}
  .todo{display:inline-block;padding:1px 8px;border-radius:999px;margin:1px 2px;font-weight:700;
    border:1px dashed var(--warn);color:var(--text);font-size:.74rem}
  .todo::before{content:"＋ ";color:var(--warn)}
  .sg{display:inline-block;padding:1px 7px;border-radius:999px;margin:1px 2px;font-weight:700;
    background:rgba(52,196,138,.15);color:var(--ok)}
  .sg.off{background:var(--bg-soft);color:var(--muted);text-decoration:line-through}
  @media(max-width:560px){.nxt tbody th{min-width:110px}.nxt td.wy{min-width:160px}}
  .gf{display:flex;flex-wrap:wrap;gap:7px;margin:4px 0 6px}
  .gf button{font:inherit;font-size:.78rem;font-weight:700;cursor:pointer;color:var(--text);
    background:var(--card);border:1px solid var(--border);padding:6px 12px;border-radius:999px}
  .gf button:hover{border-color:var(--accent)}
  .gf button[aria-pressed=true]{background:var(--text);color:var(--bg);border-color:var(--text)}
  [data-gf] .ac{opacity:.16}
  [data-gf="0"] .ac[data-g="0"],[data-gf="1"] .ac[data-g="1"],
  [data-gf="2"] .ac[data-g="2"],[data-gf="3"] .ac[data-g="3"]{opacity:1}
  .lr{display:grid;grid-template-columns:104px 1fr 28px;align-items:center;gap:4px 10px;
    padding:7px 0;border-top:1px solid var(--border)}
  .lr:first-child{border-top:0}
  .ln{font-size:.82rem;font-weight:700}
  .ln em{font-style:normal;font-size:.68rem;color:var(--muted);margin-left:6px}
  .lt{height:8px;border-radius:999px;background:var(--bg-soft);overflow:hidden}
  .lt i{display:block;height:100%;border-radius:999px;
    background:linear-gradient(90deg,var(--accent),var(--accent-2))}
  .lr>b{font-size:.8rem;text-align:right}
  .li{grid-column:2/-1;display:flex;flex-wrap:wrap;gap:4px}
  .li:empty{display:none}
  .li .ic{width:26px;height:26px;border-radius:7px}
  .li .ic.fb{font-size:.7rem}
  .li a{border-radius:7px;transition:.12s}.li a:hover{transform:translateY(-2px)}
  .lbt td,.lbt th{vertical-align:top;white-space:normal}
  .lbt tbody th{min-width:96px}
  .lbt tbody th b{display:block;font-size:.84rem}
  .lbt tbody th em{font-style:normal;font-size:.66rem;color:var(--muted);font-weight:700}
  .lbt td.lc{width:84px;text-align:left}
  .lbt td.lc b{font-size:.95rem}
  .lbt td.lc .lt{display:block;margin-top:6px}
  .lbt td.lc .lt i{display:block;height:100%;border-radius:999px;
    background:linear-gradient(90deg,var(--accent),var(--accent-2))}
  .lbt tbody tr:hover>*{background:transparent}
  @media(max-width:560px){.lg.lbt th:first-child{min-width:62px;padding-left:10px}
    .lbt td.lc{width:40px}}
  .lh{font-size:.95rem;margin:26px 0 3px}
  .lgw{overflow-x:auto;border:1px solid var(--border);border-radius:14px;background:var(--card)}
  .lg{border-collapse:collapse;width:100%;font-size:.76rem}
  .lg th,.lg td{padding:7px 6px;text-align:center;border-bottom:1px solid var(--border);white-space:nowrap}
  .lg tbody tr:last-child>*{border-bottom:0}
  .lg thead th{font-size:.68rem;color:var(--muted);font-weight:800;letter-spacing:.03em}
  .lg th:first-child{text-align:left;position:sticky;left:0;background:var(--card);z-index:1;
    padding-left:12px;min-width:150px}
  .lg tbody th a{display:flex;align-items:center;gap:8px;color:var(--text);text-decoration:none;font-weight:600}
  .lg tbody th a:hover{color:var(--accent)}
  .lg tbody th .ic{width:24px;height:24px;border-radius:6px}
  .lg tbody th .ic.fb{font-size:.65rem}
  .lg td i{display:inline-block;width:11px;height:11px;border-radius:50%;background:var(--c)}
  .lg .ls{color:var(--muted);padding-right:12px}
  .lg tbody tr:hover>*{background:var(--bg-soft)}
  @media(max-width:560px){.lr{grid-template-columns:84px 1fr 24px}.lg th:first-child{min-width:120px}
    .lg tbody th span{max-width:84px;overflow:hidden;text-overflow:ellipsis}}
"""

GF_JS = """
<script>
document.addEventListener('click',function(e){var b=e.target.closest('.axt button');if(!b)return;
var v=b.getAttribute('data-ax'),sec=b.closest('section');
sec.querySelectorAll('.axt button').forEach(function(x){x.setAttribute('aria-selected',x===b?'true':'false')});
sec.querySelectorAll('[data-axp]').forEach(function(p){p.hidden=p.getAttribute('data-axp')!==v});});
</script>
<script>
(function(){var tip=null;
function hide(){if(tip){tip.remove();tip=null;}}
function show(a){hide();tip=document.createElement('div');tip.className='tip';
var t=a.getAttribute('data-tip').split('\\n');var b=document.createElement('b');b.textContent=t.shift();
tip.appendChild(b);tip.appendChild(document.createTextNode(t.join('\\n')));document.body.appendChild(tip);
var r=a.getBoundingClientRect(),w=tip.offsetWidth,h=tip.offsetHeight;
var x=Math.min(Math.max(8,r.left+r.width/2-w/2),innerWidth-w-8),y=r.top-h-10;if(y<8)y=r.bottom+10;
tip.style.left=x+'px';tip.style.top=y+'px';}
document.addEventListener('mouseover',function(e){var a=e.target.closest('[data-tip]');if(a)show(a);});
document.addEventListener('mouseout',function(e){if(e.target.closest('[data-tip]'))hide();});
document.addEventListener('focusin',function(e){var a=e.target.closest('[data-tip]');if(a)show(a);});
document.addEventListener('focusout',hide);window.addEventListener('scroll',hide,{passive:true});})();
</script>
<script>
(function(){var box=document.getElementById('journey');if(!box)return;
document.addEventListener('click',function(e){var b=e.target.closest('.gf button');if(!b)return;
var v=b.getAttribute('data-v');document.querySelectorAll('.gf button').forEach(function(x){
x.setAttribute('aria-pressed',x===b?'true':'false');});
if(v==='all')box.removeAttribute('data-gf');else box.setAttribute('data-gf',v);});})();
</script>
"""


def reach(app):
    """글로벌 지원 단계. 수집 전이면 None."""
    g = app.get("globalReach")
    return g.get("level") if g else None


LANG_KR = {"KO": "한국어", "EN": "영어", "ZH": "중국어", "JA": "일본어", "DE": "독일어",
           "ES": "스페인어", "FR": "프랑스어", "IT": "이탈리아어", "PT": "포르투갈어",
           "RU": "러시아어", "TH": "태국어", "VI": "베트남어", "AR": "아랍어",
           "HI": "힌디어", "ID": "인도네시아어", "NL": "네덜란드어", "TR": "튀르키예어",
           "CS": "체코어", "DA": "덴마크어", "EL": "그리스어", "FI": "핀란드어", "NB": "노르웨이어",
           "PL": "폴란드어", "SV": "스웨덴어"}


def app_langs(app):
    """앱이 실제로 지원하는 언어. EN 단독 번들은 개발 기본 언어일 뿐이라
    스토어 소개가 영어일 때만 영어로, 아니면 한국어 앱으로 본다."""
    g = app.get("globalReach") or {}
    langs = g.get("languages") or []
    if langs == ["EN"]:
        return ["EN"] if g.get("englishPage") else ["KO"]
    return langs


def lang_names(app):
    return ", ".join(LANG_KR.get(l, l) for l in app_langs(app))


def reach_badge(app):
    g = app.get("globalReach")
    if not g:
        return ""
    lv = g["level"]
    text = "%d개 언어" % g["languageCount"] if lv == 3 else {2: "한·영", 1: "EN", 0: "KO"}[lv]
    color = dict((k, c) for k, _, _, c in GLOBAL)[lv]
    return '<i class="gb" style="--c:%s" title="%s">%s</i>' % (
        color, esc("지원 언어: " + lang_names(app)), esc(text))


def lang_section(ls):
    """언어별로 보기 — 언어마다 몇 개 앱이 닿는지, 앱마다 어떤 언어를 지원하는지."""
    reached = [a for a in ls if (reach(a) or 0) >= 1]
    if not reached:
        return ""
    count = {}
    for a in ls:
        if reach(a) is None:
            continue
        for l in app_langs(a):
            count[l] = count.get(l, 0) + 1
    order = sorted(count, key=lambda l: (-count[l], l))
    top = max(count.values())
    gcolor = {lv: c for lv, _, _, c in GLOBAL}

    # 언어 × 앱 이름 표 — 언어마다 그 언어로 쓸 수 있는 앱을 이름으로 모두 적는다
    trs = ""
    for l in order:
        users = sorted((a for a in ls if reach(a) is not None and l in app_langs(a)),
                       key=lambda a: (-(reach(a) or 0), a["name"]))
        chips = "".join(
            '<a href="%s" style="--c:%s">%s<span>%s</span></a>'
            % (intro_link(a), gcolor[reach(a)], icon_img(a), esc(a["name"])) for a in users)
        trs += ('<tr><th><b>%s</b><em>%s</em></th><td class="lc"><b>%d</b>'
                '<span class="lt"><i style="width:%.1f%%"></i></span></td>'
                '<td><div class="lnames">%s</div></td></tr>'
                % (esc(LANG_KR.get(l, l)), esc(l), count[l], 100.0 * count[l] / top, chips))
    bars = ('<div class="lgw"><table class="lg lbt"><thead><tr><th>언어</th><th>앱 수</th>'
            '<th style="text-align:left">그 언어로 쓸 수 있는 앱</th></tr></thead>'
            '<tbody>%s</tbody></table></div>' % trs)

    # 앱 × 언어 표 — 영어권 준비를 마친 앱만
    reached.sort(key=lambda a: (-reach(a), -len(app_langs(a)), a["name"]))
    thead = '<tr><th>앱</th>%s<th class="ls">스토어 소개</th></tr>' % "".join(
        '<th title="%s">%s</th>' % (esc(LANG_KR.get(l, l)), esc(l)) for l in order)
    tbody = ""
    for a in reached:
        al = app_langs(a)
        g = a["globalReach"]
        tbody += ('<tr><th><a href="%s">%s<span>%s</span></a></th>%s'
                  '<td class="ls">%s</td></tr>'
                  % (intro_link(a), icon_img(a), esc(a["name"]),
                     "".join('<td>%s</td>' % (
                         '<i style="--c:%s" title="%s"></i>' % (
                             gcolor[g["level"]], esc(LANG_KR.get(l, l))) if l in al else "")
                         for l in order),
                     "영어" if g.get("englishPage") else "한국어"))
    rest = sum(1 for a in ls if reach(a) == 0)
    return ('<section><h2>언어별로 보기<span class="hc">%d개 언어</span></h2>'
            '<p class="lead">App Store에 공개된 앱 언어 정보 기준입니다. 언어마다 그 언어로 쓸 수 있는 '
            '앱을 모두 적었고, 이름 앞 색은 글로벌 지원 수준입니다.</p>'
            '%s'
            '<h3 class="lh">앱마다 지원하는 언어</h3>'
            '<p class="lead">영어권 준비를 마친 앱 %d개입니다. 점 색은 글로벌 지원 수준이고, '
            '나머지 %d개는 아직 한국어로만 쓸 수 있습니다.</p>'
            '<div class="lgw"><table class="lg"><thead>%s</thead><tbody>%s</tbody></table></div>'
            '</section>' % (len(order), bars, len(reached), rest, thead, tbody))


# ── 다음 단계 후보 ──
# 두 축 지도에서 '다음 칸으로 넘어갈 앱'을 뽑는다. 3단계는 사람이 정하므로 '검토 후보'로만 보인다.
POLISH_RULE = 90      # 1→2: 출시 후 다듬은 기간이 이 일수를 넘으면 2단계 (사용자 확정 기준)
POLISH_NEAR = 45      # 이 일수 이상 다듬었으면 '다가가는 중'으로 본다
FRESH_DAYS = 30       # 2→3 후보는 최근 이 기간 안에 업데이트한 앱만


def polish_days(app):
    lc = app.get("lifecycle") or {}
    if lc.get("polishDays") is not None:
        return lc["polishDays"]
    m = re.search(r"다듬은 기간 (\d+)일", lc.get("basis") or "")
    return int(m.group(1)) if m else None


def maturity_pct(app):
    if not (app.get("serviceMaturity") or {}).get("source"):
        return None
    got, known = total_score(app)
    return round(100 * got / known) if known else None


# 다음 단계 관문 — 단계마다 '다음으로 가려면 갖출 것'. 항목을 바꾸려면 여기만 고친다.
# 각 항목: (키, 이름, 판정 함수(app) → True/False/None). None 은 '확인 불가'라 분모에서 뺀다.
def _m(area, key):
    return lambda a: area_vals(a, area).get(key)


def _any(*fns):
    def f(a):
        vals = [fn(a) for fn in fns]
        if any(v for v in vals):
            return True
        return None if all(v is None for v in vals) else False
    return f


def _lc(fn):
    return lambda a: fn(a.get("lifecycle") or {})


def _reach_at_least(n):
    return lambda a: None if reach(a) is None else reach(a) >= n


# ── 5단계 관문: 매출로 검증한다 (2026-10-18 사용자 기준 — 매출 발생 · 순수익 · 안정적 우상향) ──
# 금액은 공개 레포에 두지 않는다. sync-revenue.py 가 reports/revenue.json(.gitignore)에 쓴 값을 여기서만 읽고,
# 공개 페이지에는 관문 통과 여부만 나간다. 비용은 reports/app-costs.json(.gitignore) — 없으면 0.
# 통과 여부는 앱 JSON revenueGates 에도 남겨, 매출 자료가 없는 컴퓨터에서 만들어도 관문이 '확인 불가'로 떨어지지 않게 한다.
REVENUE_WINDOW = 6   # 최근 이 개월 수(끝난 달)로 본다
_REVENUE = None


def _revenue_data():
    global _REVENUE
    if _REVENUE is None:
        def load(name):
            try:
                with open(os.path.join(ROOT, "reports", name), encoding="utf-8") as fh:
                    return json.load(fh)
            except (OSError, ValueError):
                return {}
        _REVENUE = (load("revenue.json"), load("app-costs.json"))
    return _REVENUE


def net_by_month(app):
    """최근 REVENUE_WINDOW 개월의 순수익(개발자 수익 − 비용) 목록. 매출 자료가 없으면 None."""
    rev, costs = _revenue_data()
    months = (rev.get("months") or [])[-REVENUE_WINDOW:]
    if len(months) < REVENUE_WINDOW:
        return None
    monthly = ((rev.get("apps") or {}).get(str(app.get("appStoreId") or "")) or {}).get("monthly") or {}
    cost = ((costs.get(app["_slug"]) or {}).get("monthlyKRW") or 0)
    return [(monthly.get(m) or 0) - cost for m in months], [monthly.get(m) or 0 for m in months]


def _gate_revenue(a):
    r = net_by_month(a)
    return None if r is None else all(g > 0 for g in r[1])


def _gate_profit(a):
    r = net_by_month(a)
    return None if r is None else sum(r[0]) > 0


def _gate_uptrend(a):
    """안정적 우상향 — 매달 흑자이고, 최소제곱 기울기가 양수이며, 최근 3개월이 그 전 3개월보다 크다."""
    r = net_by_month(a)
    if r is None:
        return None
    net = r[0]
    n = len(net)
    mx, my = (n - 1) / 2, sum(net) / n
    slope = sum((i - mx) * (y - my) for i, y in enumerate(net))
    half = n // 2
    return all(y > 0 for y in net) and slope > 0 and sum(net[half:]) > sum(net[:half])



def _cached(key, fn):
    """매출 자료가 없으면 마지막으로 매출 자료가 있던 컴퓨터가 남긴 통과 여부(revenueGates)를 쓴다."""
    def gate(a):
        v = fn(a)
        return (a.get("revenueGates") or {}).get(key) if v is None and net_by_month(a) is None else v
    return gate


def save_revenue_gates(apps):
    """매출 자료가 있으면 5단계 관문 통과 여부를 앱 JSON revenueGates 에 적는다 — 금액은 적지 않는다."""
    rev, _ = _revenue_data()
    if not rev.get("months"):
        return
    for a in apps:
        if (a.get("lifecycle") or {}).get("stage") != 4:
            continue
        gates = {k: fn(a) for k, _, fn in GATES[5][2]}
        if None in gates.values():
            continue
        gates["through"] = rev["months"][-1]
        if a.get("revenueGates") == gates:
            continue
        path = os.path.join(APPS, a["_slug"] + ".json")
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        d["revenueGates"] = a["revenueGates"] = gates
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=2)
            fh.write("\n")

GATES = {
    2: ("쓸 수 있는 제품", "출시 후 90일 넘게 다듬으면 자동으로 2단계가 됩니다.", [
        ("polish", "출시 후 90일 넘게 다듬기",
         lambda a: None if polish_days(a) is None else polish_days(a) > POLISH_RULE),
        ("supportOpen", "지원 페이지 열림", _m("support", "reachable")),
        ("contact", "앱 안 문의 수단", _any(_m("feedback", "inAppFeedback"), _m("feedback", "mailContact"),
                                       _m("feedback", "instagram"))),
        ("review", "리뷰 부탁", _any(_m("feedback", "reviewPrompt"), _m("feedback", "writeReview"))),
    ]),
    3: ("반응을 듣고 고치는 제품", "3단계는 쓰는 사람의 반응을 보고 직접 정합니다. 모두 갖추면 검토 후보입니다.", [
        ("fresh", "최근 %d일 안에 업데이트" % FRESH_DAYS,
         _lc(lambda lc: None if lc.get("daysSinceUpdate") is None else lc["daysSinceUpdate"] <= FRESH_DAYS)),
        ("rating", "외부 평점 1개 이상", _lc(lambda lc: (lc.get("ratingCount") or 0) >= 1)),
        ("inAppFeedback", "앱 안 피드백", _m("feedback", "inAppFeedback")),
        ("analytics", "사용 통계", _m("ops", "analytics")),
        ("crash", "크래시 진단", _m("ops", "crash")),
        ("bilingual", "한·영 이상", _reach_at_least(2)),
    ]),
    4: ("넓혀도 버티는 제품", "4단계는 사용자를 넓혀 가는 단계입니다. 모두 갖추면 검토 후보입니다.", [
        ("multi", "다국어(3개 언어 이상)", _reach_at_least(3)),
        ("killSwitch", "원격 기능 끄기", _m("ops", "killSwitch")),
        ("tests", "자동 테스트", _m("ops", "tests")),
        ("supportEn", "영어 지원 페이지", _m("support", "english")),
        ("privacy", "개인정보 처리방침 안내", _m("support", "privacy")),
        ("surface", "위젯·단축어", _any(_m("ux", "widgets"), _m("ux", "shortcuts"))),
        ("a11y", "VoiceOver 대응", _m("a11y", "voiceOver")),
        ("ratings10", "외부 평점 10개 이상", _lc(lambda lc: (lc.get("ratingCount") or 0) >= 10)),
    ]),
    5: ("돈이 되는 제품", "5단계는 매출로 검증합니다. 최근 %d개월(끝난 달) App Store 개발자 수익 기준이며, "
        "모두 갖추면 검토 후보입니다." % REVENUE_WINDOW, [
        ("revenue", "최근 %d개월 매달 매출 발생" % REVENUE_WINDOW, _cached("revenue", _gate_revenue)),
        ("profit", "순수익 흑자(수익 − 비용)", _cached("profit", _gate_profit)),
        ("uptrend", "안정적 우상향(매달 흑자 · 추세 상승)", _cached("uptrend", _gate_uptrend)),
    ]),
}
STAGE_NAME = {2: "PS Fit", 3: "PMF 탐색", 4: "넓히는 중", 5: "자리 잡음"}
# 준비도 칸 — 왼쪽에서 오른쪽으로 다음 단계에 가까워진다
READY_COLS = [
    ("low", "갖출 것 많음", "절반 미만", "#8b90a0"),
    ("half", "절반 넘음", "50% 이상", "#e0a53a"),
    ("near", "거의 다 옴", "75% 이상", "#5b8def"),
    ("ready", "준비 완료", "관문 모두 통과", "#34c48a"),
]


def readiness(app):
    """{next, have, known, missing:[이름], unknown:[이름], ratio, col} — 의도적 유지 앱은 None."""
    lc = app.get("lifecycle") or {}
    st = lc.get("stage")
    if lc.get("intent") or st not in (1, 2, 3, 4) or st + 1 not in GATES:
        return None
    nxt = st + 1
    have, missing, unknown = [], [], []
    for key, label, fn in GATES[nxt][2]:
        v = fn(app)
        (unknown if v is None else have if v else missing).append(label)
    known = len(have) + len(missing)
    ratio = len(have) / known if known else 0
    col = ("ready" if known and not missing else "near" if ratio >= .75
           else "half" if ratio >= .5 else "low")
    return {"next": nxt, "have": len(have), "known": known, "missing": missing,
            "unknown": unknown, "ratio": ratio, "col": col}


def polish_hint(app):
    """1→2 의 핵심 할 일 — 다듬은 기간은 업데이트를 내야만 늘어난다."""
    lc = app.get("lifecycle") or {}
    pd, since, rel = polish_days(app), lc.get("daysSinceUpdate"), lc.get("releasedAt")
    if pd is None:
        return None
    if pd + (since or 0) > POLISH_RULE:
        return "업데이트를 한 번 더 내면 90일 기준을 넘깁니다"
    if rel:
        due = date.fromisoformat(rel) + timedelta(days=POLISH_RULE + 1)
        return "%d월 %d일 이후에 업데이트를 내면 90일 기준을 넘깁니다" % (due.month, due.day)
    return None


def readiness_tip(app, r):
    lines = ["다음: %d %s · 관문 %d/%d" % (r["next"], STAGE_NAME[r["next"]], r["have"], r["known"])]
    if r["missing"]:
        todo = list(r["missing"])
        if "출시 후 90일 넘게 다듬기" in todo and polish_hint(app):
            todo[todo.index("출시 후 90일 넘게 다듬기")] = polish_hint(app)
        lines.append("할 일 · " + " / ".join(todo))
    elif r["known"]:  # 모두 확인 불가면 통과가 아니다 — 매출 데이터가 없는 컴퓨터에서 5단계 관문이 이렇게 된다
        lines.append("관문을 모두 통과했습니다" + (" — 단계를 올릴지 검토할 때입니다" if r["next"] >= 3 else ""))
    if r["unknown"]:
        lines.append("확인 불가 · " + ", ".join(r["unknown"]))
    return "\n".join(lines)


def ready_table(ls):
    """다음 단계에 가까운 앱 — 준비 완료 · 거의 다 옴. 업데이트 한 번만 남은 1단계 앱은 한 줄로 묶는다."""
    rows, one_update = [], []
    for a in ls:
        r = readiness(a)
        if not r or r["col"] not in ("near", "ready"):
            continue
        if r["next"] == 2 and r["missing"] == ["출시 후 90일 넘게 다듬기"]:
            one_update.append(a)
        else:
            rows.append((a, r))
    if not rows and not one_update:
        return ""
    order = {c[0]: i for i, c in enumerate(READY_COLS)}
    rows.sort(key=lambda x: (-order[x[1]["col"]], -(x[0].get("lifecycle") or {}).get("stage", 0),
                             -x[1]["ratio"], x[0]["name"]))
    color = {c[0]: c[3] for c in READY_COLS}
    label = {c[0]: c[1] for c in READY_COLS}
    trs = ""
    for a, r in rows:
        st = (a.get("lifecycle") or {}).get("stage")
        todo = list(r["missing"])
        if "출시 후 90일 넘게 다듬기" in todo and polish_hint(a):
            todo[todo.index("출시 후 90일 넘게 다듬기")] = polish_hint(a)
        chips = "".join('<span class="todo">%s</span>' % esc(t) for t in todo) or \
            '<span class="sg">관문 모두 통과%s</span>' % (" · 검토 후보" if r["next"] >= 3 else "")
        trs += ('<tr><th><a href="%s" title="%s">%s<span>%s</span></a></th>'
                '<td class="nw">%d %s</td><td class="ar">→</td><td class="nx-to">%d %s</td>'
                '<td class="rd"><b style="color:%s">%s</b> %d/%d'
                '<span class="pg"><i style="width:%d%%;background:%s"></i></span></td>'
                '<td class="wy">%s</td></tr>'
                % (intro_link(a), esc(a["name"]), icon_img(a), esc(a["name"]),
                   st, esc(STAGE_SHORT[st]), r["next"], esc(STAGE_NAME[r["next"]]),
                   color[r["col"]], esc(label[r["col"]]), r["have"], r["known"],
                   round(r["ratio"] * 100), color[r["col"]], chips))
    if one_update:
        one_update.sort(key=lambda a: a["name"])
        later = [a for a in one_update if "이후에" in (polish_hint(a) or "")]
        tips = {a["_slug"]: polish_hint(a) or "" for a in one_update}
        trs += ('<tr><th colspan="2"><span class="grpn">1 Pre-MVP · %d개</span></th>'
                '<td class="ar">→</td><td class="nx-to">2 PS Fit</td>'
                '<td class="rd"><b style="color:%s">%s</b> 관문 3/4</td>'
                '<td class="wy"><span class="todo">업데이트 한 번</span> 나머지 관문은 모두 통과했고, '
                '출시 90일이 지난 뒤 업데이트를 한 번 내면 2단계로 넘어갑니다.%s'
                '<div class="lnames" style="margin-top:7px">%s</div></td></tr>'
                % (len(one_update), color["near"], esc(label["near"]),
                   (" 다만 %s %d개는 출시 90일이 아직 안 돼, 그 뒤에 내야 합니다(이름에 마우스를 올리면 날짜가 보입니다)."
                    % ("·".join(esc(a["name"]) for a in later), len(later)))
                   if later else "",
                   "".join('<a href="%s" style="--c:%s" data-tip="%s">%s<span>%s</span></a>'
                           % (intro_link(a), color["near"], esc("%s\n%s" % (a["name"], tips[a["_slug"]])),
                              icon_img(a), esc(a["name"]))
                           for a in one_update)))
    gate_doc = "".join(
        '<div class="gt"><b>→ %d %s</b><em>%s</em><p>%s</p><span>%s</span></div>'
        % (n, esc(STAGE_NAME[n]), esc(title), esc(note), " · ".join(esc(l) for _, l, _ in items))
        for n, (title, note, items) in sorted(GATES.items()))
    return ('<h3 class="lh">다음 단계에 가까운 앱 <span class="hc">%d</span></h3>'
            '<p class="lead">관문을 75%% 넘게 통과한 앱입니다. 오른쪽 칸은 아직 갖추지 못한 것, 곧 할 일입니다.</p>'
            '<div class="lgw"><table class="lg nxt"><tbody>%s</tbody></table></div>'
            '<h3 class="lh">단계별 관문</h3><div class="gts">%s</div>'
            % (len(rows) + len(one_update), trs, gate_doc))


def stage_map(buckets, cols, col_of, tip_of, mark_of=lambda a: False):
    """제품 여정(세로) × 임의의 가로축 지도. cols: [(키, 이름, 짧은 뜻, 색)]"""
    thead = "<tr><th></th>%s</tr>" % "".join(
        '<th style="--c:%s">%s<em>%s</em></th>' % (c, esc(name), esc(sub)) for _, name, sub, c in cols)
    tbody = ""
    for st, _, _, _ in STAGES:
        items = buckets.get(st, [])
        if not items:
            continue
        cells = ""
        for key, name, _, c in cols:
            hit = sorted((a for a in items if col_of(a) == key), key=lambda a: a["name"])
            if not hit:
                cells += '<td class="z"></td>'
                continue
            cells += '<td data-l="%s" style="--c:%s"><span class="n">%d</span>%s</td>' % (
                esc(name), c, len(hit), "".join(
                    '<a href="%s"%s aria-label="%s" data-tip="%s">%s</a>' % (
                        intro_link(a), ' class="nx"' if mark_of(a) else "", esc(a["name"]),
                        esc("%s\n%s" % (a["name"], tip_of(a))), icon_img(a))
                    for a in hit))
        tbody += '<tr><th><b>%d</b>%s</th>%s</tr>' % (st, esc(STAGE_SHORT[st]), cells)
    return '<div class="mxw"><table class="mx"><thead>%s</thead><tbody>%s</tbody></table></div>' % (
        thead, tbody)


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
        g = reach(a)
        return ('<a class="ac" href="%s"%s>%s%s<span>%s</span>%s</a>'
                % (intro_link(a), ' data-g="%d"' % g if g is not None else "",
                   reach_badge(a), icon_img(a), esc(a["name"]), note))

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

    # ── 글로벌 지원 축 ──
    gcount = {lv: sum(1 for a in ls if reach(a) == lv) for lv, _, _, _ in GLOBAL}
    gbar, gleg = "", ""
    for lv, name, _, c in GLOBAL:
        if gcount[lv]:
            gbar += '<i style="flex:%d;background:%s"></i>' % (gcount[lv], c)
            gleg += ('<span><span class="dot" style="background:%s"></span>%s <b>%d</b></span>'
                     % (c, esc(name), gcount[lv]))
    n_global = sum(1 for a in ls if (reach(a) or 0) >= 1)
    n_multi = gcount[3] + gcount[2]

    axes = (
        '<div class="axes">'
        '<div class="axis"><h3>제품 여정</h3><p>시장에서 어디까지 왔나</p>'
        '<div class="barwrap">%s</div><div class="barleg">%s</div></div>'
        '<div class="axis"><h3>글로벌 지원</h3><p>어디까지 닿을 수 있나 · 영어권 준비 %d개</p>'
        '<div class="barwrap">%s</div><div class="barleg">%s</div></div>'
        '</div>' % (bar, leg, n_global, gbar, gleg))

    # 두 축 지도 — 가로축을 '다음 단계 준비도'(종합)와 '글로벌 지원'(언어) 중에서 고른다
    mapped = [a for a in ls if reach(a) is not None]   # 스토어에서 내려간 앱은 뺀다
    mb = {}
    for a in mapped:
        mb.setdefault((a.get("lifecycle") or {}).get("stage", 1), []).append(a)

    def ready_col(a):
        r = readiness(a)
        return r["col"] if r else "low"

    def ready_tip(a):
        r = readiness(a)
        return readiness_tip(a, r) if r else "브랜드 소개용으로 지금 모습을 유지하는 앱입니다"

    # 브랜드 소개용으로 지금 모습을 유지하는 앱(intent)은 준비도로 재지 않는다
    rb = {st: [a for a in items if readiness(a)] for st, items in mb.items()}
    ready_map = stage_map(rb, READY_COLS, ready_col, ready_tip,
                         mark_of=lambda a: ready_col(a) in ("near", "ready") and readiness(a) is not None)
    gcols = [(lv, name, GLOBAL_SUB[lv], c) for lv, name, _, c in reversed(GLOBAL) if gcount[lv]]
    lang_map = stage_map(mb, gcols, reach, lambda a: "지원 언어 · " + lang_names(a))
    n_ready = sum(1 for a in mapped if ready_col(a) == "ready" and readiness(a))
    n_near = sum(1 for a in mapped if ready_col(a) == "near" and readiness(a))
    matrix = (
        '<section><h2>두 축으로 보기</h2>'
        '<div class="axt" role="tablist" aria-label="가로축">'
        '<button role="tab" aria-selected="true" data-ax="ready">종합 준비도</button>'
        '<button role="tab" aria-selected="false" data-ax="lang">글로벌 지원</button></div>'
        '<div data-axp="ready"><p class="lead">세로는 제품 여정, 가로는 <b>다음 단계 준비도</b>입니다. '
        '단계마다 다음으로 가려면 갖출 관문(지원 페이지·피드백·안정성·언어 등)을 정해 두고, 앱이 그중 '
        '얼마나 통과했는지로 칸을 나눴습니다. 오른쪽으로 갈수록 다음 단계에 가깝고, 지금 준비를 마친 앱은 '
        '%d개, 거의 다 온 앱은 %d개입니다. <i class="nxk">↗</i> 아이콘에 마우스를 올리면 남은 할 일이 보입니다.</p>'
        '%s%s</div>'
        '<div data-axp="lang" hidden><p class="lead">세로는 제품 여정, 가로는 글로벌 지원입니다. 오른쪽으로 '
        '갈수록 더 많은 언어로 닿습니다. 앱은 지금 닿는 가장 넓은 칸 하나에만 들어갑니다. 다국어 칸의 앱도 '
        '한국어를 지원하므로 한국어만 칸에는 다시 넣지 않습니다.</p>%s'
        '<p class="lead" style="margin-top:12px">%s</p></div></section>'
        % (n_ready, n_near, ready_map, ready_table(ls), lang_map,
           " ".join("<b>%s</b> %s" % (esc(name), esc(why))
                    for lv, name, why, _ in reversed(GLOBAL) if gcount[lv])))

    languages = lang_section(ls)

    filters = ('<div class="gf" role="group" aria-label="글로벌 지원으로 강조">'
               '<button data-v="all" aria-pressed="true">전체</button>%s</div>'
               % "".join('<button data-v="%d" aria-pressed="false">%s %d</button>'
                         % (lv, esc(name), gcount[lv]) for lv, name, _, _ in GLOBAL if gcount[lv]))

    head = ('<div class="eyebrow">Product Lifecycle · Global Reach</div><h1>제품 여정</h1>'
            '<p>만든 앱 %d개가 지금 어느 단계에 있는지, 그리고 한국 밖의 사람에게도 닿을 '
            '준비가 되어 있는지. 두 축으로 나눠 봤습니다. 지금은 %d개가 영어권에 나갈 준비를 '
            '마쳤고, 그중 %d개는 앱 안에서도 여러 언어를 지원합니다.</p>'
            % (total, n_global, n_multi))
    main = ('<section>%s</section>%s%s'
            '<section id="journey"><h2>단계별로 보기</h2>'
            '<p class="lead">아래로 갈수록 이른 단계입니다. 오른쪽 위 표시는 글로벌 지원 수준이고, '
            '앱을 누르면 소개를 볼 수 있습니다.</p>%s%s</section>'
            % (axes, matrix, languages, filters, "".join(rows)))
    return page("제품 여정 — 리이오의 앱 포트폴리오",
                "만든 앱 %d개를 제품 여정 5단계와 글로벌 지원 수준, 두 축으로 정리했습니다." % total,
                {"head": head, "main": main}, "life", LIFE_CSS, GF_JS)


# ── 공개: 서비스 숙성도 ───────────────────────────────────────────
# sync-service-maturity.py 가 앱 JSON serviceMaturity 에 기록한 실측값을 탭별로 보여 준다.
# 값은 True(있음) / False(없음) / None(확인 불가). "안 했다"와 "모른다"를 섞지 않는다.
AREAS = [
    ("support", "지원 페이지",
     "App Store에 등록한 문의·안내 페이지가 열리고, 필요한 내용을 담고 있는지 봅니다.",
     [("registered", "등록"), ("reachable", "열림"), ("privacy", "개인정보 처리방침"),
      ("english", "영어 안내"), ("contact", "문의 수단")]),
    ("feedback", "피드백 수집",
     "쓰는 사람의 목소리가 만든 사람에게 닿는 길이 몇 개나 열려 있는지 봅니다.",
     [("inAppFeedback", "앱 안 피드백"), ("mailContact", "메일 문의"),
      ("instagram", "인스타그램 DM"), ("reviewPrompt", "리뷰 요청"),
      ("writeReview", "리뷰 쓰기 바로가기")]),
    ("ops", "운영·안정성",
     "출시한 뒤에도 문제를 먼저 알아채고, 심사 없이 대응할 수 있는지 봅니다.",
     [("analytics", "사용 통계"), ("crash", "크래시 진단"), ("killSwitch", "원격 기능 끄기"),
      ("tests", "자동 테스트"), ("leeoKit", "공통 서비스 기반")]),
    ("ux", "사용 경험",
     "앱을 열지 않아도, 기기를 바꿔도, 처음 열어도 쓰기 편한지 봅니다.",
     [("widgets", "위젯"), ("shortcuts", "단축어·Siri"), ("cloudSync", "iCloud 동기화"),
      ("tips", "사용 팁"), ("onboarding", "첫 실행 안내")]),
    ("a11y", "접근성",
     "눈이 불편하거나, 손을 쓰기 어렵거나, 큰 글씨가 필요하거나, 움직임에 민감한 사람도 똑같이 쓸 수 있는지 봅니다.",
     [("voiceOver", "VoiceOver 설명"), ("dynamicType", "큰 글씨 따라가기"), ("darkMode", "다크 모드"),
      ("voiceControl", "음성 제어 이름"), ("structure", "읽는 순서·역할"), ("actions", "VoiceOver 동작"),
      ("announcements", "바뀐 내용 알려 주기"), ("largeLayout", "큰 글씨 배치 바꾸기"),
      ("reduceMotion", "애니메이션 줄이기"), ("differentiate", "색 없이 구별"), ("contrast", "대비 높이기"),
      ("reduceTransparency", "투명도 줄이기"), ("a11yAudit", "접근성 자동 점검")]),
    ("devices", "기기",
     "어떤 기기에서 쓸 수 있도록 만들었는지 봅니다. 모든 앱이 모든 기기를 지원할 필요는 "
     "없어서 숙성도 점수에는 넣지 않았습니다.",
     [("iphone", "iPhone"), ("ipad", "iPad"), ("mac", "Mac"), ("watch", "Apple Watch"),
      ("vision", "Vision Pro")]),
]
A11Y_NOTE = ("VoiceOver 설명은 화면 읽기용 설명이 5곳 이상 붙어 있을 때 있음으로 봅니다. 다크 모드는 어두운 화면용 색을 "
             "따로 준비했거나 화면 모드에 따라 그리는 흔적이 있을 때 있음으로 보고, 밝은 모드로 고정한 앱은 없음입니다. "
             "큰 글씨는 시스템 글자 스타일만 써도 어느 정도 따라가지만, 크기를 직접 맞춘 흔적이 있을 때만 셉니다. "
             "나머지는 앱 소스 코드에서 해당 설정을 읽거나 따르는지로 판정했고, 자막·음성 해설은 영상이 있는 앱만 봅니다.")
SCORED = ("support", "feedback", "ops", "ux", "a11y")
ITEM_HELP = {
    "registered": "App Store에 지원 페이지 주소가 등록되어 있습니다.",
    "reachable": "등록한 주소가 실제로 열립니다.",
    "privacy": "페이지에서 개인정보 처리방침을 안내합니다.",
    "english": "영어로도 읽을 수 있습니다.",
    "contact": "메일·SNS 등 연락할 방법을 적어 두었습니다.",
    "inAppFeedback": "앱 안에서 바로 의견을 보낼 수 있습니다.",
    "mailContact": "앱에서 메일로 문의할 수 있습니다.",
    "instagram": "앱에서 인스타그램 DM으로 연결됩니다.",
    "reviewPrompt": "만족한 순간에 별점을 부탁합니다.",
    "writeReview": "설정에서 리뷰 작성 화면으로 바로 갑니다.",
    "analytics": "개인을 식별하지 않는 사용 통계를 모읍니다.",
    "crash": "앱이 멈추거나 꺼진 기록을 받아 봅니다.",
    "killSwitch": "문제가 생긴 기능을 업데이트 없이 끌 수 있습니다.",
    "tests": "코드가 바뀔 때 돌려 보는 자동 테스트가 있습니다.",
    "leeoKit": "피드백·리뷰·정책 링크를 공통 기반(LeeoKit)으로 갖췄습니다.",
    "widgets": "홈 화면이나 잠금 화면 위젯을 제공합니다.",
    "shortcuts": "단축어 앱과 Siri에서 기능을 부를 수 있습니다.",
    "cloudSync": "iCloud로 기기 사이에 데이터를 맞춥니다.",
    "tips": "처음 보는 기능을 알맞은 때에 알려 줍니다.",
    "onboarding": "처음 열었을 때 쓰는 법을 안내합니다.",
    "moments": "앱을 잘 쓴 순간을 세어 두었다가 알맞은 때에만 별점·후원을 부탁합니다.",
    "sheets": "아래에서 올라오는 화면에 알맞은 높이와 손잡이를 정해 두었습니다.",
    "liveNumbers": "숫자가 바뀔 때 자리마다 굴러가듯 바뀝니다.",
    "localeFormat": "날짜·숫자·돈을 쓰는 사람의 지역 방식대로 적습니다.",
    "textOverflow": "글자가 길어도 잘리는 자리를 정해 두어 중요한 부분이 남습니다.",
    "inputFlow": "키보드의 확인 키 이름과 키보드 내리기를 상황에 맞춰 두었습니다.",
    "textCopy": "앱이 보여 준 결과 글을 길게 눌러 복사할 수 있습니다.",
    "purchaseTest": "실제 결제 없이 구매·복원·환불 흐름을 미리 돌려 볼 설정이 있습니다.",
    "releaseTags": "버전을 낼 때마다 코드에 표시를 남깁니다.",
    "steadyUpdates": "최근 90일 동안 꾸준히 고치고 다듬었습니다.",
    "voiceOver": "화면 읽기(VoiceOver)용 설명을 붙였습니다.",
    "dynamicType": "설정에서 글자를 키우면 앱 글자와 크기도 함께 커집니다.",
    "darkMode": "어두운 화면에서 쓸 색을 따로 준비했습니다.",
    "voiceControl": "음성 제어로 부를 이름을 버튼에 붙였습니다.",
    "structure": "VoiceOver가 읽는 순서와 묶음, 버튼·제목 같은 역할을 정해 두었습니다.",
    "actions": "밀기·길게 누르기 같은 동작을 VoiceOver에서도 고를 수 있습니다.",
    "announcements": "화면 내용이 바뀌면 VoiceOver가 소리 내어 알려 줍니다.",
    "largeLayout": "글자가 아주 커지면 가로 배치를 세로로 바꾸는 식으로 화면을 다시 짭니다.",
    "reduceMotion": "‘동작 줄이기’를 켜면 화면 움직임을 줄입니다.",
    "differentiate": "‘색상 없이 구별’을 켜면 색 대신 모양·글자로도 상태를 알려 줍니다.",
    "contrast": "‘대비 증가’를 켜면 더 진한 색으로 바꿉니다.",
    "reduceTransparency": "‘투명도 줄이기’를 켜면 비치는 배경을 불투명하게 바꿉니다.",
    "a11yAudit": "자동 테스트가 화면의 접근성 문제를 찾아냅니다.",
    "captions": "영상에 자막과 화면 해설을 켤 수 있습니다.",
    "boldText": "‘굵은 텍스트’를 켜면 직접 그린 글자도 굵게 바꿉니다.",
    "invertColors": "‘스마트 반전’을 켜도 사진과 그림은 원래 색으로 둡니다.",
    "keyboard": "키보드나 스위치로 화면을 옮겨 다니며 쓸 수 있습니다.",
    "iphone": "iPhone에서 쓰도록 만들었습니다.",
    "ipad": "iPad 화면에 맞춰 쓸 수 있습니다.",
    "mac": "Mac용으로 직접 만들었습니다.",
    "watch": "Apple Watch에서 쓸 수 있습니다.",
    "vision": "Apple Vision Pro에서 쓸 수 있습니다.",
}
# 열 제목을 누르면 뜨는 설명 — ITEM_HELP(무엇인가) 아래에 '왜 필요한가'를 한두 문장으로 덧붙인다
ITEM_WHY = {
    "registered": "App Store 제품 페이지의 ‘지원’ 링크가 이 주소로 갑니다. 없으면 쓰는 사람이 물어볼 곳을 찾지 못합니다.",
    "reachable": "주소를 등록해 두어도 페이지가 사라지면, 링크를 누른 사람은 빈 화면을 보게 됩니다.",
    "privacy": "어떤 정보를 모으고 어디에 쓰는지 밝히는 글입니다. App Store 심사에서도 꼭 필요합니다.",
    "english": "한국어를 모르는 사람도 쓰는 법과 문의 방법을 읽을 수 있어야 해외에서도 안심하고 씁니다.",
    "contact": "문제가 생겼을 때 만든 사람에게 직접 닿을 방법입니다.",
    "inAppFeedback": "앱을 나가지 않고 설정에서 바로 의견이나 버그를 보냅니다. 기기 정보가 함께 붙어 원인을 찾기 쉽습니다.",
    "mailContact": "받는 사람과 제목이 채워진 메일이 열려, 긴 이야기나 사진을 보내기 좋습니다.",
    "instagram": "메일보다 가볍게 말을 걸 수 있는 창구입니다.",
    "reviewPrompt": "앱을 즐겁게 쓴 순간에만 별점을 부탁합니다. 아쉬워하는 사람에게는 별점 대신 의견 보내기를 권합니다.",
    "writeReview": "설정의 ‘리뷰 남기기’를 누르면 App Store 리뷰 작성 화면이 바로 열립니다.",
    "analytics": "하루에 몇 명이 앱을 여는지처럼 누구인지 알 수 없는 숫자만 모읍니다. 어떤 기능을 다듬을지 정하는 근거가 됩니다.",
    "crash": "앱이 갑자기 꺼지거나 멈춘 기록을 받아, 쓰는 사람이 알려 주기 전에 먼저 고칠 수 있습니다.",
    "killSwitch": "새 버전의 어떤 기능에 문제가 생기면, 앱 업데이트와 심사를 기다리지 않고 서버의 스위치로 그 기능만 잠시 끕니다. "
                  "나머지 기능은 그대로 쓸 수 있고, 스위치를 읽지 못하면 켜진 채로 둡니다.",
    "tests": "코드를 고칠 때마다 핵심 계산이 여전히 맞는지 자동으로 확인해, 고치다 다른 곳을 망가뜨리는 일을 줄입니다.",
    "leeoKit": "피드백·리뷰·통계·원격 끄기 같은 기능을 여러 앱이 똑같이 쓰도록 묶은 자체 패키지입니다. "
               "한 곳을 고치면 모든 앱이 함께 좋아집니다.",
    "widgets": "앱을 열지 않고 홈 화면이나 잠금 화면에서 바로 내용을 봅니다.",
    "shortcuts": "단축어 앱이나 Siri에게 말해서 앱의 핵심 동작을 바로 부릅니다.",
    "cloudSync": "iPhone·iPad·Mac에서 같은 기록을 이어 쓰고, 기기를 바꿔도 데이터가 남습니다.",
    "tips": "처음 보는 기능을 쓸 만한 때에 짧게 알려 주고, 한 번 써 보면 다시 띄우지 않습니다.",
    "onboarding": "처음 연 사람에게 무엇을 하는 앱이고 어떻게 시작하는지 몇 장으로 보여 줍니다.",
    "moments": "처음 연 날이나 막 실수한 때에 부탁하면 귀찮은 앱이 됩니다. 기록을 끝냈거나 여러 번 잘 쓴 뒤처럼 기분 좋은 순간을 골라 부탁합니다.",
    "sheets": "짧은 내용이 화면 가득 올라오면 흐름이 끊깁니다. 필요한 만큼만 올리고 손잡이를 보여 주면 끌어 내려 닫을 수 있다는 걸 바로 압니다.",
    "liveNumbers": "합계나 남은 시간이 툭 바뀌면 무엇이 달라졌는지 놓치기 쉽습니다. 바뀌는 자리만 움직여 눈이 따라가게 합니다.",
    "localeFormat": "같은 날짜도 나라마다 쓰는 순서가 다릅니다. 기기 지역 설정을 따라 적으면 번역을 늘려도 어색한 표기가 남지 않습니다.",
    "textOverflow": "긴 이름이나 다른 언어로 바뀐 문구가 화면을 넘칠 때, 어디를 줄일지 정하지 않으면 뒤쪽의 중요한 말이 사라집니다.",
    "inputFlow": "‘완료’·‘다음’·‘검색’처럼 누르면 무엇이 되는지 키에 적혀 있고, 화면을 밀면 키보드가 내려가 입력이 막히지 않습니다.",
    "textCopy": "만든 결과를 메시지나 메모로 옮기고 싶을 때, 복사가 막혀 있으면 다시 손으로 써야 합니다.",
    "purchaseTest": "돈이 오가는 화면은 한 번 틀리면 바로 별점으로 돌아옵니다. 출시 전에 살 때와 되살릴 때를 직접 시험합니다. 파는 상품이 없는 앱은 해당 없음입니다.",
    "releaseTags": "어느 버전에 무엇이 들어갔는지 바로 찾아, 문제가 생긴 버전을 되짚거나 되돌리기 쉽습니다.",
    "steadyUpdates": "출시하고 멈춘 앱은 새 기기와 새 iOS에서 조금씩 어긋납니다. 계속 손보는 앱이 쓰는 사람의 의견도 빨리 반영합니다.",
    "voiceOver": "화면을 보기 어려운 사람도 VoiceOver로 버튼과 내용을 들을 수 있습니다. 그림만 있는 버튼에 이름이 없으면 ‘버튼’이라고만 읽혀 무엇인지 알 수 없습니다.",
    "dynamicType": "작은 글씨가 잘 안 보이는 사람은 시스템 설정에서 글자를 키웁니다. 앱이 이를 따르지 않으면 그 사람에게만 화면이 작게 남습니다.",
    "darkMode": "빛에 민감하거나 밤에 쓰는 사람은 어두운 화면을 켭니다. 밝은 모드로 고정하거나 어두운 색을 준비하지 않으면 눈부시거나 글자가 묻힙니다.",
    "voiceControl": "손을 쓰기 어려운 사람은 ‘저장 탭’처럼 말로 화면을 조작합니다. 화면에 보이는 말과 부르는 이름이 다르거나 그림만 있는 버튼이면 부를 방법이 없어, 부를 이름을 따로 붙여 둡니다.",
    "structure": "카드 하나를 한 번에 읽거나 제목에서 제목으로 건너뛸 수 있게 합니다. 꾸밈 그림은 읽지 않게 숨깁니다. 설명이 있어도 순서가 뒤섞이면 화면을 머릿속에 그리기 어렵습니다.",
    "actions": "VoiceOver를 켜면 밀어서 지우기나 끌어 놓기 같은 몸짓을 쓰기 어렵습니다. 같은 일을 동작 목록에서 고르거나 위아래로 값을 바꿀 수 있게 합니다.",
    "announcements": "저장이 끝났거나 타이머가 끝난 것처럼 눈으로만 보이는 변화를, 화면을 보지 않는 사람도 놓치지 않게 합니다.",
    "largeLayout": "가장 큰 글자 크기에서는 한 줄에 들어가던 것이 잘리거나 겹칩니다. 배치를 바꾸거나, 아이콘을 길게 누르면 크게 보여 줘서 잘림 없이 읽게 합니다.",
    "reduceMotion": "확대·회전·튀는 효과는 어지럼을 일으킬 수 있습니다. ‘동작 줄이기’를 켠 사람에게는 움직임을 빼거나 부드럽게 바꿔 보여 줍니다.",
    "differentiate": "빨강·초록처럼 색만으로 맞고 틀림을 나누면 색을 구별하기 어려운 사람은 놓칩니다. 아이콘이나 글자를 함께 보여 줍니다.",
    "contrast": "흐린 회색 글자나 옅은 테두리는 시력이 약한 사람에게 보이지 않습니다. 대비를 높인 색을 따로 준비해 둡니다.",
    "reduceTransparency": "뒤가 비치는 흐린 배경 위의 글자는 읽기 어렵습니다. 이 설정을 켠 사람에게는 단색 배경으로 보여 줍니다.",
    "a11yAudit": "설명 빠진 버튼, 잘리는 글자, 너무 낮은 대비를 사람이 매번 다 볼 수는 없습니다. 테스트가 돌 때마다 자동으로 찾아 새 문제가 섞여 들어가지 않게 합니다.",
    "captions": "소리를 듣기 어려운 사람은 자막으로, 화면을 보기 어려운 사람은 음성 해설로 영상을 따라갑니다. 영상이 없는 앱은 해당 없음으로 둡니다.",
    "boldText": "시스템 글자는 저절로 굵어지지만, 앱이 직접 그린 글자나 숫자는 따로 맞춰야 같이 굵어집니다.",
    "invertColors": "화면 색을 뒤집어 쓰는 사람에게 사진까지 뒤집혀 보이면 알아볼 수 없습니다. 사진·그림은 반전에서 빼 둡니다.",
    "keyboard": "화면을 직접 누르기 어려운 사람은 키보드나 스위치 장치로 앱을 씁니다. 단축키와 옮겨 다닐 순서를 정해 두면 손가락 없이도 쓸 수 있습니다.",
}


def help_attrs(item, label, have, known, tier=None):
    """열 제목에 붙이는 설명 속성 — 누르면 MAT_JS 가 이것으로 설명 창을 띄운다."""
    summary = "앱 %d개 중 %d개가 갖췄습니다." % (known, have) if known else ""
    if tier:
        summary = ("%s 항목 · %s" % (TIER_NAME[tier], summary)).strip(" ·")
    return (' tabindex="0" role="button" aria-haspopup="dialog" data-k="%s" data-n="%s" data-h="%s" '
            'data-w="%s" data-s="%s"' % (
                esc(item), esc(label), esc(ITEM_HELP.get(item) or CHECK_HELP.get(item, "")),
                esc(ITEM_WHY.get(item, "") if ITEM_HELP.get(item) else ""), esc(summary)))

# 주요 18개국 스토어 — sync-global-reach.py 의 STOREFRONTS 와 같은 순서
# 인도는 영어만 둔다(2026-10-27). 힌디어를 지원하는 앱이 하나도 없어 한눈에 표에 늘 빈 열, 국가별 탭에 0개 줄만
# 남았다. 인도 스토어는 영어로 쓰는 사람이 대부분이다. 힌디어 앱이 생기면 언어 열 뒤쪽(`rest`)에 저절로 선다.
COUNTRIES = [
    ("kr", "🇰🇷", "한국", ["KO"]), ("us", "🇺🇸", "미국", ["EN"]), ("jp", "🇯🇵", "일본", ["JA"]),
    ("gb", "🇬🇧", "영국", ["EN"]), ("de", "🇩🇪", "독일", ["DE"]), ("fr", "🇫🇷", "프랑스", ["FR"]),
    ("cn", "🇨🇳", "중국", ["ZH"]), ("tw", "🇹🇼", "대만", ["ZH"]), ("es", "🇪🇸", "스페인", ["ES"]),
    ("br", "🇧🇷", "브라질", ["PT"]), ("in", "🇮🇳", "인도", ["EN"]),
    ("ca", "🇨🇦", "캐나다", ["EN", "FR"]), ("au", "🇦🇺", "호주", ["EN"]),
    ("it", "🇮🇹", "이탈리아", ["IT"]), ("vn", "🇻🇳", "베트남", ["VI"]),
    ("th", "🇹🇭", "태국", ["TH"]), ("id", "🇮🇩", "인도네시아", ["ID"]),
    ("mx", "🇲🇽", "멕시코", ["ES"]),
]

# 한눈에 표의 언어 열 — 주요 18개국에서 쓰는 말만, COUNTRIES 순서대로 한 번씩
MAIN_LANGS = list(dict.fromkeys(l for _, _, _, langs in COUNTRIES for l in langs))
for _l in MAIN_LANGS:
    ITEM_HELP["lang" + _l] = "%s로 쓸 수 있습니다." % LANG_KR.get(_l, _l)
    ITEM_WHY["lang" + _l] = "이 말을 쓰는 주요 나라: %s." % ", ".join(
        nm for _, _, nm, langs in COUNTRIES if _l in langs)
ITEM_HELP["langCount"] = ("앱이 지원하는 언어 수입니다. 주요 18개국 밖의 언어까지 모두 셉니다. "
                          "제목 아래 숫자는 두 가지 이상 언어로 쓸 수 있는 앱 수입니다.")
ITEM_WHY["langCount"] = "숫자에 마우스를 올리면 지원하는 언어 이름을 모두 볼 수 있습니다."


def lang_columns(apps):
    """한눈에 표의 언어 열 — 주요 18개국의 말을 먼저, 그다음 앱들이 지원하는 나머지 언어를 많이 쓰는 순으로 전부."""
    counts = {}
    for a in apps:
        for l in app_langs(a):
            counts[l] = counts.get(l, 0) + 1
    rest = sorted((l for l in counts if l not in MAIN_LANGS), key=lambda l: (-counts[l], l))
    for l in rest:
        ITEM_HELP["lang" + l] = "%s로 쓸 수 있습니다." % LANG_KR.get(l, l)
        ITEM_WHY["lang" + l] = "주요 18개국 스토어의 말은 아니지만, 이 말을 쓰는 사람도 앱을 제 말로 씁니다."
    return MAIN_LANGS + rest

MAT_CSS = NAMES_CSS + """
  .tabs{display:flex;gap:6px;overflow-x:auto;padding-bottom:4px;margin-bottom:22px;
    scrollbar-width:none;position:sticky;top:0;z-index:5;background:var(--bg);padding-top:10px}
  .tabs::-webkit-scrollbar{display:none}
  .tabs button{font:inherit;font-size:.84rem;font-weight:700;white-space:nowrap;cursor:pointer;
    color:var(--text);background:var(--card);border:1px solid var(--border);
    padding:8px 14px;border-radius:999px}
  .tabs button:hover{border-color:var(--accent)}
  .tabs button[aria-selected=true]{background:linear-gradient(120deg,var(--accent),var(--accent-2));
    color:#fff;border-color:transparent}
  .tabs button i{font-style:normal;font-weight:600;opacity:.75;margin-left:5px;font-size:.75rem}
  [role=tabpanel][hidden]{display:none}
  .kp{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:18px}
  .kp div{background:var(--card);border:1px solid var(--border);border-radius:13px;padding:12px 14px}
  .kp b{display:block;font-size:1.35rem;letter-spacing:-.01em}
  .kp span{font-size:.76rem;color:var(--muted);font-weight:600}
  .kp b u{text-decoration:none;font-size:.75rem;color:var(--muted);font-weight:600;margin-left:3px}
  .kp small{display:block;height:5px;border-radius:999px;background:var(--bg-soft);margin-top:8px;overflow:hidden}
  .kp small i{display:block;height:100%;background:var(--c,var(--accent))}
  .tw{overflow-x:auto;border:1px solid var(--border);border-radius:14px;background:var(--card)}
  .mt{border-collapse:collapse;width:100%;font-size:.78rem}
  .mt th,.mt td{padding:8px 7px;text-align:center;border-bottom:1px solid var(--border);white-space:nowrap}
  .mt tbody tr:last-child>*{border-bottom:0}
  .mt thead th{font-size:.7rem;color:var(--muted);font-weight:800;vertical-align:bottom;line-height:1.35}
  .mt thead th em{display:block;font-style:normal;font-weight:700;color:var(--text);font-size:.74rem;margin-top:2px}
  .mt thead th[data-k]{cursor:help}
  .mt thead th[data-k]:hover,.mt thead th[data-k]:focus-visible,.mt thead th.on{color:var(--accent);outline:none}
  .hp{position:fixed;z-index:20;max-width:300px;background:var(--card);color:var(--text);
    border:1px solid var(--border);border-radius:14px;padding:14px 16px 12px;
    box-shadow:0 12px 32px rgba(0,0,0,.18);font-size:.82rem;line-height:1.55;white-space:normal;text-align:left}
  .hp[hidden]{display:none}
  .hp b{display:block;font-size:.92rem;margin-bottom:4px;padding-right:22px}
  .hp p{margin:0 0 6px}
  .hp .w{color:var(--muted)}
  .hp small{display:block;color:var(--muted);font-weight:700;font-size:.72rem;margin-top:4px}
  .hp button{position:absolute;top:8px;right:8px;border:0;background:none;color:var(--muted);
    font-size:1.1rem;line-height:1;cursor:pointer;padding:4px}
  .mt th:first-child{text-align:left;position:sticky;left:0;background:var(--card);z-index:1;
    padding-left:12px;min-width:150px}
  .mt tbody th a{display:flex;align-items:center;gap:8px;color:var(--text);text-decoration:none;font-weight:600}
  .mt tbody th a:hover{color:var(--accent)}
  .mt tbody th .ic{width:24px;height:24px;border-radius:6px}
  .mt tbody th .ic.fb{font-size:.65rem}
  .mt tbody tr:hover>*{background:var(--bg-soft)}
  .y,.n,.u{display:inline-grid;place-items:center;width:20px;height:20px;border-radius:50%;
    font-size:.7rem;font-weight:800;font-style:normal;vertical-align:middle}
  .y{background:var(--ok);color:#fff}
  .y::before{content:"✓"}
  .n{border:1.5px solid var(--muted);opacity:.45}
  .u{color:var(--muted)}
  .u::before{content:"?"}
  .na{display:inline-grid;place-items:center;width:20px;height:20px;font-style:normal;color:var(--muted)}
  .na::before{content:"–"}
  .ov2 .na{width:16px;height:16px}
  .mt thead th.t-opt{opacity:.6}
  .sc{display:inline-flex;align-items:center;gap:6px;font-variant-numeric:tabular-nums}
  .sc s{display:inline-block;width:38px;height:6px;border-radius:999px;background:var(--bg-soft);
    overflow:hidden;text-decoration:none}
  .sc s i{display:block;height:100%;background:var(--c)}
  .pct{font-weight:800}
  .ov2 th,.ov2 td{padding:6px 2px}
  .wrap{max-width:1240px}
  .ov2 thead th{white-space:normal;word-break:keep-all;min-width:34px;font-size:.64rem;line-height:1.25}
  .ov2 thead th em{font-size:.68rem}
  .ov2 thead tr:first-child th{vertical-align:middle}
  .ov2 thead tr:nth-child(2) th:first-child{position:static;text-align:center;min-width:34px;padding-left:3px}
  .ov2 th.ap{min-width:112px}
  .ov2 tbody th span{max-width:104px;overflow:hidden;text-overflow:ellipsis}
  .ov2 .gh{color:var(--text);font-size:.72rem;border-bottom:3px solid var(--c);padding:7px 4px}
  .ov2 .g0{border-left:2px solid var(--border)}
  .ov2 thead tr:first-child th+th.gh{border-left:2px solid var(--border)}
  .ov2 .y,.ov2 .n,.ov2 .u{width:16px;height:16px;font-size:.6rem}
  .ov2 td.pct{padding-right:12px;border-left:2px solid var(--border)}
  .ov2 td.lc2{font-weight:800;font-variant-numeric:tabular-nums}
  .ct td,.ct th{vertical-align:top;white-space:normal}
  .ct tbody th{min-width:96px}
  .ct tbody th b{display:block;font-size:.84rem}
  .ct tbody th em{font-style:normal;font-size:.66rem;color:var(--muted);font-weight:700}
  .ct td.cp{text-align:left;font-size:.74rem;color:var(--muted);min-width:110px}
  .ct td.cp span{display:block;white-space:nowrap;line-height:1.7}
  .ct td.lc{width:84px;text-align:left}
  .ct td.lc b{font-size:.95rem}
  .ct td.lc .lt{display:block;height:6px;border-radius:999px;background:var(--bg-soft);overflow:hidden;margin-top:6px}
  .ct td.lc .lt i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--accent-2))}
  .ct tr.zero{opacity:.6}
  .ct tbody tr:hover>*{background:transparent}
  @media(max-width:560px){.mt.ct th:first-child{min-width:62px;padding-left:10px}
    .ct td.cp{min-width:84px}.ct td.lc{width:40px}}
  .note{color:var(--muted);font-size:.78rem;margin-top:10px;max-width:720px}
  .lgd{display:flex;flex-wrap:wrap;gap:14px;font-size:.76rem;color:var(--muted);margin:0 0 10px}
  .lgd span{display:inline-flex;align-items:center;gap:6px}
  .lgd .y,.lgd .n,.lgd .u{width:16px;height:16px;font-size:.6rem}
  @media(max-width:560px){.mt th:first-child{min-width:118px}
    .mt tbody th span{max-width:80px;overflow:hidden;text-overflow:ellipsis}
    .kp{grid-template-columns:1fr 1fr}}
"""

MAT_JS = """
<script>
(function(){var tabs=document.querySelectorAll('.tabs button');if(!tabs.length)return;
function show(id){var hit=false;tabs.forEach(function(b){var on=b.getAttribute('data-t')===id;
if(on)hit=true;b.setAttribute('aria-selected',on?'true':'false');
document.getElementById('t-'+b.getAttribute('data-t')).hidden=!on;});return hit;}
var h=location.hash.slice(1);if(!h||!show(h))show(tabs[0].getAttribute('data-t'));
document.addEventListener('click',function(e){var b=e.target.closest('.tabs button');
if(b){var id=b.getAttribute('data-t');hide();show(id);history.replaceState(null,'','#'+id);return;}
if(e.target.closest('.hp'))return;var th=e.target.closest('th[data-k]');
if(!th||th===cur){hide();return;}open(th);});
var hp=document.createElement('div'),cur=null;hp.className='hp';hp.hidden=true;
hp.setAttribute('role','dialog');document.body.appendChild(hp);
function add(tag,cls,txt){if(!txt)return;var x=document.createElement(tag);if(cls)x.className=cls;
x.textContent=txt;hp.appendChild(x);}
function open(th){hide();cur=th;th.classList.add('on');hp.textContent='';
var x=document.createElement('button');x.type='button';x.setAttribute('aria-label','닫기');x.textContent='×';
x.onclick=function(){var t=cur;hide();if(t)t.focus();};hp.appendChild(x);
add('b','',th.getAttribute('data-n'));add('p','',th.getAttribute('data-h'));
add('p','w',th.getAttribute('data-w'));add('small','',th.getAttribute('data-s'));
hp.setAttribute('aria-label',th.getAttribute('data-n'));hp.hidden=false;place();}
function place(){if(!cur)return;var r=cur.getBoundingClientRect();
if(r.bottom<0||r.top>window.innerHeight){hide();return;}
var w=hp.offsetWidth,h=hp.offsetHeight,vw=document.documentElement.clientWidth;
var left=Math.min(Math.max(8,r.left+r.width/2-w/2),vw-w-8),top=r.bottom+8;
if(top+h>window.innerHeight-8)top=Math.max(8,r.top-h-8);
hp.style.left=left+'px';hp.style.top=top+'px';}
function hide(){if(cur)cur.classList.remove('on');cur=null;hp.hidden=true;}
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&cur){var t=cur;hide();t.focus();return;}
var th=e.target.closest&&e.target.closest('th[data-k]');
if(th&&(e.key==='Enter'||e.key===' ')){e.preventDefault();th===cur?hide():open(th);}});
window.addEventListener('scroll',place,true);window.addEventListener('resize',place);
window.addEventListener('hashchange',function(){hide();show(location.hash.slice(1))});})();
</script>
"""


def mat(app):
    return app.get("serviceMaturity") or {}


def area_vals(app, key):
    m = mat(app)
    if key == "devices":
        d = m.get("devices")
        return {k: (d.get(k) if d else None) for k, _ in dict((a[0], a[3]) for a in AREAS)[key]}
    return {k: (m.get(key) or {}).get(k) for k, _ in dict((a[0], a[3]) for a in AREAS)[key]}


def area_score(app, key):
    vals = [v for v in area_vals(app, key).values() if v is not None]
    return sum(1 for v in vals if v), len(vals)


def total_score(app):
    got = known = 0
    for k in SCORED:
        g, n = area_score(app, k)
        got += g
        known += n
    return got, known


def cell(v, label=""):
    t = ' title="%s"' % esc(label) if label else ""
    if v is None:
        return '<i class="u"%s></i>' % t
    return '<i class="%s"%s></i>' % ("y" if v else "n", t)


def score_color(r):
    return "#34c48a" if r >= .75 else "#5b8def" if r >= .5 else "#e0a53a" if r >= .25 else "#8b90a0"


def score_cell(got, known):
    if not known:
        return '<i class="u" title="확인 불가"></i>'
    r = got / known
    return ('<span class="sc"><s><i style="width:%d%%;--c:%s"></i></s>%d/%d</span>'
            % (round(r * 100), score_color(r), got, known))


def app_th(a):
    return ('<th><a href="%s" title="%s">%s<span>%s</span></a></th>'
            % (intro_link(a), esc(a["name"]), icon_img(a), esc(a["name"])))


LEGEND = ('<div class="lgd"><span><i class="y"></i>있음</span><span><i class="n"></i>없음</span>'
          '<span><i class="u"></i>확인 불가</span><span>열 제목을 누르면 그 항목이 무엇인지 설명이 뜹니다.</span></div>')


def area_panel(key, name, why, items, apps):
    rows = sorted(apps, key=lambda a: (-(area_score(a, key)[0]), a["name"]))
    counts = {k: sum(1 for a in apps if area_vals(a, key).get(k)) for k, _ in items}
    known = {k: sum(1 for a in apps if area_vals(a, key).get(k) is not None) for k, _ in items}
    thead = '<tr><th>앱</th>%s%s</tr>' % (
        "".join('<th%s>%s<em>%d/%d</em></th>'
                % (help_attrs(k, lbl, counts[k], known[k]), esc(lbl), counts[k], known[k])
                for k, lbl in items),
        "" if key == "devices" else "<th>갖춘 정도</th>")
    tbody = ""
    for a in rows:
        vals = area_vals(a, key)
        tbody += "<tr>%s%s%s</tr>" % (
            app_th(a), "".join("<td>%s</td>" % cell(vals[k], lbl) for k, lbl in items),
            "" if key == "devices" else "<td>%s</td>" % score_cell(*area_score(a, key)))
    kp = "".join(
        '<div><span>%s</span><b>%d<u>/ %d</u></b><small><i style="width:%d%%"></i></small></div>'
        % (esc(lbl), counts[k], known[k], round(100 * counts[k] / known[k]) if known[k] else 0)
        for k, lbl in items)
    notes = {
        "support": "노션으로 만든 페이지는 본문을 스크립트로 그려서 자동으로 읽을 수 없어 ‘확인 불가’로 둡니다. "
                   "‘열림’이 비어 있는 앱은 등록한 주소가 지금 열리지 않습니다.",
        "feedback": "앱 소스 코드에서 해당 기능을 부르는지로 판정했습니다.",
        "ops": "사용 통계와 크래시 진단은 개인을 식별하지 않는 방식만 씁니다. "
               "공통 서비스 기반은 피드백·리뷰·정책 링크를 한 번에 갖추게 해 주는 자체 패키지(LeeoKit)입니다.",
        "ux": "앱 소스 코드에서 해당 기능을 부르는지로 판정했습니다.",
        "a11y": A11Y_NOTE,
        "devices": "Mac은 Mac용으로 직접 빌드한 경우만 셉니다. Apple 실리콘 Mac에서 iPad 앱을 그대로 "
                   "여는 경우는 넣지 않았습니다.",
    }
    return ('<p class="lead">%s</p><div class="kp">%s</div>%s'
            '<div class="tw"><table class="mt"><thead>%s</thead><tbody>%s</tbody></table></div>'
            '<p class="note">%s</p>' % (esc(why), kp, LEGEND, thead, tbody, esc(notes.get(key, ""))))


def country_panel(apps):
    """국가별 언어 — 같은 말을 쓰는 나라를 한 줄로 묶어, 그 말로 쓸 수 있는 앱을 이름으로 적는다."""
    n = len(apps)
    gcolor = {lv: c for lv, _, _, c in GLOBAL}
    by_lang = {}
    for code, flag, name, langs in COUNTRIES:
        for l in langs:
            by_lang.setdefault(l, []).append((flag, name))
    rows = []
    for l, places in by_lang.items():
        users = sorted((a for a in apps if l in app_langs(a)),
                       key=lambda a: (-(reach(a) or 0), a["name"]))
        rows.append((len(users), l, places, users))
    rows.sort(key=lambda r: (-r[0], [c[3][0] for c in COUNTRIES].index(r[1])
                             if r[1] in [c[3][0] for c in COUNTRIES] else 99))
    covered = sum(1 for _, _, _, langs in COUNTRIES
                  if any(l in app_langs(a) for a in apps for l in langs))
    trs = ""
    for cnt, l, places, users in rows:
        chips = "".join(
            '<a href="%s" style="--c:%s">%s<span>%s</span></a>'
            % (intro_link(a), gcolor.get(reach(a), "#8b90a0"), icon_img(a), esc(a["name"]))
            for a in users) or '<span class="none">아직 없습니다</span>'
        trs += ('<tr%s><th><b>%s</b><em>%s</em></th><td class="cp">%s</td>'
                '<td class="lc"><b>%d</b><span class="lt"><i style="width:%.1f%%"></i></span></td>'
                '<td><div class="lnames">%s</div></td></tr>'
                % ("" if cnt else ' class="zero"', esc(LANG_KR.get(l, l)), esc(l),
                   "".join('<span>%s %s</span>' % (f, esc(nm)) for f, nm in places),
                   cnt, 100.0 * cnt / n if n else 0, chips))
    store_en = sum(1 for a in apps if (a.get("globalReach") or {}).get("englishPage"))
    return ('<p class="lead">주요 18개국 App Store에서 판매하는 앱 %d개 가운데, 그 나라 말로 쓸 수 있는 앱을 '
            '언어별로 모았습니다. 같은 말을 쓰는 나라는 한 줄로 묶었고, 18개국 중 %d개국은 현지어로 쓸 수 '
            '있는 앱이 하나 이상 있습니다. 이름 앞 색은 글로벌 지원 수준입니다.</p>'
            '<div class="tw"><table class="mt ct"><thead><tr><th>언어</th><th>쓰는 나라</th><th>앱 수</th>'
            '<th style="text-align:left">그 말로 쓸 수 있는 앱</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">App Store에 공개된 앱 언어 정보 기준이며, 18개국 모두에서 판매 중입니다. '
            '영어권에서는 앱 언어와 별개로 스토어 소개를 영어로 준비한 앱이 %d개 있습니다. 중국어는 간체·번체를 '
            '나누지 않고 한 언어로 셉니다. 인도는 영어, 캐나다는 영어·프랑스어를 현지어로 봅니다.</p>'
            % (n, covered, trs, store_en))


# 한눈에 표의 짧은 열 이름 — 누르면 긴 이름과 설명(ITEM_HELP · ITEM_WHY)이 뜬다
SHORT = {
    "registered": "등록", "reachable": "열림", "privacy": "개인정보", "english": "영어",
    "contact": "문의", "inAppFeedback": "앱 안", "mailContact": "메일", "instagram": "인스타",
    "reviewPrompt": "리뷰 요청", "writeReview": "리뷰 쓰기", "analytics": "통계",
    "crash": "크래시", "killSwitch": "원격 끄기", "tests": "테스트", "leeoKit": "LeeoKit",
    "widgets": "위젯", "shortcuts": "단축어", "cloudSync": "iCloud", "tips": "팁",
    "onboarding": "첫 안내", "voiceOver": "VoiceOver", "dynamicType": "큰 글씨", "darkMode": "다크",
    "voiceControl": "음성 제어", "structure": "읽는 순서", "actions": "VO 동작", "announcements": "변화 알림",
    "largeLayout": "큰 배치", "reduceMotion": "애니메이션", "differentiate": "색 없이", "contrast": "대비",
    "reduceTransparency": "투명도", "a11yAudit": "자동 점검", "captions": "자막", "boldText": "굵게",
    "invertColors": "색 반전", "keyboard": "키보드", "iphone": "iPhone", "ipad": "iPad",
    "mac": "Mac", "watch": "Watch", "vision": "Vision",
}
LANG_SHORT = {"KO": "한국어", "EN": "영어", "JA": "일본어", "DE": "독일어", "FR": "프랑스어",
              "ZH": "중국어", "ES": "스페인어", "PT": "포르투갈어", "HI": "힌디어", "IT": "이탈리아어",
              "VI": "베트남어", "TH": "태국어", "ID": "인니어", "RU": "러시아어", "NL": "네덜란드어",
              "PL": "폴란드어", "TR": "튀르키예어", "SV": "스웨덴어", "DA": "덴마크어", "NB": "노르웨이어",
              "FI": "핀란드어", "CS": "체코어", "EL": "그리스어", "AR": "아랍어"}
AREA_COLOR = {"lang": "#ef6aa0", "support": "#5b8def", "feedback": "#34c48a", "ops": "#e0a53a",
              "ux": "#a78bfa", "a11y": "#e8789a", "devices": "#8b90a0"}


# 서비스 숙성도는 CHECKLIST(앱별 할 일과 같은 피처 목록)로 잰다. 종합은 기본·권장 가운데 갖춘 비율.
TIER_ORDER = {"base": 0, "rec": 1, "opt": 2}
CHECK_SHORT = {
    "appEn": "앱 영어", "storeEn": "스토어 영어", "multi": "3개+ 언어", "registered": "등록", "reachable": "열림",
    "privacy": "개인정보", "contact": "문의", "english": "영어 안내", "inAppFeedback": "앱 안", "reviewPrompt": "리뷰 요청",
    "mailContact": "메일", "writeReview": "리뷰 쓰기", "instagram": "인스타", "analytics": "통계", "crash": "크래시",
    "leeoKit": "LeeoKit", "privacyManifest": "매니페스트", "killSwitch": "원격 끄기", "crashLoop": "크래시 보호",
    "performance": "성능", "logging": "로그", "funnel": "퍼널", "appSpec": "계약", "preflight": "사전 점검",
    "abTesting": "A/B", "tests": "테스트", "uiTests": "UI 테스트", "swiftlint": "SwiftLint", "ci": "CI",
    "onboarding": "첫 안내", "voiceOver": "VoiceOver", "dynamicType": "큰 글씨", "darkMode": "다크",
    "voiceControl": "음성 제어", "structure": "읽는 순서", "actions": "VO 동작", "announcements": "변화 알림",
    "largeLayout": "큰 배치", "reduceMotion": "애니메이션", "differentiate": "색 없이", "contrast": "대비",
    "reduceTransparency": "투명도", "a11yAudit": "자동 점검", "captions": "자막", "boldText": "굵게",
    "invertColors": "색 반전", "keyboard": "키보드", "tips": "팁", "emptyStates": "빈 화면", "haptics": "햅틱",
    "widgets": "위젯", "shortcuts": "단축어", "cloudSync": "iCloud", "biometricLock": "생체 잠금",
    "notifications": "알림", "fold": "폴더블", "backup": "백업", "schemaMigration": "구조 이전", "restore": "복원",
    "paywall": "페이월", "tiers": "등급", "freeGate": "무료 문턱", "discount": "할인", "tipJar": "후원",
    "tipAsk": "후원 부탁", "gift": "선물", "iapEnglish": "인앱 영어", "whatsNew": "새 기능", "roadmap": "로드맵",
    "feedbackReply": "답장", "family": "다른 앱",
    "introPage": "소개", "introScreens": "화면", "introVideo": "영상", "introScenario": "장면",
    "introSteps": "순서", "introStoreLink": "스토어", "introEnglish": "영어", "introOgImage": "미리보기",
    "introTryIt": "체험", "introProof": "후기",
    "storeCopy": "스토어 문구", "screenshotCapture": "자동 촬영", "marketingScreens": "문구 스샷",
    "localizedScreens": "언어별 스샷", "demoMode": "데모 모드", "videoAsset": "영상", "videoTool": "영상 제작",
    "promoKit": "홍보 글", "shareApp": "앱 공유", "shareImage": "공유 이미지", "shareVideo": "공유 영상",
    "deepLink": "딥링크", "offerCode": "코드 입력", "invite": "초대", "installNudge": "설치 유도",
    "moments": "순간 세기",
    "sheets": "시트",
    "liveNumbers": "숫자 효과",
    "localeFormat": "지역 표기",
    "textOverflow": "긴 글자",
    "inputFlow": "입력 흐름",
    "textCopy": "복사",
    "purchaseTest": "구매 시험",
    "releaseTags": "출시 기록",
    "steadyUpdates": "꾸준함",
    "progressive": "단계적 공개",
    "contextualLesson": "상황 수업",
    "practice": "직접 해 보기",
    "promptArbiter": "창 교통정리",
    "lessonLedger": "배운 것 기록",
}
CAT_WHY = {
    "lang": "한국어 밖의 사람도 쓸 수 있는지 봅니다.",
    "support": "App Store에 등록한 문의·안내 페이지가 열리고, 필요한 내용을 담고 있는지 봅니다.",
    "feedback": "쓰는 사람의 목소리가 만든 사람에게 닿는 길이 몇 개나 열려 있는지 봅니다.",
    "infra": "출시한 뒤에도 문제를 먼저 알아채고, 심사 없이 대응하고, 숫자로 판단할 수 있는지 봅니다.",
    "quality": "고치다 다른 곳을 망가뜨리지 않도록 자동으로 확인하는 장치가 있는지 봅니다.",
    "feature": "앱을 열지 않아도, 처음 열어도 편하게 쓸 수 있는지 봅니다.",
    "craft": "종합 점수가 높은 앱들이 공통으로 갖췄고 낮은 앱에는 드문 것을 모았습니다. 기능 목록에는 잘 안 보이지만 "
             "쓰는 사람이 ‘잘 만든 앱’이라고 느끼는 손질입니다.",
    "a11y": "눈이 불편하거나, 손을 쓰기 어렵거나, 큰 글씨가 필요하거나, 움직임에 민감한 사람도 똑같이 쓸 수 있는지 "
            "봅니다. App Store 제품 페이지의 접근성 정보 항목(VoiceOver·음성 제어·큰 텍스트·다크 인터페이스·색상 없이 "
            "구별·충분한 대비·동작 줄이기·자막·오디오 설명)에, 접근성이 좋은 앱이 더 갖추는 것을 더했습니다.",
    "data": "쓰는 사람의 데이터를 잃지 않고 옮기고 지킬 수 있는지 봅니다.",
    "money": "돈을 받는 길이 공정하고 막힘없이 설계되어 있는지 봅니다. 파는 상품이 없는 앱은 등급·할인·선물 같은 항목을 ‘해당 없음’으로 둡니다.",
    "comms": "업데이트와 계획, 답장을 쓰는 사람에게 돌려주는지 봅니다.",
    "guide": "첫 실행 화면이 있는지를 넘어, 무엇을 언제 어떻게 가르치는지 봅니다. 처음엔 단순하게 두고, 쓰는 모습이 "
             "계기가 될 때 그 기능을 직접 해 보게 하고, 안내끼리 겹쳐 서로 밀어내지 않게 하는지입니다.",
    "marketing": "앱 밖에서 사람을 데려오는 길이 있는지 봅니다.",
    "intro": "App Store에서 ‘개발자 웹사이트’를 누른 사람이 앱을 받기 전에 쓰는 모습을 그려 볼 수 있는지 봅니다.",
}
CAT_NOTE = {
    "support": "노션으로 만든 페이지는 본문을 스크립트로 그려서 자동으로 읽을 수 없어 ‘확인 불가’로 둡니다.",
    "feedback": "앱 소스 코드에서 해당 기능을 부르는지로 판정했습니다.",
    "infra": "사용 통계와 크래시 진단은 개인을 식별하지 않는 방식만 씁니다.",
    "a11y": A11Y_NOTE,
    "marketing": "앱 레포에 홍보 파이프라인(스토어 문구 · 스크린샷 촬영·합성 · 영상 · 홍보 글)이 함께 있는지는 레포 파일로, "
                 "앱 안의 장치(데모 모드 · 공유 · 딥링크 · 코드 입력 · 초대)는 앱 소스 코드로 판정했습니다. "
                 "언어별 스크린샷은 3개 이상 언어 폴더에 그림이 있을 때, 공유 장치는 같은 파일에 공유 시트가 함께 있을 때 있음으로 봅니다.",
    "intro": "소개 페이지는 App Store 마케팅 URL(한국 스토어 기준, 미국 스토어 주소가 다르면 그쪽을 영어 소개로)을 열어 판정했습니다. "
             "앱 화면은 아이콘·배지를 뺀 그림이 2장 이상일 때, 직접 체험은 긴 스크립트와 ‘직접 눌러보세요’ 같은 안내가 함께 있을 때 있음으로 봅니다. "
             "마케팅 URL 이 없으면 소개가 닿지 않으므로 나머지 항목도 모두 없음입니다.",
    "guide": "클립키보드 5.1.14 의 백지 첫 실행을 다듬으며 세운 항목이라 아직 다른 앱에는 없습니다. 선택 항목이라 할 일로 세지 않습니다. "
             "소스 코드에서 해당 장치를 부르는지로 판정했습니다.",
    "craft": "종합 상위 10개 앱과 하위 20개 앱의 코드를 견주어, 상위 앱 절반 이상이 갖췄고 하위 앱에는 드문 것을 골랐습니다. "
             "버전별 출시 기록은 버전 표시가 3개 이상, 꾸준한 손질은 최근 90일 동안 고친 기록이 20번 이상일 때 있음으로 봅니다.",
}


def check_items(cat=None):
    """(등급, 분류, 키, 이름) — 분류 순서 → 등급 순서."""
    order = {c: i for i, (c, _, _) in enumerate(CHECK_CATS)}
    rows = [(t, c, k, n) for t, c, k, n, _ in CHECKLIST if cat is None or c == cat]
    return sorted(rows, key=lambda r: (order[r[1]], TIER_ORDER[r[0]]))


def check_score(app, cat=None):
    """기본·권장 가운데 (갖춘 수, 판정한 수). 선택·해당 없음·확인 불가는 뺀다."""
    ck = checklist(app)
    vals = [v for t, c, _, v in ck.values() if t != "opt" and (cat is None or c == cat) and v not in (None, NA)]
    return sum(1 for v in vals if v is True), len(vals)


def mcell(v, label=""):
    if v == NA:
        return '<i class="na" title="%s 해당 없음"></i>' % esc(label)
    return cell(v, label)


def _item_head(t, k, n, apps, short=True):
    have = sum(1 for a in apps if checklist(a)[k][3] is True)
    known = sum(1 for a in apps if checklist(a)[k][3] not in (None, NA))
    return '<th class="t-%s"%s>%s<em>%d</em></th>' % (
        t, help_attrs(k, n, have, known, t), esc(CHECK_SHORT.get(k, n) if short else n), have)


def maturity_apps(apps):
    """서비스 숙성도 탭에 나오는 앱 — 스토어에서 내려간 앱(글로벌 지원 판정 없음)은 뺀다."""
    return [a for a in live(apps) if a.get("serviceMaturity") and a.get("globalReach")]


def maturity_sorted(apps):
    """한눈에 표의 순서 — 줄에 찬 원(✓)이 많은 앱부터. 숙성도를 재지 못한 앱은 맨 뒤(이름순)."""
    ls = maturity_apps(apps)
    lang_cols = lang_columns(ls)

    def filled(a):
        langs = app_langs(a)
        return (sum(1 for l in lang_cols if l in langs)
                + sum(1 for v in checklist(a).values() if v[3] is True)
                + sum(1 for v in area_vals(a, "devices").values() if v))
    return sorted(ls, key=lambda a: (-filled(a), -check_score(a)[0], a["name"]))


def maturity_rank(apps):
    """앱 slug → 숙성도 순위(0부터). 다른 탭이 같은 순서로 앱을 늘어놓을 때 쓴다."""
    rank = {a["_slug"]: i for i, a in enumerate(maturity_sorted(apps))}
    return lambda a: (rank.get(a["_slug"], len(rank)), a["name"])


def overview_panel(apps):
    """앱 × 피처 전체 한 표. 분류별로 머리줄을 묶고, 첫 열은 고정한 채 가로로 넘긴다."""
    cks = {a["_slug"]: checklist(a) for a in apps}
    dev_items = dict((x[0], x[3]) for x in AREAS)["devices"]
    lang_cols = lang_columns(apps)
    rows = maturity_sorted(apps)

    groups = '<tr><th rowspan="2" class="ap">앱</th>'
    cols = ""
    for c, cn, color in CHECK_CATS:
        its = check_items(c)
        extra = len(lang_cols) + 1 if c == "lang" else 0
        groups += '<th colspan="%d" class="gh" style="--c:%s">%s</th>' % (len(its) + extra, color, esc(cn))
        for i, (t, _, k, n) in enumerate(its):
            h = _item_head(t, k, n, apps)
            cols += h.replace('<th class="', '<th class="g0 ', 1) if i == 0 else h
        if c == "lang":
            cols += '<th%s>언어 수<em>%d</em></th>' % (
                help_attrs("langCount", "언어 수", 0, 0), sum(1 for a in apps if len(app_langs(a)) > 1))
            for l in lang_cols:
                have = sum(1 for a in apps if l in app_langs(a))
                cols += '<th class="t-opt"%s>%s<em>%d</em></th>' % (
                    help_attrs("lang" + l, LANG_KR.get(l, l), have, len(apps)), esc(LANG_SHORT.get(l, l)), have)
    groups += '<th colspan="%d" class="gh" style="--c:%s">기기</th><th rowspan="2">종합</th></tr>' % (
        len(dev_items), AREA_COLOR["devices"])
    for i, (k, lbl) in enumerate(dev_items):
        have = sum(1 for a in apps if area_vals(a, "devices").get(k))
        known = sum(1 for a in apps if area_vals(a, "devices").get(k) is not None)
        cols += '<th%s%s>%s<em>%d</em></th>' % (' class="g0"' if i == 0 else "", help_attrs(k, lbl, have, known),
                                               esc(SHORT.get(k, lbl)), have)
    thead = groups + "<tr>%s</tr>" % cols

    tbody = ""
    for a in rows:
        ck = cks[a["_slug"]]
        langs = app_langs(a)
        cells = ""
        for c, _, _ in CHECK_CATS:
            for i, (t, _, k, n) in enumerate(check_items(c)):
                cells += '<td%s>%s</td>' % (' class="g0"' if i == 0 else "", mcell(ck[k][3], n))
            if c == "lang":
                cells += '<td class="lc2" title="%s">%s</td>' % (esc(lang_names(a)), len(langs) if langs else '<i class="u"></i>')
                cells += "".join('<td>%s</td>' % (cell(l in langs, LANG_KR.get(l, l)) if langs else cell(None))
                                 for l in lang_cols)
        dv = area_vals(a, "devices")
        cells += "".join('<td%s>%s</td>' % (' class="g0"' if i == 0 else "", cell(dv[k], lbl))
                         for i, (k, lbl) in enumerate(dev_items))
        got, known = check_score(a)
        ok = known and mat(a).get("source")
        tbody += '<tr>%s%s<td class="pct" style="color:%s">%s</td></tr>' % (
            app_th(a), cells, score_color(got / known) if ok else "var(--muted)",
            "%d%%" % round(100 * got / known) if ok else '<i class="u" title="앱 소스를 확인하지 못했습니다"></i>')

    kp = ""
    for c, cn, color in CHECK_CATS:
        g = sum(check_score(a, c)[0] for a in apps)
        t = sum(check_score(a, c)[1] for a in apps)
        if not t:
            continue  # 선택 항목만 있는 분류는 비율이 없다
        r = g / t
        kp += ('<div><span>%s</span><b>%d%%</b><small><i style="width:%d%%;--c:%s"></i></small></div>'
               % (esc(cn), round(r * 100), round(r * 100), score_color(r)))
    legend = ('<div class="lgd"><span><i class="y"></i>있음</span><span><i class="n"></i>없음</span>'
              '<span><i class="u"></i>확인 불가</span><span><i class="na"></i>해당 없음</span>'
              '<span>흐린 열 제목은 선택 항목</span><span>열 제목을 누르면 설명이 뜹니다.</span></div>')
    return ('<p class="lead">앱 %d개가 피처 %d개 가운데 무엇을 갖췄는지 한 표에 모았습니다. 찬 원이 많은 앱부터 놓았고, '
            '열 제목 아래 숫자는 그 피처를 갖춘 앱 수입니다. 종합은 기본·권장 피처 가운데 갖춘 비율입니다.</p>'
            '<div class="kp">%s</div>%s'
            '<div class="tw"><table class="mt ov2"><thead>%s</thead><tbody>%s</tbody></table></div>'
            '<p class="note">언어 묶음은 주요 18개국에서 쓰는 말을 먼저, 그다음 앱들이 지원하는 나머지 언어를 모두 열로 보여 줍니다. '
            '나라별 언어와 기기는 종합 비율에 넣지 않았습니다. 소스 코드를 찾지 못한 앱은 앱 안의 기능을 ‘확인 불가’로 두고 '
            '분모에서 뺍니다. 판정 방법이 아직 없는 도입 예정 피처는 할 일 탭의 피처 지도에 있습니다.</p>'
            % (len(apps), len(CHECKLIST), kp, legend, thead, tbody))


def check_panel(cat, apps):
    """분류 하나 — 앱 × 그 분류의 피처."""
    its = check_items(cat)
    rows = sorted(apps, key=lambda a: (-sum(1 for v in checklist(a).values() if v[1] == cat and v[3] is True),
                                       a["name"]))
    scored = any(t != "opt" for t, _, _, _ in its)
    thead = '<tr><th>앱</th>%s%s</tr>' % ("".join(_item_head(t, k, n, apps, short=False) for t, _, k, n in its),
                                         "<th>갖춘 정도</th>" if scored else "")
    tbody = ""
    for a in rows:
        ck = checklist(a)
        tbody += "<tr>%s%s%s</tr>" % (
            app_th(a), "".join("<td>%s</td>" % mcell(ck[k][3], n) for _, _, k, n in its),
            "<td>%s</td>" % score_cell(*check_score(a, cat)) if scored else "")
    kp = ""
    for t, _, k, n in its:
        have = sum(1 for a in apps if checklist(a)[k][3] is True)
        known = sum(1 for a in apps if checklist(a)[k][3] not in (None, NA))
        kp += ('<div><span>%s · %s</span><b>%d<u>/ %d</u></b><small><i style="width:%d%%"></i></small></div>'
               % (esc(n), esc(TIER_NAME[t]), have, known, round(100 * have / known) if known else 0))
    legend = ('<div class="lgd"><span><i class="y"></i>있음</span><span><i class="n"></i>없음</span>'
              '<span><i class="u"></i>확인 불가</span><span><i class="na"></i>해당 없음</span>'
              '<span>%s</span></div>' % ("갖춘 정도는 기본·권장만 셉니다." if scored else
                                         "모두 선택 항목이라 앱 성격에 맞을 때만 갖추면 됩니다."))
    return ('<p class="lead">%s</p><div class="kp">%s</div>%s'
            '<div class="tw"><table class="mt"><thead>%s</thead><tbody>%s</tbody></table></div>%s'
            % (esc(CAT_WHY.get(cat, "")), kp, legend, thead, tbody,
               '<p class="note">%s</p>' % esc(CAT_NOTE[cat]) if cat in CAT_NOTE else ""))


def maturity_page(apps):
    # 스토어에서 내려간 앱(글로벌 지원 판정 없음)은 뺀다 — 제품 여정의 글로벌 축과 같은 기준
    ls = maturity_apps(apps)
    n = len(ls)
    todo_n = sum(len(todo_of(a)[1]) for a in ls)
    tabs = [("overview", "한눈에", None, overview_panel(ls)),
            ("todo", "할 일", "%d건" % todo_n, todo_panel(ls)),
            ("country", "국가별 언어", "%d개국" % len(COUNTRIES), country_panel(ls))]
    for c, cn, _ in CHECK_CATS:
        if c == "lang":
            continue
        g = sum(check_score(a, c)[0] for a in ls)
        t = sum(check_score(a, c)[1] for a in ls)
        tabs.append((c, cn, "%d%%" % round(100 * g / t) if t else "", check_panel(c, ls)))
    key, name, why, items = AREAS[-1]
    tabs.append((key, name, None, area_panel(key, name, why, items, ls)))

    bar = '<div class="tabs" role="tablist" aria-label="숙성도 영역">%s</div>' % "".join(
        '<button role="tab" data-t="%s" aria-selected="%s" aria-controls="t-%s">%s%s</button>'
        % (k, "true" if i == 0 else "false", k, esc(nm), "<i>%s</i>" % esc(sub) if sub else "")
        for i, (k, nm, sub, _) in enumerate(tabs))
    panels = "".join('<section role="tabpanel" id="t-%s"%s>%s</section>'
                     % (k, "" if i == 0 else " hidden", body) for i, (k, _, _, body) in enumerate(tabs))
    allg = sum(check_score(a)[0] for a in ls)
    allt = sum(check_score(a)[1] for a in ls)
    head = ('<div class="eyebrow">Service Maturity</div><h1>서비스 숙성도</h1>'
            '<p>앱 %d개가 ‘출시한 앱’을 넘어 ‘운영하는 서비스’로 얼마나 갖춰졌는지, 갖춰야 할 피처 %d개로 재 봤습니다. '
            '언어·지원 페이지·피드백·인프라·품질·기능·접근성·다듬기·데이터·수익화·소통·홍보로 나눴고, 할 일 탭에서 앱마다 남은 일을 볼 수 있습니다. '
            '지금 전체로는 기본·권장 피처의 %d%%를 갖췄습니다.</p>'
            % (n, len(CHECKLIST) + len(PLANNED), round(100 * allg / allt) if allt else 0))
    return page("서비스 숙성도 — 리이오의 앱 포트폴리오",
                "앱 %d개의 언어·지원 페이지·피드백·인프라·품질·기능·접근성·다듬기·데이터·수익화·소통·홍보 피처와 앱별 할 일을 정리했습니다." % n,
                {"head": head, "main": bar + panels}, "maturity",
                MAT_CSS + APPS_CSS + "  .wrap{max-width:1480px}\n", MAT_JS + APPS_JS)


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
        '<p class="lead">전체를 한눈에 보는 페이지들입니다.</p><div class="ovgrid">'
        '<a class="ov" href="index.html"><b>쇼케이스</b>'
        '<p>출시한 앱 전체를 문제 → 해결 방식의 이야기로 소개합니다. 한국어·영어 전환과 '
        '문제 해결 지도를 함께 제공합니다.</p></a>'
        '<a class="ov" href="lifecycle.html"><b>제품 여정</b>'
        '<p>만든 앱들을 제품 여정 다섯 단계와 글로벌 지원 수준, 두 축으로 정리했습니다.</p></a>'
        '<a class="ov" href="maturity.html"><b>서비스 숙성도</b>'
        '<p>갖춰야 할 피처(언어·지원 페이지·피드백·인프라·품질·기능·접근성·다듬기·데이터·수익화·소통·홍보)를 '
        '앱마다 무엇을 갖췄는지 한 표로 보고, 할 일 탭에서 앱별로 남은 일을 봅니다.</p></a>'
        '<a class="ov" href="business.html"><b>비즈니스 모델</b>'
        '<p>앱마다 누구에게, 언제, 무엇에 돈을 받는지 — 결제 시점 × 방식 프레임워크와 페이월, '
        'Lean Canvas로 정리했습니다.</p></a>'
        '<a class="ov" href="reddit-launch.html"><b>레딧 출격</b>'
        '<p>영어권(레딧)에서 사람을 데려와도 새지 않는 앱을 판정합니다. 미국 App Store 기준으로 '
        '영어로 읽히는지, 무료로 받아 결제까지 갈 수 있는지 봅니다.</p></a>'
        '<a class="ov" href="paywalls.html"><b>페이월 모음</b>'
        '<p>앱 안에서 결제를 권하는 화면과 가격 사다리를 한자리에 모아 앱끼리 가격을 비교합니다.</p></a>'
        '<a class="ov" href="category.html"><b>범주 · 언어 · 확산</b>'
        '<p>앱마다 어떤 문제의 답인지, 뭐라고 부를지, 무엇에 빗댈지, 누구의 사례로 넘어갈지, 어떤 습관과 싸우는지.</p></a>'
        '<a class="ov" href="shop.html"><b>생활도구점</b>'
        '<p>일상의 순간에서 출발해 나에게 맞는 앱을 고르는 가게입니다.</p></a>'
        '</div></section>'
        '<section><h2>앱별 지원 페이지<span class="hc">%d</span></h2>'
        '<p class="lead">App Store에 등록된 문의·안내 페이지입니다. 만든 시기에 따라 '
        '호스팅한 곳이 %d군데로 나뉘어 있어, 서비스별로 묶어 두었습니다.</p>%s</section>'
        % (n_sup, n_host, sup))
    return page("페이지 모음 — 리이오의 앱 포트폴리오",
                "앱 %d개의 지원 페이지와 포트폴리오 페이지를 한자리에 모았습니다." % n_live,
                {"head": head, "main": main}, "hub", HUB_CSS)


# ── 공개: 비즈니스 모델 ───────────────────────────────────────────
# 가격(price)은 sync-pricing.py 가 스토어 실데이터로, 페이월(scripts/paywalls.json)은 소스를 읽어 정리한다.
# 공개 페이지에는 상품 ID · 소스 경로 · 내부 메모(notes) · 결제 동작 여부(reachable)를 넣지 않는다.
MODELS = [
    # key, 이름, 결제 시점, 결제 방식, 한 줄 공식, 잘 맞는 경우, 조심할 점, 색
    ("paid", "유료 앱", "설치할 때", "한 번",
     "가치를 알아본 사람이 설치 전에 한 번 낸다",
     "스토어 소개만으로 쓸모가 분명하고, 한 번 사면 오래 쓰는 도구",
     "써 보기 전에 결정해야 하니 스크린샷과 소개 문구가 곧 영업이다", "#e0a53a"),
    ("freemium", "부분 유료", "써 보고 나서", "한 번",
     "무료로 쓰다가 더 쓰고 싶어진 사람이 한 번 연다",
     "핵심은 무료로 충분하고, 많이 쓰는 사람에게 한도나 고급 기능이 필요한 앱",
     "무료 몫이 너무 크면 아무도 열지 않고, 너무 작으면 써 보기 전에 떠난다", "#5b8def"),
    ("freemium-subscription", "무료 + 구독", "써 보고 나서", "계속",
     "무료로 쓰다가 계속 쓰는 사람이 기간마다 낸다",
     "콘텐츠가 늘거나 매일 여는 습관형 앱 — 내는 만큼 계속 받는다는 느낌이 있어야 한다",
     "매달 다시 결정받는 구조라, 업데이트가 멈추면 해지가 바로 따라온다", "#a78bfa"),
    ("paid+subscription", "유료 + 구독", "설치할 때", "계속",
     "설치할 때 한 번, 더 깊게 쓰는 사람은 기간마다 한 번 더",
     "기본 도구 값은 받고, 생성·저장처럼 쓸수록 비용이 드는 기능은 따로 받는 앱",
     "두 번 내라는 구조라 무엇이 기본이고 무엇이 추가인지 선이 분명해야 한다", "#34c48a"),
    ("paid+iap", "유료 + 인앱", "설치할 때", "한 번 더",
     "설치할 때 한 번, 필요한 사람은 추가 기능을 한 번 더",
     "기본 도구에 확장팩이 붙는 앱", "기본 몫이 줄어 보이면 유료 앱 값이 아깝게 느껴진다", "#34c48a"),
]
MODEL_BY = {m[0]: m for m in MODELS}
FREE_MODEL = ("free", "무료", "—", "—", "아직 돈을 받지 않는다 — 쓰는 사람과 반응을 먼저 모은다",
              "완성해 가는 단계의 앱, 브랜드를 알리는 앱", "언제 무엇에 돈을 받을지 정하지 않은 채 오래 두면 "
              "나중에 유료화할 때 '원래 무료였던 것'을 빼앗는 느낌이 든다", "#8b90a0")
KIND_KR = {"one-time-unlock": "한 번 잠금 해제", "subscription": "구독", "tip-jar": "후원",
           "consumable-pack": "소모성 팩", "mixed": "여러 방식"}

BIZ_CSS = NAMES_CSS + """
  .wrap{max-width:1160px}
  .kp{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:8px}
  .kp div{background:var(--card);border:1px solid var(--border);border-radius:13px;padding:12px 14px}
  .kp b{display:block;font-size:1.35rem;letter-spacing:-.01em}
  .kp span{font-size:.76rem;color:var(--muted);font-weight:600}
  .grid2{display:grid;grid-template-columns:110px minmax(0,1fr) minmax(0,1fr);gap:8px}
  .cell .when{display:none;font-size:.7rem;color:var(--muted);font-weight:800;margin-bottom:2px}
  .grid2 .ax{font-size:.74rem;font-weight:800;color:var(--muted);display:flex;align-items:center;
    justify-content:center;text-align:center}
  .cell{background:var(--card);border:1px solid var(--border);border-top:3px solid var(--c);
    border-radius:13px;padding:13px 14px;min-height:140px}
  .cell.empty{opacity:.45;border-top-color:var(--border)}
  .cell h3{font-size:.95rem;display:flex;gap:7px;align-items:baseline}
  .cell h3 i{font-style:normal;font-size:.74rem;color:var(--muted);font-weight:700}
  .cell .f{font-size:.8rem;color:var(--muted);margin:3px 0 9px}
  .freeband{margin-top:8px;background:var(--card);border:1px dashed var(--border);border-radius:13px;padding:13px 14px}
  .freeband h3{font-size:.95rem}
  .mods{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:10px}
  .mod{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--c);border-radius:13px;padding:13px 15px}
  .mod b{font-size:.92rem}
  .mod dl{font-size:.78rem;margin-top:6px}
  .mod dt{color:var(--muted);font-weight:800;font-size:.68rem;margin-top:6px}
  .xt{border-collapse:collapse;width:100%;font-size:.8rem;background:var(--card);border-radius:13px;overflow:hidden}
  .tw{overflow-x:auto;border:1px solid var(--border);border-radius:14px}
  .xt th,.xt td{border-bottom:1px solid var(--border);padding:9px 10px;text-align:left;vertical-align:top}
  .xt thead th{font-size:.7rem;color:var(--muted);font-weight:800}
  .xt tbody th{white-space:nowrap;font-size:.8rem}
  .xt tbody tr:last-child>*{border-bottom:0}
  .xt td .lnames{min-width:120px}
  .pws{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
  .pw{background:var(--card);border:1px solid var(--border);border-radius:22px;overflow:hidden;display:flex;flex-direction:column}
  .pw .top{padding:18px 18px 14px;background:radial-gradient(120% 120% at 50% 0%,
    color-mix(in srgb,var(--c) 22%,transparent),transparent)}
  .pw .app{display:flex;align-items:center;gap:9px;font-size:.8rem;font-weight:700;color:var(--muted)}
  .pw .app .ic{width:30px;height:30px;border-radius:8px}
  .pw .app em{margin-left:auto;font-style:normal;font-size:.68rem;padding:2px 9px;border-radius:999px;
    background:var(--bg-soft);border:1px solid var(--border)}
  .pw h3{font-size:1.12rem;margin-top:12px;line-height:1.35;word-break:keep-all}
  .pw .sub{font-size:.8rem;color:var(--muted);margin-top:4px;word-break:keep-all}
  .pw ul{list-style:none;padding:0 18px;font-size:.8rem}
  .pw ul li{padding:3px 0 3px 22px;position:relative;word-break:keep-all}
  .pw ul li::before{content:"✓";position:absolute;left:2px;color:var(--c);font-weight:900}
  .tiers{padding:12px 18px 4px;display:grid;gap:6px}
  .tier{display:flex;align-items:center;gap:8px;border:1.5px solid var(--border);border-radius:12px;padding:8px 11px;font-size:.8rem}
  .tier b{margin-left:auto;font-variant-numeric:tabular-nums}
  .tier small{font-size:.68rem;color:var(--muted)}
  .tier.off{opacity:.55;border-style:dashed}
  .cta{margin:10px 18px 6px;text-align:center;border-radius:12px;padding:10px;font-weight:800;font-size:.85rem;
    color:#fff;background:var(--c)}
  .fine{text-align:center;font-size:.68rem;color:var(--muted);padding:0 18px 14px}
  .gate{border-top:1px solid var(--border);padding:12px 18px 16px;font-size:.76rem;display:grid;gap:8px;margin-top:auto}
  .gate h4{font-size:.66rem;color:var(--muted);font-weight:800;letter-spacing:.04em}
  .gate p{margin:1px 0;word-break:keep-all}
  .gate .when span{display:inline-block;background:var(--bg-soft);border:1px solid var(--border);
    border-radius:999px;padding:1px 8px;margin:2px 3px 0 0;font-size:.7rem}
  .canv{display:grid;gap:8px}
  .canv details{background:var(--card);border:1px solid var(--border);border-radius:13px}
  .canv summary{display:flex;align-items:center;gap:10px;padding:10px 14px;cursor:pointer;list-style:none;font-size:.85rem}
  .canv summary::-webkit-details-marker{display:none}
  .canv summary .ic{width:28px;height:28px;border-radius:7px}
  .canv summary b{font-weight:700}
  .canv summary .m{font-size:.7rem;font-weight:800;color:#fff;background:var(--c);border-radius:999px;padding:2px 9px}
  .canv summary .pr{margin-left:auto;font-size:.76rem;color:var(--muted);text-align:right}
  .lc{display:grid;grid-template-columns:repeat(5,1fr);grid-template-rows:auto auto auto;gap:1px;
    background:var(--border);border-top:1px solid var(--border);border-radius:0 0 13px 13px;overflow:hidden}
  .lc>div{background:var(--card);padding:10px 12px;font-size:.78rem;word-break:keep-all}
  .lc h4{font-size:.64rem;letter-spacing:.06em;color:var(--muted);font-weight:800;margin-bottom:3px}
  .lc .pb{grid-column:1;grid-row:1/3}.lc .so{grid-column:2;grid-row:1}.lc .km{grid-column:2;grid-row:2}
  .lc .uv{grid-column:3;grid-row:1/3}.lc .ch{grid-column:4;grid-row:2}.lc .ad{grid-column:4;grid-row:1}
  .lc .cs{grid-column:5;grid-row:1/3}.lc .co{grid-column:1/3;grid-row:3}.lc .rv{grid-column:3/6;grid-row:3}
  .lc .na{color:var(--muted)}
  .note{color:var(--muted);font-size:.78rem;margin-top:10px;max-width:760px}
  @media(max-width:760px){.lc{grid-template-columns:1fr 1fr}
    .lc>div{grid-column:auto!important;grid-row:auto!important}.lc .uv,.lc .rv{grid-column:1/3!important}
    .grid2{grid-template-columns:minmax(0,1fr)}.grid2 .ax{display:none}.cell{min-height:0}.cell .when{display:block}
    .lnames a{white-space:normal}}
"""


def load_paywalls():
    path = os.path.join(ROOT, "scripts/paywalls.json")
    if not os.path.exists(path):
        return {}
    return json.load(open(path, encoding="utf-8")).get("apps", {})


def load_showcase():
    path = os.path.join(ROOT, "scripts/showcase-content.json")
    return json.load(open(path, encoding="utf-8")).get("apps", {}) if os.path.exists(path) else {}


def model_of(app):
    return MODEL_BY.get((app.get("price") or {}).get("pricingModel")) or FREE_MODEL


def price_text(app):
    """가격 사다리 — 앱 가격 + 스토어에 있는 인앱결제 상품."""
    p = app.get("price") or {}
    parts = []
    if p.get("priceKRW"):
        parts.append("앱 ￦{:,}".format(p["priceKRW"]))
    elif p.get("priceUSD"):
        parts.append("앱 ${}".format(p["priceUSD"]))
    for it in p.get("iapItems") or []:
        parts.append("%s %s" % (it["name"], it["price"]))
    return parts


def chips(ls):
    if not ls:
        return '<span class="none">없음</span>'
    return '<div class="lnames">%s</div>' % "".join(
        '<a href="#bm-%s" style="--c:%s">%s%s</a>' % (esc(a["_slug"]), model_of(a)[7], icon_img(a), esc(a["name"]))
        for a in ls)


def paywall_card(app, pw):
    m = model_of(app)
    store = {it["name"]: it["price"] for it in (app.get("price") or {}).get("iapItems") or []}
    tiers = pw.get("tiers") or []
    rows = ""
    for t in tiers:
        price = with_us(t.get("price"), t.get("priceUS"))
        rows += ('<div class="tier%s"><span>%s%s</span><b>%s</b></div>'
                 % ("" if t.get("live") else " off", esc(t.get("label") or t.get("period") or "상품"),
                    " <small>· %s</small>" % esc(t["period"]) if t.get("period") and t.get("period") not in (t.get("label") or "") else "",
                    esc(price) if t.get("live") else "<small>스토어 준비 중</small>" + (" " + esc(price) if price else "")))
    if not tiers and store:
        rows = "".join('<div class="tier"><span>%s</span><b>%s</b></div>' % (esc(k), esc(v)) for k, v in store.items())
    bl = "".join("<li>%s</li>" % esc(b) for b in (pw.get("benefits") or [])[:6])
    free = "".join("<p>%s</p>" % esc(x) for x in (pw.get("free") or [])[:4]) or "<p>—</p>"
    lock = "".join("<p>%s</p>" % esc(x) for x in (pw.get("locked") or [])[:4]) or "<p>—</p>"
    when = "".join("<span>%s</span>" % esc(x) for x in (pw.get("triggers") or [])[:4]) or "<span>—</span>"
    fine = " · ".join(x for x in [pw.get("trial"), "구매 복원" if pw.get("restore") else None] if x)
    return (
        '<article class="pw" id="pw-%s" style="--c:%s"><div class="top"><div class="app">%s%s<em>%s</em></div>'
        '<h3>%s</h3>%s</div>%s<div class="tiers">%s</div>%s%s'
        '<div class="gate"><div><h4>무료로 주는 것</h4>%s</div><div><h4>돈을 내면 열리는 것</h4>%s</div>'
        '<div class="when"><h4>언제 보이나</h4>%s</div><div><h4>후원</h4><p>%s</p></div></div></article>'
        % (esc(app["_slug"]), m[7], icon_img(app), esc(app["name"]), esc(KIND_KR.get(pw.get("kind"), m[1])),
           esc(pw.get("headline") or app["name"]),
           '<p class="sub">%s</p>' % esc(pw["subheadline"]) if pw.get("subheadline") else "",
           "<ul>%s</ul>" % bl if bl else "", rows,
           '<div class="cta">%s</div>' % esc(pw["cta"]) if pw.get("cta") else "",
           '<div class="fine">%s</div>' % esc(fine) if fine else "",
           free, lock, when, donation_text(app["_slug"])))


def canvas(app, sc, pw):
    m = model_of(app)
    lc = app.get("lifecycle") or {}
    g = app.get("globalReach") or {}
    na = '<span class="na">—</span>'

    def cell(cls, title, body):
        return '<div class="%s"><h4>%s</h4>%s</div>' % (cls, title, body or na)

    metrics = []
    if lc.get("stage"):
        metrics.append("제품 여정 %d단계 · %s" % (lc["stage"], STAGE_SHORT.get(lc["stage"], "")))
    if lc.get("polishDays") is not None:
        metrics.append("출시 후 다듬은 기간 %d일" % lc["polishDays"])
    metrics.append("스토어 평점 %d개" % (lc.get("ratingCount") or 0))
    ch = ["App Store%s" % (" · %d개국 판매" % g["storefronts"] if g.get("storefronts") else "")]
    if g:
        ch.append("앱 언어: " + lang_names(app))
    rv = "<b>%s</b> — %s<br>%s" % (esc(m[1]), esc(m[4]), esc(" · ".join(price_text(app)) or "받는 돈 없음"))
    if pw and pw.get("locked"):
        rv += "<br><span class='na'>유료로 여는 것: %s</span>" % esc(" · ".join(pw["locked"][:3]))
    summary = ('<summary>%s<b>%s</b><span class="m" style="--c:%s">%s</span><span class="pr">%s</span></summary>'
               % (icon_img(app), esc(app["name"]), m[7], esc(m[1]),
                  esc(" · ".join(price_text(app)[:2]) or "무료")))
    return ('<details id="bm-%s">%s<div class="lc">%s%s%s%s%s%s%s%s%s</div></details>'
            % (esc(app["_slug"]), summary,
               cell("pb", "문제", esc(sc.get("problem"))),
               cell("so", "솔루션", esc(sc.get("solution"))),
               cell("km", "핵심 지표", "<br>".join(esc(x) for x in metrics)),
               cell("uv", "고유 가치 제안", "<b>%s</b><br>%s" % (esc(sc.get("highlight") or ""), esc(sc.get("tagline") or ""))
                    if sc else ""),
               cell("ad", "경쟁 우위", ""),
               cell("ch", "채널", "<br>".join(esc(x) for x in ch)),
               cell("cs", "고객", "%s<br><span class='na'>%s</span>" % (esc(sc.get("stakeholders") or ""), esc(sc.get("persona") or ""))
                    if sc else ""),
               cell("co", "비용 구조", "1인 개발 · Apple 개발자 프로그램 연 1회 · 서버 비용은 앱마다 다름"),
               cell("rv", "수익원", rv)))


def business_page(apps):
    ls = [a for a in live(apps) if (a.get("price") or {}).get("evaluatedAt")]
    pws = load_paywalls()
    scs = load_showcase()
    by = {}
    for a in ls:
        by.setdefault(model_of(a)[0], []).append(a)
    n = len(ls)
    paying = n - len(by.get("free", []))
    subs = len(by.get("freemium-subscription", [])) + len(by.get("paid+subscription", []))

    def has_paywall(a):
        pw = pws.get(a["_slug"]) or {}
        return pw.get("kind") not in (None, "none") and (pw.get("headline") or pw.get("benefits") or pw.get("locked"))

    def selling(a):  # 스토어에 상품이 있고, 출시 빌드에서 결제 화면이 켜져 있다
        return (a.get("price") or {}).get("hasInAppPurchases") and not pws[a["_slug"]].get("hidden")

    live_pw = [a for a in ls if has_paywall(a) and selling(a)]
    prep_pw = [a for a in ls if has_paywall(a) and not selling(a)]

    head = ('<div class="eyebrow">Business Model</div><h1>비즈니스 모델</h1>'
            '<p>앱 %d개가 누구에게, 언제, 무엇에 돈을 받는지 정리했습니다. 가격은 App Store 실데이터, '
            '페이월은 앱 소스에서 읽었습니다.</p>' % n)

    kp = '<div class="kp">%s</div>' % "".join(
        '<div><b>%s</b><span>%s</span></div>' % (v, esc(k)) for k, v in [
            ("돈을 받는 앱", "%d / %d" % (paying, n)), ("설치할 때 받는 앱", len(by.get("paid", [])) + len(by.get("paid+subscription", []))),
            ("써 본 뒤 받는 앱", len(by.get("freemium", [])) + len(by.get("freemium-subscription", []))),
            ("구독이 있는 앱", subs), ("앱 안 결제 화면", len(live_pw))])

    # 프레임워크 — 결제 시점 × 결제 방식
    def cell_for(key):
        mm = MODEL_BY[key]
        a = by.get(key, [])
        return ('<div class="cell%s" style="--c:%s"><div class="when">%s · %s 낸다</div><h3>%s<i>%d개</i></h3><p class="f">%s</p>%s</div>'
                % ("" if a else " empty", mm[7], esc(mm[2]), esc(mm[3]), esc(mm[1]), len(a), esc(mm[4]), chips(a)))

    paid_sub = by.get("paid+subscription", []) + by.get("paid+iap", [])
    sub_cell = ('<div class="cell%s" style="--c:%s"><div class="when">설치할 때 · 계속 낸다</div><h3>유료 + 구독·인앱<i>%d개</i></h3><p class="f">%s</p>%s</div>'
                % ("" if paid_sub else " empty", MODEL_BY["paid+subscription"][7], len(paid_sub),
                   esc(MODEL_BY["paid+subscription"][4]), chips(paid_sub)))
    grid = ('<div class="grid2"><div></div><div class="ax">한 번 낸다</div><div class="ax">계속 낸다</div>'
            '<div class="ax">설치할 때</div>%s%s'
            '<div class="ax">써 보고 나서</div>%s%s</div>'
            '<div class="freeband"><h3>아직 받지 않음 · 무료 <span class="hc">%d개</span></h3>'
            '<p class="f note" style="margin:3px 0 9px">%s</p>%s</div>'
            % (cell_for("paid"), sub_cell, cell_for("freemium"), cell_for("freemium-subscription"),
               len(by.get("free", [])), esc(FREE_MODEL[4]), chips(by.get("free", []))))

    mods = '<div class="mods">%s</div>' % "".join(
        '<div class="mod" style="--c:%s"><b>%s</b><dl><dt>누가 · 언제 · 어떻게</dt><dd>%s · %s</dd>'
        '<dt>공식</dt><dd>%s</dd><dt>잘 맞는 앱</dt><dd>%s</dd><dt>조심할 점</dt><dd>%s</dd></dl></div>'
        % (mm[7], esc(mm[1]), esc(mm[2]), esc(mm[3]), esc(mm[4]), esc(mm[5]), esc(mm[6]))
        for mm in [FREE_MODEL] + MODELS[:4])

    # 수익 모델 × 제품 여정 단계
    stages = sorted({(a.get("lifecycle") or {}).get("stage") for a in ls if (a.get("lifecycle") or {}).get("stage")},
                    reverse=True)
    order = [FREE_MODEL] + MODELS[:4]
    xt = ('<div class="tw"><table class="xt"><thead><tr><th>단계</th>%s</tr></thead><tbody>%s</tbody></table></div>'
          % ("".join("<th>%s</th>" % esc(mm[1]) for mm in order),
             "".join("<tr><th>%d · %s</th>%s</tr>" % (st, esc(STAGE_SHORT.get(st, "")), "".join(
                 "<td>%s</td>" % chips([a for a in by.get(mm[0], []) if (a.get("lifecycle") or {}).get("stage") == st])
                 for mm in order)) for st in stages)))

    pw_live = '<div class="pws">%s</div>' % "".join(paywall_card(a, pws[a["_slug"]]) for a in live_pw)
    pw_prep = '<div class="pws">%s</div>' % "".join(paywall_card(a, pws[a["_slug"]]) for a in prep_pw)

    groups = ""
    for mm in MODELS + [FREE_MODEL]:
        a = by.get(mm[0], [])
        if not a:
            continue
        groups += ('<h3 style="margin:18px 0 8px;font-size:.95rem">%s <span class="hc">%d</span></h3><div class="canv">%s</div>'
                   % (esc(mm[1]), len(a), "".join(canvas(x, scs.get(x["_slug"]) or {}, pws.get(x["_slug"])) for x in a)))

    main = (
        '<section>%s</section>'
        '<section><h2>결제 시점 × 결제 방식</h2><p class="lead">돈을 <b>언제</b>(설치할 때 / 써 보고 나서) '
        '<b>어떻게</b>(한 번 / 계속) 받느냐로 나누면 네 칸이 됩니다. 칸마다 사용자에게 하는 약속이 다릅니다.</p>%s</section>'
        '<section><h2>모델별 공식</h2><p class="lead">같은 칸에 있는 앱은 같은 질문에 답해야 합니다.</p>%s</section>'
        '<section><h2>수익 모델 × 제품 여정</h2><p class="lead">단계가 올라갈수록 돈을 받는 방식이 분명해지는지 봅니다. '
        '아직 완성해 가는 단계(1단계)라면 무료로 반응을 먼저 모으는 것이 자연스럽습니다.</p>%s</section>'
        '<section><h2>페이월<span class="hc">%d</span></h2><p class="lead">앱 안에서 결제를 권하는 화면입니다. '
        '앱 소스에서 문구와 혜택, 무료 몫, 화면이 뜨는 시점을 읽어 그대로 옮겼습니다. 가격은 App Store 기준입니다.</p>%s</section>'
        '%s'
        '<section><h2>앱별 비즈니스 모델 캔버스</h2><p class="lead">Lean Canvas 아홉 칸으로 앱마다 펼쳐 볼 수 있습니다. '
        '문제·고객·가치 제안은 쇼케이스 소개에서, 수익원은 스토어에서, 핵심 지표는 제품 여정에서 가져왔습니다.</p>%s'
        '<p class="note">경쟁 우위 칸은 앱마다 근거 있는 자료가 아직 없어 비워 두었습니다. 비용 구조는 1인 개발이라 앱마다 거의 같습니다.</p></section>'
        % (kp, grid, mods, xt, len(live_pw), pw_live,
           ('<section><h2>준비 중인 페이월<span class="hc">%d</span></h2><p class="lead">결제 화면은 만들어 두었지만 '
            '아직 판매를 열지 않은 앱입니다.</p>%s</section>' % (len(prep_pw), pw_prep)) if prep_pw else "",
           groups))
    return page("비즈니스 모델 — 리이오의 앱 포트폴리오",
                "앱 %d개의 수익 모델과 페이월을 결제 시점 × 결제 방식 프레임워크와 Lean Canvas로 정리했습니다." % n,
                {"head": head, "main": main}, "biz", BIZ_CSS)


# ── 공개: 페이월 모음 ─────────────────────────────────────────────
# 비즈니스 모델 페이지의 페이월 카드만 모으고, 앱끼리 가격을 견줄 수 있게 기간별 비교표를 붙인다.
# 공개 페이지라 내부 판정(가격이 맞나·고칠 곳)은 넣지 않는다 — 사실(가격·기간·무료 몫)만.
PERIODS = [("주", "주간"), ("월", "월간"), ("연", "연간"), ("평생", "평생"), ("1회", "1회")]
PW_CSS = BIZ_CSS + """
  .pt{border-collapse:collapse;width:100%;font-size:.8rem;background:var(--card)}
  .pt th,.pt td{border-bottom:1px solid var(--border);padding:9px 10px;text-align:right;white-space:nowrap;
    font-variant-numeric:tabular-nums}
  .pt thead th{font-size:.7rem;color:var(--muted);font-weight:800}
  .pt th:first-child,.pt td.k{text-align:left}
  .pt tbody th{text-align:left}
  .pt tbody th a{display:flex;align-items:center;gap:8px;color:var(--text);text-decoration:none;font-weight:600}
  .pt tbody th a:hover{color:var(--accent)}
  .pt tbody th .ic{width:24px;height:24px;border-radius:6px}
  .pt tbody tr:last-child>*{border-bottom:0}
  .pt td.k{color:var(--muted);font-size:.74rem}
  .pt td.r{color:var(--muted);font-size:.74rem;text-align:left;white-space:normal;min-width:150px}
  .pt td small{display:block;font-size:.66rem;color:var(--muted);font-weight:600}
  .pt td.off{color:var(--muted)}
  .pt td.off b{font-weight:500;text-decoration:line-through dashed}
  .pt .na{color:var(--border)}
  .pt tr.grp th{background:var(--bg-soft);font-size:.72rem;color:var(--muted);font-weight:800;text-align:left;padding:6px 10px}
  .rules{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:14px 0}
  .rules>div{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 16px}
  .rules h4{margin:0 0 6px;font-size:.95rem}
  .rules p{margin:0;font-size:.85rem;color:var(--muted);line-height:1.55}
  h3.sh{margin:26px 0 10px;font-size:1.05rem}
  /* 설계안 카드: 글이 길어 두 줄 그리드 · 넉넉한 안쪽 여백 · 묶음마다 간격 */
  .npws{grid-template-columns:repeat(auto-fill,minmax(min(420px,100%),1fr));gap:22px}
  .np .top{padding:24px 26px 18px}
  .np h3{font-size:1.2rem;margin-top:14px}
  .np .sub{font-size:.84rem;line-height:1.6;margin-top:6px}
  .np .tiers{padding:4px 26px 22px;gap:8px}
  .np .tier{padding:11px 14px;font-size:.84rem;gap:14px;align-items:baseline}
  .np .tier span{flex:none;color:var(--muted)}
  .np .tier b{text-align:right;line-height:1.5;word-break:keep-all}
  .np .tier{flex-wrap:wrap}
  .np .tier ul{flex-basis:100%;margin:2px 0 0;padding:10px 0 0;border-top:1px dashed var(--border);
    display:grid;gap:2px;font-size:.82rem;line-height:1.55}
  .np .tier ul li{padding:1px 0 1px 22px}
  .np .why,.np .moments{border-top:1px solid var(--border);padding:22px 26px}
  .np h4{margin:0 0 12px;font-size:.74rem;color:var(--muted);font-weight:800;letter-spacing:.04em}
  .np .why p{margin:0;font-size:.92rem;line-height:1.8;word-break:keep-all}
  .np .moments ul{margin:0;padding:0;list-style:none;display:grid;gap:20px}
  .np .moments li{display:grid;gap:5px;padding:0 0 0 24px;font-size:.88rem;line-height:1.65;word-break:keep-all}
  .np .moments li::before{top:1px}
  .np .moments li b{font-size:.94rem}
  .np .moments li small{font-size:.86rem}
  .np .moments li span{color:var(--muted);font-size:.86rem}
  .np .moments li em{justify-self:start;margin-top:3px;font-style:normal;font-weight:700;font-size:.76rem;color:var(--c);
    padding:2px 10px;border-radius:999px;background:color-mix(in srgb,var(--c) 14%,transparent)}
  .pt.pl th,.pt.pl td{padding:14px 16px;vertical-align:middle}
  .pt.pl td.r{min-width:320px;font-size:.84rem;line-height:1.7;word-break:keep-all}
  .pt.pl tr.grp th{padding:12px 16px;font-size:.78rem;line-height:1.6;white-space:normal}
  @media (max-width:520px){.np .top,.np .why,.np .moments{padding-left:18px;padding-right:18px}
    .np .tiers{padding-left:18px;padding-right:18px}.np .tier{flex-wrap:wrap}}
  .pt.dn td.r{min-width:190px;line-height:1.55}
  .kp a.kpl{display:block;background:var(--card);border:1px solid var(--border);border-radius:13px;padding:12px 14px;
    color:var(--text);text-decoration:none}
  .kp a.kpl:hover{border-color:var(--accent)}
  .np .don h4{display:flex;align-items:center;gap:8px}
  .ttw{margin:0 20px 18px;overflow-x:auto;border:1px solid var(--border);border-radius:14px}
  .tt{border-collapse:collapse;width:100%;font-size:.84rem;background:var(--card)}
  .tt th,.tt td{padding:9px 10px;border-bottom:1px solid var(--border);text-align:center;vertical-align:middle;word-break:keep-all}
  .tt thead th{vertical-align:top;background:var(--bg-soft);min-width:96px}
  .tt thead th:first-child{min-width:0}
  .tt thead .tn{display:block;font-size:1rem;font-weight:800;margin-bottom:6px;color:var(--text)}
  .tt thead .tc-pro .tn{color:var(--c)}
  .tt thead .tp{display:block;font-size:.84rem;font-variant-numeric:tabular-nums;color:var(--text)}
  .tt thead .tp.tl{margin-top:4px}
  .tt thead small{display:block;font-size:.72rem;color:var(--muted);font-weight:600}
  .tt thead em{display:block;font-style:normal;font-size:.74rem;font-weight:600;color:var(--muted);margin-top:6px;line-height:1.45}
  .tt tbody th{text-align:left;font-weight:600;color:var(--text);min-width:8em}
  .tt td.ok{color:#34c48a;font-weight:900;font-size:1rem}
  .tt td.no{color:var(--muted);opacity:.5}
  .tt td.inf{font-size:1.25rem;font-weight:700;line-height:1;color:var(--text)}
  .tt tbody tr:last-child>*{border-bottom:0}
  .tx{margin:-8px 20px 16px;font-size:.78rem;color:var(--muted);line-height:1.6}
  .ftw{max-height:78vh;overflow:auto}
  .ft{border-collapse:separate;border-spacing:0;font-size:.82rem;background:var(--card);min-width:100%}
  .ft th,.ft td{border-bottom:1px solid var(--border);padding:8px 6px;text-align:center;white-space:nowrap}
  .ft thead th{position:sticky;top:0;z-index:2;background:var(--card);font-size:.74rem;color:var(--muted);font-weight:800;
    vertical-align:bottom;cursor:help}
  .ft thead th span{display:block}
  .ft thead th i{display:block;font-style:normal;color:var(--text);font-size:.8rem;margin-top:2px}
  .ft tbody th{position:sticky;left:0;z-index:1;background:var(--card);text-align:left}
  .ft thead th:first-child{left:0;z-index:3;cursor:default}
  .ft tbody th a{display:flex;align-items:center;gap:8px;color:var(--text);text-decoration:none;font-weight:600}
  .ft tbody th .ic{width:24px;height:24px;border-radius:6px}
  .ft td.y{color:#34c48a;font-weight:900;font-size:.95rem}
  .ft td.n{color:var(--border);font-weight:900}
  .ft td.u{color:var(--muted)}
  .ft td.m,.ft th.m{text-align:left;color:var(--muted);font-size:.76rem}
  .ft td.c{font-weight:800;font-variant-numeric:tabular-nums}
  .ft td.k{text-align:left}
  .ft tbody tr:hover>*{background:var(--bg-soft)}
  .tiers3 .nd{font-weight:700;color:var(--text);margin-bottom:8px}
  .tiers3 ul{margin:0;padding-left:18px;font-size:.85rem;line-height:1.6;color:var(--muted)}
  ol.steps,ul.steps{margin:0;padding-left:22px;font-size:.88rem;line-height:1.8;max-width:820px}
  .pt.dn td.r b{color:var(--text);font-weight:600}
  .pt.dn td.r small{margin-top:3px}
  .vd{display:inline-block;font-weight:700;color:var(--c);border:1px solid var(--c);border-radius:999px;padding:1px 8px;font-size:.72rem}
"""


def with_us(price, us):
    """'₩17,000' + '$9.99' → '₩17,000 ($9.99)'. 원래 달러면 그대로."""
    if not price or not us or price.startswith("$"):
        return price or us or ""
    return "%s (%s)" % (price, us)


def krw(price):
    """'￦17,000' · '₩1,100' → 17000. 달러 등 다른 통화는 None."""
    if not price or not re.search(r"[￦₩]", price):
        return None
    d = re.sub(r"[^\d]", "", price)
    return int(d) if d else None


def ladder_row(app, pw):
    by = {}
    for t in pw.get("tiers") or []:
        by.setdefault(t.get("period"), []).append(t)
    cells = ""
    for key, _ in PERIODS:
        ts = by.get(key) or []
        if not ts:
            cells += '<td><span class="na">—</span></td>'
            continue
        t = ts[0]
        extra = " 외 %d" % (len(ts) - 1) if len(ts) > 1 else ""
        if t.get("live"):
            cells += "<td><b>%s</b><small>%s%s</small></td>" % (esc(with_us(t.get("price"), t.get("priceUS"))), esc(t.get("label") or ""), extra)
        else:
            cells += ('<td class="off"><b>%s</b><small>스토어 준비 중</small></td>'
                      % esc(with_us(t.get("price"), t.get("priceUS")) or "—"))
    # 기간끼리의 비율 — 팔리는 상품끼리만 견준다
    live_p = {t.get("period"): krw(t.get("price")) for t in (pw.get("tiers") or []) if t.get("live")}
    rel = []
    if live_p.get("평생") and live_p.get("연"):
        rel.append("평생 = 연간 %.1f년치" % (live_p["평생"] / live_p["연"]))
    if live_p.get("연") and live_p.get("월"):
        rel.append("연간 = 월간 %.1f개월치" % (live_p["연"] / live_p["월"]))
    if live_p.get("월") and live_p.get("주"):
        rel.append("월간 = 주간 %.1f주치" % (live_p["월"] / live_p["주"]))
    p = app.get("price") or {}
    us = (app.get("usStore") or {}).get("price")
    ap = with_us("￦{:,}".format(p["priceKRW"]), us and "$%.2f" % us) if p.get("priceKRW") else "무료"
    return ('<tr><th><a href="#pw-%s">%s<span>%s</span></a></th><td class="k">%s</td><td>%s</td>%s<td class="r">%s</td></tr>'
            % (esc(app["_slug"]), icon_img(app), esc(app["name"]),
               esc(KIND_KR.get(pw.get("kind"), "")), ap, cells, esc(" · ".join(rel)) or "—"))


# ── 페이월 탭: 다음 페이월(설계안) ─────────────────────────────────
# scripts/paywall-plans.json 을 읽는다. 1순위 다섯 앱은 확정안, 나머지는 옛 규칙의 판단이라 그렇게 나눠 적는다.
# 상품 ID · 근거 소스 경로는 내보내지 않는다.
PLAN_VERDICT = {"new": ("새로 설계", "#34c48a"), "adjust": ("고칠 것", "#e0a53a"), "keep": ("지금도 충분", "#8b90a0")}


def load_paywall_plans():
    path = os.path.join(ROOT, "scripts", "paywall-plans.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def public_text(s):
    """설계안 문장에서 상품 ID · 파일 이름 같은 내부 표기를 걷어 낸다(공개 페이지용)."""
    s = re.sub(r"\s*\([^()]*(?:com\.|iCloud\.|\.swift|originalAppVersion|ProMark|productId|\.md\b|\.txt\b|\.json\b|쇼케이스|메타데이터|metadata|serviceMaturity|lifecycle|revenueGates|appstore-cache)[^()]*\)", "", s or "")
    s = s.replace("APPSTORE.md", "스토어 문구 원고").replace("REDESIGN.md", "다시 설계 문서")
    return re.sub(r"\s{2,}", " ", s).strip()


def trim_table(p, fp_price=""):
    """설계안 트림을 비교표로 — 열은 무료 · Plus · Pro, 머리에 가격 · 한 줄, 행은 기능(compare)."""
    trims = p.get("trims") or []
    if not trims:
        return ""

    def price_cell(tr):
        if not tr.get("price"):
            return ""  # 열 이름이 이미 '무료'다
        out = ""
        sub = tr.get("subscription")
        if sub:
            out += '<b class="tp">연 %s</b><small>%s</small>' % (esc(sub["price"]), esc(sub.get("priceUS") or ""))
        out += '<b class="tp%s">평생 %s</b><small>%s</small>' % (" tl" if sub else "", esc(tr["price"]), esc(tr.get("priceUS") or ""))
        return out

    def val(v):
        v = (v or "").strip()
        if v in ("✓", "O", "o"):
            return '<td class="ok">✓</td>'
        if v in ("", "–", "-", "—", "✗", "X"):
            return '<td class="no">–</td>'
        if v == "무제한":
            return '<td class="inf" aria-label="무제한">∞</td>'
        return "<td>%s</td>" % esc(public_text(v))

    head = "".join('<th class="tc-%s"><span class="tn">%s</span>%s<em>%s</em></th>'
                   % (esc(tr.get("id") or ""), esc(tr.get("label") or ""), price_cell(tr), esc(public_text(tr.get("pitch") or "")))
                   for tr in trims)
    body = "".join("<tr><th>%s</th>%s</tr>" % (esc(public_text(r.get("feature"))),
                                                "".join(val(r.get(tr.get("id"))) for tr in trims))
                   for r in p.get("compare") or [])
    extra = [x for x in [
        p.get("upgrade") and "Plus → Pro 올리기 %s" % with_us(p["upgrade"], p.get("upgradeUS")),
        p.get("graduate") and "구독 졸업 %s" % with_us(p["graduate"], p.get("graduateUS")),
        fp_price and "언제나 평생 패스 %s" % fp_price] if x]
    return ('<div class="ttw"><table class="tt"><thead><tr><th></th>%s</tr></thead><tbody>%s</tbody></table></div>%s'
            % (head, body, '<p class="tx">%s</p>' % esc(" · ".join(extra)) if extra else ""))


def paywall_plans_section(apps):
    data = load_paywall_plans()
    plans = data.get("apps") or {}
    if not plans:
        return ""
    by = {a["_slug"]: a for a in live(apps)}
    p1 = sorted((s for s, p in plans.items() if p.get("priority")), key=lambda s: plans[s]["priority"])
    fp = data.get("foreverPass") or {}
    fp_y, fp_l = fp.get("yearly") or {}, fp.get("lifetime") or {}
    fp_price = "연 %s · 평생 %s" % (with_us(fp_y.get("price"), fp_y.get("priceUS")), with_us(fp_l.get("price"), fp_l.get("priceUS")))

    rules = "".join('<div><h4>%s</h4><p>%s</p></div>' % (esc(h), esc(b)) for h, b in [
        ("무료 · Plus · Pro", "모든 앱은 무료로 받는다. 무료로 핵심을 한 번 끝까지 겪고, Plus 는 더 많이 · 내 취향대로, Pro 는 지키고 · 넓히고 · 자동으로."),
        ("연 구독 + 평생", "유료 칸마다 연 구독과 평생을 나란히 둔다. 평생은 연 구독의 3배 이상. 처음 보는 사람에게는 연 구독 첫 해 반값."),
        ("구독 졸업", "연 구독을 쓰던 사람에게 6개월째와 갱신 7일 전에 평생을 약 30% 깎은 값으로 권한다. 설정에는 늘 '평생으로 바꾸기'."),
        ("언제나 평생 패스", "한 번 사면 모든 앱의 Plus · Pro 평생과 앞으로 나올 앱까지. %s." % fp_price),
    ])
    ladder = ('<div class="tw"><table class="pt"><thead><tr><th>앱 크기</th><th>Plus 연 / 평생</th><th>Pro 연 / 평생</th>'
              '<th>미국 Plus</th><th>미국 Pro</th></tr></thead><tbody>'
              '<tr><th>S</th><td>₩2,200 / ₩6,600</td><td>₩4,400 / ₩13,000</td><td>$1.49 / $4.49</td><td>$2.99 / $8.99</td></tr>'
              '<tr><th>M</th><td>₩4,400 / ₩14,000</td><td>₩8,800 / ₩27,000</td><td>$2.99 / $8.99</td><td>$5.99 / $17.99</td></tr>'
              '<tr><th>L</th><td>₩6,600 / ₩20,000</td><td>₩13,000 / ₩39,000</td><td>$4.99 / $14.99</td><td>$8.99 / $26.99</td></tr>'
              '</tbody></table></div>')

    def card(s):
        p, a = plans[s], by.get(s)
        if not a:
            return ""
        trims = trim_table(p, fp_price if fp else "")
        moments = "".join('<li><b>%s</b><small>%s</small><span>%s</span><em>%s</em></li>'
                          % (esc(m["when"]), esc(m.get("see") or ""), esc(m["why"]), esc(m["plan"]))
                          for m in p.get("moments") or [])
        tag = ("1순위 %d · %s" % (p["priority"], p.get("stage") or "예정")) if p.get("priority") else "%s · %s" % (
            p.get("size") or "", PLAN_VERDICT.get(p.get("verdict"), ("",))[0])
        return ('<article class="pw np" style="--c:%s"><div class="top"><div class="app">%s%s<em>%s</em></div>'
                  '<h3>%s</h3><p class="sub">지금: %s</p></div>%s'
                  '<div class="why"><h4>왜 바꾸나</h4><p>%s</p></div>'
                  '<div class="moments"><h4>결제하고 싶어지는 순간</h4><ul>%s</ul></div>%s</article>'
                  % (PLAN_VERDICT.get(p.get("verdict"), ("", "#8b90a0"))[1], icon_img(a), esc(a["name"]), esc(tag),
                     esc(p.get("oneLine") or p.get("headline") or a["name"]), esc(p.get("currentPublic") or ""), trims,
                     esc(public_text(p.get("intent") or p.get("priorityReason") or p.get("verdictReason"))), moments,
                     donation_block(s)))

    order = {"new": 0, "adjust": 1, "keep": 2}
    cards = "".join(card(s) for s in p1)
    mr = maturity_rank(apps)
    rest = sorted((s for s, p in plans.items() if not p.get("priority") and p.get("oneLine") and s in by),
                  key=lambda s: mr(by[s]))
    rest_cards = "".join(card(s) for s in rest)

    rows, old = "", False
    for s in sorted(plans, key=lambda s: (plans[s].get("priority") or 99, not plans[s].get("oneLine"),
                                          mr(by[s]) if s in by else (999, ""))):
        p, a = plans[s], by.get(s)
        if not a:
            continue
        lbl, col = PLAN_VERDICT.get(p.get("verdict"), ("", "#8b90a0"))
        if not p.get("priority") and not p.get("oneLine") and not old:
            old = True
            rows += ('<tr class="grp"><th colspan="6">여기부터는 옛 규칙(평생만 · 옛 사다리)으로 낸 판단입니다. '
                     '새 규칙으로 다시 계산하기 전이라 이유에 적힌 가격 · 구독 판단은 바뀝니다.</th></tr>')
        rows += ('<tr><th><a href="%s">%s<span>%s</span></a></th><td class="k"><span class="vd" style="--c:%s">%s</span></td>'
                 '<td class="k">%s</td><td class="k">%s칸</td><td class="k">%s</td><td class="r">%s</td></tr>'
                 % (intro_link(a), icon_img(a), esc(a["name"]), col, esc(lbl), esc(p.get("size") or ""),
                    len(p.get("trims") or []), donation_short(s), esc(public_text(p.get("verdictReason")))))
    counts = {k: sum(1 for p in plans.values() if p.get("verdict") == k) for k in PLAN_VERDICT}
    return (
        '<section id="next"><h2>다음 페이월 · 설계안<span class="hc">%d</span></h2>'
        '<p class="lead">모든 앱을 무료 다운로드 + 무료 · Plus · Pro 로 바꾸는 설계입니다. 2026-10-27 에 확정했고, '
        '먼저 바꿀 다섯 앱부터 반영합니다(클립키보드부터). 괄호 안은 미국 가격입니다. 새로 설계 %d · 고칠 것 %d · 지금도 충분 %d.</p>'
        '<div class="rules">%s</div>'
        '<h3 class="sh">가격 사다리</h3>%s'
        '<p class="note">클립키보드는 L, 두번알림 · 욕망의 무지개 · 무지개 공방은 M 입니다. 골드위크는 지금 연 구독 가격'
        '(Plus ₩17,000 · Pro ₩33,000)이 매출이 나는 값이라 그대로 두고, 평생만 연 구독의 3배로 맞췄습니다. '
        '나머지 앱도 같은 사다리에서 앱 가치와 쓰는 빈도로 크기를 골랐습니다. 이미 산 사람, 구독 중인 사람의 권한은 그대로 둡니다.</p>'
        '<h3 class="sh">먼저 바꿀 다섯 앱</h3><div class="pws npws">%s</div>%s'
        '<h3 class="sh">앱별 판단</h3><div class="tw"><table class="pt pl"><thead><tr><th>앱</th><th>판단</th><th>크기</th>'
        '<th>칸</th><th>후원</th><th style="text-align:left">이유</th></tr></thead><tbody>%s</tbody></table></div></section>'
        % (len(plans), counts["new"], counts["adjust"], counts["keep"], rules, ladder, cards,
           ('<h3 class="sh">나머지 앱<span class="hc">%d</span></h3><p class="note">같은 규칙으로 앱마다 소스를 읽고 설계했습니다. '
            '1순위 다섯 앱을 낸 뒤 숫자를 보고 차례로 반영합니다.</p><div class="pws npws">%s</div>' % (len(rest), rest_cards))
           if rest else "", rows))


# ── 페이월 탭: 기능 한눈에 ─────────────────────────────────────────
# 앱 × 페이월 기능 한 표. 값은 앱 소스를 잰 serviceMaturity.money(sync-service-maturity.py),
# 평생 · 구독 상품은 페이월 정리(scripts/paywalls.json), 후원은 scripts/donations.json, 설계안은 paywall-plans.json.
PW_FEATURES = [
    # (키, 머리, 설명) — 값은 pw_feature(app, 키) 가 True/False/None 으로 준다
    ("paywall", "페이월", "무엇이 무료이고 무엇을 돈 내고 여는지 보여 주는 결제 화면"),
    ("tiers", "등급", "Plus · Pro 처럼 유료 칸이 둘 이상"),
    ("freeGate", "무료 문턱", "무료로 몇 번 써 본 뒤에 결제를 권한다"),
    ("subscription", "구독", "연 · 월 구독 상품을 판다"),
    ("lifetime", "평생", "한 번 사면 계속 쓰는 상품을 판다"),
    ("trial", "무료 체험", "구독 첫 기간을 무료나 할인으로 준다"),
    ("discount", "할인 제안", "할인 코드 · 되돌아온 사람 할인 · 프로모션"),
    ("graduation", "구독 졸업", "구독하던 사람에게 평생을 깎아 권한다"),
    ("foreverPass", "언제나 패스", "모든 앱 평생 패스를 앱 안에서 보여 준다"),
    ("restore", "구매 복원", "기기를 바꿔도 산 것을 되찾는다"),
    ("gift", "선물", "다른 사람에게 이용권을 선물한다"),
    ("tipJar", "후원", "기능을 열지 않는 응원(팁)"),
    ("tipAsk", "후원 부탁", "잘 쓴 순간에 드물게 응원을 부탁한다"),
    ("thanks", "고마운 사람들", "팁 화면에서 소개 페이지에 이름을 올리게 한다"),
]


def pw_feature(app, key, pws, dons):
    money = mat(app).get("money") or {}
    if not mat(app).get("source"):
        return None
    tiers = [t for t in (pws.get(app["_slug"]) or {}).get("tiers") or [] if t.get("live")]
    if key == "lifetime":
        return any(t.get("period") == "평생" for t in tiers)
    if key == "subscription":
        return bool(money.get("subscription")) or any(t.get("period") in ("주", "월", "연") for t in tiers)
    if key == "tipJar":
        d = dons.get(app["_slug"])
        return bool(d and d.get("status") == "live") or bool(money.get("tipJar"))
    if key == "thanks":
        return bool((dons.get(app["_slug"]) or {}).get("thanksButton"))
    return money.get(key)


def paywall_features_section(apps):
    pws = load_paywalls()
    dons = load_donations().get("apps") or {}
    plans = load_paywall_plans().get("apps") or {}
    ls = sorted(live(apps), key=maturity_rank(apps))
    vals = {a["_slug"]: {k: pw_feature(a, k, pws, dons) for k, _, _ in PW_FEATURES} for a in ls}
    known = [a for a in ls if mat(a).get("source")]

    head = "".join('<th title="%s"><span>%s</span><i>%d</i></th>' % (
        esc(why), esc(name), sum(1 for a in known if vals[a["_slug"]][k])) for k, name, why in PW_FEATURES)

    def cell(v):
        if v is None:
            return '<td class="u">?</td>'
        return '<td class="y">✓</td>' if v else '<td class="n">·</td>'

    rows = ""
    for a in ls:
        p = plans.get(a["_slug"]) or {}
        lbl, col = PLAN_VERDICT.get(p.get("verdict"), ("—", "#8b90a0"))
        got = sum(1 for v in vals[a["_slug"]].values() if v)
        rows += ('<tr><th><a href="%s">%s<span>%s</span></a></th><td class="m">%s</td>%s<td class="c">%d</td>'
                 '<td class="k"><span class="vd" style="--c:%s">%s</span></td><td class="k">%s</td></tr>'
                 % (intro_link(a), icon_img(a), esc(a["name"]), esc(model_of(a)[1]),
                    "".join(cell(vals[a["_slug"]][k]) for k, _, _ in PW_FEATURES), got, col, esc(lbl),
                    esc(("1순위 %d" % p["priority"]) if p.get("priority") else (p.get("size") or ""))))
    return (
        '<section id="features"><h2>페이월 기능 한눈에<span class="hc">%d</span></h2>'
        '<p class="lead">앱마다 결제 · 후원 기능을 무엇까지 갖췄는지 한 표에 모았습니다. 앱 소스를 직접 읽어 판정했고(%s 기준), '
        '서비스 숙성도 순서로 늘어놓았습니다. 머리의 숫자는 그 기능을 갖춘 앱 수입니다.</p>'
        '<p class="note">✓ 있음 · · 없음 · ? 소스를 찾지 못함. 머리에 마우스를 올리면 무엇을 보는지 나옵니다. '
        '오른쪽 두 칸은 다음 페이월 설계안의 판단입니다.</p>'
        '<div class="tw ftw"><table class="ft"><thead><tr><th>앱</th><th class="m">지금 방식</th>%s'
        '<th class="c">갖춘 수</th><th>설계안</th><th>크기</th></tr></thead><tbody>%s</tbody></table></div></section>'
        % (len(ls), esc(max((mat(a).get("evaluatedAt") or "") for a in ls)), head, rows))


# ── 페이월 탭: 후원 ───────────────────────────────────────────────
# scripts/donations.json 을 읽는다. 여기 없는 앱은 후원 상품이 없다. 상품 ID 는 내보내지 않는다.
DONATION_STATUS = {"live": ("받는 중", "#34c48a"), "code-only": ("코드만", "#e0a53a")}


def load_donations():
    path = os.path.join(ROOT, "scripts", "donations.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def donation_text(slug):
    """카드에 넣을 한 줄 — 상품과 가격, 없으면 '후원 없음'."""
    d = (load_donations().get("apps") or {}).get(slug)
    if not d:
        return "후원 없음"
    if d.get("status") != "live":
        return d.get("gives") or "코드만 있고 사용자에게 보이지 않음"
    items = " · ".join(" ".join(x for x in (p["label"], p.get("price") or p.get("usd")) if x) for p in d.get("products") or [])
    return "%s — %s" % (items, " · ".join(d.get("where") or [])) if d.get("where") else items


def donation_block(slug):
    d = (load_donations().get("apps") or {}).get(slug)
    lbl, col = DONATION_STATUS.get((d or {}).get("status"), ("없음", "#8b90a0"))
    return ('<div class="why don"><h4>후원 <span class="vd" style="--c:%s">%s</span></h4><p>%s</p></div>'
            % (col, esc(lbl), esc(donation_text(slug) if d else "앱 안에서 후원을 받지 않습니다")))


def donation_short(slug):
    d = (load_donations().get("apps") or {}).get(slug)
    lbl, col = DONATION_STATUS.get((d or {}).get("status"), ("없음", "#8b90a0"))
    return '<a class="vd" href="#tips" style="--c:%s;text-decoration:none">%s</a>' % (col, esc(lbl))


def donations_section(apps):
    data = load_donations()
    dons = data.get("apps") or {}
    ls = sorted(live(apps), key=maturity_rank(apps))
    has = [a for a in ls if a["_slug"] in dons]
    has.sort(key=lambda a: list(DONATION_STATUS).index(dons[a["_slug"]].get("status", "live")))
    none = [a for a in ls if a["_slug"] not in dons]

    def product_cell(d):
        out = []
        for p in d.get("products") or []:
            price = " · ".join(x for x in [p.get("price"), p.get("usd")] if x) or "가격 미정"
            out.append("<b>%s</b> %s%s" % (esc(p["label"]), esc(price),
                                           "" if p.get("inStore") else " <small>스토어 목록에 안 보임</small>"))
        return "<br>".join(out) or '<span class="na">—</span>'

    rows = ""
    for a in has:
        d = dons[a["_slug"]]
        lbl, col = DONATION_STATUS.get(d.get("status"), ("", "#8b90a0"))
        rows += ('<tr><th><a href="%s">%s<span>%s</span></a></th><td class="k"><span class="vd" style="--c:%s">%s</span></td>'
                 '<td class="r">%s</td><td class="r">%s</td><td class="r">%s</td><td class="r">%s</td></tr>'
                 % (intro_link(a), icon_img(a), esc(a["name"]), col, esc(lbl), product_cell(d),
                    "<br>".join(esc(w) for w in d.get("where") or []) or '<span class="na">—</span>',
                    (esc(d["ask"]) + ("<small>%s</small>" % esc(d["cadence"]) if d.get("cadence") else ""))
                    if d.get("ask") else '<span class="na">—</span>',
                    esc(d.get("gives") or "")))
    live_n = sum(1 for a in has if dons[a["_slug"]].get("status") == "live")
    chips_none = '<div class="lnames">%s</div>' % "".join(
        '<a href="%s" style="--c:#8b90a0">%s%s</a>' % (intro_link(a), icon_img(a), esc(a["name"])) for a in none)
    return (
        '<section id="tips"><h2>후원<span class="hc">%d</span></h2>'
        '<p class="lead">앱 %d개 가운데 %d개가 앱 안에서 후원을 받고 있습니다. 후원은 기능을 열지 않고, '
        '이미 다 가진 사람이 더 내고 싶을 때 갈 곳입니다. 상품과 부탁하는 순간은 앱 소스에서 읽었습니다(%s 기준).</p>'
        '<div class="tw"><table class="pt pl dn"><thead><tr><th>앱</th><th>상태</th><th style="text-align:left">상품 · 가격</th>'
        '<th style="text-align:left">어디서</th><th style="text-align:left">응원 부탁</th><th style="text-align:left">받으면</th>'
        '</tr></thead><tbody>%s</tbody></table></div>'
        '<p class="note">스토어 목록에 안 보이는 상품은 App Store 앱 페이지의 인앱 구입 목록에 아직 없다는 뜻입니다. '
        '등록 전이거나 목록에서 밀렸을 수 있으니 App Store Connect 에서 확인합니다.</p>'
        '<h3 class="sh">후원 없음<span class="hc">%d</span></h3>%s%s</section>'
        % (len(has), len(ls), live_n, esc(data.get("checkedAt") or ""), rows, len(none), chips_none,
           donation_reward_plan(data.get("rewardPlan"))))


def donation_reward_plan(rp):
    """후원 보상 설계안 — 원칙 · 단계 · 지금 후원자 · 도입 순서 · 정할 것."""
    if not rp:
        return ""
    rules = "".join('<div><h4>%s</h4><p>%s</p></div>' % (esc(h), esc(b)) for h, b in rp.get("rules") or [])
    tiers = "".join('<div><h4>%s</h4><p class="nd">%s</p><ul>%s</ul></div>'
                    % (esc(t["name"]), esc(t["need"]), "".join("<li>%s</li>" % esc(g) for g in t["gets"]))
                    for t in rp.get("tiers") or [])
    existing = "".join('<tr><th>%s</th><td class="r">%s</td></tr>' % (esc(a), esc(b)) for a, b in rp.get("existing") or [])
    steps = "".join("<li>%s</li>" % esc(x) for x in rp.get("rollout") or [])
    opens = "".join("<li>%s</li>" % esc(x) for x in rp.get("open") or [])
    decided = "".join("<li><b>%s</b> %s</li>" % (esc(d), esc(x)) for d, x in rp.get("decided") or [])
    return (
        '<h3 class="sh" id="tip-rewards">후원 보상 설계안 <span class="vd" style="--c:#e0a53a">%s</span></h3>'
        '<p class="note">후원한 사람에게 무엇을 돌려줄지 정한 설계입니다. 기능은 열지 않고, 알아봐 주고 · 꾸밈 하나를 주고 · 먼저 들려줍니다.</p>'
        '<div class="rules">%s</div>'
        '<h3 class="sh">단계</h3><p class="note">%s</p><div class="rules tiers3">%s</div>'
        '<h3 class="sh">지금 후원한 사람들</h3><div class="tw"><table class="pt pl dn"><tbody>%s</tbody></table></div>'
        '<h3 class="sh">도입 순서</h3><ol class="steps">%s</ol>'
        '%s<h3 class="sh">정할 것</h3><ul class="steps">%s</ul>'
        % (esc(rp.get("status") or ""), rules, esc(rp.get("points") or ""), tiers, existing, steps,
           '<h3 class="sh">정한 것</h3><ul class="steps">%s</ul>' % decided if decided else "", opens))


def paywalls_page(apps):
    ls = [a for a in live(apps) if (a.get("price") or {}).get("evaluatedAt")]
    pws = load_paywalls()

    def has_paywall(a):
        pw = pws.get(a["_slug"]) or {}
        return pw.get("kind") not in (None, "none") and (pw.get("headline") or pw.get("benefits") or pw.get("locked"))

    def selling(a):
        return (a.get("price") or {}).get("hasInAppPurchases") and not pws[a["_slug"]].get("hidden")

    key = maturity_rank(apps)
    live_pw = sorted([a for a in ls if has_paywall(a) and selling(a)], key=key)
    prep_pw = sorted([a for a in ls if has_paywall(a) and not selling(a)], key=key)

    lifetimes = sorted(krw(t.get("price")) for a in live_pw for t in pws[a["_slug"]].get("tiers") or []
                       if t.get("live") and t.get("period") == "평생" and krw(t.get("price")))
    subs = sum(1 for a in live_pw if any(t.get("live") and t.get("period") in ("주", "월", "연")
                                          for t in pws[a["_slug"]].get("tiers") or []))
    mid = lifetimes[len(lifetimes) // 2] if lifetimes else 0

    head = ('<div class="eyebrow">Paywalls</div><h1>페이월 모음</h1>'
            '<p>앱 %d개가 앱 안에서 결제를 권하는 화면을 한자리에 모았습니다. 가격은 App Store 실데이터, '
            '문구와 무료 몫은 앱 소스에서 읽었습니다. 앱은 모든 목록에서 서비스 숙성도 순서(갖춘 것이 많은 앱부터)로 늘어놓았습니다.</p>' % (len(live_pw) + len(prep_pw)))
    kp = '<div class="kp">%s%s</div>' % ("".join(
        '<div><b>%s</b><span>%s</span></div>' % (v, esc(k)) for k, v in [
            ("판매 중인 페이월", len(live_pw)), ("준비 중인 페이월", len(prep_pw)),
            ("구독 상품이 있는 앱", subs),
            ("평생 이용권 가격 중앙값", "￦{:,}".format(mid) if mid else "—"),
            ("평생 이용권 가격 폭", "￦{:,} ~ ￦{:,}".format(lifetimes[0], lifetimes[-1]) if lifetimes else "—")]),
        '<a class="kpl" href="#tips"><b>%d</b><span>후원 받는 앱 ↓</span></a>' % sum(
            1 for d in (load_donations().get("apps") or {}).values() if d.get("status") == "live"))

    thead = "<tr><th>앱</th><th>방식</th><th>앱 가격</th>%s<th>기간끼리 견주면</th></tr>" % "".join(
        "<th>%s</th>" % esc(t) for _, t in PERIODS)
    body = "".join(ladder_row(a, pws[a["_slug"]]) for a in live_pw)
    if prep_pw:
        body += '<tr class="grp"><th colspan="%d">준비 중 — 결제 화면은 있지만 아직 판매를 열지 않음</th></tr>' % (len(PERIODS) + 4)
        body += "".join(ladder_row(a, pws[a["_slug"]]) for a in prep_pw)
    table = '<div class="tw"><table class="pt"><thead>%s</thead><tbody>%s</tbody></table></div>' % (thead, body)

    main = (
        '<section>%s</section>%s%s%s'
        '<section><h2>가격 비교표</h2><p class="lead">기간별로 무엇을 얼마에 파는지 나란히 놓았습니다. '
        '한 기간에 상품이 여럿이면 대표 하나와 나머지 개수를 적었습니다. 오른쪽 칸은 같은 앱 안에서 '
        '긴 기간 상품이 짧은 기간의 몇 배인지 보여 줍니다. 괄호 안은 미국 App Store 가격입니다.</p>%s'
        '<p class="note">달러만 적힌 가격은 앱 코드에 적힌 값이라 스토어 실가격과 다를 수 있습니다. '
        '괄호가 없는 원화 가격은 미국 스토어에서 같은 상품을 찾지 못한 것입니다.</p></section>'
        '<section><h2>판매 중인 페이월<span class="hc">%d</span></h2><p class="lead">문구와 혜택, 무료로 주는 몫, '
        '화면이 뜨는 시점을 앱 소스에서 그대로 옮겼습니다.</p><div class="pws">%s</div></section>'
        '%s'
        % (kp, paywall_features_section(apps), donations_section(apps), paywall_plans_section(apps), table, len(live_pw), "".join(paywall_card(a, pws[a["_slug"]]) for a in live_pw),
           ('<section><h2>준비 중인 페이월<span class="hc">%d</span></h2><p class="lead">결제 화면은 만들어 두었지만 '
            '아직 판매를 열지 않은 앱입니다.</p><div class="pws">%s</div></section>'
            % (len(prep_pw), "".join(paywall_card(a, pws[a["_slug"]]) for a in prep_pw))) if prep_pw else ""))
    return page("페이월 모음 — 리이오의 앱 포트폴리오",
                "앱 %d개의 페이월과 가격 사다리를 모아 앱끼리 가격을 비교합니다." % (len(live_pw) + len(prep_pw)),
                {"head": head, "main": main}, "pw", PW_CSS)


# ── 공개: 범주 · 언어 · 확산 ────────────────────────────────────────
# scripts/category-design.json 을 읽는다. 앱마다 다섯 관점(범주 설계 · 제품보다 언어 · 참조점 · 캐즘 · 행동 변화 비용)
# 과, 관점마다 "이걸로 내리는 결정" 의 답을 보여 준다. 근거 파일 경로(sources)는 내보내지 않는다.
CAT_LENSES = [
    ("cat", "범주 설계", "Category Design · Play Bigger",
     "제품을 파는 게 아니라, 그 제품이 답이 되는 질문을 먼저 심는다. 문제에 이름을 붙이고(범주명), 왜 지금인지 말하고(전환 서사), 이 앱이 기준점이라는 증거를 쌓는다.",
     "랜딩 첫 문장을 '무엇을 하는 도구' 로 쓸지 '어떤 문제가 있다' 로 쓸지. 새 범주라면 후자.",
     "혼자서 시장 인식을 통째로 바꿀 수는 없다. 좁은 교두보 안에서만 통하는 범주를 만든다."),
    ("lang", "제품보다 언어", "Language before product",
     "부를 이름이 없는 것은 인식되지도 추천되지도 않는다. 입소문은 이름을 타고 흐른다.",
     "다음 작업 시간을 기능 개발에 쓸지, 이름과 설명문 수정에 쓸지.",
     "멋진 이름과 이해되는 이름은 다르다. 조어는 검색 유입이 0이다. 이미 검색되는 단어에 새 수식어를 붙인다."),
    ("ref", "참조점", "Reference point · analogy",
     "'OO 같은데 XX한 것' 으로 설명되지 않으면 이해 비용을 사용자에게 떠넘긴다. 참조점은 문이지 집이 아니다.",
     "첫 화면 카피에 비유를 쓸 것인가. 쓰되 두 번째 화면부터 자기 언어로 갈아탄다.",
     "참조 대상보다 명백히 나은 점이 한 줄로 안 나오면 '그것의 열등한 버전' 으로 고정된다. 그때는 쓰지 않는다."),
    ("chasm", "확산과 캐즘", "Diffusion of Innovations · Crossing the Chasm",
     "초기 수용자는 새로움을 사고, 다수는 남들이 이미 쓴다는 증거를 산다. 그 사이의 단절은 새 범주일수록 깊다.",
     "성장이 멈췄을 때 제품을 고칠지, 사례와 증거를 만들지.",
     "초기 수용자의 요구를 그대로 받으면 다수가 못 쓰는 제품이 된다. 그들은 불편을 신고하지 않는다."),
    ("switch", "행동 변화 비용", "Behavior change cost · 9x effect",
     "경쟁 상대는 다른 제품이 아니라 지금의 습관이다. 조금 나은 정도로는 아무도 옮겨 오지 않는다.",
     "다음에 만들 것이 '새 기능' 인지 '이사 도구' 인지.",
     "습관이 아예 없는 영역은 전환 비용이 낮지만 수요 자체가 없을 확률이 높다."),
]
CAT_KIND = {"new": ("새 범주", "#34c48a"), "niche": ("뾰족한 하위 범주", "#5b8def"), "existing": ("기존 범주", "#8b90a0")}
CAT_BADGE = {
    "landing": {"problem": ("문제형 첫 문장", "#34c48a"), "tool": ("도구형 첫 문장", "#8b90a0")},
    "lang": {"naming": ("이름 · 설명문 먼저", "#e0a53a"), "features": ("기능 먼저", "#8b90a0")},
    "ref": {True: ("비유 쓰기", "#5b8def"), False: ("비유 안 씀", "#8b90a0")},
    "chasm": {"proof": ("사례 · 증거 먼저", "#e0a53a"), "product": ("제품 먼저", "#8b90a0")},
    "switch": {"moving-tool": ("이사 도구 먼저", "#e0a53a"), "feature": ("새 기능 먼저", "#8b90a0")},
}
CAT_STAGE = {"early": "초기 수용자", "stalled": "성장 멈춤", "crossing": "다수로 넘어가는 중", "unknown": "자료 없음"}
CAT_NAME = {"plain": "검색되는 일반어", "coined": "조어", "combo": "검색어 + 수식어"}
CAT_HABIT = {"strong": "강한 습관", "weak": "약한 습관", "none": "습관 없음"}


def load_category():
    path = os.path.join(ROOT, "scripts", "category-design.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh).get("apps") or {}


def cat_badge(group, key):
    lbl, col = CAT_BADGE[group].get(key, ("—", "#8b90a0"))
    return '<span class="cb" style="--c:%s">%s</span>' % (col, esc(lbl))


def cat_list(items):
    items = [x for x in (items or []) if x]
    return "<ul>%s</ul>" % "".join("<li>%s</li>" % esc(public_text(x)) for x in items) if items else '<p class="na">없음</p>'


def category_card(app, c):
    kind_lbl, kind_col = CAT_KIND.get(c.get("kind"), ("—", "#8b90a0"))
    cat, lang, ref, ch, sw, ld = (c.get("category") or {}), (c.get("language") or {}), (c.get("reference") or {}), \
        (c.get("chasm") or {}), (c.get("switching") or {}), (c.get("landing") or {})
    t = public_text

    def lens(key, title, decision, body):
        return '<section class="ln ln-%s"><h4>%s %s</h4>%s</section>' % (key, esc(title), decision, body)

    body = (
        lens("cat", "범주 설계", cat_badge("landing", ld.get("type")),
             '<p class="q">%s</p><dl><dt>교두보</dt><dd>%s</dd><dt>지금 버티는 방식</dt><dd>%s</dd>'
             '<dt>왜 지금</dt><dd>%s</dd><dt>기준점이라는 증거</dt><dd>%s</dd><dt>만들어야 할 증거</dt><dd>%s</dd>'
             '<dt>랜딩 첫 문장</dt><dd><s>%s</s><b>%s</b></dd></dl>'
             % (esc(cat.get("question")), esc(t(c.get("beachhead"))), esc(t(c.get("oldWay"))), esc(t(c.get("shift"))),
                cat_list(c.get("evidence")), cat_list(c.get("evidenceToBuild")),
                esc(ld.get("current") or "찾지 못함"), esc(ld.get("proposed")))) +
        lens("lang", "제품보다 언어", cat_badge("lang", lang.get("decision")),
             '<dl><dt>써 본 사람의 한마디 (추정)</dt><dd>"%s" <span class="na">· %s</span></dd>'
             '<dt>이름</dt><dd>%s · %s</dd><dt>이미 검색되는 말</dt><dd>%s</dd>'
             '<dt>제안 표현</dt><dd><b>%s</b></dd><dt>왜</dt><dd>%s</dd></dl>'
             % (esc(t(lang.get("wordOfMouth")).replace(" (추정)", "")),
                "사람마다 같은 말로 설명할 것" if lang.get("wordOfMouthSpread") == "consistent" else "사람마다 다른 말로 설명할 것",
                esc(CAT_NAME.get(lang.get("nameType"), "")), esc(t(lang.get("nameNote"))),
                esc(" · ".join(lang.get("searchTerms") or [])), esc(lang.get("proposedPhrase")), esc(t(lang.get("decisionReason"))))) +
        lens("ref", "참조점", cat_badge("ref", bool(ref.get("useAnalogy"))),
             '<p class="q">%s</p><dl><dt>참조점</dt><dd>%s</dd><dt>더 나은 한 줄</dt><dd>%s</dd>'
             '<dt>끌고 오는 기대치</dt><dd>%s</dd><dt>두 번째 화면부터</dt><dd>%s</dd></dl>'
             % (esc(ref.get("analogy")), esc(ref.get("anchor")), esc(t(ref.get("betterLine")) or "없음"),
                esc(t(ref.get("risk"))), esc(t(ref.get("secondScreen"))))) +
        lens("chasm", "확산과 캐즘", cat_badge("chasm", ch.get("decision")),
             '<dl><dt>지금 어디</dt><dd>%s · %s</dd><dt>초기 수용자</dt><dd>%s</dd><dt>다수가 원하는 증거</dt><dd>%s</dd>'
             '<dt>성공 사례를 만들 좁은 집단</dt><dd><b>%s</b></dd><dt>왜</dt><dd>%s</dd>%s</dl>'
             % (esc(CAT_STAGE.get(ch.get("stage"), "")), esc(t(ch.get("stageReason"))), esc(t(ch.get("earlyAdopters"))),
                esc(t(ch.get("majorityProof"))), esc(t(ch.get("referenceCase"))), esc(t(ch.get("decisionReason"))),
                '<dt>받지 말 요구</dt><dd>%s</dd>' % esc(t(ch["earlyAdopterTrap"])) if ch.get("earlyAdopterTrap") else "")) +
        lens("switch", "행동 변화 비용", cat_badge("switch", sw.get("decision")),
             '<dl><dt>싸우는 습관</dt><dd>%s <span class="na">· %s</span></dd><dt>습관보다 나은 점</dt><dd>%s</dd>'
             '<dt>옮겨 오는 비용</dt><dd>%s</dd><dt>있는 이사 도구</dt><dd>%s</dd><dt>만들 이사 도구</dt><dd>%s</dd>'
             '<dt>왜</dt><dd>%s</dd>%s</dl>'
             % (esc(t(sw.get("habit"))), esc(CAT_HABIT.get(sw.get("habitStrength"), "")), esc(t(sw.get("gain"))),
                cat_list(sw.get("switchCosts")), cat_list(sw.get("movingToolsHave")), cat_list(sw.get("movingToolsNeed")),
                esc(t(sw.get("decisionReason"))),
                '<dt>주의</dt><dd>%s</dd>' % esc(t(sw["noHabitWarning"])) if sw.get("noHabitWarning") else "")))
    summary = ('<summary>%s<span class="nm"><b>%s</b><em>%s</em></span><span class="kd" style="--c:%s">%s</span>'
               '<span class="cn">%s</span><span class="bd">%s%s%s%s%s</span></summary>'
               % (icon_img(app), esc(app["name"]), esc(t(lang.get("proposedPhrase") or "")), kind_col, esc(kind_lbl),
                  esc(cat.get("name")), cat_badge("landing", ld.get("type")), cat_badge("lang", lang.get("decision")),
                  cat_badge("ref", bool(ref.get("useAnalogy"))), cat_badge("chasm", ch.get("decision")),
                  cat_badge("switch", sw.get("decision"))))
    return '<details class="cd" id="cd-%s">%s<p class="kr">%s</p><div class="lns">%s</div></details>' % (
        esc(app["_slug"]), summary, esc(t(c.get("kindReason"))), body)


CAT_CSS = BIZ_CSS + """
  .lenses{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin:14px 0 6px}
  .lenses>div{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:13px 15px}
  .lenses h3{font-size:.95rem;margin:0}
  .lenses small{display:block;color:var(--muted);font-size:.7rem;margin:2px 0 8px}
  .lenses p{margin:0 0 6px;font-size:.82rem;line-height:1.55}
  .lenses p.d b,.lenses p.t b{font-size:.72rem;color:var(--muted);display:block}
  .cb{display:inline-block;font-size:.68rem;font-weight:800;color:var(--c);border:1px solid var(--c);border-radius:999px;
    padding:1px 8px;white-space:nowrap;margin-left:4px}
  .cd{background:var(--card);border:1px solid var(--border);border-radius:13px;margin-bottom:8px}
  .cd summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:30px minmax(0,200px) auto minmax(0,1fr);
    gap:6px 12px;align-items:center;padding:12px 14px}
  .cd summary::-webkit-details-marker{display:none}
  .cd summary .ic{width:30px;height:30px;border-radius:8px}
  .cd .nm b{display:block}.cd .nm em{font-style:normal;font-size:.74rem;color:var(--muted)}
  .cd .kd{font-size:.7rem;font-weight:800;color:var(--c);white-space:nowrap}
  .cd .cn{font-weight:700}
  .cd .bd{grid-column:2/-1;display:flex;flex-wrap:wrap;gap:4px}
  .cd .bd .cb{margin-left:0}
  .cd .kr{margin:0 14px 10px;color:var(--muted);font-size:.84rem;line-height:1.55}
  .cd .lns{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:10px;padding:0 14px 14px}
  .ln{border:1px solid var(--border);border-radius:11px;padding:12px 14px;background:var(--bg-soft)}
  .ln h4{margin:0 0 8px;font-size:.88rem;display:flex;flex-wrap:wrap;align-items:center;gap:4px}
  .ln .q{margin:0 0 8px;font-weight:700;line-height:1.5}
  .ln dl{margin:0;display:grid;gap:3px}
  .ln dt{font-size:.7rem;color:var(--muted);font-weight:800;margin-top:6px}
  .ln dd{margin:0;font-size:.84rem;line-height:1.55}
  .ln dd s{display:block;color:var(--muted);font-size:.8rem}
  .ln ul{margin:0;padding-left:1.1em}
  .ln .na{color:var(--muted)}
  .ctab{border-collapse:collapse;width:100%;font-size:.8rem;background:var(--card)}
  .ctab th,.ctab td{border-bottom:1px solid var(--border);padding:8px 10px;text-align:left;vertical-align:top}
  .ctab thead th{font-size:.7rem;color:var(--muted);font-weight:800}
  .ctab tbody th a{display:flex;align-items:center;gap:8px;color:var(--text);text-decoration:none;font-weight:600;white-space:nowrap}
  .ctab tbody th .ic{width:24px;height:24px;border-radius:6px}
  .ctab td .cb{margin-left:0}
  @media (max-width:700px){.cd summary{grid-template-columns:30px minmax(0,1fr)}.cd .kd,.cd .cn{grid-column:2}}
"""


def category_page(apps):
    data = load_category()
    by = {a["_slug"]: a for a in live(apps)}
    items = [(by[s], c) for s, c in data.items() if s in by]
    order = {"new": 0, "niche": 1, "existing": 2}
    items.sort(key=lambda x: (order.get(x[1].get("kind"), 9), x[0]["name"]))
    n = len(items)

    def cnt(f):
        return sum(1 for _, c in items if f(c))
    kp = '<div class="kp">%s</div>' % "".join('<div><b>%d</b><span>%s</span></div>' % (v, esc(k)) for k, v in [
        ("새 범주를 세울 수 있는 앱", cnt(lambda c: c.get("kind") == "new")),
        ("뾰족한 하위 범주", cnt(lambda c: c.get("kind") == "niche")),
        ("기존 범주에서 경쟁", cnt(lambda c: c.get("kind") == "existing")),
        ("이름 · 설명문부터 고칠 앱", cnt(lambda c: (c.get("language") or {}).get("decision") == "naming")),
        ("사례 · 증거가 먼저인 앱", cnt(lambda c: (c.get("chasm") or {}).get("decision") == "proof")),
        ("이사 도구가 먼저인 앱", cnt(lambda c: (c.get("switching") or {}).get("decision") == "moving-tool"))])
    lenses = '<div class="lenses">%s</div>' % "".join(
        '<div><h3>%s</h3><small>%s</small><p>%s</p><p class="d"><b>이걸로 내리는 결정</b>%s</p><p class="t"><b>함정</b>%s</p></div>'
        % (esc(ti), esc(en), esc(c), esc(d), esc(tr)) for _, ti, en, c, d, tr in CAT_LENSES)
    rows = "".join(
        '<tr><th><a href="#cd-%s">%s<span>%s</span></a></th><td><span class="cb" style="--c:%s">%s</span></td><td>%s</td>'
        '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
        % (esc(a["_slug"]), icon_img(a), esc(a["name"]), CAT_KIND.get(c.get("kind"), ("", "#8b90a0"))[1],
           esc(CAT_KIND.get(c.get("kind"), ("—",))[0]), esc((c.get("category") or {}).get("name")),
           cat_badge("landing", (c.get("landing") or {}).get("type")), cat_badge("lang", (c.get("language") or {}).get("decision")),
           cat_badge("ref", bool((c.get("reference") or {}).get("useAnalogy"))), cat_badge("chasm", (c.get("chasm") or {}).get("decision")),
           cat_badge("switch", (c.get("switching") or {}).get("decision")))
        for a, c in items)
    table = ('<div class="tw"><table class="ctab"><thead><tr><th>앱</th><th>범주</th><th>범주명</th><th>첫 문장</th>'
             '<th>다음 시간</th><th>비유</th><th>성장이 멈추면</th><th>다음에 만들 것</th></tr></thead><tbody>%s</tbody></table></div>' % rows)
    head = ('<div class="eyebrow">Positioning</div><h1>범주 · 언어 · 확산</h1>'
            '<p>앱 %d개를 다섯 관점으로 봤습니다. 무엇을 하는 앱인지보다 먼저, 어떤 문제의 답인지 · 사람들이 뭐라고 부를지 · '
            '무엇에 빗대어 들어오게 할지 · 누구의 성공 사례로 넘어갈지 · 어떤 습관과 싸우는지. '
            '관점마다 지금 내릴 결정을 앱별로 적었습니다.</p>' % n)
    main = ('<section>%s%s</section>'
            '<section><h2>한눈에</h2><p class="lead">앱마다 다섯 결정의 답입니다. 이름을 누르면 아래 자세한 칸으로 갑니다.</p>%s</section>'
            '<section><h2>앱별 자세히<span class="hc">%d</span></h2><p class="lead">새 범주 · 뾰족한 하위 범주 · 기존 범주 순입니다. '
            '증거는 앱에 실제로 있는 것만 적었고, 써 본 사람의 한마디는 스토어 문구와 이름으로 짐작한 것입니다.</p>%s</section>'
            % (kp, lenses, table, n, "".join(category_card(a, c) for a, c in items)))
    return page("범주 · 언어 · 확산 — 리이오의 앱 포트폴리오",
                "앱 %d개의 범주 설계 · 이름 · 참조점 · 캐즘 · 행동 변화 비용과 지금 내릴 결정." % n,
                {"head": head, "main": main}, "cat", CAT_CSS)


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
        '<a class="ov" href="%(site)slifecycle.html"><b>제품 여정</b><p>수명주기 5단계 × 글로벌 지원 공개판. '
        '재생성: <code>build-portfolio-hub.py</code></p></a>'
        '<a class="ov" href="%(site)smaturity.html"><b>서비스 숙성도</b><p>기능별 탭 공개판. '
        '재수집: <code>sync-service-maturity.py</code> → 재생성: <code>build-portfolio-hub.py</code></p></a>'
        '<a class="ov" href="%(site)shub.html"><b>페이지 모음</b><p>공개 허브(안전 버전). '
        '재생성: <code>build-portfolio-hub.py</code></p></a>'
        '</div></section>'
        '<section><h2>내부 판정</h2><div class="ovgrid">'
        '<a class="ov" href="%(site)sreddit-launch.html"><b>레딧 출격</b><p>영어권 유입을 받아도 되는 앱. '
        '재수집: <code>sync-us-store.py</code> → 재생성: <code>build-portfolio-hub.py</code></p></a>'
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


# ── 내부: 레딧 출격 ───────────────────────────────────────────────
# 영어권 커뮤니티로 사람을 데려와도 되는 앱인가. 데려온 사람이 보는 것은 미국 스토어라
# sync-us-store.py 가 남긴 usStore 와 sync-global-reach.py 의 globalReach 로 판정한다.
# 사용자 요청으로 docs/ 에 배포한다(2026-10-15). 찾아갈 수 있게 상단 메뉴와 페이지 모음에 건다.
REDDIT_GATES = [
    ("us", "미국 판매", "미국 스토어에 올리기"),
    ("store", "영어 소개", "미국 스토어 소개를 영어로"),
    ("app", "앱 영어", "앱에 영어 넣기"),
    ("free", "무료 다운로드", "무료 다운로드 + 인앱 구입으로 바꾸기"),
    ("iap", "인앱 구입", "인앱 구입(Pro) 붙이기"),
    ("iapen", "인앱 이름 영어", "인앱 구입 표시 이름을 영어로"),
]
REDDIT_VERDICT = [
    (0, "지금 올리기", "다섯 관문을 다 넘었습니다. 데려온 사람이 영어로 읽고, 무료로 받고, 결제까지 갑니다.", "#34c48a"),
    (1, "하나만 고치면", "한 가지만 고치면 올릴 수 있습니다. 고칠 것이 표 오른쪽에 있습니다.", "#e0a53a"),
    (2, "준비 더 필요", "두 가지 이상 빠졌습니다. 지금 사람을 데려오면 새어 나갑니다.", "#8b90a0"),
    (3, "이미 올림", "레딧에 올린 앱입니다. 빨간 칸이 남아 있으면 들어온 사람이 새는 자리입니다.", "#a78bfa"),
]


def reddit_posted(app):
    """레딧에 이미 올렸는가 — 앱 JSON marketing.reddit.posted (수동 기록)."""
    return bool(((app.get("marketing") or {}).get("reddit") or {}).get("posted"))


def reddit_url(app):
    """올린 레딧 글 주소 — 앱 JSON marketing.reddit.url (수동 기록)."""
    return ((app.get("marketing") or {}).get("reddit") or {}).get("url")


def reddit_gates(app):
    """관문별 통과 여부. True 통과 · False 막힘 · None 판정 불가(앞 관문에서 막힘)."""
    us = app.get("usStore") or {}
    g = app.get("globalReach") or {}
    if not us.get("available"):
        return {"us": False, "store": None, "app": None, "free": None, "iap": None, "iapen": None}
    has_iap = bool(us.get("iap"))
    return {
        "us": True,
        "store": bool(g.get("englishPage")),
        "app": "EN" in app_langs(app),
        "free": us.get("price", 0) == 0,
        "iap": has_iap,
        "iapen": us.get("iapEnglish") if has_iap else None,
    }


def reddit_miss(gates):
    """막힌 관문 키 — 고칠 일 단위로 센다."""
    miss = [k for k, v in gates.items() if v is False]
    if gates["us"] is False:
        miss = ["us"]
    if gates["free"] is False and "iap" in miss:
        miss.remove("iap")  # 유료 앱을 무료+인앱으로 바꾸는 것은 한 가지 일이다
    return miss


def reddit_tier(app):
    """레딧 출격 판정 칸(REDDIT_VERDICT 키). 미국 스토어 정보가 없으면 None."""
    if not app.get("usStore"):
        return None, []
    miss = reddit_miss(reddit_gates(app))
    return (3 if reddit_posted(app) else min(len(miss), 2)), miss


def reddit_page(apps):
    rows, gone = [], []
    for a in live(apps):
        if not a.get("usStore"):
            continue
        if not a.get("globalReach") and not a["usStore"].get("available"):
            gone.append(a)  # 어느 스토어에서도 안 보인다 — 내려간 앱
            continue
        gates = reddit_gates(a)
        rows.append((a, gates, reddit_miss(gates)))
    stage = lambda a: (a.get("lifecycle") or {}).get("stage") or 0
    tier = lambda r: 3 if reddit_posted(r[0]) else min(len(r[2]), 2)
    rows.sort(key=lambda r: (tier(r), -stage(r[0]),
                             -((r[0].get("usStore") or {}).get("ratingCount") or 0),
                             len(r[2]), r[0]["name"]))
    counts = {t: sum(1 for r in rows if tier(r) == t) for t, *_ in REDDIT_VERDICT}

    def mark(v):
        if v is None:
            return '<td class="na">–</td>'
        return '<td class="%s">%s</td>' % ("ok" if v else "no", "✓" if v else "✕")

    def price_txt(a):
        us = a.get("usStore") or {}
        if not us.get("available"):
            return ""
        p = us.get("price", 0)
        base = "무료" if p == 0 else "$%.2f" % p
        iap = us.get("iap") or []
        if iap:
            base += " · 인앱 %d개" % len(iap)
        return base

    def iap_tip(a):
        iap = (a.get("usStore") or {}).get("iap") or []
        return "\n".join("%s  %s" % (i["name"], i["price"]) for i in iap)

    body, cur = "", None
    for r in rows:
        a, gates, miss = r
        t = tier(r)
        if t != cur:
            cur = t
            _, name, why, color = REDDIT_VERDICT[t]
            body += ('<tr class="grp" style="--c:%s"><th colspan="%d"><i></i>%s<b>%d</b>'
                     '<em>%s</em></th></tr>' % (color, len(REDDIT_GATES) + 4, esc(name), counts[t], esc(why)))
        fix = "".join('<span class="todo">%s</span>' % esc(dict((k, f) for k, _, f in REDDIT_GATES)[k])
                      for k in miss) or ('<span class="go">올림 ✓</span>' if t == 3 else '<span class="go">올리기</span>')
        post = reddit_url(a)
        if post:
            fix += '<a class="post" href="%s" target="_blank" rel="noopener">레딧 글 ↗</a>' % esc(post)
        us = a.get("usStore") or {}
        tip = iap_tip(a)
        body += (
            '<tr><th><a href="%s" target="_blank" rel="noopener">%s<span>%s<em>%s</em></span></a></th>'
            '%s<td class="pr"%s>%s</td><td class="rc">%s</td><td class="sg">%s</td><td class="fx">%s</td></tr>'
            % (esc(a.get("appStoreUrl") or ""), icon_img(a), esc(a["name"]), esc(a.get("nameEn") or ""),
               "".join(mark(gates[k]) for k, _, _ in REDDIT_GATES),
               ' data-tip="%s"' % esc("인앱 구입 (미국 스토어)\n" + tip) if tip else "",
               esc(price_txt(a)),
               esc(us.get("ratingCount") or "–"),
               esc(STAGE_SHORT.get(stage(a), "")), fix))

    # 한 칸만 고치면 되는 앱이 어느 관문에 걸렸는지 — 가장 싼 일부터 보이게
    blockers = {}
    for a, gates, miss in rows:
        if len(miss) == 1 and not reddit_posted(a):
            blockers.setdefault(miss[0], []).append(a)
    block_html = "".join(
        '<div class="bk"><b>%s</b><span>%s</span></div>'
        % (esc(dict((k, f) for k, _, f in REDDIT_GATES)[k]),
           " · ".join(esc(a["name"]) for a in blockers[k]))
        for k, _, _ in REDDIT_GATES if k in blockers)

    cards = "".join(
        '<div class="vc" style="--c:%s"><b>%d</b><span>%s</span></div>' % (c, counts[t], esc(n))
        for t, n, _, c in REDDIT_VERDICT)
    head = ('<div class="eyebrow">Reddit Launch</div><h1>레딧 출격</h1>'
            '<p>영어권에서 사람을 데려와도 새지 않는 앱이 무엇인지. 데려온 사람이 보는 미국 '
            'App Store 기준으로, 영어로 읽히는지와 무료로 받아 결제까지 갈 수 있는지(부분 유료)를 봅니다.</p>'
            '<div class="vcs">%s</div>' % cards)
    main = (
        '<section><h2>앱별 판정<span class="hc">%d</span></h2>'
        '<p class="lead">초록 줄부터 올리세요. 같은 판정 안에서는 제품 여정 단계가 높고 미국 평가가 '
        '많은 앱이 위입니다. 가격 칸에 마우스를 올리면 인앱 구입 목록이 나옵니다.</p>'
        '<div class="lgw"><table class="lg rd"><thead><tr><th>앱</th>%s'
        '<th>미국 가격</th><th>미국 평가</th><th>단계</th><th class="fx">할 일</th></tr></thead>'
        '<tbody>%s</tbody></table></div></section>'
        '%s'
        '<section><h2>판정 기준</h2><p class="lead">'
        '<b>미국 판매</b> 미국 스토어 페이지가 열린다 · <b>영어 소개</b> 미국 스토어 소개에 한글이 없다 · '
        '<b>앱 영어</b> 앱 번들에 영어가 있다(EN 하나뿐이면 스토어 소개가 영어일 때만) · '
        '<b>무료 다운로드</b> 미국 가격 $0 · <b>인앱 구입</b> 스토어에 인앱 구입이 있다 · '
        '<b>인앱 이름 영어</b> 미국 사용자가 결제 화면에서 보는 인앱 이름에 한글이 없다.<br>'
        '출처: <code>sync-us-store.py</code>(미국 스토어 %s) · <code>sync-global-reach.py</code>. '
        '사용자 수·결제 수는 아직 넣지 못했습니다 — FeedbackHub Viewer 캐시는 앱 보호 폴더에 있어 '
        '스크립트가 읽지 못합니다.%s</p></section>'
        % (len(rows), "".join("<th>%s</th>" % esc(n) for _, n, _ in REDDIT_GATES), body,
           ('<section><h2>한 가지만 고치면 되는 앱</h2><p class="lead">고칠 것별로 묶었습니다. '
            '같은 일을 한 번에 몰아서 하면 빠릅니다.</p><div class="bks">%s</div></section>' % block_html)
           if block_html else "",
           max(((a.get("usStore") or {}).get("evaluatedAt") or "") for a, _, _ in rows) if rows else "-",
           ("<br>스토어에서 내려가 표에서 뺀 앱: " + " · ".join(esc(a["name"]) for a in gone)) if gone else ""))
    return page("레딧 출격", "레딧에 올릴 앱 판정", {"head": head, "main": main}, "reddit",
                LIFE_CSS + REDDIT_CSS, GF_JS)


REDDIT_CSS = """
  .vcs{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
  .vc{background:var(--card);border:1px solid var(--border);border-top:3px solid var(--c);
    border-radius:14px;padding:12px 18px;min-width:130px}
  .vc b{display:block;font-size:1.8rem;line-height:1.1;color:var(--c)}
  .vc span{font-size:.85rem;font-weight:700}
  .lg.rd{font-size:.86rem}
  .lg.rd thead th{font-size:.76rem}
  .lg.rd tbody th a span{display:flex;flex-direction:column;line-height:1.25}
  .lg.rd tbody th em{font-style:normal;font-size:.72rem;color:var(--muted);font-weight:600}
  .lg.rd td.ok{color:var(--ok);font-weight:800}
  .lg.rd td.no{color:#e5534b;font-weight:800;background:rgba(229,83,75,.08)}
  .lg.rd td.na{color:var(--muted);opacity:.5}
  .lg.rd td.pr,.lg.rd td.rc,.lg.rd td.sg{color:var(--muted)}
  .lg.rd td.pr[data-tip]{text-decoration:underline dotted;cursor:help;color:var(--text)}
  .lg.rd th.fx,.lg.rd td.fx{text-align:left;white-space:normal;min-width:200px}
  .lg.rd .todo{font-size:.78rem}
  .lg.rd .post{display:inline-block;margin-left:6px;padding:1px 9px;border-radius:999px;font-weight:700;
    font-size:.78rem;color:#ff4500;border:1px solid #ff450066;text-decoration:none}
  .lg.rd .post:hover{background:#ff45001a}
  .lg.rd .go{display:inline-block;padding:1px 9px;border-radius:999px;font-weight:800;font-size:.78rem;
    background:rgba(52,196,138,.15);color:var(--ok)}
  .rd tr.grp th{position:static;background:var(--bg-soft);text-align:left;padding:10px 12px;
    font-size:.86rem;font-weight:800;white-space:normal}
  .rd tr.grp i{display:inline-block;width:10px;height:10px;border-radius:3px;background:var(--c);margin-right:7px}
  .rd tr.grp b{margin:0 8px 0 6px;color:var(--c)}
  .rd tr.grp em{font-style:normal;font-weight:600;color:var(--muted);font-size:.8rem}
  .bks{display:grid;gap:8px}
  .bk{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:11px 14px}
  .bk b{display:block;font-size:.9rem;margin-bottom:2px}
  .bk span{font-size:.86rem;color:var(--muted)}
"""


# ── 공개: 앱별 할 일 ──────────────────────────────────────────────
# 목적: 앱마다 '갖춰야 할 것' 중 무엇이 되었고 무엇이 안 되었는지 — 곧 그 앱의 할 일 — 를 한눈에.
# 판정값은 서비스 숙성도·글로벌 지원과 같은 데이터를 쓴다. 기준(기본·권장·선택)은 CHECKLIST 만 고치면 된다.
def _lang(fn):
    return lambda a: fn(a) if a.get("globalReach") else None


CHECK_CATS = [
    ("lang", "언어", "#ef6aa0"), ("support", "지원 페이지", "#5b8def"), ("feedback", "피드백", "#34c48a"),
    ("infra", "인프라", "#e0a53a"), ("feature", "기능", "#a78bfa"), ("a11y", "접근성", "#e8789a"), ("craft", "다듬기", "#c9a227"),
    ("money", "수익화", "#f08c4a"), ("guide", "안내", "#6fbf73"),
    ("comms", "소통", "#3fb8c9"), ("quality", "품질", "#7c8cff"), ("data", "데이터", "#9aa5b1"),
    ("marketing", "홍보", "#d65db1"), ("intro", "소개 페이지", "#4fb3a9"),
]
NA = "na"  # 해당 없음 — 이 앱에는 물을 필요가 없는 항목. 분모에서 뺀다.


def _src(area, key):
    """sync-service-maturity.py 가 남긴 값. 그 칸을 아직 재지 않았으면 None(확인 불가)."""
    return lambda a: (mat(a).get(area) or {}).get(key)


def _intro(key):
    """sync-intro-pages.py 가 남긴 소개 페이지 판정. 아직 재지 않았으면 None."""
    return lambda a: (a.get("introPage") or {}).get(key)


def _intro_exists(a):
    """App Store 마케팅 URL 이 있고, 열리고, 지원 페이지가 아니라 앱을 소개한다."""
    m = a.get("introPage")
    if not m:
        return None
    if not m.get("set"):
        return False
    if m.get("reachable") is None:
        return None
    return bool(m["reachable"] and m.get("intro"))


def _sells(a):
    p = a.get("price") or {}
    return bool(p.get("hasInAppPurchases") or p.get("iapItems"))


def _if_sells(fn):
    """파는 상품이 있어야 뜻이 있는 항목 — 인앱 구입이 없으면 해당 없음."""
    return lambda a: fn(a) if _sells(a) else NA


def _mac_only(a):
    d = mat(a).get("devices") or {}
    return bool(d.get("mac")) and not any(d.get(k) for k in ("iphone", "ipad", "watch", "vision"))


def _unless_mac_only(fn):
    """맥 앱에서는 아무것도 바꾸지 않는 API 로 재는 항목 — 맥 전용 앱이면 해당 없음.
    (macOS 에서 presentationDetents·dynamicTypeSize·@ScaledMetric·submitLabel 은 효과가 없다)"""
    return lambda a: NA if _mac_only(a) else fn(a)


_restore = _if_sells(_src("money", "restore"))


def _tip_jar(a):
    v = _src("money", "tipJar")(a)
    kind = (load_paywalls().get(a["_slug"]) or {}).get("kind")
    return True if kind == "tip-jar" else v
CHECK_TIERS = [
    ("base", "기본", "모든 앱이 갖출 것 — 빠져 있으면 먼저 할 일입니다."),
    ("rec", "권장", "기본을 갖춘 다음 차례로 갖출 것입니다."),
    ("opt", "선택", "앱 성격에 맞을 때만 — 빠져 있어도 할 일로 세지 않습니다."),
]


def _a11y_captions(a):
    """영상이 있는 앱만 자막·음성 해설을 묻는다."""
    m = mat(a).get("a11y") or {}
    if not m:
        return None
    return m.get("captions") if m.get("_video") else NA


# (등급, 분류, 키, 이름, 판정 함수 → True/False/None)
CHECKLIST = [
    ("rec", "craft", "moments", "만족한 순간 세기", _src("craft", "moments")),
    ("rec", "craft", "sheets", "시트 다듬기", _unless_mac_only(_src("craft", "sheets"))),
    ("rec", "craft", "liveNumbers", "숫자 바뀜 효과", _src("craft", "liveNumbers")),
    ("rec", "craft", "localeFormat", "지역 맞춤 표기", _src("craft", "localeFormat")),
    ("rec", "craft", "textOverflow", "긴 글자 처리", _src("craft", "textOverflow")),
    ("rec", "craft", "inputFlow", "입력 흐름 다듬기", _unless_mac_only(_src("craft", "inputFlow"))),
    ("rec", "craft", "textCopy", "글자 복사 허용", _src("craft", "textCopy")),
    ("rec", "craft", "purchaseTest", "구매 흐름 시험", _if_sells(_src("craft", "purchaseTest"))),
    ("rec", "craft", "releaseTags", "버전별 출시 기록", _src("craft", "releaseTags")),
    ("rec", "craft", "steadyUpdates", "꾸준한 손질", _src("craft", "steadyUpdates")),
    ("base", "a11y", "voiceOver", "VoiceOver 설명", _m("a11y", "voiceOver")),
    ("base", "a11y", "dynamicType", "큰 글씨 따라가기", _unless_mac_only(_m("a11y", "dynamicType"))),
    ("base", "a11y", "darkMode", "다크 모드", _m("a11y", "darkMode")),
    ("rec", "a11y", "voiceControl", "음성 제어 이름", _m("a11y", "voiceControl")),
    ("rec", "a11y", "structure", "읽는 순서·역할", _m("a11y", "structure")),
    ("rec", "a11y", "actions", "VoiceOver 동작", _m("a11y", "actions")),
    ("rec", "a11y", "announcements", "바뀐 내용 알려 주기", _m("a11y", "announcements")),
    ("rec", "a11y", "largeLayout", "큰 글씨 배치 바꾸기", _m("a11y", "largeLayout")),
    ("rec", "a11y", "reduceMotion", "애니메이션 줄이기", _m("a11y", "reduceMotion")),
    ("rec", "a11y", "differentiate", "색 없이 구별", _m("a11y", "differentiate")),
    ("rec", "a11y", "contrast", "대비 높이기", _m("a11y", "contrast")),
    ("rec", "a11y", "reduceTransparency", "투명도 줄이기", _m("a11y", "reduceTransparency")),
    ("rec", "a11y", "a11yAudit", "접근성 자동 점검", _src("a11y", "a11yAudit")),
    ("opt", "a11y", "captions", "자막·음성 해설", _a11y_captions),
    ("opt", "a11y", "boldText", "굵은 텍스트", _src("a11y", "boldText")),
    ("opt", "a11y", "invertColors", "색 반전 보호", _src("a11y", "invertColors")),
    ("opt", "a11y", "keyboard", "키보드로 조작", _src("a11y", "keyboard")),
    ("base", "lang", "appEn", "앱 영어 지원", _lang(lambda a: "EN" in app_langs(a))),
    ("base", "lang", "storeEn", "영어 스토어 소개", _lang(lambda a: bool(a["globalReach"].get("englishPage")))),
    ("base", "support", "registered", "지원 페이지 등록", _m("support", "registered")),
    ("base", "support", "reachable", "지원 페이지 열림", _m("support", "reachable")),
    ("base", "support", "privacy", "개인정보 처리방침", _m("support", "privacy")),
    ("base", "support", "contact", "문의 수단 안내", _m("support", "contact")),
    ("base", "feedback", "inAppFeedback", "앱 안 피드백", _m("feedback", "inAppFeedback")),
    ("base", "feedback", "reviewPrompt", "리뷰 요청", _m("feedback", "reviewPrompt")),
    ("base", "infra", "analytics", "사용 통계", _m("ops", "analytics")),
    ("base", "infra", "crash", "크래시 진단", _m("ops", "crash")),
    ("base", "infra", "leeoKit", "LeeoKit 적용", _m("ops", "leeoKit")),
    ("base", "feature", "onboarding", "첫 실행 안내", _m("ux", "onboarding")),
    ("base", "infra", "privacyManifest", "개인정보 매니페스트", _src("ops", "privacyManifest")),
    ("base", "money", "restore", "구매 복원", _restore),
    ("base", "comms", "whatsNew", "새 기능 알림", _src("comms", "whatsNew")),
    ("base", "intro", "introPage", "소개 페이지", _intro_exists),
    ("rec", "lang", "multi", "3개 이상 언어", _lang(lambda a: len(app_langs(a)) >= 3)),
    ("rec", "support", "english", "영어 지원 페이지", _m("support", "english")),
    ("rec", "feedback", "mailContact", "메일 문의", _m("feedback", "mailContact")),
    ("rec", "feedback", "writeReview", "리뷰 쓰기 바로가기", _m("feedback", "writeReview")),
    ("rec", "infra", "killSwitch", "원격 기능 끄기", _m("ops", "killSwitch")),
    ("rec", "quality", "tests", "자동 테스트", _m("ops", "tests")),
    ("rec", "feature", "tips", "사용 팁", _m("ux", "tips")),
    ("rec", "infra", "crashLoop", "연속 크래시 보호", _src("ops", "crashLoop")),
    ("rec", "money", "paywall", "페이월 화면", _if_sells(_src("money", "paywall"))),
    ("rec", "money", "tiers", "유료 등급 설계", _if_sells(_src("money", "tiers"))),
    ("rec", "money", "freeGate", "써 보고 결제(무료 문턱)", _if_sells(_src("money", "freeGate"))),
    ("rec", "money", "discount", "할인 제안", _if_sells(_src("money", "discount"))),
    ("rec", "money", "tipJar", "후원 받기", _tip_jar),
    ("rec", "money", "tipAsk", "후원 부탁 장치", _src("money", "tipAsk")),
    ("rec", "money", "gift", "선물하기", _if_sells(_src("money", "gift"))),
    ("rec", "comms", "roadmap", "로드맵 공개", _src("comms", "roadmap")),
    ("rec", "comms", "feedbackReply", "의견에 답장", _src("comms", "feedbackReply")),
    ("opt", "guide", "progressive", "단계적 공개", _src("guide", "progressive")),
    ("opt", "guide", "contextualLesson", "상황 맞춤 수업", _src("guide", "contextualLesson")),
    ("opt", "guide", "practice", "직접 해 보는 첫 실행", _src("guide", "practice")),
    ("opt", "guide", "promptArbiter", "안내 창 교통정리", _src("guide", "promptArbiter")),
    ("opt", "guide", "lessonLedger", "배운 것 기록", _src("guide", "lessonLedger")),
    ("rec", "money", "iapEnglish", "인앱 상품 이름 영어", _if_sells(lambda a: (a.get("usStore") or {}).get("iapEnglish"))),
    ("rec", "infra", "performance", "성능 측정", _src("more", "performance")),
    ("rec", "infra", "logging", "구조적 로그", _src("more", "logging")),
    ("rec", "infra", "funnel", "전환 퍼널 측정", _src("more", "funnel")),
    ("rec", "infra", "appSpec", "완성도 계약 선언", _src("more", "appSpec")),
    ("rec", "infra", "preflight", "출시 전 자동 점검", _src("more", "preflight")),
    ("rec", "quality", "uiTests", "UI 자동 테스트", _src("more", "uiTests")),
    ("rec", "quality", "swiftlint", "정적 분석(SwiftLint)", _src("more", "swiftlint")),
    ("rec", "quality", "ci", "CI 자동 빌드", _src("more", "ci")),
    ("rec", "feature", "emptyStates", "빈 화면 안내", _src("more", "emptyStates")),
    ("rec", "feature", "haptics", "햅틱 피드백", _src("more", "haptics")),
    ("rec", "marketing", "family", "내 다른 앱 소개", _src("more", "family")),
    ("rec", "marketing", "storeCopy", "스토어 문구 원고", _src("marketing", "storeCopy")),
    ("rec", "marketing", "screenshotCapture", "스크린샷 자동 촬영", _src("marketing", "screenshotCapture")),
    ("rec", "marketing", "marketingScreens", "문구 입힌 스크린샷", _src("marketing", "marketingScreens")),
    ("rec", "marketing", "localizedScreens", "언어별 스토어 스크린샷", _src("marketing", "localizedScreens")),
    ("rec", "marketing", "demoMode", "촬영용 데모 모드", _src("marketing", "demoMode")),
    ("rec", "marketing", "videoAsset", "사용·미리보기 영상", _src("marketing", "videoAsset")),
    ("opt", "feature", "widgets", "위젯", _m("ux", "widgets")),
    ("opt", "feature", "shortcuts", "단축어·Siri", _m("ux", "shortcuts")),
    ("opt", "feature", "cloudSync", "iCloud 동기화", _m("ux", "cloudSync")),
    ("opt", "feedback", "instagram", "인스타그램 DM", _m("feedback", "instagram")),
    ("opt", "data", "backup", "백업·내보내기", _src("ux", "backup")),
    ("opt", "data", "schemaMigration", "데이터 구조 이전", _src("more", "schemaMigration")),
    ("opt", "feature", "biometricLock", "생체 잠금", _src("more", "biometricLock")),
    ("opt", "feature", "notifications", "알림·재참여", _src("more", "notifications")),
    ("opt", "feature", "fold", "폴더블(아이폰 듀오) 대응", _src("more", "fold")),
    ("opt", "infra", "abTesting", "A/B 테스트", _src("more", "abTesting")),
    ("rec", "intro", "introScreens", "소개에 앱 화면", _intro("screens")),
    ("rec", "intro", "introVideo", "소개에 사용 영상", _intro("video")),
    ("rec", "intro", "introScenario", "쓰는 장면 이야기", _intro("scenario")),
    ("rec", "intro", "introSteps", "쓰는 순서 안내", _intro("steps")),
    ("rec", "intro", "introStoreLink", "App Store 링크", _intro("storeLink")),
    ("rec", "intro", "introEnglish", "영어 소개", _intro("english")),
    ("rec", "intro", "introOgImage", "공유 미리보기 그림", _intro("ogImage")),
    ("opt", "intro", "introTryIt", "페이지에서 직접 체험", _intro("tryIt")),
    ("opt", "intro", "introProof", "후기·평점", _intro("proof")),
    ("opt", "marketing", "videoTool", "사용 영상 자동 제작", _src("marketing", "videoTool")),
    ("opt", "marketing", "promoKit", "홍보 글 원고", _src("marketing", "promoKit")),
    ("opt", "marketing", "shareApp", "앱 추천 공유", _src("marketing", "shareApp")),
    ("opt", "marketing", "shareImage", "공유용 이미지", _src("marketing", "shareImage")),
    ("opt", "marketing", "shareVideo", "공유용 영상", _src("marketing", "shareVideo")),
    ("opt", "marketing", "deepLink", "딥링크", _src("marketing", "deepLink")),
    ("opt", "marketing", "offerCode", "프로모션 코드 입력", _if_sells(_src("marketing", "offerCode"))),
    ("opt", "marketing", "invite", "친구 초대", _src("marketing", "invite")),
    ("opt", "marketing", "installNudge", "앱 클립·설치 유도", _src("marketing", "installNudge")),
]
# 갖춰야 하지만 아직 자동으로 판정할 길이 없는 피처 — LeeoCapability 계약 · 클립키보드 운영에서 나온 것.
# 판정 방법이 생기면 CHECKLIST 로 옮긴다.
PLANNED = [
    ("data", "동기화 충돌 처리", "두 기기에서 같은 것을 고쳤을 때 어느 쪽도 잃지 않게 합니다."),
    ("data", "데이터 무결성 검증", "저장된 값이 깨졌는지 확인하고 고칩니다."),
    ("data", "자동저장·작업 복구", "쓰다 앱이 꺼져도 하던 일이 남아 있습니다."),
    ("infra", "네트워크 재시도·타임아웃", "연결이 잠깐 끊겨도 다시 시도하고, 오래 걸리면 알려 줍니다."),
    ("infra", "전역 에러 폴백 화면", "예상 못한 오류에서도 빈 화면 대신 돌아갈 길을 보여 줍니다."),
    ("infra", "롤백 전략", "새 버전에 문제가 있을 때 되돌릴 방법을 정해 둡니다."),
    ("infra", "릴리즈 건강 기준", "출시 뒤 크래시율·실행 실패율이 넘으면 안 되는 선을 정해 두고 봅니다."),
    ("infra", "핵심지표 대시보드", "앱의 핵심 숫자를 한 화면에서 매일 봅니다."),
    ("infra", "리텐션·코호트 분석", "처음 온 사람이 며칠 뒤에도 남아 있는지 봅니다."),
    ("quality", "베타 테스트(TestFlight)", "출시 전에 실제 사람에게 먼저 써 보게 합니다."),
    ("quality", "회귀 테스트 루틴", "출시 전마다 핵심 흐름을 정해진 순서로 다시 확인합니다."),
    ("quality", "코드 리뷰", "합치기 전에 다른 눈으로 바뀐 코드를 봅니다."),
    ("infra", "전송·저장 암호화", "민감한 값을 기기와 서버 사이, 기기 안에서 암호화합니다."),
    ("infra", "최소 권한 요청", "꼭 필요한 권한만, 필요한 순간에 묻습니다."),
    ("data", "데이터 삭제 경로", "쓰는 사람이 자기 데이터를 앱 안에서 지울 수 있습니다."),
    ("feature", "다크 모드 점검", "어두운 화면에서도 글자와 버튼이 묻히지 않는지 확인합니다."),
    ("feature", "앱 버전 표시", "설정 화면에서 버전과 빌드 번호를 볼 수 있어 문의할 때 편합니다."),
    ("marketing", "ASO 키워드 최적화", "검색어에 맞춰 이름·부제·키워드를 다듬습니다."),
    ("marketing", "홍보 채널 다변화", "스토어 밖에서 사람을 데려올 길을 여러 개 둡니다."),
    ("marketing", "이벤트·캠페인", "할인·무료 기간 같은 행사로 사람을 모읍니다."),
    ("marketing", "커뮤니티·제휴", "같은 관심사를 가진 모임·사람과 함께 알립니다."),
]

CHECK_HELP = {"appEn": "앱 화면을 영어로 쓸 수 있습니다.",
              "storeEn": "App Store 소개(이름·설명·스크린샷 문구)를 영어로 준비했습니다.",
              "multi": "한국어·영어 말고도 한 가지 이상 언어를 더 지원합니다.",
              "privacyManifest": "앱이 어떤 정보를 왜 쓰는지 Apple에 밝히는 파일(PrivacyInfo)입니다. 심사에서 요구합니다.",
              "restore": "기기를 바꾸거나 앱을 다시 깔아도 산 것을 되찾는 버튼입니다. 인앱 구입이 있으면 Apple이 요구합니다.",
              "whatsNew": "업데이트 뒤 처음 열 때 무엇이 새로 생겼는지 알려 줍니다. 새 기능이 쓰이지 않고 묻히는 것을 막습니다.",
              "crashLoop": "앱이 뜨자마자 연달아 꺼지면 가벼운 모드로 열어, 쓰는 사람이 앱에 갇히지 않게 합니다.",
              "paywall": "무엇이 무료이고 무엇을 돈 내고 여는지 보여 주는 결제 화면입니다.",
              "tiers": "무료 · Plus · Pro처럼 등급마다 열리는 기능을 나눠, 쓰는 만큼 고를 수 있게 합니다.",
              "freeGate": "처음부터 막지 않고 일정 횟수까지 다 써 보게 한 뒤, 쓸모를 느낀 사람에게 결제를 묻습니다.",
              "discount": "망설이는 사람에게 할인을 한 번 제안해 결제로 이어지게 합니다.",
              "tipJar": "기능을 잠그지 않고, 고마운 사람이 원하는 만큼 개발자를 응원할 수 있게 합니다.",
              "tipAsk": "오래 잘 쓴 사람에게 드물게, 알맞은 순간에 응원을 부탁하는 카드입니다.",
              "gift": "산 것을 다른 사람에게 선물하고, 받은 코드를 앱에서 넣을 수 있습니다.",
              "roadmap": "앞으로 만들 기능을 앱 안에서 보여 줘, 쓰는 사람이 다음을 기대하게 합니다.",
              "feedbackReply": "보낸 의견에 개발자가 단 답장을 앱 안에서 다시 볼 수 있습니다.",
              "backup": "데이터를 파일로 내보내거나 다시 들여올 수 있습니다.",
              "iapEnglish": "미국 스토어에서 인앱 상품 이름이 영어로 보입니다. 한국어로 남아 있으면 결제 직전에 떠납니다.",
              "performance": "앱이 느려지는 곳을 재서 기록합니다(OSSignposter·MetricKit).",
              "logging": "무슨 일이 있었는지 나중에 따라갈 수 있게 분류된 로그를 남깁니다.",
              "funnel": "설치부터 핵심 기능을 처음 쓰기까지 어디서 떠나는지 단계별로 셉니다.",
              "appSpec": "이 앱이 무엇을 갖췄는지 LeeoKit 완성도 계약(LeeoAppSpec)으로 선언합니다.",
              "preflight": "출시 전에 계약·설정을 자동으로 점검해 빠진 것을 알려 줍니다(LeeoPreflight).",
              "uiTests": "화면을 실제로 눌러 보는 자동 테스트로 핵심 흐름이 끝까지 가는지 확인합니다.",
              "swiftlint": "코드 규칙을 자동으로 검사합니다.",
              "ci": "올릴 때마다 자동으로 빌드하고 테스트합니다(GitHub Actions·Xcode Cloud).",
              "emptyStates": "내용이 없거나 불러오지 못했을 때 빈 화면 대신 안내를 보여 줍니다.",
              "haptics": "눌렀을 때 손끝으로 느껴지는 반응을 줍니다.",
              "family": "앱 안에서 내가 만든 다른 앱을 소개합니다(LeeoFamily).",
              "introPage": "App Store ‘마케팅 URL’(개발자 웹사이트)에 앱을 소개하는 페이지가 걸려 있고 열립니다. "
                           "지원 페이지·노션·블로그 글이나 문의·FAQ만 있는 페이지는 소개로 치지 않습니다.",
              "introScreens": "소개 페이지에 앱 화면 그림이 2장 이상 있어, 들어가기 전에 생김새를 봅니다.",
              "introVideo": "소개 페이지에서 앱이 움직이는 모습을 영상으로 봅니다.",
              "introScenario": "‘이럴 때 씁니다’처럼 쓰는 장면을 이야기로 보여 줍니다.",
              "introSteps": "‘이렇게 써요’처럼 쓰는 순서를 단계로 보여 줍니다.",
              "introStoreLink": "소개 페이지에서 바로 App Store 로 넘어가 받을 수 있습니다.",
              "introEnglish": "영어로 된 소개가 있습니다(미국 스토어 마케팅 URL 또는 영어 페이지).",
              "introOgImage": "소개 링크를 메신저·SNS에 붙이면 미리보기 그림이 뜹니다(og:image).",
              "introTryIt": "소개 페이지 안에서 앱의 핵심 동작을 직접 눌러 봅니다.",
              "introProof": "쓰는 사람의 후기나 평점을 보여 줍니다.",
              "storeCopy": "App Store 이름·부제·설명 원고를 앱 레포에 함께 둡니다(APPSTORE.md · fastlane metadata).",
              "screenshotCapture": "시뮬레이터에서 스크린샷을 찍는 스크립트가 있어, 화면이 바뀔 때마다 다시 찍기 쉽습니다.",
              "marketingScreens": "찍은 화면에 문구와 배경을 입혀 스토어용 스크린샷으로 만듭니다.",
              "localizedScreens": "3개 이상 언어로 그 언어 화면의 스토어 스크린샷을 만들어 두었습니다.",
              "demoMode": "스크린샷·영상을 찍을 때 보기 좋은 데이터를 채우는 모드가 앱 안에 있습니다.",
              "videoAsset": "앱이 움직이는 모습을 담은 영상(App Store 미리보기·홍보용)을 레포에 만들어 두었습니다.",
              "videoTool": "시뮬레이터 화면을 녹화해 사용 영상을 만드는 스크립트가 있습니다.",
              "promoKit": "레딧·SNS 등에 올릴 홍보 글 원고를 레포에 함께 둡니다.",
              "shareApp": "앱 안에서 이 앱의 App Store 링크를 다른 사람에게 보낼 수 있습니다.",
              "shareImage": "앱에서 만든 것을 그림으로 그려 바로 공유할 수 있습니다.",
              "shareVideo": "앱에서 만든 것을 짧은 영상으로 만들어 공유할 수 있습니다.",
              "deepLink": "링크·위젯에서 앱의 특정 화면으로 바로 들어옵니다.",
              "offerCode": "앱 안에서 프로모션 코드를 입력해 혜택을 받을 수 있습니다.",
              "invite": "친구를 초대하는 코드·링크가 있습니다.",
              "installNudge": "앱 클립이나 다른 화면에서 이 앱을 설치하도록 안내하는 배너를 띄웁니다.",
              "schemaMigration": "저장 구조가 바뀌어도 이전 데이터를 새 구조로 옮깁니다.",
              "biometricLock": "Face ID·Touch ID로 앱이나 민감한 내용을 잠급니다.",
              "notifications": "알림으로 다시 찾아오게 합니다.",
              "fold": "펼치는 아이폰(아이폰 듀오) 화면에 맞춰 두 쪽으로 나눠 보여 줍니다(LeeoFold).",
              "abTesting": "두 가지 안을 나눠 보여 주고 어느 쪽이 나은지 숫자로 비교합니다."}


def checklist(app):
    """{키: (등급, 분류, 이름, 값)} — CHECKLIST 순서."""
    return {k: (t, c, n, fn(app)) for t, c, k, n, fn in CHECKLIST}


def todo_of(app):
    """할 일 = 기본·권장 중 없는 것. 확인 불가는 따로."""
    ck = checklist(app)
    miss = [k for k, (t, _, _, v) in ck.items() if t != "opt" and v is False]  # NA 는 False 가 아니라 빠진다
    unk = [k for k, (t, _, _, v) in ck.items() if t != "opt" and v is None]
    return ck, miss, unk


def tier_score(ck, tier):
    vals = [v for t, _, _, v in ck.values() if t == tier and v is not None and v != NA]
    return sum(1 for v in vals if v), len(vals)


APPS_CSS = NAMES_CSS + """
  .wrap{max-width:1160px}
  .tdw .y,.tdw .n,.tdw .u{display:inline-grid;place-items:center;width:16px;height:16px;border-radius:50%;
    font-size:.58rem;font-weight:800;font-style:normal;flex:none}
  .tdw .n{border:1.5px solid #e5675f;opacity:1}
  .na{display:inline-grid;place-items:center;width:16px;height:16px;font-style:normal;color:var(--muted);flex:none}
  .na::before{content:"–"}
  .mu{color:var(--muted)}
  .tierh{display:flex;align-items:baseline;gap:9px;margin:14px 0 7px;font-size:.86rem}
  .tierh span{color:var(--muted);font-size:.76rem}
  .items{display:grid;grid-template-columns:repeat(auto-fill,minmax(205px,1fr));gap:6px}
  .it{font:inherit;text-align:left;cursor:pointer;display:flex;align-items:center;gap:8px;color:var(--text);
    background:var(--card);border:1px solid var(--border);border-left:3px solid var(--c);border-radius:10px;
    padding:7px 10px;font-size:.8rem}
  .it:hover{border-color:var(--accent);border-left-color:var(--c)}
  .it[aria-pressed=true]{background:var(--bg-soft);outline:2px solid var(--accent)}
  .it b{font-weight:700;flex:1}
  .it em{font-style:normal;font-weight:800;font-variant-numeric:tabular-nums;color:#e5675f}
  .it em.z{color:var(--ok)}
  .it small{font-size:.68rem;color:var(--muted);font-weight:700;white-space:nowrap}
  .it.zero{border-style:dashed;border-left-style:solid}
  .it.zero small{color:#e5675f}
  .it.plan{cursor:default;border-style:dashed;border-left-style:solid;opacity:.75}
  .it.plan:hover{border-color:var(--border);border-left-color:var(--c)}
  .tool{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:26px 0 10px;
    position:sticky;top:52px;z-index:5;background:var(--bg);padding:10px 0}
  .tool input{font:inherit;font-size:.9rem;flex:1 1 200px;min-width:0;color:var(--text);background:var(--card);
    border:1px solid var(--border);border-radius:999px;padding:8px 15px}
  .tool input:focus{outline:none;border-color:var(--accent)}
  .tool button{font:inherit;font-size:.8rem;font-weight:700;cursor:pointer;color:var(--text);
    background:var(--card);border:1px solid var(--border);padding:7px 12px;border-radius:999px;white-space:nowrap}
  .tool button:hover{border-color:var(--accent)}
  .tool button[aria-pressed=true]{background:linear-gradient(120deg,var(--accent),var(--accent-2));
    color:#fff;border-color:transparent}
  .cnt{font-size:.82rem;color:var(--muted);font-weight:700;margin:0 0 8px}
  .cnt b{color:var(--text)}
  .hd,.ap>summary{display:grid;grid-template-columns:minmax(160px,1.3fr) 90px 92px 92px minmax(0,2.4fr) 18px;
    gap:12px;align-items:center;padding:10px 14px}
  .hd{font-size:.7rem;color:var(--muted);font-weight:800;padding-top:0;padding-bottom:6px}
  .ap{background:var(--card);border:1px solid var(--border);border-radius:14px;margin-bottom:8px}
  .ap[hidden]{display:none}
  .ap>summary{cursor:pointer;list-style:none;font-size:.82rem}
  .ap>summary::-webkit-details-marker{display:none}
  .ap>summary::after{content:"▾";color:var(--muted);transition:.15s}
  .ap[open]>summary::after{transform:rotate(180deg)}
  .ap>summary:hover{background:var(--bg-soft);border-radius:14px}
  .ap[open]>summary{border-bottom:1px solid var(--border);border-radius:14px 14px 0 0}
  .nm{display:flex;align-items:center;gap:9px;min-width:0}
  .nm .ic{width:32px;height:32px;border-radius:8px}
  .nm>span{min-width:0}
  .nm b{display:block;font-size:.9rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .nm small{display:block;font-size:.7rem;color:var(--muted);font-weight:600;white-space:nowrap;
    overflow:hidden;text-overflow:ellipsis}
  .bd{display:inline-flex;align-items:center;gap:5px;font-weight:700;font-size:.76rem;white-space:nowrap}
  .bd::before{content:"";width:8px;height:8px;border-radius:3px;background:var(--c,var(--muted));flex:none}
  .tsc b{font-variant-numeric:tabular-nums;font-size:.86rem}
  .tsc b.done{color:var(--ok)}
  .pbar{display:block;height:5px;border-radius:999px;background:var(--bg-soft);overflow:hidden;margin-top:4px}
  .pbar i{display:block;height:100%;background:var(--c)}
  .miss{display:flex;flex-wrap:wrap;gap:4px;min-width:0}
  .miss span{font-size:.72rem;font-weight:700;padding:2px 8px;border-radius:999px;white-space:nowrap;
    border:1px solid var(--border);border-left:3px solid var(--c);background:var(--bg-soft)}
  .miss span.r{opacity:.65;border-style:dashed;border-left-style:solid}
  .miss .ok{color:var(--ok);font-weight:800;font-size:.78rem}
  .miss .more{color:var(--muted);border:0;background:none;padding:2px 2px}
  .body{padding:16px;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.5fr);gap:16px}
  .body h4{font-size:.86rem;margin-bottom:8px;display:flex;gap:8px;align-items:baseline}
  .body h4 span{color:var(--muted);font-size:.74rem;font-weight:700}
  .todo{list-style:none;display:grid;gap:6px;counter-reset:t}
  .todo li{display:grid;grid-template-columns:22px 1fr;gap:4px 8px;font-size:.82rem;counter-increment:t;
    border:1px solid var(--border);border-left:3px solid var(--c);border-radius:10px;padding:8px 10px}
  .todo li::before{content:counter(t);font-weight:800;color:var(--muted);font-variant-numeric:tabular-nums}
  .todo li b{font-weight:700}
  .todo li b i{font-style:normal;font-size:.68rem;font-weight:800;color:var(--muted);margin-left:6px}
  .todo li p{grid-column:2;color:var(--muted);font-size:.76rem;line-height:1.5}
  .todo li.rec{border-style:dashed;border-left-style:solid}
  .allgood{color:var(--ok);font-weight:700;font-size:.85rem}
  .unk{margin-top:10px;font-size:.78rem;color:var(--muted)}
  .cats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}
  .cats h5{font-size:.78rem;display:flex;align-items:center;gap:7px;margin-bottom:5px}
  .cats h5::before{content:"";width:8px;height:8px;border-radius:3px;background:var(--c)}
  .cats h5 em{margin-left:auto;font-style:normal;color:var(--muted)}
  .cats ul{list-style:none;display:grid;gap:3px}
  .cats li{display:flex;align-items:center;gap:7px;font-size:.78rem}
  .cats li small{margin-left:auto;font-size:.64rem;color:var(--muted);font-weight:700}
  .cats li.opt{opacity:.7}
  .lk{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}
  .lk a{font-size:.76rem;font-weight:700;text-decoration:none;color:var(--text);background:var(--bg-soft);
    border:1px solid var(--border);padding:4px 10px;border-radius:999px}
  .lk a:hover{border-color:var(--accent);color:var(--accent)}
  .empty{padding:30px;text-align:center;color:var(--muted)}
  @media(max-width:860px){.hd{display:none}
    .ap>summary{grid-template-columns:1fr 1fr 1fr 18px;row-gap:8px}
    .ap>summary .nm{grid-column:1/4}
    .ap>summary::after{grid-column:4;grid-row:1}
    .ap>summary .miss{grid-column:1/-1}
    .ap>summary>[data-l]::before{content:attr(data-l);display:block;font-size:.66rem;color:var(--muted);font-weight:800}
    .body{grid-template-columns:1fr}}
"""

APPS_JS = """
<script>
(function(){var q=document.getElementById('q'),list=[].slice.call(document.querySelectorAll('.ap')),
box=document.getElementById('list'),cnt=document.getElementById('cnt'),emp=document.getElementById('emp'),
st='all',item=null,sort='stage';
function run(){var t=(q.value||'').trim().toLowerCase(),n=0;list.forEach(function(d){
var ok=(!t||d.getAttribute('data-q').indexOf(t)>=0)&&(st==='all'||d.getAttribute('data-s')===st)
&&(!item||(' '+d.getAttribute('data-miss')+' ').indexOf(' '+item+' ')>=0);
d.hidden=!ok;if(ok)n++;});
var lbl=item?document.querySelector('.it[data-k="'+item+'"] b').textContent:'';
cnt.innerHTML='';var b=document.createElement('b');b.textContent=n+'개 앱';cnt.appendChild(b);
if(item)cnt.appendChild(document.createTextNode(' — ‘'+lbl+'’이(가) 빠진 앱'));emp.hidden=n>0;}
function resort(){var key=sort==='todo'?function(d){return -(+d.getAttribute('data-n'))}:function(d){return +d.getAttribute('data-o')};
list.slice().sort(function(a,b){return key(a)-key(b)||(+a.getAttribute('data-o'))-(+b.getAttribute('data-o'))})
.forEach(function(d){box.appendChild(d)});box.appendChild(emp);}
q.addEventListener('input',run);
document.addEventListener('click',function(e){var b=e.target.closest('[data-st]');
if(b){st=b.getAttribute('data-st');document.querySelectorAll('[data-st]').forEach(function(x){
x.setAttribute('aria-pressed',x===b?'true':'false');});run();return;}
b=e.target.closest('[data-sort]');if(b){sort=b.getAttribute('data-sort');document.querySelectorAll('[data-sort]')
.forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});resort();return;}
b=e.target.closest('.it');if(b){var k=b.getAttribute('data-k');item=item===k?null:k;
document.querySelectorAll('.it').forEach(function(x){x.setAttribute('aria-pressed',x.getAttribute('data-k')===item?'true':'false');});
run();if(item)document.getElementById('tool').scrollIntoView({block:'start',behavior:'smooth'});return;}
var x=e.target.closest('#all');if(x){var open=x.getAttribute('aria-pressed')!=='true';
x.setAttribute('aria-pressed',open?'true':'false');x.textContent=open?'모두 접기':'모두 펼치기';
list.forEach(function(d){if(!d.hidden)d.open=open;});}});
function hash(){var h=location.hash.slice(1);if(!h)return;var d=document.getElementById(h);
if(d&&d.classList.contains('ap')){var tb=document.querySelector('.tabs button[data-t="todo"]');if(tb)tb.click();
d.hidden=false;d.open=true;d.scrollIntoView({block:'start'});}}
run();hash();window.addEventListener('hashchange',hash);})();
</script>
"""

STAGE_COLOR = {5: "#34c48a", 4: "#5b8def", 3: "#a78bfa", 2: "#e0a53a", 1: "#8b90a0"}
CAT_COLOR = {k: c for k, _, c in CHECK_CATS}
CAT_NAME = {k: n for k, n, _ in CHECK_CATS}
TIER_NAME = {k: n for k, n, _ in CHECK_TIERS}


def _mark(v):
    if v == NA:
        return '<i class="na" title="해당 없음"></i>'
    return '<i class="%s"></i>' % ("u" if v is None else "y" if v else "n")


def _score_html(got, known, color):
    if not known:
        return '<span class="mu">확인 불가</span>'
    return ('<b%s>%d/%d</b><span class="pbar"><i style="width:%d%%;--c:%s"></i></span>'
            % (' class="done"' if got == known else "", got, known, round(100 * got / known), color))


def _app_detail(a, ck, miss, unk):
    todo = ""
    for k in miss:
        t, c, n, _ = ck[k]
        why = ITEM_WHY.get(k) or CHECK_HELP.get(k) or ITEM_HELP.get(k) or ""
        todo += ('<li class="%s" style="--c:%s"><b>%s<i>%s · %s</i></b>%s</li>'
                 % (t, CAT_COLOR[c], esc(n), esc(TIER_NAME[t]), esc(CAT_NAME[c]),
                    "<p>%s</p>" % esc(why) if why else ""))
    left = ('<h4>할 일<span>%d개 · 기본부터</span></h4>' % len(miss)
            + ('<ol class="todo">%s</ol>' % todo if todo else '<p class="allgood">기본·권장 항목을 모두 갖췄습니다.</p>'))
    if unk:
        left += '<p class="unk">확인 필요 · %s</p>' % esc(", ".join(ck[k][2] for k in unk))
    cats = ""
    for c, cn, color in CHECK_CATS:
        rows = [(k, v) for k, v in ck.items() if v[1] == c]
        got = sum(1 for _, v in rows if v[3] is True and v[0] != "opt")
        known = sum(1 for _, v in rows if v[3] not in (None, NA) and v[0] != "opt")
        cats += ('<div><h5 style="--c:%s">%s<em>%d/%d</em></h5><ul>%s</ul></div>'
                 % (color, esc(cn), got, known, "".join(
                     '<li class="%s">%s%s<small>%s</small></li>' % (v[0], _mark(v[3]), esc(v[2]), esc(TIER_NAME[v[0]]))
                     for k, v in rows)))
    g = a.get("globalReach")
    langs = ('<p class="mu" style="font-size:.76rem;margin-top:10px">지원 언어 %d개 · %s</p>'
             % (len(app_langs(a)), esc(lang_names(a)))) if g else ""
    ls = [("쇼케이스 소개", intro_link(a), False)]
    for t, u in (("App Store", a.get("appStoreUrl")), ("지원 페이지", a.get("supportUrl"))):
        if u:
            ls.append((t, u, True))
    ls.append(("비즈니스 모델", "business.html#bm-%s" % a["_slug"], False))
    links = '<div class="lk">%s</div>' % "".join(
        '<a href="%s"%s>%s</a>' % (esc(u), ' target="_blank" rel="noopener"' if ext else "", esc(t))
        for t, u, ext in ls)
    right = '<h4>항목별 상태<span>✓ 됨 · ○ 안 됨 · ? 확인 불가 · – 해당 없음</span></h4><div class="cats">%s</div>%s%s' % (cats, langs, links)
    return '<div class="body"><div>%s</div><div>%s</div></div>' % (left, right)


def todo_panel(ls):
    """서비스 숙성도의 '할 일' 탭 — 피처 지도 + 앱별 할 일 목록."""
    ls = sorted(ls, key=lambda a: a["name"])
    ls.sort(key=lambda a: (-((a.get("lifecycle") or {}).get("stage") or 0), a["name"]))
    data = [(a,) + todo_of(a) for a in ls]

    # 항목별로 빠진 앱 수 — 누르면 그 항목이 빠진 앱만 남는다
    items = ""
    for tier, tn, tdesc in CHECK_TIERS:
        btns = ""
        for t, c, k, n, _ in CHECKLIST:
            if t != tier:
                continue
            missing = sum(1 for _, ck, _, _ in data if ck[k][3] is False)
            known = sum(1 for _, ck, _, _ in data if ck[k][3] not in (None, NA))
            have = known - missing
            btns += ('<button type="button" class="it%s" data-k="%s" aria-pressed="false" style="--c:%s" '
                     'title="%s"><b>%s</b><small>%s</small><em class="%s">%s</em></button>'
                     % ("" if have else " zero", k, CAT_COLOR[c],
                        esc("%s · %s" % (CAT_NAME[c], CHECK_HELP.get(k) or ITEM_HELP.get(k) or "")), esc(n),
                        "적용 %d" % have if have else "아직 없음", "z" if not missing else "",
                        "빠짐 %d" % missing if missing else "모두 됨"))
        items += '<div class="tierh"><b>%s</b><span>%s</span></div><div class="items">%s</div>' % (esc(tn), esc(tdesc), btns)
    items += ('<div class="tierh"><b>도입 예정</b><span>갖춰야 하지만 아직 자동으로 판정할 방법이 없는 피처입니다. '
              '판정 방법이 생기면 위로 옮깁니다.</span></div><div class="items">%s</div>'
              % "".join('<div class="it plan" style="--c:%s" title="%s"><b>%s</b><small>%s</small></div>'
                        % (CAT_COLOR[c], esc(why), esc(n), esc(CAT_NAME[c])) for c, n, why in PLANNED))
    nobody = [n for t, c, k, n, _ in CHECKLIST if not any(ck[k][3] is True for _, ck, _, _ in data)]

    rows = ""
    for i, (a, ck, miss, unk) in enumerate(data):
        st = (a.get("lifecycle") or {}).get("stage")
        bg, bk = tier_score(ck, "base")
        rg, rk = tier_score(ck, "rec")
        base_miss = [k for k in miss if ck[k][0] == "base"]
        chips = "".join('<span%s style="--c:%s">%s</span>' % ("" if ck[k][0] == "base" else ' class="r"',
                                                             CAT_COLOR[ck[k][1]], esc(ck[k][2])) for k in miss[:5])
        if len(miss) > 5:
            chips += '<span class="more">외 %d개</span>' % (len(miss) - 5)
        if not miss:
            chips = '<span class="ok">할 일 없음</span>' if not unk else '<span class="mu">확인 필요 %d개</span>' % len(unk)
        sub = " · ".join(x for x in [a.get("nameEn"), ("v" + a["currentVersion"]) if a.get("currentVersion") else ""] if x)
        q = " ".join([a["name"], a.get("nameEn") or "", a["_slug"]]).lower()
        rows += ('<details class="ap" id="%s" data-q="%s" data-s="%s" data-miss="%s" data-n="%d" data-o="%d"><summary>'
                 '<span class="nm">%s<span><b>%s</b><small>%s</small></span></span>'
                 '<span data-l="제품 여정"><span class="bd" style="--c:%s">%s</span></span>'
                 '<span class="tsc" data-l="기본">%s</span><span class="tsc" data-l="권장">%s</span>'
                 '<span class="miss" data-l="할 일 %d개">%s</span></summary>%s</details>'
                 % (esc(a["_slug"]), esc(q), st or 0, " ".join(miss), len(base_miss) * 100 + len(miss), i,
                    icon_img(a), esc(a["name"]), esc(sub), STAGE_COLOR.get(st, "var(--muted)"),
                    esc("%d %s" % (st, STAGE_SHORT.get(st, ""))) if st else "—",
                    _score_html(bg, bk, "#34c48a"), _score_html(rg, rk, "#5b8def"), len(miss), chips,
                    _app_detail(a, ck, miss, unk)))

    stages = sorted({(a.get("lifecycle") or {}).get("stage") or 0 for a in ls}, reverse=True)
    filt = '<button type="button" data-st="all" aria-pressed="true">전체</button>' + "".join(
        '<button type="button" data-st="%d" aria-pressed="false">%s</button>'
        % (s_, esc("%d %s" % (s_, STAGE_SHORT.get(s_, "")) if s_ else "판정 전")) for s_ in stages)
    total_base = sum(1 for _, ck, miss, _ in data for k in miss if ck[k][0] == "base")
    total_rec = sum(1 for _, ck, miss, _ in data for k in miss if ck[k][0] == "rec")
    base_done = sum(1 for _, ck, miss, _ in data if not [k for k in miss if ck[k][0] == "base"])
    main = ('<section><h2>피처 지도<span class="hc">%d개</span></h2><p class="lead">갖춰야 할 피처를 모두 늘어놓았습니다. '
            '자동으로 판정하는 %d개는 몇 개 앱에 들어갔는지 보이고, 그중 아직 어느 앱에도 없는 %d개와 '
            '판정 방법이 없는 도입 예정 %d개는 점선으로 표시했습니다. 적용 1인 피처는 대부분 클립키보드에서 먼저 만든 것입니다. '
            '누르면 그 피처가 빠진 앱만 아래에 남고, 다시 누르면 풀립니다.</p>%s</section>'
            '<div class="tool" id="tool"><input id="q" type="search" placeholder="앱 이름으로 찾기" aria-label="앱 이름으로 찾기">'
            '%s<span style="flex:1"></span><button type="button" data-sort="stage" aria-pressed="true">단계 높은 순</button>'
            '<button type="button" data-sort="todo" aria-pressed="false">할 일 많은 순</button>'
            '<button type="button" id="all" aria-pressed="false">모두 펼치기</button></div>'
            '<p class="cnt" id="cnt"></p>'
            '<div class="hd"><span>앱</span><span>제품 여정</span><span>기본</span><span>권장</span>'
            '<span>할 일 (기본 먼저, 점선은 권장)</span><span></span></div>'
            '<div id="list">%s<p class="empty" id="emp" hidden>조건에 맞는 앱이 없습니다.</p></div>'
            % (len(CHECKLIST) + len(PLANNED), len(CHECKLIST), len(nobody), len(PLANNED), items, filt, rows))
    lead = ('<p class="lead">기본 항목을 모두 갖춘 앱은 %d개이고, 남은 할 일은 기본 %d건 · 권장 %d건입니다. '
            '줄을 누르면 그 앱의 할 일 목록이 펼쳐집니다.</p>' % (base_done, total_base, total_rec))
    return '<div class="tdw">%s%s</div>' % (lead, main)


def apps_page(apps):
    """옛 '앱별 할 일' 주소 — 서비스 숙성도의 할 일 탭으로 넘긴다. 앱 앵커(#slug)는 그대로 살린다."""
    head = '<div class="eyebrow">Moved</div><h1>서비스 숙성도로 옮겼습니다</h1>' \
           '<p>앱별 할 일은 이제 <a href="maturity.html#todo">서비스 숙성도의 할 일 탭</a>에 있습니다.</p>'
    js = "<script>location.replace('maturity.html'+(location.hash&&location.hash!=='#'?location.hash:'#todo'));</script>"
    return page("서비스 숙성도로 옮김 — 리이오의 앱 포트폴리오", "앱별 할 일은 서비스 숙성도 페이지의 할 일 탭으로 옮겼습니다.",
                {"head": head, "main": ""}, "maturity", "", js)


def main():
    links = json.load(open(os.path.join(ROOT, "scripts/hub-links.json"), encoding="utf-8"))
    apps = load_apps()
    save_revenue_gates(apps)
    os.makedirs(REPORTS, exist_ok=True)
    outs = [
        (os.path.join(DOCS, "apps.html"), apps_page(apps), "공개"),
        (os.path.join(DOCS, "lifecycle.html"), lifecycle_page(apps), "공개"),
        (os.path.join(DOCS, "maturity.html"), maturity_page(apps), "공개"),
        (os.path.join(DOCS, "business.html"), business_page(apps), "공개"),
        (os.path.join(DOCS, "paywalls.html"), paywalls_page(apps), "공개"),
        (os.path.join(DOCS, "category.html"), category_page(apps), "공개"),
        (os.path.join(DOCS, "hub.html"), hub_page(apps), "공개"),
        (os.path.join(REPORTS, "portfolio-hub.html"), internal_hub(apps, links), "내부"),
        (os.path.join(DOCS, "reddit-launch.html"), reddit_page(apps), "공개"),
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
