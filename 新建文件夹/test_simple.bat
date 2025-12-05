@echo off
chcp 65001 >nul
title Network Config Test

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0test_network_config.ps1"

pause
