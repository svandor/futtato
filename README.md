# Ollama — segédscriptek és prompt-generator

Magyar
------

Ez a mappa az Ollama-hoz kapcsolódó segédscripteket és konfigurációkat tartalmazza. Célja, hogy megkönnyítse a prompt-generator modellek helyi telepítését és tesztelését, valamint integrálást biztosítson más, helyi AI munkafolyamatokkal.

Fontos megjegyzések
- A modelleket és a `.ollama/` mappát **NE** töltsd fel a repóba — ezek nagyon nagy méretűek. A `.gitignore` már kizárja a modelleket és a blobokat.

Gyors indítás
1. Nyisd meg a `F:\AI\Ollama` könyvtárat.
2. Telepítsd a függőségeket:

```powershell
pip install -r requirements.txt
```

3. Használd a segédscript-eket a `scripts/` mappából, pl:

```powershell
.\scripts\install_prompt_generator.ps1 -Model "prompthero/stable-diffusion-prompt-generator"
```

4. Smoke-test (gyors ellenőrzés)

```powershell
# Ellenőrizd az environmentet csak (ellenőrzi az 'ollama' CLI-t és a python helper-t):
.\scripts\smoke_test.ps1 -CheckOnly

# Ha van 'ollama' CLI és szeretnéd lefuttatni a modellt (ne töltsön le nagy modelleket automatikusan):
.\scripts\smoke_test.ps1 -Model "prompthero/stable-diffusion-prompt-generator" -Prompt "Adj 3 rövid SD promptot"

# Ha nincs ollama, de a python helper megvan, futtathatod a beépített HF helpert:
python .\scripts\run_hf_prompt_generator.py --model sambanovasystems/SambaLingo-Hungarian-Chat --prompt "Adj 3 rövid SD promptot" --n 3
```

Attribúció
- Továbbfejlesztve és karbantartva: Varga Sándor (svandor)

Licence
- A mappa tartalma a projekt gyökérben található `LICENSE` fájl szerint licencelt (MIT). A `LICENSE` fájl megtalálható ezen a szinten.

English
-------

This folder contains helper scripts and configuration for working with Ollama locally. It provides tools for installing and smoke-testing prompt-generator models and integrating prompt generation into local Stable Diffusion workflows.

Quick start
1. Open `F:\AI\Ollama`.
2. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

3. Run helper scripts from `scripts/`, for example:

```powershell
.\scripts\install_prompt_generator.ps1 -Model "prompthero/stable-diffusion-prompt-generator"
```

4. Smoke-test (quick environment check)

```powershell
# Check environment only (verifies 'ollama' CLI and python helper presence):
.\scripts\smoke_test.ps1 -CheckOnly

# If you have the 'ollama' CLI and want to run a model:
.\scripts\smoke_test.ps1 -Model "prompthero/stable-diffusion-prompt-generator" -Prompt "Generate 3 short SD prompts"

# Fallback using the included HF helper script if ollama is not installed:
python .\scripts\run_hf_prompt_generator.py --model sambanovasystems/SambaLingo-Hungarian-Chat --prompt "Generate 3 short SD prompts" --n 3
```

Credits
- Maintained and further developed by Varga Sándor (svandor)

License
- See `LICENSE` in the repository root (MIT).
