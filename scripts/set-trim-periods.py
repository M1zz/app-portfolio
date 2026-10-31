#!/usr/bin/env python3
"""설계안(scripts/paywall-plans.json)의 유료 트림마다 주 · 월 · 연 · 평생 가격을 앱 크기 사다리로 다시 매긴다.

사용법:
  python3 scripts/set-trim-periods.py          # 계산해서 쓴다
  python3 scripts/set-trim-periods.py --dry    # 쓰지 않고 가격 조합만 보여 준다

규칙 (PERIOD_RULE — 페이월 탭에도 그대로 싣는다):
  연 구독은 앱 크기(S · M · L)와 칸(첫 유료 칸 · 둘째 칸)으로 정한다 — YEAR.
  월 = 연 ÷ 3, 주 = 월 × 0.4, 평생 = 연 × 3. 달러로 계산해 App Store 가격대에 맞추고, 원화는 달러 × 1,450 을 원화 가격대에.
  바닥: 주 $0.99 · 월 $1.49 · 연 $5.99 (주 ₩600 · 연 $1.99 는 너무 싸 보인다). 비율이 깨지는 것은 감수한다.
  천장: 주 $2.49 · 월 $6.49 · 연 $19.99 · 평생 $59.99 — 실제로 매출이 나는 황금주간 Pro 값이다. 그보다 비싸게 받지 않는다.
  같은 기간에서 둘째 칸(Pro)은 첫 칸(Plus)보다 한 가격대 이상 비싸다.
  이미 사다리보다 비싸게 잡아 둔 칸(황금주간)은 그 값을 지킨다. 값이 그대로인 칸은 원화도 손대지 않는다.
  업그레이드 = Pro 평생 − Plus 평생, 구독 졸업 = Pro 평생 − Pro 연.
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "scripts/paywall-plans.json")

USD_POINTS = sorted(set(round(x, 2) for x in [0.99] + [x + 0.49 for x in range(1, 10)] + [x + 0.99 for x in range(1, 100)]))
KRW_POINTS = sorted(set([1100 * i for i in range(1, 10)] + list(range(10000, 200001, 1000))))
WON_PER_USD = 1450
# 앱 크기 → (첫 유료 칸, 둘째 칸) 연 구독 달러
YEAR = {"S": (5.99, 8.99), "M": (7.99, 11.99), "L": (9.99, 14.99)}
FLOOR = {"weekly": 0.99, "monthly": 1.49, "year": 5.99}
CEIL = {"weekly": 2.49, "monthly": 6.49, "year": 19.99, "life": 59.99}
PERIOD_RULE = ("연 구독은 앱 크기 사다리(S $5.99 · $8.99, M $7.99 · $11.99, L $9.99 · $14.99), 월 = 연 ÷ 3, 주 = 월 × 0.4, "
               "평생 = 연 × 3. 바닥 주 $0.99 · 월 $1.49 · 연 $5.99, 천장 주 $2.49 · 월 $6.49 · 연 $19.99 · 평생 $59.99. "
               "Pro 는 같은 기간 Plus 보다 한 가격대 위. 원화는 달러 × 1,450 을 원화 가격대에 맞춘다.")


def snap(x, points):
    return min(points, key=lambda p: (abs(p - x), p))


def above(x):
    """x 보다 한 가격대 위."""
    return next(p for p in USD_POINTS if p > x + 1e-9)


def clamp(x, lo, hi):
    return min(max(x, lo), hi)


def usd(s):
    return float(s.replace("$", "")) if s and s.startswith("$") else None


def won(n):
    return "₩{:,}".format(n)


def money(s):
    return int(s.replace("₩", "").replace("￦", "").replace(",", "")) if s else None


def put(obj, u):
    """달러가 바뀐 칸만 원화를 새로 맞춘다. 바뀌었으면 True."""
    if obj.get("priceUS") == "$%.2f" % u:
        return False
    obj["price"], obj["priceUS"] = won(snap(u * WON_PER_USD, KRW_POINTS)), "$%.2f" % u
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    data = json.load(open(PATH, encoding="utf-8"))
    rows = {}
    for slug, plan in data["apps"].items():
        paid = [tr for tr in plan.get("trims") or [] if tr.get("price")]
        ladder = YEAR.get(plan.get("size") or "S", YEAR["S"])
        prev, changed = None, False
        for i, tr in enumerate(paid):
            sub = tr.setdefault("subscription", {"period": "연"})
            y = clamp(max(ladder[min(i, 1)], usd(sub.get("priceUS")) or 0), FLOOR["year"], CEIL["year"])
            m = clamp(snap(y / 3, USD_POINTS), FLOOR["monthly"], CEIL["monthly"])
            w = clamp(snap(m * 0.4, USD_POINTS), FLOOR["weekly"], CEIL["weekly"])
            life = min(max(snap(y * 3, USD_POINTS), usd(tr.get("priceUS")) or 0), CEIL["life"])
            if prev:  # Pro 는 같은 기간 Plus 보다 한 가격대 위
                y, m, w, life = (max(y, above(prev[0])), max(m, above(prev[1])),
                                 max(w, above(prev[2])), max(life, above(prev[3])))
            assert w < m < y < life, (slug, tr["id"], w, m, y, life)
            tr["monthly"], tr["weekly"] = tr.get("monthly") or {}, tr.get("weekly") or {}
            for obj, u in ((sub, y), (tr, life), (tr["monthly"], m), (tr["weekly"], w)):
                changed |= put(obj, u)
            prev = (y, m, w, life)
            key = (plan.get("size"), min(i, 1), y, tr["weekly"]["price"], w, tr["monthly"]["price"], m,
                   sub["price"], tr["price"], life)
            rows.setdefault(key, []).append(slug)
        if paid and changed:
            top = paid[-1]
            if len(paid) > 1:
                plan["upgrade"] = won(snap(money(top["price"]) - money(paid[0]["price"]), KRW_POINTS))
                plan["upgradeUS"] = "$%.2f" % snap(usd(top["priceUS"]) - usd(paid[0]["priceUS"]), USD_POINTS)
            plan["graduate"] = won(snap(money(top["price"]) - money(top["subscription"]["price"]), KRW_POINTS))
            plan["graduateUS"] = "$%.2f" % snap(usd(top["priceUS"]) - usd(top["subscription"]["priceUS"]), USD_POINTS)
    for (size, i, y, wk, w, mk, m, yk, lk, life), who in sorted(rows.items()):
        print("  %s %-4s 주 %-7s $%-5.2f 월 %-7s $%-5.2f 연 %-8s $%-6.2f 평생 %-8s $%-6.2f %d개" % (
            size, ("Plus", "Pro")[i], wk, w, mk, m, yk, y, lk, life, len(who)))
    if args.dry:
        return
    data["periodRule"] = PERIOD_RULE
    with open(PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
