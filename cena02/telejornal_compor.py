# Compoe os graficos do jornal POR CIMA do estudio: estudio (render/telejornal_victoria/tv_####.png) + overlay RGBA (render/telejornal_ovl/ov_####.png)
# -> render/telejornal_final/tv_####.png (a textura da TV do apartamento usa estes arquivos depois de copiados para render/telejornal/).
# Uso: python cena02/telejornal_compor.py [primeiro ultimo]
import os, sys
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "render", "telejornal_victoria"); B = os.path.join(ROOT, "render", "telejornal_ovl"); O = os.path.join(ROOT, "render", "telejornal_final")
os.makedirs(O, exist_ok=True)
a, b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (1, 103)
for n in range(a, b + 1):
    fa, fb = os.path.join(A, f"tv_{n:04d}.png"), os.path.join(B, f"ov_{n:04d}.png")
    if not (os.path.exists(fa) and os.path.exists(fb)): print("falta", n); continue
    base = Image.open(fa).convert("RGBA"); top = Image.open(fb).convert("RGBA")
    Image.alpha_composite(base, top).convert("RGB").save(os.path.join(O, f"tv_{n:04d}.png"))
print("compostos", a, "-", b)
