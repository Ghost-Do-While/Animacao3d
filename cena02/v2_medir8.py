import bpy
sc = bpy.context.scene; r = bpy.data.objects["RIG-Snow"]; pb = r.pose.bones; W = r.matrix_world
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith("GEO-"): o.hide_viewport = True
def pos(n): return W @ pb[n].head
for f in (300, 512, 518, 560):
    sc.frame_set(f); bpy.context.view_layer.update()
    g = W.translation.z if f < 500 else 6.2
    hip = pos("FK-Thigh.L"); knee = pos("FK-Knee.L"); foot = pos("DEF-Foot.L"); ankle_ik = pos("IK-Foot.L")
    d = (foot - hip).length
    print("HP", f, "quadril-z acima do chao", round(hip.z - (6.2 if f > 500 else 0.0), 3), "dist quadril->tornozelo", round(d, 3), "soma coxa+canela", round((knee-hip).length + (foot-knee).length, 3),
          "joelho-z", round(knee.z - (6.2 if f > 500 else 0.0), 3), "cotovelo/mao-z", round(pos("DEF-Wrist.L").z - (6.2 if f > 500 else 0), 3))
