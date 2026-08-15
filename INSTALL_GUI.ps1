[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = Split-Path -Parent $ProjectRoot
$VenvRoot = Join-Path $WorkspaceRoot ".videohoarder-gui"
$VenvPython = Join-Path $VenvRoot "Scripts\python.exe"
$VenvPythonw = Join-Path $VenvRoot "Scripts\pythonw.exe"
$VenvPip = Join-Path $VenvRoot "Scripts\pip.exe"

Set-Location -LiteralPath $ProjectRoot

if (-not (Test-Path -LiteralPath $VenvPython)) {
    $SystemPython = (Get-Command python.exe -ErrorAction Stop).Source
    Write-Host "Creating VideoHoarder's private Python environment..."
    & $SystemPython -m venv $VenvRoot
    if ($LASTEXITCODE -ne 0) { throw "Could not create the Python environment." }
}

if (-not (Test-Path -LiteralPath $VenvPip)) {
    Write-Host "Completing pip setup in the private environment..."
    & $VenvPython -m ensurepip --upgrade --default-pip
    if ($LASTEXITCODE -ne 0) { throw "Could not initialize pip." }
}

Write-Host "Installing the PySide6 desktop interface..."
& $VenvPython -m pip install --disable-pip-version-check --upgrade -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "GUI dependency installation failed." }

Write-Host "Starting VideoHoarder..."
Start-Process -FilePath $VenvPythonw -ArgumentList ('"{0}"' -f (Join-Path $ProjectRoot "run_gui.pyw")) -WorkingDirectory $ProjectRoot
