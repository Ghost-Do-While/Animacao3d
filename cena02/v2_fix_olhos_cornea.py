# CORRECAO (olhos brancos): a cornea do Snow (material snow.eyes_cornea, Refraction no Eevee) vira uma mancha BRANCA que cobre iris e pupila,
# tanto no viewport quanto no render (frames 91, 640...). A cornea fica escondida em TODO o filme (viewport e render); iris/pupila aparecem.
# Rodar com -S Scene.
import bpy
objs = [o for o in bpy.data.objects if o.type == 'MESH' and any(s.material and s.material.name == "snow.eyes_cornea" for s in o.material_slots)]
assert objs, "cornea nao encontrada"
for o in objs:
    if o.animation_data: o.animation_data_clear()
    o.hide_render = True; o.hide_viewport = True
    print("CORNEA", o.name)
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
