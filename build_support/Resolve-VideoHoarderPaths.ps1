function Get-VideoHoarderPaths {
    param([Parameter(Mandatory=$true)][string]$StartingDirectory)

    $cursor = (Resolve-Path -LiteralPath $StartingDirectory).Path
    $configPath = $null
    for ($i = 0; $i -lt 6; $i++) {
        $candidate = Join-Path $cursor "videohoarder.paths.json"
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { $configPath = $candidate; break }
        $parent = Split-Path -Parent $cursor
        if (-not $parent -or $parent -eq $cursor) { break }
        $cursor = $parent
    }
    if (-not $configPath) { throw "videohoarder.paths.json was not found above $StartingDirectory" }

    $config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
    $configDirectory = Split-Path -Parent $configPath
    $installRoot = if ([IO.Path]::IsPathRooted([string]$config.install_root)) {
        [IO.Path]::GetFullPath([string]$config.install_root)
    } else {
        [IO.Path]::GetFullPath((Join-Path $configDirectory ([string]$config.install_root)))
    }
    function Resolve-ConfiguredPath([string]$Value) {
        if ([IO.Path]::IsPathRooted($Value)) { return [IO.Path]::GetFullPath($Value) }
        return [IO.Path]::GetFullPath((Join-Path $installRoot $Value))
    }

    $sourceRoot = Resolve-ConfiguredPath ([string]$config.source_dir)
    if (-not (Test-Path -LiteralPath $sourceRoot -PathType Container)) {
        throw "Configured source_dir does not exist: $sourceRoot"
    }
    $config.last_known_install_root = $installRoot
    $config | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $configPath -Encoding UTF8

    [pscustomobject]@{
        ConfigPath = $configPath
        InstallRoot = $installRoot
        SourceRoot = $sourceRoot
        BuildEnvironment = Resolve-ConfiguredPath ([string]$config.build_environment)
        GuiEnvironment = Resolve-ConfiguredPath ([string]$config.gui_environment)
        PythonRuntime = Resolve-ConfiguredPath ([string]$config.python_runtime)
        Wheelhouse = Resolve-ConfiguredPath ([string]$config.wheelhouse)
        CacheRoot = Resolve-ConfiguredPath ([string]$config.cache_root)
        ArtifactsDirectory = Resolve-ConfiguredPath ([string]$config.artifacts_dir)
        ToolsDirectory = Resolve-ConfiguredPath ([string]$config.tools_dir)
        LibraryRoot = Resolve-ConfiguredPath ([string]$config.library_root)
        VideoLibrary = Resolve-ConfiguredPath ([string]$config.video_library_dir)
    }
}

function Export-VideoHoarderRuntimePaths {
    param(
        [Parameter(Mandatory=$true)]$Paths,
        [Parameter(Mandatory=$true)][string]$RuntimeDirectory,
        [Parameter(Mandatory=$true)][string]$Destination
    )
    $runtime = [IO.Path]::GetFullPath($RuntimeDirectory)
    $install = [IO.Path]::GetFullPath([string]$Paths.InstallRoot)
    $config = Get-Content -LiteralPath $Paths.ConfigPath -Raw | ConvertFrom-Json
    $config.install_root = [IO.Path]::GetRelativePath($runtime, $install).Replace('\','/')
    $config.last_known_install_root = $install
    $config | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $Destination -Encoding UTF8
}
