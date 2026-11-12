# Parte 0 - limpa a cena e configura projeto
sc = bpy.context.scene
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Limpa tudo (cena é reconstruída do zero a cada execução)
for o in list(D.objects): D.objects.remove(o, do_unlink=True)
for c in list(D.collections): D.collections.remove(c)
for coll_ in (D.meshes, D.materials, D.cameras, D.lights, D.curves, D.armatures, D.actions,
              D.node_groups, D.shape_keys if hasattr(D, 'shape_keys') else [], D.images):
    for b in list(coll_):
        try: coll_.remove(b)
        except Exception: pass
for s_ in list(D.scenes):
    if s_ != sc: D.scenes.remove(s_)
for tx_ in list(D.texts): D.texts.remove(tx_)
sc.timeline_markers.clear()
if sc.animation_data: sc.animation_data_clear()
random.seed(2)

COLS = {'MAQUETE_Condominio': ['Predio', 'Guarita', 'Cancelas', 'Sensores', 'Muros', 'Gradis_Postes', 'Vagas', 'Carros_Estacionados'],
        'ENV_Rua_Entorno': [], 'ENV_Apartamento': [],
        'VEHICLES_Animados': [], 'CAMERAS': [], 'LIGHTS': []}
for n, subs in COLS.items():
    c = D.collections.new(n)
    sc.collection.children.link(c)
    for s_ in subs:
        c.children.link(D.collections.new(s_))
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 1.0

# Tempo / formato
sc.render.fps = 24
sc.frame_start = 1
sc.frame_end = 720
sc.frame_current = 1
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

# Color management
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
sc.view_settings.exposure = 0.0
sc.view_settings.use_curve_mapping = False

# Engine: Eevee (Cycles pré-configurado como alternativa)
sc.render.engine = 'BLENDER_EEVEE'
ee = sc.eevee
ee.use_raytracing = True
ee.use_shadows = True
ee.shadow_ray_count = 2
ee.shadow_step_count = 6
ee.taa_render_samples = 64
ee.volumetric_tile_size = '8'
ee.volumetric_end = 120
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = 0.5
sc.render.motion_blur_position = 'START'  # evita rastro nos cortes (teleportes entre planos)
try:
    sc.cycles.samples = 128
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 6
except Exception:
    pass

# Saída
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_depth = '16'
sc.render.image_settings.color_mode = 'RGB'
sc.render.filepath = '//render/cena02/'

# World (céu de entardecer) é montado em p6_lights_comp.py
