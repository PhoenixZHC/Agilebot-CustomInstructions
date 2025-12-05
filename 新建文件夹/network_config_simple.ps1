# Network Config Tool - Simple Command Line Version

# Set encoding
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Clear-Host
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Network Configuration Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check admin rights
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Error: Administrator rights required!" -ForegroundColor Red
    Write-Host "Please right-click script and select 'Run as administrator'" -ForegroundColor Yellow
    Write-Host ""
    $null = Read-Host "Press Enter to exit"
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

# Get network adapters list with details
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
            $skipHeader = $true
            foreach ($line in $lines) {
                if ($skipHeader) {
                    if ($line -match "State") {
                        $skipHeader = $false
                    }
                    continue
                }
                if ($line.Trim()) {
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
        Write-Host "Removing existing IP configuration..." -ForegroundColor Yellow
        netsh interface ipv4 delete address name="$AdapterName" address=$IPAddress 2>&1 | Out-Null

        # Also try to remove gateway if exists
        if ($Gateway) {
            netsh interface ipv4 delete route 0.0.0.0/0 "$AdapterName" $Gateway 2>&1 | Out-Null
        }

        # Wait a moment for the deletion to complete
        Start-Sleep -Milliseconds 500

        # Now set the new IP configuration
        Write-Host "Setting new IP configuration..." -ForegroundColor Yellow
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
                Write-Host "Trying alternative method..." -ForegroundColor Yellow
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
    Write-Host "Getting network adapters..." -ForegroundColor Yellow
    $adapters = Get-NetworkAdapters

    if ($adapters.Count -eq 0) {
        Write-Host "Error: No network adapters found!" -ForegroundColor Red
        Write-Host ""
        $null = Read-Host "Press Enter to exit"
        exit 1
    }
}
catch {
    Write-Host "Error occurred while getting adapters: $_" -ForegroundColor Red
    Write-Host ""
    $null = Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Found network adapters:" -ForegroundColor Green
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
    Write-Host "Please select network adapter (1-$($adapters.Count)): " -ForegroundColor Yellow -NoNewline
    $input = Read-Host
    if ([int]::TryParse($input, [ref]$adapterIndex)) {
        if ($adapterIndex -lt 1 -or $adapterIndex -gt $adapters.Count) {
            Write-Host "Invalid selection, please try again!" -ForegroundColor Red
            $adapterIndex = -1
        }
    }
    else {
        Write-Host "Invalid input, please enter a number!" -ForegroundColor Red
    }
}

$selectedAdapter = $adapters[$adapterIndex - 1].Name
Write-Host "Selected adapter: $selectedAdapter" -ForegroundColor Green
Write-Host ""

# Input control cabinet IP address
Write-Host "Please enter control cabinet IP address: " -ForegroundColor Yellow -NoNewline
$controlIP = Read-Host

if (-not $controlIP -or -not (Test-IPAddress $controlIP)) {
    Write-Host "Error: Invalid IP address format!" -ForegroundColor Red
    Write-Host ""
    $null = Read-Host "Press Enter to exit"
    exit 1
}

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

Write-Host ""
Write-Host "Control cabinet IP: $controlIP" -ForegroundColor Cyan
Write-Host "Calculated local IP: $localIP" -ForegroundColor Green
Write-Host "Subnet mask: $subnetMask" -ForegroundColor Cyan
Write-Host ""
Write-Host "Applying configuration..." -ForegroundColor Yellow

# Apply configuration
$success, $message = Set-StaticIP -AdapterName $selectedAdapter -IPAddress $localIP -SubnetMask $subnetMask -Gateway $null

Write-Host ""
if ($success) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   Configuration Successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Network adapter: $selectedAdapter" -ForegroundColor White
    Write-Host "Local IP address: $localIP" -ForegroundColor White
    Write-Host "Subnet mask: $subnetMask" -ForegroundColor White
    Write-Host ""
    Write-Host "The network configuration has been applied successfully!" -ForegroundColor Green
}
else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "   Configuration Failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host $message -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the error message above and try again." -ForegroundColor Yellow
}

Write-Host ""
$null = Read-Host "Press Enter to exit"
