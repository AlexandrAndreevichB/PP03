#!/usr/bin/env bash
# Копирует папку practice/ и шаблоны .github/ в ваш проект.
# Существующие файлы НЕ перезаписываются.
# Использование: bash tools/install.sh /путь/к/вашему/проекту
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Использование: bash tools/install.sh /путь/к/вашему/проекту"
  exit 1
fi

TARGET="$1"
SRC="$(cd "$(dirname "$0")/.." && pwd)/skeleton"

if [ ! -d "$TARGET/.git" ]; then
  echo "Ошибка: в $TARGET нет папки .git — укажите путь к клонированному репозиторию вашего проекта."
  exit 1
fi

copied=0; skipped=0
while IFS= read -r -d '' file; do
  rel="${file#$SRC/}"
  dest="$TARGET/$rel"
  if [ -e "$dest" ]; then
    echo "  пропущен (уже есть): $rel"; skipped=$((skipped+1))
  else
    mkdir -p "$(dirname "$dest")"
    cp "$file" "$dest"
    echo "  + $rel"; copied=$((copied+1))
  fi
done < <(find "$SRC" -type f -print0)

chmod +x "$TARGET/practice/m11/pre-receive" 2>/dev/null || true
echo
echo "Готово: скопировано $copied, пропущено $skipped."
echo "Дальше:"
echo "  cd \"$TARGET\""
echo "  git add practice .github"
echo "  git commit -m \"chore: add practice skeleton\""
echo "  git push"
