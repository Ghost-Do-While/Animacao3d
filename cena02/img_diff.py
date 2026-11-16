# Compara duas imagens PNG (media da diferenca absoluta e % de pixels que mudam). Uso: blender -b --python img_diff.py -- A.png B.png
import bpy, sys, numpy as np
a, b = sys.argv[sys.argv.index("--") + 1:][:2]
def load(p):
    im = bpy.data.images.load(p); w, h = im.size; x = np.empty(w * h * 4, dtype=np.float32); im.pixels.foreach_get(x); return x.reshape(h, w, 4)[..., :3]
A, B = load(a), load(b); d = np.abs(A - B)
print("DIFF", a.split("\\")[-1].split("/")[-1], "media", round(float(d.mean()), 5), "max", round(float(d.max()), 3), "pixels>2%:", round(float((d.max(axis=2) > 0.02).mean()) * 100, 3), "%")
