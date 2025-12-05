# 网络配置工具
# 根据输入的控制柜IP地址，自动配置本地以太网适配器的IP地址和子网掩码

# 设置编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

# 检查管理员权限
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "错误：此脚本需要管理员权限！" -ForegroundColor Red
    Write-Host "请右键点击脚本，选择'以管理员身份运行'" -ForegroundColor Yellow
    Read-Host "按Enter键退出"
    exit 1
}

# 加载Windows Forms
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

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

# 根据控制柜IP计算本地IP
function Get-LocalIP {
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

# 获取网络适配器列表
function Get-NetworkAdapters {
    try {
        $adapters = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Select-Object -ExpandProperty Name
        return $adapters
    }
    catch {
        try {
            $result = netsh interface show interface
            $adapters = @()
            $lines = $result -split "`n"
            foreach ($line in $lines) {
                if ($line -match "已连接|Connected") {
                    $parts = $line -split '\s+', 4
                    if ($parts.Length -ge 4) {
                        $adapters += $parts[3]
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

# 获取适配器当前IP配置
function Get-AdapterIPConfig {
    param([string]$AdapterName)
    try {
        $ipConfig = Get-NetIPAddress -InterfaceAlias $AdapterName -AddressFamily IPv4 -ErrorAction SilentlyContinue
        if ($ipConfig) {
            $prefix = $ipConfig.PrefixLength
            $mask = [System.Net.IPAddress]::new([System.Net.IPAddress]::HostToNetworkOrder([int](([Math]::Pow(2, 32) - 1) - ([Math]::Pow(2, 32 - $prefix) - 1))))
            return @{
                IPAddress = $ipConfig.IPAddress
                SubnetMask = $mask.ToString()
            }
        }
    }
    catch {
    }
    try {
        $result = netsh interface ipv4 show config name="$AdapterName"
        $ipAddress = $null
        $subnetMask = $null
        foreach ($line in $result) {
            if ($line -match "IP.*地址|IP.*Address") {
                if ($line -match "(\d+\.\d+\.\d+\.\d+)") {
                    $ipAddress = $matches[1]
                }
            }
            if ($line -match "子网掩码|Subnet.*Mask") {
                if ($line -match "(\d+\.\d+\.\d+\.\d+)") {
                    $subnetMask = $matches[1]
                }
            }
        }
        return @{
            IPAddress = $ipAddress
            SubnetMask = $subnetMask
        }
    }
    catch {
        return @{
            IPAddress = $null
            SubnetMask = $null
        }
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
        if ($Gateway) {
            netsh interface ipv4 set address name="$AdapterName" source=static address=$IPAddress mask=$SubnetMask gateway=$Gateway | Out-Null
        }
        else {
            netsh interface ipv4 set address name="$AdapterName" source=static address=$IPAddress mask=$SubnetMask | Out-Null
        }
        if ($LASTEXITCODE -eq 0) {
            return $true, "IP配置成功！"
        }
        else {
            return $false, "配置失败，错误代码: $LASTEXITCODE"
        }
    }
    catch {
        return $false, "发生错误: $_"
    }
}

# 重置为DHCP
function Reset-ToDHCP {
    param([string]$AdapterName)
    try {
        netsh interface ipv4 set address name="$AdapterName" source=dhcp | Out-Null
        netsh interface ipv4 set dns name="$AdapterName" source=dhcp | Out-Null
        return $true, "已重置为DHCP"
    }
    catch {
        return $false, "重置失败: $_"
    }
}

# 创建GUI窗口
$form = New-Object System.Windows.Forms.Form
$form.Text = "网络配置工具"
$form.Size = New-Object System.Drawing.Size(550, 550)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.MinimizeBox = $false

# 标题
$titleLabel = New-Object System.Windows.Forms.Label
$titleLabel.Text = "网络配置工具"
$titleLabel.Font = New-Object System.Drawing.Font("Microsoft YaHei", 14, [System.Drawing.FontStyle]::Bold)
$titleLabel.AutoSize = $true
$titleLabel.Location = New-Object System.Drawing.Point(200, 20)
$form.Controls.Add($titleLabel)

# 控制柜IP地址
$controlIPLabel = New-Object System.Windows.Forms.Label
$controlIPLabel.Text = "控制柜IP地址:"
$controlIPLabel.Location = New-Object System.Drawing.Point(30, 70)
$controlIPLabel.AutoSize = $true
$form.Controls.Add($controlIPLabel)

$controlIPTextBox = New-Object System.Windows.Forms.TextBox
$controlIPTextBox.Location = New-Object System.Drawing.Point(150, 68)
$controlIPTextBox.Size = New-Object System.Drawing.Size(200, 20)
$form.Controls.Add($controlIPTextBox)

# 本地IP地址
$localIPLabel = New-Object System.Windows.Forms.Label
$localIPLabel.Text = "本地IP地址:"
$localIPLabel.Location = New-Object System.Drawing.Point(30, 100)
$localIPLabel.AutoSize = $true
$form.Controls.Add($localIPLabel)

$localIPTextBox = New-Object System.Windows.Forms.TextBox
$localIPTextBox.Location = New-Object System.Drawing.Point(150, 98)
$localIPTextBox.Size = New-Object System.Drawing.Size(200, 20)
$form.Controls.Add($localIPTextBox)

# 子网掩码
$subnetMaskLabel = New-Object System.Windows.Forms.Label
$subnetMaskLabel.Text = "子网掩码:"
$subnetMaskLabel.Location = New-Object System.Drawing.Point(30, 130)
$subnetMaskLabel.AutoSize = $true
$form.Controls.Add($subnetMaskLabel)

$subnetMaskTextBox = New-Object System.Windows.Forms.TextBox
$subnetMaskTextBox.Location = New-Object System.Drawing.Point(150, 128)
$subnetMaskTextBox.Size = New-Object System.Drawing.Size(200, 20)
$subnetMaskTextBox.Text = "255.255.255.0"
$form.Controls.Add($subnetMaskTextBox)

# 网关
$gatewayLabel = New-Object System.Windows.Forms.Label
$gatewayLabel.Text = "网关 (可选):"
$gatewayLabel.Location = New-Object System.Drawing.Point(30, 160)
$gatewayLabel.AutoSize = $true
$form.Controls.Add($gatewayLabel)

$gatewayTextBox = New-Object System.Windows.Forms.TextBox
$gatewayTextBox.Location = New-Object System.Drawing.Point(150, 158)
$gatewayTextBox.Size = New-Object System.Drawing.Size(200, 20)
$form.Controls.Add($gatewayTextBox)

# 网络适配器
$adapterLabel = New-Object System.Windows.Forms.Label
$adapterLabel.Text = "网络适配器:"
$adapterLabel.Location = New-Object System.Drawing.Point(30, 190)
$adapterLabel.AutoSize = $true
$form.Controls.Add($adapterLabel)

$adapterComboBox = New-Object System.Windows.Forms.ComboBox
$adapterComboBox.Location = New-Object System.Drawing.Point(150, 188)
$adapterComboBox.Size = New-Object System.Drawing.Size(300, 20)
$adapterComboBox.DropDownStyle = "DropDownList"
$form.Controls.Add($adapterComboBox)

# 刷新按钮
$refreshButton = New-Object System.Windows.Forms.Button
$refreshButton.Text = "刷新"
$refreshButton.Location = New-Object System.Drawing.Point(460, 186)
$refreshButton.Size = New-Object System.Drawing.Size(60, 25)
$form.Controls.Add($refreshButton)

# 当前配置显示
$configLabel = New-Object System.Windows.Forms.Label
$configLabel.Text = "当前配置:"
$configLabel.Location = New-Object System.Drawing.Point(30, 230)
$configLabel.AutoSize = $true
$form.Controls.Add($configLabel)

$configTextBox = New-Object System.Windows.Forms.TextBox
$configTextBox.Location = New-Object System.Drawing.Point(30, 250)
$configTextBox.Size = New-Object System.Drawing.Size(480, 150)
$configTextBox.Multiline = $true
$configTextBox.ReadOnly = $true
$configTextBox.ScrollBars = "Vertical"
$form.Controls.Add($configTextBox)

# 应用配置按钮
$applyButton = New-Object System.Windows.Forms.Button
$applyButton.Text = "应用配置"
$applyButton.Location = New-Object System.Drawing.Point(100, 420)
$applyButton.Size = New-Object System.Drawing.Size(100, 30)
$form.Controls.Add($applyButton)

# 重置为DHCP按钮
$resetButton = New-Object System.Windows.Forms.Button
$resetButton.Text = "重置为DHCP"
$resetButton.Location = New-Object System.Drawing.Point(220, 420)
$resetButton.Size = New-Object System.Drawing.Size(100, 30)
$form.Controls.Add($resetButton)

# 退出按钮
$exitButton = New-Object System.Windows.Forms.Button
$exitButton.Text = "退出"
$exitButton.Location = New-Object System.Drawing.Point(340, 420)
$exitButton.Size = New-Object System.Drawing.Size(100, 30)
$form.Controls.Add($exitButton)

# 刷新适配器列表
function Refresh-Adapters {
    $adapters = Get-NetworkAdapters
    $adapterComboBox.Items.Clear()
    foreach ($adapter in $adapters) {
        $adapterComboBox.Items.Add($adapter) | Out-Null
    }
    if ($adapters.Count -gt 0) {
        $adapterComboBox.SelectedIndex = 0
        Update-CurrentConfig
    }
    else {
        $configTextBox.Text = "未找到已连接的网络适配器"
    }
}

# 更新当前配置显示
function Update-CurrentConfig {
    $adapterName = $adapterComboBox.SelectedItem
    if ($adapterName) {
        $config = Get-AdapterIPConfig -AdapterName $adapterName
        $configText = "适配器: $adapterName`r`n"
        if ($config.IPAddress) {
            $configText += "当前IP地址: $($config.IPAddress)`r`n"
        }
        else {
            $configText += "当前IP地址: 未配置或使用DHCP`r`n"
        }
        if ($config.SubnetMask) {
            $configText += "当前子网掩码: $($config.SubnetMask)`r`n"
        }
        else {
            $configText += "当前子网掩码: 未配置`r`n"
        }
        $configTextBox.Text = $configText
    }
}

# 控制柜IP地址改变事件
$controlIPTextBox.Add_TextChanged({
    $controlIP = $controlIPTextBox.Text.Trim()
    if (Test-IPAddress $controlIP) {
        $localIP = Get-LocalIP -ControlIP $controlIP
        if ($localIP) {
            $localIPTextBox.Text = $localIP
        }
        $subnetMask = Get-SubnetMask -IpAddress $controlIP
        $subnetMaskTextBox.Text = $subnetMask
    }
})

# 适配器选择改变事件
$adapterComboBox.Add_SelectedIndexChanged({
    Update-CurrentConfig
})

# 刷新按钮事件
$refreshButton.Add_Click({
    Refresh-Adapters
})

# 应用配置按钮事件
$applyButton.Add_Click({
    $controlIP = $controlIPTextBox.Text.Trim()
    $localIP = $localIPTextBox.Text.Trim()
    $subnetMask = $subnetMaskTextBox.Text.Trim()
    $gateway = $gatewayTextBox.Text.Trim()
    $adapterName = $adapterComboBox.SelectedItem

    if (-not $controlIP) {
        [System.Windows.Forms.MessageBox]::Show("请输入控制柜IP地址！", "错误", "OK", "Error")
        return
    }

    if (-not (Test-IPAddress $controlIP)) {
        [System.Windows.Forms.MessageBox]::Show("控制柜IP地址格式不正确！", "错误", "OK", "Error")
        return
    }

    if (-not $localIP) {
        [System.Windows.Forms.MessageBox]::Show("请输入本地IP地址！", "错误", "OK", "Error")
        return
    }

    if (-not (Test-IPAddress $localIP)) {
        [System.Windows.Forms.MessageBox]::Show("本地IP地址格式不正确！", "错误", "OK", "Error")
        return
    }

    if (-not $subnetMask) {
        [System.Windows.Forms.MessageBox]::Show("请输入子网掩码！", "错误", "OK", "Error")
        return
    }

    if (-not (Test-IPAddress $subnetMask)) {
        [System.Windows.Forms.MessageBox]::Show("子网掩码格式不正确！", "错误", "OK", "Error")
        return
    }

    if ($gateway -and -not (Test-IPAddress $gateway)) {
        [System.Windows.Forms.MessageBox]::Show("网关IP地址格式不正确！", "错误", "OK", "Error")
        return
    }

    if (-not $adapterName) {
        [System.Windows.Forms.MessageBox]::Show("请选择网络适配器！", "错误", "OK", "Error")
        return
    }

    $message = "确定要修改网络适配器 '$adapterName' 的配置吗？`r`n`r`n"
    $message += "本地IP地址: $localIP`r`n"
    $message += "子网掩码: $subnetMask`r`n"
    $message += "网关: $(if ($gateway) { $gateway } else { '未设置' })`r`n`r`n"
    $message += "注意：此操作可能会暂时断开网络连接！"

    $result = [System.Windows.Forms.MessageBox]::Show($message, "确认", "YesNo", "Question")
    if ($result -eq "Yes") {
        $success, $msg = Set-StaticIP -AdapterName $adapterName -IPAddress $localIP -SubnetMask $subnetMask -Gateway $(if ($gateway) { $gateway } else { $null })
        if ($success) {
            [System.Windows.Forms.MessageBox]::Show("网络配置已成功应用！`r`n`r`n$msg", "成功", "OK", "Information")
            Update-CurrentConfig
        }
        else {
            [System.Windows.Forms.MessageBox]::Show("网络配置失败！`r`n`r`n$msg`r`n`r`n请确保以管理员权限运行此程序。", "失败", "OK", "Error")
        }
    }
})

# 重置为DHCP按钮事件
$resetButton.Add_Click({
    $adapterName = $adapterComboBox.SelectedItem
    if (-not $adapterName) {
        [System.Windows.Forms.MessageBox]::Show("请选择网络适配器！", "错误", "OK", "Error")
        return
    }

    $result = [System.Windows.Forms.MessageBox]::Show("确定要将网络适配器 '$adapterName' 重置为DHCP自动获取IP吗？", "确认", "YesNo", "Question")
    if ($result -eq "Yes") {
        $success, $msg = Reset-ToDHCP -AdapterName $adapterName
        if ($success) {
            [System.Windows.Forms.MessageBox]::Show("已重置为DHCP自动获取IP！", "成功", "OK", "Information")
            Update-CurrentConfig
        }
        else {
            [System.Windows.Forms.MessageBox]::Show("重置失败！`r`n`r`n$msg`r`n`r`n请确保以管理员权限运行此程序。", "失败", "OK", "Error")
        }
    }
})

# 退出按钮事件
$exitButton.Add_Click({
    $form.Close()
})

# 初始化
Refresh-Adapters

# 显示窗口
[System.Windows.Forms.Application]::EnableVisualStyles()
$form.ShowDialog() | Out-Null
