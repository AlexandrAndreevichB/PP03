r"""Статистика репозитория для паспорта проекта (модуль 1).

Использование:
    (из папки своего проекта)
    python ..\pp03-ispo332\tools\repo_stats.py
    python ..\pp03-ispo332\tools\repo_stats.py --out practice\m01\repo-stats.md
"""
import argparse
import os
from collections import Counter
import subprocess
import sys


# ===== общие функции (встроены, чтобы скрипт работал одним файлом) =====
# Папки, которые не считаются кодом проекта
SKIP_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", "out", "target", "bin", "obj",
    ".idea", ".vscode", ".gradle", "__pycache__", ".venv", "venv", "env", ".next",
    ".nuxt", "coverage", "practice", "Pods", ".dart_tool", "storage", "public/build",
}

# Расширение -> (язык, символ однострочного комментария)
LANGS = {
    ".py": ("Python", "#"), ".js": ("JavaScript", "//"), ".jsx": ("JavaScript", "//"),
    ".mjs": ("JavaScript", "//"), ".ts": ("TypeScript", "//"), ".tsx": ("TypeScript", "//"),
    ".vue": ("Vue", "//"), ".php": ("PHP", "//"), ".java": ("Java", "//"), ".kt": ("Kotlin", "//"),
    ".cs": ("C#", "//"), ".cpp": ("C++", "//"), ".c": ("C", "//"), ".h": ("C/C++ header", "//"),
    ".go": ("Go", "//"), ".rb": ("Ruby", "#"), ".swift": ("Swift", "//"), ".dart": ("Dart", "//"),
    ".html": ("HTML", None), ".css": ("CSS", None), ".scss": ("SCSS", "//"), ".sql": ("SQL", "--"),
    ".xml": ("XML", None), ".gd": ("GDScript", "#"),
}


def setup_console():
    """Чтобы кириллица нормально выводилась в консоли Windows."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass


def git(path, *args):
    """Выполнить git-команду в папке path и вернуть вывод (пустая строка при ошибке)."""
    try:
        r = subprocess.run(["git", "-C", path, *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        return r.stdout.strip() if r.returncode == 0 else ""
    except FileNotFoundError:
        print("Ошибка: git не найден. Установите Git и перезапустите терминал.")
        sys.exit(1)


def iter_code_files(root):
    """Все файлы с кодом проекта (без node_modules, vendor и т. п.)."""
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root).replace("\\", "/")
        dirnames[:] = [d for d in dirnames if not is_practice_repo(os.path.join(dirpath, d))]
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and f"{rel}/{d}".lstrip("./") not in SKIP_DIRS
                       and not d.startswith(".")]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext in LANGS and not name.endswith((".min.js", ".min.css")):
                yield os.path.join(dirpath, name), ext


def count_lines(path, comment):
    """Вернуть (код, комментарии, пустые) для файла."""
    code = com = blank = 0
    in_block = False
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                s = line.strip()
                if not s:
                    blank += 1
                elif in_block:
                    com += 1
                    if "*/" in s or "-->" in s:
                        in_block = False
                elif s.startswith("/*") or s.startswith("<!--"):
                    com += 1
                    if not ("*/" in s or "-->" in s):
                        in_block = True
                elif comment and s.startswith(comment):
                    com += 1
                else:
                    code += 1
    except OSError:
        pass
    return code, com, blank


def loc_by_language(root):
    stats = {}
    for path, ext in iter_code_files(root):
        lang, comment = LANGS[ext]
        c, m, b = count_lines(path, comment)
        s = stats.setdefault(lang, [0, 0, 0, 0])
        s[0] += 1; s[1] += c; s[2] += m; s[3] += b
    return dict(sorted(stats.items(), key=lambda kv: -kv[1][1]))


PATH_HELP = "папка вашего проекта (форка); если не указать — текущая папка"


def is_practice_repo(p):
    return os.path.isdir(os.path.join(p, "skeleton")) and os.path.isfile(os.path.join(p, "tools", "check_practice.py"))


def project_root(path):
    """Проверить, что path — папка проекта, а не репозиторий практики; вернуть абсолютный путь."""
    if not path or path == ".":
        here = os.path.abspath(".")
        if not git(here, "rev-parse", "--show-toplevel") or is_practice_repo(git(here, "rev-parse", "--show-toplevel")):
            # запуск двойным щелчком или из IDLE (F5) — спросить папку
            path = input("Путь к папке вашего проекта (можно перетащить папку сюда): ").strip().strip('"')
    p = os.path.abspath(path or ".")
    if p.lower().endswith((".md", ".txt", ".docx")):
        print(f"Ошибка: {path} — это файл результата, а первым указывается ПАПКА ПРОЕКТА.")
        print("Файл для записи указывается после --out. Пример (из папки проекта):")
        print("  python ..\\PP03-main\\tools\\repo_stats.py . --out practice\\m01\\repo-stats.md")
        sys.exit(1)
    if not os.path.isdir(p):
        print(f"Ошибка: папки {p} нет.")
        sys.exit(1)
    top = git(p, "rev-parse", "--show-toplevel")
    if top:
        p = os.path.abspath(top)
    if is_practice_repo(p):
        print(f"Ошибка: {p} — это репозиторий практики pp03-ispo332, а нужна папка ВАШЕГО ПРОЕКТА.")
        print("Перейдите в папку проекта и запустите оттуда, например:")
        print("  cd C:\\xampp\\htdocs\\kait-library")
        print("  python ..\\pp03-ispo332\\tools\\repo_stats.py --out practice\\m01\\repo-stats.md")
        sys.exit(1)
    if not top:
        print(f"Ошибка: {p} — не git-репозиторий. Укажите папку, куда вы клонировали свой форк.")
        if os.path.basename(p).lower().endswith(("-main", "-master")):
            print("Похоже, проект скачан ZIP-архивом (Code → Download ZIP): в таком архиве нет истории git.")
            print("Сделайте форк и клонируйте его: git clone https://github.com/ВАШ_ЛОГИН/kait-library.git")
        sys.exit(1)
    return p


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def write_or_print(text, out_path):
    if out_path:
        out_dir = os.path.dirname(os.path.abspath(out_path))
        if not os.path.isdir(out_dir):
            print(f"Ошибка: нет папки {out_dir}.")
            print("Сначала скопируйте шаблоны практики в проект: tools\\install.cmd (или install.ps1).")
            sys.exit(1)
        if "skeleton" in os.path.abspath(out_path).replace("\\", "/").split("/"):
            print("Ошибка: --out указывает в skeleton репозитория практики. Результат пишется в practice\\... ВАШЕГО проекта.")
            sys.exit(1)
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"Добавлено в {out_path}")
    else:
        print(text)
# ===== конец общих функций =====


def main():
    setup_console()
    ap = argparse.ArgumentParser(description="Статистика git-репозитория в формате Markdown")
    ap.add_argument("path", nargs="?", default=".", help=PATH_HELP)
    ap.add_argument("--out", help="дописать результат в файл")
    ap.add_argument("--top", type=int, default=10, help="сколько файлов показать в топе изменений")
    a = ap.parse_args()
    p = project_root(a.path)

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
