@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0BUILD_DEV_LAUNCHER.ps1" %*
exit /b %errorlevel%
