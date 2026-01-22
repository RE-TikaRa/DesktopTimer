@echo off
setlocal
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "C_RESET=%ESC%[0m"
set "C_RED=%ESC%[31m"
set "C_GREEN=%ESC%[32m"
set "C_YELLOW=%ESC%[33m"
set "C_CYAN=%ESC%[36m"
echo.
echo %C_CYAN%======================================%C_RESET%
echo %C_CYAN%DesktopTimer Build (UV + PyInstaller)%C_RESET%
echo %C_CYAN%======================================%C_RESET%

echo %C_YELLOW%[1/5] Cleaning old build...%C_RESET%
if exist build (
    rmdir /s /q build
    echo   - build removed
)
if exist dist (
    rmdir /s /q dist
    echo   - dist removed
)
if exist DesktopTimer.zip (
    del /q DesktopTimer.zip
    echo   - DesktopTimer.zip removed
)

echo %C_YELLOW%[2/5] Syncing UV env...%C_RESET%
uv sync --dev
if errorlevel 1 goto :fail

echo %C_YELLOW%[3/5] Building exe...%C_RESET%
uv run python -m PyInstaller DesktopTimer.spec --noconfirm
if errorlevel 1 goto :fail

echo %C_YELLOW%[4/5] Copying resource folders...%C_RESET%
set "DIST_DIR=dist"
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"
for %%D in (img lang sounds) do (
    if exist "%%D" (
        echo   - %%D
        xcopy "%%D" "%DIST_DIR%\%%D\" /E /I /Y >nul
    ) else (
        echo   - Skipping %%D (folder not found)
    )
)

echo %C_YELLOW%[5/5] Packaging dist into DesktopTimer.zip...%C_RESET%
powershell -Command "Compress-Archive -Path '%DIST_DIR%\*' -DestinationPath 'DesktopTimer.zip' -Force"
if errorlevel 1 goto :fail

echo.
echo %C_GREEN%[OK]%C_RESET% Build complete.
echo EXE: %DIST_DIR%\DesktopTimer.exe
echo ZIP: DesktopTimer.zip
echo RES: %DIST_DIR%\img  %DIST_DIR%\lang  %DIST_DIR%\sounds
goto :done

:fail
echo.
echo %C_RED%[ERROR]%C_RESET% Build failed.
exit /b 1

:done
echo.
echo Done.
pause
