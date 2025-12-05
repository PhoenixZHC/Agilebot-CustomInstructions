@echo off
chcp 65001 >nul
title 网络配置测试

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0test_network_config_cn.ps1"

pause

