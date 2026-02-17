# ---------------------------------------------------------------------------
# DCS Config Repo Update Tool (Secure Version)
# Description: Pushed changes to the DCS-Unified-Repo using a local secrets file.
# ---------------------------------------------------------------------------

# --- CONFIGURATION ---
# Set these as needed
# RepoUrl    = "https://github.com/<username>/<dcs_repo-library-name>.git"
# TargetDir  = "<name of local folder to clone repo into - typically C:\Utils\dcs-config-repo>"
# SecretFile = Join-Path $PSScriptRoot ".secrets-dcs-library-readonly"

param (
    [switch]$Debug # Use -Debug to enable verbose output
)

# --- CONFIGURATION ---
$RepoUrl    = "https://github.com/RadicalGoat/dcs-config-library.git"
$RootDir    = "C:\Utils\dcs-config-manager" # Assumed context from previous turns
$TargetDir  = Join-Path $RootDir "dcs-config-library-repo"
$SecretFile = Join-Path $RootDir ".secrets-dcs-library-readwrite"

# --- DEBUG BLOCK: Configuration State ---
if ($Debug) {
    Write-Host "`n--- DEBUG INFO ---" -ForegroundColor Cyan
    Write-Host "Repo URL:         $RepoUrl"
    Write-Host "Target Directory: $TargetDir"
    Write-Host "Secret File:      $SecretFile"
}

# 1. Check for .secrets file
if (!(Test-Path $SecretFile)) {
    Write-Host "CRITICAL: .secrets file not found!" -ForegroundColor Red
    exit 1
}

# 2. Load Token
$GithubToken = Get-Content -Path $SecretFile -Raw

if ([string]::IsNullOrWhiteSpace($GithubToken)) { 
    Write-Error "Token cannot be empty. Exiting."
    exit 1 
}

# --- DEBUG BLOCK: Token & URL Verification ---
if ($Debug) {
    Write-Host "Secret Content:   $($GithubToken.Trim())"
}

$AuthRepoUrl = $RepoUrl.Replace("https://", "https://$($GithubToken.Trim())@")

if ($Debug) {
    Write-Host "Built Auth URL:   $AuthRepoUrl"
}

