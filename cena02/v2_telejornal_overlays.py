# CORRECAO (frame 568 da cena principal): os graficos do jornal (tarja, URGENTE, manchete, AO VIVO, relogio, ticker, logo) eram objetos 3D presos
# a camera a 2 m e a bancada/ancora ENTRAVAM neles (o ticker e a tarja ficavam cortados por dentro da mesa). Agora ficam numa cena propria
# (SCN_Telejornal_Ovl, camera fixa SEM desfoque, fundo transparente) e sao compostos POR CIMA de tudo (cena/telejornal_compor.py).
# Uso: blender -b cena02_v2.blend -S SCN_Telejornal --python cena02/v2_telejornal_overlays.py
import bpy
D = bpy.data
NS = D.scenes["SCN_Telejornal"]
assert bpy.context.scene.name == "SCN_Telejornal"
if "SCN_Telejornal_Ovl" in D.scenes:
    print("OVL ja existe")
    # correcao: a etiqueta URGENTE (e seu texto) ficava na mesma profundidade da tarja vermelha (z-fighting): aproxima 4 mm da camera
    for nm in ("TJ_G_Urgente", "TJ_G_UrgenteTxt"):
        o = D.objects[nm]; a = o.animation_data.action
        for fc in (a.fcurves if hasattr(a, "fcurves") else [fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]):
            if fc.data_path == "location" and fc.array_index == 2:
                for kp in fc.keyframe_points: kp.co[1] += 0.004; kp.handle_left[1] += 0.004; kp.handle_right[1] += 0.004
        o.location.z += 0.004
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    raise SystemExit
ov = D.scenes.new("SCN_Telejornal_Ovl")
ov.frame_start, ov.frame_end = NS.frame_start, NS.frame_end
r = ov.render
r.engine = NS.render.engine; r.resolution_x, r.resolution_y, r.resolution_percentage = NS.render.resolution_x, NS.render.resolution_y, 100
r.fps = NS.render.fps; r.film_transparent = True; r.use_motion_blur = False
r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'; r.image_settings.color_depth = '8'
r.filepath = '//render/telejornal_ovl/ov_'
ov.eevee.taa_render_samples = 24
ov.view_settings.view_transform = NS.view_settings.view_transform; ov.view_settings.look = NS.view_settings.look
w = D.worlds.new("TJ_Ovl_World"); w.use_nodes = True
for n in w.node_tree.nodes:
    if n.type == 'BACKGROUND': n.inputs['Strength'].default_value = 0.0
ov.world = w

cd = D.cameras.new("CAM_TV_Ovl"); cd.lens = 35; cd.sensor_width = 36; cd.clip_start = 0.05; cd.dof.use_dof = False
cam = D.objects.new("CAM_TV_Ovl", cd); coll = D.collections.new("TJ_Overlay"); ov.collection.children.link(coll); coll.objects.link(cam)
ov.camera = cam
n = 0
for o in list(D.objects):
    if o.name.startswith("TJ_G_"):
        for c in list(o.users_collection): c.objects.unlink(o)
        coll.objects.link(o); o.parent = cam; o.matrix_parent_inverse.identity(); n += 1
print("OVL objetos movidos:", n)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
