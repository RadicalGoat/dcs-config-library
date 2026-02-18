
# ---------------------------------------------------------------------------
# DPM-011: Setup Contributor Remote
# Description: Adds a dedicated 'contributor' remote for Read/Write access.
# ---------------------------------------------------------------------------

param (
    [switch]$DebugMode
)

# --- CONFIGURATION ---
# Set these as needed
# RepoUrl    = "https://github.com/<username>/<dcs_repo-library-name>.git"
# TargetDir  = "<name of local folder to clone repo into - typically C:\Utils\dcs-config-repo>"
# SecretFile = Join-Path $PSScriptRoot ".secrets-dcs-library-readonly"

$RepoUrl    = "github.com/RadicalGoat/dcs-config-library.git" # Clean URL without https://
$RootDir    = "C:\Utils\dcs-config-manager"
$TargetDir  = Join-Path $RootDir "dcs-config-library-repo"
# Use a DIFFERENT secret file for the RW token
$SecretFile = Join-Path $RootDir ".secrets-dcs-library-readwrite"

# --- DEBUG BLOCK: Configuration State ---
if ($Debug) {
    Write-Host "`n--- DEBUG INFO ---" -ForegroundColor Cyan
    Write-Host "Repo URL:         $RepoUrl"
    Write-Host "Target Directory: $TargetDir"
    Write-Host "Secret File:      $SecretFile"
}

# 1. Check for RW secrets file
if (!(Test-Path $SecretFile)) {
    Write-Host "CRITICAL: Read/Write secret file not found at $SecretFile" -ForegroundColor Red
    exit 1
}

$RWToken = (Get-Content -Path $SecretFile -Raw).Trim()

if ([string]::IsNullOrWhiteSpace($RWToken)) { 
    Write-Error "RW Token cannot be empty. Exiting."
    exit 1 
}

$AuthRWUrl = "https://$($RWToken)@$($RepoUrl)"

# 2. Enter Repo Directory
if (!(Test-Path $TargetDir)) {
    Write-Error "Target directory $TargetDir does not exist. Run refresh_dcs_repo.ps1 first."
    exit 1
}
Push-Location $TargetDir

# 3. Logic to Add or Update 'contributor' remote
$ExistingRemotes = git remote
if ($ExistingRemotes -contains "contributor") {
    Write-Host "Updating existing contributor remote..." -ForegroundColor Yellow
    git remote set-url contributor $AuthRWUrl
} else {
    Write-Host "Adding new contributor remote..." -ForegroundColor Cyan
    git remote add contributor $AuthRWUrl
}

# 4. Debug Output
if ($DebugMode) {
    Write-Host "`n--- REMOTE CONFIGURATION ---" -ForegroundColor Gray
    git remote -v
    Write-Host "----------------------------`n"
}

Pop-Location
Write-Host "SUCCESS: You can now push changes using: git push contributor main" -ForegroundColor Green




