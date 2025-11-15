<#
Creates a timestamped zip backup of the Ollama folder to D:\Backup.

Behavior:
- Copies project contents into a temporary folder while excluding large/blob directories (.ollama, models, etc.).
- Compresses the temp folder contents into D:\Backup\Ollama_YYYYMMDD_HHMMSS.zip (no extra top-level folder inside the zip).
- Cleans up the temporary folder.

Run manually or via scheduled task. Example:
  powershell -NoProfile -ExecutionPolicy Bypass -File "F:\AI\Ollama\scripts\backup_ollama.ps1"

Note: adjust $Excludes array to match any other directories you don't want backed up.
#>

param(
    [string]$Source = 'F:\AI\Ollama',
    [string]$BackupRoot = 'D:\Backup'
)

Set-StrictMode -Version Latest

function Write-Log { param($m) $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'; Write-Host "[$ts] $m" }

if (-not (Test-Path $Source)) { Write-Error "Source not found: $Source"; exit 2 }

if (-not (Test-Path $BackupRoot)) {
    New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
    Write-Log "Created backup root: $BackupRoot"
}

$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$zipName = "Ollama_$ts.zip"
$zipPath = Join-Path $BackupRoot $zipName

$temp = Join-Path $env:TEMP ("ollama_backup_$ts")
if (Test-Path $temp) { Remove-Item -Recurse -Force $temp }
New-Item -ItemType Directory -Path $temp | Out-Null

# Directories to exclude (top-level names relative to $Source)
$Excludes = @(
    '.git',
    '.ollama',
    'models',
    'checkpoints',
    'embeddings',
    '.venv',
    'venv',
    'outputs',
    'backups',
    '.playwright'
)

Write-Log "Preparing backup from $Source to $zipPath"

Write-Log "Running robocopy (this may take a while for large folders)..."
& robocopy $Source $temp /E /COPY:DAT /R:1 /W:1 /XD $Excludes | Out-Null
if ($LASTEXITCODE -ge 16) {
    Write-Log "Robocopy failed with exit code $LASTEXITCODE"
    Remove-Item -Recurse -Force $temp -ErrorAction SilentlyContinue
    exit 3
}

Write-Log "Creating zip archive: $zipPath"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

try {
    Write-Log "Attempting Compress-Archive..."
    Compress-Archive -Path (Join-Path $temp '*') -DestinationPath $zipPath -Force -ErrorAction Stop
    $usedMethod = 'Compress-Archive'
} catch {
    Write-Log "Compress-Archive failed: $($_.Exception.Message) -- falling back to system tar (if available)."
    $tar = Get-Command tar -ErrorAction SilentlyContinue
    if ($null -ne $tar) {
        Write-Log "Using tar to create zip archive (tar -a -c -f)"
        $args = @('-a','-c','-f', $zipPath, '-C', $temp, '.')
        $p = Start-Process -FilePath $tar.Source -ArgumentList $args -NoNewWindow -Wait -PassThru
        if ($p.ExitCode -eq 0) { $usedMethod = 'tar' } else { Write-Log "tar failed with exit code $($p.ExitCode)" }
    } else {
        Write-Log "No tar command found to fall back to."
    }
}

if (Test-Path $zipPath) {
    $size = (Get-Item $zipPath).Length / 1MB
    Write-Log "Backup created: $zipPath (" + ('{0:N2}' -f $size) + " MB) using method: $usedMethod"
} else {
    Write-Log "Failed to create backup zip."
}

# Clean up
Remove-Item -Recurse -Force $temp -ErrorAction SilentlyContinue
Write-Log "Temporary files cleaned up"

exit 0
