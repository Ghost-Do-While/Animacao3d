# Alternativa SEM Pillow: compoe estudio + overlay usando o numpy do proprio Blender.
# Uso: blender -b --python cena02/telejornal_compor_blender.py
import bpy, os, numpy as np
ROOT = os.getcwd()
A, B, O = (os.path.join(ROOT, "render", d) for d in ("telejornal_victoria", "telejornal_ovl", "telejornal_final"))
os.makedirs(O, exist_ok=True)
def load(p):
    im = bpy.data.images.load(p); im.alpha_mode = 'STRAIGHT'; im.colorspace_settings.name = 'Non-Color'
    w, h = im.size; a = np.empty(w * h * 4, dtype=np.float32); im.pixels.foreach_get(a); return im, a.reshape(-1, 4)
for n in range(1, 104):
    fa, fb = os.path.join(A, f"tv_{n:04d}.png"), os.path.join(B, f"ov_{n:04d}.png")
    if not (os.path.exists(fa) and os.path.exists(fb)): print("falta", n); continue
    ia, a = load(fa); ib, b = load(fb)
    al = b[:, 3:4]; out = np.empty_like(a); out[:, :3] = b[:, :3] * al + a[:, :3] * (1 - al); out[:, 3] = 1.0
    w, h = ia.size; r = bpy.data.images.new("o", w, h, alpha=False); r.colorspace_settings.name = 'Non-Color'
    r.pixels.foreach_set(out.ravel()); r.filepath_raw = os.path.join(O, f"tv_{n:04d}.png"); r.file_format = 'PNG'; r.save()
    for i in (ia, ib, r): bpy.data.images.remove(i)
print("compostos 1-103")
