#!/usr/bin/env python3
"""'고마운 사람들'에 이름을 올린다 (docs/thanks.json).

사용법:
  python3 scripts/add-thanks.py clip-keyboard "보내 준 이름"
  python3 scripts/add-thanks.py clip-keyboard "보내 준 이름" --remove   # 본인이 내려 달라고 할 때

올리기 전에 메일로 받은 주문 번호(Order ID)로 후원을 확인한다(App Store Connect · 결제 내역).
주문 번호 · 메일 주소는 이 파일에 적지 않는다. 커밋 · 푸시하면 소개 페이지에 바로 보인다.
"""
import argparse
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "docs/thanks.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app", help="앱 slug (예: clip-keyboard)")
    ap.add_argument("name", help="보내 준 이름 그대로")
    ap.add_argument("--remove", action="store_true")
    args = ap.parse_args()
    data = json.load(open(PATH, encoding="utf-8"))
    names = data.setdefault("apps", {}).setdefault(args.app, [])
    name = args.name.strip()
    if args.remove:
        names[:] = [n for n in names if n.get("name") != name]
    elif any(n.get("name") == name for n in names):
        print("이미 있습니다: %s · %s" % (args.app, name))
        return
    else:
        names.append({"name": name, "since": date.today().isoformat()[:7]})
    with open(PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("%s · %s — %d명" % (args.app, "내림" if args.remove else "올림", len(names)))


if __name__ == "__main__":
    main()
