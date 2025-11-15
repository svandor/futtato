# Non-interactive SambaLingo HF-cache cleanup (deletes matching files)
$hf = Join-Path $env:USERPROFILE '.cache\huggingface\hub'
$logdir = 'F:\AI\Ollama\logs'
if (-not (Test-Path $logdir)) { New-Item -ItemType Directory -Path $logdir | Out-Null }
$deletedLog = Join-Path $logdir 'samba_deleted.txt'
Add-Content -Path $deletedLog -Value "--- Samba cleanup run: $(Get-Date -Format o) ---"
if (-Not (Test-Path $hf)) {
    Write-Host "HF cache not found at $hf" | Tee-Object -FilePath $deletedLog -Append
    exit 2
}
$matches = Get-ChildItem -Path $hf -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match 'SambaLingo' -or $_.FullName -match 'sambanovasystems' }
if ($matches -eq $null -or $matches.Count -eq 0) {
    Write-Host "No SambaLingo files found in HF cache." | Tee-Object -FilePath $deletedLog -Append
    exit 0
}
Write-Host "Found $($matches.Count) SambaLingo-related files; deleting and logging..."
foreach ($m in $matches) {
    try {
        $p = $m.FullName
        Remove-Item -LiteralPath $p -Force -Recurse -ErrorAction Stop
        Write-Host "Deleted: $p"
        Add-Content -Path $deletedLog -Value "Deleted: $p"
    } catch {
        Write-Host "Failed to delete: $p -> $($_.Exception.Message)"
        Add-Content -Path $deletedLog -Value "Failed: $p -> $($_.Exception.Message)"
    }
}
Write-Host "Cleanup complete. Details appended to $deletedLog" | Tee-Object -FilePath $deletedLog -Append
