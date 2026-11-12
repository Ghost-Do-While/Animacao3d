# Renderiza frames de prévia (25%) e monta uma folha de contato. Variáveis esperadas: SP (pasta), FRAMES (lista)
import bpy, os, numpy as np
sc = bpy.context.scene
old = (sc.render.resolution_percentage, sc.eevee.taa_render_samples, sc.render.filepath, sc.frame_current)
sc.render.resolution_percentage = 25; sc.eevee.taa_render_samples = 8
imgs = []
for f in FRAMES:
    sc.frame_set(f); p = os.path.join(SP, f'shot_{f:03d}.png'); sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(p); imgs.append(np.array(im.pixels[:]).reshape(im.size[1], im.size[0], 4)); bpy.data.images.remove(im)
sc.render.resolution_percentage, sc.eevee.taa_render_samples, sc.render.filepath, _f = old
sc.frame_set(_f)
h, w = imgs[0].shape[:2]; cols = 3; rows = (len(imgs) + cols - 1) // cols
sheet = np.zeros((h * rows, w * cols, 4)); sheet[..., 3] = 1
for i, a in enumerate(imgs):
    r, c = divmod(i, cols); sheet[(rows - 1 - r) * h:(rows - r) * h, c * w:(c + 1) * w] = a
img = bpy.data.images.new('sheet', w * cols, h * rows); img.pixels = sheet.ravel().tolist()
img.filepath_raw = os.path.join(SP, SHEET); img.file_format = 'PNG'; img.save(); bpy.data.images.remove(img)
