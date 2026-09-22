[CmdletBinding()]
param(
    [switch]$CleanTempAfterBuild,
    [switch]$Deploy
)

$ErrorActionPreference = "Stop"
$ScriptRoot = (Resolve-Path -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path
. (Join-Path $ScriptRoot "build_support\Resolve-VideoHoarderPaths.ps1")
. (Join-Path $ScriptRoot "build_support\Initialize-PortableBuild.ps1")
$Paths = Get-VideoHoarderPaths -StartingDirectory $ScriptRoot
$ProjectRoot = $Paths.SourceRoot
$ProjectRootItem = Get-Item -LiteralPath $ProjectRoot -Force
if (($ProjectRootItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -and $ProjectRootItem.Target) {
    $ProjectRoot = @($ProjectRootItem.Target)[0]
}
$WorkspaceRoot = $Paths.InstallRoot
$VenvRoot = $Paths.BuildEnvironment
$VenvPython = Join-Path $VenvRoot "Scripts\python.exe"
$VenvPip = Join-Path $VenvRoot "Scripts\pip.exe"
$OutputDir = Join-Path $Paths.ArtifactsDirectory "full-dist"
$WorkDir = Join-Path $Paths.ArtifactsDirectory "full-build"
$OutputZip = Join-Path $OutputDir "VideoHoarder-v33.2-Windows.zip"
$OutputExe = Join-Path $OutputDir "VideoHoarder.exe"
$SelfTestRoot = Join-Path $Paths.CacheRoot ("temp\VideoHoarder-clean-smoke-" + [Guid]::NewGuid().ToString("N"))

$InstallRoot = $Paths.InstallRoot
$InstalledExe = Join-Path $InstallRoot "VideoHoarder.exe"
$BackupExe = Join-Path $InstallRoot "VideoHoarder_previous.exe"

function Remove-IfSafeDirectory {
    param([Parameter(Mandatory=$true)][string]$PathToRemove,[Parameter(Mandatory=$true)][string]$AllowedParent)
    if (-not (Test-Path -LiteralPath $PathToRemove -PathType Container)) { return }
    $resolvedTarget = (Resolve-Path -LiteralPath $PathToRemove).Path
    $resolvedParent = (Resolve-Path -LiteralPath $AllowedParent).Path
    if (-not $resolvedTarget.StartsWith($resolvedParent, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing cleanup outside allowed parent: $resolvedTarget"
    }
    Remove-Item -LiteralPath $resolvedTarget -Recurse -Force
}

function Remove-PythonCacheUnder {
    param([Parameter(Mandatory=$true)][string]$Root)
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return }
    Get-ChildItem -LiteralPath $Root -Recurse -Force -Directory -ErrorAction SilentlyContinue |
        Where-Object { -not ($_.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -and $_.Name -in @("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache") } |
        Sort-Object FullName -Descending | ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }
}

Set-Location -LiteralPath $ProjectRoot

# ChatGPT/file-sync tools sometimes leave duplicate prompt copies in the
# source tree. They are never valid application inputs and make the audit gate
# fail nondeterministically. Remove only the known duplicate naming pattern,
# then fail early if any such file remains.
$PromptDir = Join-Path $ProjectRoot "app\prompts"
if (Test-Path -LiteralPath $PromptDir -PathType Container) {
    Get-ChildItem -LiteralPath $PromptDir -File -Force |
        Where-Object { $_.BaseName -match ' - Copy(?: \(\d+\))?$' } |
        Remove-Item -Force
    $duplicatePrompts = @(Get-ChildItem -LiteralPath $PromptDir -File -Force |
        Where-Object { $_.BaseName -match ' - Copy(?: \(\d+\))?$' })
    if ($duplicatePrompts.Count -gt 0) {
        throw "Duplicate prompt copies remain in app\prompts: $($duplicatePrompts.Name -join ', ')"
    }
}

Write-Host "Installing release/build dependencies..."
$VenvPython = Initialize-VideoHoarderPortableBuild -Paths $Paths -EnvironmentPath $VenvRoot -RequirementsFile (Join-Path $ProjectRoot "requirements-build.txt")

Write-Host "Running syntax validation and complete pytest gate..."
& $VenvPython -m compileall -q app run_gui.pyw scripts
if ($LASTEXITCODE -ne 0) { throw "Python compilation failed." }
& $VenvPython -m pytest -q tests
if ($LASTEXITCODE -ne 0) { throw "Complete pytest gate failed." }

Write-Host "Running native PySide6 acceptance subset (skips are not allowed in the Windows build environment)..."
$nativeOutput = & $VenvPython -m pytest -q tests\test_native_ui.py tests\test_phase3_native_ui_contract.py 2>&1
$nativeOutput | ForEach-Object { Write-Host $_ }
if ($LASTEXITCODE -ne 0) { throw "Native PySide6 acceptance tests failed." }
if (($nativeOutput -join "`n") -match "\bskipped\b") { throw "Native PySide6 acceptance contains skipped tests. Investigate before release." }

& $VenvPython build_support\generate_icon.py
if ($LASTEXITCODE -ne 0) { throw "Application icon generation failed." }

if (-not (Test-Path -LiteralPath $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir | Out-Null }
Write-Host "Building the true self-contained VideoHoarder application..."
& $VenvPython -m PyInstaller --noconfirm --clean --distpath $OutputDir --workpath $WorkDir VideoHoarder.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller release build failed." }
if (-not (Test-Path -LiteralPath $OutputExe -PathType Leaf)) { throw "Release EXE is missing: $OutputExe" }
$OutputPathConfig = Join-Path $OutputDir "videohoarder.paths.json"
Export-VideoHoarderRuntimePaths -Paths $Paths -RuntimeDirectory $OutputDir -Destination $OutputPathConfig

# Clean-room smoke: only the EXE and a fresh writable library root are present.
Write-Host "Running clean-room self-test with no Source, build venv or system Python dependency beside the EXE..."
New-Item -ItemType Directory -Path $SelfTestRoot -Force | Out-Null
$SmokeExe = Join-Path $SelfTestRoot "VideoHoarder.exe"
$SmokeLibrary = Join-Path $SelfTestRoot "FreshLibrary"
$SmokeResult = Join-Path $SelfTestRoot "release_self_test.json"
New-Item -ItemType Directory -Path $SmokeLibrary -Force | Out-Null
Copy-Item -LiteralPath $OutputExe -Destination $SmokeExe -Force
$oldLibrary = $env:VLM_LIBRARY_ROOT
$oldSelfTest = $env:VIDEOHOARDER_RELEASE_SELFTEST_OUTPUT
try {
    $env:VLM_LIBRARY_ROOT = $SmokeLibrary
    $env:VIDEOHOARDER_RELEASE_SELFTEST_OUTPUT = $SmokeResult
    $process = Start-Process -FilePath $SmokeExe -ArgumentList "--release-self-test" -PassThru
    if (-not $process.WaitForExit(120000)) {
        $process.Kill()
        throw "Release clean-room self-test timed out after 120 seconds."
    }
    if ($process.ExitCode -ne 0) { throw "Clean-room release self-test returned exit code $($process.ExitCode)." }
    if (-not (Test-Path -LiteralPath $SmokeResult -PathType Leaf)) { throw "Clean-room self-test did not write evidence." }
    $smoke = Get-Content -LiteralPath $SmokeResult -Raw | ConvertFrom-Json
    if (-not $smoke.ok -or -not $smoke.frozen -or $smoke.source_neighbor_exists -or $smoke.build_venv_neighbor_exists -or -not $smoke.backend_http_ready -or -not $smoke.queue_acceptance_ok -or -not $smoke.restart_recovery_ok) {
        throw "Clean-room release self-test evidence is not acceptable: $(Get-Content -LiteralPath $SmokeResult -Raw)"
    }
    Copy-Item -LiteralPath $SmokeResult -Destination (Join-Path $OutputDir "release_self_test.json") -Force
} finally {
    $env:VLM_LIBRARY_ROOT = $oldLibrary
    $env:VIDEOHOARDER_RELEASE_SELFTEST_OUTPUT = $oldSelfTest
    if (Test-Path -LiteralPath $SelfTestRoot) { Remove-Item -LiteralPath $SelfTestRoot -Recurse -Force -ErrorAction SilentlyContinue }
}

if (Test-Path -LiteralPath $OutputZip) { Remove-Item -LiteralPath $OutputZip -Force }

$BuildInfoPath = Join-Path $OutputDir "BUILD_INFO.txt"
$DependencySnapshotPath = Join-Path $OutputDir "DEPENDENCIES.txt"
$AppVersion = (Get-Content -LiteralPath (Join-Path $ProjectRoot "app\\VERSION.txt") -Raw).Trim()
$BuiltHash = (Get-FileHash -LiteralPath $OutputExe -Algorithm SHA256).Hash
$PythonVersion = (& $VenvPython --version).Trim()
$PyInstallerVersion = (& $VenvPython -m PyInstaller --version).Trim()
& $VenvPython -m pip freeze | Set-Content -LiteralPath $DependencySnapshotPath -Encoding UTF8
@(
    "VideoHoarder version: $AppVersion"
    "Build host: $env:COMPUTERNAME"
    "Python: $PythonVersion"
    "PyInstaller: $PyInstallerVersion"
    "VideoHoarder.exe SHA256: $BuiltHash"
    "Dependency snapshot: DEPENDENCIES.txt"
) | Set-Content -LiteralPath $BuildInfoPath -Encoding UTF8

$ZipItems = @(
    $OutputExe,
    (Join-Path $OutputDir "release_self_test.json"),
    $OutputPathConfig,
    $BuildInfoPath,
    $DependencySnapshotPath
)
Compress-Archive -LiteralPath $ZipItems -DestinationPath $OutputZip -CompressionLevel Optimal

if ($Deploy) {
    Write-Host "Deploying the self-contained application..."
    if (Test-Path -LiteralPath $InstalledExe -PathType Leaf) {
        try {
            Copy-Item -LiteralPath $InstalledExe -Destination $BackupExe -Force
        } catch {
            throw "The current VideoHoarder executable could not be backed up. Close VideoHoarder if it is running and retry. $($_.Exception.Message)"
        }
    }
    try {
        Copy-Item -LiteralPath $OutputExe -Destination $InstalledExe -Force
    } catch {
        throw "The self-contained release could not be deployed. Close VideoHoarder if it is running and retry. $($_.Exception.Message)"
    }
    $BuiltHash = (Get-FileHash -LiteralPath $OutputExe -Algorithm SHA256).Hash
    $InstalledHash = (Get-FileHash -LiteralPath $InstalledExe -Algorithm SHA256).Hash
    if ($BuiltHash -ne $InstalledHash) { throw "Deployment verification failed." }
    Write-Host "Deployed and SHA256 verified: $InstalledExe"
}

if ($CleanTempAfterBuild) {
    Remove-IfSafeDirectory -PathToRemove (Join-Path $ProjectRoot "build") -AllowedParent $ProjectRoot
    Remove-PythonCacheUnder -Root $ProjectRoot
}

$ExeSizeMiB = [Math]::Round((Get-Item -LiteralPath $OutputExe).Length / 1MB, 1)
Write-Host ""
Write-Host "Self-contained release complete:"
Write-Host "EXE size: $ExeSizeMiB MiB (full build includes PySide6 + QtWebEngine/Chromium for specialist embedded web pages)"
Write-Host "EXE : $OutputExe"
Write-Host "ZIP : $OutputZip"
Write-Host "Clean-room evidence: $(Join-Path $OutputDir 'release_self_test.json')"
if ($Deploy) { Write-Host "Live: $InstalledExe" }
