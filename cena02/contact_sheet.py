# Folha de contato do filme: renderiza frames de teste (25% de resolucao, 1 por processo) e monta folhas de 3x3.
# Uso: python -u cena02/contact_sheet.py        (saida: render/folha_contato/f_####.png e folha_1..3.png)
import subprocess, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUT = os.path.join(ROOT, "render", "folha_contato"); os.makedirs(OUT, exist_ok=True)
FRAMES = [1, 36, 80, 110, 150, 190, 225, 249, 262, 300, 345, 395, 430, 470, 495, 503, 510, 520, 530, 545, 580, 620, 660, 700, 720]
MARK = [(1, "CAM_01"), (73, "CAM_02"), (145, "CAM_03"), (205, "CAM_04"), (253, "CAM_05"), (289, "CAM_06"), (397, "CAM_07"), (493, "CAM_08"), (541, "CAM_09"), (601, "CAM_10")]
def cam(f): return [c for a, c in MARK if a <= f][-1]
for f in FRAMES:
    dst = os.path.join(OUT, "f_%04d_%s.png" % (f, cam(f)))
    if os.path.exists(dst) and os.path.getsize(dst) > 20000: continue
    subprocess.run([B, "-b", os.path.join(ROOT, "cena02_v2.blend"), "-S", "Scene", "--python", os.path.join(ROOT, "cena02", "v2_render_frames.py"), "--", OUT, "25", "%d:%s" % (f, cam(f))],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=900)
    src = os.path.join(OUT, "f%04d_%s.png" % (f, cam(f)))
    if os.path.exists(src): os.replace(src, dst)
    print("frame", f, cam(f), "ok" if os.path.exists(dst) else "FALHOU", flush=True)
# monta as folhas (3x3) com o proprio Blender (sem PIL)
subprocess.run([B, "-b", "--python", os.path.join(ROOT, "cena02", "contact_montage.py"), "--", OUT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("FIM", flush=True)
