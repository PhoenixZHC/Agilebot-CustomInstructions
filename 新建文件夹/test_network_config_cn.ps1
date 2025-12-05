# 网络配置测试脚本

chcp 65001 | Out-Null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    网络配置工具 - 测试版" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "错误：需要管理员权限！" -ForegroundColor Red
    Write-Host "请右键点击脚本，选择以管理员身份运行" -ForegroundColor Yellow
    $null = Read-Host "按Enter键退出"
    exit 1
}

Write-Host "管理员权限检查通过" -ForegroundColor Green
Write-Host ""

# 获取网络适配器
Write-Host "正在获取网络适配器..." -ForegroundColor Yellow
try {
    $adapters = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Select-Object -ExpandProperty Name
    if ($adapters) {
        Write-Host "找到以下网络适配器：" -ForegroundColor Green
        for ($i = 0; $i -lt $adapters.Count; $i++) {
            Write-Host "  [$($i + 1)] $($adapters[$i])" -ForegroundColor Cyan
        }
    }
    else {
        Write-Host "未找到已连接的网络适配器" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "获取适配器失败，尝试使用netsh..." -ForegroundColor Yellow
    try {
        $result = netsh interface show interface
        Write-Host $result
    }
    catch {
        Write-Host "错误：无法获取网络适配器" -ForegroundColor Red
        Write-Host "错误信息: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "测试完成！" -ForegroundColor Green
$null = Read-Host "按Enter键退出"

