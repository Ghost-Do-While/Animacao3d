import bpy, math
sc = bpy.context.scene; r = bpy.data.objects["RIG-Vincent"]; pb = r.pose.bones
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith("GEO-"): o.hide_viewport = True
sc.frame_set(382); bpy.context.view_layer.update()
W = r.matrix_world
def tip(fg): return W @ pb[f"fing_{fg}_4_L"].tail
def d(fg): return round((tip(fg) - W @ pb["hand_fk_L"].head).length, 3)
names = [b.name for b in pb if b.name.endswith("_L") and ("thumb" in b.name.lower() or "pulg" in b.name.lower()) and "bbone" not in b.name][:12]
print("POL", names)
print("BASE", {fg: d(fg) for fg in ("ind", "mid", "ring", "lit")})
for ang in (0.5, 1.0):
    for fg in ("ind", "mid", "ring", "lit"):
        for j in (2, 3, 4): pb[f"fing_{fg}_{j}_L"].rotation_euler = (0, 0, 0)
        for j in (2, 3, 4): pb[f"fing_{fg}_{j}_L"].rotation_euler[0] = ang
    bpy.context.view_layer.update(); print("CURL", ang, {fg: d(fg) for fg in ("ind", "mid", "ring", "lit")})
    for fg in ("ind", "mid", "ring", "lit"):
        for j in (2, 3, 4): pb[f"fing_{fg}_{j}_L"].rotation_euler = (0, 0, 0)
for fg in ("ind", "mid", "ring", "lit"):
    print("MODE", fg, [pb[f"fing_{fg}_{j}_L"].rotation_mode for j in (2, 3, 4)], [pb[f"fing_{fg}_{j}_L"].lock_rotation[:] for j in (2,)])
