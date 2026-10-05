#!/usr/bin/env python3
"""포트폴리오 허브·수명주기 페이지 생성.

사용법:
  python3 scripts/build-portfolio-hub.py

출력 3종:
  docs/hub.html               공개 허브 — 쇼케이스·수명주기·앱별 지원페이지 (GitHub Pages 배포)
  docs/lifecycle.html         공개 수명주기 — 제품 여정 5단계 (GitHub Pages 배포)
  docs/maturity.html          공개 서비스 숙성도 — 국가별 언어·지원 페이지·피드백·운영·경험·기기 탭
  reports/portfolio-hub.html  내부 허브 — 위 + 아티팩트·로컬 파일 링크 (비배포)

⚠️ docs/ 는 통째로 공개된다. 공개 페이지에는 다음을 넣지 않는다:
  · 아티팩트 URL (기본 비공개지만 링크를 알면 열리므로 사실상 전체 공개가 된다)
  · 수명주기 하위 등급 A/B/C(개선 중·소강·정지) — 내부 트리아지 표현
  · 폐기(stage 0) 앱
  · file:// 로컬 경로

데이터 출처:
  scripts/hub-links.json          수동 관리 링크(개요·아티팩트)
  Data/apps/*.json                supportUrl · lifecycle · globalReach · serviceMaturity (자동 수집)
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
           "HI": "힌디어", "ID": "인도네시아어", "NL": "네덜란드어", "TR": "튀르키예어"}


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

    # 단계 × 글로벌 지원 지도
    # 왼쪽(한국어만) → 오른쪽(다국어)으로 넓어지게 놓는다 — '오른쪽 위'가 가장 멀리 닿는 칸
    cols = [g for g in reversed(GLOBAL) if gcount[g[0]]]
    gname = {lv: n for lv, n, _, _ in GLOBAL}
    gcolor = {lv: c for lv, _, _, c in GLOBAL}
    thead = "<tr><th></th>%s</tr>" % "".join(
        '<th style="--c:%s">%s<em>%s</em></th>' % (c, esc(name), esc(GLOBAL_SUB[lv]))
        for lv, name, _, c in cols)
    tbody = ""
    for st, en, kr, _ in STAGES:
        items = buckets.get(st, [])
        if not items:
            continue
        cells = ""
        for lv, _, _, _ in cols:
            hit = sorted((a for a in items if reach(a) == lv), key=lambda a: a["name"])
            if not hit:
                cells += '<td class="z"></td>'
                continue
            cells += '<td data-l="%s" style="--c:%s"><span class="n">%d</span>%s</td>' % (
                esc(gname[lv]), gcolor[lv], len(hit), "".join(
                '<a href="%s" title="%s">%s</a>' % (
                    intro_link(a), esc("%s · %s" % (a["name"], lang_names(a))), icon_img(a))
                for a in hit))
        tbody += '<tr><th><b>%d</b>%s</th>%s</tr>' % (st, esc(STAGE_SHORT[st]), cells)
    matrix = ('<section><h2>두 축으로 보기</h2>'
              '<p class="lead">세로는 제품 여정, 가로는 글로벌 지원입니다. 오른쪽으로 갈수록 더 많은 '
              '언어로, 위로 갈수록 더 단단하게 닿는 앱입니다. 앱은 지금 닿는 가장 넓은 칸 하나에만 '
              '들어갑니다. 다국어 칸의 앱도 한국어를 지원하므로 한국어만 칸에는 다시 넣지 않습니다.</p>'
              '<div class="mxw"><table class="mx"><thead>%s</thead><tbody>%s</tbody></table></div>'
              '<p class="lead" style="margin-top:12px">%s</p></section>'
              % (thead, tbody, " ".join(
                  "<b>%s</b> %s" % (esc(name), esc(why)) for _, name, why, _ in cols)))

    languages = lang_section(ls)

    filters = ('<div class="gf" role="group" aria-label="글로벌 지원으로 강조">'
               '<button data-v="all" aria-pressed="true">전체</button>%s</div>'
               % "".join('<button data-v="%d" aria-pressed="false">%s %d</button>'
                         % (lv, esc(name), gcount[lv]) for lv, name, _, _ in cols))

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
     "앱을 열지 않아도, 기기를 바꿔도, 눈이 불편해도 쓸 수 있는지 봅니다.",
     [("widgets", "위젯"), ("shortcuts", "단축어·Siri"), ("cloudSync", "iCloud 동기화"),
      ("tips", "사용 팁"), ("accessibility", "VoiceOver 대응"), ("onboarding", "첫 실행 안내")]),
    ("devices", "기기",
     "어떤 기기에서 쓸 수 있도록 만들었는지 봅니다. 모든 앱이 모든 기기를 지원할 필요는 "
     "없어서 숙성도 점수에는 넣지 않았습니다.",
     [("iphone", "iPhone"), ("ipad", "iPad"), ("mac", "Mac"), ("watch", "Apple Watch"),
      ("vision", "Vision Pro")]),
]
SCORED = ("support", "feedback", "ops", "ux")
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
    "accessibility": "화면 읽기(VoiceOver)용 설명을 붙였습니다.",
    "onboarding": "처음 열었을 때 쓰는 법을 안내합니다.",
}

# 주요 18개국 스토어 — sync-global-reach.py 의 STOREFRONTS 와 같은 순서
COUNTRIES = [
    ("kr", "🇰🇷", "한국", ["KO"]), ("us", "🇺🇸", "미국", ["EN"]), ("jp", "🇯🇵", "일본", ["JA"]),
    ("gb", "🇬🇧", "영국", ["EN"]), ("de", "🇩🇪", "독일", ["DE"]), ("fr", "🇫🇷", "프랑스", ["FR"]),
    ("cn", "🇨🇳", "중국", ["ZH"]), ("tw", "🇹🇼", "대만", ["ZH"]), ("es", "🇪🇸", "스페인", ["ES"]),
    ("br", "🇧🇷", "브라질", ["PT"]), ("in", "🇮🇳", "인도", ["EN", "HI"]),
    ("ca", "🇨🇦", "캐나다", ["EN", "FR"]), ("au", "🇦🇺", "호주", ["EN"]),
    ("it", "🇮🇹", "이탈리아", ["IT"]), ("vn", "🇻🇳", "베트남", ["VI"]),
    ("th", "🇹🇭", "태국", ["TH"]), ("id", "🇮🇩", "인도네시아", ["ID"]),
    ("mx", "🇲🇽", "멕시코", ["ES"]),
]

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
  .mt thead th[data-c]{cursor:pointer}
  .mt thead th[data-c]:hover,.mt thead th.on{color:var(--accent)}
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
  [data-focus] tbody tr{opacity:.22}
  [data-focus] tbody tr.miss{opacity:1}
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
if(b){var id=b.getAttribute('data-t');show(id);history.replaceState(null,'','#'+id);return;}
var th=e.target.closest('th[data-c]');if(!th)return;var t=th.closest('table'),c=th.getAttribute('data-c');
t.querySelectorAll('th.on').forEach(function(x){if(x!==th)x.classList.remove('on')});
if(t.getAttribute('data-focus')===c){t.removeAttribute('data-focus');th.classList.remove('on');
t.querySelectorAll('tr.miss').forEach(function(r){r.classList.remove('miss')});return;}
t.setAttribute('data-focus',c);th.classList.add('on');
t.querySelectorAll('tbody tr').forEach(function(r){var td=r.children[+c];
r.classList.toggle('miss',!!td&&!!td.querySelector('.n'));});});
window.addEventListener('hashchange',function(){show(location.hash.slice(1))});})();
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
          '<span><i class="u"></i>확인 불가</span><span>열 제목을 누르면 그 항목이 없는 앱만 남깁니다.</span></div>')


def area_panel(key, name, why, items, apps):
    rows = sorted(apps, key=lambda a: (-(area_score(a, key)[0]), a["name"]))
    counts = {k: sum(1 for a in apps if area_vals(a, key).get(k)) for k, _ in items}
    known = {k: sum(1 for a in apps if area_vals(a, key).get(k) is not None) for k, _ in items}
    thead = '<tr><th>앱</th>%s%s</tr>' % (
        "".join('<th data-c="%d" title="%s">%s<em>%d/%d</em></th>'
                % (i + 1, esc(ITEM_HELP.get(k, "")), esc(lbl), counts[k], known[k])
                for i, (k, lbl) in enumerate(items)),
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
        "ux": "VoiceOver 대응은 화면 읽기용 설명이 %d곳 이상 붙어 있을 때 있음으로 봅니다." % 5,
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
            '나누지 않고 한 언어로 셉니다. 인도는 영어·힌디어, 캐나다는 영어·프랑스어를 현지어로 봅니다.</p>'
            % (n, covered, trs, store_en))


# 한눈에 표의 짧은 열 이름 — 탭의 긴 이름은 ITEM_HELP 툴팁으로 보여 준다
SHORT = {
    "registered": "등록", "reachable": "열림", "privacy": "개인정보", "english": "영어",
    "contact": "문의", "inAppFeedback": "앱 안", "mailContact": "메일", "instagram": "인스타",
    "reviewPrompt": "리뷰 요청", "writeReview": "리뷰 쓰기", "analytics": "통계",
    "crash": "크래시", "killSwitch": "원격 끄기", "tests": "테스트", "leeoKit": "LeeoKit",
    "widgets": "위젯", "shortcuts": "단축어", "cloudSync": "iCloud", "tips": "팁",
    "accessibility": "VoiceOver", "onboarding": "첫 안내", "iphone": "iPhone", "ipad": "iPad",
    "mac": "Mac", "watch": "Watch", "vision": "Vision",
}
AREA_COLOR = {"support": "#5b8def", "feedback": "#34c48a", "ops": "#e0a53a",
              "ux": "#a78bfa", "devices": "#8b90a0"}


def overview_panel(apps):
    """앱 × 전체 항목 한 표. 영역별로 머리줄을 묶고, 첫 열은 고정한 채 가로로 넘긴다."""
    # 소스를 못 찾은 앱은 지원 페이지만으로 비율이 매겨져 순위가 왜곡되므로 종합을 비우고 맨 아래에 둔다
    def rank(a):
        if not mat(a).get("source"):
            return (1, 0, 0, a["name"])
        got, known = total_score(a)
        return (0, -(got / (known or 1)), -got, a["name"])
    rows = sorted(apps, key=rank)

    groups = '<tr><th rowspan="2" class="ap">앱</th><th rowspan="2">언어</th>%s' \
             '<th rowspan="2">종합</th></tr>' % "".join(
                 '<th colspan="%d" class="gh" style="--c:%s">%s</th>'
                 % (len(items), AREA_COLOR[k], esc(n)) for k, n, _, items in AREAS)
    cols, col = "", 2  # tbody 의 칸 순서: 앱(0) · 언어(1) · 항목들(2~) · 종합
    for k, _, _, items in AREAS:
        for i, (item, lbl) in enumerate(items):
            have = sum(1 for a in apps if area_vals(a, k).get(item))
            known = sum(1 for a in apps if area_vals(a, k).get(item) is not None)
            cols += ('<th data-c="%d"%s title="%s — %s">%s<em>%d</em></th>'
                     % (col, ' class="g0"' if i == 0 else "", esc(lbl),
                        esc(ITEM_HELP.get(item, "있는 앱 %d / %d" % (have, known))),
                        esc(SHORT.get(item, lbl)), have))
            col += 1
    thead = groups + "<tr>%s</tr>" % cols

    tbody = ""
    for a in rows:
        got, known = total_score(a)
        langs = app_langs(a)
        cells = ""
        for k, _, _, items in AREAS:
            vals = area_vals(a, k)
            cells += "".join('<td%s>%s</td>' % (' class="g0"' if i == 0 else "", cell(vals[item], lbl))
                             for i, (item, lbl) in enumerate(items))
        ok = known and mat(a).get("source")
        tbody += '<tr>%s<td title="%s">%s</td>%s<td class="pct" style="color:%s">%s</td></tr>' % (
            app_th(a), esc(lang_names(a)), len(langs) if langs else '<i class="u"></i>', cells,
            score_color(got / known) if ok else "var(--muted)",
            "%d%%" % round(100 * got / known) if ok else
            '<i class="u" title="앱 소스를 확인하지 못했습니다"></i>')

    kp = ""
    for k, n, _, _ in AREAS:
        if k not in SCORED:
            continue
        g = sum(area_score(a, k)[0] for a in apps)
        t = sum(area_score(a, k)[1] for a in apps)
        r = g / t if t else 0
        kp += ('<div><span>%s</span><b>%d%%</b><small><i style="width:%d%%;--c:%s"></i></small></div>'
               % (esc(n), round(r * 100), round(r * 100), score_color(r)))
    return ('<p class="lead">앱 %d개가 항목 %d개 중 무엇을 갖췄는지 한 표에 모았습니다. 열 제목 아래 숫자는 '
            '그 항목을 갖춘 앱 수이고, 종합은 기기를 뺀 항목 가운데 갖춘 비율입니다.</p>'
            '<div class="kp">%s</div>%s'
            '<div class="tw"><table class="mt ov2"><thead>%s</thead><tbody>%s</tbody></table></div>'
            '<p class="note">소스 코드를 찾지 못한 앱은 앱 안의 기능을 ‘확인 불가’로 두고 종합 비율의 '
            '분모에서 뺍니다. 각 항목의 뜻은 열 제목에 마우스를 올리거나 위 탭에서 볼 수 있습니다.</p>'
            % (len(apps), col - 2, kp, LEGEND, thead, tbody))


def maturity_page(apps):
    # 스토어에서 내려간 앱(글로벌 지원 판정 없음)은 뺀다 — 제품 여정의 글로벌 축과 같은 기준
    ls = [a for a in live(apps) if a.get("serviceMaturity") and a.get("globalReach")]
    n = len(ls)
    tabs = [("overview", "한눈에", None, overview_panel(ls)),
            ("country", "국가별 언어", "%d개국" % len(COUNTRIES), country_panel(ls))]
    for key, name, why, items in AREAS:
        if key == "devices":
            continue
        g = sum(area_score(a, key)[0] for a in ls)
        t = sum(area_score(a, key)[1] for a in ls)
        tabs.append((key, name, "%d%%" % round(100 * g / t) if t else "", area_panel(key, name, why, items, ls)))
    key, name, why, items = AREAS[-1]
    tabs.append((key, name, None, area_panel(key, name, why, items, ls)))

    bar = '<div class="tabs" role="tablist" aria-label="숙성도 영역">%s</div>' % "".join(
        '<button role="tab" data-t="%s" aria-selected="%s" aria-controls="t-%s">%s%s</button>'
        % (k, "true" if i == 0 else "false", k, esc(nm), "<i>%s</i>" % esc(sub) if sub else "")
        for i, (k, nm, sub, _) in enumerate(tabs))
    panels = "".join('<section role="tabpanel" id="t-%s"%s>%s</section>'
                     % (k, "" if i == 0 else " hidden", body) for i, (k, _, _, body) in enumerate(tabs))
    allg = sum(total_score(a)[0] for a in ls)
    allt = sum(total_score(a)[1] for a in ls)
    head = ('<div class="eyebrow">Service Maturity</div><h1>서비스 숙성도</h1>'
            '<p>앱 %d개가 ‘출시한 앱’을 넘어 ‘운영하는 서비스’로 얼마나 갖춰졌는지 기능별로 나눠 봤습니다. '
            '어느 앱이 무엇을 지원하고 무엇이 아직 비어 있는지 탭마다 볼 수 있습니다. '
            '지금 전체로는 확인한 항목의 %d%%를 갖췄습니다.</p>' % (n, round(100 * allg / allt) if allt else 0))
    return page("서비스 숙성도 — 리이오의 앱 포트폴리오",
                "앱 %d개의 국가별 언어·지원 페이지·피드백 수집·운영·사용 경험·기기 지원 현황을 기능별로 정리했습니다." % n,
                {"head": head, "main": bar + panels}, "maturity", MAT_CSS, MAT_JS)


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
        '<p>국가별 언어·지원 페이지·피드백 수집·운영·사용 경험·기기를 앱마다 무엇을 갖췄는지 '
        '기능별 탭으로 보여 줍니다.</p></a>'
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
        '<a class="ov" href="%(site)slifecycle.html"><b>제품 여정</b><p>수명주기 5단계 × 글로벌 지원 공개판. '
        '재생성: <code>build-portfolio-hub.py</code></p></a>'
        '<a class="ov" href="%(site)smaturity.html"><b>서비스 숙성도</b><p>기능별 탭 공개판. '
        '재수집: <code>sync-service-maturity.py</code> → 재생성: <code>build-portfolio-hub.py</code></p></a>'
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
        (os.path.join(DOCS, "maturity.html"), maturity_page(apps), "공개"),
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
