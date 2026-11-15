import bpy, sys, os, glob, numpy as np
OUT = sys.argv[sys.argv.index("--") + 1]
files = sorted(glob.glob(os.path.join(OUT, "f_*.png")))
W, H = 480, 270
for k in range(0, len(files), 9):
    chunk = files[k:k + 9]; canvas = np.zeros((H * 3, W * 3, 4), dtype=np.float32); canvas[..., 3] = 1
    for i, fp in enumerate(chunk):
        im = bpy.data.images.load(fp); w, h = im.size
        a = np.empty(w * h * 4, dtype=np.float32); im.pixels.foreach_get(a); a = a.reshape(h, w, 4)
        r, c = divmod(i, 3); y0 = (2 - r) * H; x0 = c * W
        canvas[y0:y0 + min(h, H), x0:x0 + min(w, W)] = a[:H, :W]
    out = bpy.data.images.new("sheet", W * 3, H * 3, alpha=False); out.pixels.foreach_set(canvas.ravel()); out.filepath_raw = os.path.join(OUT, "folha_%d.png" % (k // 9 + 1)); out.file_format = 'PNG'; out.save()
    print("folha", k // 9 + 1, [os.path.basename(f) for f in chunk])
