#!/usr/bin/env python3
"""포트폴리오 허브 페이지 생성 — 흩어진 페이지를 한 곳에서 찾는 색인.

사용법:
  python3 scripts/build-portfolio-hub.py

출력:
  reports/portfolio-hub.html   전체 색인 (로컬 전용·비배포)

데이터 출처:
  scripts/hub-links.json                     수동 관리 링크(개요 페이지·아티팩트)
  Data/apps/*.json 의 supportUrl             앱별 지원·랜딩 페이지 (자동 수집)
  marketing/apps/*.md, docs/*.md             제작물·가이드 문서 (자동 집계)

내부 리포트로 링크하므로 배포하지 않는다. reports/ 는 .gitignore 대상.
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

# 지원 페이지 호스트 → 표시 이름·색. 한 앱의 지원 페이지가 어디 살고 있는지 한눈에 보이게 한다.
HOSTS = {
    "m1zz.github.io": ("GitHub Pages", "#3a7ae8"),
    "leeo75.notion.site": ("Notion", "#8a7cf8"),
    "www.notion.so": ("Notion", "#8a7cf8"),
    "dev200ok.blogspot.com": ("Blogspot", "#d6a01e"),
    "www.blogger.com": ("Blogspot", "#d6a01e"),
    "developeracademy-postech.github.io": ("POSTECH Pages", "#1fa878"),
}
LC = {3: ("3 PMF", "#1fa878"), 2: ("2 PSF", "#3a7ae8"), 1: ("1 Pre-MVP", "#8a90a0"),
      0: ("폐기", "#8a90a0")}
TIER = {"A": "개선 중", "B": "소강", "C": "정지"}


def esc(s):
    return html.escape(str(s or ""), quote=True)


def load_apps():
    out = []
    for f in sorted(glob.glob(os.path.join(APPS, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        d["_slug"] = os.path.basename(f)[:-5]
        out.append(d)
    return out


def host_of(url):
    net = urlparse(url).netloc
    return HOSTS.get(net, (net or "기타", "#8a90a0"))


def lc_badge(app):
    lc = app.get("lifecycle") or {}
    st = lc.get("stage", 1)
    label, color = LC.get(st, ("—", "#8a90a0"))
    tier = lc.get("tier")
    if tier:
        label = "2-%s %s" % (tier, TIER[tier])
    return ('<span class="lcb" style="--c:%s" title="%s">%s</span>'
            % (color, esc(lc.get("basis", "")), esc(label)))


def overview_cards(links):
    out = []
    for it in links:
        url, local = it.get("url", ""), it.get("local", "")
        href = url or ("file://" + os.path.join(ROOT, local) if local else "")
        kind = it.get("kind", "")
        kc = {"공개": "k-pub", "내부": "k-int", "아티팩트": "k-art", "레거시": "k-old"}.get(kind, "")
        sub = []
        if url and local:
            sub.append('<a class="alt" href="file://%s">로컬 파일 열기</a>'
                       % esc(os.path.join(ROOT, local)))
        if local:
            sub.append('<code>%s</code>' % esc(local))
        if it.get("auto"):
            sub.append('<span class="auto">↻ <code>%s</code> 로 재생성</span>' % esc(it["auto"]))
        stale = ('<div class="stale">⚠ %s</div>' % esc(it["stale"])) if it.get("stale") else ""
        out.append(
            '<a class="ov %s" href="%s"><div class="ovh"><b>%s</b><span class="kind %s">%s</span></div>'
            '<p>%s</p>%s<div class="ovm">%s</div></a>'
            % ("dim" if kind == "레거시" else "", esc(href), esc(it["title"]), kc, esc(kind),
               esc(it.get("desc", "")), stale, " · ".join(sub)))
    return "".join(out)


def support_section(apps):
    live = [a for a in apps if (a.get("lifecycle") or {}).get("stage") != 0 and a.get("supportUrl")]
    groups = {}
    for a in live:
        name, color = host_of(a["supportUrl"])
        groups.setdefault((name, color), []).append(a)
    blocks = []
    for (name, color), items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        rows = "".join(
            '<a class="sup" href="%s"><span class="sn">%s</span>%s'
            '<span class="su">%s</span></a>'
            % (esc(a["supportUrl"]), esc(a["name"]), lc_badge(a),
               esc(urlparse(a["supportUrl"]).path or "/"))
            for a in sorted(items, key=lambda a: a["name"])
        )
        blocks.append('<div class="hostblk"><div class="hosth" style="--c:%s">%s'
                      '<span class="hc">%d</span></div><div class="suplist">%s</div></div>'
                      % (color, esc(name), len(items), rows))
    return "".join(blocks), len(live), len(groups)


def artifact_section(groups, by_slug):
    out = []
    for g in groups:
        slug = g.get("app") or ""
        app = by_slug.get(slug)
        title = ("%s 관련" % app["name"]) if app else "그 외 · 앱 미지정"
        rows = "".join(
            '<a class="art" href="%s"><span class="at">%s</span><span class="ad">%s</span></a>'
            % (esc(i["u"]), esc(i["t"]), esc(i.get("d", "")))
            for i in g["items"]
        )
        out.append('<div class="artblk"><div class="arth">%s<span class="hc">%d</span></div>'
                   '<div class="artlist">%s</div></div>'
                   % (esc(title), len(g["items"]), rows))
    return "".join(out)


def asset_section():
    kits = sorted(os.path.basename(f)[:-3] for f in glob.glob(os.path.join(ROOT, "marketing/apps/*.md")))
    docs = sorted(os.path.basename(f) for f in glob.glob(os.path.join(ROOT, "docs/*.md")))
    shots = sorted(os.path.basename(f) for f in glob.glob(os.path.join(ROOT, "docs/screenshots/*.png")))
    def chips(items, base):
        return "".join('<a class="chip" href="file://%s">%s</a>'
                       % (esc(os.path.join(ROOT, base, i)), esc(i)) for i in items)
    return (
        '<div class="assetblk"><div class="arth">마케팅 킷<span class="hc">%d</span></div>'
        '<p class="note">앱별 콘텐츠 세트. <b>제작만 되어 있고 발행되지 않았다</b> — 실제 게시가 4단계(Growth) 진입 조건.</p>'
        '<div class="chips">%s</div></div>'
        '<div class="assetblk"><div class="arth">운영 가이드<span class="hc">%d</span></div>'
        '<div class="chips">%s</div></div>'
        '<div class="assetblk"><div class="arth">쇼케이스 스크린샷<span class="hc">%d</span></div>'
        '<div class="chips">%s</div></div>'
        % (len(kits), chips([k + ".md" for k in kits], "marketing/apps"),
           len(docs), chips(docs, "docs"),
           len(shots), chips(shots, "docs/screenshots"))
    )


CSS = """
:root{--bg:#0f1116;--card:#171a21;--ink:#e8eaf0;--muted:#8a90a0;--line:#262a34;
  --accent:#3a7ae8;--ok:#1fa878;--mid:#d6a01e;--no:#d64a40}
html[data-theme=light]{--bg:#f6f7f9;--card:#fff;--ink:#1c2030;--muted:#6b7280;--line:#e3e6ec}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.6 -apple-system,BlinkMacSystemFont,
  'Pretendard','Apple SD Gothic Neo',sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:40px 22px 80px}
.toggle{position:fixed;top:16px;right:16px;z-index:9;background:var(--card);color:var(--ink);
  border:1px solid var(--line);border-radius:8px;padding:7px 12px;font-size:12.5px;cursor:pointer}
header{margin-bottom:34px}
.eyebrow{font-size:11.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:600}
h1{margin:8px 0 6px;font-size:29px;letter-spacing:-.02em}
.sub{color:var(--muted);font-size:13.5px}
.local-note{margin-top:13px;padding:11px 14px;border-radius:9px;font-size:12.5px;
  background:rgba(58,122,232,.09);border:1px solid rgba(58,122,232,.25)}
section{margin-top:44px}
h2{font-size:17px;margin:0 0 4px;display:flex;align-items:center;gap:9px}
.hn{display:inline-grid;place-items:center;width:25px;height:25px;border-radius:7px;
  background:var(--accent);color:#fff;font-size:13px;font-weight:700}
.lead{color:var(--muted);font-size:12.5px;margin:0 0 16px}
.ovgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:13px}
.ov{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:16px 17px;text-decoration:none;color:inherit;transition:.14s}
.ov:hover{border-color:var(--accent);transform:translateY(-2px)}
.ov.dim{opacity:.55}
.ovh{display:flex;align-items:center;gap:8px;margin-bottom:7px}
.ovh b{font-size:14.5px}
.kind{font-size:10.5px;font-weight:700;padding:2px 7px;border-radius:5px;margin-left:auto;white-space:nowrap}
.k-pub{background:rgba(31,168,120,.16);color:var(--ok)}
.k-int{background:rgba(58,122,232,.16);color:var(--accent)}
.k-art{background:rgba(138,124,248,.16);color:#8a7cf8}
.k-old{background:rgba(127,127,127,.14);color:var(--muted)}
.ov p{margin:0 0 9px;font-size:12.5px;color:var(--muted);line-height:1.55}
.ovm{font-size:11.5px;color:var(--muted);display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.ovm code{background:rgba(127,127,127,.12);padding:1px 5px;border-radius:4px;font-size:11px}
.alt{color:var(--accent);text-decoration:none;border-bottom:1px dotted}
.stale{font-size:11.5px;color:var(--mid);margin-bottom:8px}
.hostblk,.artblk,.assetblk{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:15px 17px;margin-bottom:12px}
.hosth,.arth{font-size:13.5px;font-weight:700;display:flex;align-items:center;gap:8px;
  margin-bottom:11px;padding-bottom:9px;border-bottom:1px solid var(--line)}
.hosth::before{content:"";width:9px;height:9px;border-radius:3px;background:var(--c)}
.hc{margin-left:auto;font-size:11.5px;font-weight:600;color:var(--muted);
  background:rgba(127,127,127,.12);padding:2px 8px;border-radius:11px}
.suplist{display:grid;grid-template-columns:repeat(auto-fill,minmax(258px,1fr));gap:7px}
.sup{display:flex;align-items:center;gap:7px;padding:7px 9px;border-radius:7px;
  text-decoration:none;color:inherit;font-size:12.5px;transition:.12s}
.sup:hover{background:rgba(58,122,232,.10)}
.sn{font-weight:600;white-space:nowrap}
.su{margin-left:auto;font-size:10.5px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap;max-width:118px;direction:rtl;text-align:right}
.lcb{font-size:10px;font-weight:700;padding:1.5px 6px;border-radius:5px;cursor:help;
  color:var(--c);background:color-mix(in srgb,var(--c) 15%,transparent);white-space:nowrap}
.artlist{display:grid;gap:6px}
.art{display:flex;align-items:baseline;gap:10px;padding:7px 9px;border-radius:7px;
  text-decoration:none;color:inherit;font-size:12.5px}
.art:hover{background:rgba(138,124,248,.11)}
.at{font-weight:600}
.ad{margin-left:auto;font-size:11px;color:var(--muted)}
.note{margin:-3px 0 11px;font-size:12px;color:var(--muted)}
.chips{display:flex;flex-wrap:wrap;gap:5px}
.chip{font-size:11.5px;padding:3px 8px;border-radius:6px;border:1px solid var(--line);
  text-decoration:none;color:var(--muted);background:rgba(127,127,127,.05)}
.chip:hover{border-color:var(--accent);color:var(--accent)}
footer{margin-top:56px;padding-top:20px;border-top:1px solid var(--line);
  font-size:11.5px;color:var(--muted);line-height:1.8}
footer code{background:rgba(127,127,127,.12);padding:1px 5px;border-radius:4px}
@media(max-width:640px){.wrap{padding:26px 15px 60px}h1{font-size:23px}
  .suplist{grid-template-columns:1fr}}
"""


def main():
    links = json.load(open(os.path.join(ROOT, "scripts/hub-links.json"), encoding="utf-8"))
    apps = load_apps()
    by_slug = {a["_slug"]: a for a in apps}
    sup_html, n_sup, n_host = support_section(apps)
    art_html = artifact_section(links["artifacts"], by_slug)
    n_art = sum(len(g["items"]) for g in links["artifacts"])
    today = date.today().isoformat()

    body = """<div class="wrap">
<button class="toggle" onclick="var r=document.documentElement;r.setAttribute('data-theme',r.getAttribute('data-theme')==='dark'?'light':'dark')">◐ 테마</button>
<header>
  <div class="eyebrow">Portfolio Hub · 내부용 (비배포)</div>
  <h1>앱 포트폴리오 허브</h1>
  <div class="sub">흩어져 있는 포트폴리오 페이지를 한 곳에서 찾는 색인 · 기준일 %(today)s</div>
  <div class="local-note">🔒 내부 리포트로 링크하므로 배포하지 않는다(<code>reports/</code>는 gitignore 대상).
  로컬 파일 링크는 이 컴퓨터에서만 열린다. 개요 %(n_ov)d · 지원 페이지 %(n_sup)d(%(n_host)d개 호스트) · 아티팩트 %(n_art)d.</div>
</header>

<section>
  <h2><span class="hn">1</span>포트폴리오 전체 보기</h2>
  <p class="lead">포트폴리오를 통째로 보는 페이지들. 공개용과 내부용이 섞여 있으니 대외 공유 시 <b>공개</b> 표시만 쓸 것.</p>
  <div class="ovgrid">%(ov)s</div>
</section>

<section>
  <h2><span class="hn">2</span>앱별 지원 · 랜딩 페이지 <span style="font-weight:400;color:var(--muted);font-size:12px">· %(n_sup)d개 · 호스트 %(n_host)d곳에 분산</span></h2>
  <p class="lead">App Store에 등록된 지원 URL. 호스트가 나뉘어 있어 한 곳에서 일괄 수정하기 어렵다 — 이 목록이 그 지도다. 앱 이름 옆 배지는 수명주기 단계(호버 시 판정 근거).</p>
  %(sup)s
</section>

<section>
  <h2><span class="hn">3</span>디자인 · QA 아티팩트 <span style="font-weight:400;color:var(--muted);font-size:12px">· %(n_art)d개</span></h2>
  <p class="lead">Claude 아티팩트로 만든 시안·실험·체크리스트. 기본 비공개이며 링크를 아는 사람만 열 수 있다.</p>
  %(art)s
</section>

<section>
  <h2><span class="hn">4</span>제작물 · 문서</h2>
  <p class="lead">레포 안에 있는 자산. 클릭하면 로컬 파일이 열린다.</p>
  %(asset)s
</section>

<footer>
생성: <code>scripts/build-portfolio-hub.py</code> · 기준일 %(today)s · 로컬 전용(비배포)<br>
링크 원본: <code>scripts/hub-links.json</code>(수동) + <code>Data/apps/*.json</code>의 <code>supportUrl</code>(자동)<br>
새 아티팩트·페이지를 만들면 <code>hub-links.json</code>에 추가하고 이 스크립트를 다시 실행할 것.
</footer>
</div>""" % {
        "today": today, "ov": overview_cards(links["overview"]), "sup": sup_html,
        "art": art_html, "asset": asset_section(), "n_sup": n_sup, "n_host": n_host,
        "n_art": n_art, "n_ov": len(links["overview"]),
    }

    out = ('<!doctype html><html lang="ko" data-theme="dark"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1">'
           '<title>앱 포트폴리오 허브 · %s</title><style>%s</style></head><body>\n%s\n</body></html>'
           % (today, CSS, body))

    os.makedirs(REPORTS, exist_ok=True)
    path = os.path.join(REPORTS, "portfolio-hub.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(out)
    print("개요 %d · 지원페이지 %d(호스트 %d) · 아티팩트 %d"
          % (len(links["overview"]), n_sup, n_host, n_art))
    print("→ %s" % path)


if __name__ == "__main__":
    main()
