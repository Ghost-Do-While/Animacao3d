# Acabamento (v2): (1) Vincent: camisa laranja mais saturada, pele e cabelo menos claros (luz de fim de tarde "lavava" as cores);
# (2) apartamento: luz de preenchimento suave so nos frames 493-540, para o Snow nao virar silhueta nos planos abertos.
# Rodar com -S Scene.
import bpy
from mathutils import Vector
def principled(name):
    m = bpy.data.materials[name]; return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
for name, col in (("vincent_shirt", (0.72, 0.13, 0.01, 1)), ("vincent_shirt.001", (0.72, 0.13, 0.01, 1)),
                  ("vincent_skin", (0.50, 0.29, 0.21, 1)), ("vincent_hair", (0.10, 0.045, 0.03, 1))):
    p = principled(name); p.inputs["Base Color"].default_value = col; p.inputs["Roughness"].default_value = 0.75
sc = bpy.context.scene
if "LGT_Apto_Fill_Snow" not in bpy.data.objects:
    ld = bpy.data.lights.new("LGT_Apto_Fill_Snow", 'AREA'); ld.energy = 110; ld.size = 3.0; ld.color = (1.0, 0.86, 0.72)
    lo = bpy.data.objects.new("LGT_Apto_Fill_Snow", ld); bpy.data.collections["LIGHTS"].objects.link(lo)
    lo.location = (-9.6, 1.4, 8.7)
    tgt = bpy.data.objects.new("LGT_Apto_Fill_Snow_Alvo", None); tgt.location = (-13.0, 4.0, 6.9); bpy.data.collections["LIGHTS"].objects.link(tgt)
    tc = lo.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    for f, hide in ((1, True), (492, True), (493, False), (540, False), (541, True), (720, True)):
        lo.hide_render = hide; lo.keyframe_insert("hide_render", frame=f)
        lo.hide_viewport = hide; lo.keyframe_insert("hide_viewport", frame=f)
    for fc in (lo.animation_data.action.fcurves if hasattr(lo.animation_data.action, "fcurves") else [fc for l in lo.animation_data.action.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
print("POLISH ok")
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
