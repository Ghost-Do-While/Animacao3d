# Parte 5 - Câmeras CAM_01..CAM_10 + markers (Bind Camera to Markers)
sc = bpy.context.scene
cC = col('CAMERAS')

def head_pos(rig, frame, up=0.16):
    sc.frame_set(frame)
    pb = rig.pose.bones['head']
    return rig.matrix_world @ pb.matrix @ Vector((0, up, 0))

def camera(name, lens, loc, target=None, fstop=None, focus=None, parent=None, clip=0.05):
    cd = D.cameras.new(name)
    cd.lens = lens; cd.clip_start = clip; cd.clip_end = 400
    cd.sensor_fit = 'HORIZONTAL'; cd.sensor_width = 36
    o = D.objects.new(name, cd); link(o, cC)
    if parent: set_parent(o, parent)
    o.location = loc
    if target is not None: look_at(o, target)
    if fstop:
        cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
        if isinstance(focus, tuple):
            cd.dof.focus_object = focus[0]; cd.dof.focus_subtarget = focus[1]
        elif focus is not None:
            cd.dof.focus_distance = focus
    return o

def handheld(o, f0, f1, strength=0.03, scale=7.0):
    key(o, 'rotation_euler', None, f0); key(o, 'rotation_euler', None, f1)
    for i in range(3):
        noise_mod(o, 'rotation_euler', i, strength * (0.6 if i == 1 else 1.0), scale)
    key(o, 'location', None, f0); key(o, 'location', None, f1)
    for i in range(3):
        noise_mod(o, 'location', i, 0.012, scale * 1.5)

CAMS = {}
# 01 - plano geral alto da portaria, 24 mm, dolly lento para frente
c1 = camera('CAM_01', 24, (7.5, -46.0, 10.5), (0, -8, 0.5))
key(c1, 'location', None, 1, 'LINEAR'); key(c1, 'location', (6.6, -41.0, 9.6), 72)
CAMS[1] = c1
# 02 - close interno pelo para-brisa, 50 mm, f/2.0 foco no Marcos (presa ao carro)
hp = head_pos(rM, 90)
sc.frame_set(90)
hp_local = carM.matrix_world.inverted() @ hp
c2 = camera('CAM_02', 50, (-0.3, 2.35, 1.24), parent=carM, fstop=2.0, focus=(rM, 'head'))
look_at(c2, hp_local + Vector((0.05, 0, -0.1)))
key(c2, 'location', None, 73, 'LINEAR'); key(c2, 'location', (-0.34, 2.15, 1.22), 144)
CAMS[2] = c2
# 03 - plano médio lateral da cancela, pan acompanhando o carro
c3 = camera('CAM_03', 30, (6.6, 4.6, 2.2))
alvo = empty('CAM_03_Alvo', (0, -3, 1.0), cC, 0.3)
tt = c3.constraints.new('TRACK_TO'); tt.target = alvo; tt.track_axis = 'TRACK_NEGATIVE_Z'; tt.up_axis = 'UP_Y'
for f, p_ in ((145, (-0.5, -2.0, 1.1)), (160, (-0.5, -2.0, 1.1)), (176, (0, 2.6, 0.9)), (190, (0, 9.5, 0.0)), (204, (0, 15.0, -1.3))):
    key(alvo, 'location', p_, f)
CAMS[3] = c3
# 04 - plano geral da garagem, 28 mm, ângulo baixo
CAMS[4] = camera('CAM_04', 28, G(2.7, -7.6, 0.42), G(-4.5, -0.9, 1.0))
# 05 - over-the-shoulder do Marcos, 35 mm
mid = (head_pos(rG, 270) + head_pos(rC, 270)) / 2
CAMS[5] = camera('CAM_05', 35, G(-1.18, -3.3, 1.66), mid + Vector((0, 0, -0.12)), fstop=2.8, focus=(rG, 'head'))
# 06 - plano médio do Miguel, câmera na mão
hg = head_pos(rG, 330)
c6 = camera('CAM_06', 30, G(-0.8, 1.4, 1.5), hg + Vector((0, 0, -0.22)), fstop=2.8, focus=(rG, 'head'))
handheld(c6, 289, 396)
CAMS[6] = c6
# 07 - contraplano do Claudio (Miguel desfocado em primeiro plano), câmera na mão
hc = head_pos(rC, 440)
c7 = camera('CAM_07', 45, G(-3.05, 2.05, 1.62), hc + Vector((0, 0, -0.18)), fstop=2.0, focus=(rC, 'head'))
handheld(c7, 397, 492)
CAMS[7] = c7
# 08 - corte seco: plano geral da sala a partir do sofá, 24 mm
CAMS[8] = camera('CAM_08', 24, A(-2.65, -1.35, 1.42), A(1.6, -0.15, 0.95))
# 09 - push-in lento na TV, 50 mm
c9 = camera('CAM_09', 50, A(0, -0.4, 1.17), A(0, 2.37, 1.15), fstop=4.0, focus=2.8)
key(c9, 'location', None, 541, 'LINEAR'); key(c9, 'location', A(0, 1.0, 1.155), 600)
CAMS[9] = c9
# 10 - close frontal do Marcos no sofá, 85 mm, DOF raso
hm = head_pos(rM, 660)
CAMS[10] = camera('CAM_10', 85, hm + Vector((0.08, 2.35, 0.02)), hm + Vector((0, 0, -0.05)), fstop=1.4, focus=(rM, 'head'))
key(CAMS[10], 'location', None, 601, 'LINEAR'); key(CAMS[10], 'location', hm + Vector((0.07, 2.15, 0.0)), 720)

# Markers ligados às câmeras (troca de plano)
SHOT_START = [1, 73, 145, 205, 253, 289, 397, 493, 541, 601]
for i, f in enumerate(SHOT_START):
    mk = sc.timeline_markers.new(f'P{i+1:02d}', frame=f)
    mk.camera = CAMS[i + 1]
sc.camera = CAMS[1]
sc.frame_set(1)
