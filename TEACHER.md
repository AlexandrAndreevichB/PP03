# Для руководителя практики

## Публикация

```
cd pp03-ispo332
git init -b main
git add .
git commit -m "ПП.03: материалы недели 1"
git remote add origin git@github.com:ЛОГИН/pp03-ispo332.git
git push -u origin main
```

Материалы следующих недель добавляются в этот же репозиторий: новые `modules/mNN.md`, папки `skeleton/practice/mNN/`,
шаблоны отчётов и строки в `tools/check_practice.py` (словарь `REQUIRED`). Студенты забирают их через `git pull`
и повторно запускают `tools/install` — уже существующие у них файлы не перезаписываются.

## Как проверять

- `practice/README.md` в репозитории студента — таблица статусов модулей.
- `python tools/check_practice.py <клон репозитория студента>` — всё ли на месте.
- История коммитов ветки `practice/mNN` — работа велась по ходу, а не одним коммитом.
- Отчёт `.docx` лежит в `practice/mNN/`.

Массовая проверка группы (ссылки на репозитории в `students.txt`, по одной на строку; Git Bash / Linux):
```
mkdir group && cd group
for url in $(cat ../students.txt); do git clone -q "$url"; done
for d in */; do echo "=== $d"; python ../pp03-ispo332/tools/check_practice.py "$d"; done > report.txt
```
