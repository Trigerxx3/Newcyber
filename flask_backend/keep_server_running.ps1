# PowerShell script to keep the Flask server running reliably
param(
    [switch]$Restart
)

$ErrorActionPreference = "Continue"

function Start-FlaskServer {
    Write-Host "🚀 Starting Cyber Intelligence Platform API Server..." -ForegroundColor Green
    Write-Host "📂 Working directory: $(Get-Location)" -ForegroundColor Cyan
    
    # Kill any existing Python processes
    if ($Restart) {
        Write-Host "🔄 Stopping existing Python processes..." -ForegroundColor Yellow
        Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    
    # Start the server process
    $process = Start-Process -FilePath "python" -ArgumentList "start_server.py" -NoNewWindow -PassThru
    
    if ($process) {
        Write-Host "✅ Server process started with PID: $($process.Id)" -ForegroundColor Green
        return $process
    } else {
        Write-Host "❌ Failed to start server process" -ForegroundColor Red
        return $null
    }
}

function Test-ServerHealth {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Main {
    Write-Host "🔄 Flask Server Manager" -ForegroundColor Magenta
    Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
    Write-Host "="*50 -ForegroundColor Gray
    
    $serverProcess = Start-FlaskServer
    
    if (-not $serverProcess) {
        Write-Host "❌ Failed to start server. Exiting." -ForegroundColor Red
        exit 1
    }
    
    # Monitor the server
    while ($true) {
        Start-Sleep -Seconds 10
        
        # Check if process is still running
        if ($serverProcess.HasExited) {
            Write-Host "⚠️ Server process has stopped. Restarting..." -ForegroundColor Yellow
            $serverProcess = Start-FlaskServer
            continue
        }
        
        # Check if server is responding
        if (-not (Test-ServerHealth)) {
            Write-Host "⚠️ Server health check failed. Restarting..." -ForegroundColor Yellow
            $serverProcess.Kill()
            Start-Sleep -Seconds 2
            $serverProcess = Start-FlaskServer
            continue
        }
        
        Write-Host "✅ Server is healthy (PID: $($serverProcess.Id))" -ForegroundColor Green
    }
}

try {
    Main
} catch {
    Write-Host "❌ Error in server manager: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Write-Host "🛑 Server manager stopped" -ForegroundColor Yellow
}