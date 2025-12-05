# Network Config Tool - Simple Command Line Version

# Set encoding for Chinese display
# 按照推荐方法设置UTF-8编码以正确显示中文（解决中文乱码问题）
# 使用 UTF8Encoding::new($false) 创建无BOM的UTF-8编码
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
# 设置控制台代码页为UTF-8
chcp 65001 | Out-Null

# 检查并设置控制台字体以支持中文显示
function Set-ConsoleFontForChinese {
    try {
        # 获取当前控制台字体
        $fontKey = "HKCU:\Console"
        $fontName = (Get-ItemProperty -Path $fontKey -Name "FaceName" -ErrorAction SilentlyContinue).FaceName

        # 推荐的支持中文的字体列表
        $recommendedFonts = @("新宋体", "NSimSun", "Consolas", "Microsoft YaHei Mono", "SimSun", "YaHei")

        # 检查当前字体是否支持中文
        $fontSupportsChinese = $false
        if ($fontName) {
            foreach ($recFont in $recommendedFonts) {
                if ($fontName -match $recFont) {
                    $fontSupportsChinese = $true
                    break
                }
            }
        }

        # 如果字体不支持中文，尝试设置推荐字体
        if (-not $fontSupportsChinese) {
            Write-Host ""
            Write-Host "提示：检测到控制台字体可能不支持中文显示" -ForegroundColor Yellow
            Write-Host "建议手动设置字体以确保中文正确显示：" -ForegroundColor Yellow
            Write-Host "  1. 右键点击窗口标题栏 -> 属性 -> 字体" -ForegroundColor Cyan
            Write-Host "  2. 选择支持中文的字体（推荐：新宋体、Consolas、Microsoft YaHei Mono）" -ForegroundColor Cyan
            Write-Host ""

            # 尝试自动设置字体（需要管理员权限）
            try {
                # 尝试设置为"新宋体"（NSimSun）
                Set-ItemProperty -Path $fontKey -Name "FaceName" -Value "NSimSun" -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $fontKey -Name "FontSize" -Value 0x00100000 -ErrorAction SilentlyContinue
                Write-Host "已尝试自动设置字体为新宋体" -ForegroundColor Green
            }
            catch {
                # 如果自动设置失败，提示用户手动设置
                Write-Host "无法自动设置字体，请手动设置" -ForegroundColor Yellow
            }
        }
    }
    catch {
        # 忽略错误，继续执行
    }
}

# 执行字体检查（仅在首次运行时显示提示）
Set-ConsoleFontForChinese

# Increase console buffer size to allow scrolling to see previous content
# Fix window and buffer size to prevent display issues when resizing
# Disable window resizing
try {
    # 禁用窗口大小调整（使用Windows API）
    Add-Type @"
        using System;
        using System.Runtime.InteropServices;
        public class Win32 {
            [DllImport("user32.dll")]
            public static extern IntPtr GetSystemMenu(IntPtr hWnd, bool bRevert);
            [DllImport("user32.dll")]
            public static extern int GetMenuItemCount(IntPtr hMenu);
            [DllImport("user32.dll")]
            public static extern bool DrawMenuBar(IntPtr hWnd);
            [DllImport("user32.dll")]
            public static extern bool RemoveMenu(IntPtr hMenu, uint uPosition, uint uFlags);
            [DllImport("kernel32.dll", ExactSpelling = true)]
            public static extern IntPtr GetConsoleWindow();
            public const uint MF_BYCOMMAND = 0x00000000;
            public const uint MF_GRAYED = 0x00000001;
            public const uint SC_SIZE = 0xF000;
            public const uint SC_MAXIMIZE = 0xF030;
        }
"@

    $consoleWindow = [Win32]::GetConsoleWindow()
    $systemMenu = [Win32]::GetSystemMenu($consoleWindow, $false)

    # 禁用窗口大小调整
    [Win32]::RemoveMenu($systemMenu, [Win32]::SC_SIZE, [Win32]::MF_BYCOMMAND)
    [Win32]::RemoveMenu($systemMenu, [Win32]::SC_MAXIMIZE, [Win32]::MF_BYCOMMAND)
    [Win32]::DrawMenuBar($consoleWindow)

    # 使用Windows API设置窗口样式，禁用大小调整
    Add-Type @"
        using System;
        using System.Runtime.InteropServices;
        public class Win32Style {
            [DllImport("user32.dll")]
            public static extern int GetWindowLong(IntPtr hWnd, int nIndex);
            [DllImport("user32.dll")]
            public static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);
            [DllImport("kernel32.dll", ExactSpelling = true)]
            public static extern IntPtr GetConsoleWindow();
            public const int GWL_STYLE = -16;
            public const int WS_SIZEBOX = 0x00040000;
            public const int WS_MAXIMIZEBOX = 0x00010000;
        }
"@

    try {
        $hwnd = [Win32Style]::GetConsoleWindow()
        $style = [Win32Style]::GetWindowLong($hwnd, [Win32Style]::GWL_STYLE)
        # 移除大小调整和最大化按钮
        $style = $style -band (-bnot [Win32Style]::WS_SIZEBOX)
        $style = $style -band (-bnot [Win32Style]::WS_MAXIMIZEBOX)
        [Win32Style]::SetWindowLong($hwnd, [Win32Style]::GWL_STYLE, $style)
    }
    catch {
        # 如果设置窗口样式失败，继续执行
    }
}
catch {
    # 如果禁用窗口大小调整失败，继续执行
}

try {
    $buffer = $Host.UI.RawUI.BufferSize
    $window = $Host.UI.RawUI.WindowSize
    $maxWindow = $Host.UI.RawUI.MaxWindowSize

    # Set fixed buffer width (120 characters)
    $buffer.Width = 120
    # Set large buffer height to allow scrolling (maximum 9999)
    $buffer.Height = 9999

    # Set window size - ensure it doesn't exceed buffer size
    $window.Width = [Math]::Min(120, $maxWindow.Width)
    $window.Height = [Math]::Min(50, $maxWindow.Height)

    # Apply buffer size first
    $Host.UI.RawUI.BufferSize = $buffer
    # Then apply window size
    $Host.UI.RawUI.WindowSize = $window

    # 确保缓冲区宽度和窗口宽度一致（防止滚动时叠字）
    Start-Sleep -Milliseconds 50
    $verifyBuffer = $Host.UI.RawUI.BufferSize
    $verifyWindow = $Host.UI.RawUI.WindowSize
    if ($verifyBuffer.Width -ne 120) {
        $verifyBuffer.Width = 120
        $Host.UI.RawUI.BufferSize = $verifyBuffer
    }
    if ($verifyWindow.Width -ne $verifyBuffer.Width) {
        $verifyWindow.Width = $verifyBuffer.Width
        $Host.UI.RawUI.WindowSize = $verifyWindow
    }

    # Set window title
    $Host.UI.RawUI.WindowTitle = "更新MAC地址"
}
catch {
    # If buffer size cannot be changed, continue anyway
}

# Function to fix window size if it gets resized
function Fix-WindowSize {
    try {
        $maxWindow = $Host.UI.RawUI.MaxWindowSize
        $targetWidth = [Math]::Min(120, $maxWindow.Width)
        $targetHeight = [Math]::Min(50, $maxWindow.Height)

        # 强制设置缓冲区宽度为120（固定），高度为9999
        $newBuffer = $Host.UI.RawUI.BufferSize
        $newBuffer.Width = 120
        $newBuffer.Height = 9999
        $Host.UI.RawUI.BufferSize = $newBuffer

        # 强制设置窗口大小为固定值
        $newWindow = $Host.UI.RawUI.WindowSize
        $newWindow.Width = $targetWidth
        $newWindow.Height = $targetHeight
        $Host.UI.RawUI.WindowSize = $newWindow

        # 等待一下让设置生效
        Start-Sleep -Milliseconds 20

        # 再次强制确保缓冲区宽度为120（防止窗口大小改变后缓冲区被修改）
        $finalBuffer = $Host.UI.RawUI.BufferSize
        if ($finalBuffer.Width -ne 120) {
            $finalBuffer.Width = 120
            $finalBuffer.Height = 9999
            $Host.UI.RawUI.BufferSize = $finalBuffer
        }

        # 再次确保窗口大小正确
        $finalWindow = $Host.UI.RawUI.WindowSize
        if ($finalWindow.Width -ne $targetWidth -or $finalWindow.Height -ne $targetHeight) {
            $finalWindow.Width = $targetWidth
            $finalWindow.Height = $targetHeight
            $Host.UI.RawUI.WindowSize = $finalWindow
        }

        # 第三次检查：确保缓冲区宽度和窗口宽度完全一致（防止滚动时叠字的关键）
        Start-Sleep -Milliseconds 20
        $verifyBuffer = $Host.UI.RawUI.BufferSize
        $verifyWindow = $Host.UI.RawUI.WindowSize
        if ($verifyBuffer.Width -ne 120) {
            $verifyBuffer.Width = 120
            $verifyBuffer.Height = 9999
            $Host.UI.RawUI.BufferSize = $verifyBuffer
        }
        # 确保窗口宽度与缓冲区宽度完全一致（这是防止滚动时叠字的关键）
        if ($verifyWindow.Width -ne $verifyBuffer.Width) {
            $verifyWindow.Width = $verifyBuffer.Width
            $Host.UI.RawUI.WindowSize = $verifyWindow
        }
    }
    catch {
        # 忽略窗口大小修复错误
    }
}

# Clear screen but keep buffer content
Clear-Host
# Fix window size after clear - 多次调用确保窗口大小正确
Fix-WindowSize
Start-Sleep -Milliseconds 100
Fix-WindowSize
Start-Sleep -Milliseconds 50
Fix-WindowSize
# Add some blank lines at the start to ensure buffer has space
Write-Host ""
Fix-WindowSize

# Check admin rights
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "错误：需要管理员权限！" -ForegroundColor Red
    Write-Host "请右键点击脚本，选择"以管理员身份运行"" -ForegroundColor Yellow
    Write-Host ""
    $null = Read-Host "按Enter键退出"
    exit 1
}

# Calculate subnet mask
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

# Calculate suggested local IP from control cabinet IP (same subnet, last byte = 1)
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

# Check if two IPs are in the same subnet
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

# Validate IP address format
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

# Generate MAC address based on current time (month, day, hour, minute, second) + random number
# Optimized to follow MAC address generation rules
function Get-RandomMAC {
    try {
        # Get current local time
        $now = Get-Date

        # Generate random number for additional uniqueness
        $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        $randomBytes = New-Object byte[] 3
        $rng.GetBytes($randomBytes)

        # Build MAC address from time components + random
        # MAC address format: 6 bytes (XX:XX:XX:XX:XX:XX)
        # Byte 1: Month (1-12) + random, ensure second nibble is even (locally administered)
        # Byte 2: Day (1-31)
        # Byte 3: Hour (0-23)
        # Byte 4: Minute (0-59)
        # Byte 5: Second (0-59)
        # Byte 6: Random (0-255)

        $macBytes = New-Object byte[] 6

        # Byte 1: Month (1-12) combined with random, ensure MAC address rule
        # Month is 1-12, we'll use it in the first nibble (0-15 range)
        # Second nibble must be 2, 6, A, or E for locally administered address
        $month = $now.Month
        $firstNibble = [Math]::Min($month - 1, 15)  # 0-11, but we want 0-15 range
        # Select second nibble from valid locally administered values: 2, 6, A, E
        $validSecondNibbles = @(0x02, 0x06, 0x0A, 0x0E)
        $secondNibbleIndex = ($randomBytes[0] -band 0x03)  # 0-3 to select from array
        $secondNibble = $validSecondNibbles[$secondNibbleIndex]
        $macBytes[0] = ($firstNibble -shl 4) -bor $secondNibble

        # Byte 2: Day (1-31)
        $macBytes[1] = [Math]::Min($now.Day, 255)

        # Byte 3: Hour (0-23)
        $macBytes[2] = $now.Hour

        # Byte 4: Minute (0-59)
        $macBytes[3] = $now.Minute

        # Byte 5: Second (0-59)
        $macBytes[4] = $now.Second

        # Byte 6: Random (0-255)
        $macBytes[5] = $randomBytes[1]

        # Additional mixing: XOR with third random byte for extra uniqueness
        for ($i = 0; $i -lt 6; $i++) {
            $macBytes[$i] = $macBytes[$i] -bxor $randomBytes[2]
        }

        # Ensure first byte's second nibble is even (locally administered address)
        # Format: x2, x6, xA, or xE (where x is any hex digit)
        $macBytes[0] = $macBytes[0] -band 0xFE -bor 0x02

        # Format as MAC address string
        $macAddress = ($macBytes | ForEach-Object { $_.ToString("X2") }) -join ":"

        # Cleanup
        if ($rng) { $rng.Dispose() }

        return $macAddress
    }
    catch {
        # Fallback to simpler method if generation fails
        $random = New-Object System.Random
        $macBytes = @()
        for ($i = 0; $i -lt 6; $i++) {
            $macBytes += $random.Next(0, 256)
        }
        # Ensure first byte's second nibble is even (locally administered address)
        $macBytes[0] = $macBytes[0] -band 0xFE -bor 0x02
        $macAddress = ($macBytes | ForEach-Object { $_.ToString("X2") }) -join ":"
        return $macAddress
    }
}

# Connect to control cabinet via SSH and modify MAC address
function Update-ControlCabinetMAC {
    param(
        [string]$ControlIP,
        [string]$Username = "root",
        [string]$Password = "root"
    )
    try {
        Write-Host "正在连接到控制柜 ($ControlIP)..." -ForegroundColor Yellow
        Fix-WindowSize

        # Check if SSH is available
        $sshAvailable = Get-Command ssh -ErrorAction SilentlyContinue
        if (-not $sshAvailable) {
            return $false, "未找到SSH客户端，请安装OpenSSH客户端。"
        }

        # 跳过网络连接测试，直接尝试SSH连接（让用户输入密码）
        # 通过SSH连接结果来判断网络是否连通

        # Create bash commands to modify /etc/network/interfaces directly via SSH
        Write-Host "正在更新控制柜上的MAC地址..." -ForegroundColor Yellow

        # Generate random MAC address (all 6 bytes)
        $randomMAC = Get-RandomMAC
        Write-Host "计算出的MAC地址: $randomMAC" -ForegroundColor Cyan
        Fix-WindowSize

        # Build bash commands using a script file to avoid quote escaping issues
        # First backup interfaces file, then replace the entire MAC address with random MAC
        # Remove # if present, replace entire MAC address (all 6 bytes)
        # Use script file to handle complex awk command
        $scriptContent = @"
#!/bin/bash

# Check if interfaces file exists
if [ ! -f /etc/network/interfaces ]; then
    echo "FILE_NOT_FOUND"
    exit 1
fi

BACKUP_FILE="/etc/network/interfaces.backup.`$(date +%Y%m%d_%H%M%S)"
cp /etc/network/interfaces "`$BACKUP_FILE" 2>/dev/null

if grep -q "hwaddress ether" /etc/network/interfaces; then
    # Remove any characters before hwaddress ether and update MAC address
    sed -i "s/.*hwaddress ether [0-9A-Fa-f]\{2\}:[0-9A-Fa-f]\{2\}:[0-9A-Fa-f]\{2\}:[0-9A-Fa-f]\{2\}:[0-9A-Fa-f]\{2\}:[0-9A-Fa-f]\{2\}/hwaddress ether RANDOM_MAC/g" /etc/network/interfaces
    # Also handle commented lines
    sed -i "s/.*#.*hwaddress ether [0-9A-Fa-f]\{2\}:[0-9A-Fa-f]\{2\}:[0-9A-Fa-f]\{2\}:[0-9A-Fa-f]\{2\}:[0-9A-Fa-f]\{2\}:[0-9A-Fa-f]\{2\}/hwaddress ether RANDOM_MAC/g" /etc/network/interfaces
    hwaddressLine=`$(grep "hwaddress ether" /etc/network/interfaces | head -1 | sed 's/^[[:space:]]*//')
    echo "UPDATED"
    echo "$hwaddressLine"
else
    awk "BEGIN{found=0} /address[[:space:]]/ && found==0 {print \$0; print \"hwaddress ether RANDOM_MAC\"; found=1; next} {print}" /etc/network/interfaces > /tmp/interfaces_new 2>&1
    if [ -f /tmp/interfaces_new ]; then
        if grep -q "hwaddress ether" /tmp/interfaces_new; then
            mv /tmp/interfaces_new /etc/network/interfaces
            if grep -q "hwaddress ether" /etc/network/interfaces; then
                hwaddressLine=`$(grep "hwaddress ether" /etc/network/interfaces | head -1 | sed 's/^[[:space:]]*//')
                echo "ADDED"
                echo "$hwaddressLine"
            else
                echo "ERROR: hwaddress ether line was not added to final file"
                exit 1
            fi
        else
            cp /etc/network/interfaces.backup.* /etc/network/interfaces 2>/dev/null || cp "$BACKUP_FILE" /etc/network/interfaces
            sed -i '/address[[:space:]]/a\hwaddress ether RANDOM_MAC' /etc/network/interfaces
            if grep -q "hwaddress ether" /etc/network/interfaces; then
                hwaddressLine=`$(grep "hwaddress ether" /etc/network/interfaces | head -1 | sed 's/^[[:space:]]*//')
                echo "ADDED"
                echo "$hwaddressLine"
            else
                echo "ERROR: hwaddress ether line was not added by awk or sed"
                exit 1
            fi
        fi
    else
        echo "ERROR: Failed to create new interfaces file"
        exit 1
    fi
fi

# 无论更新还是添加，都从保存后的interfaces文件中读取hwaddress ether行（确保获取最新内容）
if [ -f /etc/network/interfaces ]; then
    finalHwaddressLine=`$(grep "hwaddress ether" /etc/network/interfaces | head -1 | sed 's/^[[:space:]]*//')
    if [ -n "$finalHwaddressLine" ]; then
        echo "FINAL_HWADDRESS_LINE"
        echo "$finalHwaddressLine"
    fi
fi
"@

        # Replace MAC placeholder with actual random MAC address
        $scriptContent = $scriptContent -replace 'RANDOM_MAC', $randomMAC

        # Encode script to base64 to pass via SSH
        $scriptBytes = [System.Text.Encoding]::UTF8.GetBytes($scriptContent)
        $scriptBase64 = [Convert]::ToBase64String($scriptBytes)

        # Create command to decode and execute script
        $bashCommand = 'echo "' + $scriptBase64 + '" | base64 -d | bash'

        # Use SSH with manual password input
        Fix-WindowSize
        Write-Host "正在通过SSH连接..." -ForegroundColor Yellow
        Fix-WindowSize
        Write-Host "正在控制柜上执行命令..." -ForegroundColor Yellow
        Fix-WindowSize
        Write-Host ""
        Fix-WindowSize
        Write-Host "密码提示：root" -ForegroundColor Yellow
        Write-Host ""
        Fix-WindowSize

        try {
            # 密码重试循环
            $maxRetries = 5
            $retryCount = 0
            $passwordCorrect = $false
            $result = $null
            $exitCode = 1

            while (-not $passwordCorrect -and $retryCount -lt $maxRetries) {
                if ($retryCount -gt 0) {
                    Fix-WindowSize
                    Write-Host ""
                    Write-Host "密码错误，请重新输入" -ForegroundColor Red
                    Write-Host ""
                    Fix-WindowSize
                }
                else {
                    Write-Host "正在链接，请输入密码：" -ForegroundColor Yellow
                    Write-Host ""
                }

                # Run SSH directly - user will enter password when prompted
                # bashCommand already contains base64 encoded script, just execute it
                $result = ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=NUL -o LogLevel=ERROR "$Username@$ControlIP" $bashCommand 2>&1
                $exitCode = $LASTEXITCODE

                # Display result (filter out SSH warning messages and backup errors, but keep hwaddress ether lines)
                if ($result) {
                    $filteredResult = $result | Where-Object {
                        $_ -notmatch "Warning: Permanently added" -and
                        $_ -notmatch "cannot stat" -and
                        $_ -notmatch "No such file or directory" -and
                        $_ -notmatch "^cp:"
                    }
                    if ($filteredResult) {
                        Write-Host $filteredResult
                    }
                }

                # Check if password input was correct
                # 首先检查是否有明确的密码错误信息
                $resultString = if ($result -is [array]) { $result -join "`n" } else { if ($result) { $result.ToString() } else { "" } }

                # 调试：保存原始结果字符串（用于调试提取问题）
                $global:debugResultString = $resultString

                Write-Host ""

                # 检查是否有明确的密码认证失败信息
                $isPasswordError = $false
                $isConnectionError = $false
                if ($resultString -match "Permission denied|Authentication failed|Permission denied \(publickey|password.*incorrect|Access denied") {
                    $isPasswordError = $true
                }
                # 检查是否是连接失败（不是密码错误）
                if ($resultString -match "Connection.*refused|Connection.*timed out|Connection.*closed|No route to host|Network is unreachable|Connection.*reset|Could not resolve hostname|ssh:.*Connection refused|ssh:.*Connection timed out") {
                    $isConnectionError = $true
                }
                # 如果exitCode不为0且没有结果，也可能是连接失败
                if ($exitCode -ne 0 -and -not $resultString -and -not $isPasswordError) {
                    $isConnectionError = $true
                }

                # 如果exitCode为0，说明密码正确（即使命令执行可能有问题）
                if ($exitCode -eq 0) {
                    Fix-WindowSize
                    Write-Host "密码输入: " -NoNewline -ForegroundColor Yellow
                    Write-Host "正确" -ForegroundColor Green
                    Write-Host "SSH连接成功，命令已执行" -ForegroundColor Green
                    $passwordCorrect = $true
                }
                # 如果有明确的密码错误信息，说明密码错误
                elseif ($isPasswordError) {
                    Fix-WindowSize
                    Write-Host "密码输入: " -NoNewline -ForegroundColor Yellow
                    Write-Host "错误" -ForegroundColor Red
                    $retryCount++

                    if ($retryCount -ge $maxRetries) {
                        Write-Host "已达到最大重试次数，请检查网络连接和SSH服务" -ForegroundColor Red
                        return $false, "SSH密码验证失败，已达到最大重试次数。"
                    }
                }
                # 如果没有明确的密码错误，但exitCode不为0，可能是命令执行问题，但密码可能是正确的
                # 检查结果中是否有我们期望的输出（如ADDED、UPDATED、FILE_NOT_FOUND等）
                elseif ($resultString -match "ADDED|UPDATED|FILE_NOT_FOUND|hwaddress ether") {
                    # 有我们期望的输出，说明密码正确，只是命令执行可能有问题
                    Fix-WindowSize
                    Write-Host "密码输入: " -NoNewline -ForegroundColor Yellow
                    Write-Host "正确" -ForegroundColor Green
                    Write-Host "SSH连接成功，命令已执行" -ForegroundColor Green
                    $passwordCorrect = $true
                }
                # 如果是连接失败（不是密码错误），显示错误信息并终止
                elseif ($isConnectionError) {
                    Fix-WindowSize
                    Write-Host "控制柜链接不上" -ForegroundColor Red
                    Write-Host "请检查:" -ForegroundColor Red
                    Write-Host "  1. 控制柜已开机" -ForegroundColor Red
                    Write-Host "  2. 网线已连接" -ForegroundColor Red
                    Write-Host "  3. IP地址正确: $ControlIP" -ForegroundColor Red
                    Write-Host "  4. 本地IP在同一子网" -ForegroundColor Red
                    Write-Host ""
                    Fix-WindowSize
                    return $false, "控制柜链接不上，请检查网络连接。"
                }
                else {
                    # 其他情况，可能是网络问题或其他错误，但密码可能是正确的
                    # 为了安全，我们假设密码错误，让用户重试
                    Fix-WindowSize
                    Write-Host "密码输入: " -NoNewline -ForegroundColor Yellow
                    Write-Host "错误或连接失败" -ForegroundColor Red
                    $retryCount++

                    if ($retryCount -ge $maxRetries) {
                        Write-Host "已达到最大重试次数，请检查网络连接和SSH服务" -ForegroundColor Red
                        return $false, "SSH连接失败，已达到最大重试次数。"
                    }
                }
            }
        }
        catch {
            Fix-WindowSize
            Write-Host "控制柜链接不上" -ForegroundColor Red
            Write-Host "请检查:" -ForegroundColor Red
            Write-Host "  1. 控制柜已开机" -ForegroundColor Red
            Write-Host "  2. 网线已连接" -ForegroundColor Red
            Write-Host "  3. IP地址正确: $ControlIP" -ForegroundColor Red
            Write-Host "  4. 本地IP在同一子网" -ForegroundColor Red
            Write-Host ""
            Fix-WindowSize
            return $false, "控制柜链接不上，请检查网络连接。"
        }

        # Check result and extract the hwaddress ether line
        if ($result -is [array]) {
            $resultString = $result -join "`n"
        }
        else {
            if ($result) {
                $resultString = $result.ToString()
            }
            else {
                $resultString = ""
            }
        }

        # Parse the result - check for status first
        $status = ""
        $hwaddressLine = ""

        # Split result into lines and check each line
        # 不要过滤空行，因为FINAL_HWADDRESS_LINE后面可能有空行，但我们需要保留所有行以正确提取
        $lines = $resultString -split "`n"
        $lineIndex = 0

        foreach ($line in $lines) {
            $trimmedLine = $line.Trim()
            # 跳过空行（但保留索引以便正确获取下一行）
            if ([string]::IsNullOrWhiteSpace($trimmedLine)) {
                $lineIndex++
                continue
            }
            # Check for status indicators (exact match)
            if ($trimmedLine -eq "UPDATED") {
                $status = "UPDATED"
                # Check the next line for hwaddress ether
                if ($lineIndex + 1 -lt $lines.Count) {
                    $nextLine = $lines[$lineIndex + 1].Trim()
                    if ($nextLine -match "hwaddress ether" -and $nextLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                        $hwaddressLine = $nextLine
                    }
                }
            }
            elseif ($trimmedLine -eq "ADDED") {
                $status = "ADDED"
                # Check the next line for hwaddress ether
                if ($lineIndex + 1 -lt $lines.Count) {
                    $nextLine = $lines[$lineIndex + 1].Trim()
                    if ($nextLine -match "hwaddress ether" -and $nextLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                        $hwaddressLine = $nextLine
                    }
                }
            }
            elseif ($trimmedLine -eq "FILE_NOT_FOUND") {
                # 未找到interfaces文件
                $errorMsg = "未找到interfaces文件"
                return $false, $errorMsg
            }
            elseif ($trimmedLine -eq "FINAL_HWADDRESS_LINE") {
                # 从保存后的interfaces文件中读取的hwaddress ether行（在bash脚本的最后执行，确保获取最新内容）
                # 查找下一行（跳过空行）
                $nextIndex = $lineIndex + 1
                while ($nextIndex -lt $lines.Count) {
                    $nextLine = $lines[$nextIndex].Trim()
                    if (-not [string]::IsNullOrWhiteSpace($nextLine)) {
                        # 更宽松的匹配：只要包含hwaddress ether和MAC地址模式即可
                        if ($nextLine -match "hwaddress ether") {
                            # 检查是否包含MAC地址模式（6组十六进制数字，用冒号分隔）
                            if ($nextLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                                # 优先使用从保存后的文件中读取的行（确保是最新的）
                                $hwaddressLine = $nextLine
                                break
                            }
                        }
                    }
                    $nextIndex++
                }
            }
            # Extract hwaddress ether line (must contain MAC address pattern)
            # Use the complete line as-is from bash output
            elseif ($trimmedLine -match "hwaddress ether" -and $trimmedLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                # Use the complete trimmed line (fallback if not found after status or FINAL_HWADDRESS_LINE)
                if (-not $hwaddressLine) {
                    $hwaddressLine = $trimmedLine
                }
            }
            $lineIndex++
        }

        # Return appropriate result based on status
        # 优先使用从FINAL_HWADDRESS_LINE中提取的行（确保是从保存后的文件中读取的）
        if ($status -eq "UPDATED") {
            # 有hwaddress ether，更新成功
            $msgUpdated = "hwaddress ether更新成功"
            if ($hwaddressLine) {
                # 确保hwaddressLine包含完整的MAC地址
                if ($hwaddressLine -match "hwaddress ether" -and $hwaddressLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                    return $true, "${msgUpdated}: $hwaddressLine"
                }
                else {
                    # 如果hwaddressLine不完整，仍然返回，让显示逻辑处理
                    return $true, "${msgUpdated}: $hwaddressLine"
                }
            }
            else {
                return $true, $msgUpdated
            }
        }
        elseif ($status -eq "ADDED") {
            # 没有找到hwaddress ether，添加成功
            $msgAdded = "hwaddress ether添加成功"
            if ($hwaddressLine) {
                # 确保hwaddressLine包含完整的MAC地址
                if ($hwaddressLine -match "hwaddress ether" -and $hwaddressLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                    return $true, "${msgAdded}: $hwaddressLine"
                }
                else {
                    # 如果hwaddressLine不完整，仍然返回，让显示逻辑处理
                    return $true, "${msgAdded}: $hwaddressLine"
                }
            }
            else {
                return $true, $msgAdded
            }
        }
        elseif ($resultString -match "ERROR") {
            return $false, "Failed to update MAC address. Error: $resultString"
        }
        else {
            # Check if interfaces file does not exist (only if no status was found)
            if ($resultString -match "FILE_NOT_FOUND") {
                # 未找到interfaces文件
                $errorMsg = "未找到interfaces文件"
                return $false, $errorMsg
            }
            return $false, "Unknown error occurred"
        }
    }
    catch {
        return $false, "Error occurred: $_"
    }
}

# Get network adapters list with details
function Get-NetworkAdapters {
    try {
        $allAdapters = Get-NetAdapter | Select-Object Name, Status, InterfaceDescription
        $adapterList = @()
        foreach ($adapter in $allAdapters) {
            $adapterList += @{
                Name        = $adapter.Name
                Status      = $adapter.Status
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
            $skipHeader = $true
            foreach ($line in $lines) {
                if ($skipHeader) {
                    if ($line -match "State") {
                        $skipHeader = $false
                    }
                    continue
                }
                if ($line.Trim()) {
                    $parts = $line -split "\s+", 4
                    if ($parts.Length -ge 4) {
                        $status = $parts[0]
                        $name = $parts[3]
                        $adapters += @{
                            Name        = $name
                            Status      = $status
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

# Set static IP address
function Set-StaticIP {
    param(
        [string]$AdapterName,
        [string]$IPAddress,
        [string]$SubnetMask,
        [string]$Gateway = $null
    )
    try {
        # First, remove any existing static IP configuration
        Fix-WindowSize
        Write-Host "正在移除现有IP配置..." -ForegroundColor Yellow
        Fix-WindowSize
        netsh interface ipv4 delete address name="$AdapterName" address=$IPAddress 2>&1 | Out-Null

        # Also try to remove gateway if exists
        if ($Gateway) {
            netsh interface ipv4 delete route 0.0.0.0/0 "$AdapterName" $Gateway 2>&1 | Out-Null
        }

        # Wait a moment for the deletion to complete
        Start-Sleep -Milliseconds 500

        # Now set the new IP configuration
        Write-Host "正在设置新IP配置..." -ForegroundColor Yellow
        if ($Gateway) {
            # Set IP, mask, and gateway in one command
            $result = netsh interface ipv4 set address name="$AdapterName" source=static address=$IPAddress mask=$SubnetMask gateway=$Gateway 2>&1
            $exitCode = $LASTEXITCODE
        }
        else {
            # Set only IP and mask
            $result = netsh interface ipv4 set address name="$AdapterName" source=static address=$IPAddress mask=$SubnetMask 2>&1
            $exitCode = $LASTEXITCODE
        }

        if ($exitCode -eq 0) {
            if ($Gateway) {
                return $true, "IP configuration successful! (IP: $IPAddress, Mask: $SubnetMask, Gateway: $Gateway)"
            }
            else {
                return $true, "IP configuration successful! (IP: $IPAddress, Mask: $SubnetMask)"
            }
        }
        else {
            $errorMsg = if ($result) { $result -join "`n" } else { "Unknown error" }
            # If error is "object already exists", try alternative method
            if ($errorMsg -like "*already exists*" -or $errorMsg -like "*已存在*") {
                Write-Host "正在尝试备用方法..." -ForegroundColor Yellow
                # Try using New-NetIPAddress (PowerShell cmdlet) instead
                try {
                    Remove-NetIPAddress -InterfaceAlias "$AdapterName" -Confirm:$false -ErrorAction SilentlyContinue
                    if ($Gateway) {
                        New-NetIPAddress -InterfaceAlias "$AdapterName" -IPAddress $IPAddress -PrefixLength (Get-PrefixLength -SubnetMask $SubnetMask) -DefaultGateway $Gateway -ErrorAction Stop
                    }
                    else {
                        New-NetIPAddress -InterfaceAlias "$AdapterName" -IPAddress $IPAddress -PrefixLength (Get-PrefixLength -SubnetMask $SubnetMask) -ErrorAction Stop
                    }
                    return $true, "IP configuration successful using alternative method!"
                }
                catch {
                    return $false, "Configuration failed. Error: $_"
                }
            }
            return $false, "Configuration failed. Error code: $exitCode. Details: $errorMsg"
        }
    }
    catch {
        return $false, "Error occurred: $_"
    }
}

# Helper function to convert subnet mask to prefix length
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
        # Default to /24 if calculation fails
        return 24
    }
}

# Main program
try {
    Write-Host "正在获取网络适配器..." -ForegroundColor Yellow
    $adapters = Get-NetworkAdapters

    if ($adapters.Count -eq 0) {
        Write-Host "错误：未找到网络适配器！" -ForegroundColor Red
        Write-Host ""
        $null = Read-Host "按Enter键退出"
        exit 1
    }
}
catch {
    Write-Host "获取适配器时发生错误: $_" -ForegroundColor Red
    Write-Host ""
    $null = Read-Host "按Enter键退出"
    exit 1
}

Write-Host "找到网络适配器:" -ForegroundColor Green
Write-Host ""
for ($i = 0; $i -lt $adapters.Count; $i++) {
    $adapter = $adapters[$i]
    # Check status (handle both English and Chinese status values)
    $statusStr = $adapter.Status.ToString()
    $isConnected = ($adapter.Status -eq "Up") -or
    ($adapter.Status -eq "Connected") -or
    ($statusStr -like "*Connected*") -or
    ($statusStr -like "*Up*")

    $statusColor = if ($isConnected) { "Green" } else { "Yellow" }
    $statusText = if ($isConnected) { "Connected" } else { $adapter.Status }

    Write-Host "  [$($i + 1)] $($adapter.Name)" -ForegroundColor Cyan -NoNewline
    Write-Host " - Status: " -NoNewline
    Write-Host $statusText -ForegroundColor $statusColor -NoNewline
    if ($adapter.Description) {
        Write-Host " ($($adapter.Description))" -ForegroundColor Gray
    }
    else {
        Write-Host ""
    }
}
Write-Host ""

# Select adapter
$adapterIndex = -1
while ($adapterIndex -lt 1 -or $adapterIndex -gt $adapters.Count) {
    Fix-WindowSize
    Start-Sleep -Milliseconds 50
    Fix-WindowSize
    Write-Host "请选择网络适配器 (1-$($adapters.Count)): " -ForegroundColor Yellow -NoNewline
    Fix-WindowSize
    $input = Read-Host
    Fix-WindowSize
    Start-Sleep -Milliseconds 50
    Fix-WindowSize
    if ([int]::TryParse($input, [ref]$adapterIndex)) {
        if ($adapterIndex -lt 1 -or $adapterIndex -gt $adapters.Count) {
            Fix-WindowSize
            Write-Host "无效选择，请重试！" -ForegroundColor Red
            $adapterIndex = -1
        }
    }
    else {
        Fix-WindowSize
        Write-Host "无效输入，请输入数字！" -ForegroundColor Red
    }
}

$selectedAdapter = $adapters[$adapterIndex - 1].Name
Fix-WindowSize
Start-Sleep -Milliseconds 50
Fix-WindowSize
Write-Host "已选择适配器: $selectedAdapter" -ForegroundColor Green
Fix-WindowSize
Write-Host ""
Fix-WindowSize

# Input control cabinet IP address
Fix-WindowSize
Start-Sleep -Milliseconds 50
Fix-WindowSize
Write-Host "请输入控制柜IP地址: " -ForegroundColor Yellow -NoNewline
Fix-WindowSize
$controlIP = Read-Host

if (-not $controlIP -or -not (Test-IPAddress $controlIP)) {
    Write-Host "错误：IP地址格式无效！" -ForegroundColor Red
    Write-Host ""
    $null = Read-Host "按Enter键退出"
    exit 1
}

# Step 1: Configure local network first
Fix-WindowSize
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   步骤 1: 配置本地网络" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Auto calculate subnet mask
$subnetMask = Get-SubnetMask -IpAddress $controlIP

# Auto calculate local IP (same subnet, keep first 3 bytes, random last byte 2-255)
$controlIPObj = [System.Net.IPAddress]::Parse($controlIP)
$controlBytes = $controlIPObj.GetAddressBytes()
$localBytes = $controlBytes.Clone()
# Generate random number between 2 and 255 for last byte
$random = Get-Random -Minimum 2 -Maximum 256
$localBytes[3] = $random
$localIP = ([System.Net.IPAddress]::new($localBytes)).ToString()

Write-Host "控制柜IP: $controlIP" -ForegroundColor Cyan
Fix-WindowSize
Write-Host "计算出的本地IP: $localIP" -ForegroundColor Green
Fix-WindowSize
Write-Host "子网掩码: $subnetMask" -ForegroundColor Cyan
Write-Host ""
Write-Host "正在应用配置..." -ForegroundColor Yellow

# Apply configuration
$success, $message = Set-StaticIP -AdapterName $selectedAdapter -IPAddress $localIP -SubnetMask $subnetMask -Gateway $null

Write-Host ""
if ($success) {
    Fix-WindowSize
    Write-Host "本地网络配置: " -NoNewline
    Write-Host "成功" -ForegroundColor Green
    Fix-WindowSize
    Write-Host "网络适配器: $selectedAdapter" -ForegroundColor White
    Fix-WindowSize
    Write-Host "本地IP地址: $localIP" -ForegroundColor White
    Fix-WindowSize
    Write-Host "子网掩码: $subnetMask" -ForegroundColor White
    Write-Host ""
    Write-Host "等待网络配置稳定..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}
else {
    Write-Host "本地网络配置: " -NoNewline
    Write-Host "失败" -ForegroundColor Red
    Write-Host $message -ForegroundColor Red
    Write-Host ""
    Write-Host "请检查上面的错误信息并重试。" -ForegroundColor Yellow
    Write-Host ""
    $null = Read-Host "按Enter键退出"
    exit 1
}

# Step 2: Update control cabinet MAC address via SSH
Fix-WindowSize
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   步骤 2: 更新控制柜MAC地址" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$macSuccess, $macMessage = Update-ControlCabinetMAC -ControlIP $controlIP -Username "root" -Password "root"

# 保存原始返回消息，用于后续提取hwaddress ether行
$originalMacMessage = $macMessage

Fix-WindowSize

Fix-WindowSize

if ($macSuccess) {
    # 没有找到hwaddress ether，添加成功
    $msgAdded = "hwaddress ether添加成功"
    # 有hwaddress ether，更新成功
    $msgUpdated = "hwaddress ether更新成功"

    if ($macMessage -match $msgAdded) {
        # 从消息中提取hwaddress ether行（必须包含完整的MAC地址）
        $hwaddressLine = $null

        # 方法1: 使用正则提取 "hwaddress ether添加成功: hwaddress ether 00:01:02:04:A8:17"
        if ($macMessage -match "${msgAdded}:\s*(.+)") {
            $hwaddressLine = $matches[1].Trim()
        }

        # 方法2: 如果方法1提取的内容不包含完整的MAC地址，尝试从整个消息中查找
        if (-not $hwaddressLine -or -not ($hwaddressLine -match "hwaddress ether.*[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            # 从消息中查找完整的hwaddress ether行（包含MAC地址）
            if ($macMessage -match "(hwaddress ether\s+[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                $hwaddressLine = $matches[1]
            }
        }

        # 方法3: 如果还是没找到，尝试从所有行中查找（逐行检查）
        if (-not $hwaddressLine -or -not ($hwaddressLine -match "hwaddress ether.*[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            $allLines = $macMessage -split "`n" | ForEach-Object { $_.Trim() }
            foreach ($line in $allLines) {
                if ($line -match "hwaddress ether" -and $line -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                    $hwaddressLine = $line
                    break
                }
            }
        }

        # 方法4: 如果还是没找到，从原始消息中查找（可能包含在返回的result中）
        if (-not $hwaddressLine -or -not ($hwaddressLine -match "hwaddress ether.*[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            if ($originalMacMessage -match "(hwaddress ether\s+[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                $hwaddressLine = $matches[1]
            }
        }

        # 必须显示完整的hwaddress ether行（包含MAC地址）
        if ($hwaddressLine -and ($hwaddressLine -match "hwaddress ether") -and ($hwaddressLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            # 从hwaddressLine中提取MAC地址
            if ($hwaddressLine -match "hwaddress ether\s+([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                $extractedMAC = $matches[1]
                Write-Host "计算出的MAC地址: $extractedMAC" -ForegroundColor Cyan
            }
            Write-Host $hwaddressLine -ForegroundColor Green
        }
        else {
            # 如果找不到完整的行，尝试最后一次从原始消息中提取（可能FINAL_HWADDRESS_LINE没有被正确解析）
            $lastTryLine = $null
            # 尝试从原始消息的所有行中查找
            $allOriginalLines = $originalMacMessage -split "`n" | ForEach-Object { $_.Trim() }
            foreach ($origLine in $allOriginalLines) {
                if ($origLine -match "hwaddress ether" -and $origLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                    $lastTryLine = $origLine
                    break
                }
            }
            if ($lastTryLine) {
                # 从lastTryLine中提取MAC地址
                if ($lastTryLine -match "hwaddress ether\s+([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                    $extractedMAC = $matches[1]
                    Write-Host "计算出的MAC地址: $extractedMAC" -ForegroundColor Cyan
                }
                Write-Host $lastTryLine -ForegroundColor Green
            }
            else {
                # 如果还是找不到，显示默认消息
                Write-Host $msgAdded -ForegroundColor Green
            }
        }
        Write-Host "更新成功" -ForegroundColor Green
    }
    elseif ($macMessage -match $msgUpdated) {
        # 从消息中提取hwaddress ether行（必须包含完整的MAC地址）
        $hwaddressLine = $null

        # 方法1: 使用正则提取 "hwaddress ether更新成功: hwaddress ether 00:01:02:04:A8:17"
        if ($macMessage -match "${msgUpdated}:\s*(.+)") {
            $hwaddressLine = $matches[1].Trim()
        }

        # 方法2: 如果方法1提取的内容不包含完整的MAC地址，尝试从整个消息中查找
        if (-not $hwaddressLine -or -not ($hwaddressLine -match "hwaddress ether.*[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            # 从消息中查找完整的hwaddress ether行（包含MAC地址）
            if ($macMessage -match "(hwaddress ether\s+[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                $hwaddressLine = $matches[1]
            }
        }

        # 方法3: 如果还是没找到，尝试从所有行中查找（逐行检查）
        if (-not $hwaddressLine -or -not ($hwaddressLine -match "hwaddress ether.*[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            $allLines = $macMessage -split "`n" | ForEach-Object { $_.Trim() }
            foreach ($line in $allLines) {
                if ($line -match "hwaddress ether" -and $line -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                    $hwaddressLine = $line
                    break
                }
            }
        }

        # 方法4: 如果还是没找到，从原始消息中查找（可能包含在返回的result中）
        if (-not $hwaddressLine -or -not ($hwaddressLine -match "hwaddress ether.*[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            if ($originalMacMessage -match "(hwaddress ether\s+[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                $hwaddressLine = $matches[1]
            }
        }

        # 必须显示完整的hwaddress ether行（包含MAC地址）
        if ($hwaddressLine -and ($hwaddressLine -match "hwaddress ether") -and ($hwaddressLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            # 从hwaddressLine中提取MAC地址
            if ($hwaddressLine -match "hwaddress ether\s+([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                $extractedMAC = $matches[1]
                Write-Host "计算出的MAC地址: $extractedMAC" -ForegroundColor Cyan
            }
            Write-Host $hwaddressLine -ForegroundColor Green
        }
        else {
            # 如果找不到完整的行，尝试最后一次从原始消息中提取（可能FINAL_HWADDRESS_LINE没有被正确解析）
            $lastTryLine = $null
            # 尝试从原始消息的所有行中查找
            $allOriginalLines = $originalMacMessage -split "`n" | ForEach-Object { $_.Trim() }
            foreach ($origLine in $allOriginalLines) {
                if ($origLine -match "hwaddress ether" -and $origLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                    $lastTryLine = $origLine
                    break
                }
            }
            if ($lastTryLine) {
                # 从lastTryLine中提取MAC地址
                if ($lastTryLine -match "hwaddress ether\s+([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                    $extractedMAC = $matches[1]
                    Write-Host "计算出的MAC地址: $extractedMAC" -ForegroundColor Cyan
                }
                Write-Host $lastTryLine -ForegroundColor Green
            }
            else {
                # 如果还是找不到，显示默认消息
                Write-Host $msgUpdated -ForegroundColor Green
            }
        }
        Write-Host "更新成功" -ForegroundColor Green
    }
    else {
        Write-Host $macMessage -ForegroundColor Green
    }
}
else {
    # 未找到interfaces文件
    $msgNotFound = "未找到interfaces文件"
    if ($macMessage -match $msgNotFound) {
        Write-Host $msgNotFound -ForegroundColor Red
    }
    else {
        Write-Host "MAC地址更新: " -NoNewline
        Write-Host "失败" -ForegroundColor Red
        Write-Host $macMessage -ForegroundColor Red
    }
}

# Final summary
Fix-WindowSize

Write-Host ""
Write-Host "控制柜IP: $controlIP" -ForegroundColor White
Write-Host ""

if ($macSuccess) {
    # 没有找到hwaddress ether，添加成功
    $msgAdded = "hwaddress ether添加成功"
    # 有hwaddress ether，更新成功
    $msgUpdated = "hwaddress ether更新成功"

    if ($macMessage -match $msgAdded) {
        Write-Host "MAC地址更新: " -NoNewline
        Write-Host "成功" -ForegroundColor Green
        # 从消息中提取hwaddress ether行（必须包含完整的MAC地址）
        $hwaddressLine = $null

        # 方法1: 使用正则提取 "hwaddress ether添加成功: hwaddress ether 00:01:02:04:A8:17"
        if ($macMessage -match "${msgAdded}:\s*(.+)") {
            $hwaddressLine = $matches[1].Trim()
        }

        # 方法2: 如果方法1提取的内容不包含完整的MAC地址，尝试从整个消息中查找
        if (-not $hwaddressLine -or -not ($hwaddressLine -match "hwaddress ether.*[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            # 从消息中查找完整的hwaddress ether行（包含MAC地址）
            if ($macMessage -match "(hwaddress ether\s+[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                $hwaddressLine = $matches[1]
            }
        }

        # 方法3: 如果还是没找到，尝试从所有行中查找（逐行检查）
        if (-not $hwaddressLine -or -not ($hwaddressLine -match "hwaddress ether.*[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            $allLines = $macMessage -split "`n" | ForEach-Object { $_.Trim() }
            foreach ($line in $allLines) {
                if ($line -match "hwaddress ether" -and $line -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                    $hwaddressLine = $line
                    break
                }
            }
        }

        # 方法4: 如果还是没找到，从原始消息中查找（可能包含在返回的result中）
        if (-not $hwaddressLine -or -not ($hwaddressLine -match "hwaddress ether.*[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            if ($originalMacMessage -match "(hwaddress ether\s+[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                $hwaddressLine = $matches[1]
            }
        }

        # 必须显示完整的hwaddress ether行（包含MAC地址）
        if ($hwaddressLine -and ($hwaddressLine -match "hwaddress ether") -and ($hwaddressLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            # 从hwaddressLine中提取MAC地址
            if ($hwaddressLine -match "hwaddress ether\s+([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                $extractedMAC = $matches[1]
                Write-Host "计算出的MAC地址: $extractedMAC" -ForegroundColor Cyan
            }
            Write-Host $hwaddressLine -ForegroundColor Green
        }
        else {
            # 如果找不到完整的行，尝试最后一次从原始消息中提取（可能FINAL_HWADDRESS_LINE没有被正确解析）
            $lastTryLine = $null
            # 尝试从原始消息的所有行中查找
            $allOriginalLines = $originalMacMessage -split "`n" | ForEach-Object { $_.Trim() }
            foreach ($origLine in $allOriginalLines) {
                if ($origLine -match "hwaddress ether" -and $origLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                    $lastTryLine = $origLine
                    break
                }
            }
            if ($lastTryLine) {
                # 从lastTryLine中提取MAC地址
                if ($lastTryLine -match "hwaddress ether\s+([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                    $extractedMAC = $matches[1]
                    Write-Host "计算出的MAC地址: $extractedMAC" -ForegroundColor Cyan
                }
                Write-Host $lastTryLine -ForegroundColor Green
            }
            else {
                # 如果还是找不到，显示默认消息
                Write-Host $msgAdded -ForegroundColor Green
            }
        }
    }
    elseif ($macMessage -match $msgUpdated) {
        Write-Host "MAC地址更新: " -NoNewline
        Write-Host "成功" -ForegroundColor Green
        # 从消息中提取hwaddress ether行（必须包含完整的MAC地址）
        $hwaddressLine = $null

        # 方法1: 使用正则提取 "hwaddress ether更新成功: hwaddress ether 00:01:02:04:A8:17"
        if ($macMessage -match "${msgUpdated}:\s*(.+)") {
            $hwaddressLine = $matches[1].Trim()
        }

        # 方法2: 如果方法1提取的内容不包含完整的MAC地址，尝试从整个消息中查找
        if (-not $hwaddressLine -or -not ($hwaddressLine -match "hwaddress ether.*[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            # 从消息中查找完整的hwaddress ether行（包含MAC地址）
            if ($macMessage -match "(hwaddress ether\s+[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                $hwaddressLine = $matches[1]
            }
        }

        # 方法3: 如果还是没找到，尝试从所有行中查找（逐行检查）
        if (-not $hwaddressLine -or -not ($hwaddressLine -match "hwaddress ether.*[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            $allLines = $macMessage -split "`n" | ForEach-Object { $_.Trim() }
            foreach ($line in $allLines) {
                if ($line -match "hwaddress ether" -and $line -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                    $hwaddressLine = $line
                    break
                }
            }
        }

        # 方法4: 如果还是没找到，从原始消息中查找（可能包含在返回的result中）
        if (-not $hwaddressLine -or -not ($hwaddressLine -match "hwaddress ether.*[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            if ($originalMacMessage -match "(hwaddress ether\s+[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})") {
                $hwaddressLine = $matches[1]
            }
        }

        # 必须显示完整的hwaddress ether行（包含MAC地址）
        if ($hwaddressLine -and ($hwaddressLine -match "hwaddress ether") -and ($hwaddressLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}")) {
            Write-Host $hwaddressLine -ForegroundColor Green
        }
        else {
            # 如果找不到完整的行，显示默认消息（但这种情况不应该发生）
            Write-Host $msgUpdated -ForegroundColor Green
            # 尝试最后一次从原始消息中提取（可能FINAL_HWADDRESS_LINE没有被正确解析）
            $lastTryLine = $null
            # 尝试从原始消息的所有行中查找
            $allOriginalLines = $originalMacMessage -split "`n" | ForEach-Object { $_.Trim() }
            foreach ($origLine in $allOriginalLines) {
                if ($origLine -match "hwaddress ether" -and $origLine -match "[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}") {
                    $lastTryLine = $origLine
                    break
                }
            }
            if ($lastTryLine) {
                Write-Host $lastTryLine -ForegroundColor Green
            }
            else {
                # 如果还是找不到，显示默认消息
                Write-Host $msgUpdated -ForegroundColor Green
            }
        }
    }
    else {
        Write-Host "MAC地址更新: " -NoNewline
        Write-Host "成功" -ForegroundColor Green
    }
}
else {
    # 未找到interfaces文件
    $msgNotFound = "未找到interfaces文件"
    if ($macMessage -match $msgNotFound) {
        Write-Host "MAC地址更新: " -NoNewline
        Write-Host "失败" -ForegroundColor Red
        Write-Host $msgNotFound -ForegroundColor Red
    }
    else {
        Write-Host "MAC地址更新: " -NoNewline
        Write-Host "失败" -ForegroundColor Red
        Write-Host $macMessage -ForegroundColor Red
    }
}
Write-Host ""

Write-Host ""
$null = Read-Host "按Enter键退出"
