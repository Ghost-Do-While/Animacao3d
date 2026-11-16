import bpy, sys, json
a = sys.argv[sys.argv.index("--") + 1:]
sc = bpy.context.scene; snow = bpy.data.objects["RIG-Snow"]
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith("GEO-"): o.hide_viewport = True
for f in [int(x) for x in a]:
    sc.frame_set(f); bpy.context.view_layer.update(); pb = snow.pose.bones
    w = lambda n: snow.matrix_world @ pb[n].head
    head = w("DEF-Eye.L").lerp(w("DEF-Eye.R"), 0.5); t = w("TGT-Eyes")
    d = t - head
    em = pb["DEF-Eye.R"].matrix.to_3x3()
    print("MED", f, "alvo-rel-olhos", [round(x, 2) for x in d], "dist", round(d.length, 2), "TGT rot", [round(x, 2) for x in pb["TGT-Eyes"].rotation_euler], "eyeR_Y", [round(x, 2) for x in (snow.matrix_world.to_3x3() @ em.col[1])])
