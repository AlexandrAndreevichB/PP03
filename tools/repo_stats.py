"""Статистика репозитория для паспорта проекта (модуль 1).

Использование:
    python tools/repo_stats.py <путь к проекту>
    python tools/repo_stats.py <путь к проекту> --out <путь к проекту>/practice/m01/repo-stats.md
"""
import argparse
import os
from collections import Counter

from common import git, loc_by_language, md_table, setup_console, write_or_print


def main():
    setup_console()
    ap = argparse.ArgumentParser(description="Статистика git-репозитория в формате Markdown")
    ap.add_argument("path", help="путь к клонированному проекту")
    ap.add_argument("--out", help="дописать результат в файл")
    ap.add_argument("--top", type=int, default=10, help="сколько файлов показать в топе изменений")
    a = ap.parse_args()
    p = os.path.abspath(a.path)
    if not git(p, "rev-parse", "--git-dir"):
        print(f"Ошибка: {p} — не git-репозиторий")
        return 1

    lines = ["## Статистика репозитория", ""]
    total = git(p, "rev-list", "--count", "--all") or "0"
    first = git(p, "log", "--all", "--reverse", "--format=%ad", "--date=short").splitlines()
    last = git(p, "log", "-1", "--all", "--format=%ad", "--date=short")
    lines += [md_table(["Показатель", "Значение"], [
        ["Коммитов (все ветки)", total],
        ["Первый коммит", first[0] if first else "—"],
        ["Последний коммит", last or "—"],
        ["Текущая ветка", git(p, "rev-parse", "--abbrev-ref", "HEAD")],
        ["Удалённый репозиторий", git(p, "remote", "get-url", "origin") or "—"],
    ]), ""]

    authors = git(p, "shortlog", "-sne", "--all", "HEAD").splitlines()
    rows = []
    for ln in authors[:15]:
        n, _, who = ln.strip().partition("\t")
        rows.append([who, n])
    lines += ["### Авторы", "", md_table(["Автор", "Коммитов"], rows) if rows else "—", ""]

    branches = [b.strip().lstrip("* ") for b in git(p, "branch", "-a").splitlines() if "->" not in b]
    tags = git(p, "tag").splitlines()
    lines += ["### Ветки и теги", "",
              f"Ветки ({len(branches)}): " + (", ".join(f"`{b}`" for b in branches[:20]) or "—"),
              "", f"Теги ({len(tags)}): " + (", ".join(f"`{t}`" for t in tags[:20]) or "нет"), ""]

    changed = Counter(f for f in git(p, "log", "--all", "--name-only", "--format=").splitlines() if f)
    rows = [[f"`{f}`", n] for f, n in changed.most_common(a.top)]
    lines += [f"### {a.top} самых часто изменяемых файлов", "",
              md_table(["Файл", "Изменений"], rows) if rows else "—", ""]

    by_month = Counter(d[:7] for d in git(p, "log", "--all", "--format=%ad", "--date=short").splitlines())
    rows = [[m, n] for m, n in sorted(by_month.items())]
    lines += ["### Активность по месяцам", "", md_table(["Месяц", "Коммитов"], rows) if rows else "—", ""]

    loc = loc_by_language(p)
    rows = [[lang, s[0], s[1], s[2], s[3]] for lang, s in loc.items()]
    lines += ["### Объём кода по языкам", "",
              md_table(["Язык", "Файлов", "Код", "Комментарии", "Пустые"], rows) if rows else "—", "",
              "Граф коммитов для скриншота: `git log --oneline --graph --all --decorate -n 40`", ""]

    write_or_print("\n".join(lines), a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
