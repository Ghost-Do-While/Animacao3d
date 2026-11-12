# Vigia: se nenhum frame novo surgir em 10 min, encerra o Blender do render (o laço de render retoma).
$dir = Join-Path $PSScriptRoot '..\render\previa'
$mp4 = Join-Path $PSScriptRoot '..\render\cena02_previa.mp4'
while (-not (Test-Path $mp4)) {
    Start-Sleep -Seconds 60
    $last = Get-ChildItem $dir -Filter *.png | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($last -and ((Get-Date) - $last.LastWriteTime).TotalMinutes -gt 10) {
        $p = Get-CimInstance Win32_Process -Filter "Name='blender.exe'" | Where-Object { $_.CommandLine -like '*render_preview*' }
        foreach ($x in $p) { Stop-Process -Id $x.ProcessId -Force; "$(Get-Date -f HH:mm) travou em $($last.Name); reiniciado" }
    }
}
"MP4 pronto"
