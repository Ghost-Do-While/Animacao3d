# Espera ate 16:50 (hora local) e PARA o render do telejornal (pipeline + Blender de fundo). Nao encosta no Blender aberto do usuario (so processos com "-b" e "SCN_Telejornal").
$alvo = Get-Date -Hour 16 -Minute 50 -Second 0
while ((Get-Date) -lt $alvo) { Start-Sleep -Seconds 20 }
# 1) o pipeline (bash + python) primeiro, para nao iniciar a proxima etapa
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'render_telejornal' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2
# 2) os Blender de fundo do estudio
Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'blender.exe' -and $_.CommandLine -match '-b ' -and $_.CommandLine -match 'SCN_Telejornal' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 3
$resta = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'render_telejornal' -or ($_.Name -eq 'blender.exe' -and $_.CommandLine -match 'SCN_Telejornal') }
"PARADO as $(Get-Date -Format HH:mm:ss); processos de render restantes: $(@($resta).Count)"
