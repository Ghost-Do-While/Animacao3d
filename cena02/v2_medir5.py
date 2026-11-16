import bpy, math
from mathutils import Quaternion
sc = bpy.context.scene; r = bpy.data.objects["RIG-Vincent"]
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith("GEO-"): o.hide_viewport = True
sc.frame_set(382); bpy.context.view_layer.update()
pb = r.pose.bones
def d(): return round(((r.matrix_world @ pb["fing_ind_4_L"].tail) - (r.matrix_world @ pb["hand_fk_L"].head)).length, 3)
print("HCT modos", [(n, pb[n].rotation_mode) for n in ("fing_ind_2_L", "fing_ind_3_L", "fing_ind_4_L", "fing_ind_ctrl_L")])
for n in ("fing_ind_ctrl_L", "fing_ind_2_L"):
    b = pb[n]
    for ax in ((1, 0, 0), (0, 0, 1)):
        for ang in (-0.9, 0.9):
            b.rotation_quaternion = Quaternion(ax, ang) if b.rotation_mode == 'QUATERNION' else b.rotation_quaternion
            if b.rotation_mode != 'QUATERNION': b.rotation_euler = tuple(a * ang for a in ax)
            bpy.context.view_layer.update(); print("HCT", n, ax, ang, d())
    b.rotation_quaternion = (1, 0, 0, 0); b.rotation_euler = (0, 0, 0)
print("HCT base", d())
