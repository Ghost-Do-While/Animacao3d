#!/bin/bash
# Pipeline completo do telejornal: estudio (4 h) -> graficos -> composicao -> copia para render/telejornal (usado pela TV do apartamento)
cd "$(dirname "$0")/.."
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
echo "[$(date +%T)] estudio"; python -u cena02/render_telejornal.py
echo "[$(date +%T)] graficos"; mkdir -p render/telejornal_ovl
"$B" -b cena02_v2.blend -S SCN_Telejornal_Ovl -o "$(pwd -W)/render/telejornal_ovl/ov_####" -F PNG -s 1 -e 103 -a > render/telejornal_ovl/log.txt 2>&1
echo "[$(date +%T)] composicao"; python cena02/telejornal_compor.py
n=$(ls render/telejornal_final/tv_*.png 2>/dev/null | wc -l)
if [ "$n" -eq 103 ]; then cp render/telejornal_final/tv_*.png render/telejornal/; echo "[$(date +%T)] copiado para render/telejornal (103)"; else echo "INCOMPLETO: $n/103 - nada copiado"; fi
echo "[$(date +%T)] FIM"
