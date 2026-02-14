# ---------------------------------------------------------------------------
# DPM-006: DCS Config Repo Sync Tool (Secure Version)
# Description: Pulls or clones the DCS-Unified-Repo using a local .secrets file.
# ---------------------------------------------------------------------------

# --- CONFIGURATION ---
# Set these as needed
# RepoUrl    = "https://github.com/YOUR_ORG/YOUR_REPO.git"
# TargetDir  = "C:\DCS_Config_Manager"
# SecretFile = Join-Path $PSScriptRoot ".secrets"

$RepoUrl   = "https://github.com/RadicalGoat/test-dcs-library.git"
$RootDir  = "test\dummy-filesystem\utils\dcs-config-manager"
$TargetDir  = Join-Path $RootDir "dcs-config-repo"
$SecretFile = Join-Path $RootDir ".github-secret"

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

$AuthRepoUrl = $RepoUrl.Replace("https://", "https://$($GithubToken.Trim())@")

# 3. Execute Git Sync
if (!(Test-Path -Path $TargetDir)) {
    Write-Host "Initial Setup: Cloning repo to $TargetDir..." -ForegroundColor Cyan
    git clone $AuthRepoUrl $TargetDir
} else {
    Write-Host "Syncing repo at $TargetDir..." -ForegroundColor Yellow
    Push-Location $TargetDir
    git fetch --all
    git reset --hard origin/main 
    Pop-Location
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: Repository is up to date." -ForegroundColor Green
} else {
    Write-Error "FAILURE: Git command failed. Check your token or network."
}