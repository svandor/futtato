#!/usr/bin/env python3
"""
Orchestrator to try many configurations of run_hf_prompt_generator.py for up to a time limit.
It runs the existing script with different flags and environment settings, logs results, and saves any successful JSON output.
"""
import subprocess
import time
import os
import shlex
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
script = repo / "scripts" / "run_hf_prompt_generator.py"
outputs = repo / "outputs"
outputs.mkdir(parents=True, exist_ok=True)
logfile = outputs / "extended_run_log.txt"

# Configurations to try (command-line args list)
configs = []
base_prompt = 'Adj 6 rövid, fotórealisztikus SD promptot hegyvidéki tájról, JSON tömbként.'
# Start with the original heavy model but allow various device choices
configs.append(["--model","sambanovasystems/SambaLingo-Hungarian-Chat","--prompt", base_prompt, "--n","6","--device","cuda","--max","128"])
# Try cuda but force cpu fallback in script by passing --device cpu
configs.append(["--model","sambanovasystems/SambaLingo-Hungarian-Chat","--prompt", base_prompt, "--n","6","--device","cpu","--max","128"])
# Try a smaller model (2.7B) as a fallback option
configs.append(["--model","EleutherAI/gpt-neo-2.7B","--prompt", base_prompt, "--n","6","--device","cuda","--max","128"])
configs.append(["--model","EleutherAI/gpt-neo-2.7B","--prompt", base_prompt, "--n","6","--device","cpu","--max","128"])

# Time limit in seconds (60 minutes)
TIME_LIMIT = 60 * 60
start = time.time()

with open(logfile, 'a', encoding='utf-8') as log:
    log.write(f"=== Extended run started: {time.ctime()}\n")
    success = False
    attempt = 0
    for cfg in configs:
        attempt += 1
        if time.time() - start > TIME_LIMIT:
            log.write('Time limit reached, stopping.\n')
            break
        cmd = ['python', str(script)] + cfg
        log.write(f"Attempt {attempt}: {' '.join(shlex.quote(x) for x in cmd)}\n")
        print(f"Running attempt {attempt}:", ' '.join(cfg))
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30*60)
            log.write('STDOUT:\n')
            log.write(proc.stdout + '\n')
            log.write('STDERR:\n')
            log.write(proc.stderr + '\n')
            if proc.returncode == 0:
                # Try to extract JSON from stdout (last lines)
                outjson = proc.stdout.strip()
                outpath = outputs / f'prompt_generator_success_{int(time.time())}.json'
                with open(outpath, 'w', encoding='utf-8') as f:
                    f.write(outjson)
                log.write(f'SUCCESS: saved output to {outpath}\n')
                print('Success, saved:', outpath)
                success = True
                break
            else:
                print('Attempt failed, see log for details')
        except subprocess.TimeoutExpired:
            log.write('Attempt timed out.\n')
            print('Attempt timed out')
        except Exception as e:
            log.write(f'Attempt raised exception: {e}\n')
            print('Exception during attempt:', e)

    if not success:
        log.write('No successful configuration found in this run.\n')
    log.write(f"=== Extended run finished: {time.ctime()}\n\n")

print('Extended orchestrator finished. See', logfile)
