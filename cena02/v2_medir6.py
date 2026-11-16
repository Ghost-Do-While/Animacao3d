import bpy
from mathutils import Vector
sc = bpy.context.scene; r = bpy.data.objects["RIG-Snow"]; k = bpy.data.objects["PRP_Chaves"]
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith("GEO-"): o.hide_viewport = True
prev = None
for f in range(505, 531):
    sc.frame_set(f); bpy.context.view_layer.update()
    p = r.matrix_world.translation.copy(); F = (r.matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
    v = (p - prev) if prev else Vector((0, 0, 0)); prev = p
    ang = ""
    if v.length > 0.02: ang = round(F.dot(v.normalized()), 2)    # 1 = anda de frente, 0 = de lado, -1 = de costas
    print("WK", f, "F", [round(x, 2) for x in F], "vel", round(v.length, 3), "frente.vel", ang, "chave", [round(x, 2) for x in k.matrix_world.translation])
