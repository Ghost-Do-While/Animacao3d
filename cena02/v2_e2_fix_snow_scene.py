# Corrige: o Snow foi anexado na SCN_Telejornal (cena ativa por engano). Move CHAR_Snow para a cena principal "Scene".
# Rodar SEMPRE com -S Scene:  blender -b cena02_v2.blend -S Scene --python cena02/v2_e2_fix_snow_scene.py
import bpy
main = bpy.data.scenes["Scene"]; tj = bpy.data.scenes["SCN_Telejornal"]
assert bpy.context.scene.name == "Scene", "rode com -S Scene"
h = bpy.data.collections["CHAR_Snow"]
if h.name in [c.name for c in tj.collection.children]: tj.collection.children.unlink(h)
if h.name not in [c.name for c in main.collection.children]: main.collection.children.link(h)
print("FIXSCENE Snow em", [s.name for s in bpy.data.scenes if h.name in [c.name for c in s.collection.children]])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
