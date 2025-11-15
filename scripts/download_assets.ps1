<#
Ollama restore helper: copy the .ollama folder from D:\Backup\Ollama\.ollama to the target F:\AI\Ollama\.ollama if missing.
This is a restore helper; do NOT put .ollama under version control.
#>

$repoRoot = (git rev-parse --show-toplevel) -replace "\\$", ""
Write-Host "Repo root: $repoRoot"

$target = Join-Path $repoRoot '.ollama'
$backup = 'D:\Backup\Ollama\.ollama'

if (Test-Path $target) { Write-Host ".ollama already exists at $target"; exit 0 }
if (-not (Test-Path $backup)) { Write-Warning "Backup not found at $backup. If the .ollama data is online, you can re-download models with the Ollama CLI after installing."; exit 2 }

Write-Host "Restoring .ollama from backup: copying $backup -> $target"
robocopy $backup $target /MIR /COPYALL /R:2 /W:5

Write-Host "Done. If you installed the data elsewhere, adjust the script accordingly."
