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
echo   Building .exe (this takes a couple minutes)...
echo ============================================
python -m PyInstaller --noconfirm --windowed --onefile --name "Taska" --icon "icon.ico" --add-data "board.html;." --add-data "icon.png;." --add-data "icon.ico;." app.py
if errorlevel 1 goto fail

echo.
echo ============================================
echo   Done!  Your app is here:  dist\Taska.exe
echo ============================================
echo Copy Taska.exe anywhere and run it.
echo Board data is saved next to the exe as drive-board.json
echo.
pause
exit /b 0

:fail
echo.
echo [!] Something went wrong - copy the error text above.
echo     Make sure Python is installed and ticked "Add to PATH".
pause
exit /b 1
