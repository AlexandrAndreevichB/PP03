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
    ap.add_argument("path", nargs="?", default=".", help=PATH_HELP)
    ap.add_argument("--label", default="", help="подпись замера, например «М03 до»")
    ap.add_argument("--out", help="дописать результат в файл")
    ap.add_argument("--ccn", type=int, default=10, help="порог сложности (по умолчанию 10)")
    ap.add_argument("--long", type=int, default=50, help="порог длины функции в строках (50)")
    a = ap.parse_args()
    root = project_root(a.path)

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
