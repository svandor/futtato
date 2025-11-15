param(
    [string]$Model = '',
    [string]$Prompt = 'Adj 3 rövid, fotórealisztikus SD promptot hegyvidéki tájról.',
    [switch]$CheckOnly
)

function Write-Info($msg){ Write-Host "[info] $msg" -ForegroundColor Cyan }
function Write-Warn($msg){ Write-Host "[warn] $msg" -ForegroundColor Yellow }
function Write-Err($msg){ Write-Host "[error] $msg" -ForegroundColor Red }

Write-Info "Running smoke test for Ollama helper scripts"

# Check for ollama CLI
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollamaCmd) {
    Write-Info "Found 'ollama' CLI: $($ollamaCmd.Source)"
    try {
        & ollama --version
    } catch {
        Write-Warn "Unable to run 'ollama --version'"
    }

    if ($CheckOnly) { Write-Info "Check-only mode completed."; exit 0 }

    if ([string]::IsNullOrWhiteSpace($Model)) {
        Write-Warn "No model provided. Use -Model to specify a model id (eg. 'prompthero/stable-diffusion-prompt-generator')."
        Write-Info "Exiting without running model."
        exit 0
    }

    Write-Info "Running model: $Model"
    Write-Info "Prompt: $Prompt"
    try {
        & ollama run $Model $Prompt
        $rc = $LASTEXITCODE
        if ($rc -ne 0) { Write-Warn "'ollama run' returned exit code $rc" }
    } catch {
        Write-Err "Failed to run 'ollama run'. Exception: $_"
        exit 2
    }
    exit 0
}

Write-Warn "'ollama' CLI not found on PATH. Falling back to Python helper if available."

# Fallback: run included Python generator if present
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) { $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue }

if ($pythonCmd) {
    $scriptPath = Join-Path $PSScriptRoot 'run_hf_prompt_generator.py'
    if (Test-Path $scriptPath) {
        if ($CheckOnly) { Write-Info "Python available and helper script present: $scriptPath"; exit 0 }

        $useModel = if ([string]::IsNullOrWhiteSpace($Model)) { 'sambanovasystems/SambaLingo-Hungarian-Chat' } else { $Model }
        Write-Info "Running Python helper: $scriptPath --model $useModel --prompt '$Prompt' --n 3"
        try {
            & $pythonCmd $scriptPath --model $useModel --prompt $Prompt --n 3
            $rc = $LASTEXITCODE
            if ($rc -ne 0) { Write-Warn "Python helper returned exit code $rc" }
        } catch {
            Write-Err "Failed to run Python helper: $_"
            exit 3
        }
        exit 0
    } else {
        Write-Warn "Python found but helper script 'run_hf_prompt_generator.py' not present in scripts/"
    }
} else {
    Write-Warn "Python not found on PATH."
}

Write-Info "Smoke test cannot proceed automatically. Please install 'ollama' or ensure Python and the helper script are available."
Write-Info "Example commands:"
Write-Host "  .\scripts\smoke_test.ps1 -Model 'prompthero/stable-diffusion-prompt-generator' -Prompt 'Generate 3 short prompts'" -ForegroundColor Green
Write-Host "  python .\scripts\run_hf_prompt_generator.py --model sambanovasystems/SambaLingo-Hungarian-Chat --prompt 'Adj 3 rövid promptot' --n 3" -ForegroundColor Green

exit 0
