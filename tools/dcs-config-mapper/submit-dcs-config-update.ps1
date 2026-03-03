# ---------------------------------------------------------------------------
# DPM-015: Request to add DCS aircraft configuration changes to uas library
# Description: Created a GitHub issue for DCS aircraft changes
# ---------------------------------------------------------------------------

param (
    [switch]$Debug # Use -Debug to enable verbose output
)

$Branch      = "main"

# --- CONFIGURATION ---
$ApiUrl = "https://api.github.com/repos/RadicalGoat/dcs-config-library/issues"
$RootDir    = "C:\Utils\dcs-config-manager"
$SecretFile = Join-Path $RootDir ".secrets-dcs-library-sim-config-bot"


# Load Token
$GithubToken = Get-Content -Path $SecretFile -Raw

if ([string]::IsNullOrWhiteSpace($GithubToken)) { 
    Write-Error "Token cannot be empty. Exiting."
    exit 1 
}


Write-Host "Checking for local commits..."


# if ($Debug) {
#     Write-Host "???"
#     command
#     command
# } else {
#     command *> $LogFile
#     command *>> $LogFile
# }


# Fetch latest remote state
git fetch origin $Branch

# Check for commits ahead of origin/main
$LocalCommits = git rev-list --count origin/$Branch..HEAD

if ($LocalCommits -eq 0) {
    Write-Host "No local commits to submit."
    exit 0
}

Write-Host "$LocalCommits local commit(s) detected."

# --- USER INPUT ------------------------------------------------------------

# Prompt for user's name
$UserName = Read-Host "Enter your name"

if ([string]::IsNullOrWhiteSpace($UserName)) {
    Write-Error "Name cannot be empty. Exiting."
    exit 1
}

# Prompt for one-line summary
$Summary = Read-Host "Enter a one-line summary of this configuration update"

if ([string]::IsNullOrWhiteSpace($Summary)) {
    Write-Error "Summary cannot be empty. Exiting."
    exit 1
}

# Trim and normalise
$UserName = $UserName.Trim()
$Summary  = $Summary.Trim()
# Generate patch content
$PatchBytes = git format-patch origin/$Branch --stdout | Out-String
$PatchBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($PatchBytes))

# Temporary patch output
$FilenameDateStamp = Get-Date -Format "yyyyMMdd-HHmmss"
$FilenameUserName = $UserName -replace '\s+', '_'
$PatchBase64 | Set-Content "C:\Utils\dcs-config-manager\${FileNameUserName}-${FilenameDateStamp}.patch" -NoNewline

# Build issue title
$MachineName = $env:COMPUTERNAME
$DateStamp   = Get-Date -Format "yyyy-MM-dd HH:mm"

$Title = "Config Update: $Summary ($MachineName - $DateStamp)"

# Build issue body
$Body = @"
A configuration update has been submitted.

**Submitted by:** $UserName  
**Machine:** $MachineName  
**Date:** $DateStamp

---

### Summary
$Summary

---

Number of commits: **$LocalCommits**

---

### Patch (Base64 Encoded)

To apply:

1. Copy the base64 text below to a file called patch.b64
2. Run:
   certutil -decode patch.b64 patch.patch
3. Apply:
   git am patch.patch

---

$PatchBase64

---
Generated automatically by DCS Config Sync.
"@

# Build JSON payload
$Payload = @{
    title = $Title
    body  = $Body
} | ConvertTo-Json -Depth 5

# Prepare headers
$Headers = @{
    Authorization = "Bearer $GithubToken"
    Accept        = "application/vnd.github+json"
    "User-Agent"  = "DCS-Config-Script"
}

if ($Debug) {
    Write-Host "Following items to be used to created GitHub issue:"
    Write-Host "Title: $Title"
    Write-Host "Body: $Body"
    Write-Host "Headers: $($Headers | Out-String)"
    Write-Host "Payload: $Payload"
    Write-Host "API URL: $ApiUrl"
}

Write-Host "Creating GitHub issue..."

try {
    $Response = Invoke-RestMethod -Method Post `
        -Uri $ApiUrl `
        -Headers $Headers `
        -Body $Payload `
        -ContentType "application/json"

    Write-Host "Issue created successfully:"
    Write-Host $Response.html_url
}
catch {
    Write-Error "Failed to create issue:"
    Write-Error $_
    exit 1
}