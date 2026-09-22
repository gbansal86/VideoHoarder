[CmdletBinding()]
param([switch]$Deploy)
$ErrorActionPreference = "Stop"
$ScriptRoot = (Resolve-Path -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path
. (Join-Path $ScriptRoot "build_support\Resolve-VideoHoarderPaths.ps1")
. (Join-Path $ScriptRoot "build_support\Initialize-PortableBuild.ps1")
$Paths = Get-VideoHoarderPaths -StartingDirectory $ScriptRoot
$ProjectRoot = $Paths.SourceRoot
$VenvRoot = $Paths.BuildEnvironment
$Python = Initialize-VideoHoarderPortableBuild -Paths $Paths -EnvironmentPath $VenvRoot -RequirementsFile (Join-Path $ProjectRoot "requirements-build.txt")
Set-Location -LiteralPath $ProjectRoot
$DevDist = Join-Path $Paths.ArtifactsDirectory "launcher-dist"
$DevBuild = Join-Path $Paths.ArtifactsDirectory "launcher-build"
& $Python -m PyInstaller --noconfirm --clean --distpath $DevDist --workpath $DevBuild VideoHoarder_launcher.spec
if ($LASTEXITCODE -ne 0) { throw "Development launcher build failed." }
$Built = Join-Path $DevDist "VideoHoarder.exe"
if (-not (Test-Path -LiteralPath $Built)) { throw "Development launcher EXE missing." }
Write-Host "Development launcher built: $Built"
Write-Host "This artifact uses the source and build environment configured in videohoarder.paths.json."
if ($Deploy) {
    $target = Join-Path $Paths.InstallRoot "VideoHoarder-dev-launcher.exe"
    Copy-Item -LiteralPath $Built -Destination $target -Force
    Write-Host "Development launcher deployed separately: $target"
}
