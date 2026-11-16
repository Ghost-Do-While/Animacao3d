import bpy, sys, json
a = sys.argv[sys.argv.index("--") + 1:]
out, frames = a[0], [int(x) for x in a[1:]]
sc = bpy.context.scene; snow = bpy.data.objects["RIG-Snow"]
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith("GEO-"): o.hide_viewport = True
res = {}
eyeb = [b.name for b in snow.pose.bones if 'eye' in b.name.lower()]
res['eye_bones'] = eyeb
for f in frames:
    sc.frame_set(f); bpy.context.view_layer.update(); d = {}
    for n in eyeb:
        b = snow.pose.bones[n]
        d[n] = {"loc": [round(x, 3) for x in b.location], "rot": [round(x, 3) for x in b.rotation_euler], "scl": [round(x, 3) for x in b.scale], "world_head": [round(x, 3) for x in (snow.matrix_world @ b.head)]}
    res[f] = d
json.dump(res, open(out, "w"), indent=1, default=str)
