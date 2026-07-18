@echo off
title Taska - build
rem "python" из PATH может быть заглушкой Windows Store — ищем настоящий интерпретатор
set "PY=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" --version >nul 2>&1 || set "PY=py -3"

echo ============================================
echo   Installing dependencies...
echo ============================================
%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt
if errorlevel 1 goto fail

echo.
echo ============================================
echo   Generating icons (gen_icons.py)...
echo ============================================
%PY% gen_icons.py
if errorlevel 1 goto fail

echo.
echo ============================================
echo   Building app (onedir, this takes a couple minutes)...
echo ============================================
rmdir /s /q build 2>nul
rmdir /s /q dist\Taska 2>nul
%PY% -m PyInstaller --noconfirm --windowed --onedir --name "Taska" --icon "icon.ico" --add-data "board.html;." --add-data "icon.png;." --add-data "icon.ico;." app.py
if errorlevel 1 goto fail

echo.
echo ============================================
echo   Building installer (Inno Setup)...
echo ============================================
"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" Taska.iss
if errorlevel 1 goto fail

echo.
echo ============================================
echo   Done!  Installer is here:  installer\TaskaSetup.exe
echo ============================================
echo Upload it to a GitHub release with asset name exactly TaskaSetup.exe
echo Board data is saved in %%APPDATA%%\Taska
echo.
pause
exit /b 0

:fail
echo.
echo [!] Something went wrong - copy the error text above.
echo     Make sure Python is installed and ticked "Add to PATH".
pause
exit /b 1
