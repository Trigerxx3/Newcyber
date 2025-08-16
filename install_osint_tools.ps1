# PowerShell script to install OSINT tools

# Create OSINT tools directory
Write-Host "Creating OSINT tools directory..." -ForegroundColor Green
New-Item -ItemType Directory -Path "osint_tools" -Force
Set-Location "osint_tools"

# Install Sherlock
Write-Host "Installing Sherlock..." -ForegroundColor Yellow
git clone https://github.com/sherlock-project/sherlock.git
Set-Location "sherlock"
python -m pip install -r requirements.txt
Set-Location ".."

# Install Spiderfoot
Write-Host "Installing Spiderfoot..." -ForegroundColor Yellow
git clone https://github.com/smicallef/spiderfoot.git
Set-Location "spiderfoot"
python -m pip install -r requirements.txt
Set-Location ".."

Write-Host "OSINT tools installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "  Sherlock: python osint_tools\sherlock\sherlock.py [username]" -ForegroundColor White
Write-Host "  SpiderFoot: python osint_tools\spiderfoot\sf.py" -ForegroundColor White
