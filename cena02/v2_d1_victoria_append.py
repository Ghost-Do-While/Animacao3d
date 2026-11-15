# Anexa a Victoria (Blender Studio, CC) na cena SCN_Telejornal no lugar da ancora TJ_Ancora (que fica escondida, backup).
import bpy, math
import os
_MODELOS = os.environ.get("ANIM3D_MODELOS", os.path.join(os.path.expanduser("~"), "Downloads"))   # pasta dos .blend baixados do Blender Studio
VIC = os.path.join(_MODELOS, *"victoria.blend".split("/"))
tj = bpy.data.scenes["SCN_Telejornal"]
if "CHAR_Victoria" in bpy.data.collections: raise SystemExit("Victoria ja anexada")
with bpy.data.libraries.load(VIC, link=False) as (src, dst):
    dst.collections = ["CH-victoria"]
holder = bpy.data.collections.new("CHAR_Victoria"); tj.collection.children.link(holder)
for c in dst.collections: holder.children.link(c)
root = bpy.data.objects.new("ROOT_Victoria", None); root.empty_display_type = 'ARROWS'; root.empty_display_size = 0.5
holder.objects.link(root)
allobjs = set()
for c in dst.collections: allobjs.update(c.all_objects)
for o in allobjs:
    if o.parent is None or o.parent not in allobjs:
        o.parent = root; o.matrix_parent_inverse.identity()
# posicao da ancora antiga (500.1, 2.67); sentada: eleva a Victoria para a cabeca ficar na altura da antiga (~1.7)
root.location = (500.1, 2.67, 0.5)
root.rotation_euler = (0, 0, 2.5)    # de frente para a camera (camera em x=503, y=5.6)
for n in ("TJ_Ancora", "TJ_Ancora_Corpo", "TJ_Ancora_Cabeca", "TJ_Ancora_Cabelo"):
    o = bpy.data.objects[n]; o.hide_render = True; o.hide_viewport = True
# limite de GPU: subdivisao de render nivel 1
for o in allobjs:
    for m in o.modifiers:
        if m.type == 'SUBSURF': m.render_levels = min(m.render_levels, 1)
print("VIC_OK", len(bpy.data.objects["RIG-Victoria"].data.bones), "objs", len(allobjs))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
