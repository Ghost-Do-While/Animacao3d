# Parte 4 - Animação dos planos 01-10 (rig Rigify FK; expressões nos FACE_<nome>; props presos a ossos de mão)
MK = CHARS['Marcos']; MG = CHARS['Miguel']; CL = CHARS['Claudio']
rM, fM = MK['rig'], MK['face']
rG, fG = MG['rig'], MG['face']
rC, fC = CL['rig'], CL['face']
carM = CARS['Marcos']['root']
sc_ = bpy.context.scene

# ---------------------------------------------------------------- infraestrutura de pose (nomes "lógicos" -> controles do Rigify)
FINGERS = ['f_index', 'f_middle', 'f_ring', 'f_pinky']
CTRLS = (['torso', 'hips', 'chest', 'neck', 'head'] + [f'{n}.{s}' for s in 'LR' for n in ('shoulder', 'upper_arm_fk', 'forearm_fk', 'hand_fk', 'thigh_fk', 'shin_fk', 'foot_fk')]
         + [f'{f}.01_master.{s}' for s in 'LR' for f in FINGERS + ['thumb']] + ['tie.001', 'tie.002', 'hem.L', 'hem.R'])
def xlate(p):
    out = {}
    def add(k, v):
        o = out.get(k, (0, 0, 0)); out[k] = (o[0] + v[0], o[1] + v[1], o[2] + v[2])
    for k, v in p.items():
        if k == 'spine': add('torso', v); add('hips', (-v[0], -v[1], -v[2]))      # tronco inclina a partir do quadril, pernas ficam plantadas
        elif k in ('chest', 'neck', 'head'): add(k, v)
        elif k.startswith(('upper_arm.', 'forearm.', 'hand.', 'thigh.', 'shin.', 'foot.')):
            n, s = k.split('.'); add(f'{n}_fk.{s}', v)
        elif k.startswith('shoulder.'): add(k, v)
        elif k[0] == 'f' and len(k) > 2 and k[1] in '1234' and k[2] == '.': add(f'{FINGERS[int(k[1]) - 1]}.01_master.{k[3:]}', v)
        elif k.startswith('thumb.'): add(f'thumb.01_master.{k[6:]}', v)
        elif k == 'tie': add('tie.001', v); add('tie.002', (v[0] * 0.6, v[1] * 0.6, v[2] * 0.6))
        elif k.startswith('hem.'): add(k, v)
    return out
def full(rig, p):
    q = xlate(p); out = {b: (0, 0, 0) for b in CTRLS if b in rig.pose.bones}
    out.update(q); return out
def P(rig, frame, *ps, interp=None):
    pose(rig, full(rig, merge(*ps)), frame, interp)
def PH(rig, f0, f1, *ps):               # hold: mesma pose entre f0 e f1 (ritmo de comédia: 2-4 frames)
    P(rig, f0, *ps); P(rig, f1, *ps)
def pose_only(rig, p, frame, interp=None):   # keys só em alguns controles (ex.: dedos do tamborilar, gravata)
    pose(rig, xlate(p), frame, interp)

def objmat(o, f):
    def ev(path, i, d):
        fc = find_fc(o, path, i); return fc.evaluate(f) if fc else d
    loc = Vector([ev('location', i, o.location[i]) for i in range(3)])
    rot = Euler([ev('rotation_euler', i, o.rotation_euler[i]) for i in range(3)], 'XYZ')
    scl = Vector([ev('scale', i, o.scale[i]) for i in range(3)])
    return Matrix.LocRotScale(loc, rot.to_quaternion(), scl)
for r_ in (rM, rG, rC):
    r_.pose.bones['eyes']['eyes_follow'] = 0.0       # alvo do olhar fixo no mundo (não acompanha a cabeça)
def look_rel(rig, f, v=(0, 0, 0), interp=None):
    """Olhar relativo ao personagem: v em metros a partir do alvo de repouso (x = lado esquerdo do personagem, z = para cima)."""
    ploc(rig, 'eyes', (v[0], -v[1], v[2]), f, interp)
def look_world(rig, f, pt, interp=None):
    """Olhar para um ponto do mundo (usa a transformação keyada do rig no frame f)."""
    M = objmat(rig, f); loc = M.inverted() @ Vector(pt)
    rest = rig.data.bones['eyes'].head_local
    ploc(rig, 'eyes', loc - rest, f, interp)
def head_world(rig, f, up=0.0):
    M = objmat(rig, f); return M @ (rig.data.bones['DEF-spine.006'].head_local + Vector((0, -0.05, 0.12 + up)))

# ---------------------------------------------------------------- biblioteca de poses (graus; x<0 balança o braço para frente)
ARMS_REST = {'upper_arm.L': (0, -6, 0), 'upper_arm.R': (0, 6, 0), 'forearm.L': (-8, 0, 0), 'forearm.R': (-8, 0, 0),
             **{f'f{i}.L': (0, 18, 0) for i in range(1, 5)}, **{f'f{i}.R': (0, -18, 0) for i in range(1, 5)},
             'thumb.L': (0, 10, 0), 'thumb.R': (0, -10, 0)}
TIRED = {'spine': (7, 0, 0), 'chest': (9, 0, 0), 'neck': (8, 0, 0), 'head': (6, 0, 0), 'shoulder.L': (0, 0, -6), 'shoulder.R': (0, 0, 6)}
SIT_LEGS = {'thigh.L': (-86, 0, -4), 'thigh.R': (-86, 0, 4), 'shin.L': (84, 0, 0), 'shin.R': (84, 0, 0), 'foot.L': (-6, 0, 0), 'foot.R': (-6, 0, 0)}
GRIP_R = {f'f{i}.R': (0, -60, 0) for i in range(1, 5)}
GRIP_L = {f'f{i}.L': (0, 60, 0) for i in range(1, 5)}
SIT_CAR = merge(SIT_LEGS, {'thigh.L': (-80, 0, -4), 'thigh.R': (-80, 0, 4), 'shin.L': (72, 0, 0), 'shin.R': (72, 0, 0),
                           'spine': (-8, 0, 0), 'chest': (-4, 0, 0), 'neck': (9, 0, 0), 'head': (7, 0, 0),
                           'upper_arm.L': (-62, 0, -8), 'upper_arm.R': (-62, 0, 8),
                           'forearm.L': (-26, 0, 0), 'forearm.R': (-26, 0, 0), 'hand.L': (10, 0, 0), 'hand.R': (10, 0, 0),
                           'shoulder.L': (0, 0, -6), 'shoulder.R': (0, 0, 6)}, GRIP_R, GRIP_L)
SIT_SOFA = merge(SIT_LEGS, {'spine': (-10, 0, 0), 'chest': (-5, 0, 0), 'neck': (10, 0, 0), 'head': (8, 0, 0),
                            'upper_arm.L': (-20, -8, 0), 'upper_arm.R': (-20, 8, 0), 'forearm.L': (-50, 0, 0), 'forearm.R': (-50, 0, 0),
                            'shoulder.L': (0, 0, -8), 'shoulder.R': (0, 0, 8)},
                 {f'f{i}.L': (0, 25, 0) for i in range(1, 5)}, {f'f{i}.R': (0, -25, 0) for i in range(1, 5)})
CROUCH = {'thigh.L': (-52, 0, -5), 'thigh.R': (-52, 0, 5), 'shin.L': (70, 0, 0), 'shin.R': (70, 0, 0),
          'foot.L': (-20, 0, 0), 'foot.R': (-20, 0, 0), 'spine': (24, 0, 0), 'chest': (12, 0, 0), 'neck': (-10, 0, 0)}

def walk(rig, f0, f1, base, period=12, amp=24, start=1):
    """Ciclo de caminhada FK: coxas/joelhos alternados, braços opostos, tronco e cabeça com leve torção."""
    f = f0; s = start
    while f <= f1:
        P(rig, f, ARMS_REST, base, {
            'thigh.L': (-amp * s, 0, 0), 'thigh.R': (amp * s, 0, 0),
            'shin.L': (10 if s > 0 else 34, 0, 0), 'shin.R': (34 if s > 0 else 10, 0, 0),
            'foot.L': (amp * 0.3 * s, 0, 0), 'foot.R': (-amp * 0.3 * s, 0, 0),
            'upper_arm.L': (amp * 0.7 * s, -6, 0), 'upper_arm.R': (-amp * 0.7 * s, 6, 0),
            'forearm.L': (-12 - 10 * (s > 0), 0, 0), 'forearm.R': (-12 - 10 * (s < 0), 0, 0),
            'chest': (base.get('chest', (0, 0, 0))[0], 0, -6 * s), 'head': (base.get('head', (0, 0, 0))[0], 0, 5 * s)})
        f += max(2, period // 2); s = -s

def blink(face, f, dur=6, amt=1.0):
    sk(face, 'blink', 0.0, f); sk(face, 'blink', amt, f + dur // 2); sk(face, 'blink', 0.0, f + dur)

def suspension(car, f0, f1, gain=0.9):
    """Balanço da carroceria ao frear/acelerar (massa-mola amortecido sobre a aceleração do carro)."""
    body = car['body']; root_ = car['root']
    def loc(f): return Vector((find_fc(root_, 'location', 0).evaluate(f), find_fc(root_, 'location', 1).evaluate(f), 0))
    def yawf(f): return find_fc(root_, 'rotation_euler', 2).evaluate(f)
    def spd(f):
        d = loc(f) - loc(f - 1); fwd = Vector((-math.sin(yawf(f)), math.cos(yawf(f)), 0))
        return d.dot(fwd)
    p = 0.0; v = 0.0; w = 0.55; z = 0.45
    body.rotation_mode = 'XYZ'
    for f in range(f0, f1 + 1):
        a = spd(f) - spd(f - 1)
        tgt = max(-0.07, min(0.07, -a * gain))          # freia -> cabeceia para frente; acelera -> agacha atrás
        acc = -w * w * (p - tgt) - 2 * z * w * v
        v += acc; p += v
        if f % 2 == 0 or f == f1:
            key(body, 'rotation_euler', (p, 0, 0), f)
            key(body, 'location', (0, 0, -abs(p) * 0.25), f)

# ================================================================ PLANOS 01-03: FILA REAL
# Os 4 carros da fila (Fila1..4) entram de verdade pela cancela da ENTRADA e estacionam nas vagas livres: V4, V5, V2, V1.
# Claudio já está na V3; Marcos (último da fila) fica com a V6. Trajetos por arcos de 4 m, velocidade com aceleração/frenagem.
ROAD_Z = -0.15
V_IN, RAMP, R_ARC = 0.38, 6, 4.0

def z_of(y): return ROAD_Z if y < -16.0 else (-0.04 if y < -13.0 else 0.0)
def densify(pts, step=0.6):
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        for i in range(1, n + 1): out.append((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n))
    return out
def arc(cx, cy, R, a0, a1, step=8, cw=True):
    """pontos de um arco (ângulos em graus a partir de +X), sentido horário se cw."""
    n = max(2, int(abs(a1 - a0) / step)); out = []
    for i in range(n + 1):
        a = rad(a0 + (a1 - a0) * i / n); out.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    return out
def dist_at(t, S, v, ramp):
    T = ramp + S / v
    if t <= 0: return 0.0
    if t >= T: return S
    if t < ramp: return v * t * t / (2 * ramp)
    if t <= S / v: return v * (t - ramp / 2)
    return S - v * (T - t) ** 2 / (2 * ramp)
def time_for(S, v, ramp, d):
    t = 0.0
    while dist_at(t, S, v, ramp) < d and t < 400: t += 0.25
    return t
def drive(car, pts, f0, v=V_IN, ramp=RAMP):
    """Anda o carro pelos pontos (x, y); a direção vem da tangente. Retorna (frame_final, S, dens, ds)."""
    root_ = car['root']; root_.rotation_mode = 'XYZ'
    dens = densify(pts)
    ds = [0.0]
    for a, b in zip(dens[:-1], dens[1:]): ds.append(ds[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    S = ds[-1]
    rots = []
    for i in range(len(dens)):
        a = dens[max(0, i - 1)]; b = dens[min(len(dens) - 1, i + 1)]
        rots.append(math.degrees(math.atan2(-(b[0] - a[0]), (b[1] - a[1]))))
    for i in range(1, len(rots)):           # desenrola ângulos
        while rots[i] - rots[i - 1] > 180: rots[i] -= 360
        while rots[i] - rots[i - 1] < -180: rots[i] += 360
    sm = [sum(rots[max(0, i - 2):i + 3]) / len(rots[max(0, i - 2):i + 3]) for i in range(len(rots))]
    T = ramp + S / v; f_end = f0 + int(math.ceil(T))
    def at(s):
        lo = 0
        while lo < len(ds) - 2 and ds[lo + 1] < s: lo += 1
        a, b = dens[lo], dens[lo + 1]; u = 0 if ds[lo + 1] == ds[lo] else (s - ds[lo]) / (ds[lo + 1] - ds[lo])
        u = max(0.0, min(1.0, u))
        return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, sm[lo] + (sm[lo + 1] - sm[lo]) * u)
    for f in list(range(f0, f_end, 2)) + [f_end]:
        x, y, r = at(dist_at(f - f0, S, v, ramp))
        key(root_, 'location', (x, y, z_of(y)), f, 'LINEAR'); key(root_, 'rotation_euler', (0, 0, rad(r)), f, 'LINEAR')
    return f_end, S, dens, ds
def frame_when_y(f0, S, v, ramp, dens, ds, ytarget):
    s_t = next((ds[i] for i, p in enumerate(dens) if p[1] >= ytarget), S)
    return f0 + time_for(S, v, ramp, s_t)
def odometer(car, f0, f1):
    root_ = car['root']; acc = 0.0; prev = None
    for f in range(f0, f1 + 1):
        p = Vector((find_fc(root_, 'location', 0).evaluate(f), find_fc(root_, 'location', 1).evaluate(f), 0))
        if prev is not None: acc += (p - prev).length
        prev = p
        if f % 2 == 0 or f == f1:
            root_['odo'] = acc; root_.keyframe_insert('["odo"]', frame=f)
            for fc in fcurves(root_):
                if fc.data_path == '["odo"]':
                    for kp in fc.keyframe_points:
                        if abs(kp.co.x - f) < 0.01: kp.interpolation = 'LINEAR'

# ---- vagas livres e trajetos
def final_x_right(L): return RIGHT_X1 - 0.4 - L / 2
LENS = {'Fila1': 4.4, 'Fila2': 4.0, 'Fila3': 4.4, 'Fila4': 4.0}
SPOTS = {'Fila1': ('R', RIGHT_Y[3]), 'Fila2': ('L', CENT_Y['V5']), 'Fila3': ('R', RIGHT_Y[1]), 'Fila4': ('R', RIGHT_Y[0])}
START = {'Fila1': ((ENTR_CX, -9.95), 'gate'), 'Fila2': ((ENTR_CX, -14.6), 'gate'),
         'Fila3': ((10.7, LANE_Y), 'lane'), 'Fila4': ((15.4, LANE_Y), 'lane')}
def lane_prefix(x0):
    c = (ENTR_CX + 3.6, -14.15)                                           # curva de 3,6 m: da faixa da rua para a entrada
    pts = [(x0, LANE_Y), (ENTR_CX + 3.6, LANE_Y)]
    pts += [(c[0] + 3.6 * math.cos(rad(a)), c[1] + 3.6 * math.sin(rad(a))) for a in range(-90, -181, -10)]    # horário: sul -> oeste... (ver abaixo)
    return pts
def lane_curve(x0):
    cx, cy, R = ENTR_CX + 3.6, -14.15, 3.6
    pts = [(x0, LANE_Y), (cx, LANE_Y)]
    for a in range(0, 91, 9):                                             # de sul (rumo oeste) até oeste (rumo norte)
        pts.append((cx - R * math.sin(rad(a)), cy - R * math.cos(rad(a))))
    pts += [(ENTR_CX, -12.0), (ENTR_CX, -9.95)]
    return pts
COMMON = [(ENTR_CX, -9.95), (ENTR_CX, -6.0), (5.5, -4.2), (AISLE_X + 0.4, -2.6), (AISLE_X, -1.0)]
def spot_tail(kind, ys, xf):
    y0 = ys - R_ARC; pts = []
    if y0 > -1.0: pts.append((AISLE_X, y0))
    for a in range(0, 91, 9):
        ph = rad(a)
        if kind == 'R': pts.append((AISLE_X + R_ARC * (1 - math.cos(ph)), y0 + R_ARC * math.sin(ph)))
        else: pts.append((AISLE_X - R_ARC * (1 - math.cos(ph)), y0 + R_ARC * math.sin(ph)))
    pts.append((xf, ys))
    return pts

# ---- a fila ANDA em passos: cada carro avança uma posição quando a da frente fica livre; na frente da cancela ele para,
#      a cancela ABRE, o carro passa e vai para a vaga, a cancela FECHA; só então abre para o próximo.
QP = [(ENTR_CX, -9.95), (ENTR_CX, -14.5), (10.7, LANE_Y), (15.4, LANE_Y)]       # posições de espera (0 = frente da cancela)
def lane_to_w1(x0):
    cx, cy, R = ENTR_CX + 3.25, -14.5, 3.25
    return [(x0, LANE_Y), (cx, LANE_Y)] + [(cx - R * math.sin(rad(a)), cy - R * math.cos(rad(a))) for a in range(0, 91, 9)]
def step_path(i):
    if i == 3: return [QP[3], QP[2]]
    if i == 2: return lane_to_w1(QP[2][0])
    return [QP[1], (ENTR_CX, -12.0), QP[0]]
SCHED = {}; GATE = []; STEPS = {}
# 1º ciclo (visível no plano 1) é lento e arrastado; os ciclos 2-4 acontecem durante o plano 2 (interior do carro) e são mais curtos
OPEN_L = [30, 12, 12, 12]; CLOSE_L = [22, 8, 8, 8]; OFF_L = [16, 6, 6, 6]
pos = {'Fila1': 0, 'Fila2': 1, 'Fila3': 2, 'Fila4': 3}
free = [0, 0, 0, 0]                    # frame a partir do qual a posição i está livre (o carro que estava nela já andou 3 m)
prev_gate_end = 0
for nm in ('Fila1', 'Fila2', 'Fila3', 'Fila4'):
    kind, ys = SPOTS[nm]
    xf = final_x_right(LENS[nm]) if kind == 'R' else (CENT_X0 + CENT_X1) / 2
    car = CARS[nm]; r_ = car['root']; r_.rotation_mode = 'XYZ'
    p = pos[nm]; q = QP[p]
    root(r_, (q[0], q[1], z_of(q[1])), 90 if p >= 2 else 0, 1, 'CONSTANT')
    arr = 0; stages = []
    while p > 0:
        f0 = int(max(arr, free[p - 1]))
        f_end, S, _d, _s = drive(car, step_path(p), f0)
        stages.append((f0, f_end)); free[p] = f0 + int(time_for(S, V_IN, RAMP, 3.0)); arr = f_end; p -= 1
    kc = len(GATE)
    T = max(prev_gate_end, arr - OFF_L[kc], 10 if kc == 0 else 0)               # a cancela só abre com o carro parado na frente dela
    fB0 = max(T + OFF_L[kc], arr + 1)
    ptsB = [QP[0]] + COMMON[1:] + spot_tail(kind, ys, xf)
    fB_end, SB, densB, dsB = drive(car, ptsB, fB0); stages.append((fB0, fB_end))
    C = int(frame_when_y(fB0, SB, V_IN, RAMP, densB, dsB, -4.4)) + 2             # a traseira já passou: pode fechar
    GATE.append((T, C, OPEN_L[kc], CLOSE_L[kc])); prev_gate_end = C + CLOSE_L[kc]
    free[0] = fB0 + int(time_for(SB, V_IN, RAMP, 3.0))
    STEPS[nm] = [s for s in stages]
    SCHED[nm] = dict(f0=stages[0][0], f_end=fB_end, stages=stages)
    br = bsdf(car['brake']).inputs['Emission Strength']; hd = bsdf(car['head']).inputs['Emission Strength']
    f = 1; on = True
    while f < stages[0][0] - 2:
        key(br, 'default_value', 8.0 if on else 0.7, f, 'CONSTANT'); f += random.randint(14, 30) if on else random.randint(4, 8); on = not on
    for (s0, s1) in stages:
        key(br, 'default_value', 0.6, s0, 'CONSTANT'); key(br, 'default_value', 8.0, s1 - 4, 'CONSTANT')
    key(br, 'default_value', 0.0, fB_end + 12, 'CONSTANT')
    key(hd, 'default_value', 3.0, 1, 'CONSTANT'); key(hd, 'default_value', 0.0, fB_end + 14, 'CONSTANT')
    suspension(car, stages[0][0] - 1, fB_end + 14, 0.5)
    odometer(car, stages[0][0] - 1, fB_end + 14)
SCHED_PRINT = {k: (v['f0'], v['f_end']) for k, v in SCHED.items()}
f_close0 = GATE[-1][1]

# ---- Carro do Marcos: último da fila; avança conforme a fila anda; para na cancela; entra; estaciona na V6
brM = bsdf(CARS['Marcos']['brake']).inputs['Emission Strength']; hdM = bsdf(CARS['Marcos']['head']).inputs['Emission Strength']
key(brM, 'default_value', 8.0, 1, 'CONSTANT'); key(brM, 'default_value', 0.6, 72, 'CONSTANT'); key(brM, 'default_value', 8.0, 87, 'CONSTANT')
key(brM, 'default_value', 8.0, 146, 'CONSTANT'); key(brM, 'default_value', 0.0, 192, 'CONSTANT'); key(brM, 'default_value', 8.0, 242, 'CONSTANT')
key(hdM, 'default_value', 4.0, 1, 'CONSTANT'); key(hdM, 'default_value', 0.0, 246, 'CONSTANT')
carM.rotation_mode = 'XYZ'
def carkey(f, loc_, rz=0, interp=None):
    key(carM, 'location', loc_, f, interp); key(carM, 'rotation_euler', (0, 0, rad(rz)), f, interp)
MX0 = 20.1; t4 = SCHED['Fila4']['f0']
f4 = STEPS['Fila4']                      # etapas do Fila4: 3->2, 2->1, 1->0, vaga
carkey(1, (MX0, LANE_Y, ROAD_Z), 90, interp='CONSTANT')
carkey(72, (MX0, LANE_Y, ROAD_Z), 90)                                    # o Fila4 já saiu da posição 3: Marcos avança um carro...
carkey(86, (15.4, LANE_Y, ROAD_Z), 90)                                   # ...com as duas mãos no volante
carkey(144, (15.4, LANE_Y, ROAD_Z), 90, interp='CONSTANT')               # PARADO durante toda a cena de estresse (frames 86-144)
carkey(145, (8.9, LANE_Y, ROAD_Z), 90)
carkey(151, (7.3, LANE_Y + 0.1, ROAD_Z), 76)
carkey(156, (6.4, -16.5, -0.1), 34)
carkey(160, (ENTR_CX, -14.4, -0.04), 5)
carkey(164, (ENTR_CX, -11.6, 0.0), 0)
carkey(168, (ENTR_CX, -10.0, 0.0), 0)                        # para na cancela fechada (passa pelo sensor S2) e ESPERA o porteiro
carkey(190, (ENTR_CX, -10.0, 0.0), 0)
carkey(198, (ENTR_CX, -6.6, 0.0), 0)                         # a cancela já está alta: avança
carkey(204, (5.6, -3.6, 0.0), 5)
carkey(205, (AISLE_X, 3.2, 0.0), 0)                          # corte P04 (elipse: carro já no corredor)
carkey(220, (AISLE_X, 7.64, 0.0), 0)
carkey(226, (AISLE_X - R_ARC * (1 - math.cos(rad(30))), 7.64 + R_ARC * math.sin(rad(30)), 0.0), 30)
carkey(232, (AISLE_X - R_ARC * (1 - math.cos(rad(60))), 7.64 + R_ARC * math.sin(rad(60)), 0.0), 60)
carkey(237, (AISLE_X - R_ARC, 7.64 + R_ARC, 0.0), 90)
V6X = (CENT_X0 + CENT_X1) / 2
carkey(243, (V6X, CENT_Y['V6'], 0.0), 90)
for fc in fcurves(carM):                                     # chegada suave na vaga
    for kp in fc.keyframe_points:
        if abs(kp.co.x - 243) < 0.01: kp.interpolation = 'BACK'; kp.easing = 'EASE_OUT'; kp.back = 0.4
suspension(CARS['Marcos'], 70, 100); suspension(CARS['Marcos'], 143, 247)
odometer(CARS['Marcos'], 1, 250)
# Porta do motorista: o vão até o carro da V5 é curto -> abre 24°
dp = CARS['Marcos']['door']; dp.rotation_mode = 'XYZ'
key(dp, 'rotation_euler', (0, 0, 0), 243); key(dp, 'rotation_euler', (0, 0, rad(-24)), 247)
key(dp, 'rotation_euler', (0, 0, rad(-24)), 249); key(dp, 'rotation_euler', (0, 0, rad(2)), 251); key(dp, 'rotation_euler', (0, 0, 0), 253)

# ---- Cancela C2 (braço aponta -X; rotação em Y POSITIVA levanta): abre, o carro passa, FECHA; abre, o próximo passa, FECHA...
key(C2, 'rotation_euler', (0, 0, 0), 1, 'CONSTANT')
def gate_cycle(T, hold_until, up, down):
    key(C2, 'rotation_euler', (0, 0, 0), T, 'LINEAR')
    key(C2, 'rotation_euler', (0, rad(78), 0), T + up - 2); key(C2, 'rotation_euler', (0, rad(88), 0), T + up)      # tranco no fim
    key(C2, 'rotation_euler', (0, rad(85), 0), T + up + 2); key(C2, 'rotation_euler', (0, rad(85), 0), hold_until)
    key(C2, 'rotation_euler', (0, 0, 0), hold_until + down)
for (T_, C_, up_, dn_) in GATE: gate_cycle(T_, C_, up_, dn_)
gate_cycle(176, 210, 30, 18)                                  # Marcos: o porteiro abre sem pressa (30 frames) e fecha depois que ele passa
key(C1, 'rotation_euler', (0, 0, 0), 1, 'CONSTANT')
pb_ = D.objects['MQ_Guarita_Porteiro_Braco']; p0_ = pb_.location.copy()
btn = D.objects['MQ_Guarita_Botao']; bm_ = bsdf(btn.data.materials[0]).inputs['Emission Strength']
key(bm_, 'default_value', 1.8, 1, 'CONSTANT')
for a_ in sorted([T_ - 6 for T_, *_r in GATE] + [C_ - 1 for _t, C_, *_r in GATE] + [168, 208]):
    key(pb_, 'location', p0_, a_ - 2); key(pb_, 'location', (p0_.x + 0.05, p0_.y - 0.25, p0_.z - 0.2), a_ + 4)
    key(pb_, 'location', (p0_.x + 0.05, p0_.y - 0.25, p0_.z - 0.2), a_ + 8); key(pb_, 'location', p0_, a_ + 14)
    key(bm_, 'default_value', 7.0, a_ + 2, 'CONSTANT'); key(bm_, 'default_value', 1.8, a_ + 10, 'CONSTANT')

# ---- Marcos dentro do carro (Child Of no carro até sair)
co = rM.constraints.new('CHILD_OF'); co.name = 'NoCarro'; co.target = carM
co.inverse_matrix = Matrix.Identity(4); co.set_inverse_pending = False
key(co, 'influence', 1.0, 1, 'CONSTANT'); key(co, 'influence', 0.0, 247, 'CONSTANT')
SEAT = (-0.41, -0.12, -0.1)
root(rM, SEAT, 180, 1, 'CONSTANT')
# Plano 02: tamborila (4 frames por dedo), olha a fila, revira os olhos, suspira e encosta a cabeça
P(rM, 1, SIT_CAR, interp='CONSTANT')
look_rel(rM, 1, (0, 0.2, 0), 'CONSTANT')
sk(fM, 'brow_down', 0.4, 1); sk(fM, 'mouth_frown', 0.4, 1); sk(fM, 'brow_sad', 0.25, 1)
P(rM, 60, SIT_CAR); P(rM, 73, SIT_CAR); P(rM, 88, SIT_CAR)        # frames 73-88: dirige normalmente (carro avançando)
for i in range(4):                                                   # tamborila (4 frames por dedo) com o carro PARADO
    fi = 90 + i * 4
    pose_only(rM, {f'f{i+1}.R': (0, -60, 0)}, fi)
    pose_only(rM, {f'f{i+1}.R': (0, -6, 0)}, fi + 2)
    pose_only(rM, {f'f{i+1}.R': (0, -60, 0)}, fi + 4)
for f in (20, 98): blink(fM, f, 10)
look_rel(rM, 88, (0, 0.2, 0)); look_rel(rM, 96, (0.7, 0.2, 0.05)); look_rel(rM, 104, (0.7, 0.2, 0.05))
look_rel(rM, 108, (0.0, 0.3, 0.55)); look_rel(rM, 112, (-0.6, 0.3, 0.45)); look_rel(rM, 116, (-0.6, 0.3, 0.45)); look_rel(rM, 122, (0, 0.2, 0))
P(rM, 100, SIT_CAR)
P(rM, 104, SIT_CAR, {'spine': (-3, 0, 0), 'chest': (3, 0, 0), 'neck': (2, 0, 0), 'head': (-5, 0, 10)})
P(rM, 110, SIT_CAR, {'spine': (-3, 0, 0), 'chest': (3, 0, 0), 'neck': (2, 0, 0), 'head': (-9, 0, 4)})
P(rM, 118, SIT_CAR, {'spine': (-6, 0, 0), 'chest': (-2, 0, 0), 'head': (-4, 0, -4)})
sk(fM, 'brow_sad', 0.25, 104); sk(fM, 'brow_sad', 0.9, 116); sk(fM, 'brow_down', 0.4, 104); sk(fM, 'brow_down', 0.0, 112)
sk(fM, 'sigh', 0.0, 118); sk(fM, 'sigh', 1.0, 125); sk(fM, 'sigh', 1.0, 128); sk(fM, 'sigh', 0.0, 136)
P(rM, 125, SIT_CAR, {'spine': (-12, 0, 0), 'chest': (-12, 0, 0), 'head': (-2, 0, 0)})
P(rM, 134, SIT_CAR, {'spine': (-12, 0, 0), 'chest': (-2, 0, 0), 'neck': (0, 0, 0), 'head': (2, 0, 0)})
P(rM, 143, SIT_CAR, {'spine': (-14, 0, 0), 'chest': (-4, 0, 0), 'neck': (-8, 0, 0), 'head': (-12, 0, 6)})       # cabeça no encosto: último gesto, ainda parado
look_rel(rM, 134, (0, 0.2, 0)); look_rel(rM, 143, (0, 0.3, -0.25))
sk(fM, 'blink', 0.0, 136); sk(fM, 'blink', 0.6, 142); sk(fM, 'blink', 0.0, 150)
# frame 145: o carro volta a andar -> ele volta a dirigir (mãos no volante, postura normal)
P(rM, 150, SIT_CAR); look_rel(rM, 150, (0, 0.2, 0))
P(rM, 176, SIT_CAR)
for f_ in (200, 222): P(rM, f_, SIT_CAR, {'head': (0, 0, -6 if f_ == 222 else 0)})
# Plano 04: estaciona na V6, sai espremido entre os carros, fecha a porta e se vira
P(rM, 240, SIT_CAR)
P(rM, 243, SIT_CAR, {'upper_arm.L': (-20, -10, 0), 'forearm.L': (-30, 0, 0), 'head': (0, 0, -25), 'spine': (4, 0, 0)})
key(rM, 'rotation_euler', (0, 0, rad(180)), 243); key(rM, 'location', SEAT, 243)
key(rM, 'rotation_euler', (0, 0, rad(235)), 246, 'CONSTANT'); key(rM, 'location', (SEAT[0] - 0.2, SEAT[1], SEAT[2] + 0.1), 246, 'CONSTANT')
P(rM, 246, SIT_CAR, {'thigh.L': (-80, 0, 30), 'thigh.R': (-80, 0, 20)}, interp='CONSTANT')
OUT = (V6X - 0.45, CENT_Y['V6'] - 1.4)                 # no vão entre os carros da V5 e da V6, junto à porta do motorista
root(rM, (OUT[0], OUT[1], -0.1), yaw(0, 1), 247)
P(rM, 247, ARMS_REST, CROUCH, {'upper_arm.L': (-30, -10, 0)})
root(rM, (OUT[0], OUT[1], 0), yaw(0, 1), 249)
P(rM, 249, ARMS_REST, TIRED, {'upper_arm.L': (-55, 0, 20), 'forearm.L': (-20, 0, 0), 'spine': (10, 0, 0)})
P(rM, 252, ARMS_REST, TIRED, {'upper_arm.L': (-15, -5, 0), 'spine': (10, 0, 0), 'head': (6, 0, 14)})
look_world(rM, 247, (OUT[0] + 2.0, OUT[1], 1.5)); look_world(rM, 252, (OUT[0] + 3.0, OUT[1] - 0.5, 1.5))
blink(fM, 244, 8)
# Plano 05: over-the-shoulder - Marcos anda, para e arqueia as sobrancelhas
MPOS = (3.4, 9.4)
look_at_dir = (MIGUEL_POS[0] - MPOS[0], MIGUEL_POS[1] - MPOS[1])
root(rM, (2.6, 9.7, 0), yaw(1, -0.1), 253, 'LINEAR')
walk(rM, 253, 259, TIRED, period=8, amp=16)
root(rM, (MPOS[0], MPOS[1], 0), yaw(*look_at_dir), 260)
P(rM, 261, ARMS_REST, TIRED); P(rM, 266, ARMS_REST, TIRED, {'spine': (2, 0, 0), 'chest': (-2, 0, 0), 'head': (-3, 0, 0), 'shoulder.L': (0, 0, -2), 'shoulder.R': (0, 0, 2)})
look_world(rM, 253, (MIGUEL_POS[0], MIGUEL_POS[1], 1.6)); look_world(rM, 260, (MIGUEL_POS[0], MIGUEL_POS[1], 1.6)); look_world(rM, 280, (CLAUDIO_POS[0], CLAUDIO_POS[1], 1.6))
sk(fM, 'brow_sad', 0.9, 253); sk(fM, 'brow_sad', 0.0, 262)
sk(fM, 'brow_up', 0.0, 262); sk(fM, 'brow_up', 1.0, 268); sk(fM, 'brow_up', 0.8, 288)
sk(fM, 'mouth_frown', 0.4, 258); sk(fM, 'mouth_frown', 0.0, 264)
sk(fM, 'O', 0.0, 262); sk(fM, 'O', 0.4, 268); sk(fM, 'O', 0.2, 288)
blink(fM, 278, 8)
P(rM, 288, ARMS_REST, TIRED, {'spine': (2, 0, 0), 'chest': (-2, 0, 0), 'head': (-3, 0, -6)})
for f in range(300, 492, 24):
    P(rM, f, ARMS_REST, TIRED, {'chest': (9 + (2 if (f // 24) % 2 else -1), 0, 0), 'head': (6, 0, -8 if (f // 24) % 2 else -3)})
    look_world(rM, f, (CLAUDIO_POS[0], CLAUDIO_POS[1], 1.6) if (f // 24) % 2 else (MIGUEL_POS[0], MIGUEL_POS[1], 1.6))

# ================================================================ BRIGA (planos 05-07): Miguel (aponta, mãos na cabeça) x Claudio (empurra o ar, ombros)
root(rG, (MIGUEL_POS[0], MIGUEL_POS[1], 0), yaw(0, -1), 1, 'CONSTANT')
root(rC, (CLAUDIO_POS[0], CLAUDIO_POS[1], 0), yaw(0, 1), 1, 'CONSTANT')
ANG_G = merge(ARMS_REST, {'spine': (8, 0, 0), 'chest': (5, 0, 0), 'neck': (-6, 0, 0), 'head': (-6, 0, 0),
                          'upper_arm.L': (-22, -20, 0), 'upper_arm.R': (-22, 20, 0), 'forearm.L': (-45, 0, 0), 'forearm.R': (-45, 0, 0),
                          'shoulder.L': (0, 0, -10), 'shoulder.R': (0, 0, 10)})
POINT_R = {'f1.R': (0, 0, 0), 'f2.R': (0, -95, 0), 'f3.R': (0, -95, 0), 'f4.R': (0, -95, 0), 'thumb.R': (0, -50, 0)}
FLOOR_G = merge(ANG_G, POINT_R, {'spine': (18, 0, 0), 'chest': (8, 0, 0), 'head': (16, 0, 0), 'upper_arm.R': (-30, -48, 0), 'forearm.R': (-6, 0, 0), 'hand.R': (-6, 0, 0)})
AT_CL_G = merge(ANG_G, POINT_R, {'spine': (10, 0, 6), 'head': (-8, 0, -6), 'upper_arm.R': (-92, 0, 4), 'forearm.R': (0, 0, 0), 'shoulder.R': (0, 0, 18)})
HEAD_G = merge(ANG_G, {'spine': (-6, 0, 0), 'chest': (-6, 0, 0), 'neck': (-10, 0, 0), 'head': (-16, 0, 0),
                       'upper_arm.L': (-30, 55, 0), 'forearm.L': (-125, 0, 0), 'upper_arm.R': (-30, -55, 0), 'forearm.R': (-125, 0, 0),
                       **{f'f{i}.L': (0, 25, 0) for i in range(1, 5)}, **{f'f{i}.R': (0, -25, 0) for i in range(1, 5)}})
DEF_C = merge(ARMS_REST, {'spine': (-5, 0, 0), 'chest': (-3, 0, 0), 'head': (0, 0, 6),
                          'upper_arm.L': (-25, -14, 0), 'upper_arm.R': (-25, 14, 0), 'forearm.L': (-58, 0, 0), 'forearm.R': (-58, 0, 0)})
PREP_C = merge(DEF_C, {'upper_arm.L': (-14, -12, 0), 'upper_arm.R': (-14, 12, 0), 'forearm.L': (-118, 0, 0), 'forearm.R': (-118, 0, 0),
                       'hand.L': (70, 0, 0), 'hand.R': (70, 0, 0), 'spine': (-10, 0, 0), 'chest': (-6, 0, 0)})
PUSH_C = merge(DEF_C, {'upper_arm.L': (-80, 0, -8), 'upper_arm.R': (-80, 0, 8), 'forearm.L': (-14, 0, 0), 'forearm.R': (-14, 0, 0),
                       'hand.L': (75, 0, 0), 'hand.R': (75, 0, 0), 'spine': (5, 0, 0), 'chest': (6, 0, 0), 'head': (-4, 0, 6),
                       **{f'f{i}.L': (0, 0, 0) for i in range(1, 5)}, **{f'f{i}.R': (0, 0, 0) for i in range(1, 5)}})
SHRUG_C = merge(DEF_C, {'upper_arm.L': (-8, -32, 0), 'upper_arm.R': (-8, 32, 0), 'forearm.L': (-85, 0, -28), 'forearm.R': (-85, 0, 28),
                        'hand.L': (0, 40, 0), 'hand.R': (0, -40, 0), 'chest': (-8, 0, 0), 'neck': (-6, 0, 0), 'head': (-5, 0, 16),
                        'shoulder.L': (0, 0, 28), 'shoulder.R': (0, 0, -28),
                        **{f'f{i}.L': (0, 0, 0) for i in range(1, 5)}, **{f'f{i}.R': (0, 0, 0) for i in range(1, 5)}})
CROSS_C = merge(DEF_C, {'upper_arm.L': (-30, 0, -20), 'upper_arm.R': (-30, 0, 20), 'forearm.L': (-98, 0, -45), 'forearm.R': (-98, 0, 45)})
for f_ in (1, 253):
    P(rG, f_, ANG_G); P(rC, f_, DEF_C)
for f, pg, pc_ in ((259, AT_CL_G, DEF_C), (266, ANG_G, PUSH_C), (272, AT_CL_G, PREP_C), (279, ANG_G, PUSH_C), (286, ANG_G, DEF_C)):
    P(rG, f, pg); P(rC, f, pc_)
sk(fG, 'brow_angry', 1.0, 1); sk(fG, 'mouth_shout', 0.35, 1); sk(fG, 'nostril_flare', 0.5, 1)
sk(fC, 'brow_angry', 0.4, 1); sk(fC, 'brow_smug', 0.6, 1); sk(fC, 'mouth_smirk', 0.6, 1)
lipsync(fG, 'Mas que absurdo, sai daí agora!', 254, 270, 0.8)
lipsync(fC, 'Calma aí, rapidinho!', 272, 287, 0.8)
def gaze_pair(f0, f1):
    for f in range(f0, f1, 12):
        look_world(rG, f, head_world(rC, f)); look_world(rC, f, head_world(rG, f))
gaze_pair(1, 289)
# Plano 06: Miguel aponta o chão (V3), aponta Claudio, mãos na cabeça ("Pelo amor de Deus!")
P(rG, 289, ANG_G)
P(rG, 293, ANG_G, {'upper_arm.R': (25, -10, 0), 'forearm.R': (-62, 0, 0), 'spine': (-4, 0, 0), 'head': (0, 0, 0)})
look_world(rG, 295, (MIGUEL_POS[0] + 2.0, MIGUEL_POS[1] - 1.5, 0.0))
P(rG, 297, FLOOR_G, interp='CONSTANT'); P(rG, 300, FLOOR_G)
for i, f in enumerate(range(303, 318, 4)):
    P(rG, f, FLOOR_G, {'upper_arm.R': (-30 - (0 if i % 2 == 0 else 12), -48, 0), 'chest': (8 + 3 * (i % 2), 0, 0)})
P(rG, 319, FLOOR_G)
look_world(rG, 319, head_world(rC, 319)); look_world(rG, 322, head_world(rC, 322))
P(rG, 321, AT_CL_G, {'upper_arm.R': (-70, 0, 4), 'head': (-4, 0, -4)})
P(rG, 324, AT_CL_G, interp='CONSTANT'); P(rG, 328, AT_CL_G)
for i, f in enumerate(range(332, 347, 4)):
    P(rG, f, AT_CL_G, {'upper_arm.R': (-86 - (0 if i % 2 == 0 else 10), 0, 4), 'spine': (12 if i % 2 == 0 else 7, 0, 6)})
P(rG, 349, AT_CL_G)
P(rG, 352, ANG_G, {'spine': (16, 0, 0), 'upper_arm.L': (-12, -34, 0), 'upper_arm.R': (-12, 34, 0)})
look_rel(rG, 352, (0, 0.3, 0.2)); look_rel(rG, 357, (0, 0.2, 0.9))
P(rG, 357, HEAD_G, interp='CONSTANT'); P(rG, 360, HEAD_G)
for i, f in enumerate(range(364, 396, 4)):
    P(rG, f, HEAD_G, {'head': (-16, 0, 12 if i % 2 == 0 else -12), 'spine': (-6 - (i % 2) * 3, 0, 0), 'chest': (-6, 0, 5 if i % 2 else -5)})
sk(fG, 'vein_pop', 0.0, 296); sk(fG, 'vein_pop', 1.0, 304)
for i, f in enumerate(range(312, 396, 8)):
    sk(fG, 'vein_pop', 0.75 if i % 2 == 0 else 1.0, f); sk(fG, 'nostril_flare', 1.0 if i % 2 == 0 else 0.4, f)
sk(fG, 'mouth_shout', 0.35, 290); sk(fG, 'mouth_shout', 0.55, 300)
lipsync(fG, 'Essa vaga é minha! Eu passei o dia todo trabalhando, aí agora eu chego e você tá no meu lugar? Pelo amor de Deus!', 292, 392, 1.0)
P(rC, 292, CROSS_C); P(rC, 392, CROSS_C, {'head': (-4, 0, 10), 'shoulder.L': (0, 0, 6)})
# Plano 07: Claudio empurra o ar, dá de ombros, deboche
P(rC, 397, DEF_C); P(rC, 401, PREP_C)
PH(rC, 405, 408, PUSH_C); P(rC, 413, PREP_C)
PH(rC, 417, 420, PUSH_C); P(rC, 426, DEF_C)
PH(rC, 431, 437, SHRUG_C); P(rC, 444, SHRUG_C, {'head': (-4, 0, -12)}); P(rC, 450, DEF_C); P(rC, 455, PREP_C)
PH(rC, 459, 463, PUSH_C); P(rC, 470, DEF_C)
PH(rC, 475, 483, SHRUG_C); P(rC, 492, SHRUG_C, {'head': (-6, 0, 18)})
sk(fC, 'brow_smug', 1.0, 398); sk(fC, 'mouth_smirk', 0.9, 398); sk(fC, 'brow_angry', 0.0, 398)
lipsync(fC, 'Eu parei rapidinho, tava só visitando um amigo! Até parece que ficar esperando um pouco vai te matar!', 400, 486, 1.0)
sk(fC, 'mouth_shout', 0.0, 398); sk(fC, 'mouth_shout', 0.3, 404); sk(fC, 'mouth_shout', 0.3, 486); sk(fC, 'mouth_shout', 0.0, 490)
for f in (428, 447, 480):   # rola os olhos
    look_rel(rC, f, (0, 0.3, 0.1)); look_rel(rC, f + 4, (0.5, 0.3, 0.6)); look_rel(rC, f + 9, (-0.5, 0.3, 0.55)); look_rel(rC, f + 14, (0, 0.3, 0.1))
for f in (398, 440, 470): look_world(rC, f, head_world(rG, f))
for f in (340, 450): blink(fC, f, 6)
blink(fG, 380, 5)
for i, f in enumerate(range(397, 493, 7)):
    P(rG, f, AT_CL_G if i % 2 == 0 else ANG_G, {'spine': (8 + (i % 3) * 3, 0, 0), 'head': (-6, 0, 8 * (-1) ** i)})
lipsync(fG, 'Não, não, não! Isso é um absurdo! Tira esse carro daí!', 410, 488, 0.8)

# ================================================================ PLANOS 08-10: APARTAMENTO (Bloco A, 3º andar)
dpA = D.objects['ENV_Apartamento_Porta_Pivo']; dpA.rotation_mode = 'XYZ'
key(dpA, 'rotation_euler', (0, 0, 0), 1, 'CONSTANT'); key(dpA, 'rotation_euler', (0, 0, 0), 492)
key(dpA, 'rotation_euler', (0, 0, rad(-82)), 499); key(dpA, 'rotation_euler', (0, 0, rad(-76)), 504)
DOORC = (-13.2, 6.0)
root(rM, AZ(DOORC[0], DOORC[1] + 0.4, 0), yaw(0, -1), 493, 'CONSTANT')
sk(fM, 'brow_up', 0.8, 492, 'CONSTANT'); sk(fM, 'brow_up', 0.0, 493, 'CONSTANT'); sk(fM, 'O', 0.2, 492, 'CONSTANT'); sk(fM, 'O', 0.0, 493, 'CONSTANT')
sk(fM, 'brow_sad', 0.0, 492, 'CONSTANT'); sk(fM, 'brow_sad', 0.7, 493, 'CONSTANT'); sk(fM, 'mouth_frown', 0.0, 492, 'CONSTANT'); sk(fM, 'mouth_frown', 0.6, 493, 'CONSTANT')
look_rel(rM, 493, (0, 0.2, -0.15), 'CONSTANT')
walk(rM, 493, 505, TIRED, period=10, amp=20)
root(rM, AZ(-13.45, 4.4, 0), yaw(0, -1), 505)
kc = keys_.constraints.new('CHILD_OF'); kc.name = 'NaMao'; kc.target = rM; kc.subtarget = 'hand_fk.L'
kc.inverse_matrix = Matrix.Identity(4); kc.set_inverse_pending = False
key(kc, 'influence', 0.0, 1, 'CONSTANT'); key(kc, 'influence', 1.0, 493, 'CONSTANT'); key(kc, 'influence', 0.0, 509, 'CONSTANT')
key(keys_, 'location', (0, 0, -100), 1, 'CONSTANT'); key(keys_, 'location', (0, 0.1, 0), 493, 'CONSTANT'); key(keys_, 'rotation_euler', (0, 0, 0), 1, 'CONSTANT')
P(rM, 505, ARMS_REST, TIRED, {'upper_arm.L': (-30, 0, 20), 'forearm.L': (-75, 0, 0), 'spine': (2, 0, 8)})
P(rM, 508, ARMS_REST, TIRED, {'upper_arm.L': (-100, -10, 40), 'forearm.L': (-8, 0, 0), 'spine': (8, 0, -10), 'head': (6, 0, -14)})
P(rM, 513, ARMS_REST, TIRED, {'upper_arm.L': (-35, -5, 15), 'forearm.L': (-18, 0, 0), 'head': (6, 0, -6)})
look_world(rM, 505, AZ(-15.05, 5.3, 0.8)); look_world(rM, 515, AZ(-15.05, 5.3, 0.8)); look_rel(rM, 520, (0, 0.2, -0.1))
key(keys_, 'location', AZ(-14.1, 4.9, 1.3), 509); key(keys_, 'location', AZ(-14.7, 5.2, 1.18), 511)
key(keys_, 'location', AZ(-15.0, 5.3, 0.83), 513); key(keys_, 'location', AZ(-15.1, 5.35, 0.9), 514); key(keys_, 'location', AZ(-15.15, 5.4, 0.805), 516)
key(keys_, 'rotation_euler', (0, 0, 0), 509); key(keys_, 'rotation_euler', (rad(200), rad(40), rad(90)), 513); key(keys_, 'rotation_euler', (rad(270), rad(10), rad(110)), 516)
walk(rM, 513, 521, TIRED, period=8, amp=22)
root(rM, AZ(-13.6, 3.3, 0), yaw(-1, 0.5), 518)
root(rM, AZ(-13.3, 2.4, 0), yaw(-1, 0), 521)
P(rM, 522, ARMS_REST, CROUCH, {'upper_arm.L': (22, -15, 0), 'upper_arm.R': (22, 15, 0)})
root(rM, AZ(-12.85, 2.3, -0.02), yaw(-1, 0), 524, scale=(0.95, 0.95, 1.08))
P(rM, 525, SIT_SOFA, {'spine': (-24, 0, 0), 'upper_arm.L': (-55, -40, 0), 'upper_arm.R': (-55, 40, 0), 'thigh.L': (-60, 0, -8), 'thigh.R': (-60, 0, 8)})
root(rM, AZ(-12.1, 2.2, -0.33), yaw(-1, 0), 527, scale=(1.1, 1.1, 0.84))
P(rM, 527, SIT_SOFA, {'spine': (-20, 0, 0), 'upper_arm.L': (-30, -35, 0), 'upper_arm.R': (-30, 35, 0)})
root(rM, AZ(-12.05, 2.2, -0.28), yaw(-1, 0), 531, scale=(0.97, 0.97, 1.04))
root(rM, AZ(-12.05, 2.2, -0.29), yaw(-1, 0), 536, scale=(1, 1, 1))
P(rM, 532, SIT_SOFA)
for nm, amt in (('ENV_Apartamento_Sofa_Assento_0', 0.8), ('ENV_Apartamento_Sofa_Assento_1', 0.55), ('ENV_Apartamento_Sofa_Assento_2', 0.8), ('ENV_Apartamento_Sofa_Costas_1', 0.85)):
    o_ = D.objects[nm]
    key(o_, 'scale', (1, 1, 1), 525); key(o_, 'scale', (1 + (1 - amt) * 0.3, 1 + (1 - amt) * 0.3, amt), 528)
    key(o_, 'scale', (0.98, 0.98, 1.06), 531); key(o_, 'scale', (1, 1, 1), 536)
for nm, amt in (('ENV_Apartamento_Almofada_L', 14), ('ENV_Apartamento_Almofada_R', -14)):
    o_ = D.objects[nm]; z0_ = o_.rotation_euler.z; ex_, ey_ = o_.rotation_euler.x, o_.rotation_euler.y
    key(o_, 'rotation_euler', None, 525); key(o_, 'rotation_euler', (ex_, ey_, z0_ + rad(amt)), 530); key(o_, 'rotation_euler', (ex_, ey_, z0_), 538)
for f, a_ in ((520, 0), (524, -30), (526, 40), (529, -25), (533, 15), (537, -5), (541, 0)):
    pose_only(rM, {'tie': (a_, 0, 0)}, f)
P(rM, 534, SIT_SOFA, {'upper_arm.R': (-15, 30, 0), 'forearm.R': (-25, 0, 0), 'head': (12, 0, -10)})
look_rel(rM, 530, (0, 0.2, 0)); look_world(rM, 536, REMOTE_SEAT); look_world(rM, 540, AZ(-15.38, 2.2, 1.35))
rc = remote.constraints.new('CHILD_OF'); rc.name = 'NaMao'; rc.target = rM; rc.subtarget = 'hand_fk.R'
rc.inverse_matrix = Matrix.Identity(4); rc.set_inverse_pending = False
key(rc, 'influence', 0.0, 1, 'CONSTANT'); key(rc, 'influence', 1.0, 535, 'CONSTANT'); key(rc, 'influence', 0.0, 627, 'CONSTANT')
key(remote, 'location', REMOTE_SEAT, 1, 'CONSTANT'); key(remote, 'rotation_euler', (0, 0, 0), 1, 'CONSTANT')
key(remote, 'location', (0, 0.08, 0.0), 535, 'CONSTANT'); key(remote, 'rotation_euler', (0, 0, 0), 535, 'CONSTANT')
key(remote, 'location', AZ(-11.78, 2.85, 0.515), 627, 'CONSTANT'); key(remote, 'rotation_euler', (0, 0, rad(25)), 627, 'CONSTANT')
AIM = {'upper_arm.R': (-70, 0, -8), 'forearm.R': (-12, 0, 0), 'hand.R': (-5, 0, 0), **GRIP_R, 'head': (6, 0, 0)}
P(rM, 538, SIT_SOFA, AIM); P(rM, 541, SIT_SOFA, AIM)
blink(fM, 532, 8)
HOLD = {'upper_arm.R': (-28, 10, 0), 'forearm.R': (-55, 0, 0), **GRIP_R}
P(rM, 553, SIT_SOFA, HOLD); P(rM, 600, SIT_SOFA, HOLD, {'spine': (-14, 0, 0), 'head': (12, 0, 0)})
blink(fM, 567, 10); blink(fM, 591, 10)
look_world(rM, 545, AZ(-15.38, 2.2, 1.35)); look_world(rM, 575, AZ(-15.38, 2.2, 1.2)); look_world(rM, 600, AZ(-15.38, 2.2, 1.0))
P(rM, 604, SIT_SOFA, HOLD, {'spine': (-14, 0, 0), 'head': (12, 0, 0)})
P(rM, 610, SIT_SOFA, AIM, {'spine': (-14, 0, 0)}); P(rM, 614, SIT_SOFA, AIM, {'spine': (-14, 0, 0), 'hand.R': (-12, 0, 0)})
look_world(rM, 614, AZ(-15.38, 2.2, 1.2)); look_rel(rM, 622, (0, 0.2, -0.3))
blink(fM, 617, 10)
P(rM, 620, SIT_SOFA, AIM, {'spine': (-14, 0, 0)})
P(rM, 628, SIT_SOFA, {'upper_arm.R': (-12, 18, 0), 'forearm.R': (-20, 0, 0), 'spine': (-16, 0, 0), 'head': (12, 0, 0)})
P(rM, 640, SIT_SOFA, {'upper_arm.R': (-12, 18, 0), 'forearm.R': (-20, 0, 0), 'spine': (-16, 0, 0), 'head': (12, 0, 0)})
sk(fM, 'eyes_closed', 0.0, 640, 'LINEAR'); sk(fM, 'eyes_closed', 1.0, 660)
sk(fM, 'brow_sad', 0.7, 640); sk(fM, 'brow_sad', 0.3, 690)
sk(fM, 'mouth_frown', 0.6, 640); sk(fM, 'mouth_frown', 0.2, 690)
sk(fM, 'sigh', 0.0, 662); sk(fM, 'sigh', 1.0, 670); sk(fM, 'sigh', 1.0, 674); sk(fM, 'sigh', 0.0, 684)
P(rM, 668, SIT_SOFA, {'upper_arm.R': (-12, 18, 0), 'forearm.R': (-20, 0, 0), 'spine': (-18, 0, 0), 'chest': (-14, 0, 0), 'head': (6, 0, 0)})
P(rM, 684, SIT_SOFA, {'upper_arm.R': (-12, 18, 0), 'forearm.R': (-20, 0, 0), 'spine': (-15, 0, 0), 'chest': (-3, 0, 0), 'head': (14, 0, 0)})
P(rM, 702, SIT_SOFA, {'upper_arm.R': (-10, 20, 0), 'forearm.R': (-18, 0, 0), 'spine': (-12, 0, 0), 'chest': (2, 0, 0), 'neck': (22, 0, 0), 'head': (22, 0, 12)})
P(rM, 720, SIT_SOFA, {'upper_arm.R': (-10, 20, 0), 'forearm.R': (-18, 0, 0), 'spine': (-12, 0, 0), 'chest': (2, 0, 0), 'neck': (24, 0, 0), 'head': (24, 0, 14)})
key_vis(tv_off, 1, True); key_vis(tv_off, 538, False); key_vis(tv_off, 615, True)
key_vis(tv_flash, 1, False); key_vis(tv_flash, 614, True); key_vis(tv_flash, 615, False)
