# Anexa o Rex (Blender Studio, CC) no lugar do Claudio. Claudio antigo fica escondido (backup).
import bpy, math
import os
_MODELOS = os.environ.get("ANIM3D_MODELOS", os.path.join(os.path.expanduser("~"), "Downloads"))   # pasta dos .blend baixados do Blender Studio
REX = os.path.join(_MODELOS, *"rex_packed.blend".split("/"))
CLAUDIO_POS = (10.0, 5.84, 0.0)
if "CHAR_Rex" in bpy.data.collections: raise SystemExit("Rex ja anexado")
with bpy.data.libraries.load(REX, link=False) as (src, dst):
    dst.collections = ["CH-rex"]
sc = bpy.context.scene
holder = bpy.data.collections.new("CHAR_Rex"); sc.collection.children.link(holder)
for c in dst.collections: holder.children.link(c)
root = bpy.data.objects.new("ROOT_Rex", None); root.empty_display_type = 'ARROWS'; root.empty_display_size = 0.5
holder.objects.link(root)
allobjs = set()
for c in dst.collections: allobjs.update(c.all_objects)
for o in allobjs:
    if o.parent is None or o.parent not in allobjs:
        o.parent = root; o.matrix_parent_inverse.identity()
root.location = CLAUDIO_POS
root.rotation_euler = (0, 0, math.pi)   # Claudio antigo: rot Z = 3.14 (de frente para o Miguel, +Y)
old = bpy.data.collections.get("CHAR_Claudio")
if old: old.hide_viewport = True; old.hide_render = True
rig = bpy.data.objects["RIG-rex"]
print("REX_OK", len(rig.data.bones), "objs", len(allobjs), "rig in", [c.name for c in rig.users_collection])
for c in dst.collections[0].children_recursive:
    print("REX_COLL", c.name, "hide_vp", c.hide_viewport, "hide_r", c.hide_render, len(c.objects))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
