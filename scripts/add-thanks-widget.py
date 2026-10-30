#!/usr/bin/env python3
"""후원을 받는 앱의 소개 페이지에 '고마운 사람들' 위젯(docs/thanks.js)을 붙인다.

사용법:
  python3 scripts/add-thanks-widget.py           # scripts/donations.json 에서 후원을 받는 앱 전부
  python3 scripts/add-thanks-widget.py --check   # 붙어 있는지만 본다

앱 레포의 docs/index.html 과 언어 폴더(docs/ko/index.html …) 모두에서 첫 <footer 바로 앞에 넣는다.
표시(<!-- leeo-thanks -->)로 감싸 두어 다시 돌려도 한 번만 들어가고, 바뀐 값은 덮어쓴다.
⚠️ 언어 페이지를 루트에서 다시 만드는 레포(클립키보드 build.mjs · 두번알림 build-lang-pages.py)는
   루트 index.html 에도 들어 있어야 다음 빌드 뒤에도 남는다 — 그래서 루트까지 넣는다.
"""
import argparse
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "projects/PortfolioCEO/PortfolioCEO/Data/apps")
CODE = os.path.expanduser("~/Documents/workspace/code")

# 앱 slug → (레포 폴더, 이름 올리기 메일). 메일은 그 소개 페이지에 이미 적힌 문의 주소를 따른다.
REPOS = {
    "clip-keyboard": ("ClipKeyboard", "leeo@kakao.com"),
    "double-reminder": ("Rereminder", "leeo@kakao.com"),
    "shared-day-designer": ("Goldweek", "leeo@kakao.com"),
    "donkko-mart": ("DontGoMart", "hyunho.lee.1993@gmail.com"),
}
WIDGET = "https://m1zz.github.io/app-portfolio/thanks.js"
BLOCK = re.compile(r"[ \t]*<!-- leeo-thanks -->.*?<!-- /leeo-thanks -->\n?", re.S)


def snippet(slug, name, mail):
    return ('<!-- leeo-thanks -->\n'
            '<section id="leeo-thanks" data-app="%s" data-name="%s" data-mail="%s"></section>\n'
            '<script src="%s" defer></script>\n'
            '<!-- /leeo-thanks -->\n' % (slug, name, mail, WIDGET))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    dons = json.load(open(os.path.join(ROOT, "scripts/donations.json"), encoding="utf-8"))["apps"]
    for slug, d in dons.items():
        if d.get("status") != "live":
            continue
        if slug not in REPOS:
            print("  %-22s 레포를 몰라 건너뜀 — REPOS 에 적어 주세요" % slug)
            continue
        repo, mail = REPOS[slug]
        app = json.load(open(os.path.join(APPS, slug + ".json"), encoding="utf-8"))
        block = snippet(slug, app.get("nameEn") or app["name"], mail)
        pages = [os.path.join(CODE, repo, "docs/index.html")] + sorted(glob.glob(os.path.join(CODE, repo, "docs/*/index.html")))
        done = changed = 0
        for p in pages:
            html = open(p, encoding="utf-8").read()
            if "<footer" not in html:
                continue
            if args.check:
                done += block in html
                continue
            new = BLOCK.sub("", html)
            new = new.replace("<footer", block + "<footer", 1)
            if new != html:
                open(p, "w", encoding="utf-8").write(new)
                changed += 1
            done += 1
        print("  %-22s %s  페이지 %d개%s" % (slug, repo, done, "" if args.check else " (바뀜 %d)" % changed))


if __name__ == "__main__":
    main()
