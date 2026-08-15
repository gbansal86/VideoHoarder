[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
# Qt ships very deeply nested QML resources. Keep the disposable environment
# one level above this long release-folder name to stay within classic Windows
# path limits even when LongPathsEnabled is not configured.
$WorkspaceRoot = Split-Path -Parent $ProjectRoot
$VenvRoot = Join-Path $WorkspaceRoot ".videohoarder-build"
$VenvPython = Join-Path $VenvRoot "Scripts\python.exe"
$VenvPip = Join-Path $VenvRoot "Scripts\pip.exe"
$PyInstaller = Join-Path $VenvRoot "Scripts\pyinstaller.exe"
$OutputZip = Join-Path $ProjectRoot "dist\VideoHoarder-v33.0-Windows.zip"
$OutputExe = Join-Path $ProjectRoot "dist\VideoHoarder.exe"

Set-Location -LiteralPath $ProjectRoot

if (-not (Test-Path -LiteralPath $VenvPython)) {
    $SystemPython = (Get-Command python.exe -ErrorAction Stop).Source
    Write-Host "Creating isolated build environment..."
    & $SystemPython -m venv $VenvRoot
    if ($LASTEXITCODE -ne 0) { throw "Could not create build environment." }
}

if (-not (Test-Path -LiteralPath $VenvPip)) {
    Write-Host "Completing pip setup in the build environment..."
    & $VenvPython -m ensurepip --upgrade --default-pip
    if ($LASTEXITCODE -ne 0) { throw "Could not initialize pip in the build environment." }
}

Write-Host "Installing build dependencies..."
& $VenvPython -m pip install --disable-pip-version-check --upgrade -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw "Build dependency installation failed." }

Write-Host "Running syntax and backend smoke tests..."
& $VenvPython -m compileall -q app run_gui.pyw
if ($LASTEXITCODE -ne 0) { throw "Python compilation failed." }
& $VenvPython -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
& $VenvPython build_support\generate_icon.py
if ($LASTEXITCODE -ne 0) { throw "Application icon generation failed." }

Write-Host "Building the windowed, self-contained application..."
& $PyInstaller --noconfirm --clean VideoHoarder.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }

if (Test-Path -LiteralPath $OutputZip) { Remove-Item -LiteralPath $OutputZip -Force }
Compress-Archive -LiteralPath $OutputExe -DestinationPath $OutputZip -CompressionLevel Optimal

Write-Host ""
Write-Host "Build complete:"
Write-Host $OutputExe
Write-Host $OutputZip
