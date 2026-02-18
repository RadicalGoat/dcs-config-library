# ---------------------------------------------------------------------------
# DPM-010: Simplified Aircraft Template Extraction
# Description: Wraps extract_template.py with machine-specific paths.
# ---------------------------------------------------------------------------

param (
    [Parameter(Mandatory=$true, Position=0)]
    [string]$AircraftName
)

$PythonExe     = "python"

# --- PRE-CONFIGURED PATHS (Set during installation) ---
# $RepoPath      = "<location of DCS repo cloned to users machine>"
# $SaveRoot      = "<location of DCS Saved Games on the user's machine>"

$RepoPath      = "C:\Utils\dcs-config-manager\dcs-config-library-repo"
$SaveRoot      = Join-Path $env:USERPROFILE "Saved Games\DCS"

# Construct paths for templates and script
$RepoTemplates = Join-Path $RepoPath "data\templates"
$ScriptPath    = Join-Path $RepoPath "tools\dcs-config-mapper\extract_template.py"

# Verify the Python script exists before running
if (!(Test-Path $ScriptPath)) {
    Write-Error "Could not find extract_template.py at $ScriptPath"
    exit 1
}

Write-Host "Extracting template for: $AircraftName..." -ForegroundColor Cyan

# Execute the command
& $PythonExe $ScriptPath `
    --saveroot $SaveRoot `
    --repotemplates $RepoTemplates `
    $AircraftName

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: Template for $AircraftName has been updated in the repo folders." -ForegroundColor Green
} else {
    Write-Host "ERROR: Extraction failed. Check the aircraft name and DCS paths." -ForegroundColor Red
}