"""Общие функции для скриптов практики. Только стандартная библиотека Python 3.8+."""
import os
import subprocess
import sys

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


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def write_or_print(text, out_path):
    if out_path:
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"Добавлено в {out_path}")
    else:
        print(text)
