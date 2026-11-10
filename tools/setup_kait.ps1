# Настройка «Библиотеки КАИТ» на Windows одной командой.
# Запуск из папки проекта (там, где лежат public\ и database\):
#   powershell -ExecutionPolicy Bypass -File setup_kait.ps1
# Параметры (необязательно): -DbUser root -DbPass "" -DbName kait_library
param(
    [string]$Project = (Get-Location).Path,
    [string]$DbUser = 'root',
    [string]$DbPass = '',
    [string]$DbName = 'kait_library'
)
$ErrorActionPreference = 'Continue'
$OutputEncoding = New-Object Text.UTF8Encoding($false)   # чтобы кириллица из SQL-файлов дошла до mysql без искажений

function Ok($m)   { Write-Host "[OK]  $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[!]   $m" -ForegroundColor Yellow }
function Fail($m) { Write-Host "[X]   $m" -ForegroundColor Red; exit 1 }

# --- 0. Папка проекта (архив мог распаковаться в kait-library\kait-library) ---
if (-not $Project) { $Project = (Get-Location).Path }
$Project = $Project.Trim().Trim('"')
if (-not (Test-Path (Join-Path $Project 'public'))) {
    $inner = Get-ChildItem $Project -Directory -ErrorAction SilentlyContinue | Where-Object { Test-Path (Join-Path $_.FullName 'public') } | Select-Object -First 1
    if (-not $inner) {
        Write-Host "Папка проекта не найдена: $Project"
        $Project = (Read-Host "Перетащите сюда папку kait-library (или вставьте путь) и нажмите Enter").Trim().Trim('"')
    }
}
if (-not (Test-Path (Join-Path $Project 'public'))) {
    $inner = Get-ChildItem $Project -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'public') } | Select-Object -First 1
    if ($inner) { $Project = $inner.FullName } else { Fail "В $Project нет папки public. Запустите скрипт из папки проекта." }
}
Ok "Проект: $Project"

# --- 1. PHP ---
# если MySQL/Apache уже запущены, путь к XAMPP/OpenServer берём из процесса
$roots = @()
foreach ($pn in 'mysqld', 'mariadbd', 'httpd') {
    Get-Process $pn -ErrorAction SilentlyContinue | ForEach-Object {
        try { if ($_.Path) { $roots += (Split-Path (Split-Path (Split-Path $_.Path))) } } catch {}
    }
}
$php = $null
foreach ($r in ($roots | Select-Object -Unique)) {
    if (Test-Path "$r\php\php.exe") { $php = "$r\php\php.exe"; break }
}
if (-not $php) { $php = (Get-Command php -ErrorAction SilentlyContinue).Source }
$needPath = -not (Get-Command php -ErrorAction SilentlyContinue)
if (-not $php) {
    $candidates = @()
    foreach ($d in 'C','D','E') {
        $candidates += "${d}:\xampp\php\php.exe"
        $candidates += Get-ChildItem "${d}:\OSPanel\modules\php\*\php.exe", "${d}:\OpenServer\modules\php\*\php.exe", "${d}:\OSPanel\modules\PHP*\php.exe" -ErrorAction SilentlyContinue |
            Sort-Object FullName -Descending | ForEach-Object { $_.FullName }
    }
    $php = $candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
    if (-not $php) { Fail "php.exe не найден. Установите XAMPP (https://www.apachefriends.org) и запустите скрипт снова." }
}
if ($needPath) {
    $phpDir = Split-Path $php
    $userPath = [string][Environment]::GetEnvironmentVariable('Path', 'User')
    if (($userPath -split ';') -notcontains $phpDir) {
        [Environment]::SetEnvironmentVariable('Path', ($userPath.TrimEnd(';') + ';' + $phpDir), 'User')
        Ok "PHP добавлен в PATH: $phpDir (перезапустите VS Code, чтобы он это увидел)"
    }
    $env:Path += ";$phpDir"
}
Ok ("PHP: " + (& $php -r 'echo PHP_VERSION;') + "  ($php)")
if (-not ((& $php -m) -contains 'pdo_mysql')) { Warn "В php.ini не включено расширение pdo_mysql (строка extension=pdo_mysql)" }

# --- 2. MySQL: найти клиент и создать БД ---
$mysql = $null
Get-Process mysqld, mariadbd -ErrorAction SilentlyContinue | ForEach-Object {
    try { $c = Join-Path (Split-Path $_.Path) 'mysql.exe'; if (-not $mysql -and (Test-Path $c)) { $mysql = $c } } catch {}
}
if (-not $mysql) { $mysql = (Get-Command mysql -ErrorAction SilentlyContinue).Source }
if (-not $mysql) {
    $candidates = @()
    foreach ($d in 'C','D','E') {
        $candidates += "${d}:\xampp\mysql\bin\mysql.exe"
        $candidates += Get-ChildItem "${d}:\OSPanel\modules\*\*\bin\mysql.exe", "${d}:\OSPanel\modules\*\bin\mysql.exe", "${d}:\OpenServer\modules\database\*\bin\mysql.exe" -ErrorAction SilentlyContinue |
            Sort-Object FullName -Descending | ForEach-Object { $_.FullName }
    }
    $mysql = $candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
}
if (-not $mysql) { Fail "mysql.exe не найден. Установите XAMPP." }

$auth = @('-u', $DbUser, '--default-character-set=utf8mb4')
if ($DbPass -ne '') { $auth += "-p$DbPass" }

& $mysql @auth -e 'SELECT 1' *> $null
if ($LASTEXITCODE -ne 0) { Fail "MySQL не отвечает. Запустите MySQL в панели XAMPP (кнопка Start) и повторите. Если у root есть пароль: -DbPass пароль" }
Ok "MySQL запущен ($mysql)"

$exists = & $mysql @auth -N -e "SHOW DATABASES LIKE '$DbName'"
if ($exists) {
    Warn "База $DbName уже есть — не трогаю. Чтобы пересоздать: удалите её в phpMyAdmin и запустите скрипт снова."
} else {
    & $mysql @auth -e "CREATE DATABASE $DbName CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
    foreach ($f in 'schema.sql', 'seed.sql') {
        $sql = Join-Path $Project "database\$f"
        Get-Content $sql -Raw -Encoding UTF8 | & $mysql @auth $DbName
        if ($LASTEXITCODE -ne 0) { Fail "Ошибка импорта $f" }
        Ok "Импортирован database\$f"
    }
}

# --- 3. .env ---
$envFile = Join-Path $Project '.env'
if (-not (Test-Path $envFile)) {
    $lines = (Get-Content (Join-Path $Project '.env.example') -Encoding UTF8) `
        -replace '^DB_USER=.*', "DB_USER=$DbUser" `
        -replace '^DB_PASS=.*', "DB_PASS=$DbPass" `
        -replace '^DB_NAME=.*', "DB_NAME=$DbName" `
        -replace '^DB_HOST=.*', 'DB_HOST=127.0.0.1'
    [IO.File]::WriteAllLines($envFile, [string[]]$lines, (New-Object Text.UTF8Encoding($false)))
    Ok "Создан .env"
} else { Ok ".env уже есть" }

# --- 4. VS Code: запуск встроенного сервера с отладкой ---
$vs = Join-Path $Project '.vscode'
New-Item -ItemType Directory -Force $vs | Out-Null
$launch = @"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Библиотека КАИТ (localhost:8000)",
      "type": "php",
      "request": "launch",
      "runtimeExecutable": "$($php -replace '\\', '\\')",
      "runtimeArgs": ["-S", "localhost:8000", "-t", "."],
      "cwd": "$((Join-Path $Project 'public') -replace '\\', '\\')",
      "port": 9003,
      "serverReadyAction": { "pattern": "Development Server \\(http://localhost:([0-9]+)\\) started", "uriFormat": "http://localhost:%s", "action": "openExternally" }
    }
  ]
}
"@
[IO.File]::WriteAllText((Join-Path $vs 'launch.json'), $launch, (New-Object Text.UTF8Encoding($false)))
Ok "Создан .vscode\launch.json (F5 в VS Code запускает сайт)"

Write-Host ""
Write-Host "Готово. Запуск сайта:" -ForegroundColor Cyan
Write-Host "  cd `"$Project`""
Write-Host "  & `"$php`" -S localhost:8000 -t public"
Write-Host "  затем откройте http://localhost:8000  (или нажмите F5 в VS Code)"
Write-Host "В новом окне терминала достаточно: php -S localhost:8000 -t public"
Write-Host "Вход: librarian@kait20.ru / password (библиотекарь), ivanov@student.kait20.ru / password (читатель)"
