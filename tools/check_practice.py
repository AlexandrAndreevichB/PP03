"""Проверка готовности модулей перед сдачей.

Смотрит, есть ли в practice/mNN нужные файлы, не осталось ли в них TODO,
лежит ли отчёт .docx и есть ли коммиты по модулю.

Использование:
    python tools/check_practice.py <путь к проекту>              # все модули
    python tools/check_practice.py <путь к проекту> --module 3   # только модуль 3
"""
import argparse
import glob
import os

from common import git, setup_console

# Что должно лежать в practice/mNN. Строка с * — шаблон имени (достаточно одного совпадения).
REQUIRED = {
    1: ["passport.md", "repo-stats.md", "*.png"],
    2: ["dfd.drawio", "dfd-0.png", "dfd-1.png", "trace.md", "input-points.md", "*.har"],
    # модули 3–13 добавляются вместе с материалами следующих недель
}
# Файлы в корне проекта, которые должны появиться к концу модуля
ROOT_FILES = {}


def exists(base, pattern):
    for alt in pattern.split("|"):
        if glob.glob(os.path.join(base, alt)):
            return True
    return False


def todo_count(folder):
    n, where = 0, []
    for f in glob.glob(os.path.join(folder, "*")):
        if f.endswith((".md", ".puml")):
            with open(f, encoding="utf-8", errors="replace") as fh:
                c = fh.read().count("TODO")
            if c:
                n += c
                where.append(f"{os.path.basename(f)} ({c})")
    return n, where


def check(root, m):
    folder = os.path.join(root, "practice", f"m{m:02d}")
    problems = []
    if not os.path.isdir(folder):
        return [f"нет папки practice/m{m:02d} — запустите tools/install"]
    for req in REQUIRED[m]:
        if not exists(folder, req):
            problems.append(f"нет файла {req}")
    for req in ROOT_FILES.get(m, []):
        if not exists(root, req):
            problems.append(f"в корне проекта нет {req.replace('|', ' или ')}")
    n, where = todo_count(folder)
    if n:
        problems.append(f"не заполнено TODO: {n} — " + ", ".join(where))
    if not glob.glob(os.path.join(folder, "*.docx")):
        problems.append("нет отчёта .docx (ISPO332_Familiya_M%02d.docx)" % m)
    commits = git(root, "log", "--all", "--oneline", "--", f"practice/m{m:02d}").splitlines()
    if commits and len(commits) < 3:
        problems.append(f"в practice/m{m:02d} всего {len(commits)} коммит(а) — коммитьте по ходу работы")
    if not commits:
        problems.append("нет ни одного коммита в practice/m%02d — закоммитьте и запушьте" % m)
    return problems


def main():
    setup_console()
    ap = argparse.ArgumentParser(description="Проверка готовности модулей практики")
    ap.add_argument("path")
    ap.add_argument("--module", type=int, choices=range(1, 14), metavar="1..13")
    a = ap.parse_args()
    root = os.path.abspath(a.path)
    if a.module and a.module not in REQUIRED:
        print(f"Материалы модуля {a.module} ещё не выданы — обновите репозиторий практики: git pull")
        return
    mods = [a.module] if a.module else sorted(REQUIRED)
    ok = 0
    for m in mods:
        pr = check(root, m)
        if pr:
            print(f"М{m:02d}  ✗")
            for p in pr:
                print(f"      – {p}")
        else:
            ok += 1
            print(f"М{m:02d}  ✓ готов к сдаче")
    if len(mods) > 1:
        print(f"\nГотово модулей: {ok} из {len(mods)}")


if __name__ == "__main__":
    main()
