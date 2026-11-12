# Parte 5 - Câmeras CAM_01..CAM_10 + markers (Bind Camera to Markers) - linguagem de estúdio: lentes abertas, DOF, movimentos suaves
sc = bpy.context.scene
cC = col('CAMERAS')

def head_pos(rig, frame, up=0.12, bone='head'):
    sc.frame_set(frame)
    pb = rig.pose.bones[bone]
    return rig.matrix_world @ pb.matrix @ Vector((0, up, 0))

def camera(name, lens, loc, target=None, fstop=None, focus=None, parent=None, clip=0.05):
    cd = D.cameras.new(name)
    cd.lens = lens; cd.clip_start = clip; cd.clip_end = 500
    cd.sensor_fit = 'HORIZONTAL'; cd.sensor_width = 36
    o = D.objects.new(name, cd); link(o, cC)
    if parent: set_parent(o, parent)
    o.location = loc
    if target is not None: look_at(o, target)
    if fstop:
        cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
        if isinstance(focus, tuple): cd.dof.focus_object = focus[0]; cd.dof.focus_subtarget = focus[1]
        elif focus is not None: cd.dof.focus_distance = focus
    return o

def aim(o, name, pts):
    """Câmera que acompanha um alvo (empty) com keys suaves."""
    t = empty(name, pts[0][1], cC, 0.3)
    tt = o.constraints.new('TRACK_TO'); tt.target = t; tt.track_axis = 'TRACK_NEGATIVE_Z'; tt.up_axis = 'UP_Y'
    for f, p_ in pts: key(t, 'location', p_, f)
    return t

def handheld(o, f0, f1, strength=0.012, scale=7.0):
    for p in ('rotation_euler', 'location'):
        key(o, p, None, f0); key(o, p, None, f1)
    for i in range(3): noise_mod(o, 'rotation_euler', i, strength * (0.6 if i == 1 else 1.0), scale)
    for i in range(3): noise_mod(o, 'location', i, 0.006, scale * 1.5)

CAMS = {}
# 01 - plano geral alto, do outro lado da rua, 18 mm, dolly lento para a frente
c1 = camera('CAM_01', 18, (4.5, -26.0, 9.6), (0.5, -8.0, 1.2))
key(c1, 'location', None, 1, 'BEZIER'); key(c1, 'location', (3.4, -22.4, 8.6), 72)
CAMS[1] = c1
# 02 - close interno pelo para-brisa, 50 mm, f/2.0, foco no Marcos (presa ao carro); ângulo ligeiramente alto
hp = head_pos(rM, 90); hp_local = carM.matrix_world.inverted() @ hp
c2 = camera('CAM_02', 50, (-0.3, 2.5, 1.72), parent=carM, fstop=2.0, focus=(rM, 'head'))
look_at(c2, hp_local + Vector((0.04, 0, -0.1)))
key(c2, 'location', None, 73, 'BEZIER'); key(c2, 'location', (-0.34, 2.25, 1.66), 144)
CAMS[2] = c2
# 03 - plano médio lateral junto ao cobogó direito, 24 mm, acompanha o carro; sensor S2 em primeiro plano
c3 = camera('CAM_03', 24, (12.0, -5.2, 1.5), fstop=5.6, focus=8.0)
aim(c3, 'CAM_03_Alvo', [(145, (8.0, -16.0, 0.9)), (163, (ENTR_CX, -13.5, 1.0)), (176, (ENTR_CX, -9.8, 1.3)), (192, (ENTR_CX - 0.5, -7.8, 2.0)), (204, (ENTR_CX - 0.4, -3.5, 1.2))])   # a cancela C2 sobe em quadro
CAMS[3] = c3
# 04 - plano geral do estacionamento, ângulo baixo, 28 mm, dolly acompanhando o carro até a vaga V6; termina olhando o vão entre V5 e V6
c4 = camera('CAM_04', 28, (1.2, -1.0, 0.85), fstop=5.6, focus=9.0)
key(c4, 'location', None, 205, 'BEZIER'); key(c4, 'location', (1.4, 3.0, 0.9), 224); key(c4, 'location', (2.2, 6.0, 0.95), 240); key(c4, 'location', (3.6, 7.4, 1.05), 252)
aim(c4, 'CAM_04_Alvo', [(205, (AISLE_X, 4.0, 1.0)), (232, (2.4, 11.0, 1.1)), (252, (-2.9, 10.4, 1.25))])
CAMS[4] = c4
# 05 - over-the-shoulder do Marcos, 35 mm, olhando a briga ao fundo
sc.frame_set(270)
hm5 = head_pos(rM, 270)
fwd = Vector((MIGUEL_POS[0] - 3.4, MIGUEL_POS[1] - 9.4, 0)).normalized(); rgt = Vector((fwd.y, -fwd.x, 0))
mid = Vector((MIGUEL_POS[0], (MIGUEL_POS[1] + CLAUDIO_POS[1]) / 2, 1.25))
CAMS[5] = camera('CAM_05', 35, hm5 - fwd * 0.8 + rgt * 0.33 + Vector((0, 0, 0.08)), mid, fstop=2.8, focus=(rG, 'head'))
# 06 - plano médio do Miguel (ângulo baixo, peso cômico), câmera na mão muito leve; V1/V2 ao fundo
hg = head_pos(rG, 330)
c6 = camera('CAM_06', 32, (7.2, 3.4, 0.95), hg + Vector((0, 0, -0.25)), fstop=2.8, focus=(rG, 'head'))
handheld(c6, 289, 396)
CAMS[6] = c6
# 07 - contraplano do Claudio (ângulo baixo), câmera na mão
hc = head_pos(rC, 440)
c7 = camera('CAM_07', 30, (10.5, 9.7, 0.95), hc + Vector((0, 0, -0.2)), fstop=2.0, focus=(rC, 'head'))
handheld(c7, 397, 492)
CAMS[7] = c7
# 08 - corte seco: plano geral da sala, 24 mm
CAMS[8] = camera('CAM_08', 24, AZ(-9.2, 0.3, 1.75), AZ(-13.6, 4.0, 0.95), fstop=8.0, focus=5.0)
# 09 - push-in lento na tela da TV, 50 mm
TVC = AZ(-15.38, 2.2, 1.35)
c9 = camera('CAM_09', 50, AZ(-11.6, 1.4, 1.15), TVC, fstop=4.0, focus=4.2)
key(c9, 'location', None, 541, 'BEZIER'); key(c9, 'location', AZ(-12.7, 1.65, 1.2), 600)
CAMS[9] = c9
# 10 - close frontal de Marcos no sofá, 85 mm, DOF raso (janela com bokeh atrás); ligeiramente alto: ele está derrotado
hm = head_pos(rM, 660)
CAMS[10] = camera('CAM_10', 85, hm + Vector((-2.4, 0.06, 0.22)), hm + Vector((0, 0, -0.04)), fstop=1.4, focus=(rM, 'head'))
key(CAMS[10], 'location', None, 601, 'BEZIER'); key(CAMS[10], 'location', hm + Vector((-2.2, 0.05, 0.2)), 720)

SHOT_START = [1, 73, 145, 205, 253, 289, 397, 493, 541, 601]
for i, f in enumerate(SHOT_START):
    mk = sc.timeline_markers.new(f'P{i+1:02d}', frame=f)
    mk.camera = CAMS[i + 1]
sc.camera = CAMS[1]
sc.frame_set(1)
