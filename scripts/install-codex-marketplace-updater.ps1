#Requires -Version 5.1
[CmdletBinding()]
param(
    [ValidatePattern("^[A-Za-z0-9._-]+$")]
    [string]$Marketplace = "my-little-skills",

    [ValidatePattern("^[A-Za-z0-9._-]+$")]
    [string]$TaskName = "Codex-MyLittleSkills-Upgrade",

    [ValidateRange(0, 23)]
    [int]$DailyHour = 3,

    [string]$CodexExecutable,

    [string]$CodexHome,

    [switch]$RunNow
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-CodexExecutable {
    param([string]$RequestedPath)

    if ($RequestedPath) {
        $resolvedPath = [System.IO.Path]::GetFullPath($RequestedPath)
        if (-not (Test-Path -LiteralPath $resolvedPath -PathType Leaf)) {
            throw "Codex executable was not found at $resolvedPath."
        }
        return $resolvedPath
    }

    foreach ($commandName in @("codex.exe", "codex")) {
        $command = Get-Command $commandName -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($command -and $command.Path) {
            return $command.Path
        }
    }

    throw "Codex CLI was not found. Install Codex and make sure the codex command is available."
}

$sourceScript = Join-Path $PSScriptRoot "update-codex-marketplace.ps1"
if (-not (Test-Path -LiteralPath $sourceScript)) {
    throw "Updater script was not found at $sourceScript."
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
$installDirectory = Join-Path $resolvedCodexHome "scripts"
$installedScript = Join-Path $installDirectory "update-my-little-skills.ps1"
New-Item -ItemType Directory -Force -Path $installDirectory | Out-Null
Copy-Item -LiteralPath $sourceScript -Destination $installedScript -Force

$powerShell = Join-Path $PSHOME "powershell.exe"
$arguments = "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$installedScript`" -Marketplace `"$Marketplace`" -CodexExecutable `"$resolvedCodex`" -CodexHome `"$resolvedCodexHome`""
$action = New-ScheduledTaskAction -Execute $powerShell -Argument $arguments

$identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $identity -RandomDelay (New-TimeSpan -Minutes 5)
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At ([DateTime]::Today.AddHours($DailyHour)) -RandomDelay (New-TimeSpan -Minutes 30)
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
$task = New-ScheduledTask `
    -Action $action `
    -Trigger @($logonTrigger, $dailyTrigger) `
    -Settings $settings `
    -Principal $principal `
    -Description "Refresh the $Marketplace Codex marketplace and its installed plugins at logon and daily."

Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force | Out-Null

if ($RunNow) {
    & $installedScript -Marketplace $Marketplace -CodexExecutable $resolvedCodex -CodexHome $resolvedCodexHome
}

Write-Output "Installed scheduled task '$TaskName' for $identity."
Write-Output "Marketplace: $Marketplace"
Write-Output "Codex home: $resolvedCodexHome"
Write-Output "Schedule: at logon and daily near $($DailyHour.ToString('00')):00."
Write-Output "Inspect it with: Get-ScheduledTask -TaskName '$TaskName'"
