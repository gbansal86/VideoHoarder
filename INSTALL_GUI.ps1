[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptRoot = (Resolve-Path -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path
. (Join-Path $ScriptRoot "build_support\Resolve-VideoHoarderPaths.ps1")
. (Join-Path $ScriptRoot "build_support\Initialize-PortableBuild.ps1")
$Paths = Get-VideoHoarderPaths -StartingDirectory $ScriptRoot
$ProjectRoot = $Paths.SourceRoot
$WorkspaceRoot = $Paths.InstallRoot
$VenvRoot = $Paths.GuiEnvironment
$VenvPython = Join-Path $VenvRoot "Scripts\python.exe"
$VenvPythonw = Join-Path $VenvRoot "Scripts\pythonw.exe"
$VenvPip = Join-Path $VenvRoot "Scripts\pip.exe"

Set-Location -LiteralPath $ProjectRoot

Write-Host "Installing the PySide6 desktop interface..."
$VenvPython = Initialize-VideoHoarderPortableBuild -Paths $Paths -EnvironmentPath $VenvRoot -RequirementsFile (Join-Path $ProjectRoot "requirements.txt")
$VenvPythonw = Join-Path $VenvRoot "Scripts\pythonw.exe"

Write-Host "Starting VideoHoarder..."
Start-Process -FilePath $VenvPythonw -ArgumentList ('"{0}"' -f (Join-Path $ProjectRoot "run_gui.pyw")) -WorkingDirectory $ProjectRoot
