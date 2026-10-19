"""Калькулятор окупаемости энергосберегающих мероприятий.

Читает мероприятия из CSV и для каждого считает:
- простую окупаемость: за сколько лет экономия вернёт затраты;
- дисконтированную окупаемость: то же, но с учётом стоимости денег во времени;
- NPV: сколько денег проект принесёт сверх затрат в сегодняшних рублях;
- IRR: ставка, при которой NPV равен нулю, то есть «доходность» мероприятия.

Запуск:  python3 расчет.py мероприятия.csv 16
Последнее число — ставка дисконтирования в процентах.
"""

import csv
import sys


def npv(rate, cost, saving, years):
    """Чистая приведённая стоимость: экономия по годам минус затраты сегодня."""
    return -cost + sum(saving / (1 + rate) ** t for t in range(1, years + 1))


def irr(cost, saving, years):
    """Внутренняя норма доходности. Ищем ставку делением отрезка пополам."""
    low, high = -0.99, 10.0
    if npv(low, cost, saving, years) * npv(high, cost, saving, years) > 0:
        return None
    for _ in range(200):
        mid = (low + high) / 2
        if npv(mid, cost, saving, years) > 0:
            low = mid
        else:
            high = mid
    return mid


def discounted_payback(rate, cost, saving, years):
    """Год, в котором дисконтированная экономия перекрыла затраты."""
    total = 0.0
    for t in range(1, years + 1):
        total += saving / (1 + rate) ** t
        if total >= cost:
            return t
    return None


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "мероприятия.csv"
    rate = float(sys.argv[2]) / 100 if len(sys.argv) > 2 else 0.16

    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = []
    for r in rows:
        cost = float(r["затраты_руб"])
        saving = float(r["экономия_руб_в_год"])
        years = int(r["срок_службы_лет"])
        rate_irr = irr(cost, saving, years)
        results.append({
            "мероприятие": r["мероприятие"],
            "простая_окупаемость_лет": round(cost / saving, 1),
            "дисконт_окупаемость_лет": discounted_payback(rate, cost, saving, years) or "не окупается",
            "NPV_руб": round(npv(rate, cost, saving, years)),
            "IRR_%": round(rate_irr * 100, 1) if rate_irr is not None else "нет",
        })

    results.sort(key=lambda x: x["NPV_руб"], reverse=True)

    print(f"Ставка дисконтирования: {rate * 100:.1f}%\n")
    for x in results:
        verdict = "выгодно" if x["NPV_руб"] > 0 else "НЕ выгодно"
        print(f"{x['мероприятие']}")
        print(f"  окупаемость: {x['простая_окупаемость_лет']} лет простая, "
              f"{x['дисконт_окупаемость_лет']} с дисконтом")
        print(f"  NPV: {x['NPV_руб']:,} руб.  IRR: {x['IRR_%']}%  ({verdict})\n".replace(",", " "))

    with open("результат.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print("Таблица сохранена в результат.csv")


if __name__ == "__main__":
    main()
