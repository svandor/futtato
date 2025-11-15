Helyi backup javaslat — Ollama

Cél: gyors, helyi biztonsági mentés készítése a fontos fájlokról anélkül, hogy modelleket vagy multi-GB blobokat verziókezelésbe kerülnének.

Alapelvek
- Ne mentse a repo a modelleket és nagy blobokat (ezeket külön tároljuk egy közös `F:\AI\Models` vagy hálózati meghajtón).
- Mentés gyakorisága: napi (fejlesztés alatt) vagy heti (stabil állapotok) másolat a kritikus konfigurációs fájlokról és script-ekről.
- Használj timestamped mentéseket és tartsd a legutóbbi N mentést.

Példa PowerShell mentőparancs (robocopy helyett egyszerű copy + zipping):

```powershell
# beállítások
$src = 'F:\AI\Ollama'
$dstRoot = 'F:\AI\Backups\Ollama'
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$dst = Join-Path $dstRoot $ts
New-Item -ItemType Directory -Path $dst -Force | Out-Null

# csak a forráskód és kis fájlok (kizárjuk a .ollama és models mappákat)
$excludes = @('.ollama','models','checkpoints','embeddings','outputs')
Get-ChildItem -Path $src -Recurse -File | Where-Object {
    foreach ($e in $excludes) { if ($_.FullName -like "*\\$e\\*") { return $false } }
    return $true
} | ForEach-Object {
    $target = Join-Path $dst ($_.FullName.Substring($src.Length).TrimStart('\'))
    $dir = Split-Path $target -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Copy-Item -Path $_.FullName -Destination $target -Force
}

# opcionális: zip az archívum
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($dst, "$dst.zip")
Write-Host "Backup completed: $dst.zip"
```

Javasolt mappastruktúra a backup root alatt
- F:\AI\Backups\Ollama\<timestamp>\ (mentett fájlok)
- F:\AI\Backups\Ollama\latest.zip (gyors elérés)

Méretezési pontosság / becslés
- A `LOCAL_BACKUP.md` melletti script használatával lekérheted a mentendő fájlok összméretét, mielőtt lefuttatnád a mentést (lásd a `du` vagy PowerShell `Measure-Object` parancsot).

Automatizálás
- Hozz létre egy időzített feladatot (Task Scheduler) vagy egy CI job-ot, ami lefuttatja a fenti scriptet.
- Tarts meg 7-14 napi mentést körforgásban, hogy helyreállítási lehetőség legyen regresszió esetén.
