@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem Настройка проекта kait-library на XAMPP. PowerShell не нужен.
rem Запуск: двойной щелчок или перетащить папку проекта на этот файл.
rem Перед запуском: панель XAMPP - MySQL - Start.

set "PROJ=%~1"
if not defined PROJ set "PROJ=%CD%"
call :findproj
if not defined OK (
  echo Папка проекта не найдена: !PROJ!
  set /p "PROJ=Перетащите сюда папку kait-library и нажмите Enter: "
  set "PROJ=!PROJ:"=!"
  call :findproj
)
if not defined OK (
  echo [X] В папке нет public\index.php - это не проект kait-library.
  goto :end
)
echo [OK] Проект: !PROJ!

rem ---- XAMPP ----
set "XAMPP="
for %%D in (C D E F) do if not defined XAMPP if exist "%%D:\xampp\php\php.exe" set "XAMPP=%%D:\xampp"
if not defined XAMPP (
  echo XAMPP не найден на дисках C, D, E, F.
  set /p "XAMPP=Введите путь к папке xampp, например C:\xampp : "
  set "XAMPP=!XAMPP:"=!"
)
if not exist "!XAMPP!\php\php.exe" (
  echo [X] Нет файла !XAMPP!\php\php.exe - установите XAMPP с https://www.apachefriends.org
  goto :end
)
set "PHP=!XAMPP!\php\php.exe"
set "MYSQL=!XAMPP!\mysql\bin\mysql.exe"
echo [OK] XAMPP: !XAMPP!

rem ---- MySQL ----
"!MYSQL!" -u root -e "SELECT 1" >nul 2>&1
if errorlevel 1 (
  echo [X] MySQL не отвечает. Откройте панель XAMPP, нажмите Start напротив MySQL и запустите этот файл снова.
  goto :end
)
echo [OK] MySQL запущен

set "DB=kait_library"
set "HAS="
"!MYSQL!" -u root -N -e "SHOW DATABASES LIKE '!DB!'" > "%TEMP%\kait_db.txt" 2>nul
for /f "usebackq delims=" %%L in ("%TEMP%\kait_db.txt") do set "HAS=1"
if defined HAS (
  echo [*] База !DB! уже есть - не трогаю. Чтобы создать заново, удалите её в phpMyAdmin и запустите файл снова.
) else (
  "!MYSQL!" -u root -e "CREATE DATABASE !DB! CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
  "!MYSQL!" -u root --default-character-set=utf8mb4 !DB! < "!PROJ!\database\schema.sql"
  if errorlevel 1 (
    echo [X] Ошибка импорта schema.sql
    goto :end
  )
  "!MYSQL!" -u root --default-character-set=utf8mb4 !DB! < "!PROJ!\database\seed.sql"
  if errorlevel 1 (
    echo [X] Ошибка импорта seed.sql
    goto :end
  )
  echo [OK] База !DB! создана, тестовые данные загружены
)

rem ---- .env ----
if exist "!PROJ!\.env" (
  echo [OK] Файл .env уже есть
) else (
  > "!PROJ!\.env" (
    echo APP_DEBUG=true
    echo DB_DRIVER=mysql
    echo DB_HOST=127.0.0.1
    echo DB_PORT=3306
    echo DB_NAME=!DB!
    echo DB_USER=root
    echo DB_PASS=
  )
  echo [OK] Создан .env
)

rem ---- VS Code: F5 запускает сайт ----
set "PHPJ=!PHP:\=\\!"
set "PUBJ=!PROJ:\=\\!\\public"
if not exist "!PROJ!\.vscode" mkdir "!PROJ!\.vscode"
> "!PROJ!\.vscode\launch.json" (
  echo {
  echo   "version": "0.2.0",
  echo   "configurations": [
  echo     {
  echo       "name": "kait-library localhost:8000",
  echo       "type": "php",
  echo       "request": "launch",
  echo       "runtimeExecutable": "!PHPJ!",
  echo       "runtimeArgs": ["-S", "localhost:8000", "-t", "."],
  echo       "cwd": "!PUBJ!",
  echo       "port": 9003
  echo     }
  echo   ]
  echo }
)
echo [OK] Создан .vscode\launch.json - в VS Code сайт запускается клавишей F5

echo.
echo Готово. Вход: librarian@kait20.ru / password - библиотекарь, ivanov@student.kait20.ru / password - читатель
echo Запуск сайта в любой момент:
echo   "!PHP!" -S localhost:8000 -t "!PROJ!\public"
echo   и открыть http://localhost:8000
echo.
set "RUN="
set /p "RUN=Запустить сайт сейчас? Y - да, Enter - нет: "
if /i "!RUN!"=="Y" (
  start "" "http://localhost:8000"
  echo Сайт работает, пока открыто это окно. Остановить - Ctrl+C.
  "!PHP!" -S localhost:8000 -t "!PROJ!\public"
)

:end
echo.
pause
exit /b

:findproj
set "OK="
if exist "!PROJ!\public\index.php" (
  set "OK=1"
  goto :eof
)
if exist "!PROJ!\kait-library\public\index.php" (
  set "PROJ=!PROJ!\kait-library"
  set "OK=1"
)
goto :eof
