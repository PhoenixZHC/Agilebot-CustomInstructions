# 网络配置工具 - 简化命令行版本

# 设置编码
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Clear-Host
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    网络配置工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "错误：此脚本需要管理员权限！" -ForegroundColor Red
    Write-Host "请右键点击脚本，选择以管理员身份运行" -ForegroundColor Yellow
    Write-Host ""
    $null = Read-Host "按Enter键退出"
    exit 1
}

# 计算子网掩码
function Get-SubnetMask {
    param([string]$IpAddress)
    try {
        $ip = [System.Net.IPAddress]::Parse($IpAddress)
        $bytes = $ip.GetAddressBytes()
        if ($bytes[0] -eq 10) {
            return "255.0.0.0"
        }
        elseif ($bytes[0] -eq 172 -and $bytes[1] -ge 16 -and $bytes[1] -le 31) {
            return "255.255.0.0"
        }
        elseif ($bytes[0] -eq 192 -and $bytes[1] -eq 168) {
            return "255.255.255.0"
        }
        else {
            return "255.255.255.0"
        }
    }
    catch {
        return "255.255.255.0"
    }
}

# 根据控制柜IP计算建议的本地IP（同网段，最后一位=1）
function Get-SuggestedLocalIP {
    param([string]$ControlIP)
    try {
        $ip = [System.Net.IPAddress]::Parse($ControlIP)
        $bytes = $ip.GetAddressBytes()
        $bytes[3] = 1
        $localIP = [System.Net.IPAddress]::new($bytes)
        return $localIP.ToString()
    }
    catch {
        return $null
    }
}

# 检查两个IP是否在同一网段
function Test-SameSubnet {
    param(
        [string]$IP1,
        [string]$IP2,
        [string]$SubnetMask
    )
    try {
        $ip1Obj = [System.Net.IPAddress]::Parse($IP1)
        $ip2Obj = [System.Net.IPAddress]::Parse($IP2)
        $maskObj = [System.Net.IPAddress]::Parse($SubnetMask)

        $ip1Bytes = $ip1Obj.GetAddressBytes()
        $ip2Bytes = $ip2Obj.GetAddressBytes()
        $maskBytes = $maskObj.GetAddressBytes()

        for ($i = 0; $i -lt 4; $i++) {
            if (($ip1Bytes[$i] -band $maskBytes[$i]) -ne ($ip2Bytes[$i] -band $maskBytes[$i])) {
                return $false
            }
        }
        return $true
    }
    catch {
        return $false
    }
}

# 验证IP地址格式
function Test-IPAddress {
    param([string]$IpAddress)
    try {
        $null = [System.Net.IPAddress]::Parse($IpAddress)
        return $true
    }
    catch {
        return $false
    }
}

# 获取网络适配器列表（包含详细信息）
function Get-NetworkAdapters {
    try {
        $allAdapters = Get-NetAdapter | Select-Object Name, Status, InterfaceDescription
        $adapterList = @()
        foreach ($adapter in $allAdapters) {
            $adapterList += @{
                Name = $adapter.Name
                Status = $adapter.Status
                Description = $adapter.InterfaceDescription
            }
        }
        return $adapterList
    }
    catch {
        try {
            $result = netsh interface show interface
            $adapters = @()
            $lines = $result -split "`n"
            foreach ($line in $lines) {
                if ($line.Trim() -and -not $line -match "状态|State|管理状态|Admin") {
                    $parts = $line -split '\s+', 4
                    if ($parts.Length -ge 4) {
                        $status = $parts[0]
                        $name = $parts[3]
                        $adapters += @{
                            Name = $name
                            Status = $status
                            Description = ""
                        }
                    }
                }
            }
            return $adapters
        }
        catch {
            return @()
        }
    }
}

# 转换子网掩码为前缀长度
function Get-PrefixLength {
    param([string]$SubnetMask)
    try {
        $mask = [System.Net.IPAddress]::Parse($SubnetMask)
        $bytes = $mask.GetAddressBytes()
        $prefix = 0
        foreach ($byte in $bytes) {
            $bits = 0
            $temp = $byte
            while ($temp -gt 0) {
                if (($temp -band 1) -eq 1) {
                    $bits++
                }
                $temp = $temp -shr 1
            }
            $prefix += $bits
        }
        return $prefix
    }
    catch {
        # 如果计算失败，默认使用/24
        return 24
    }
}

# 设置静态IP地址
function Set-StaticIP {
    param(
        [string]$AdapterName,
        [string]$IPAddress,
        [string]$SubnetMask,
        [string]$Gateway = $null
    )
    try {
        # 首先删除现有的静态IP配置
        Write-Host "正在删除现有IP配置..." -ForegroundColor Yellow
        netsh interface ipv4 delete address name="$AdapterName" address=$IPAddress 2>&1 | Out-Null

        # 如果存在网关，也尝试删除
        if ($Gateway) {
            netsh interface ipv4 delete route 0.0.0.0/0 "$AdapterName" $Gateway 2>&1 | Out-Null
        }

        # 等待删除完成
        Start-Sleep -Milliseconds 500

        # 现在设置新的IP配置
        Write-Host "正在设置新IP配置..." -ForegroundColor Yellow
        if ($Gateway) {
            # 一次性设置IP、掩码和网关
            $result = netsh interface ipv4 set address name="$AdapterName" source=static address=$IPAddress mask=$SubnetMask gateway=$Gateway 2>&1
            $exitCode = $LASTEXITCODE
        }
        else {
            # 只设置IP和掩码
            $result = netsh interface ipv4 set address name="$AdapterName" source=static address=$IPAddress mask=$SubnetMask 2>&1
            $exitCode = $LASTEXITCODE
        }

        if ($exitCode -eq 0) {
            if ($Gateway) {
                return $true, "IP配置成功！(IP: $IPAddress, 掩码: $SubnetMask, 网关: $Gateway)"
            }
            else {
                return $true, "IP配置成功！(IP: $IPAddress, 掩码: $SubnetMask)"
            }
        }
        else {
            $errorMsg = if ($result) { $result -join "`n" } else { "未知错误" }
            # 如果错误是"对象已存在"，尝试使用替代方法
            if ($errorMsg -like "*already exists*" -or $errorMsg -like "*已存在*") {
                Write-Host "尝试使用替代方法..." -ForegroundColor Yellow
                # 尝试使用New-NetIPAddress (PowerShell cmdlet)
                try {
                    Remove-NetIPAddress -InterfaceAlias "$AdapterName" -Confirm:$false -ErrorAction SilentlyContinue
                    if ($Gateway) {
                        New-NetIPAddress -InterfaceAlias "$AdapterName" -IPAddress $IPAddress -PrefixLength (Get-PrefixLength -SubnetMask $SubnetMask) -DefaultGateway $Gateway -ErrorAction Stop
                    }
                    else {
                        New-NetIPAddress -InterfaceAlias "$AdapterName" -IPAddress $IPAddress -PrefixLength (Get-PrefixLength -SubnetMask $SubnetMask) -ErrorAction Stop
                    }
                    return $true, "IP配置成功（使用替代方法）！"
                }
                catch {
                    return $false, "配置失败。错误: $_"
                }
            }
            return $false, "配置失败。错误代码: $exitCode。详情: $errorMsg"
        }
    }
    catch {
        return $false, "发生错误: $_"
    }
}

# 主程序
Write-Host "正在获取网络适配器列表..." -ForegroundColor Yellow
$adapters = Get-NetworkAdapters

if ($adapters.Count -eq 0) {
    Write-Host "错误：未找到网络适配器！" -ForegroundColor Red
    Write-Host ""
    $null = Read-Host "按Enter键退出"
    exit 1
}

Write-Host "找到以下网络适配器：" -ForegroundColor Green
Write-Host ""
for ($i = 0; $i -lt $adapters.Count; $i++) {
    $adapter = $adapters[$i]
    $statusColor = if ($adapter.Status -eq "Up" -or $adapter.Status -eq "已连接" -or $adapter.Status -eq "Connected") { "Green" } else { "Yellow" }
    $statusText = if ($adapter.Status -eq "Up" -or $adapter.Status -eq "已连接" -or $adapter.Status -eq "Connected") { "已连接" } else { $adapter.Status }

    Write-Host "  [$($i + 1)] $($adapter.Name)" -ForegroundColor Cyan -NoNewline
    Write-Host " - 状态: " -NoNewline
    Write-Host $statusText -ForegroundColor $statusColor -NoNewline
    if ($adapter.Description) {
        Write-Host " ($($adapter.Description))" -ForegroundColor Gray
    }
    else {
        Write-Host ""
    }
}
Write-Host ""

# 选择适配器
$adapterIndex = -1
while ($adapterIndex -lt 1 -or $adapterIndex -gt $adapters.Count) {
    Write-Host "请选择网络适配器 (1-$($adapters.Count)): " -ForegroundColor Yellow -NoNewline
    $input = Read-Host
    if ([int]::TryParse($input, [ref]$adapterIndex)) {
        if ($adapterIndex -lt 1 -or $adapterIndex -gt $adapters.Count) {
            Write-Host "无效的选择，请重新输入！" -ForegroundColor Red
            $adapterIndex = -1
        }
    }
    else {
        Write-Host "无效的输入，请输入数字！" -ForegroundColor Red
    }
}

$selectedAdapter = $adapters[$adapterIndex - 1].Name
Write-Host "已选择适配器: $selectedAdapter" -ForegroundColor Green
Write-Host ""

# 输入控制柜IP地址
Write-Host "请输入控制柜IP地址: " -ForegroundColor Yellow -NoNewline
$controlIP = Read-Host

if (-not $controlIP -or -not (Test-IPAddress $controlIP)) {
    Write-Host "错误：IP地址格式不正确！" -ForegroundColor Red
    Write-Host ""
    $null = Read-Host "按Enter键退出"
    exit 1
}

# 自动计算子网掩码
$subnetMask = Get-SubnetMask -IpAddress $controlIP

# 自动计算本地IP（同网段，前3个字节相同，最后一位随机生成2-255）
$controlIPObj = [System.Net.IPAddress]::Parse($controlIP)
$controlBytes = $controlIPObj.GetAddressBytes()
$localBytes = $controlBytes.Clone()
# 生成2-255之间的随机数作为最后一位
$random = Get-Random -Minimum 2 -Maximum 256
$localBytes[3] = $random
$localIP = ([System.Net.IPAddress]::new($localBytes)).ToString()

Write-Host ""
Write-Host "控制柜IP: $controlIP" -ForegroundColor Cyan
Write-Host "计算的本地IP: $localIP" -ForegroundColor Green
Write-Host "子网掩码: $subnetMask" -ForegroundColor Cyan
Write-Host ""
Write-Host "正在应用配置..." -ForegroundColor Yellow

# 应用配置
$success, $message = Set-StaticIP -AdapterName $selectedAdapter -IPAddress $localIP -SubnetMask $subnetMask -Gateway $null

Write-Host ""
if ($success) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   配置成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "网络适配器: $selectedAdapter" -ForegroundColor White
    Write-Host "本地IP地址: $localIP" -ForegroundColor White
    Write-Host "子网掩码: $subnetMask" -ForegroundColor White
    Write-Host ""
    Write-Host "网络配置已成功应用！" -ForegroundColor Green
}
else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "   配置失败！" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host $message -ForegroundColor Red
    Write-Host ""
    Write-Host "请检查上面的错误信息并重试。" -ForegroundColor Yellow
}

Write-Host ""
$null = Read-Host "按Enter键退出"

