# Limite de GPU (Radeon integrada 512 MB): subdivisao de render do Vincent/Rex no nivel MAXLV (frames pretos com niveis altos).
import bpy, os
MAXLV = int(os.environ.get("MAXLV", "1"))
for o in bpy.data.objects:
    if o.name.startswith(("GEO-rex", "GEO-vincent")):
        for m in o.modifiers:
            if m.type == 'SUBSURF':
                print("SUB", o.name, m.levels, m.render_levels, "->", min(m.render_levels, MAXLV))
                m.render_levels = min(m.render_levels, MAXLV)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
