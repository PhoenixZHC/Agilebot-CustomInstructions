# Simple Network Config Test Script

# Set encoding
chcp 65001 | Out-Null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Network Config Tool - Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check admin rights
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Error: Administrator rights required!" -ForegroundColor Red
    Write-Host "Please right-click script and select 'Run as administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Admin check passed" -ForegroundColor Green
Write-Host ""

# Get network adapters
Write-Host "Getting network adapters..." -ForegroundColor Yellow
try {
    $adapters = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Select-Object -ExpandProperty Name
    if ($adapters) {
        Write-Host "Found network adapters:" -ForegroundColor Green
        for ($i = 0; $i -lt $adapters.Count; $i++) {
            Write-Host "  [$($i + 1)] $($adapters[$i])" -ForegroundColor Cyan
        }
    }
    else {
        Write-Host "No connected network adapters found" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Failed to get adapters, trying netsh..." -ForegroundColor Yellow
    try {
        $result = netsh interface show interface
        Write-Host $result
    }
    catch {
        Write-Host "Error: Cannot get network adapters" -ForegroundColor Red
        Write-Host "Error message: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Test completed!" -ForegroundColor Green
Read-Host "Press Enter to exit"
