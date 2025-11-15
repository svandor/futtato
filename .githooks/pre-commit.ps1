param(
    [int]$MaxMB = 5
)

$root = (& git rev-parse --show-toplevel).Trim()
$maxBytes = $MaxMB * 1MB
$errors = @()

$staged = (& git diff --cached --name-only --diff-filter=ACM) -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
foreach ($f in $staged) {
    $full = Join-Path $root $f
    if (Test-Path $full) {
        try { $len = (Get-Item $full -ErrorAction Stop).Length; if ($len -gt $maxBytes) { $errors += @{Path=$f; Bytes=$len} } } catch { }
    }
}

if ($errors.Count -gt 0) {
    Write-Host "ERROR: The following staged files exceed $MaxMB MB and will block the commit:`n" -ForegroundColor Red
    foreach ($e in $errors) { Write-Host "  $($e.Path) -> $([Math]::Round($e.Bytes/1MB,2)) MB" }
    exit 1
}

exit 0
