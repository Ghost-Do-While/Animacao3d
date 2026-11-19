# Mata o Blender se ficar 6 min sem gerar frame novo; render_telejornal.py refaz o lote sozinho.
$dir = Join-Path $PSScriptRoot "..\render\telejornal_victoria"
while ((Get-Date).Hour -lt 12) {
  Start-Sleep -Seconds 30
  $b = Get-Process blender -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -eq 0 } | Select-Object -First 1
  if (-not $b) { continue }
  $last = (Get-ChildItem $dir -Filter "tv_*.png" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
  $ref = if ($last -gt $b.StartTime) { $last } else { $b.StartTime }
  if (((Get-Date) - $ref).TotalMinutes -gt 6) {
    Add-Content (Join-Path $dir "render_log.txt") ("[{0}] vigia: travado ha 6 min, reiniciando o lote" -f (Get-Date -Format HH:mm:ss))
    Stop-Process -Id $b.Id -Force
  }
}
