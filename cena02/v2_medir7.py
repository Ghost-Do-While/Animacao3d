import bpy, math
sc = bpy.context.scene
for o in bpy.data.objects:
    if o.name.startswith("VEH_CarroMarcos") and o.parent is None or o.name in ("VEH_CarroMarcos_Corpo", "VEH_CarroMarcos_Body"):
        print("OBJ", o.name, o.type, o.parent.name if o.parent else None, o.animation_data.action.name if o.animation_data and o.animation_data.action else None)
print("OBJS", [o.name for o in bpy.data.objects if o.name.startswith("VEH_CarroMarcos") and o.type == 'EMPTY'])
b = next((o for o in bpy.data.objects if o.name.startswith("VEH_CarroMarcos") and o.type == 'EMPTY' and 'orpo' in o.name), None)
print("BODY", b.name if b else None)
