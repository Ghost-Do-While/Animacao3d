# Espera ate 12:00 (hora local) e PARA o render do telejornal (pipeline + Blender de fundo do estudio/graficos + composicao).
# Nao encosta no Blender aberto do usuario (so processos com "-b" e "SCN_Telejornal").
$alvo = Get-Date -Hour 12 -Minute 0 -Second 0
while ((Get-Date) -lt $alvo) { Start-Sleep -Seconds 20 }
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'render_telejornal|telejornal_compor' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2
Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'blender.exe' -and $_.CommandLine -match '-b ' -and $_.CommandLine -match 'SCN_Telejornal' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 3
$resta = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'render_telejornal|telejornal_compor' -or ($_.Name -eq 'blender.exe' -and $_.CommandLine -match 'SCN_Telejornal') }
"PARADO as $(Get-Date -Format HH:mm:ss); processos de render restantes: $(@($resta).Count)"
