@echo off
title Taska - build
echo ============================================
echo   Installing dependencies...
echo ============================================
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 goto fail

echo.
echo ============================================
echo   Building app (onedir, this takes a couple minutes)...
echo ============================================
rmdir /s /q build 2>nul
rmdir /s /q dist\Taska 2>nul
python -m PyInstaller --noconfirm --windowed --onedir --name "Taska" --icon "icon.ico" --add-data "board.html;." --add-data "icon.png;." --add-data "icon.ico;." app.py
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
