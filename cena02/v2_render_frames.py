# Uso: blender -b arq.blend --python v2_render_frames.py -- OUTDIR PCT frame:CAM [frame:CAM ...]
import bpy, sys, os
a = sys.argv[sys.argv.index("--")+1:]
out, pct, items = a[0], int(a[1]), a[2:]
sc = bpy.context.scene
sc.render.resolution_percentage = pct
sc.render.image_settings.file_format = 'PNG'
sc.eevee.taa_render_samples = 16
for it in items:
    f, cam = it.split(":")
    sc.frame_set(int(f)); sc.camera = bpy.data.objects[cam]
    sc.render.filepath = os.path.join(out, f"f{int(f):04d}_{cam}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", sc.render.filepath)
