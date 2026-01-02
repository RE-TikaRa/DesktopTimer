@echo off
echo Cleaning old build...
rmdir /s /q build
rmdir /s /q dist

echo Building...
python -m PyInstaller DesktopTimer.spec --noconfirm

echo Copying resource folders to dist...
set "DIST_DIR=dist"
if not exist "%DIST_DIR%" (
    mkdir "%DIST_DIR%"
)
for %%D in (img lang sounds settings) do (
    if exist "%%D" (
        echo   - %%D
        xcopy "%%D" "%DIST_DIR%\%%D\" /E /I /Y >nul
    ) else (
        echo   - Skipping %%D (folder not found)
    )
)

:zip
echo Packaging dist into DesktopTimer.zip...
if exist DesktopTimer.zip del /q DesktopTimer.zip
powershell -Command "Compress-Archive -Path '%DIST_DIR%\*' -DestinationPath 'DesktopTimer.zip' -Force"

:done
echo Done.
pause
