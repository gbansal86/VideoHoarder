[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptRoot = (Resolve-Path -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path
. (Join-Path $ScriptRoot "build_support\Resolve-VideoHoarderPaths.ps1")
$Paths = Get-VideoHoarderPaths -StartingDirectory $ScriptRoot
$systemPython = (Get-Command python.exe -ErrorAction Stop).Source
$systemRoot = Split-Path -Parent $systemPython

New-Item -ItemType Directory -Path $Paths.PythonRuntime,$Paths.Wheelhouse,$Paths.CacheRoot -Force | Out-Null
Write-Host "Copying the Python runtime into the VideoHoarder parent folder..."
& robocopy.exe $systemRoot $Paths.PythonRuntime /E /XD "__pycache__" "Doc" "Tools" "tcl" "site-packages" /XF "*.pyc" /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Portable Python copy failed (robocopy exit $LASTEXITCODE)." }

$gitCommand = Get-Command git.exe -ErrorAction SilentlyContinue
if ($gitCommand) {
    $gitRoot = (Resolve-Path -LiteralPath (Join-Path (Split-Path -Parent $gitCommand.Source) "..")).Path
    $gitTarget = Join-Path $Paths.ToolsDirectory "git"
    New-Item -ItemType Directory -Path $gitTarget -Force | Out-Null
    & robocopy.exe $gitRoot $gitTarget /E /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Portable Git copy failed (robocopy exit $LASTEXITCODE)." }
}

$portablePython = Join-Path $Paths.PythonRuntime "python.exe"
Write-Host "Caching every build wheel for future offline installs..."
$env:PIP_CACHE_DIR = Join-Path $Paths.CacheRoot "pip"
New-Item -ItemType Directory -Path $env:PIP_CACHE_DIR -Force | Out-Null
& $systemPython -m pip download --disable-pip-version-check --dest $Paths.Wheelhouse -r (Join-Path $Paths.SourceRoot "requirements-build.txt")
if ($LASTEXITCODE -ne 0) { throw "Could not complete the offline wheelhouse." }

Write-Host "Portable Python : $portablePython"
Write-Host "Offline wheels  : $($Paths.Wheelhouse)"
Write-Host "Build cache     : $($Paths.CacheRoot)"
