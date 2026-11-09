@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem Копирует practice\ и .github\ в ваш проект. Существующие файлы не перезаписываются.
rem Запуск: двойной щелчок или перетащить папку проекта на этот файл. PowerShell не нужен.

set "SRC=%~dp0..\skeleton"
set "T=%~1"
if not defined T set /p "T=Перетащите сюда папку вашего проекта - форка kait-library - и нажмите Enter: "
set "T=!T:"=!"
if not exist "!T!\.git" (
  echo [X] В папке !T! нет .git - укажите папку, куда вы клонировали свой форк.
  goto :end
)
robocopy "!SRC!" "!T!" /E /XC /XN /XO /NJH /NJS /NDL /NP
if errorlevel 8 (
  echo [X] Ошибка копирования
  goto :end
)
echo.
echo [OK] Шаблоны скопированы, уже существующие файлы не тронуты.
echo Дальше выполните:
echo   cd /d "!T!"
echo   git switch -c practice/m01
echo   git add practice .github
echo   git commit -m "chore: add practice skeleton"
echo   git push -u origin practice/m01

:end
echo.
pause
exit /b
