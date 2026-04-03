@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT_DIR=%%~fI"
set "UV_LINK_MODE=copy"
pushd "%ROOT_DIR%" >nul
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "C_RESET=%ESC%[0m"
set "C_GREEN=%ESC%[32m"
set "C_RED=%ESC%[31m"
set "C_CYAN=%ESC%[36m"
echo.
echo %C_CYAN%=========================%C_RESET%
echo %C_CYAN%DesktopTimer Run (UV)%C_RESET%
echo %C_CYAN%=========================%C_RESET%
echo.
uv run python main.py
if errorlevel 1 goto :fail
echo.
echo %C_GREEN%Done.%C_RESET%
goto :done

:fail
echo.
echo %C_RED%[ERROR]%C_RESET% Run failed.

:done
popd >nul
pause
