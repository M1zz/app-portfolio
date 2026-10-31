#!/usr/bin/env python3
"""설계안(scripts/paywall-plans.json)의 유료 트림마다 주 · 월 구독 가격을 연 구독 가격에서 계산해 넣는다.

사용법:
  python3 scripts/set-trim-periods.py          # 계산해서 쓴다
  python3 scripts/set-trim-periods.py --dry    # 쓰지 않고 가격 조합만 보여 준다

규칙 (PERIOD_RULE — 페이월 탭에도 그대로 싣는다):
  달러가 기준이다. 월 = 연 ÷ 3 (연 구독이 월 석 달 값), 주 = 월 × 0.4 (주 넷이면 월보다 70% 비싸다).
  달러는 App Store 가격대(USD_POINTS)에 맞추고, 원화는 달러 × 1,450 을 원화 가격대(KRW_POINTS)에 맞춘다.
  어떤 결제도 $0.99 · ₩1,100 아래로 내리지 않는다(주 ₩600 은 너무 싸 보인다). 비율이 깨지는 것은 감수한다.
  그래도 주 < 월 < 연 < 평생 순서는 지킨다 — 겹치면 위 칸을 한 가격대 올리고(월 → 연),
  평생보다 비싸지면 주부터 비운다(아주 싼 트림은 연 · 평생만).
  연 구독이 없는 트림(평생만)은 연 = 평생 ÷ 3 으로 연부터 채운다.
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "scripts/paywall-plans.json")

FLOOR_USD = 0.99
USD_POINTS = ([0.99]
              + [x + 0.49 for x in range(1, 10)] + [x + 0.99 for x in range(1, 10)]
              + [x + 0.99 for x in range(10, 100)])
USD_POINTS = sorted(set(round(x, 2) for x in USD_POINTS))
KRW_POINTS = sorted(set([1100 * i for i in range(1, 10)] + list(range(10000, 200001, 1000))))
WON_PER_USD = 1450
PERIOD_RULE = ("월 = 연 ÷ 3 (연 구독이 월 석 달 값) · 주 = 월 × 0.4 (주 넷이면 월보다 비싸다). "
               "달러로 계산해 App Store 가격대에 맞추고, 원화는 달러 × 1,450 을 원화 가격대에 맞춘다. "
               "최저가는 $0.99 · ₩1,100 — 그 아래로 내리지 않고, 겹치면 위 칸을 한 가격대 올린다.")


def snap(x, points):
    return min(points, key=lambda p: (abs(p - x), p))


def usd(s):
    return float(s.replace("$", "")) if s and s.startswith("$") else None


def won(n):
    return "₩{:,}".format(n)


def money(s):
    return int(s.replace("₩", "").replace("￦", "").replace(",", "")) if s else None


def above(x):
    """x 보다 한 가격대 위."""
    return next(p for p in USD_POINTS if p > x + 1e-9)


def price(u):
    return {"price": won(snap(u * WON_PER_USD, KRW_POINTS)), "priceUS": "$%.2f" % u}


def periods(year_usd, life_usd):
    """(주, 월, 연) 달러. 최저가 $0.99 를 지키고 겹치면 위 칸을 올린다. 평생 아래에 안 들어가면 주 → 월 순으로 비운다."""
    year = max(year_usd, FLOOR_USD)
    for keep in (("week", "month"), ("month",), ()):
        y, m, w = year, None, None
        if "month" in keep:
            m = max(snap(y / 3, USD_POINTS), FLOOR_USD)
            if "week" in keep:
                w = max(snap(m * 0.4, USD_POINTS), FLOOR_USD)
                if m <= w:
                    m = above(w)
            if y <= m:
                y = above(m)
        if not life_usd or y < life_usd:
            return w, m, y
    return None, None, year


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    data = json.load(open(PATH, encoding="utf-8"))
    seen = {}
    for slug, plan in data["apps"].items():
        for tr in plan.get("trims") or []:
            if not tr.get("price"):
                continue
            sub = tr.get("subscription")
            if not sub:
                life_usd = usd(tr.get("priceUS"))
                y_usd = snap(life_usd / 3, USD_POINTS)
                sub = tr["subscription"] = {"period": "연", "price": won(snap(y_usd * WON_PER_USD, KRW_POINTS)),
                                            "priceUS": "$%.2f" % y_usd}
            w, m, y = periods(usd(sub["priceUS"]), usd(tr.get("priceUS")))
            if y != usd(sub["priceUS"]):
                sub.update(price(y))  # 최저가 · 순서 때문에 연을 올린 칸만 — 손으로 맞춘 원화는 그대로 둔다
            tr["monthly"], tr["weekly"] = m and price(m), w and price(w)
            week, month = tr["weekly"], tr["monthly"]
            key = (sub["price"], sub["priceUS"])
            seen.setdefault(key, (week, month, []))[2].append("%s.%s" % (slug, tr["id"]))
    for (yk, yu), (w, m, who) in sorted(seen.items(), key=lambda kv: money(kv[0][0])):
        print("  연 %-8s %-7s → 월 %-16s 주 %-16s  (%d칸)" % (
            yk, yu, m and "%s %s" % (m["price"], m["priceUS"]) or "—",
            w and "%s %s" % (w["price"], w["priceUS"]) or "—", len(who)))
    if args.dry:
        return
    data["periodRule"] = PERIOD_RULE
    with open(PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
