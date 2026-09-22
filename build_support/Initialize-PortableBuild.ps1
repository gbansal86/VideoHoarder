function Initialize-VideoHoarderPortableBuild {
    param(
        [Parameter(Mandatory=$true)]$Paths,
        [Parameter(Mandatory=$true)][string]$EnvironmentPath,
        [Parameter(Mandatory=$true)][string]$RequirementsFile
    )

    $portablePython = Join-Path $Paths.PythonRuntime "python.exe"
    if (-not (Test-Path -LiteralPath $portablePython -PathType Leaf)) {
        throw "Portable Python is missing: $portablePython. Run PREPARE_PORTABLE_BUILD.ps1 on a connected machine."
    }
    if (-not (Test-Path -LiteralPath $Paths.Wheelhouse -PathType Container)) {
        throw "Offline wheelhouse is missing: $($Paths.Wheelhouse). Run PREPARE_PORTABLE_BUILD.ps1 first."
    }

    New-Item -ItemType Directory -Path $Paths.CacheRoot -Force | Out-Null
    $env:PIP_CACHE_DIR = Join-Path $Paths.CacheRoot "pip"
    $env:PYINSTALLER_CONFIG_DIR = Join-Path $Paths.CacheRoot "pyinstaller"
    $env:TEMP = Join-Path $Paths.CacheRoot "temp"
    $env:TMP = $env:TEMP
    New-Item -ItemType Directory -Path $env:PIP_CACHE_DIR,$env:PYINSTALLER_CONFIG_DIR,$env:TEMP -Force | Out-Null

    $environmentPython = Join-Path $EnvironmentPath "Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $environmentPython -PathType Leaf)) {
        & $portablePython -m venv $EnvironmentPath
        if ($LASTEXITCODE -ne 0) { throw "Could not create portable Python environment: $EnvironmentPath" }
    }
    # A copied venv records its creator's absolute path. Repair that small file
    # on every run so moving the complete parent folder to another drive works.
    $pythonVersion = (& $portablePython -c "import platform; print(platform.python_version())").Trim()
    @(
        "home = $($Paths.PythonRuntime)",
        "include-system-site-packages = false",
        "version = $pythonVersion",
        "executable = $portablePython",
        "command = $portablePython -m venv $EnvironmentPath"
    ) | Set-Content -LiteralPath (Join-Path $EnvironmentPath "pyvenv.cfg") -Encoding UTF8

    & $environmentPython -m pip install --disable-pip-version-check --no-index --find-links $Paths.Wheelhouse -r $RequirementsFile | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "Offline dependency installation failed. Refresh the wheelhouse with PREPARE_PORTABLE_BUILD.ps1." }
    return [string]$environmentPython
}
