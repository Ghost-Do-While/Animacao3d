import bpy
sc = bpy.context.scene; r = bpy.data.objects["RIG-Victoria"]; pb = r.pose.bones; W = r.matrix_world
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith("GEO-"): o.hide_viewport = True
sc.frame_set(1); bpy.context.view_layer.update()
j = pb["Jaw"]
print("JAWBONE", j.rotation_mode, [round(x, 3) for x in j.location], "lock", tuple(j.lock_rotation), tuple(j.lock_location), "len", round(j.length, 3), "parent", j.parent.name if j.parent else None)
base = (W @ pb["DEF-Jaw"].tail).copy()
for ax in (0, 1, 2):
    for ang in (-0.3, 0.3):
        j.rotation_euler = (0, 0, 0); e = [0, 0, 0]; e[ax] = ang; j.rotation_euler = e
        bpy.context.view_layer.update(); t = W @ pb["DEF-Jaw"].tail
        print("JAWT", ax, ang, [round(x, 3) for x in (t - base)])
j.rotation_euler = (0, 0, 0)
print("PRPT", {n: list(pb[n].keys()) for n in ("PRP-Thigh.L", "PRP-Head", "PRP-Spine")})
print("IKK", [b.name for b in pb if b.name.startswith(("IK-Knee", "IK-Foot", "IK-Thigh", "FK-Hips", "Hips", "Torso", "CTR-Hips", "ROOT"))])
