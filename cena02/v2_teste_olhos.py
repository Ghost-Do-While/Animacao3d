import bpy, os
sc = bpy.context.scene
out = os.path.join(os.path.dirname(bpy.data.filepath), "render", "teste4")
sc.render.resolution_percentage = 40; sc.eevee.taa_render_samples = 16
sc.frame_set(640); sc.camera = bpy.data.objects["CAM_10"]
snow = bpy.data.objects["RIG-Snow"]; P = snow.pose.bones["Properties_Character_Snow"]
eyeobjs = [(o.name, [s.material.name for s in o.material_slots if s.material]) for o in bpy.data.objects if o.name.startswith("GEO-snow") and "eye" in o.name.lower()]
print("EYEOBJS", eyeobjs)
def shot(tag):
    sc.render.filepath = os.path.join(out, tag + ".png"); bpy.ops.render.render(write_still=True); print("SHOT", tag)
P["Eye Highlight Strength"] = 0.0; shot("A_highlight0")
for n, mats in eyeobjs:
    if any("cornea" in m for m in mats): bpy.data.objects[n].hide_render = True
shot("B_sem_cornea")
