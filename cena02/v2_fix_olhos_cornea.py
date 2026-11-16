# CORRECAO (frames ~493-720, apartamento): a cornea do Snow (material snow.eyes_cornea, Refraction no Eevee) renderiza como uma mancha
# BRANCA que cobre iris e pupila. Nos planos do apartamento a cornea fica escondida no render (a iris/pupila aparecem normalmente);
# no resto do filme ela continua ligada. Rodar com -S Scene.
import bpy
objs = [o for o in bpy.data.objects if o.type == 'MESH' and any(s.material and s.material.name == "snow.eyes_cornea" for s in o.material_slots)]
assert objs, "cornea nao encontrada"
for o in objs:
    if o.animation_data and o.animation_data.action:
        o.animation_data_clear()
    for f, hide in ((1, False), (492, False), (493, True), (720, True)):
        o.hide_render = hide; o.keyframe_insert("hide_render", frame=f)
    a = o.animation_data.action
    chans = a.fcurves if hasattr(a, "fcurves") else [fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
    for fc in chans:
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    print("CORNEA", o.name)
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
