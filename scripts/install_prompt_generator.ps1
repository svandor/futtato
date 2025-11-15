<#
.SYNOPSIS
  Install and smoke-test a prompt-generator model into local Ollama.

.DESCRIPTION
  This script checks that the Ollama CLI/server is available, attempts to pull
  a specified model identifier with `ollama pull`, then runs a small smoke
  prompt to verify the model runs locally.

.PARAMETER Model
  The Ollama model identifier to pull/run (e.g. "prompthero/stable-diffusion-prompt-generator" or a local name).

.PARAMETER Prompt
  A test prompt to send to the model to generate example prompts.

.EXAMPLE
  .\install_prompt_generator.ps1 -Model "prompthero/stable-diffusion-prompt-generator"

#>

param(
    [string]$Model = "prompt-generator:latest",
    [string]$Prompt = "Generate 6 concise, creative photorealistic prompts for landscape photography. Include style, lighting and camera lens. Output as a JSON array of strings."
)

function Fail([string]$msg) {
    Write-Host "ERROR: $msg" -ForegroundColor Red
    exit 1
}

Write-Host "Checking for 'ollama' CLI in PATH..."
$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    Fail "The 'ollama' CLI was not found in PATH. Install Ollama or add it to PATH."
}

Write-Host "Checking Ollama daemon on 127.0.0.1:11434..."
$portTest = Test-NetConnection -ComputerName 127.0.0.1 -Port 11434 -WarningAction SilentlyContinue
if (-not $portTest.TcpTestSucceeded) {
    Write-Host "Ollama does not appear to be listening on 127.0.0.1:11434." -ForegroundColor Yellow
    Write-Host "If Ollama is installed, start it (for example: run 'ollama serve' in a separate terminal) and re-run this script."
}

Write-Host "Pulling model: $Model"
try {
    & ollama pull $Model 2>&1 | Write-Host
} catch {
    Write-Host "Warning: 'ollama pull' failed or printed messages above. If the model identifier is not in the Ollama registry, you can provide a local model directory or an alternative model id." -ForegroundColor Yellow
}

Write-Host "Running smoke test against model: $Model"
try {
    # Use the CLI run command; output may vary by model. Capture output.
    $runCmd = "ollama run $Model --prompt `"$Prompt`""
    Write-Host "Executing: $runCmd"
    $output = & ollama run $Model "$Prompt" 2>&1
    Write-Host "--- MODEL OUTPUT START ---"
    Write-Host $output
    Write-Host "--- MODEL OUTPUT END ---"
} catch {
    Write-Host "Failed to run the model. See above output for errors." -ForegroundColor Red
}

Write-Host "If the model produced output, you can integrate it into your Stable Diffusion workflow by calling the model via the Ollama CLI or via the Ollama HTTP server (if running: POST /api/generate). See README_PROMPT_GENERATOR.md for usage notes."
