#!/usr/bin/env python3
"""
앱이 사람이라면 — 앱들이 앱이 아니라 사람 · 도구였다면 누구일지 소개하는 페이지.

  docs/personas.html   공개 (GitHub Pages)

· 내용: scripts/personas.json (앱마다 kind = person | tool, who, line, says) — 손으로 쓴다.
· 순서: 제품 여정 단계가 높은 앱부터, 같은 단계는 이름순.
· 폐기 앱은 넣지 않는다 (build-portfolio-hub.py 공개 규칙). 소개가 없는 앱은 빌드 때 알려 준다.
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("hub", os.path.join(HERE, "build-portfolio-hub.py"))
hub = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hub)

OUT = os.path.join(hub.DOCS, "personas.html")
SRC = os.path.join(HERE, "personas.json")
esc = hub.esc

KIND = {"person": "사람", "tool": "도구"}

CSS = """
  .filters{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:22px}
  .filters button{font:inherit;font-size:.9rem;font-weight:700;cursor:pointer;color:var(--text);
    background:var(--card);border:1px solid var(--border);padding:7px 15px;border-radius:999px}
  .filters button.on{background:linear-gradient(120deg,var(--accent),var(--accent-2));color:#fff;border-color:transparent}
  .filters .n{opacity:.75;margin-left:4px;font-weight:600}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:14px}
  .pc{display:flex;flex-direction:column;gap:10px;background:var(--card);border:1px solid var(--border);
    border-radius:16px;padding:18px 18px 16px;border-top:3px solid var(--c)}
  .pc[data-kind=person]{--c:var(--accent-2)}
  .pc[data-kind=tool]{--c:var(--warn)}
  .pc .top{display:flex;align-items:center;gap:10px}
  .pc .ic{width:40px;height:40px;border-radius:10px;flex:none;object-fit:cover;
    background:var(--bg-soft);border:1px solid var(--border)}
  .pc .ic.fb{display:inline-grid;place-items:center;font-size:1rem;font-weight:800;color:var(--muted)}
  .pc .app{font-size:.95rem;font-weight:700;color:var(--text);text-decoration:none}
  .pc .app:hover{color:var(--accent)}
  .pc .kind{margin-left:auto;font-size:.85rem;font-weight:800;color:var(--c);
    border:1px solid var(--c);padding:1px 10px;border-radius:999px;white-space:nowrap}
  .pc h3{font-size:1.15rem;line-height:1.4;letter-spacing:-.01em;word-break:keep-all}
  .pc p{font-size:1rem;color:var(--muted);word-break:keep-all}
  .pc blockquote{margin-top:auto;font-size:1rem;font-weight:600;color:var(--text);word-break:keep-all;
    background:var(--bg-soft);border-left:3px solid var(--c);border-radius:8px;padding:9px 12px}
  .pc blockquote::before{content:"“"}
  .pc blockquote::after{content:"”"}
  @media(max-width:560px){.grid{grid-template-columns:1fr}}
"""

JS = """
<script>
(function(){
  var bs = document.querySelectorAll('.filters button'), cs = document.querySelectorAll('.pc');
  bs.forEach(function(b){ b.addEventListener('click', function(){
    bs.forEach(function(x){ x.classList.toggle('on', x === b); });
    var k = b.getAttribute('data-k');
    cs.forEach(function(c){ c.hidden = k !== 'all' && c.getAttribute('data-kind') !== k; });
  }); });
})();
</script>
"""


def render(apps, personas):
    ls = hub.live(apps)
    ls.sort(key=lambda a: (-((a.get("lifecycle") or {}).get("stage") or 0), a.get("name") or a["_slug"]))
    cards, missing, count = [], [], {"person": 0, "tool": 0}
    for a in ls:
        p = personas.get(a["_slug"])
        if not p:
            missing.append(a["_slug"])
            continue
        count[p["kind"]] += 1
        cards.append(
            '<article class="pc" data-kind="%(k)s"><div class="top">%(icon)s'
            '<a class="app" href="%(href)s">%(name)s</a><span class="kind">%(kk)s</span></div>'
            '<h3>%(who)s</h3><p>%(line)s</p><blockquote>%(says)s</blockquote></article>'
            % {"k": p["kind"], "icon": hub.icon_img(a), "href": hub.intro_link(a),
               "name": esc(a.get("name") or a["_slug"]), "kk": KIND[p["kind"]],
               "who": esc(p["who"]), "line": esc(p["line"]), "says": esc(p["says"])})
    head = ('<div class="eyebrow">If Apps Were People</div><h1>앱이 사람이라면</h1>'
            '<p>앱 %d개가 앱이 아니라 사람이나 도구였다면 누구였을지 소개합니다. '
            '두번알림은 내가 발표할 때 끝나는 시간을 놓치지 않게 몇 분 남았는지 알려 주는 사람입니다.</p>'
            % len(cards))
    filters = ('<div class="filters"><button class="on" data-k="all">전체<span class="n">%d</span></button>'
               '<button data-k="person">사람<span class="n">%d</span></button>'
               '<button data-k="tool">도구<span class="n">%d</span></button></div>'
               % (len(cards), count["person"], count["tool"]))
    main = filters + '<div class="grid">%s</div>' % "".join(cards)
    html = hub.page("앱이 사람이라면 — 리이오의 앱 포트폴리오",
                    "앱 %d개가 사람이나 도구였다면 누구였을지 소개하는 페이지" % len(cards),
                    {"head": head, "main": main}, "persona", CSS, JS)
    return html, missing


def main():
    apps = hub.load_apps()
    personas = json.load(open(SRC, encoding="utf-8")).get("apps", {})
    html, missing = render(apps, personas)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("  [공개] %s" % os.path.relpath(OUT, hub.ROOT))
    if missing:
        print("  ⚠️ 소개가 없는 앱 %d개: %s — scripts/personas.json 에 추가" % (len(missing), ", ".join(missing)))


if __name__ == "__main__":
    main()
