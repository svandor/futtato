# PowerShell helper to find and optionally remove Hugging Face cache files related to SambaLingo
# Run interactively and confirm before deletion.

$hfCache = Join-Path $env:USERPROFILE ".cache\huggingface\hub"
Write-Host "HF cache root: $hfCache"

if (-not (Test-Path $hfCache)) {
    Write-Host "Hugging Face cache directory not found at $hfCache. Exiting."; exit 1
}

Write-Host "Searching for SambaLingo files..."
$matches = Get-ChildItem -Path $hfCache -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match 'SambaLingo' }
if ($matches.Count -eq 0) {
    Write-Host "No SambaLingo files found in HF cache (no action)."
    exit 0
}

Write-Host "Found the following SambaLingo-related files:"; $matches | Select-Object -ExpandProperty FullName

$confirm = Read-Host "Remove these files? Type YES to confirm"
if ($confirm -ne 'YES') {
    Write-Host "Aborting removal. No files deleted."; exit 0
}

foreach ($f in $matches) {
    try {
        Remove-Item -Path $f.FullName -Force -Recurse
        Write-Host "Deleted: $($f.FullName)"
    } catch {
        Write-Host "Failed to delete: $($f.FullName) -> $_"
    }
}

Write-Host "Done. Please consider running `git gc` if you have git objects to clean, and empty recycle bin if needed."