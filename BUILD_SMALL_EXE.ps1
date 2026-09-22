[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptRoot = (Resolve-Path -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path
. (Join-Path $ScriptRoot "build_support\Resolve-VideoHoarderPaths.ps1")
. (Join-Path $ScriptRoot "build_support\Initialize-PortableBuild.ps1")
$Paths = Get-VideoHoarderPaths -StartingDirectory $ScriptRoot
$ProjectRoot = $Paths.SourceRoot
$WorkspaceRoot = $Paths.InstallRoot
$VenvRoot = $Paths.BuildEnvironment
$VenvPython = Join-Path $VenvRoot "Scripts\python.exe"
$VenvPip = Join-Path $VenvRoot "Scripts\pip.exe"
$OutputDir = Join-Path $Paths.ArtifactsDirectory "small-dist"
$WorkDir = Join-Path $Paths.ArtifactsDirectory "small-build"
$RuntimeDir = Join-Path $OutputDir "VideoHoarder"
$OutputExe = Join-Path $RuntimeDir "VideoHoarder.exe"
$OutputZip = Join-Path $OutputDir "VideoHoarder-v33.2-Windows-SmallExe.zip"
$SelfTestRoot = Join-Path $Paths.CacheRoot ("temp\VideoHoarder-small-exe-smoke-" + [Guid]::NewGuid().ToString("N"))

Set-Location -LiteralPath $ProjectRoot

$PromptDir = Join-Path $ProjectRoot "app\prompts"
if (Test-Path -LiteralPath $PromptDir -PathType Container) {
    Get-ChildItem -LiteralPath $PromptDir -File -Force |
        Where-Object { $_.BaseName -match ' - Copy(?: \(\d+\))?$' } |
        Remove-Item -Force
}

Write-Host "Installing build dependencies..."
$VenvPython = Initialize-VideoHoarderPortableBuild -Paths $Paths -EnvironmentPath $VenvRoot -RequirementsFile (Join-Path $ProjectRoot "requirements-build.txt")

Write-Host "Running complete test gate..."
& $VenvPython -m compileall -q app run_gui.pyw scripts
if ($LASTEXITCODE -ne 0) { throw "Python compilation failed." }
& $VenvPython -m pytest -q tests
if ($LASTEXITCODE -ne 0) { throw "Complete pytest gate failed." }

$nativeOutput = & $VenvPython -m pytest -q tests\test_native_ui.py tests\test_phase3_native_ui_contract.py 2>&1
$nativeOutput | ForEach-Object { Write-Host $_ }
if ($LASTEXITCODE -ne 0) { throw "Native PySide6 acceptance failed." }
if (($nativeOutput -join "`n") -match "\bskipped\b") { throw "Native PySide6 acceptance contains skipped tests." }

& $VenvPython build_support\generate_icon.py
if ($LASTEXITCODE -ne 0) { throw "Application icon generation failed." }

Write-Host "Building one-folder Small-EXE release..."
& $VenvPython -m PyInstaller --noconfirm --clean --distpath $OutputDir --workpath $WorkDir VideoHoarder_onedir.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller Small-EXE build failed." }
if (-not (Test-Path -LiteralPath $OutputExe -PathType Leaf)) { throw "Small-EXE output is missing: $OutputExe" }
Export-VideoHoarderRuntimePaths -Paths $Paths -RuntimeDirectory $RuntimeDir -Destination (Join-Path $RuntimeDir "videohoarder.paths.json")

New-Item -ItemType Directory -Path $SelfTestRoot -Force | Out-Null
# The library and evidence locations are isolated; copying the complete
# ~700 MiB Qt/Chromium runtime adds minutes without changing what the EXE
# self-test exercises. Relocation is covered by the relative-path contract.
$SmokeExe = $OutputExe
$SmokeLibrary = Join-Path $SelfTestRoot "FreshLibrary"
$SmokeResult = Join-Path $SelfTestRoot "release_self_test.json"
New-Item -ItemType Directory -Path $SmokeLibrary -Force | Out-Null
$oldLibrary = $env:VLM_LIBRARY_ROOT
$oldSelfTest = $env:VIDEOHOARDER_RELEASE_SELFTEST_OUTPUT
try {
    $env:VLM_LIBRARY_ROOT = $SmokeLibrary
    $env:VIDEOHOARDER_RELEASE_SELFTEST_OUTPUT = $SmokeResult
    $process = Start-Process -FilePath $SmokeExe -ArgumentList "--release-self-test" -PassThru
    if (-not $process.WaitForExit(120000)) {
        $process.Kill()
        throw "Small-EXE clean-room self-test timed out after 120 seconds."
    }
    if ($process.ExitCode -ne 0) { throw "Small-EXE clean-room self-test returned exit code $($process.ExitCode)." }
    if (-not (Test-Path -LiteralPath $SmokeResult -PathType Leaf)) { throw "Small-EXE self-test evidence missing." }
    $smoke = Get-Content -LiteralPath $SmokeResult -Raw | ConvertFrom-Json
    if (-not $smoke.ok -or -not $smoke.queue_acceptance_ok -or -not $smoke.restart_recovery_ok) {
        throw "Small-EXE self-test failed: $(Get-Content -LiteralPath $SmokeResult -Raw)"
    }
} finally {
    $env:VLM_LIBRARY_ROOT = $oldLibrary
    $env:VIDEOHOARDER_RELEASE_SELFTEST_OUTPUT = $oldSelfTest
    if (Test-Path -LiteralPath $SelfTestRoot) { Remove-Item -LiteralPath $SelfTestRoot -Recurse -Force -ErrorAction SilentlyContinue }
}

if (Test-Path -LiteralPath $OutputZip) { Remove-Item -LiteralPath $OutputZip -Force }
Compress-Archive -Path (Join-Path $RuntimeDir "*") -DestinationPath $OutputZip -CompressionLevel Optimal
$ExeSizeMiB = [Math]::Round((Get-Item -LiteralPath $OutputExe).Length / 1MB, 1)
$FolderSizeMiB = [Math]::Round(((Get-ChildItem -LiteralPath $RuntimeDir -Recurse -File | Measure-Object Length -Sum).Sum) / 1MB, 1)
Write-Host ""
Write-Host "Small-EXE release complete."
Write-Host "EXE size   : $ExeSizeMiB MiB"
Write-Host "Folder size: $FolderSizeMiB MiB (QtWebEngine/Chromium remains in sidecar files)"
Write-Host "Run        : $OutputExe"
Write-Host "ZIP        : $OutputZip"
