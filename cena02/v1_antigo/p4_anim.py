# Parte 4 - Animação dos planos 01-10
MK = CHARS['Marcos']; MG = CHARS['Miguel']; CL = CHARS['Claudio']
rM, fM = MK['rig'], MK['face']
rG, fG = MG['rig'], MG['face']
rC, fC = CL['rig'], CL['face']
carM = CARS['Marcos']['root']

def full(rig, p):
    out = {b.name: (0, 0, 0) for b in rig.pose.bones}
    out.update(p)
    return out

def P(rig, frame, *ps, interp=None):
    pose(rig, full(rig, merge(*ps)), frame, interp)

# ---------------------------------------------------------------- biblioteca de poses
ARMS_REST = {'upper_arm.L': (0, -6, 0), 'upper_arm.R': (0, 6, 0), 'forearm.L': (-8, 0, 0), 'forearm.R': (-8, 0, 0),
             **{f'f{i}.L': (0, 18, 0) for i in range(1, 5)}, **{f'f{i}.R': (0, -18, 0) for i in range(1, 5)}}
TIRED = {'spine': (6, 0, 0), 'chest': (7, 0, 0), 'neck': (8, 0, 0), 'head': (6, 0, 0)}
SIT_LEGS = {'thigh.L': (-86, 0, -4), 'thigh.R': (-86, 0, 4), 'shin.L': (84, 0, 0), 'shin.R': (84, 0, 0), 'foot.L': (-6, 0, 0), 'foot.R': (-6, 0, 0)}
GRIP_R = {f'f{i}.R': (0, -60, 0) for i in range(1, 5)}
GRIP_L = {f'f{i}.L': (0, 60, 0) for i in range(1, 5)}
SIT_CAR = merge(SIT_LEGS, {'thigh.L': (-78, 0, -4), 'thigh.R': (-78, 0, 4), 'shin.L': (70, 0, 0), 'shin.R': (70, 0, 0),
                           'spine': (-12, 0, 0), 'chest': (-4, 0, 0), 'neck': (9, 0, 0), 'head': (7, 0, 0),
                           'upper_arm.L': (-66, 0, -10), 'upper_arm.R': (-66, 0, 10),
                           'forearm.L': (-22, 0, 0), 'forearm.R': (-22, 0, 0), 'hand.L': (8, 0, 0), 'hand.R': (8, 0, 0)},
                GRIP_R, GRIP_L)
SIT_SOFA = merge(SIT_LEGS, {'spine': (-16, 0, 0), 'chest': (-6, 0, 0), 'neck': (12, 0, 0), 'head': (10, 0, 0),
                            'upper_arm.L': (-22, -8, 0), 'upper_arm.R': (-22, 8, 0), 'forearm.L': (-48, 0, 0), 'forearm.R': (-48, 0, 0)},
                 {f'f{i}.L': (0, 25, 0) for i in range(1, 5)}, {f'f{i}.R': (0, -25, 0) for i in range(1, 5)})
CROUCH = {'thigh.L': (-55, 0, -5), 'thigh.R': (-55, 0, 5), 'shin.L': (75, 0, 0), 'shin.R': (75, 0, 0),
          'foot.L': (-20, 0, 0), 'foot.R': (-20, 0, 0), 'spine': (28, 0, 0), 'chest': (10, 0, 0), 'neck': (-10, 0, 0)}

def walk(rig, f0, f1, base, period=12, amp=24, start=1):
    f = f0; s = start
    while f <= f1:
        P(rig, f, ARMS_REST, base, {
            'thigh.L': (-amp * s, 0, 0), 'thigh.R': (amp * s, 0, 0),
            'shin.L': (12 if s > 0 else 30, 0, 0), 'shin.R': (30 if s > 0 else 12, 0, 0),
            'upper_arm.L': (amp * 0.6 * s, -6, 0), 'upper_arm.R': (-amp * 0.6 * s, 6, 0)})
        f += period // 2; s = -s

def blink(face, f, dur=6, amt=1.0):
    sk(face, 'blink', 0.0, f); sk(face, 'blink', amt, f + dur // 2); sk(face, 'blink', 0.0, f + dur)

# ================================================================ PLANO 01-03: PORTARIA
# Fila: carro 3 avança alguns centímetros; lanternas de freio piscando
for i in range(4):
    r_ = CARS[f'Fila{i+1}']['root']
    key(r_, 'location', (0, FILA_Y[i], 0), 1, 'CONSTANT' if i != 2 else None)
    br = bsdf(CARS[f'Fila{i+1}']['brake']).inputs['Emission Strength']
    f = 1; on = True
    while f < 145:
        key(br, 'default_value', 7.0 if on else 0.6, f, 'CONSTANT')
        f += random.randint(14, 30) if on else random.randint(4, 8)
        on = not on
r3 = CARS['Fila3']['root']
key(r3, 'location', (0, FILA_Y[2], 0), 28)
key(r3, 'location', (0, FILA_Y[2] + 0.45, 0), 42)
for i in range(4):  # após o corte, a fila já passou
    r_ = CARS[f'Fila{i+1}']['root']
    key(r_, 'location', None, 144, 'CONSTANT')
    key(r_, 'location', (-300, -300 - i * 8, 0), 145, 'CONSTANT')

# Carro do Marcos
brM = bsdf(CARS['Marcos']['brake']).inputs['Emission Strength']
hdM = bsdf(CARS['Marcos']['head']).inputs['Emission Strength']
key(brM, 'default_value', 7.0, 1, 'CONSTANT'); key(brM, 'default_value', 0.0, 161, 'CONSTANT')
key(hdM, 'default_value', 0.0, 1, 'CONSTANT'); key(hdM, 'default_value', 5.0, 145, 'CONSTANT')
key(hdM, 'default_value', 0.0, 233, 'CONSTANT')
carM.rotation_mode = 'XYZ'
def carkey(f, loc, rx=0, rz=0, interp=None):
    key(carM, 'location', loc, f, interp); key(carM, 'rotation_euler', (rad(rx), 0, rad(rz)), f, interp)
carkey(1, (0, MARCOS_FILA_Y, 0), interp='CONSTANT')
carkey(145, (0, -4.3, 0), interp='CONSTANT')
carkey(160, (0, -4.3, 0))
carkey(176, (0, 1.2, 0), interp='LINEAR')
carkey(184, (0, 5.6, 0), 0, interp='LINEAR')
carkey(190, (0, 10.0, -0.86), -12, interp='LINEAR')
carkey(204, (0, 17.5, -2.46), -12, interp='CONSTANT')
# Plano 04: garagem - entra e estaciona na vaga 13 (manobra curta em Z)
carkey(205, G(1.2, -12.5, 0), 0, 0)
carkey(216, G(1.2, -4.4, 0), 0, 0)
carkey(224, G(-1.5, -0.9, 0), 0, 52)
carkey(232, G(-5.45, 0.0, 0), 0, 90)
for fc in fcurves(carM):  # chegada suave na vaga
    for kp in fc.keyframe_points:
        if abs(kp.co.x - 224) < 0.01: kp.interpolation = 'BACK'; kp.easing = 'EASE_OUT'; kp.back = 0.6
# Porta do motorista: abre 0->70°, bate
dp = CARS['Marcos']['door']; dp.rotation_mode = 'XYZ'
key(dp, 'rotation_euler', (0, 0, 0), 233)
key(dp, 'rotation_euler', (0, 0, rad(-70)), 238)
key(dp, 'rotation_euler', (0, 0, rad(-70)), 242)
key(dp, 'rotation_euler', (0, 0, rad(2)), 246)
key(dp, 'rotation_euler', (0, 0, 0), 248)

# Cancela: 0° -> 85° em 18 frames, ease-out com pequeno overshoot
cp = D.objects['ENV_Portaria_Cancela_Pivo']; cp.rotation_mode = 'XYZ'
key(cp, 'rotation_euler', (0, 0, 0), 1, 'CONSTANT')
key(cp, 'rotation_euler', (0, 0, 0), 150)
key(cp, 'rotation_euler', (0, rad(-90), 0), 164)
key(cp, 'rotation_euler', (0, rad(-85), 0), 168)

# Marcos dentro do carro (Child Of no carro até sair)
co = rM.constraints.new('CHILD_OF'); co.name = 'NoCarro'; co.target = carM
co.inverse_matrix = Matrix.Identity(4); co.set_inverse_pending = False
key(co, 'influence', 1.0, 1, 'CONSTANT'); key(co, 'influence', 0.0, 236, 'CONSTANT')
root(rM, (-0.4, -0.12, -0.36), 180, 1, 'CONSTANT')
fM.data.shape_keys.key_blocks['brow_down'].value = 0
P(rM, 1, SIT_CAR, interp='CONSTANT')
sk(fM, 'brow_down', 0.4, 1); sk(fM, 'mouth_frown', 0.4, 1); sk(fM, 'brow_sad', 0.2, 1)
P(rM, 60, SIT_CAR)
# Plano 02: tamborila os dedos (ciclo de 4 frames por dedo)
P(rM, 73, SIT_CAR)
for f in range(74, 102, 16):
    for i in range(4):
        fi = f + i * 4
        pose(rM, {f'f{i+1}.R': (0, -60, 0)}, fi)
        pose(rM, {f'f{i+1}.R': (0, -8, 0)}, fi + 2)
        pose(rM, {f'f{i+1}.R': (0, -60, 0)}, fi + 4)
blink(fM, 84, 8)
# olha a fila (inclina para frente), revira os olhos, suspira e encosta a cabeça
P(rM, 102, SIT_CAR)
P(rM, 108, SIT_CAR, {'spine': (-4, 0, 0), 'chest': (4, 0, 0), 'neck': (2, 0, 0), 'head': (-6, 0, 4)})
sk(fM, 'look_up', 0.0, 108); sk(fM, 'look_up', 1.0, 113); sk(fM, 'look_up', 1.0, 117); sk(fM, 'look_up', 0.0, 122)
sk(fM, 'brow_sad', 0.2, 108); sk(fM, 'brow_sad', 0.9, 114); sk(fM, 'brow_down', 0.4, 108); sk(fM, 'brow_down', 0.0, 114)
P(rM, 116, SIT_CAR, {'spine': (-6, 0, 0), 'chest': (-2, 0, 0), 'head': (-10, 0, -3)})
sk(fM, 'sigh', 0.0, 118); sk(fM, 'sigh', 1.0, 125); sk(fM, 'sigh', 1.0, 128); sk(fM, 'sigh', 0.0, 134)
P(rM, 125, SIT_CAR, {'spine': (-10, 0, 0), 'chest': (-12, 0, 0), 'head': (-4, 0, 0)})
P(rM, 134, SIT_CAR, {'spine': (-14, 0, 0), 'chest': (-2, 0, 0), 'neck': (2, 0, 0), 'head': (2, 0, 0)})
P(rM, 144, SIT_CAR, {'spine': (-16, 0, 0), 'chest': (-6, 0, 0), 'neck': (-10, 0, 0), 'head': (-10, 0, 6)})
sk(fM, 'blink', 0.0, 134); sk(fM, 'blink', 0.55, 142)
# Plano 03: cabeça no encosto enquanto avança
P(rM, 160, SIT_CAR, {'spine': (-16, 0, 0), 'chest': (-6, 0, 0), 'neck': (-10, 0, 0), 'head': (-10, 0, 6)})
sk(fM, 'blink', 0.55, 160); sk(fM, 'blink', 0.1, 166)
P(rM, 168, SIT_CAR)
# Plano 04: sai do carro
P(rM, 228, SIT_CAR)
P(rM, 233, SIT_CAR, {'upper_arm.L': (-20, -10, 0), 'forearm.L': (-30, 0, 0), 'head': (0, 0, -25)})
key(rM, 'rotation_euler', (0, 0, rad(180)), 233)
key(rM, 'location', (-0.4, -0.12, -0.36), 233)
key(rM, 'rotation_euler', (0, 0, rad(235)), 235, 'CONSTANT')
key(rM, 'location', (-0.55, -0.15, -0.3), 235, 'CONSTANT')
P(rM, 235, SIT_CAR, {'thigh.L': (-80, 0, 30), 'thigh.R': (-80, 0, 20)}, interp='CONSTANT')
# fora do carro (mundo)
root(rM, G(-5.05, -1.35, -0.12), 0, 236)
P(rM, 236, ARMS_REST, CROUCH, {'upper_arm.R': (-30, 10, 0)})
root(rM, G(-5.0, -1.55, 0), 0, 242)
P(rM, 242, ARMS_REST, TIRED, {'upper_arm.R': (-50, 0, -20), 'forearm.R': (-20, 0, 0)})  # empurra a porta
P(rM, 246, ARMS_REST, TIRED, {'upper_arm.R': (-15, 5, 0), 'spine': (10, 0, 0)})
key(rM, 'rotation_euler', (0, 0, 0), 246)
key(rM, 'location', G(-5.0, -1.55, 0), 246)
walk(rM, 247, 252, TIRED, period=10, amp=18)
root(rM, G(-4.3, -1.95, 0), 120, 252, 'CONSTANT')
blink(fM, 239, 8)
# Plano 05: over-the-shoulder - Marcos para e arqueia as sobrancelhas
root(rM, G(-1.55, -2.45, 0), 180, 253, 'CONSTANT')
P(rM, 253, ARMS_REST, TIRED)
P(rM, 262, ARMS_REST, TIRED, {'spine': (-3, 0, 0), 'chest': (-2, 0, 0), 'head': (-4, 0, 0)})
sk(fM, 'brow_sad', 0.9, 253); sk(fM, 'brow_sad', 0.0, 260)
sk(fM, 'brow_up', 0.0, 258); sk(fM, 'brow_up', 1.0, 265); sk(fM, 'brow_up', 0.8, 288)
sk(fM, 'mouth_frown', 0.4, 258); sk(fM, 'mouth_frown', 0.0, 264)
sk(fM, 'O', 0.0, 260); sk(fM, 'O', 0.35, 266); sk(fM, 'O', 0.2, 288)
blink(fM, 276, 8)
P(rM, 288, ARMS_REST, TIRED, {'spine': (-3, 0, 0), 'chest': (-2, 0, 0), 'head': (-4, 0, 0)})

# ================================================================ BRIGA (planos 05-07)
root(rG, G(-2.3, 2.6, 0), 90, 1, 'CONSTANT')
root(rC, G(-0.25, 2.6, 0), -90, 1, 'CONSTANT')
ANG_G = merge(ARMS_REST, {'spine': (6, 0, 0), 'chest': (4, 0, 0), 'neck': (-4, 0, 0), 'head': (-6, 0, 0),
                          'upper_arm.L': (-18, -18, 0), 'upper_arm.R': (-18, 18, 0), 'forearm.L': (-40, 0, 0), 'forearm.R': (-40, 0, 0)})
POINT_R = {'f1.R': (0, 0, 0), 'f2.R': (0, -95, 0), 'f3.R': (0, -95, 0), 'f4.R': (0, -95, 0)}
FLOOR_G = merge(ANG_G, POINT_R, {'spine': (16, 0, 0), 'chest': (6, 0, 0), 'head': (16, 0, 0),
                                 'upper_arm.R': (-58, 0, 12), 'forearm.R': (-4, 0, 0), 'hand.R': (-8, 0, 0)})
AT_CL_G = merge(ANG_G, POINT_R, {'spine': (8, 0, 0), 'head': (-6, 0, 0), 'upper_arm.R': (-90, 0, 4), 'forearm.R': (0, 0, 0)})
HEAD_G = merge(ANG_G, {'spine': (-8, 0, 0), 'chest': (-4, 0, 0), 'neck': (-10, 0, 0), 'head': (-14, 0, 0),
                       'upper_arm.L': (0, -143, 0), 'forearm.L': (0, -112, 0), 'upper_arm.R': (0, 143, 0), 'forearm.R': (0, 112, 0),
                       **{f'f{i}.L': (0, 20, 0) for i in range(1, 5)}, **{f'f{i}.R': (0, -20, 0) for i in range(1, 5)}})
DEF_C = merge(ARMS_REST, {'spine': (-5, 0, 0), 'chest': (-3, 0, 0), 'head': (0, 6, 0),
                          'upper_arm.L': (-25, -12, 0), 'upper_arm.R': (-25, 12, 0), 'forearm.L': (-55, 0, 0), 'forearm.R': (-55, 0, 0)})
PREP_C = merge(DEF_C, {'upper_arm.L': (-12, -10, 0), 'upper_arm.R': (-12, 10, 0), 'forearm.L': (-115, 0, 0), 'forearm.R': (-115, 0, 0),
                       'hand.L': (70, 0, 0), 'hand.R': (70, 0, 0), 'spine': (-8, 0, 0)})
PUSH_C = merge(DEF_C, {'upper_arm.L': (-78, 0, -6), 'upper_arm.R': (-78, 0, 6), 'forearm.L': (-12, 0, 0), 'forearm.R': (-12, 0, 0),
                       'hand.L': (75, 0, 0), 'hand.R': (75, 0, 0), 'spine': (4, 0, 0), 'chest': (4, 0, 0),
                       **{f'f{i}.L': (0, 0, 0) for i in range(1, 5)}, **{f'f{i}.R': (0, 0, 0) for i in range(1, 5)}})
SHRUG_C = merge(DEF_C, {'upper_arm.L': (-8, -28, 0), 'upper_arm.R': (-8, 28, 0), 'forearm.L': (-80, 0, -25), 'forearm.R': (-80, 0, 25),
                        'hand.L': (0, 40, 0), 'hand.R': (0, -40, 0), 'chest': (-6, 0, 0), 'neck': (-6, 0, 0), 'head': (-4, 14, 0),
                        **{f'f{i}.L': (0, 0, 0) for i in range(1, 5)}, **{f'f{i}.R': (0, 0, 0) for i in range(1, 5)}})

# Fundo do plano 05: os dois já discutindo
P(rG, 1, ANG_G); P(rC, 1, DEF_C)
for f, pg, pc_ in ((253, ANG_G, DEF_C), (259, AT_CL_G, DEF_C), (266, ANG_G, PUSH_C), (272, AT_CL_G, PREP_C),
                   (279, ANG_G, PUSH_C), (286, ANG_G, DEF_C)):
    P(rG, f, pg); P(rC, f, pc_)
sk(fG, 'brow_angry', 1.0, 1); sk(fG, 'mouth_shout', 0.35, 1); sk(fG, 'nostril_flare', 0.5, 1)
sk(fC, 'brow_angry', 0.4, 1); sk(fC, 'brow_smug', 0.6, 1); sk(fC, 'mouth_smirk', 0.6, 1)
lipsync(fG, 'Mas que absurdo, sai daí agora!', 254, 270, 0.8)
lipsync(fC, 'Calma aí, rapidinho!', 272, 287, 0.8)

# Plano 06: Miguel aponta o chão, aponta Claudio, mãos na cabeça
P(rG, 289, ANG_G)
P(rG, 293, ANG_G, {'upper_arm.R': (25, 10, 0), 'forearm.R': (-60, 0, 0), 'spine': (-4, 0, 0)})  # antecipação
P(rG, 297, FLOOR_G, interp='CONSTANT')
P(rG, 299, FLOOR_G)
for i, f in enumerate(range(303, 316, 4)):
    P(rG, f, FLOOR_G, {'upper_arm.R': (-48 if i % 2 == 0 else -62, 0, 12)})
P(rG, 318, FLOOR_G)
P(rG, 321, AT_CL_G, {'upper_arm.R': (-70, 0, 4)})
P(rG, 324, AT_CL_G, interp='CONSTANT')
P(rG, 327, AT_CL_G)
for i, f in enumerate(range(331, 346, 4)):
    P(rG, f, AT_CL_G, {'upper_arm.R': (-84 if i % 2 == 0 else -96, 0, 4), 'spine': (10 if i % 2 == 0 else 6, 0, 0)})
P(rG, 348, AT_CL_G)
P(rG, 351, ANG_G, {'spine': (14, 0, 0), 'upper_arm.L': (-10, -30, 0), 'upper_arm.R': (-10, 30, 0)})  # antecipação
P(rG, 356, HEAD_G, interp='CONSTANT')
P(rG, 359, HEAD_G)
for i, f in enumerate(range(363, 397, 4)):
    P(rG, f, HEAD_G, {'head': (-14, 0, 10 if i % 2 == 0 else -10), 'spine': (-8 - (i % 2) * 3, 0, 0)})
sk(fG, 'vein_pop', 0.0, 296); sk(fG, 'vein_pop', 1.0, 304)
for i, f in enumerate(range(312, 396, 8)):
    sk(fG, 'vein_pop', 0.75 if i % 2 == 0 else 1.0, f)
    sk(fG, 'nostril_flare', 1.0 if i % 2 == 0 else 0.4, f)
sk(fG, 'mouth_shout', 0.35, 290); sk(fG, 'mouth_shout', 0.55, 300)
lipsync(fG, 'Essa vaga é minha! Eu passei o dia todo trabalhando, aí agora eu chego e você tá no meu lugar? Pelo amor de Deus!', 292, 392, 1.0)
# Claudio ao fundo do plano 06: braços cruzados de deboche
CROSS_C = merge(DEF_C, {'upper_arm.L': (-30, 0, -20), 'upper_arm.R': (-30, 0, 20), 'forearm.L': (-95, 0, -40), 'forearm.R': (-95, 0, 40)})
P(rC, 292, CROSS_C); P(rC, 392, CROSS_C, {'head': (-4, 10, 0)})

# Plano 07: Claudio empurra o ar, dá de ombros, deboche
P(rC, 397, DEF_C)
P(rC, 401, PREP_C)
P(rC, 405, PUSH_C, interp='CONSTANT'); P(rC, 408, PUSH_C)
P(rC, 413, PREP_C)
P(rC, 417, PUSH_C, interp='CONSTANT'); P(rC, 420, PUSH_C)
P(rC, 426, DEF_C)
P(rC, 431, SHRUG_C, interp='CONSTANT'); P(rC, 436, SHRUG_C)
P(rC, 444, SHRUG_C, {'head': (-4, -10, 0)})
P(rC, 450, DEF_C)
P(rC, 455, PREP_C)
P(rC, 459, PUSH_C, interp='CONSTANT'); P(rC, 463, PUSH_C)
P(rC, 470, DEF_C)
P(rC, 475, SHRUG_C, interp='CONSTANT'); P(rC, 482, SHRUG_C)
P(rC, 492, SHRUG_C, {'head': (-6, 16, 0)})
sk(fC, 'brow_smug', 1.0, 398); sk(fC, 'mouth_smirk', 0.9, 398); sk(fC, 'brow_angry', 0.0, 398)
lipsync(fC, 'Eu parei rapidinho, tava só visitando um amigo! Até parece que ficar esperando um pouco vai te matar!', 400, 486, 1.0)
sk(fC, 'mouth_shout', 0.0, 398); sk(fC, 'mouth_shout', 0.3, 404); sk(fC, 'mouth_shout', 0.3, 486); sk(fC, 'mouth_shout', 0.0, 490)
# Miguel ao fundo continua gesticulando
for i, f in enumerate(range(397, 493, 7)):
    P(rG, f, AT_CL_G if i % 2 == 0 else ANG_G, {'spine': (8 + (i % 3) * 3, 0, 0)})
lipsync(fG, 'Não, não, não! Isso é um absurdo! Tira esse carro daí!', 410, 488, 0.8)

# ================================================================ PLANO 08-10: APARTAMENTO
dpA = D.objects['ENV_Apartamento_Porta_Pivo']; dpA.rotation_mode = 'XYZ'
key(dpA, 'rotation_euler', (0, 0, 0), 1, 'CONSTANT')
key(dpA, 'rotation_euler', (0, 0, 0), 493)
key(dpA, 'rotation_euler', (0, 0, rad(82)), 500)
key(dpA, 'rotation_euler', (0, 0, rad(78)), 504)
# Marcos entra
root(rM, A(3.75, 0.62, 0), -90, 493, 'CONSTANT')
sk(fM, 'brow_up', 0.8, 492, 'CONSTANT'); sk(fM, 'brow_up', 0.0, 493, 'CONSTANT')
sk(fM, 'O', 0.2, 492, 'CONSTANT'); sk(fM, 'O', 0.0, 493, 'CONSTANT')
sk(fM, 'brow_sad', 0.0, 492, 'CONSTANT'); sk(fM, 'brow_sad', 0.7, 493, 'CONSTANT')
sk(fM, 'mouth_frown', 0.0, 492, 'CONSTANT'); sk(fM, 'mouth_frown', 0.6, 493, 'CONSTANT')
walk(rM, 493, 503, TIRED, period=10, amp=20)
root(rM, A(2.45, 0.15, 0), -90, 503)
# joga as chaves (antecipação + arco com quique)
kc = keys_.constraints.new('CHILD_OF'); kc.name = 'NaMao'; kc.target = rM; kc.subtarget = 'hand.L'
kc.inverse_matrix = Matrix.Identity(4); kc.set_inverse_pending = False
key(kc, 'influence', 1.0, 1, 'CONSTANT'); key(kc, 'influence', 0.0, 506, 'CONSTANT')
key(keys_, 'location', (0, 0.07, 0), 1, 'CONSTANT')
key(keys_, 'rotation_euler', (0, 0, 0), 1, 'CONSTANT')
P(rM, 503, ARMS_REST, TIRED, {'upper_arm.L': (25, -20, 0), 'forearm.L': (-50, 0, 0), 'spine': (2, 0, 8)})
P(rM, 506, ARMS_REST, TIRED, {'upper_arm.L': (-55, -5, 30), 'forearm.L': (-5, 0, 0), 'spine': (8, 0, -8)})
P(rM, 510, ARMS_REST, TIRED, {'upper_arm.L': (-30, -5, 15), 'forearm.L': (-15, 0, 0)})
key(keys_, 'location', A(2.35, -0.1, 1.05), 506)
key(keys_, 'location', A(2.55, -0.45, 1.12), 508)
key(keys_, 'location', A(2.7, -0.55, 0.79), 511)
key(keys_, 'location', A(2.72, -0.58, 0.83), 513)
key(keys_, 'location', A(2.74, -0.6, 0.79), 515)
key(keys_, 'rotation_euler', (0, 0, 0), 506)
key(keys_, 'rotation_euler', (rad(200), rad(40), rad(90)), 511)
key(keys_, 'rotation_euler', (rad(270), rad(10), rad(110)), 515)
# vai até o sofá, vira, antecipa e se joga (squash & stretch)
walk(rM, 510, 518, TIRED, period=8, amp=22)
root(rM, A(0.25, -1.05, 0), -59, 518)
root(rM, A(0.1, -1.15, -0.08), -180, 522, scale=(1, 1, 1))
P(rM, 522, ARMS_REST, CROUCH, {'upper_arm.L': (30, -15, 0), 'upper_arm.R': (30, 15, 0)})  # antecipação
root(rM, A(0.04, -1.55, -0.12), -180, 525, scale=(0.94, 0.94, 1.1))  # stretch
P(rM, 525, SIT_SOFA, {'spine': (-30, 0, 0), 'upper_arm.L': (-60, -40, 0), 'upper_arm.R': (-60, 40, 0), 'thigh.L': (-60, 0, -8), 'thigh.R': (-60, 0, 8)})
root(rM, A(0.0, -1.83, -0.43), -180, 527, scale=(1.1, 1.1, 0.84))  # squash
P(rM, 527, SIT_SOFA, {'spine': (-24, 0, 0), 'upper_arm.L': (-30, -35, 0), 'upper_arm.R': (-30, 35, 0)})
root(rM, A(0.0, -1.83, -0.37), -180, 531, scale=(0.97, 0.97, 1.04))
root(rM, A(0.0, -1.83, -0.37), -180, 535, scale=(1, 1, 1))
P(rM, 531, SIT_SOFA)
for nm, amt in (('ENV_Apartamento_Sofa_Assento_0', 0.8), ('ENV_Apartamento_Sofa_Assento_1', 0.55), ('ENV_Apartamento_Sofa_Assento_2', 0.8),
                ('ENV_Apartamento_Sofa_Costas_1', 0.85)):
    o_ = D.objects[nm]
    key(o_, 'scale', (1, 1, 1), 525)
    key(o_, 'scale', (1 + (1 - amt) * 0.3, 1 + (1 - amt) * 0.3, amt), 528)
    key(o_, 'scale', (0.98, 0.98, 1.06), 531)
    key(o_, 'scale', (1, 1, 1), 535)
# gravata (follow-through)
for f, a_ in ((520, 0), (525, 25), (527, -35), (530, 18), (534, -6), (538, 0)):
    pose(rM, {'tie': (a_, 0, 0)}, f)
# pega o controle e liga a TV
P(rM, 533, SIT_SOFA, {'upper_arm.R': (-15, 30, 0), 'forearm.R': (-25, 0, 0), 'head': (12, 0, -10)})
rc = remote.constraints.new('CHILD_OF'); rc.name = 'NaMao'; rc.target = rM; rc.subtarget = 'hand.R'
rc.inverse_matrix = Matrix.Identity(4); rc.set_inverse_pending = False
key(rc, 'influence', 0.0, 1, 'CONSTANT'); key(rc, 'influence', 1.0, 535, 'CONSTANT'); key(rc, 'influence', 0.0, 627, 'CONSTANT')
key(remote, 'location', A(0.62, -1.75, 0.515), 1, 'CONSTANT'); key(remote, 'rotation_euler', (0, 0, 0), 1, 'CONSTANT')
key(remote, 'location', (0, 0.06, 0.0), 535, 'CONSTANT'); key(remote, 'rotation_euler', (0, 0, 0), 535, 'CONSTANT')
key(remote, 'location', A(0.5, -1.62, 0.515), 627, 'CONSTANT'); key(remote, 'rotation_euler', (0, 0, rad(25)), 627, 'CONSTANT')
AIM = {'upper_arm.R': (-68, 0, -6), 'forearm.R': (-12, 0, 0), 'hand.R': (-5, 0, 0), **GRIP_R, 'head': (6, 0, 0)}
P(rM, 538, SIT_SOFA, AIM)
P(rM, 540, SIT_SOFA, AIM)
blink(fM, 531, 8)
# Plano 09
HOLD = {'upper_arm.R': (-28, 10, 0), 'forearm.R': (-55, 0, 0), **GRIP_R}
P(rM, 552, SIT_SOFA, HOLD)
P(rM, 600, SIT_SOFA, HOLD, {'spine': (-18, 0, 0), 'head': (12, 0, 0)})
blink(fM, 566, 10); blink(fM, 590, 10)
# Plano 10: desliga a TV, solta o controle, fecha os olhos, suspira, cabeça pende
P(rM, 603, SIT_SOFA, HOLD, {'spine': (-18, 0, 0), 'head': (12, 0, 0)})
P(rM, 610, SIT_SOFA, AIM, {'spine': (-15, 0, 0)})
P(rM, 614, SIT_SOFA, AIM, {'spine': (-15, 0, 0), 'hand.R': (-12, 0, 0)})
blink(fM, 616, 10)
P(rM, 620, SIT_SOFA, AIM, {'spine': (-15, 0, 0)})
P(rM, 628, SIT_SOFA, {'upper_arm.R': (-12, 18, 0), 'forearm.R': (-20, 0, 0), 'spine': (-18, 0, 0), 'head': (12, 0, 0)})
P(rM, 640, SIT_SOFA, {'upper_arm.R': (-12, 18, 0), 'forearm.R': (-20, 0, 0), 'spine': (-18, 0, 0), 'head': (12, 0, 0)})
sk(fM, 'eyes_closed', 0.0, 640, 'LINEAR'); sk(fM, 'eyes_closed', 1.0, 660)
sk(fM, 'brow_sad', 0.7, 640); sk(fM, 'brow_sad', 0.3, 690)
sk(fM, 'mouth_frown', 0.6, 640); sk(fM, 'mouth_frown', 0.2, 690)
sk(fM, 'sigh', 0.0, 662); sk(fM, 'sigh', 1.0, 670); sk(fM, 'sigh', 1.0, 674); sk(fM, 'sigh', 0.0, 684)
P(rM, 668, SIT_SOFA, {'upper_arm.R': (-12, 18, 0), 'forearm.R': (-20, 0, 0), 'spine': (-20, 0, 0), 'chest': (-12, 0, 0), 'head': (6, 0, 0)})
P(rM, 684, SIT_SOFA, {'upper_arm.R': (-12, 18, 0), 'forearm.R': (-20, 0, 0), 'spine': (-17, 0, 0), 'chest': (-3, 0, 0), 'head': (14, 0, 0)})
P(rM, 702, SIT_SOFA, {'upper_arm.R': (-10, 20, 0), 'forearm.R': (-18, 0, 0), 'spine': (-15, 0, 0), 'chest': (2, 0, 0),
                      'neck': (22, 0, 0), 'head': (22, 10, 0)})
P(rM, 720, SIT_SOFA, {'upper_arm.R': (-10, 20, 0), 'forearm.R': (-18, 0, 0), 'spine': (-15, 0, 0), 'chest': (2, 0, 0),
                      'neck': (24, 0, 0), 'head': (24, 12, 0)})

# Tela da TV: liga (f538), tarja entra (f548-560), desliga com flash (f614)
for o_ in (tv_off,):
    key_vis(o_, 1, True); key_vis(o_, 538, False); key_vis(o_, 615, True)
key_vis(tv_flash, 1, False); key_vis(tv_flash, 614, True); key_vis(tv_flash, 615, False)
key(tarja, 'scale', (0.0001, 1, 1), 1, 'CONSTANT'); key(tarja, 'scale', (0.0001, 1, 1), 548)
key(tarja, 'scale', (1.03, 1, 1), 557); key(tarja, 'scale', (1, 1, 1), 560)
key(manchete, 'scale', (0.0001, 1, 1), 1, 'CONSTANT'); key(manchete, 'scale', (0.0001, 1, 1), 553)
key(manchete, 'scale', (1, 1, 1), 562)
for o_ in (D.objects['PRP_TV_Urgente'], D.objects['PRP_TV_UrgenteTxt']):
    key_vis(o_, 1, False); key_vis(o_, 556, True)
