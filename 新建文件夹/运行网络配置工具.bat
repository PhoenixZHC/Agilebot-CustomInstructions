@echo off
chcp 65001 >nul
title Network Configuration Tool

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process powershell.exe -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0network_config.ps1\"'"
    exit /b
)

:: Run script with admin rights
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0network_config.ps1"

pause
