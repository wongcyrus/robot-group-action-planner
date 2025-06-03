# PowerShell script to create and set up a Python virtual environment
# Created: June 3, 2025

# Configuration
$venvName = "venv"
$requirementsFile = "requirements.txt"

Write-Host "Setting up Python virtual environment for robot-group-action-planner..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found $pythonVersion" -ForegroundColor Cyan
}
catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path $venvName)) {
    Write-Host "Creating virtual environment: $venvName" -ForegroundColor Cyan
    python -m venv $venvName
}
else {
    Write-Host "Virtual environment already exists: $venvName" -ForegroundColor Yellow
}

# Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
$activateScript = Join-Path -Path $venvName -ChildPath "Scripts\Activate.ps1"
& $activateScript

# Check if requirements.txt exists and install dependencies
if (Test-Path $requirementsFile) {
    Write-Host "Installing dependencies from $requirementsFile..." -ForegroundColor Cyan
    pip install -r $requirementsFile
}
else {
    Write-Host "No $requirementsFile found. Creating an empty one." -ForegroundColor Yellow
    "# Python dependencies for robot-group-action-planner" | Out-File -FilePath $requirementsFile
    "# Add your dependencies below, for example:" | Out-File -FilePath $requirementsFile -Append
    "# numpy==1.21.0" | Out-File -FilePath $requirementsFile -Append
    "# pandas==1.3.0" | Out-File -FilePath $requirementsFile -Append
}

Write-Host "Virtual environment setup complete!" -ForegroundColor Green
Write-Host "To activate the virtual environment in the future, run: .\$venvName\Scripts\Activate.ps1" -ForegroundColor Cyan
