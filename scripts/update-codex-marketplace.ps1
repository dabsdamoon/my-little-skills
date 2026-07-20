#Requires -Version 5.1
[CmdletBinding()]
param(
    [ValidatePattern("^[A-Za-z0-9._-]+$")]
    [string]$Marketplace = "my-little-skills",

    [string]$CodexExecutable,

    [string]$CodexHome,

    [string]$LogPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-CodexExecutable {
    param([string]$RequestedPath)

    if ($RequestedPath) {
        $resolvedPath = [System.IO.Path]::GetFullPath($RequestedPath)
        if (Test-Path -LiteralPath $resolvedPath -PathType Leaf) {
            return $resolvedPath
        }
    }

    foreach ($commandName in @("codex.exe", "codex")) {
        $command = Get-Command $commandName -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($command -and $command.Path) {
            return $command.Path
        }
    }

    $installRoot = Join-Path $env:LOCALAPPDATA "OpenAI\Codex\bin"
    if (Test-Path -LiteralPath $installRoot) {
        $candidate = Get-ChildItem -LiteralPath $installRoot -Filter codex.exe -File -Recurse -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if ($candidate) {
            return $candidate.FullName
        }
    }

    throw "Codex CLI was not found. Install Codex and make sure the codex command is available."
}

$resolvedCodex = Resolve-CodexExecutable -RequestedPath $CodexExecutable
$resolvedCodexHome = if ($CodexHome) {
    [System.IO.Path]::GetFullPath($CodexHome)
}
elseif ($env:CODEX_HOME) {
    [System.IO.Path]::GetFullPath($env:CODEX_HOME)
}
else {
    Join-Path $env:USERPROFILE ".codex"
}

New-Item -ItemType Directory -Force -Path $resolvedCodexHome | Out-Null
$env:CODEX_HOME = $resolvedCodexHome

if (-not $LogPath) {
    $LogPath = Join-Path $resolvedCodexHome "log\marketplace-updates.log"
}
else {
    $LogPath = [System.IO.Path]::GetFullPath($LogPath)
}

$logDirectory = Split-Path -Parent $LogPath
if ($logDirectory) {
    New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
}

if ((Test-Path -LiteralPath $LogPath) -and (Get-Item -LiteralPath $LogPath).Length -gt 1MB) {
    Move-Item -LiteralPath $LogPath -Destination "$LogPath.1" -Force
}

$mutex = New-Object System.Threading.Mutex($false, "Local\CodexMarketplace-$Marketplace")
$lockAcquired = $false
try {
    try {
        $lockAcquired = $mutex.WaitOne(0)
    }
    catch [System.Threading.AbandonedMutexException] {
        $lockAcquired = $true
    }

    if (-not $lockAcquired) {
        Write-Output "Marketplace updater '$Marketplace' is already running."
        return
    }

    $startedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -LiteralPath $LogPath -Value "[$startedAt] marketplace=$Marketplace codex_home=$resolvedCodexHome status=starting"

    try {
        $output = & $resolvedCodex plugin marketplace upgrade $Marketplace 2>&1
        $exitCode = $LASTEXITCODE
        $output | ForEach-Object { Add-Content -LiteralPath $LogPath -Value ([string]$_) }
    }
    catch {
        Add-Content -LiteralPath $LogPath -Value ([string]$_)
        throw
    }

    $status = if ($exitCode -eq 0) { "succeeded" } else { "failed" }
    $finishedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -LiteralPath $LogPath -Value "[$finishedAt] marketplace=$Marketplace status=$status exit=$exitCode"

    if ($exitCode -ne 0) {
        throw "Codex marketplace update failed with exit code $exitCode. See $LogPath."
    }

    Write-Output "Updated Codex marketplace '$Marketplace' in '$resolvedCodexHome'. Log: $LogPath"
}
finally {
    if ($lockAcquired) {
        $mutex.ReleaseMutex()
    }
    $mutex.Dispose()
}
