import bpy
from mathutils import Vector
sc = bpy.context.scene
print("CENA", sc.name, sc.frame_start, sc.frame_end, "cam", sc.camera.name if sc.camera else None)
for o in sc.objects:
    if o.type in ('MESH', 'EMPTY', 'CAMERA', 'ARMATURE', 'FONT', 'CURVE') and not o.name.startswith(("GEO-victoria", "DEF", "MCH", "ORG")):
        if o.type == 'ARMATURE' or o.parent is None or o.type in ('CAMERA', 'FONT'):
            bb = ""
            if o.type == 'MESH':
                c = [o.matrix_world @ Vector(v) for v in o.bound_box]
                bb = "bbox x[%.2f,%.2f] y[%.2f,%.2f] z[%.2f,%.2f]" % (min(v.x for v in c), max(v.x for v in c), min(v.y for v in c), max(v.y for v in c), min(v.z for v in c), max(v.z for v in c))
            print("TJ", o.type, o.name, "par=", o.parent.name if o.parent else None, [round(x, 2) for x in o.matrix_world.translation], bb)
