<# Install git hooks for this repo by copying .githooks/* to .git/hooks/ #>
$root = (git rev-parse --show-toplevel).Trim()
$src = Join-Path $root '.githooks'
$dst = Join-Path $root '.git\hooks'
if (-not (Test-Path $src)) { Write-Error ".githooks directory not found: $src"; exit 2 }
if (-not (Test-Path $dst)) { Write-Error ".git/hooks not found. Is this a git repo?"; exit 2 }
Get-ChildItem -Path $src -File | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination (Join-Path $dst $_.Name) -Force
    Write-Host "Installed hook: $($_.Name)"
}
Write-Host "Done."
