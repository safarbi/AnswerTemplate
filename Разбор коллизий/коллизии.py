"""Разбор коллизий: помечает каждую как настоящую, допустимую или требующую проверки.

Понимает два формата:
- отчёт Navisworks Clash Detective в формате XML;
- HTML-отчёт «Проверка на пересечения» из Revit.

Правила лежат в таблице правила.csv, её можно править в Excel.
Правила проверяются сверху вниз, срабатывает первое подходящее.

Запуск:  python3 коллизии.py отчёт.xml [правила.csv]
"""

import csv
import html
import re
import sys
import xml.etree.ElementTree as ET

DEFAULT_VERDICT = ("Настоящая", "Ни одно правило не подошло, коллизия считается настоящей")


# ---------- Чтение отчётов ----------

def describe(obj):
    """Описание элемента из Navisworks: путь в дереве модели, слой и умные метки."""
    parts = [n.text or "" for n in obj.iter("node")]
    parts += [(obj.findtext("layer") or "")]
    parts += [t.findtext("value") or "" for t in obj.iter("smarttag")]
    return " / ".join(p.strip() for p in parts if p and p.strip())


def element_id(obj):
    for attr in obj.iter("objectattribute"):
        if "id" in (attr.findtext("name") or "").lower():
            return (attr.findtext("value") or "").strip()
    return ""


def read_navisworks(path):
    root = ET.parse(path).getroot()
    for test in root.iter("clashtest"):
        for res in test.iter("clashresult"):
            objs = list(res.iter("clashobject"))
            if len(objs) < 2:
                continue
            p = res.find(".//pos3f")
            point = f"{p.get('x')}; {p.get('y')}; {p.get('z')}" if p is not None else ""
            distance = res.get("distance")
            yield {
                "Тест": test.get("name", ""),
                "Коллизия": res.get("name", ""),
                "Статус": res.findtext("resultstatus") or res.get("status", ""),
                "Глубина, мм": round(abs(float(distance)) * 1000, 1) if distance else None,
                "Элемент A": describe(objs[0]), "ID A": element_id(objs[0]),
                "Элемент B": describe(objs[1]), "ID B": element_id(objs[1]),
                "Координаты": point,
            }


def read_revit_html(path):
    """В отчёте Revit каждая строка таблицы: номер, элемент A, элемент B."""
    text = open(path, encoding="utf-8", errors="replace").read()
    n = 0
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S | re.I):
        cells = [html.unescape(re.sub(r"<[^>]+>", " ", c)).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S | re.I)]
        cells = [c for c in cells if c and not c.isdigit()]
        if len(cells) < 2:
            continue
        n += 1
        ids = [re.search(r"(?:ID|код)\D*(\d+)", c, re.I) for c in cells[:2]]
        yield {
            "Тест": "Revit", "Коллизия": str(n), "Статус": "", "Глубина, мм": None,
            "Элемент A": cells[0], "ID A": ids[0].group(1) if ids[0] else "",
            "Элемент B": cells[1], "ID B": ids[1].group(1) if ids[1] else "",
            "Координаты": "",
        }


# ---------- Правила ----------

def load_rules(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def matches(pattern, text):
    """Пустое поле подходит ко всему. «Труб|Воздуховод» означает «или»."""
    if not pattern.strip():
        return True
    return any(p.strip().lower() in text.lower() for p in pattern.split("|") if p.strip())


def apply_rules(clash, rules):
    a, b, depth = clash["Элемент A"], clash["Элемент B"], clash["Глубина, мм"]
    for r in rules:
        limit = r["Глубина до, мм"].strip().replace(",", ".")
        if limit:
            if depth is None or depth > float(limit):
                continue
        pa, pb = r["Элемент A содержит"], r["Элемент B содержит"]
        # Порядок элементов в отчёте случайный, поэтому проверяем обе стороны.
        if (matches(pa, a) and matches(pb, b)) or (matches(pa, b) and matches(pb, a)):
            return r["Вердикт"], r["Причина"], r["№"]
    return DEFAULT_VERDICT[0], DEFAULT_VERDICT[1], ""


# ---------- Главная часть ----------

def main():
    if len(sys.argv) < 2:
        raise SystemExit("Укажите файл отчёта: python3 коллизии.py отчёт.xml")
    path = sys.argv[1]
    rules = load_rules(sys.argv[2] if len(sys.argv) > 2 else "правила.csv")
    reader = read_revit_html if path.lower().endswith((".html", ".htm")) else read_navisworks

    seen, results = {}, []
    for c in reader(path):
        pair = frozenset((c["ID A"], c["ID B"])) if c["ID A"] and c["ID B"] else None
        if pair and pair in seen:
            verdict, reason, rule = "Дубликат", f"Та же пара элементов, что в «{seen[pair]}»", ""
        else:
            verdict, reason, rule = apply_rules(c, rules)
            if pair:
                seen[pair] = f"{c['Тест']} / {c['Коллизия']}"
        c.update({"Вердикт": verdict, "Причина": reason, "Правило №": rule})
        results.append(c)

    out = "коллизии_разбор.csv"
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(results)

    print(f"Всего коллизий: {len(results)}\n")
    counts = {}
    for r in results:
        counts[r["Вердикт"]] = counts.get(r["Вердикт"], 0) + 1
    for v, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {v}: {n}")
    print()
    for r in results:
        depth = f"{r['Глубина, мм']} мм" if r["Глубина, мм"] is not None else "нет данных"
        print(f"[{r['Вердикт']}] {r['Тест']} / {r['Коллизия']}, глубина {depth}")
        print(f"    A: {r['Элемент A']}\n    B: {r['Элемент B']}\n    {r['Причина']}")
    print(f"\nТаблица сохранена в {out}")


if __name__ == "__main__":
    main()
