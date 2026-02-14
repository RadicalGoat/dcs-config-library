<#
.SYNOPSIS
    Initializes the DCS Unified Repository folder structure.
#>

$RepoStructure = @(
    "tools/dcs-config-mapper",
    "data/fingerprints",
    "data/templates",
    "data/options",
    "data/scripts",
    "data/kneeboards",
    "content/liveries",
    "content/missions",
    "docs"
)

Write-Host "--- Initializing DCS Unified Repository ---" -ForegroundColor Cyan
$rootPath = (Get-Item .).FullName
Write-Host "Root: $rootPath`n" -ForegroundColor Gray

foreach ($path in $RepoStructure) {
    if (-not (Test-Path $path)) {
        New-Item -Path $path -ItemType Directory | Out-Null
        Write-Host "  [CREATED]  " -NoNewline -ForegroundColor Green
        Write-Host "$path"
    } else {
        Write-Host "  [EXISTS]   " -NoNewline -ForegroundColor Yellow
        Write-Host "$path"
    }
}

Write-Host "`n--- Repository Structure Confirmation ---" -ForegroundColor Cyan

# Using standard ASCII characters to avoid encoding issues
Get-ChildItem -Path . -Recurse -Directory | Where-Object { $_.FullName -notmatch ".git" } | ForEach-Object {
    $relative = $_.FullName.Replace($rootPath, "").TrimStart('\')
    if ($relative) {
        $level = ($relative.ToCharArray() | Where-Object { $_ -eq '\' -or $_ -eq '/' }).Count
        $indent = "  " * $level
        Write-Host "$indent+-- $($_.Name)" -ForegroundColor Gray
    }
}

Write-Host "`nInitialization Complete." -ForegroundColor Cyan