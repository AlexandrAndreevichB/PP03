# Копирует папку practice\ и шаблоны .github\ в ваш проект.
# Существующие файлы НЕ перезаписываются.
# Использование (из папки pp03-ispo332):
#   powershell -ExecutionPolicy Bypass -File tools\install.ps1 C:\путь\к\вашему\проекту
param(
  [Parameter(Position = 0)]
  [string]$Target = ""
)
if (-not $Target) {
  $Target = Read-Host "Перетащите сюда папку вашего проекта (форк kait-library) и нажмите Enter"
}
$Target = $Target.Trim().Trim('"')
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Src = Join-Path (Split-Path -Parent $PSScriptRoot) "skeleton"
$Target = (Resolve-Path $Target).Path

if (-not (Test-Path (Join-Path $Target ".git"))) {
  Write-Host "Ошибка: в $Target нет папки .git — укажите путь к клонированному репозиторию вашего проекта." -ForegroundColor Red
  exit 1
}

$copied = 0; $skipped = 0
Get-ChildItem -Path $Src -Recurse -File -Force | ForEach-Object {
  $rel = $_.FullName.Substring($Src.Length).TrimStart('\', '/')
  $dest = Join-Path $Target $rel
  if (Test-Path $dest) {
    Write-Host "  пропущен (уже есть): $rel"
    $skipped++
  } else {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dest) | Out-Null
    Copy-Item $_.FullName $dest
    Write-Host "  + $rel" -ForegroundColor Green
    $copied++
  }
}

Write-Host ""
Write-Host "Готово: скопировано $copied, пропущено $skipped."
Write-Host "Дальше:"
Write-Host "  cd `"$Target`""
Write-Host "  git add practice .github"
Write-Host "  git commit -m `"chore: add practice skeleton`""
Write-Host "  git push"
