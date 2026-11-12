# ================================================================ PLANOS 01-03: FILA REAL
# Os 4 carros da fila (Fila1..4) entram de verdade pela cancela da ENTRADA e estacionam nas vagas livres: V4, V5, V2, V1.
# Claudio já está na V3; Marcos (último da fila) fica com a V6. Trajetos por arcos de 4 m, velocidade com aceleração/frenagem.
ROAD_Z = -0.15
V_IN, RAMP, R_ARC = 0.30, 8, 4.0

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

SCHED = {}
f_start = 18; prev_info = None
for nm in ('Fila1', 'Fila2', 'Fila3', 'Fila4'):
    (p0, mode) = START[nm]; kind, ys = SPOTS[nm]
    xf = final_x_right(LENS[nm]) if kind == 'R' else (CENT_X0 + CENT_X1) / 2
    head = lane_curve(p0[0]) if mode == 'lane' else ([p0] if p0[1] > -10 else [p0, (ENTR_CX, -12.0), (ENTR_CX, -9.95)])
    pts = head + COMMON[1:] + spot_tail(kind, ys, xf)
    car = CARS[nm]; r_ = car['root']; r_.rotation_mode = 'XYZ'
    rot0 = 90 if mode == 'lane' else 0
    root(r_, (p0[0], p0[1], z_of(p0[1])), rot0, 1, 'CONSTANT')
    if prev_info:      # parte quando o carro da frente já andou 3,5 m
        f_start = prev_info[0] + time_for(prev_info[1], V_IN, RAMP, 3.5)
    f_end, S, dens, ds = drive(car, pts, int(round(f_start)))
    SCHED[nm] = dict(f0=int(round(f_start)), f_end=f_end, S=S, dens=dens, ds=ds)
    prev_info = (int(round(f_start)), S)
    # luzes: freio aceso enquanto espera, apagado em movimento, aceso ao parar; faróis até estacionar
    br = bsdf(car['brake']).inputs['Emission Strength']; hd = bsdf(car['head']).inputs['Emission Strength']
    f = 1; on = True
    while f < int(round(f_start)) - 2:
        key(br, 'default_value', 8.0 if on else 0.7, f, 'CONSTANT'); f += random.randint(14, 30) if on else random.randint(4, 8); on = not on
    key(br, 'default_value', 0.6, int(round(f_start)), 'CONSTANT'); key(br, 'default_value', 8.0, f_end - 4, 'CONSTANT'); key(br, 'default_value', 0.0, f_end + 12, 'CONSTANT')
    key(hd, 'default_value', 3.0, 1, 'CONSTANT'); key(hd, 'default_value', 0.0, f_end + 14, 'CONSTANT')
    suspension(car, int(round(f_start)) - 1, f_end + 14, 0.5)
    odometer(car, int(round(f_start)) - 1, f_end + 14)
SCHED_PRINT = {k: (v['f0'], v['f_end']) for k, v in SCHED.items()}
# a cancela fica aberta enquanto a fila passa e fecha em seguida; só reabre para o Marcos (164-196)
f_gate_last = int(frame_when_y(SCHED['Fila4']['f0'], SCHED['Fila4']['S'], V_IN, RAMP, SCHED['Fila4']['dens'], SCHED['Fila4']['ds'], -4.6))
f_close0 = min(f_gate_last + 3, 136)

# ---- Carro do Marcos: último da fila; avança conforme a fila anda; para na cancela; entra; estaciona na V6
brM = bsdf(CARS['Marcos']['brake']).inputs['Emission Strength']; hdM = bsdf(CARS['Marcos']['head']).inputs['Emission Strength']
key(brM, 'default_value', 8.0, 1, 'CONSTANT'); key(brM, 'default_value', 0.6, SCHED['Fila4']['f0'] + 8, 'CONSTANT')
key(brM, 'default_value', 8.0, 146, 'CONSTANT'); key(brM, 'default_value', 0.0, 199, 'CONSTANT'); key(brM, 'default_value', 8.0, 242, 'CONSTANT')
key(hdM, 'default_value', 4.0, 1, 'CONSTANT'); key(hdM, 'default_value', 0.0, 246, 'CONSTANT')
carM.rotation_mode = 'XYZ'
def carkey(f, loc_, rz=0, interp=None):
    key(carM, 'location', loc_, f, interp); key(carM, 'rotation_euler', (0, 0, rad(rz)), f, interp)
MX0 = 20.1; t4 = SCHED['Fila4']['f0']
carkey(1, (MX0, LANE_Y, ROAD_Z), 90, interp='CONSTANT')
carkey(t4 + 10, (MX0, LANE_Y, ROAD_Z), 90)                  # espera a fila andar...
carkey(t4 + 52, (8.9, LANE_Y, ROAD_Z), 90)                  # ...e avança devagar até o ponto de entrada
carkey(145, (8.9, LANE_Y, ROAD_Z), 90)
carkey(151, (7.3, LANE_Y + 0.1, ROAD_Z), 76)
carkey(157, (6.4, -16.5, -0.1), 34)
carkey(163, (ENTR_CX, -14.4, -0.04), 5)
carkey(169, (ENTR_CX, -11.6, 0.0), 0)
carkey(176, (ENTR_CX, -10.0, 0.0), 0)                        # para na cancela fechada (passa pelo sensor S2)
carkey(186, (ENTR_CX, -10.0, 0.0), 0)
carkey(194, (ENTR_CX, -6.6, 0.0), 0)                         # cancela subiu: avança
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
suspension(CARS['Marcos'], t4 + 8, 247)
odometer(CARS['Marcos'], 1, 250)
# Porta do motorista: o vão até o carro da V5 é curto -> abre 24°
dp = CARS['Marcos']['door']; dp.rotation_mode = 'XYZ'
key(dp, 'rotation_euler', (0, 0, 0), 243); key(dp, 'rotation_euler', (0, 0, rad(-24)), 247)
key(dp, 'rotation_euler', (0, 0, rad(-24)), 249); key(dp, 'rotation_euler', (0, 0, rad(2)), 251); key(dp, 'rotation_euler', (0, 0, 0), 253)

# ---- Cancela C2 (braço aponta -X; rotação em Y POSITIVA levanta). 1) abre devagar para a fila; 2) fecha; 3) reabre para o Marcos
key(C2, 'rotation_euler', (0, 0, 0), 1, 'CONSTANT'); key(C2, 'rotation_euler', (0, 0, 0), 8, 'LINEAR')
key(C2, 'rotation_euler', (0, rad(78), 0), 30); key(C2, 'rotation_euler', (0, rad(88), 0), 32); key(C2, 'rotation_euler', (0, rad(85), 0), 34)
key(C2, 'rotation_euler', (0, rad(85), 0), f_close0)
key(C2, 'rotation_euler', (0, 0, 0), f_close0 + 24)
key(C2, 'rotation_euler', (0, 0, 0), 164, 'LINEAR')
key(C2, 'rotation_euler', (0, rad(78), 0), 192)
key(C2, 'rotation_euler', (0, rad(88), 0), 194)
key(C2, 'rotation_euler', (0, rad(85), 0), 196)
key(C1, 'rotation_euler', (0, 0, 0), 1, 'CONSTANT')
pb_ = D.objects['MQ_Guarita_Porteiro_Braco']; p0_ = pb_.location.copy()
press = (4, 12, f_close0 - 2, f_close0 + 6, 150, 160, 166, 176)
for a_, b_ in ((press[0], press[1]), (press[2], press[3]), (press[4], press[5])):
    key(pb_, 'location', p0_, a_ - 2); key(pb_, 'location', (p0_.x + 0.05, p0_.y - 0.25, p0_.z - 0.2), a_ + 6)
    key(pb_, 'location', (p0_.x + 0.05, p0_.y - 0.25, p0_.z - 0.2), b_); key(pb_, 'location', p0_, b_ + 10)
btn = D.objects['MQ_Guarita_Botao']; bm_ = bsdf(btn.data.materials[0]).inputs['Emission Strength']
key(bm_, 'default_value', 1.8, 1, 'CONSTANT')
for a_ in (6, f_close0, 162): key(bm_, 'default_value', 7.0, a_, 'CONSTANT'); key(bm_, 'default_value', 1.8, a_ + 10, 'CONSTANT')

