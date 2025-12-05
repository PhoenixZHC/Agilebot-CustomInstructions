@echo off
chcp 65001
title Network Config Tool - Debug

echo Starting script...
echo Current directory: %CD%
echo Script path: %~dp0network_config_simple.ps1
echo.

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Not running as administrator.
    echo Requesting administrator privileges...
    powershell -Command "Start-Process powershell.exe -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -NoExit -File \"%~dp0network_config_simple.ps1\"'"
    echo.
    echo A new window should open with administrator privileges.
    pause
    exit /b
)

echo Running as administrator.
echo Executing PowerShell script...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -NoExit -File "%~dp0network_config_simple.ps1"

echo.
echo PowerShell script execution finished.
echo Error code: %errorLevel%
echo.
pause

