"""
Query Hugging Face for Hungarian / Hungarian-tagged models and test-download a safe smaller candidate (EleutherAI/gpt-neo-1.3B).
Saves results to F:\AI\Ollama\logs\hf_hu_models.json and test output to hf_model_test_gptneo1_3b.json
"""
import json
import time
from pathlib import Path
from huggingface_hub import HfApi
import subprocess, sys

logs = Path('F:/AI/Ollama/logs')
logs.mkdir(parents=True, exist_ok=True)
api = HfApi()

out = []
try:
    # Try filter by language tag
    models_lang = api.list_models(filter='language:hu')
    out.extend([{'modelId': m.modelId, 'pipeline_tag': m.pipeline_tag, 'tags': m.tags[:10]} for m in models_lang[:50]])
except Exception as e:
    out.append({'error': 'list_models language filter failed', 'exc': str(e)})

# Also search for 'Hungarian' in model card (best-effort)
try:
    models_search = api.list_models(filter="")
    # naive filter locally for 'Hungarian' in tags or modelId
    found = []
    for m in models_search:
        if 'hungarian' in (m.modelId or '').lower() or any('hungarian' in t.lower() for t in (m.tags or [])):
            found.append({'modelId': m.modelId, 'tags': m.tags[:10]})
        if len(found) >= 50:
            break
    out.append({'found_hungarian_like': found})
except Exception as e:
    out.append({'error_search': str(e)})

with open(logs / 'hf_hu_models.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

# Test-download / run EleutherAI/gpt-neo-1.3B (smaller)
model = 'EleutherAI/gpt-neo-1.3B'
runner = Path('F:/AI/Ollama/scripts/run_hf_prompt_generator.py')
if not runner.exists():
    print('Runner not found at', runner)
    sys.exit(2)

prompt = 'Adj 1 rövid, fotórealisztikus SD promptot hegyvidéki tájról, JSON tömbként.'
cmd = [sys.executable, str(runner), '--model', model, '--prompt', prompt, '--n', '1', '--device', 'cuda', '--max', '128']
print('Running test command:', ' '.join(cmd))
res = subprocess.run(cmd, capture_output=True, text=True)
with open(logs / 'hf_model_test_gptneo1_3b.txt', 'w', encoding='utf-8') as f:
    f.write('Returncode: %s\n' % res.returncode)
    f.write('STDOUT:\n')
    f.write(res.stdout)
    f.write('\nSTDERR:\n')
    f.write(res.stderr)

print('Done. Wrote hf_hu_models.json and hf_model_test_gptneo1_3b.txt')
