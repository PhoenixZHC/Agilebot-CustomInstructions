@echo off
chcp 65001 >nul 2>&1
title 网络配置工具 - 更新MAC地址
mode con: cols=120 lines=9999 >nul 2>&1

cd /d "%~dp0"

if not exist "network_config_simple.ps1" (
    echo.
    echo [错误] 找不到PowerShell脚本文件: network_config_simple.ps1
    echo.
    echo 请确保 network_config_simple.ps1 文件与此批处理文件在同一目录下。
    echo.
    pause >nul
    exit /b 1
)

net session >nul 2>&1
if errorlevel 1 (
    echo.
    echo [信息] 需要管理员权限，正在请求提升权限...
    echo.
    echo 如果出现UAC提示，请点击"是"允许运行。
    echo.
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell.exe -Verb RunAs -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-NoExit','-File',(Resolve-Path 'network_config_simple.ps1').Path)"
    exit /b
)

echo.
echo [信息] 正在启动网络配置工具...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "network_config_simple.ps1"

if errorlevel 1 (
    echo.
    echo [错误] 脚本执行失败，错误代码: %errorLevel%
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b 1
)

echo.
echo [信息] 脚本执行完成
echo 按任意键退出...
pause >nul
exit /b 0

