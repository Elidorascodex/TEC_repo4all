# TEC Automation PowerShell Launcher
# This script activates the virtual environment and runs the automation pipeline

Write-Host "TEC_repo4all Automation Pipeline Launcher" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Define paths
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptPath
$venvPath = Join-Path -Path $repoRoot -ChildPath "venv"
$pythonScript = Join-Path -Path $scriptPath -ChildPath "run_automation.py"
$configPath = Join-Path -Path $repoRoot -ChildPath "config"
$envFile = Join-Path -Path $configPath -ChildPath ".env"
$envExampleFile = Join-Path -Path $configPath -ChildPath ".env.example"

# Check if virtual environment exists
if (-not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found. Creating one now..." -ForegroundColor Yellow
    
    # Create virtual environment
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    python -m venv $venvPath
    
    if (-not (Test-Path $venvPath)) {
        Write-Host "Failed to create virtual environment. Please make sure Python is installed and in your PATH." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Virtual environment created successfully." -ForegroundColor Green
}

# Check if .env file exists
if (-not (Test-Path $envFile)) {
    Write-Host ".env file not found in config directory." -ForegroundColor Yellow
    
    if (Test-Path $envExampleFile) {
        Write-Host "Found .env.example file. You need to create a .env file with your credentials." -ForegroundColor Yellow
        Write-Host "Would you like to copy the example file to .env? (You'll still need to edit it)" -ForegroundColor Yellow
        $createEnv = Read-Host "Create .env from example? (Y/N)"
        
        if ($createEnv -eq "Y" -or $createEnv -eq "y") {
            Copy-Item -Path $envExampleFile -Destination $envFile
            Write-Host ".env file created. Please edit it with your actual credentials before running the automation." -ForegroundColor Green
            Write-Host "Open the file in a text editor: $envFile" -ForegroundColor Green
            exit 0
        }
        else {
            Write-Host "You need to create a .env file with your credentials before running the automation." -ForegroundColor Yellow
            Write-Host "Use the .env.example file as a template." -ForegroundColor Yellow
            exit 1
        }
    }
    else {
        Write-Host ".env.example file not found. Please create a .env file in the config directory with your credentials." -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
$activateScript = Join-Path -Path $venvPath -ChildPath "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    & $activateScript
}
else {
    Write-Host "Activation script not found. The virtual environment may be corrupted." -ForegroundColor Red
    exit 1
}

# Check if requirements are installed
$requirementsFile = Join-Path -Path $repoRoot -ChildPath "requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "Checking if requirements are installed..." -ForegroundColor Green
    
    # Simple check - try importing yaml
    $checkImport = python -c "try: import yaml; print('OK'); except ImportError: print('MISSING')"
    
    if ($checkImport -ne "OK") {
        Write-Host "Installing requirements from $requirementsFile..." -ForegroundColor Yellow
        pip install -r $requirementsFile
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to install requirements. Please check the error message above." -ForegroundColor Red
            exit 1
        }
        
        Write-Host "Requirements installed successfully." -ForegroundColor Green
    }
}

# Run the automation script
Write-Host "Running TEC automation pipeline..." -ForegroundColor Green
python $pythonScript

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Host "Automation pipeline execution failed with exit code $LASTEXITCODE." -ForegroundColor Red
}
else {
    Write-Host "Automation pipeline completed successfully." -ForegroundColor Green
}

# Deactivate virtual environment (it's automatically deactivated when the script ends)
deactivate

Write-Host ""
Write-Host "Pipeline execution finished." -ForegroundColor Cyan