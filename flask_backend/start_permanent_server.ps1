# PowerShell script for permanent Flask server management
param(
    [switch]$AsService
)

$ErrorActionPreference = "Continue"

# Colors for output
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Cyan = "Cyan"

function Write-ColorText($Text, $Color) {
    Write-Host $Text -ForegroundColor $Color
}

function Test-ServerHealth {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Start-PermanentServer {
    Write-ColorText "===============================================" $Cyan
    Write-ColorText "  Cyber Intelligence Platform Backend" $Cyan
    Write-ColorText "  PERMANENT SERVER MANAGER" $Cyan
    Write-ColorText "===============================================" $Cyan
    Write-Host ""
    Write-ColorText "🔄 Starting permanent server manager..." $Green
    Write-ColorText "📋 This will keep the server running automatically" $Yellow
    Write-ColorText "🛑 Press Ctrl+C to stop the manager" $Yellow
    Write-Host ""
    
    # Kill existing Python processes
    Write-ColorText "🧹 Cleaning up existing processes..." $Yellow
    Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    # Check if requests module is available
    $hasRequests = $false
    try {
        python -c "import requests" 2>$null
        $hasRequests = $true
    } catch {
        Write-ColorText "📦 Installing requests module..." $Yellow
        pip install requests
    }
    
    # Start the server manager
    Write-ColorText "🚀 Launching server manager..." $Green
    python server_manager.py
}

function Start-AsWindowsService {
    Write-ColorText "🔧 Starting as Windows Service..." $Cyan
    
    # Create a scheduled task that runs the server manager
    $taskName = "CyberIntelligenceServer"
    $scriptPath = Join-Path $PSScriptRoot "server_manager.py"
    
    # Remove existing task if it exists
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    
    # Create new task
    $action = New-ScheduledTaskAction -Execute "python" -Argument "`"$scriptPath`"" -WorkingDirectory $PSScriptRoot
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
    
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal
    
    # Start the task
    Start-ScheduledTask -TaskName $taskName
    
    Write-ColorText "✅ Server scheduled to run as Windows service" $Green
    Write-ColorText "📋 Task name: $taskName" $Cyan
    Write-ColorText "🔧 Use Task Scheduler to manage the service" $Yellow
}

try {
    Set-Location $PSScriptRoot
    
    if ($AsService) {
        Start-AsWindowsService
    } else {
        Start-PermanentServer
    }
} catch {
    Write-ColorText "❌ Error: $($_.Exception.Message)" $Red
} finally {
    Write-ColorText "🛑 Script completed" $Yellow
}