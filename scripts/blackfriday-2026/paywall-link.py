#!/usr/bin/env python3
"""
앱 레포 하나에 '세일 링크(<번들 ID 소문자>://paywall)' 를 받을 준비 중 기계적인 부분을 한다.

  python3 paywall-link.py <레포> <번들 ID> <릴리즈 버전>

  1. LeeoKit 최소 버전을 3.47.0 으로 (pbxproj)
  2. 앱 타겟 Info.plist 의 CFBundleURLTypes 에 스킴을 더한다 (이미 있으면 그대로)
  3. RELEASE_NOTES.md 의 그 버전 절 언어마다 첫 줄로 한 줄을 더한다 (절이 없으면 새로 만든다)
루트 화면에 `.leeoPaywallLink { … }` 를 붙이는 일은 앱마다 달라 손으로 한다.
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LINE = json.load(open(os.path.join(HERE, "release-line.json"), encoding="utf-8"))
LEEOKIT = "3.47.1"
ALIAS = {"en-US": "en", "es-ES": "es", "de-DE": "de", "fr-FR": "fr", "nl-NL": "nl", "no": "nb"}
NAMES = {"ko": "한국어", "en": "English"}
KNAMES = {"한국어": "ko", "English": "en", "영어": "en", "영어(영국)": "en-GB", "중국어 간체": "zh-Hans", "중국어 번체": "zh-Hant",
          "일본어": "ja", "러시아어": "ru", "스페인어": "es", "스페인어(멕시코)": "es-MX", "독일어": "de", "프랑스어": "fr",
          "이탈리아어": "it", "포르투갈어(브라질)": "pt-BR", "포르투갈어(포르투갈)": "pt-PT", "태국어": "th", "베트남어": "vi",
          "체코어": "cs", "덴마크어": "da", "그리스어": "el", "핀란드어": "fi", "인도네시아어": "id", "노르웨이어": "nb",
          "노르웨이어 보크말": "nb", "노르웨이어(보크말)": "nb", "네덜란드어": "nl", "폴란드어": "pl", "스웨덴어": "sv", "튀르키예어": "tr", "터키어": "tr", "아랍어": "ar"}


def bump_leeokit(repo):
    for p in subprocess.run(["find", repo, "-name", "project.pbxproj", "-not", "-path", "*/build/*"], capture_output=True, text=True).stdout.split():
        s = open(p, encoding="utf-8").read()
        new = re.sub(r'(repositoryURL = "https://github.com/M1zz/LeeoKit(?:\.git)?";\s*requirement = \{[^}]*?minimumVersion = )([\d.]+)', lambda m: m.group(1) + LEEOKIT, s)
        if new != s:
            open(p, "w", encoding="utf-8").write(new); print("LeeoKit →", LEEOKIT, os.path.relpath(p, repo))


def app_plists(repo, bundle):
    out = set()
    for p in subprocess.run(["find", repo, "-name", "project.pbxproj", "-not", "-path", "*/build/*"], capture_output=True, text=True).stdout.split():
        s = open(p, encoding="utf-8").read()
        for blk in re.findall(r"buildSettings = \{(.*?)\n\t\t\t\};", s, re.S):
            m = re.search(r'PRODUCT_BUNDLE_IDENTIFIER = "?([^";]+)"?;', blk)
            f = re.search(r'(?<![A-Z_])INFOPLIST_FILE = "?([^";]+)"?;', blk)
            if m and m.group(1) == bundle and f:
                out.add(os.path.join(os.path.dirname(os.path.dirname(p)), f.group(1).replace("$(SRCROOT)/", "")))
    return out


def add_scheme(plist, scheme):
    pb = "/usr/libexec/PlistBuddy"
    cur = subprocess.run([pb, "-c", "Print :CFBundleURLTypes", plist], capture_output=True, text=True)
    if re.search(rf"^\s+{re.escape(scheme)}\s*$", cur.stdout, re.M):
        return print("스킴 이미 있음", plist)
    if cur.returncode != 0:
        subprocess.run([pb, "-c", "Add :CFBundleURLTypes array", plist], check=True)
    n = cur.stdout.count("CFBundleURLSchemes") if cur.returncode == 0 else 0
    for c in (f"Add :CFBundleURLTypes:{n} dict", f"Add :CFBundleURLTypes:{n}:CFBundleURLName string {scheme}",
              f"Add :CFBundleURLTypes:{n}:CFBundleURLSchemes array", f"Add :CFBundleURLTypes:{n}:CFBundleURLSchemes:0 string {scheme}"):
        subprocess.run([pb, "-c", c, plist], check=True)
    print("스킴 더함", scheme, plist)


def locales(repo):
    env = open(os.path.join(repo, "deploy.env"), encoding="utf-8").read()
    m = re.search(r"^LOCALES=\"?([^\"\n]+)", env, re.M)
    return [ALIAS.get(x.strip(), x.strip()) for x in m.group(1).split(",")] if m else ["ko", "en"]


def heading_locale(h):
    m = re.search(r"\((.*)\)", h)
    if not m:
        return None
    for tok in reversed([t.strip() for t in m.group(1).split(",")]):
        if re.fullmatch(r"[a-z]{2}(-[A-Za-z]{2,4})?", tok):
            return ALIAS.get(tok, tok)
    return KNAMES.get(m.group(1).split(",")[0].strip())


def notes(repo, version):
    cands = [os.path.join(repo, x) for x in ("RELEASE_NOTES.md", "RELEASENOTES.md", "CHANGELOG.md", "docs/RELEASE_NOTES.md", "docs/CHANGELOG.md")]
    path = next((c for c in cands if os.path.exists(c)), cands[0])
    s = open(path, encoding="utf-8").read() if os.path.exists(path) else "# 릴리스 노트\n"
    sec = re.search(rf"^## v?{re.escape(version)}\b.*?(?=^## |\Z)", s, re.M | re.S)
    if not sec:
        body = f"## {version}\n\n"
        for lc in locales(repo):
            head = "### 앱스토어 (한국어, ko)" if lc == "ko" else f"### App Store ({NAMES.get(lc, lc)}, {lc})"
            body += f"{head}\n\n{LINE.get(lc, LINE['en'])}\n\n"
        first = re.search(r"^## ", s, re.M)
        s = s[:first.start()] + body + s[first.start():] if first else s.rstrip() + "\n\n" + body
        open(path, "w", encoding="utf-8").write(s); return print("노트 새 절", version)
    text = sec.group(0)
    def put(m):
        lc = heading_locale(m.group(1))
        line = LINE.get(lc) if lc else None
        if not line or line in m.group(0):
            return m.group(0)
        return f"{m.group(1)}\n\n{line}\n" + m.group(2).lstrip("\n")
    new = re.sub(r"^(###[^\n]*)\n(.*?)(?=^###|\Z)", put, text, flags=re.M | re.S)
    s = s.replace(text, new); open(path, "w", encoding="utf-8").write(s); print("노트 줄 더함", version)


if __name__ == "__main__":
    repo, bundle, version = sys.argv[1:4]
    bump_leeokit(repo)
    for p in app_plists(repo, bundle) or [None]:
        if p is None: print("! 앱 타겟 Info.plist 없음 — 손으로"); break
        add_scheme(p, bundle.lower())
    notes(repo, version)
