Stable Diffusion Prompt Generator — Ollama
======================================

Purpose
-------
Small guide and smoke-test for installing a prompt-generator model into your local Ollama instance and using it to generate creative prompts for Stable Diffusion.

Quick steps
-----------
1. Choose a model identifier that Ollama can pull from a registry, or use a local model directory. Example identifiers vary by registry; replace the placeholder below with a real model id if you have one.

2. From PowerShell run (examples):

```powershell
# pull & smoke-test using the helper script
.\scripts\install_prompt_generator.ps1 -Model "prompthero/stable-diffusion-prompt-generator"

# or run directly with the Ollama CLI
# ollama pull <model-id>
# ollama run <model-id> "Generate example SD prompts"
```

Notes
-----
- The helper script will check that the `ollama` CLI is available and attempt a pull, then run a short smoke prompt. Adjust the `-Prompt` argument to tune the expected output.
- If the model is not present in your Ollama registry, the `ollama pull` step will fail; you can instead provide an alternative model name or install a local model following Ollama's docs.
- If you prefer the HTTP API, run `ollama serve` and use `POST /api/generate` with JSON specifying the model and prompt — verify the exact API schema with your Ollama version.

Integration into SD workflow
---------------------------
Once a prompt-generator model is available locally under a name you control, you can:
- Use the `ollama run <model>` CLI from your preprocessing scripts to generate prompts programmatically.
- Call the Ollama HTTP server (if running) from your app to obtain prompts before passing them to your Stable Diffusion pipeline.

If you want, I can:
- help pick a specific public prompt-generator model to pull (you can tell me which repos/registries you prefer),
- or wire the output directly into `Fooocus` preprocessing scripts so it runs automatically before a smoke generation.

Fallback: run HF model locally with transformers
-----------------------------------------------
If `ollama pull <hf-id>` fails (manifest not available), you can run the Hugging Face model locally using the included Python helper:

```powershell
# from F:\AI\Ollama
python .\scripts\run_hf_prompt_generator.py --model sambanovasystems/SambaLingo-Hungarian-Chat --prompt "Adj 6 rövid, fotórealisztikus SD promptot hegyvidéki tájról, JSON tömbként." --n 6
```

Requirements:
- Python 3.10+ recommended
- pip install transformers accelerate
- For large models (7B) you will likely need a GPU and the `bitsandbytes` package (and to start with `--device cuda`).

If you want I can also prepare a small wrapper in `F:\AI\Fooocus` that calls this script and feeds the generated prompts into your existing SD pipeline.
