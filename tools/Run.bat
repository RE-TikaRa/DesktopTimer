@echo off
setlocal
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "C_RESET=%ESC%[0m"
set "C_GREEN=%ESC%[32m"
set "C_CYAN=%ESC%[36m"
echo.
echo %C_CYAN%=========================%C_RESET%
echo %C_CYAN%DesktopTimer Run (UV)%C_RESET%
echo %C_CYAN%=========================%C_RESET%
echo.
uv run python main.py
echo.
echo %C_GREEN%Done.%C_RESET%
pause
