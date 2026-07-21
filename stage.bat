@echo off
title Taska STAGE
rem Стейдж-версия: запускает приложение прямо из исходников (app.py + board.html),
rem БЕЗ сборки и установки. Что видишь здесь — то попадёт в следующий релиз.
rem Данные общие с установленной Taska, поэтому она закрывается автоматически.
taskkill /im Taska.exe /f >nul 2>&1
set "PY=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
if not exist "%PY%" set "PY=python"
cd /d "%~dp0"
echo === Taska STAGE: запуск из исходников (закрой окно, чтобы выйти) ===
"%PY%" app.py
