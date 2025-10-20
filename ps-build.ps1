Write-Host "Setting up the environment..."
Write-Host "Installing required packages..."

python -m pip install pymem dearpygui pypresence pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Error "Package installation failed."
    exit $LASTEXITCODE
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    py main.py
} else {
    python main.py
}

Write-Host "Build complete"
Write-Host "Setting up the environment..."
Write-Host "Installing required packages..."

python -m pip install pymem dearpygui pypresence pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Error "Package installation failed."
    exit $LASTEXITCODE
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    py aeglemain.py
} else {
    python aeglemain.py
}

Write-Host "Build complete"
