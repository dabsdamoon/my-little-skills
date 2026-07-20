#Requires -Version 5.1
[CmdletBinding()]
param(
    [ValidatePattern("^[A-Za-z0-9._-]+$")]
    [string]$TaskName = "Codex-MyLittleSkills-Upgrade",

    [string]$CodexHome
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$resolvedCodexHome = if ($CodexHome) {
    [System.IO.Path]::GetFullPath($CodexHome)
}
elseif ($env:CODEX_HOME) {
    [System.IO.Path]::GetFullPath($env:CODEX_HOME)
}
else {
    Join-Path $env:USERPROFILE ".codex"
}

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($task) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Output "Removed scheduled task '$TaskName'."
}
else {
    Write-Output "Scheduled task '$TaskName' was not installed."
}

$installedScript = Join-Path $resolvedCodexHome "scripts\update-my-little-skills.ps1"
if (Test-Path -LiteralPath $installedScript) {
    Remove-Item -LiteralPath $installedScript -Force
    Write-Output "Removed $installedScript."
}

Write-Output "Update logs were preserved under $resolvedCodexHome\log."
