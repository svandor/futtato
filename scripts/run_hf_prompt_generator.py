#!/usr/bin/env python3
"""
Run a Hugging Face text-generation model to produce prompts.

Usage:
  python run_hf_prompt_generator.py --model <hf-id> --prompt "..." [--max 128] [--n 6] [--device cpu|cuda]

Notes:
- For large models prefer a GPU and install the required packages (transformers, accelerate, optionally bitsandbytes).
- This script tries to load models with device_map='auto' and will fall back to CPU if GPU not available.
"""
import argparse
import json
import sys
import os

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="Hugging Face model id, e.g. sambanovasystems/SambaLingo-Hungarian-Chat")
    p.add_argument("--prompt", required=True, help="Instruction/prompt to send to the model")
    p.add_argument("--max", type=int, default=256, help="max new tokens")
    p.add_argument("--n", type=int, default=6, help="number of prompts to generate")
    p.add_argument("--device", choices=["cpu","cuda"], default=None, help="Force device")
    p.add_argument("--quantize", action='store_true', help="Hint to attempt quantized model loading (8-bit/4-bit) when available")
    return p.parse_args()

def main():
    args = parse_args()

    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    except Exception as e:
        print("ERROR: transformers not installed. Install with: pip install transformers accelerate", file=sys.stderr)
        sys.exit(2)

    model_id = args.model
    prompt = args.prompt
    max_new_tokens = args.max
    num = args.n

    # Attempt a safe device selection
    device = None
    if args.device == "cuda":
        device = 0
    elif args.device == "cpu":
        device = -1
    else:
        # let transformers decide
        device = None

    print(f"Loading model {model_id} (this may take a while)...")
    # Honor Fooocus quantize hint via environment variable or CLI flag
    env_q = os.environ.get('FOOOCUS_HU_FORCE_QUANTIZE', '').lower() in ('1', 'true', 'yes', 'on')
    force_quantize = args.quantize or env_q
    if force_quantize:
        print('FOOOCUS_HU_FORCE_QUANTIZE is set: attempting quantized load when possible')
    # Try to load with a normal pipeline first. If GPU OOM occurs, retry using 4-bit quantization
    gen = None
    try:
        # When device is explicitly specified as CPU/CUDA, pass appropriate device index
        if device is None:
            gen = pipeline("text-generation", model=model_id)
        else:
            gen = pipeline("text-generation", model=model_id, device=device)
    except RuntimeError as e:
        # Common case: CUDA OOM. Try a quantized 4-bit load if bitsandbytes is available.
        err = str(e)
        print("Initial model load failed:", err, file=sys.stderr)
        # If the caller requested quantized models, try an 8-bit (bitsandbytes) load first
        if force_quantize:
            try:
                print('Force-quantize requested: attempting 8-bit (bitsandbytes) load...')
                import bitsandbytes as bnb  # noqa: F401
                from transformers import AutoModelForCausalLM, AutoTokenizer
                # Try a simple 8-bit load with device_map='auto'
                try:
                    model = AutoModelForCausalLM.from_pretrained(model_id, device_map='auto', load_in_8bit=True, low_cpu_mem_usage=True)
                    tok = AutoTokenizer.from_pretrained(model_id)
                    gen = pipeline("text-generation", model=model, tokenizer=tok, device=0)
                    print('8-bit load via bitsandbytes succeeded')
                except Exception as e_bnb:
                    print('8-bit load failed:', e_bnb, file=sys.stderr)
                    gen = None
            except Exception as e_bnb_imp:
                print('bitsandbytes not available or failed to import:', e_bnb_imp, file=sys.stderr)

        if gen is None and ("out of memory" in err.lower() or "cuda" in err.lower()):
            try:
                print("Retrying model load with 4-bit quantization + offload (requires bitsandbytes)...")
                from transformers import AutoModelForCausalLM, AutoTokenizer
                import torch
                # Prepare an offload folder under the repository to allow CPU/disk offloading
                repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                offload_folder = os.path.join(repo_root, 'offload')
                os.makedirs(offload_folder, exist_ok=True)

                # Try to build a BitsAndBytesConfig if available
                try:
                    from transformers import BitsAndBytesConfig
                    bnb_config = BitsAndBytesConfig(llm_int8_threshold=6.0)
                except Exception:
                    bnb_config = None

                # We'll attempt several loading configurations with increasing offload/CPU usage.
                gpu_mem_gb = None
                try:
                    gpu_mem_gb = int(torch.cuda.get_device_properties(0).total_memory / (1024**3))
                except Exception:
                    gpu_mem_gb = 6

                configs = []
                # Conservative GPU budget config (fit most on CPU/disk)
                configs.append({
                    'desc': 'quant + max_memory small GPU, large CPU',
                    'kwargs': dict(device_map='auto', low_cpu_mem_usage=True, offload_folder=offload_folder, offload_state_dict=True, max_memory={0: f"{max(2, gpu_mem_gb-1)}GB", 'cpu': '128GB'})
                })
                # Try with quantization_config if available
                if bnb_config is not None:
                    configs.insert(0, {
                        'desc': 'bnb quantization + auto device_map',
                        'kwargs': dict(device_map='auto', low_cpu_mem_usage=True, quantization_config=bnb_config, offload_folder=offload_folder, offload_state_dict=True, max_memory={0: f"{max(2, gpu_mem_gb-1)}GB", 'cpu': '128GB'})
                    })
                else:
                    configs.insert(0, {
                        'desc': 'load_in_4bit + auto device_map',
                        'kwargs': dict(device_map='auto', low_cpu_mem_usage=True, load_in_4bit=True, offload_folder=offload_folder, offload_state_dict=True, max_memory={0: f"{max(2, gpu_mem_gb-1)}GB", 'cpu': '128GB'})
                    })

                last_err = None
                for cfg in configs:
                    print('Attempting config:', cfg['desc'])
                    try:
                        model = AutoModelForCausalLM.from_pretrained(model_id, **cfg['kwargs'])
                        tok = AutoTokenizer.from_pretrained(model_id)
                        gen = pipeline("text-generation", model=model, tokenizer=tok, device=0)
                        last_err = None
                        break
                    except Exception as ex_cfg:
                        print(f"Config '{cfg['desc']}' failed:", ex_cfg, file=sys.stderr)
                        last_err = ex_cfg

                # If simple configs failed, try a more advanced strategy using accelerate to infer a device_map
                if gen is None:
                    try:
                        print('Attempting advanced device_map inference using accelerate.init_empty_weights + infer_auto_device_map...')
                        from accelerate import init_empty_weights, infer_auto_device_map
                        from transformers import AutoConfig
                        # Load config first
                        cfg = AutoConfig.from_pretrained(model_id)
                        # Build an empty model to infer device map
                        with init_empty_weights():
                            empty_model = AutoModelForCausalLM.from_config(cfg)

                        # Compute a conservative max_memory dict
                        try:
                            total_gb = int(torch.cuda.get_device_properties(0).total_memory / (1024**3))
                        except Exception:
                            total_gb = 6
                        max_mem = {0: f"{max(2, total_gb-1)}GB", 'cpu': '200GB'}

                        device_map = infer_auto_device_map(empty_model, max_memory=max_mem, no_split_module_classes=["LlamaDecoderLayer"])
                        print('Inferred device_map:', device_map)

                        # Try multiple manual device_maps with decreasing GPU layer counts.
                        n_layers = 0
                        try:
                            n_layers = len(getattr(empty_model, 'model').layers)
                        except Exception:
                            n_layers = 32

                        success = False
                        for gpu_layers in [3,2,1,0]:
                            # Build manual map
                            manual_map = {}
                            # Put embeddings on GPU if gpu_layers>0 else CPU
                            manual_map['model.embed_tokens'] = 0 if gpu_layers>0 else 'cpu'
                            for i in range(n_layers):
                                key = f'model.layers.{i}'
                                manual_map[key] = 0 if i < gpu_layers else 'cpu'
                            manual_map['model.norm'] = 'cpu'
                            manual_map['lm_head'] = 'cpu'

                            print(f'Trying manual device_map with gpu_layers={gpu_layers}:', manual_map)
                            # Build kwargs
                            load_kwargs = dict(device_map=manual_map, low_cpu_mem_usage=True, offload_folder=offload_folder, offload_state_dict=True)
                            if bnb_config is not None:
                                load_kwargs['quantization_config'] = bnb_config
                            else:
                                load_kwargs['load_in_4bit'] = True
                            # best-effort flag
                            load_kwargs['load_in_8bit_fp32_cpu_offload'] = True

                            print('Loading with kwargs keys:', list(load_kwargs.keys()))
                            try:
                                # clear cache between attempts
                                try:
                                    import torch
                                    torch.cuda.empty_cache()
                                except Exception:
                                    pass
                                model = AutoModelForCausalLM.from_pretrained(model_id, **load_kwargs)
                                tok = AutoTokenizer.from_pretrained(model_id)
                                gen = pipeline("text-generation", model=model, tokenizer=tok, device=0)
                                success = True
                                break
                            except Exception as ex_map:
                                print(f'manual_map gpu_layers={gpu_layers} failed:', ex_map, file=sys.stderr)
                                # try next gpu_layers
                                continue

                        if not success:
                            raise RuntimeError('All manual device_map attempts failed')
                        tok = AutoTokenizer.from_pretrained(model_id)
                        gen = pipeline("text-generation", model=model, tokenizer=tok, device=0)
                    except Exception as e_adv:
                        print('Advanced device_map strategy failed:', e_adv, file=sys.stderr)
                        if last_err is not None:
                            raise last_err
                        raise e_adv
            except Exception as e2:
                print("Quantized model load failed:", e2, file=sys.stderr)
                print("You may need to choose a smaller model or enable additional offloading/quantization support.", file=sys.stderr)
                sys.exit(3)
        else:
            print("Model load failed:", e, file=sys.stderr)
            print("You may need to install bitsandbytes / accelerate or choose a smaller model.", file=sys.stderr)
            sys.exit(3)
    except Exception as e:
        print("Model load failed:", e, file=sys.stderr)
        print("You may need to install bitsandbytes / accelerate or choose a smaller model.", file=sys.stderr)
        sys.exit(3)

    outputs = []
    print("Generating...")
    for i in range(num):
        try:
            out = gen(prompt, max_new_tokens=max_new_tokens, do_sample=True, top_p=0.95, temperature=0.85)
            text = out[0]["generated_text"]
            # Heuristic: remove the input prompt from the output if repeated
            if text.startswith(prompt):
                text = text[len(prompt):].strip()
            outputs.append(text)
        except Exception as e:
            print("Generation error:", e, file=sys.stderr)
            break

    # Print as JSON array
    print(json.dumps(outputs, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
