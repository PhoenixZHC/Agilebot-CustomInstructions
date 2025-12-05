@echo off
chcp 65001 >nul
title 网络配置工具 - 简化版

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 正在请求管理员权限...
    powershell -Command "Start-Process powershell.exe -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -NoExit -File \"%~dp0network_config_simple_cn.ps1\"'"
    exit /b
)

:: 以管理员权限运行脚本
powershell.exe -NoProfile -ExecutionPolicy Bypass -NoExit -File "%~dp0network_config_simple_cn.ps1"

if %errorLevel% neq 0 (
    echo.
    echo 脚本执行失败，错误代码: %errorLevel%
    echo.
    pause
)
