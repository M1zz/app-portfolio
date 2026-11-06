#!/usr/bin/env python3
"""
서비스 점검표 — 모든 앱이 실제로 제대로 동작하는지 손으로 확인하는 순서와 기록장.

  docs/service-check.html   공개 (GitHub Pages)

· 순서: 사람과 돈이 걸린 앱부터 (제품 여정 단계 → 외부 평점 수 → 돈 받는 앱 → 최근 업데이트).
· 항목: 앱마다 serviceMaturity 가 '있다'고 판정한 기능만 점검 항목으로 만든다.
  각 항목은 QuestLoop 의 가설 문장처럼 '해 볼 것 → 기대'로 적는다. 기대대로 안 되면 그게 고칠 일.
· 기록: 항목마다 잘 됨 · 불편함 · 안 됨 · 해당 없음. 브라우저(localStorage)에 남고,
  JSON 으로 내보내기 · 가져오기로 다른 기기와 옮긴다.

공개 규칙(build-portfolio-hub.py 머리말)을 따른다 — 폐기 앱 · 하위 등급 · 수익 숫자 · 로컬 경로는 넣지 않는다.
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("hub", os.path.join(HERE, "build-portfolio-hub.py"))
hub = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hub)

OUT = os.path.join(hub.DOCS, "service-check.html")
SHOWCASE = os.path.join(HERE, "showcase-content.json")

# 무게: 3 = 이게 안 되면 서비스가 아님, 2 = 돈 · 데이터가 걸림, 1 = 있으면 좋은 것
# (key, 무게, 묶음, 이름, 해 볼 것, 기대, 조건)
def _sm(app, area, key):
    return ((app.get("serviceMaturity") or {}).get(area) or {}).get(key) is True


def _paid(app):
    return "paid" in ((app.get("price") or {}).get("pricingModel") or "")


def checks_for(app, story):
    sm = app.get("serviceMaturity") or {}
    langs = (app.get("globalReach") or {}).get("languageCount") or 1
    solution = (story or {}).get("solution") or ((app.get("vision") or {}).get("tagline") or "")
    out = []

    def add(key, w, group, name, how, expect):
        out.append({"k": key, "w": w, "g": group, "n": name, "h": how, "e": expect})

    add("store", 3, "설치", "App Store 에서 받기",
        "App Store 링크를 열어 설치한다" + (" (유료라면 결제까지)" if _paid(app) else ""),
        "페이지가 열리고, 스크린샷 · 설명이 지금 앱과 맞고, 설치가 끝난다")
    add("launch", 3, "설치", "처음 실행",
        "앱을 지운 뒤 새로 설치해 처음 연다" + (" — 온보딩을 끝까지 넘긴다" if _sm(app, "ux", "onboarding") else ""),
        "멈춤 · 빈 화면 · 튕김 없이 첫 화면까지 간다")
    add("core", 3, "핵심", "핵심 기능 한 바퀴",
        solution or "앱이 약속하는 일을 처음부터 끝까지 한 번 해 본다",
        "처음 쓰는 사람이 설명 없이 끝까지 해내고, 결과가 맞다")
    add("persist", 3, "핵심", "껐다 켜도 남는가",
        "무언가 만들거나 바꾼 뒤 앱을 완전히 종료하고 다시 연다",
        "만든 것 · 설정이 그대로 있다")
    if _sm(app, "ux", "cloudSync"):
        add("sync", 2, "데이터", "iCloud 동기화",
            "기기 두 대(또는 지우고 다시 설치)에서 같은 Apple ID 로 연다",
            "한쪽에서 만든 것이 다른 쪽에 나타난다 · 중복이 생기지 않는다")
    if _sm(app, "ux", "backup"):
        add("backup", 2, "데이터", "백업 · 복원",
            "백업 파일을 만들고, 지운 뒤 그 파일로 되살린다",
            "빠짐없이 돌아온다")
    if _sm(app, "money", "paywall") or _sm(app, "money", "subscription"):
        add("paywall", 2, "결제", "페이월 열기",
            "무료 한도에 닿거나 Pro 버튼을 눌러 결제 화면을 연다",
            "가격이 현지 통화로 뜨고 (로딩만 돌지 않고), 닫기 버튼이 있다")
        add("buy", 3, "결제", "구입 (샌드박스 · TestFlight)",
            "가장 싼 상품을 실제로 산다",
            "결제 직후 잠긴 기능이 바로 풀리고, 앱을 다시 켜도 풀려 있다")
    if _sm(app, "money", "restore"):
        add("restore", 2, "결제", "구입 복원",
            "지우고 다시 설치한 뒤 '구입 복원'을 누른다",
            "산 것이 돌아온다 · 안 산 계정은 '복원할 것 없음'을 알려 준다")
    if _sm(app, "money", "trial"):
        add("trial", 2, "결제", "무료 체험",
            "체험을 시작하고 설정 → 구독에서 확인한다",
            "체험 기간 · 끝나는 날이 맞게 보인다")
    if _sm(app, "money", "tipJar"):
        add("tip", 1, "결제", "후원(팁)",
            "설정의 후원 줄을 눌러 가장 작은 팁을 낸다",
            "상품 가격이 뜨고, 낸 뒤 고맙다는 화면이 나온다")
    if _sm(app, "more", "notifications"):
        add("notify", 2, "곁기능", "알림",
            "알림을 1~2분 뒤로 맞추고 앱을 닫는다",
            "제 시간에 오고, 누르면 맞는 화면으로 간다")
    if _sm(app, "ux", "widgets"):
        add("widget", 1, "곁기능", "위젯",
            "홈 화면에 위젯을 올리고 앱에서 내용을 바꾼다",
            "위젯이 비어 있지 않고, 바뀐 내용이 곧 반영된다")
    if _sm(app, "ux", "shortcuts"):
        add("shortcut", 1, "곁기능", "단축어 · Siri",
            "단축어 앱에서 이 앱의 동작을 찾아 실행한다",
            "동작이 보이고, 실행하면 결과가 맞다")
    devices = sm.get("devices") or {}
    if devices.get("ipad"):
        add("ipad", 1, "기기", "iPad",
            "iPad 에서 가로 · 세로 · 화면 분할로 연다",
            "잘리거나 늘어진 화면 없이 쓸 만하다")
    if devices.get("mac") or devices.get("_macViaDesignedForIPad"):
        add("mac", 1, "기기", "Mac",
            "Mac 에서 설치해 핵심 기능을 한 번 해 본다",
            "창 크기를 바꿔도 깨지지 않고 키보드 · 마우스로 된다")
    if devices.get("watch"):
        add("watch", 1, "기기", "Apple Watch",
            "워치 앱을 열어 핵심 동작을 한 번 한다",
            "iPhone 과 내용이 맞는다")
    if langs > 1:
        add("lang", 1, "언어", "영어로 보기",
            "설정 → 앱 → 언어를 English 로 바꿔 연다",
            "한국어가 섞여 나오지 않고, 글자가 잘리지 않는다")
    if _sm(app, "feedback", "inAppFeedback") or _sm(app, "feedback", "mailContact"):
        add("feedback", 1, "소통", "피드백 보내기",
            "앱 안의 피드백 · 문의 버튼으로 시험 메시지를 보낸다",
            "보냈다는 표시가 나오고, 내 쪽(피드백 허브 · 메일)에 도착한다")
    if app.get("supportUrl"):
        ok = (sm.get("support") or {}).get("reachable")
        add("support", 1, "소통", "지원 페이지",
            "App Store 의 '지원' 링크를 연다",
            "페이지가 열리고 연락 방법 · 개인정보 처리방침이 있다"
            + ("" if ok is not False else " (자동 점검에서 안 열렸음)"))
    return out


def order_key(app):
    lc = app.get("lifecycle") or {}
    money = 1 if (_paid(app) or _sm(app, "money", "paywall")) else 0
    return (-(lc.get("stage") or 0), -(lc.get("ratingCount") or 0), -money,
            -int((lc.get("updatedAt") or "0").replace("-", "") or 0), app.get("name") or "")


def tier_of(app):
    lc = app.get("lifecycle") or {}
    st = lc.get("stage") or 0
    if st >= 3:
        return 1
    if (lc.get("ratingCount") or 0) > 0 or _paid(app) or _sm(app, "money", "paywall"):
        return 2
    if st == 2:
        return 3
    return 4


TIERS = {
    1: ("먼저", "넓히는 중 · PMF 탐색 앱 — 사람이 가장 많이 들어오는 곳. 여기서 깨지면 손해가 가장 큽니다."),
    2: ("다음", "평점이 달렸거나 돈을 받는 앱 — 산 사람 · 써 본 사람이 이미 있습니다."),
    3: ("그다음", "문제-해결 맞춤(PS Fit) 단계의 무료 앱."),
    4: ("마지막", "아직 다듬는 중(Pre-MVP)인 앱 — 핵심 기능 한 바퀴만 봐도 됩니다."),
}


CSS = """
  .intro{font-size:1rem;color:var(--muted);max-width:760px}
  .how{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;margin:18px 0 6px}
  .how div{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 14px;font-size:1rem}
  .how b{display:block;margin-bottom:2px}
  .sum{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--border);
    padding:12px 0;margin:18px 0 8px;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;font-size:1rem}
  .sum .big{font-size:1.25rem;font-weight:800}
  .sum .bar{flex:1 1 220px;height:10px;border-radius:99px;background:var(--bg-soft);overflow:hidden;display:flex}
  .sum .bar i{display:block;height:100%}
  .tools{display:flex;flex-wrap:wrap;gap:8px}
  .tools button,.tools select{font:inherit;font-size:1rem;background:var(--card);color:var(--text);
    border:1px solid var(--border);border-radius:999px;padding:6px 13px;cursor:pointer}
  .tools button:hover{border-color:var(--accent)}
  .tier{margin:30px 0 8px}
  .tier h2{font-size:1.3rem;display:flex;gap:10px;align-items:baseline}
  .tier h2 .n{font-size:1rem;color:var(--muted);font-weight:600}
  .tier p{color:var(--muted);font-size:1rem}
  details.app{background:var(--card);border:1px solid var(--border);border-radius:14px;margin:10px 0;overflow:hidden}
  details.app[open]{border-color:var(--accent)}
  details.app>summary{list-style:none;cursor:pointer;display:grid;
    grid-template-columns:34px 44px 1fr auto;gap:12px;align-items:center;padding:12px 16px}
  details.app>summary::-webkit-details-marker{display:none}
  .rank{font-weight:800;color:var(--muted);text-align:right;font-size:1rem}
  .ic{width:44px;height:44px;border-radius:11px;display:block}
  .ic.fb{display:flex;align-items:center;justify-content:center;background:var(--bg-soft);font-weight:800}
  .nm b{font-size:1.08rem}
  .nm .meta{font-size:1rem;color:var(--muted)}
  .score{text-align:right;min-width:120px}
  .score .pct{font-size:1.2rem;font-weight:800}
  .score .st{font-size:1rem;color:var(--muted)}
  .mini{display:flex;gap:2px;margin-top:4px;justify-content:flex-end}
  .mini i{width:9px;height:9px;border-radius:2px;background:var(--border)}
  .body{padding:4px 16px 16px;border-top:1px solid var(--border)}
  .links{display:flex;flex-wrap:wrap;gap:12px;margin:10px 0;font-size:1rem}
  .links a{color:var(--accent)}
  .grp{margin-top:14px;font-weight:700;color:var(--muted);font-size:1rem}
  .ck{display:grid;grid-template-columns:1fr auto;gap:6px 14px;padding:10px 0;border-top:1px dashed var(--border)}
  .ck:first-of-type{border-top:0}
  .ck .t{font-size:1.02rem;font-weight:700}
  .ck .t .w{font-size:1rem;font-weight:600;color:var(--warn);margin-left:6px}
  .ck .d{font-size:1rem;color:var(--muted);line-height:1.5}
  .ck .d span{color:var(--text)}
  .seg{display:flex;gap:4px;flex-wrap:wrap;justify-content:flex-end;align-self:start}
  .seg button{font:inherit;font-size:1rem;padding:5px 11px;border-radius:999px;cursor:pointer;
    border:1px solid var(--border);background:var(--bg-soft);color:var(--muted)}
  .seg button.on[data-v="2"]{background:var(--ok);border-color:var(--ok);color:#fff}
  .seg button.on[data-v="1"]{background:var(--warn);border-color:var(--warn);color:#111}
  .seg button.on[data-v="0"]{background:#e5534b;border-color:#e5534b;color:#fff}
  .seg button.on[data-v="na"]{background:var(--border);color:var(--text)}
  .ck textarea{grid-column:1/-1;display:none;font:inherit;font-size:1rem;width:100%;min-height:52px;
    background:var(--bg-soft);color:var(--text);border:1px solid var(--border);border-radius:10px;padding:8px 10px}
  .ck.note textarea,.ck textarea.has{display:block}
  .appnote{width:100%;margin-top:12px;font:inherit;font-size:1rem;min-height:60px;background:var(--bg-soft);
    color:var(--text);border:1px solid var(--border);border-radius:10px;padding:8px 10px}
  .stamp{font-size:1rem;color:var(--muted);margin-top:6px}
  .hide{display:none!important}
  @media(max-width:620px){details.app>summary{grid-template-columns:44px 1fr;}
    .rank{display:none}.score{grid-column:1/-1;text-align:left}.mini{justify-content:flex-start}
    .ck{grid-template-columns:1fr}.seg{justify-content:flex-start}}
"""

JS = r"""
<script>
const DATA = __DATA__;
const KEY = 'service-check-v1';
let S = {};
try { S = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { S = {}; }
const save = () => localStorage.setItem(KEY, JSON.stringify(S));
const LABEL = {'2':'잘 됨','1':'불편함','0':'안 됨','na':'해당 없음'};
const COLOR = {'2':'var(--ok)','1':'var(--warn)','0':'#e5534b','na':'var(--muted)'};

function appStats(a) {
  const st = S[a.slug] || {};
  let got = 0, max = 0, done = 0, bad = 0, todo = 0;
  a.checks.forEach(c => {
    const v = (st.v || {})[c.k];
    if (v === undefined) { todo++; return; }
    done++;
    if (v === 'na') return;
    max += 2 * c.w; got += Number(v) * c.w;
    if (v === '0') bad++;
  });
  return {got, max, done, bad, todo, pct: max ? Math.round(got / max * 100) : null};
}

function verdict(s, n) {
  if (s.done === 0) return '아직 안 봄';
  if (s.bad) return '안 되는 것 ' + s.bad + '개';
  if (s.todo) return s.done + ' / ' + n + ' 확인';
  return s.pct >= 90 ? '잘 동작' : s.pct >= 60 ? '쓸 만함' : '손볼 곳 많음';
}

function renderApp(a) {
  const s = appStats(a);
  const el = document.getElementById('app-' + a.slug);
  el.querySelector('.pct').textContent = s.pct === null ? '–' : s.pct + '%';
  el.querySelector('.pct').style.color = s.pct === null ? 'var(--muted)' : s.pct >= 90 ? 'var(--ok)' : s.pct >= 60 ? 'var(--warn)' : '#e5534b';
  el.querySelector('.st').textContent = verdict(s, a.checks.length);
  const st = S[a.slug] || {};
  el.querySelector('.mini').innerHTML = a.checks.map(c => {
    const v = (st.v || {})[c.k];
    return '<i title="' + c.n + '" style="background:' + (v === undefined ? 'var(--border)' : COLOR[v]) + '"></i>';
  }).join('');
  el.querySelector('.stamp').textContent = st.at ? '마지막 기록 ' + st.at : '';
  el.dataset.state = s.done === 0 ? 'none' : s.bad ? 'bad' : s.todo ? 'part' : 'done';
}

function renderSum() {
  let apps = 0, checked = 0, full = 0, bad = 0, got = 0, max = 0, cnt = {'2':0,'1':0,'0':0,'na':0}, total = 0;
  DATA.forEach(a => {
    const s = appStats(a); total += a.checks.length;
    if (s.done) checked++;
    if (s.done && !s.todo) full++;
    if (s.bad) bad++;
    got += s.got; max += s.max;
    const st = (S[a.slug] || {}).v || {};
    Object.values(st).forEach(v => cnt[v] = (cnt[v] || 0) + 1);
  });
  document.getElementById('sApps').textContent = full + ' / ' + DATA.length;
  document.getElementById('sBad').textContent = bad;
  document.getElementById('sPct').textContent = max ? Math.round(got / max * 100) + '%' : '–';
  document.getElementById('sBar').innerHTML = ['2','1','0','na'].map(k =>
    '<i style="width:' + (cnt[k] / total * 100) + '%;background:' + COLOR[k] + '" title="' + LABEL[k] + ' ' + cnt[k] + '"></i>').join('');
  document.getElementById('sCnt').textContent = '잘 됨 ' + cnt['2'] + ' · 불편함 ' + cnt['1'] + ' · 안 됨 ' + cnt['0'] + ' · 남은 항목 ' + (total - cnt['2'] - cnt['1'] - cnt['0'] - cnt['na']);
}

function applyFilter() {
  const f = document.getElementById('filter').value;
  document.querySelectorAll('details.app').forEach(el => {
    const s = el.dataset.state;
    const show = f === 'all' || (f === 'todo' && s !== 'done') || (f === 'bad' && s === 'bad') || (f === 'done' && s === 'done');
    el.classList.toggle('hide', !show);
  });
  document.querySelectorAll('.tier').forEach(t => {
    const any = t.querySelectorAll('details.app:not(.hide)').length;
    t.classList.toggle('hide', !any);
  });
}

function today() { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0'); }

document.addEventListener('click', e => {
  const b = e.target.closest('.seg button');
  if (!b) return;
  const ck = b.closest('.ck'), app = b.closest('details.app');
  const slug = app.dataset.slug, k = ck.dataset.k, v = b.dataset.v;
  const st = S[slug] = S[slug] || {v: {}, n: {}};
  st.v = st.v || {};
  if (st.v[k] === v) delete st.v[k]; else st.v[k] = v;
  st.at = today();
  ck.querySelectorAll('.seg button').forEach(x => x.classList.toggle('on', st.v[k] === x.dataset.v));
  ck.classList.toggle('note', st.v[k] === '0' || st.v[k] === '1');
  save(); renderApp(DATA.find(a => a.slug === slug)); renderSum(); applyFilter();
});

document.addEventListener('input', e => {
  const t = e.target; if (t.tagName !== 'TEXTAREA') return;
  const app = t.closest('details.app'), slug = app.dataset.slug;
  const st = S[slug] = S[slug] || {v: {}, n: {}};
  st.n = st.n || {};
  const k = t.dataset.k || '_app';
  if (t.value) st.n[k] = t.value; else delete st.n[k];
  t.classList.toggle('has', !!t.value);
  st.at = today(); save();
});

function restore() {
  DATA.forEach(a => {
    const st = S[a.slug] || {};
    const el = document.getElementById('app-' + a.slug);
    el.querySelectorAll('.ck').forEach(ck => {
      const v = (st.v || {})[ck.dataset.k];
      ck.querySelectorAll('.seg button').forEach(x => x.classList.toggle('on', v === x.dataset.v));
      ck.classList.toggle('note', v === '0' || v === '1');
      const ta = ck.querySelector('textarea'), n = (st.n || {})[ck.dataset.k] || '';
      ta.value = n; ta.classList.toggle('has', !!n);
    });
    el.querySelector('.appnote').value = (st.n || {})._app || '';
    renderApp(a);
  });
  renderSum(); applyFilter();
}

document.getElementById('filter').addEventListener('change', applyFilter);
document.getElementById('next').addEventListener('click', () => {
  const a = DATA.find(a => appStats(a).todo > 0);
  if (!a) { document.getElementById('next').textContent = '모두 확인했어요'; return; }
  document.getElementById('filter').value = 'all'; applyFilter();
  const el = document.getElementById('app-' + a.slug);
  el.open = true; el.scrollIntoView({behavior: 'smooth', block: 'start'});
});
document.getElementById('export').addEventListener('click', () => {
  const blob = new Blob([JSON.stringify({saved: today(), data: S}, null, 2)], {type: 'application/json'});
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
  a.download = 'service-check-' + today() + '.json'; a.click();
});
document.getElementById('import').addEventListener('click', () => document.getElementById('file').click());
document.getElementById('file').addEventListener('change', e => {
  const f = e.target.files[0]; if (!f) return;
  f.text().then(t => { const j = JSON.parse(t); S = j.data || j; save(); restore(); });
});
document.getElementById('reset').addEventListener('click', e => {
  const b = e.currentTarget;
  if (b.dataset.armed) { S = {}; save(); restore(); b.textContent = '기록 비우기'; delete b.dataset.armed; return; }
  b.dataset.armed = 1; b.textContent = '한 번 더 누르면 비웁니다';
  setTimeout(() => { b.textContent = '기록 비우기'; delete b.dataset.armed; }, 3000);
});
restore();
</script>
"""


def render(apps, stories):
    esc = hub.esc
    ordered = sorted(hub.live(apps), key=order_key)
    data = []
    tiers = {}
    for i, a in enumerate(ordered, 1):
        cks = checks_for(a, stories.get(a["_slug"]))
        data.append({"slug": a["_slug"], "checks": [{"k": c["k"], "w": c["w"], "n": c["n"]} for c in cks]})
        lc = a.get("lifecycle") or {}
        meta = [hub.STAGE_SHORT.get(lc.get("stage"), "")]
        if lc.get("ratingCount"):
            meta.append("평점 %d개" % lc["ratingCount"])
        if _paid(a) or _sm(a, "money", "paywall"):
            meta.append("돈 받음")
        if a.get("currentVersion"):
            meta.append("v" + a["currentVersion"])
        meta.append("항목 %d개" % len(cks))
        links = []
        if a.get("appStoreUrl"):
            links.append('<a href="%s" target="_blank" rel="noopener">App Store</a>' % esc(a["appStoreUrl"]))
        if a.get("supportUrl"):
            links.append('<a href="%s" target="_blank" rel="noopener">지원 페이지</a>' % esc(a["supportUrl"]))
        links.append('<a href="maturity.html#todo">숙성도 할 일</a>')
        body, last = [], None
        for c in cks:
            if c["g"] != last:
                body.append('<div class="grp">%s</div>' % esc(c["g"]))
                last = c["g"]
            body.append(
                '<div class="ck" data-k="%s"><div><div class="t">%s%s</div>'
                '<div class="d">해 볼 것 <span>%s</span><br>기대 <span>%s</span></div></div>'
                '<div class="seg"><button data-v="2">잘 됨</button><button data-v="1">불편함</button>'
                '<button data-v="0">안 됨</button><button data-v="na">해당 없음</button></div>'
                '<textarea data-k="%s" placeholder="무엇이 어떻게 안 됐는지 (기기 · iOS 버전 · 재현 순서)"></textarea></div>'
                % (c["k"], esc(c["n"]), '<span class="w">필수</span>' if c["w"] == 3 else "",
                   esc(c["h"]), esc(c["e"]), c["k"]))
        card = (
            '<details class="app" id="app-%(s)s" data-slug="%(s)s"><summary>'
            '<span class="rank">%(i)d</span>%(icon)s'
            '<span class="nm"><b>%(name)s</b><br><span class="meta">%(meta)s</span></span>'
            '<span class="score"><span class="pct">–</span><br><span class="st"></span><span class="mini"></span></span>'
            '</summary><div class="body"><div class="links">%(links)s</div>%(body)s'
            '<textarea class="appnote" placeholder="이 앱 전체 메모"></textarea><div class="stamp"></div></div></details>'
            % {"s": esc(a["_slug"]), "i": i, "icon": hub.icon_img(a), "name": esc(a.get("name") or a["_slug"]),
               "meta": esc(" · ".join(m for m in meta if m)), "links": " ".join(links), "body": "".join(body)})
        tiers.setdefault(tier_of(a), []).append(card)

    n_checks = sum(len(d["checks"]) for d in data)
    head = ('<div class="eyebrow">Service Check</div><h1>서비스 점검표</h1>'
            '<p class="intro">앱 %d개가 실제로 제대로 동작하는지 손으로 확인하는 순서와 기록장입니다. '
            '사람과 돈이 걸린 앱부터 위에 두었고, 앱마다 갖춘 기능만 점검 항목(모두 %d개)으로 만들었습니다.</p>'
            '<div class="how"><div><b>1. 위에서부터</b>순서는 제품 여정 단계 → 외부 평점 수 → 돈을 받는지 → 최근 업데이트.</div>'
            '<div><b>2. 해 보고 기대와 비교</b>항목마다 해 볼 것과 기대가 있습니다. 기대대로 안 되면 그게 고칠 일입니다.</div>'
            '<div><b>3. 네 가지로 기록</b>잘 됨 2점 · 불편함 1점 · 안 됨 0점. 필수 항목은 3배로 셉니다.</div>'
            '<div><b>4. 기록은 이 브라우저에</b>다른 기기로 옮길 땐 내보내기 → 가져오기.</div></div>'
            % (len(data), n_checks))
    sumbar = ('<div class="sum"><span>다 본 앱 <span class="big" id="sApps"></span></span>'
              '<span>안 되는 게 있는 앱 <span class="big" id="sBad" style="color:#e5534b"></span></span>'
              '<span>전체 동작 <span class="big" id="sPct"></span></span>'
              '<span class="bar" id="sBar"></span><span id="sCnt" style="color:var(--muted)"></span>'
              '<span class="tools"><button id="next">다음 점검할 앱</button>'
              '<select id="filter"><option value="all">전체</option><option value="todo">남은 앱</option>'
              '<option value="bad">안 되는 게 있는 앱</option><option value="done">다 본 앱</option></select>'
              '<button id="export">내보내기</button><button id="import">가져오기</button>'
              '<button id="reset">기록 비우기</button>'
              '<input type="file" id="file" accept="application/json" hidden></span></div>')
    main = [sumbar]
    for t in sorted(tiers):
        name, desc = TIERS[t]
        main.append('<section class="tier"><h2>%s<span class="n">%d개</span></h2><p>%s</p>%s</section>'
                    % (name, len(tiers[t]), desc, "".join(tiers[t])))
    js = JS.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    return hub.page("서비스 점검표 — 리이오의 앱 포트폴리오",
                    "앱 %d개가 제대로 동작하는지 우선순위대로 확인하고 기록하는 점검표" % len(data),
                    {"head": head, "main": "".join(main)}, "check", CSS, js)


def main():
    apps = hub.load_apps()
    stories = json.load(open(SHOWCASE, encoding="utf-8")).get("apps", {})
    html = render(apps, stories)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("  [공개] %s" % os.path.relpath(OUT, hub.ROOT))


if __name__ == "__main__":
    main()
