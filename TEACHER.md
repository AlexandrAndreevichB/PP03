# Для руководителя практики

## Учебный проект «Библиотека КАИТ»

Проект лежит отдельно — архив `kait-library.zip` (внутри уже есть `.git` с историей: 38 коммитов, 3 ветки, тег `v1.0`).
Ключ с заложенными дефектами — `Ключ_Библиотека_КАИТ_для_руководителя.pdf`; **в этот репозиторий и в репозиторий проекта его не кладите**.

```
cd kait-library
git remote add origin git@github.com:ЛОГИН/kait-library.git
git push -u origin --all
git push origin --tags
```

Репозиторий проекта — публичный. Студенты делают форк, сняв галочку *Copy the main branch only*.

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

## Неделя 2 (модули 3–4)

- Перед 09.11: `git push` обновлённого репозитория; студенты делают `git pull` и ещё раз запускают `tools/install.cmd` — появятся `practice/m03`, `practice/m04`.
- Поставить вторую среду (Apache NetBeans от Codelerity или PhpStorm) на компьютеры класса заранее — установщик около 500 МБ.
- Проверка в М4 — в паре (по желанию студентов) или самостоятельно в чистом окружении; пары не назначаются обязательно.
- Линтер PHP_CodeSniffer уже лежит в `tools/php/`, ставить его не нужно — нужен только `php` в командной строке.
- Ожидаемые числа и типичные ошибки — в отдельном файле `Ключ_неделя2_для_руководителя.pdf` (в репозиторий не класть).

## Неделя 3 (модули 5–7)

- Перед 13.11: `git push` обновлённого репозитория; студенты — `git pull` и снова `tools/install.cmd`.
- Поставить на компьютеры класса: LibreOffice, ONLYOFFICE Desktop Editors, МойОфис (домашняя версия); Firefox, Яндекс Браузер; OBS Studio, VLC, MPC-HC, mpv.net. Для бенчмарков браузеров нужен интернет.
- Таблица расчёта для всех трёх модулей — `templates/week3/weighted-score.xlsx`.
- Ожидаемые результаты и типичные ошибки — `Ключ_неделя3_для_руководителя.pdf` (в репозиторий не класть).
