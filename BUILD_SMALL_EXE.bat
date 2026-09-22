@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0BUILD_SMALL_EXE.ps1"
if errorlevel 1 (
  echo.
  echo Small-EXE build failed.
  pause
  exit /b 1
)
echo.
echo Small-EXE build completed successfully.
pause
