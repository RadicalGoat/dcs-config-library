# ---------------------------------------------------------------------------
# DPM-011: Simplified Aircraft Configuration Restore
# Description: Wraps restoredcs.py, auto-detecting hostname for the user.
# ---------------------------------------------------------------------------

param (
    [Parameter(Mandatory=$true, Position=0)]
    [string]$AircraftName
)

$PythonExe = "python"

# --- PRE-CONFIGURED PATHS (Set during installation) ---
# $RepoPath      = "<location of DCS repo cloned to users machine>"
# $SaveRoot      = "<location of DCS Saved Games on the user's machine>"

$RepoPath      = "C:\Utils\dcs-config-manager\dcs-config-library-repo"
$SaveRoot      = Join-Path $env:USERPROFILE "Saved Games\DCS"

# Construct repository sub-paths
$RepoTemplates = Join-Path $RepoPath "data\templates"
$RepoFprints   = Join-Path $RepoPath "data\fingerprints"
$ScriptPath    = Join-Path $RepoPath "tools\dcs-config-mapper\restore_config.py"

# Auto-detect local hostname
$LocalHostname = $env:COMPUTERNAME

# Verify the Python script exists
if (!(Test-Path $ScriptPath)) {
    Write-Error "Could not find restore_config.py at $ScriptPath"
    exit 1
}

Write-Host "Target Machine: $LocalHostname" -ForegroundColor Gray
Write-Host "Restoring configuration for: $AircraftName..." -ForegroundColor Cyan

# Execute the restore command
& $PythonExe $ScriptPath `
    --repofprints $RepoFprints `
    --repotemplates $RepoTemplates `
    --saveroot $SaveRoot `
    $AircraftName `
    $LocalHostname

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: $AircraftName configuration applied to $LocalHostname." -ForegroundColor Green
} else {
    Write-Host "ERROR: Restore failed. Ensure a fingerprint exists for $LocalHostname." -ForegroundColor Red
}