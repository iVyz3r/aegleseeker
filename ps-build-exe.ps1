Write-Host "Setting up the environment..."
$venvPath = Join-Path $PSScriptRoot 'venv'

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating VENV environment..."
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment."
        exit $LASTEXITCODE
    }
} else {
    Write-Host "VENV already exists."
}

$activateScript = Join-Path $venvPath 'Scripts\Activate.ps1'
if (Test-Path $activateScript) {
    Write-Host "Activating VENV..."
    & $activateScript
} else {
    Write-Error "Cannot find Activate.ps1. Ensure the venv was created correctly."
    exit 1
}

Write-Host "Installing required packages..."
$venvPython = Join-Path $venvPath 'Scripts\python.exe'
& $venvPython -m pip install pymem dearpygui pypresence pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Error "Package installation failed."
    exit $LASTEXITCODE
}

Write-Host "Building the executable..."
$pyinstallerExe = Join-Path $venvPath 'Scripts\pyinstaller.exe'
if (Test-Path $pyinstallerExe) {
    & $pyinstallerExe --onefile --noconsole --icon="aegleseeker.ico" aeglemain.py
} else {
    & $venvPython -m PyInstaller --onefile --noconsole --icon="aegleseeker.ico" aeglemain.py
}
if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller build failed."
    exit $LASTEXITCODE
}

Write-Host "Build complete"

Write-Host "Deactivating VENV environment..."
if (Get-Command Deactivate -ErrorAction SilentlyContinue) {
    Deactivate
} else {
    Write-Host "No PowerShell deactivate function found; close the shell or manually deactivate if needed."
}

Write-Host "Build process finished."
