"""Метрики кода (модули 3, 10, 13).

Считает строки кода по языкам. Если установлен lizard (`pip install lizard`),
дополнительно считает цикломатическую сложность и длину функций.

Использование:
    python tools/metrics.py <путь к проекту>
    python tools/metrics.py <путь к проекту> --label "М03 до" --out <путь>/practice/m03/metrics-raw.md
"""
import argparse
import datetime
import os

from common import iter_code_files, loc_by_language, md_table, setup_console, write_or_print

LIZARD_EXT = {".py", ".js", ".jsx", ".mjs", ".ts", ".tsx", ".vue", ".php", ".java", ".kt", ".cs",
              ".cpp", ".c", ".h", ".go", ".rb", ".swift", ".gd"}


def complexity(root, ccn_limit, len_limit):
    try:
        import lizard
    except ImportError:
        return None
    funcs = []
    for path, ext in iter_code_files(root):
        if ext not in LIZARD_EXT:
            continue
        try:
            info = lizard.analyze_file(path)
        except Exception:
            continue
        rel = os.path.relpath(path, root).replace("\\", "/")
        for fn in info.function_list:
            funcs.append((fn.cyclomatic_complexity, fn.nloc, f"{rel}:{fn.start_line}", fn.name))
    return funcs


def main():
    setup_console()
    ap = argparse.ArgumentParser(description="Метрики кода в формате Markdown")
    ap.add_argument("path")
    ap.add_argument("--label", default="", help="подпись замера, например «М03 до»")
    ap.add_argument("--out", help="дописать результат в файл")
    ap.add_argument("--ccn", type=int, default=10, help="порог сложности (по умолчанию 10)")
    ap.add_argument("--long", type=int, default=50, help="порог длины функции в строках (50)")
    a = ap.parse_args()
    root = os.path.abspath(a.path)

    title = f"## Метрики кода {a.label}".rstrip()
    lines = [title, "", f"Дата замера: {datetime.datetime.now():%d.%m.%Y %H:%M}", ""]

    loc = loc_by_language(root)
    rows = [[lang, s[0], s[1], s[2], s[3]] for lang, s in loc.items()]
    tot = [sum(s[i] for s in loc.values()) for i in range(4)]
    rows.append(["**Итого**", tot[0], tot[1], tot[2], tot[3]])
    lines += ["### Строки кода", "", md_table(["Язык", "Файлов", "Код", "Комментарии", "Пустые"], rows), ""]

    funcs = complexity(root, a.ccn, a.long)
    if funcs is None:
        lines += ["> Сложность не посчитана: установите lizard командой `pip install lizard` и запустите снова.", ""]
    elif not funcs:
        lines += ["> lizard не нашёл функций в коде проекта.", ""]
    else:
        n = len(funcs)
        avg = sum(f[0] for f in funcs) / n
        mx = max(funcs)
        hard = sorted([f for f in funcs if f[0] > a.ccn], reverse=True)
        long_ = sorted([f for f in funcs if f[1] > a.long], key=lambda f: -f[1])
        lines += ["### Сложность", "", md_table(["Метрика", "Значение"], [
            ["Функций", n],
            ["Средняя цикломатическая сложность", f"{avg:.2f}".replace(".", ",")],
            ["Максимальная сложность", f"{mx[0]} — `{mx[3]}` ({mx[2]})"],
            [f"Функций со сложностью > {a.ccn}", len(hard)],
            [f"Функций длиннее {a.long} строк", len(long_)],
        ]), ""]
        if hard:
            lines += [f"#### Самые сложные функции (сложность > {a.ccn})", "",
                      md_table(["Функция", "Где", "Сложность", "Строк"],
                               [[f"`{f[3]}`", f[2], f[0], f[1]] for f in hard[:15]]), ""]
        if long_:
            lines += [f"#### Самые длинные функции (> {a.long} строк)", "",
                      md_table(["Функция", "Где", "Строк", "Сложность"],
                               [[f"`{f[3]}`", f[2], f[1], f[0]] for f in long_[:15]]), ""]
    lines += ["Перенесите итоговые числа в таблицу `practice/m03/metrics.md`.", ""]
    write_or_print("\n".join(lines), a.out)


if __name__ == "__main__":
    main()
