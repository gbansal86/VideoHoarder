@echo off
setlocal
title VideoHoarder - Create Code Parent Package

cd /d "%~dp0"

echo Creating clean VideoHoarder Code Parent handoff package...
echo Source: %~dp0
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0CREATE_CODE_PARENT_PACKAGE.ps1"
if errorlevel 1 (
    echo.
    echo FAILED: Could not create VideoHoarder_Code_Parent.zip.
    pause
    exit /b 1
)

echo.
echo SUCCESS: VideoHoarder_Code_Parent.zip created under the install root.
echo The temporary staging folder is removed by default.
echo.
pause
exit /b 0
