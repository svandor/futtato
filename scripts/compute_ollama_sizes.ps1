$root='F:\AI\Ollama'
Write-Output "Size report for: $root"
Write-Output "-----------------------------------------------"
Get-ChildItem -Force $root | ForEach-Object {
    try {
        if ($_.PSIsContainer) {
            $sum=(Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            if (-not $sum) { $sum = 0 }
            $hr = '{0:N2} MB' -f ($sum/1MB)
            Write-Output ("{0,-40} {1,12}" -f $_.Name, $hr)
        } else {
            $len = (Get-Item $_.FullName).Length
            $hr = '{0:N2} KB' -f ($len/1KB)
            Write-Output ("{0,-40} {1,12}" -f $_.Name, $hr)
        }
    } catch {
        Write-Output ("{0,-40} {1,12}" -f $_.Name, 'error')
    }
}
