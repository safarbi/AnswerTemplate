"""Сборщик спецификации оборудования, изделий и материалов из выгрузки Revit.

Что делает:
1. Читает спецификацию, экспортированную из Revit в текстовый файл.
2. Проверяет, заполнены ли обязательные параметры, и выводит список ошибок.
3. Складывает одинаковые позиции внутри каждой системы.
4. Сохраняет таблицу по форме ГОСТ 21.110, которая сразу открывается в Excel.

Запуск:  python3 спецификация.py выгрузка_revit.txt
"""

import csv
import sys
from collections import OrderedDict

# Обязательные параметры: без них строка не попадёт в спецификацию.
REQUIRED = ["Наименование", "Ед. изм.", "Количество"]

# По этим параметрам строки считаются одной позицией и складываются.
KEY = ["Наименование", "Обозначение", "Код", "Изготовитель", "Ед. изм.", "Масса ед., кг", "Примечание"]

# Колонки итоговой спецификации по ГОСТ 21.110.
GOST_COLUMNS = ["Поз.", "Наименование и техническая характеристика", "Тип, марка, обозначение документа",
                "Код продукции", "Поставщик", "Ед. измерения", "Кол.", "Масса 1 ед., кг", "Примечание"]


def read_text(path):
    """Revit сохраняет файлы в разных кодировках. Пробуем по очереди."""
    raw = open(path, "rb").read()
    for enc in ("utf-16", "utf-8-sig", "cp1251"):
        try:
            return raw.decode(enc)
        except UnicodeError:
            continue
    raise SystemExit("Не удалось прочитать файл: неизвестная кодировка")


def to_number(text):
    """Превращает «12,5» в 12.5. Пустое или нечисловое значение даёт None."""
    try:
        return float(str(text).replace(" ", "").replace(",", "."))
    except ValueError:
        return None


def fmt(n):
    """Число для таблицы: без лишних нулей и с запятой, как принято в России."""
    return f"{n:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "выгрузка_revit.txt"
    text = read_text(path)
    delimiter = "\t" if "\t" in text.splitlines()[0] else ";"
    rows = list(csv.DictReader(text.splitlines(), delimiter=delimiter))

    errors = []
    systems = OrderedDict()
    for line_no, r in enumerate(rows, start=2):
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        missing = [p for p in REQUIRED if not r.get(p)]
        qty = to_number(r.get("Количество", ""))
        if r.get("Количество") and qty is None:
            missing.append("Количество (не число)")
        if missing:
            name = r.get("Наименование") or "без наименования"
            errors.append(f"строка {line_no}, система {r.get('Система') or '?'}, {name}: не заполнено {', '.join(missing)}")
            continue
        key = tuple(r.get(k, "") for k in KEY)
        items = systems.setdefault(r.get("Система") or "Без системы", OrderedDict())
        items[key] = items.get(key, 0) + qty

    out_rows, pos, total_mass = [], 0, 0.0
    for system, items in systems.items():
        out_rows.append(["", f"Система {system}", "", "", "", "", "", "", ""])
        for key, qty in items.items():
            pos += 1
            name, designation, code, maker, unit, mass, note = key
            m = to_number(mass)
            if m:
                total_mass += m * qty
            out_rows.append([pos, name, designation, code, maker, unit, fmt(qty), mass, note])

    out_path = "спецификация_ГОСТ.csv"
    # Точка с запятой и BOM нужны, чтобы русский Excel открыл файл двойным щелчком.
    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(GOST_COLUMNS)
        writer.writerows(out_rows)

    print(f"Прочитано строк: {len(rows)}")
    print(f"Позиций в спецификации: {pos} в {len(systems)} системах")
    print(f"Общая масса изделий с указанной массой: {fmt(total_mass)} кг")
    print(f"Спецификация сохранена в {out_path}\n")
    if errors:
        print(f"Ошибки в модели, строк пропущено: {len(errors)}")
        for e in errors:
            print("  -", e)
    else:
        print("Ошибок в параметрах нет")


if __name__ == "__main__":
    main()
