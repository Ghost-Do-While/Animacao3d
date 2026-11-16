import bpy
sc = bpy.context.scene; r = bpy.data.objects["RIG-Victoria"]; pb = r.pose.bones; W = r.matrix_world
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith("GEO-"): o.hide_viewport = True
sc.frame_set(1); bpy.context.view_layer.update()
def p(n): return [round(x, 3) for x in (W @ pb[n].head)]
print("VIC root", [round(x, 3) for x in W.translation], "scale", [round(x, 2) for x in W.to_scale()], "parent", r.parent.name, [round(x, 3) for x in r.parent.matrix_world.translation], "rot", [round(x, 3) for x in r.parent.rotation_euler])
for n in ("FK-Thigh.L", "FK-Knee.L", "FK-Foot.L", "FK-Spine", "FK-Chest", "FK-Neck", "FK-Head", "FK-UpperArm.L", "FK-Wrist.L", "IK-Foot.L", "TGT-Eyes"):
    if n in pb: print("VIC", n, p(n))
print("VIC props", [k for k in pb["Properties"].keys()][:30] if "Properties" in pb else [b.name for b in pb if b.name.startswith("PRP")])
print("VIC bones TGT/IK/Mouth", [b.name for b in pb if b.name.startswith(("TGT", "IK-", "Properties", "PRP"))][:30])
for o in bpy.data.objects:
    if o.name.startswith("TJ_G_") and o.parent: print("PAR", o.name, o.parent.name, [round(x, 2) for x in o.location], "inv_loc", [round(x, 2) for x in o.matrix_parent_inverse.translation])
print("ACT", r.animation_data.action.name if r.animation_data and r.animation_data.action else None)
