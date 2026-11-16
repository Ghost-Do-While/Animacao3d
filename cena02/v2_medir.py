# Medicoes de diagnostico (nao altera o arquivo). Uso: blender -b cena02_v2.blend -S Scene --python cena02/v2_medir.py -- saida.json frame [frame ...]
import bpy, sys, json
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
out, frames = a[0], [int(x) for x in a[1:]]
sc = bpy.context.scene
snow = bpy.data.objects["RIG-Snow"]
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith("GEO-"): o.hide_viewport = True
res = {}
car = bpy.data.objects.get("VEH_CarroMarcos")
for f in frames:
    sc.frame_set(f); bpy.context.view_layer.update()
    d = {}
    pb = snow.pose.bones
    for n in ("DEF-Thigh.L", "DEF-Shin.L", "DEF-Foot.L", "DEF-Thigh.R", "DEF-Foot.R", "DEF-Wrist.L", "DEF-Wrist.R", "FK-Head", "FK-Foot.L", "FK-Knee.L"):
        if n in pb:
            d[n] = [round(x, 3) for x in (snow.matrix_world @ pb[n].head)]
            d[n + "_tail"] = [round(x, 3) for x in (snow.matrix_world @ pb[n].tail)]
    if car:
        d["car_loc"] = [round(x, 3) for x in car.matrix_world.translation]
    rm = bpy.data.objects["RIG_Marcos"]
    d["RIG_Marcos"] = [round(x, 3) for x in rm.matrix_world.translation]
    d["RIG_Marcos_yaw_deg"] = round(rm.rotation_euler[2] * 57.2958, 1)
    d["RIG-Snow_world"] = [round(x, 3) for x in snow.matrix_world.translation]
    res[f] = d
car_parts = {}
for o in bpy.data.objects:
    if o.name.startswith("VEH_CarroMarcos") and o.type == 'MESH':
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        car_parts[o.name] = [round(min(v.z for v in bb), 3), round(max(v.z for v in bb), 3)]
res["car_parts_zrange"] = car_parts
json.dump(res, open(out, "w"), indent=1)
print("MEDIR_OK")
