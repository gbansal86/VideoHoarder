@echo off
setlocal
title VideoHoarder - Self-Contained Release Build and Deploy
cd /d "%~dp0"
echo ============================================================
echo VideoHoarder Self-Contained Release Build and Deploy
echo ============================================================
echo This will test, build, back up, deploy, and verify the self-contained release.
echo It builds VideoHoarder.spec, runs the complete pytest and native
echo PySide6 gates, performs an EXE-only clean-room self-test, then deploys.
echo The lightweight configured source/build-environment launcher is built separately
echo with BUILD_DEV_LAUNCHER.bat.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0BUILD_WINDOWS.ps1" -CleanTempAfterBuild -Deploy
if errorlevel 1 (
  echo.
  echo BUILD OR DEPLOY FAILED. Review the evidence above.
  pause
  exit /b 1
)
echo.
echo SUCCESS - self-contained release built, clean-room tested and deployed.
pause
exit /b 0
