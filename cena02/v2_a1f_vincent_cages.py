# Esconde as gaiolas de deformacao do Vincent (mdef_cage) no render e no viewport (continuam avaliadas pelos modificadores).
import bpy
for o in bpy.data.objects:
    if o.name.startswith("vincent_mdef_cage") or (o.type == 'MESH' and not o.material_slots and o.name.startswith("vincent")):
        o.hide_render = True; o.hide_set(True); print("HID", o.name)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
