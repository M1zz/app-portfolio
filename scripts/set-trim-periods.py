#!/usr/bin/env python3
"""설계안(scripts/paywall-plans.json)의 유료 트림마다 주 · 월 구독 가격을 연 구독 가격에서 계산해 넣는다.

사용법:
  python3 scripts/set-trim-periods.py          # 계산해서 쓴다
  python3 scripts/set-trim-periods.py --dry    # 쓰지 않고 가격 조합만 보여 준다

규칙 (PERIOD_RULE — 페이월 탭에도 그대로 싣는다):
  달러가 기준이다. 월 = 연 ÷ 3 (연 구독이 월 석 달 값), 주 = 월 × 0.4 (주 넷이면 월보다 70% 비싸다).
  달러는 App Store 가격대(USD_POINTS)에 맞추고, 원화는 달러 × 1,450 을 원화 가격대(KRW_POINTS)에 맞춘다.
  같거나 거꾸로 되면(주 ≥ 월, 월 ≥ 연) 그 칸은 비운다 — 최저가에 걸린 아주 싼 트림.
  연 구독이 없는 트림(평생만)은 연 = 평생 ÷ 3 으로 연부터 채운다.
⚠️ 원화 최저가 ₩400 은 2022년 말 가격대 확장 기사 기준이다. App Store Connect 의 가격표로 확인하고 등록한다.
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "scripts/paywall-plans.json")

USD_POINTS = ([0.29, 0.39, 0.49, 0.59, 0.69, 0.79, 0.89, 0.99]
              + [x + 0.49 for x in range(1, 10)] + [x + 0.99 for x in range(1, 10)]
              + [x + 0.99 for x in range(10, 100)])
USD_POINTS = sorted(set(round(x, 2) for x in USD_POINTS))
KRW_POINTS = sorted(set(list(range(400, 1001, 100)) + [1100 * i for i in range(1, 10)] + list(range(10000, 200001, 1000))))
WON_PER_USD = 1450
PERIOD_RULE = ("월 = 연 ÷ 3 (연 구독이 월 석 달 값) · 주 = 월 × 0.4 (주 넷이면 월보다 비싸다). "
               "달러로 계산해 App Store 가격대에 맞추고, 원화는 달러 × 1,450 을 원화 가격대에 맞춘다.")


def snap(x, points):
    return min(points, key=lambda p: (abs(p - x), p))


def usd(s):
    return float(s.replace("$", "")) if s and s.startswith("$") else None


def won(n):
    return "₩{:,}".format(n)


def money(s):
    return int(s.replace("₩", "").replace("￦", "").replace(",", "")) if s else None


def periods(year_usd, year_krw):
    m_usd = snap(year_usd / 3, USD_POINTS)
    w_usd = snap(m_usd * 0.4, USD_POINTS)
    m_krw = snap(m_usd * WON_PER_USD, KRW_POINTS)
    w_krw = snap(w_usd * WON_PER_USD, KRW_POINTS)
    month = {"price": won(m_krw), "priceUS": "$%.2f" % m_usd} if m_usd < year_usd and m_krw < year_krw else None
    week = ({"price": won(w_krw), "priceUS": "$%.2f" % w_usd}
            if month and w_usd < m_usd and w_krw < m_krw and w_krw * 4.33 > m_krw else None)
    return week, month


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
            week, month = periods(usd(sub["priceUS"]), money(sub["price"]))
            tr["monthly"], tr["weekly"] = month, week
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
