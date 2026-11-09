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

# Что должно лежать в practice/mNN. Строка с * — шаблон имени (достаточно одного совпадения).
REQUIRED = {
    1: ["passport.md", "repo-stats.md", "*.png"],
    2: ["dfd.drawio", "dfd-0.png", "dfd-1.png", "trace.md", "input-points.md", "*.har"],
    3: ["metrics.md", "metrics-raw.md", "*.png"],
    4: ["README.md", "*.code-profile", "*settings*.zip|*.vssettings", "*empty-diff*.png"],
    # модули 5–13 добавляются вместе с материалами следующих недель
}
# Файлы в корне проекта, которые должны появиться к концу модуля
ROOT_FILES = {
    4: [".gitattributes", ".editorconfig", ".vscode/settings.json", ".vscode/extensions.json", "CONTRIBUTING.md"],
}


def extra_checks(root, m):
    """Проверки содержимого, специфичные для модуля."""
    problems = []
    if m == 3:
        raw = os.path.join(root, "practice", "m03", "metrics-raw.md")
        if os.path.isfile(raw):
            with open(raw, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            for label in ("М03 до", "М03 после"):
                if label not in text:
                    problems.append(f"в metrics-raw.md нет замера «{label}» (metrics.py --label \"{label}\")")
    if m == 4:
        import glob as _glob
        linter_files = ["phpcs.xml", "phpcs.xml.dist", ".phpcs.xml", "pint.json", ".php-cs-fixer.php", ".php-cs-fixer.dist.php",
                        "eslint.config.*", ".eslintrc*", ".prettierrc*", "prettier.config.*", "biome.json",
                        "ruff.toml", ".ruff.toml", ".flake8", "setup.cfg",
                        "checkstyle.xml", "config/checkstyle/checkstyle.xml", "detekt.yml", "config/detekt/detekt.yml",
                        "stylecop.json", ".globalconfig", "Directory.Build.props"]
        found = any(_glob.glob(os.path.join(root, pat)) for pat in linter_files)
        if not found and os.path.isfile(os.path.join(root, "pyproject.toml")):
            with open(os.path.join(root, "pyproject.toml"), encoding="utf-8", errors="replace") as fh:
                found = "[tool.ruff" in fh.read()
        if not found and os.path.isfile(os.path.join(root, ".editorconfig")):
            with open(os.path.join(root, ".editorconfig"), encoding="utf-8", errors="replace") as fh:
                ec = fh.read()
            found = any(k in ec for k in ("ktlint", "dotnet_", "csharp_"))   # Kotlin и C# хранят правила линтера в .editorconfig
        if not found:
            problems.append("в корне проекта нет файла правил линтера (phpcs.xml, eslint.config.js, ruff.toml, checkstyle.xml …) — см. шаг 3 М4")
        eol = git(root, "ls-files", "--eol").splitlines()
        crlf = [ln.split("\t")[-1] for ln in eol if ln.startswith("i/crlf") and not ln.rstrip().endswith((".cmd", ".bat"))]
        if crlf:
            problems.append("в репозитории есть файлы с CRLF: " + ", ".join(crlf[:5]) + " — см. шаг 1 М4 (.gitattributes)")
        contrib = os.path.join(root, "CONTRIBUTING.md")
        if os.path.isfile(contrib):
            with open(contrib, encoding="utf-8", errors="replace") as fh:
                c = fh.read().count("TODO")
            if c:
                problems.append(f"в CONTRIBUTING.md не заполнено TODO: {c}")
    return problems


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
    problems += extra_checks(root, m)
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
    ap.add_argument("path", nargs="?", default=".", help=PATH_HELP)
    ap.add_argument("--module", type=int, choices=range(1, 14), metavar="1..13")
    a = ap.parse_args()
    root = project_root(a.path)
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
