@echo off
echo Cleaning old build...
rmdir /s /q build
rmdir /s /q dist

echo Building...
python -m PyInstaller DesktopTimer.spec --noconfirm

echo Done.
pause
