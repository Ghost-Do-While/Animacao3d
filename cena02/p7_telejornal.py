# Parte 7 - SET_Telejornal: estúdio de TV 3D completo (cena SCN_Telejornal, a 500 m de distância, fora da luz do condomínio)
# CAM_TV_Jornal é renderizada em sequência de imagens (render_telejornal.py) e vira a textura animada da tela da TV (p1c_apto.py).
NS = D.scenes.new('SCN_Telejornal')
cSet = D.collections.new('SET_Telejornal'); NS.collection.children.link(cSet)
NEWS_FRAMES = 103                       # = frames 538..640 da cena principal
OX = 500.0                              # estúdio em X = 500 m
def S_(x, y, z=0.0): return (OX + x, y, z)

# ------------------------------------------------ geometria auxiliar (cápsula/elipsoide) e rosto, em escala de estúdio
def _us(u, v):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    vs = [vv.co.copy() for vv in bm.verts]; fs = [[vv.index for vv in f.verts] for f in bm.faces]; bm.free(); return vs, fs
US_B = _us(32, 16); US_S = _us(16, 10)
def _MM(c, r, rot=(0, 0, 0)):
    return (Matrix.Translation(Vector(c)) @ Euler([rad(a) for a in rot], 'XYZ').to_matrix().to_4x4() @ Matrix.Diagonal((r[0], r[1], r[2], 1)))
def add_capsule_(bm, a, b, ra, rb, mi, segs=16, rings=10):
    a = Vector(a); b = Vector(b); d = b - a; L = d.length; q = Vector((0, 0, 1)).rotation_difference(d)
    res = bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0); fs = set()
    for v in res['verts']:
        x, y, z = v.co
        loc = Vector((x * ra, y * ra, z * ra)) if z < -1e-6 else Vector((x * rb, y * rb, L + z * rb))
        v.co = a + q @ loc; fs.update(v.link_faces)
    for f in fs: f.material_index = mi; f.smooth = True
def add_ell_(bm, c, r, mi, rot=None, segs=(20, 12)):
    res = bmesh.ops.create_uvsphere(bm, u_segments=segs[0], v_segments=segs[1], radius=1.0)
    Rm = rot.to_matrix() if rot is not None else Matrix.Identity(3); fs = set()
    for v in res['verts']:
        v.co = Vector(c) + Rm @ Vector((v.co.x * r[0], v.co.y * r[1], v.co.z * r[2])); fs.update(v.link_faces)
    for f in fs: f.material_index = mi; f.smooth = True
def emat2(name, hx, s=2.0):
    m_ = new_mat(name, principled=False); nt_ = m_.node_tree
    e_ = nt_.nodes.new('ShaderNodeEmission'); e_.inputs['Color'].default_value = (*hexc(hx), 1); e_.inputs['Strength'].default_value = s
    nt_.links.new(e_.outputs[0], mat_out(m_).inputs['Surface']); return m_

# ------------------------------------------------ materiais do estúdio (saturados, brilhantes)
m_floor = mat('MAT_TJ_Piso', hexc('#101C44'), 0.06, 0.2)
m_deskTop = mat('MAT_TJ_BancadaTampo', hexc('#F4F6FF'), 0.08, 0.1, coat=0.8)
m_deskFront = mat('MAT_TJ_BancadaFrente', hexc('#16286A'), 0.15, 0.3)
m_led_b = emat2('MAT_TJ_LED_Azul', '#2F7BFF', 9.0)
m_led_r = emat2('MAT_TJ_LED_Verm', '#FF3B4A', 8.0)
m_led_w = emat2('MAT_TJ_LED_Branco', '#FFFFFF', 7.0)
m_logo = emat2('MAT_TJ_Logo', '#FFFFFF', 5.0)
m_wall_frame = mat('MAT_TJ_Moldura', hexc('#0A0F24'), 0.2, 0.6)
m_glass = mat('MAT_TJ_Vidro', hexc('#5C8CFF'), 0.03, alpha=0.18)
m_suit = mat('MAT_TJ_Blazer', hexc('#C2257A'), 0.55, sss=0.1)
m_shirt = mat('MAT_TJ_Blusa', hexc('#FFF4EA'), 0.6)
m_skinA = mat('MAT_TJ_Pele', hexc('#E8A682'), 0.5, sss=0.2)
m_hairA = mat('MAT_TJ_Cabelo', hexc('#3A1E14'), 0.35)
m_paper = mat('MAT_TJ_Papel', hexc('#FFFFFF'), 0.7)
m_mug = mat('MAT_TJ_Caneca', hexc('#FFC93A'), 0.35)
m_metal2 = mat('MAT_TJ_Metal', hexc('#C8CFE0'), 0.2, 1.0)
m_chair = mat('MAT_TJ_Cadeira', hexc('#1C2350'), 0.5)
m_eyew = mat('MAT_TJ_Olho', hexc('#FFFFFF'), 0.12); m_pup = mat('MAT_TJ_Pupila', hexc('#2A160C'), 0.1); m_lip = mat('MAT_TJ_Labio', hexc('#C8404E'), 0.4)

# ------------------------------------------------ cenário: piso refletivo, painel de vidro com skyline, telão (video wall), luzes LED de contorno
box('TJ_Piso', (40, 40, 0.1), S_(0, 6, -0.05), m_floor, cSet, bevel=0)
box('TJ_FundoEscuro', (36, 0.3, 14), S_(0, 11.5, 7), mat('MAT_TJ_Fundo', hexc('#0C1236'), 0.5), cSet, bevel=0)
# painel de vidro com skyline (prédios com janelas acesas) ao fundo
box('TJ_Vidro', (14, 0.06, 5.0), S_(0, 9.9, 3.2), m_glass, cSet, bevel=0)
box('TJ_Vidro_Moldura_Topo', (14.2, 0.14, 0.14), S_(0, 9.88, 5.75), m_wall_frame, cSet)
box('TJ_Vidro_Moldura_Base', (14.2, 0.14, 0.14), S_(0, 9.88, 0.7), m_wall_frame, cSet)
random.seed(21)
m_win = emat2('MAT_TJ_JanelaSky', '#FFC96A', 6.0); m_bld = mat('MAT_TJ_PredioSky', hexc('#141B44'), 0.6)
x = -6.8
while x < 6.8:
    w_ = random.uniform(0.7, 1.4); h_ = random.uniform(1.2, 3.8)
    box(f'TJ_Sky_{int((x+7)*10)}', (w_, 0.3, h_), S_(x + w_ / 2, 10.2, 0.8 + h_ / 2), m_bld, cSet)
    for fl in range(int(h_ / 0.45)):
        for j in range(max(1, int(w_ / 0.35))):
            if random.random() < 0.55:
                box(f'TJ_SkyJ_{int((x+7)*10)}_{fl}_{j}', (0.14, 0.04, 0.2), S_(x + 0.2 + j * 0.3, 10.03, 1.1 + fl * 0.45), m_win, cSet, bevel=0)
    x += w_ + random.uniform(0.05, 0.25)
# telão de LED (video wall) com mapa da cidade animado
WALL_C = S_(3.4, 9.5, 3.1); WW, WH = 5.2, 2.9
m_vw = new_mat('MAT_TJ_Telao', principled=False); nt = m_vw.node_tree
tcn = nt.nodes.new('ShaderNodeTexCoord'); vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.feature = 'DISTANCE_TO_EDGE'; vor.inputs['Scale'].default_value = 9.0
mp = nt.nodes.new('ShaderNodeMapping'); nt.links.new(tcn.outputs['Generated'], mp.inputs['Vector']); nt.links.new(mp.outputs[0], vor.inputs['Vector'])
vw_w = vor.inputs['W'] if 'W' in vor.inputs else None
rmp = nt.nodes.new('ShaderNodeValToRGB'); rmp.color_ramp.interpolation = 'LINEAR'
rmp.color_ramp.elements[0].position = 0.0; rmp.color_ramp.elements[0].color = (*hexc('#4FD0FF'), 1)
rmp.color_ramp.elements[1].position = 0.12; rmp.color_ramp.elements[1].color = (*hexc('#0B2A7A'), 1)
nt.links.new(vor.outputs['Distance'], rmp.inputs[0])
grad = nt.nodes.new('ShaderNodeTexGradient'); mix2 = nt.nodes.new('ShaderNodeMix'); mix2.data_type = 'RGBA'; mix2.blend_type = 'ADD'; sock(mix2.inputs, 'Factor').default_value = 0.35
nt.links.new(tcn.outputs['Generated'], grad.inputs['Vector']); nt.links.new(rmp.outputs['Color'], sock(mix2.inputs, 'A')); nt.links.new(grad.outputs['Color'], sock(mix2.inputs, 'B'))
emv = nt.nodes.new('ShaderNodeEmission'); emv.inputs['Strength'].default_value = 2.2
nt.links.new(sock(mix2.outputs, 'Result'), emv.inputs['Color']); nt.links.new(emv.outputs[0], mat_out(m_vw).inputs['Surface'])
vwall = box('TJ_Telao', (WW, 0.08, WH), WALL_C, m_vw, cSet, bevel=0)
mp.inputs['Location'].default_value = (0, 0, 0)
key(mp.inputs['Location'], 'default_value', (0.0, 0.0, 0.0), 1); key(mp.inputs['Location'], 'default_value', (0.08, 0.04, 0.0), NEWS_FRAMES)
box('TJ_Telao_Moldura', (WW + 0.3, 0.14, WH + 0.3), (WALL_C[0], WALL_C[1] + 0.05, WALL_C[2]), m_wall_frame, cSet)
# "imagens" no telão: viatura + garagem (montagem plana emissiva, só visível no plano 2)
e_navy = emat2('MAT_TJ_Art_Azul', '#0E2A7A', 1.6); e_asph = emat2('MAT_TJ_Art_Asfalto', '#1A1E34', 1.2); e_garg = emat2('MAT_TJ_Art_Garagem', '#8A93B8', 1.8)
e_white = emat2('MAT_TJ_Art_Branco', '#F4F6FF', 2.4); e_sirB = emat2('MAT_TJ_Art_SireneAzul', '#2A6BFF', 9.0); e_sirR = emat2('MAT_TJ_Art_SireneVerm', '#FF2A3A', 9.0)
e_black = emat2('MAT_TJ_Art_Preto', '#0A0A12', 1.0); e_yel = emat2('MAT_TJ_Art_Amarelo', '#FFC62B', 2.8); e_sky = emat2('MAT_TJ_Art_Ceu', '#E8884A', 1.8)
art = []
def ap(nm, size, x, z, m_, dy=0.0):
    o = box(f'TJ_Art_{nm}', (size[0], 0.02, size[1]), (WALL_C[0] + x, WALL_C[1] - 0.06 - dy, WALL_C[2] + z), m_, cSet, bevel=0); art.append(o); return o
ap('Fundo', (WW - 0.2, WH - 0.2), 0, 0, e_sky)
ap('Garagem', (2.3, 1.5), -1.0, 0.1, e_garg, 0.005)
ap('Garagem_Porta', (1.5, 1.0), -1.0, -0.1, e_black, 0.01)
ap('Garagem_Placa', (0.6, 0.35), -1.0, 0.65, e_yel, 0.01)
ap('Chao', (WW - 0.2, 0.7), 0, -1.05, e_asph, 0.005)
ap('Viatura_Corpo', (2.2, 0.62), 1.2, -0.55, e_white, 0.012)
ap('Viatura_Cabine', (1.1, 0.5), 1.0, -0.08, e_white, 0.013)
ap('Viatura_Faixa', (2.2, 0.16), 1.2, -0.6, e_navy, 0.014)
ap('Viatura_Vidro', (0.9, 0.34), 1.0, -0.06, e_navy, 0.014)
ap('Viatura_SireneA', (0.3, 0.14), 0.75, 0.22, e_sirB, 0.015)
ap('Viatura_SireneV', (0.3, 0.14), 1.2, 0.22, e_sirR, 0.015)
ap('Viatura_RodaE', (0.5, 0.5), 0.45, -0.95, e_black, 0.013)
ap('Viatura_RodaD', (0.5, 0.5), 1.95, -0.95, e_black, 0.013)
for o_ in art: o_.hide_render = True
for o_ in art: key(o_, 'hide_render', True, 1, 'CONSTANT'); key(o_, 'hide_render', False, 57, 'CONSTANT')
# sirene piscando
for o_ in (D.objects['TJ_Art_Viatura_SireneA'], D.objects['TJ_Art_Viatura_SireneV']):
    b_ = bsdf(o_.data.materials[0]) if bsdf(o_.data.materials[0]) else None
for f in range(57, NEWS_FRAMES, 4):
    for nm, on in (('MAT_TJ_Art_SireneAzul', (f // 4) % 2 == 0), ('MAT_TJ_Art_SireneVerm', (f // 4) % 2 == 1)):
        em_ = next(n for n in D.materials[nm].node_tree.nodes if n.type == 'EMISSION'); key(em_.inputs['Strength'], 'default_value', 9.0 if on else 0.6, f, 'CONSTANT')

# bancada de apresentadores curva (arco de 11 segmentos), tampo brilhante, logo iluminado e LED de contorno
R_ARC = 4.2; N_SEG = 11
for i in range(N_SEG):
    a = rad(-36 + i * 72 / (N_SEG - 1)); cx = R_ARC * math.sin(a); cy = 5.2 - R_ARC * math.cos(a) + R_ARC * 0.25
    seg_w = 2 * R_ARC * math.tan(rad(72 / (N_SEG - 1) / 2)) * 1.08
    top = box(f'TJ_Bancada_Tampo_{i}', (seg_w, 1.1, 0.07), S_(cx, cy, 1.0), m_deskTop, cSet, rot=(0, 0, -math.degrees(a)), bevel=0.012)
    box(f'TJ_Bancada_Frente_{i}', (seg_w, 0.16, 0.98), S_(cx + 0.0 + math.sin(a) * 0.0, cy - 0.5 * math.cos(a), 0.49), m_deskFront, cSet, rot=(0, 0, -math.degrees(a)), bevel=0.02)
    box(f'TJ_Bancada_LED_{i}', (seg_w, 0.03, 0.04), S_(cx, cy - 0.58 * math.cos(a), 1.0), m_led_b, cSet, rot=(0, 0, -math.degrees(a)), bevel=0)
    box(f'TJ_Bancada_LEDbase_{i}', (seg_w, 0.03, 0.04), S_(cx, cy - 0.58 * math.cos(a), 0.06), m_led_r, cSet, rot=(0, 0, -math.degrees(a)), bevel=0)
# logo da emissora na frente da bancada
box('TJ_Logo_Placa', (2.8, 0.05, 0.62), S_(0, 5.2 - R_ARC + R_ARC * 0.25 - 0.62, 0.55), mat('MAT_TJ_LogoFundo', hexc('#0A1A5A'), 0.3), cSet, bevel=0.02)
text('TJ_Logo_Texto', 'JORNAL DA CIDADE', 0.2, S_(0.2, 5.2 - R_ARC + R_ARC * 0.25 - 0.66, 0.52), (90, 0, 0), m_logo, cSet, extrude=0.01)
cyl('TJ_Logo_Globo', 0.2, 0.03, S_(-1.05, 5.2 - R_ARC + R_ARC * 0.25 - 0.66, 0.55), mat('MAT_TJ_Globo', hexc('#FF3B4A'), 0.3, emit=hexc('#FF3B4A'), emit_str=5.0), cSet, rot=(90, 0, 0), segs=28)
# props da bancada: monitor, papéis, caneca, microfone de lapela/mesa
DESK_Y = 5.2 - R_ARC + R_ARC * 0.25           # y do centro da bancada (a = 0)
box('TJ_Monitor', (0.9, 0.05, 0.55), S_(1.5, DESK_Y + 0.25, 1.4), mat('MAT_TJ_MonitorTela', hexc('#0A1A5A'), 0.3, emit=hexc('#4FD0FF'), emit_str=2.0), cSet, rot=(-8, 0, -10))
box('TJ_Monitor_Pe', (0.1, 0.1, 0.25), S_(1.5, DESK_Y + 0.3, 1.1), m_metal2, cSet)
for i in range(3):
    box(f'TJ_Papel_{i}', (0.32, 0.24, 0.012), S_(-0.15 - i * 0.04, DESK_Y - 0.05 + i * 0.02, 1.04 + i * 0.012), m_paper, cSet, rot=(0, 0, 8 - 6 * i), bevel=0.003)
cyl('TJ_Caneca', 0.06, 0.12, S_(-0.9, DESK_Y + 0.08, 1.1), m_mug, cSet, segs=20)
cyl('TJ_Mic_Haste', 0.01, 0.2, S_(0.45, DESK_Y - 0.28, 1.15), m_metal2, cSet, segs=8)
sphere('TJ_Mic_Cabeca', (0.03, 0.03, 0.05), S_(0.45, DESK_Y - 0.28, 1.27), m_metal2, cSet, segs=(14, 10))

# ------------------------------------------------ âncora (mesma linguagem dos personagens): blazer, mãos sobre os papéis, rosto expressivo
AC = Vector(S_(0.1, DESK_Y + 0.62, 0.0))         # eixo da âncora (atrás da bancada)
anchor = empty('TJ_Ancora', tuple(AC), cSet, 0.4, 'ARROWS')
bm = bmesh.new()
add_ell_(bm, (0, 0, 1.15), (0.27, 0.15, 0.31), 0)                      # tronco
add_ell_(bm, (0, 0, 0.82), (0.25, 0.17, 0.2), 0)
add_capsule_(bm, (0, 0, 1.38), (0, -0.01, 1.50), 0.055, 0.05, 1)       # pescoço (pele)
for sg in (-1, 1):
    add_ell_(bm, (sg * 0.28, 0, 1.38), (0.1, 0.1, 0.1), 0)           # ombros
    add_capsule_(bm, (sg * 0.29, 0, 1.36), (sg * 0.30, -0.3, 1.1), 0.07, 0.06, 0)   # braços até a mesa
    add_capsule_(bm, (sg * 0.30, -0.3, 1.1), (sg * 0.15, -0.5, 1.07), 0.06, 0.05, 0)
    add_ell_(bm, (sg * 0.14, -0.55, 1.07), (0.075, 0.09, 0.04), 1)   # mãos
add_ell_(bm, (0, -0.1, 1.28), (0.07, 0.04, 0.12), 2)                   # blusa/gola
body_a = bm_obj('TJ_Ancora_Corpo', bm, cSet, [m_suit, m_skinA, m_shirt]); body_a.data.shade_smooth()
set_parent(body_a, anchor)
# cadeira atrás
box('TJ_Cadeira_Encosto', (0.6, 0.12, 0.7), S_(0.1, DESK_Y + 0.95, 1.1), m_chair, cSet, bevel=0.06)
cyl('TJ_Cadeira_Haste', 0.04, 0.5, S_(0.1, DESK_Y + 0.85, 0.35), m_metal2, cSet, segs=12)
# cabeça com shape keys (visemas, piscada, sobrancelhas, sorriso)
Sf = 1.0; HC = Vector((0, -0.02, 1.7))
def fparts():
    h = lambda v: tuple(x * Sf for x in v)
    return [('cranio', (0, 0, 0), h((0.14, 0.145, 0.165)), (0, 0, 0), 0, True),
            ('bochecha_L', h((0.075, -0.1, -0.05)), h((0.05, 0.04, 0.04)), (0, 0, 0), 0, False), ('bochecha_R', h((-0.075, -0.1, -0.05)), h((0.05, 0.04, 0.04)), (0, 0, 0), 0, False),
            ('orelha_L', h((0.14, 0, 0)), h((0.022, 0.035, 0.045)), (0, 0, 0), 0, False), ('orelha_R', h((-0.14, 0, 0)), h((0.022, 0.035, 0.045)), (0, 0, 0), 0, False),
            ('nariz', h((0, -0.15, -0.01)), h((0.022, 0.028, 0.032)), (0, 0, 0), 0, False),
            ('olho_L', h((0.055, -0.12, 0.025)), h((0.032, 0.032, 0.032)), (0, 0, 0), 1, False), ('olho_R', h((-0.055, -0.12, 0.025)), h((0.032, 0.032, 0.032)), (0, 0, 0), 1, False),
            ('pupila_L', h((0.055, -0.149, 0.025)), h((0.015, 0.008, 0.016)), (0, 0, 0), 2, False), ('pupila_R', h((-0.055, -0.149, 0.025)), h((0.015, 0.008, 0.016)), (0, 0, 0), 2, False),
            ('palpebra_L', h((0.055, -0.121, 0.062)), h((0.037, 0.036, 0.012)), (0, 0, 0), 0, False), ('palpebra_R', h((-0.055, -0.121, 0.062)), h((0.037, 0.036, 0.012)), (0, 0, 0), 0, False),
            ('sobrancelha_L', h((0.055, -0.142, 0.085)), h((0.032, 0.008, 0.006)), (0, 8, 0), 3, False), ('sobrancelha_R', h((-0.055, -0.142, 0.085)), h((0.032, 0.008, 0.006)), (0, -8, 0), 3, False),
            ('boca', h((0, -0.135, -0.07)), h((0.03, 0.012, 0.007)), (0, 0, 0), 4, False),
            ('canto_L', h((0.03, -0.132, -0.07)), h((0.008, 0.008, 0.008)), (0, 0, 0), 4, False), ('canto_R', h((-0.03, -0.132, -0.07)), h((0.008, 0.008, 0.008)), (0, 0, 0), 4, False)]
parts = fparts(); pd = {p[0]: p for p in parts}
def ovr(pn, dc=(0, 0, 0), sr=(1, 1, 1), rot=None):
    p = pd[pn]; return (tuple(p[1][i] + dc[i] for i in range(3)), tuple(p[2][i] * sr[i] for i in range(3)), rot if rot is not None else p[3])
def mth(sx_, sz_, dz=0.0, dy=0.0, cdz=0.0):
    w = pd['boca'][2][0] * sx_
    return {'boca': ovr('boca', (0, dy, dz), (sx_, 1.0, sz_)), 'canto_L': ((w, pd['canto_L'][1][1] + dy, pd['canto_L'][1][2] + dz + cdz), pd['canto_L'][2], (0, 0, 0)),
            'canto_R': ((-w, pd['canto_R'][1][1] + dy, pd['canto_R'][1][2] + dz + cdz), pd['canto_R'][2], (0, 0, 0))}
def lidk():
    d = {}
    for s_ in 'LR':
        p = pd[f'palpebra_{s_}']; d[f'palpebra_{s_}'] = ((p[1][0], p[1][1], 0.025), (p[2][0] * 1.02, p[2][1] * 1.05, 0.039), (0, 0, 0))
    return d
fkeys = {'blink': lidk(), 'brow_up': {'sobrancelha_L': ovr('sobrancelha_L', (0, 0.002, 0.016)), 'sobrancelha_R': ovr('sobrancelha_R', (0, 0.002, 0.016))},
         'mouth_smile': mth(1.35, 1.1, -0.002, 0, 0.012), 'A': mth(1.1, 5.5, -0.012), 'E': mth(1.35, 3.0, -0.006), 'I': mth(1.3, 1.6, -0.002), 'O': mth(0.75, 4.5, -0.01, -0.004),
         'U': mth(0.5, 3.0, -0.006, -0.008), 'MBP': mth(1.0, 0.25), 'FV': mth(0.95, 1.2, 0.002), 'rest': mth(0.95, 0.9)}
_u2 = _us(32, 16); _u3 = _us(16, 10)
verts, faces_, mids, rng_ = [], [], [], {}
for (pn, pc, pr, prot, mi, big) in parts:
    uv, uf = _u2 if big else _u3; off = len(verts); M_ = _MM(pc, pr, prot)
    verts += [M_ @ u for u in uv]; faces_ += [[i + off for i in f] for f in uf]; mids += [mi] * len(uf); rng_[pn] = (off, len(uv), big)
me = D.meshes.new('TJ_Ancora_Rosto'); me.from_pydata(verts, [], faces_)
for m_ in (m_skinA, m_eyew, m_pup, m_hairA, m_lip): me.materials.append(m_)
for p_, mi in zip(me.polygons, mids): p_.material_index = mi
me.shade_smooth()
head_a = D.objects.new('TJ_Ancora_Cabeca', me); link(head_a, cSet); head_a.location = HC; set_parent(head_a, anchor)
head_a.shape_key_add(name='Basis', from_mix=False)
for kn, ov in fkeys.items():
    kb = head_a.shape_key_add(name=kn, from_mix=False); kb.value = 0.0
    for pn, (kc, kr, krot) in ov.items():
        off, n_, big = rng_[pn]; uv = (_u2 if big else _u3)[0]; M_ = _MM(kc, kr, krot)
        for i in range(n_): kb.data[off + i].co = M_ @ uv[i]
# cabelo (bob castanho com franja)
bm = bmesh.new()
add_ell_(bm, (0, 0.03, 0.02), (0.158, 0.165, 0.165), 3)
add_ell_(bm, (0, -0.1, 0.12), (0.12, 0.06, 0.05), 3, rot=Euler((rad(-20), 0, 0)))
for sg in (-1, 1): add_capsule_(bm, (sg * 0.15, 0.02, 0.0), (sg * 0.155, 0.0, -0.2), 0.05, 0.05, 3)
add_ell_(bm, (0, 0.1, -0.1), (0.14, 0.1, 0.17), 3)
hair_a = bm_obj('TJ_Ancora_Cabelo', bm, cSet, [m_hairA, m_hairA, m_hairA, m_hairA]); hair_a.data.shade_smooth(); set_parent(hair_a, head_a)
# controle por propriedades + drivers (mesmo padrão dos personagens)
ctrlA = empty('TJ_FACE_Ancora', S_(0, 0, 0), cSet, 0.1, 'SPHERE')
for kb in head_a.data.shape_keys.key_blocks[1:]:
    ctrlA[kb.name] = 0.0
    fc = kb.driver_add('value'); dr = fc.driver; dr.type = 'AVERAGE'
    v_ = dr.variables.new(); v_.name = 'v'; v_.type = 'SINGLE_PROP'; v_.targets[0].id = ctrlA; v_.targets[0].data_path = f'["{kb.name}"]'
# animação da âncora: fala (lip-sync), piscadas, balanço de cabeça e tronco, mãos mexendo nos papéis
anchor.rotation_mode = 'XYZ'; head_a.rotation_mode = 'XYZ'
lipsync(ctrlA, 'Boa noite. Uma discussão por vaga de garagem terminou na delegacia no fim da tarde. A briga entre dois moradores começou no estacionamento do condomínio, e a polícia precisou intervir. Imagens do local.', 3, 100, 0.9)
sk(ctrlA, 'mouth_smile', 0.0, 1); sk(ctrlA, 'mouth_smile', 0.25, 6); sk(ctrlA, 'mouth_smile', 0.0, 40)
for f, a_ in ((1, 0), (14, 3), (30, -2), (50, 3), (70, -3), (90, 2), (NEWS_FRAMES, 0)):
    key(head_a, 'rotation_euler', (rad(2), rad(a_ * 0.6), rad(a_)), f)
for f in (8, 36, 66, 92): blink(ctrlA, f, 5)
for f, a_ in ((1, 0), (24, 1.5), (52, -1.5), (80, 1.2), (NEWS_FRAMES, 0)):
    key(anchor, 'rotation_euler', (0, 0, rad(a_)), f)
sk(ctrlA, 'brow_up', 0.0, 20); sk(ctrlA, 'brow_up', 0.7, 24); sk(ctrlA, 'brow_up', 0.0, 34); sk(ctrlA, 'brow_up', 0.8, 60); sk(ctrlA, 'brow_up', 0.0, 68)

# ------------------------------------------------ iluminação de estúdio de TV
NSc = NS
def tlight(name, kind, e, color, loc, tgt=None, size=None, size_y=None, rot=(0, 0, 0), spot=None):
    ld = D.lights.new(name, kind); ld.energy = e; ld.color = color
    if kind == 'AREA': ld.shape = 'RECTANGLE'; ld.size = size; ld.size_y = size_y or size
    if kind == 'SPOT': ld.spot_size = rad(spot[0]); ld.spot_blend = spot[1]
    o = D.objects.new(name, ld); link(o, cSet); o.location = loc; o.rotation_euler = [rad(a) for a in rot]
    if tgt is not None: look_at(o, tgt)
    return o
tlight('TJ_Key_E', 'AREA', 420, hexc('#FFF1E0'), S_(-2.4, -1.5, 3.4), S_(0.1, DESK_Y + 0.6, 1.5), 2.6, 1.8)
tlight('TJ_Key_D', 'AREA', 320, hexc('#FFF1E0'), S_(2.8, -1.5, 3.0), S_(0.1, DESK_Y + 0.6, 1.5), 2.6, 1.8)
tlight('TJ_Fill', 'AREA', 140, hexc('#A8C4FF'), S_(0, -2.5, 1.2), S_(0.1, DESK_Y + 0.6, 1.5), 4.0, 2.0)
tlight('TJ_Back_E', 'SPOT', 520, hexc('#FFE6C0'), S_(-1.6, DESK_Y + 3.0, 3.6), S_(0.1, DESK_Y + 0.62, 1.4), spot=(40, 0.6))
tlight('TJ_Back_D', 'SPOT', 520, hexc('#FFE6C0'), S_(1.8, DESK_Y + 3.0, 3.6), S_(0.1, DESK_Y + 0.62, 1.4), spot=(40, 0.6))
tlight('TJ_Acento_Azul', 'AREA', 260, hexc('#2F6BFF'), S_(-5.0, 7.5, 2.5), S_(0.0, 9.8, 2.5), 2.0, 3.0)
tlight('TJ_Acento_Verm', 'AREA', 200, hexc('#FF3B5A'), S_(6.5, 7.5, 2.0), S_(3.4, 9.5, 2.5), 2.0, 3.0)
tlight('TJ_Piso_Luz', 'AREA', 180, hexc('#4F7BFF'), S_(0, 1.0, 5.5), S_(0.0, 5.0, 0.0), 5.0, 5.0)

# ------------------------------------------------ CAM_TV_Jornal: plano médio com dolly (1-56), corte para o telão com a viatura/garagem (57-103)
cam_cd = D.cameras.new('CAM_TV_Jornal'); cam_cd.lens = 35; cam_cd.sensor_width = 36; cam_cd.clip_start = 0.05
cam_cd.dof.use_dof = True; cam_cd.dof.aperture_fstop = 2.8
camTV = D.objects.new('CAM_TV_Jornal', cam_cd); link(camTV, cSet)
tgtA = empty('TJ_CamAlvo', S_(0.1, DESK_Y + 0.62, 1.45), cSet, 0.2)
tt = camTV.constraints.new('TRACK_TO'); tt.target = tgtA; tt.track_axis = 'TRACK_NEGATIVE_Z'; tt.up_axis = 'UP_Y'
key(camTV, 'location', S_(-1.1, -0.3, 1.5), 1); key(camTV, 'location', S_(-0.35, 1.2, 1.5), 56)        # dolly lento para a âncora
key(tgtA, 'location', S_(0.1, DESK_Y + 0.62, 1.45), 1); key(tgtA, 'location', S_(0.1, DESK_Y + 0.62, 1.5), 56)
key(camTV, 'location', S_(2.6, 4.0, 3.3), 57, 'CONSTANT'); key(camTV, 'location', S_(3.0, 5.6, 3.1), NEWS_FRAMES)                       # corte: crane até o telão
key(tgtA, 'location', S_(3.4, 9.5, 3.0), 57, 'CONSTANT'); key(tgtA, 'location', S_(3.4, 9.5, 3.05), NEWS_FRAMES)
cam_cd.dof.focus_object = None
key(cam_cd.dof, 'focus_distance', 3.4, 1); key(cam_cd.dof, 'focus_distance', 2.6, 56); key(cam_cd.dof, 'focus_distance', 6.2, 57, 'CONSTANT'); key(cam_cd.dof, 'focus_distance', 5.4, NEWS_FRAMES)
key(cam_cd.dof, 'aperture_fstop', 2.8, 1, 'CONSTANT'); key(cam_cd.dof, 'aperture_fstop', 6.3, 57, 'CONSTANT')
key(cam_cd, 'lens', 35, 1); key(cam_cd, 'lens', 28, 57, 'CONSTANT')

# ------------------------------------------------ gráficos de broadcast (presos à câmera): tarja inferior animada, AO VIVO, relógio, ticker, logo
GD = 2.0
def gp(name, size, x, y, m_, parent=camTV, z=0.0):
    o = box(name, (size[0], size[1], 0.004), (x, y, -(GD - z)), m_, cSet, parent=parent, bevel=0); return o
def gt(name, body, size, x, y, m_, align='LEFT', z=0.0):
    return text(name, body, size, (x, y, -(GD - z) + 0.002), (0, 0, 0), m_, cSet, align=align, parent=camTV)
g_red = emat2('MAT_TJ_G_Verm', '#E0101C', 1.3); g_navy = emat2('MAT_TJ_G_Azul', '#0A1F8A', 1.5); g_white = emat2('MAT_TJ_G_Branco', '#FFFFFF', 3.2)
g_yel = emat2('MAT_TJ_G_Amarelo', '#FFC000', 2.2); g_dark = emat2('MAT_TJ_G_Escuro', '#0B0F28', 2.0)
LT_Y = -0.40
bar = gp('TJ_G_Tarja', (1.78, 0.115), -0.12, LT_Y, g_red); bar.location.x = -0.12;
for v in bar.data.vertices: v.co.x += 0.89            # origem na borda esquerda para a tarja deslizar da esquerda
bar.location.x = -1.01
tag = gp('TJ_G_Urgente', (0.32, 0.052), -0.85, LT_Y + 0.085, g_yel)
tagt = gt('TJ_G_UrgenteTxt', 'URGENTE', 0.034, -0.86, LT_Y + 0.085 - 0.016, g_red, 'CENTER', 0.002)
manch = gt('TJ_G_Manchete', 'Discussão por vaga de garagem termina na delegacia', 0.05, -0.97, LT_Y - 0.02, g_white, 'LEFT', 0.003)
sub = gp('TJ_G_SubBarra', (1.78, 0.05), -0.12, LT_Y - 0.083, g_navy)
subt = gt('TJ_G_SubTxt', 'Moradores brigam por vaga em condomínio; polícia foi chamada', 0.026, -0.97, LT_Y - 0.097, g_white, 'LEFT', 0.003)
tick = gp('TJ_G_TickerBarra', (2.07, 0.075), 0.0, -0.545, g_dark)
tickt = gt('TJ_G_TickerTxt', 'ÚLTIMAS NOTÍCIAS  •  Trânsito intenso na região central  •  Previsão: noite fria e céu aberto  •  Condomínios discutem controle de acesso  •  Moradores pedem solução para filas e vagas  •  ', 0.034, 1.1, -0.558, g_yel, 'LEFT', 0.003)
live = gp('TJ_G_AoVivoFundo', (0.3, 0.075), 0.87, 0.5, g_red); livet = gt('TJ_G_AoVivoTxt', 'AO VIVO', 0.044, 0.87, 0.486, g_white, 'CENTER', 0.002)
clock = gp('TJ_G_RelogioFundo', (0.22, 0.075), 0.58, 0.5, g_navy); clockt = gt('TJ_G_RelogioTxt', '18:47', 0.044, 0.58, 0.486, g_white, 'CENTER', 0.002)
lg = gp('TJ_G_LogoFundo', (0.62, 0.095), -0.69, 0.495, g_navy); lgt = gt('TJ_G_LogoTxt', 'JORNAL DA CIDADE', 0.04, -0.69, 0.48, g_white, 'CENTER', 0.002)
dot = cyl('TJ_G_LogoPonto', 0.034, 0.004, (-1.0, 0.495, -(GD - 0.001)), g_red, cSet, rot=(90, 0, 0), segs=20, parent=camTV)
# tarja entra deslizando da esquerda (f10-f22), mantém; ticker rola continuamente; "AO VIVO" pisca
for o_ in (bar, tag, tagt, manch, sub, subt):
    px = o_.location.x
    key(o_, 'location', (px - 2.4, o_.location.y, o_.location.z), 1, 'CONSTANT'); key(o_, 'location', (px - 2.4, o_.location.y, o_.location.z), 10)
    key(o_, 'location', (px, o_.location.y, o_.location.z), 22)
key(tickt, 'location', (1.1, tickt.location.y, tickt.location.z), 1, 'LINEAR'); key(tickt, 'location', (-2.6, tickt.location.y, tickt.location.z), NEWS_FRAMES, 'LINEAR')
for f in range(1, NEWS_FRAMES, 12):
    key(livet, 'hide_render', (f // 12) % 2 == 1, f, 'CONSTANT')

# ------------------------------------------------ cena/render do estúdio
NS.camera = camTV
NS.frame_start = 1; NS.frame_end = NEWS_FRAMES
NS.render.resolution_x = 1280; NS.render.resolution_y = 720; NS.render.resolution_percentage = 100
NS.render.fps = 24
NS.render.engine = 'BLENDER_EEVEE'
NS.eevee.taa_render_samples = 48; NS.eevee.use_raytracing = True
NS.view_settings.view_transform = 'AgX'; NS.view_settings.look = 'AgX - Medium High Contrast'
NS.render.use_motion_blur = False; NS.render.use_compositing = False
NS.render.image_settings.file_format = 'PNG'; NS.render.image_settings.color_depth = '8'
NS.render.filepath = '//render/telejornal/tv_'
nw = D.worlds.new('TJ_World'); NS.world = nw; nwt = nw.node_tree
for n_ in list(nwt.nodes): nwt.nodes.remove(n_)
bgw = nwt.nodes.new('ShaderNodeBackground'); wow = nwt.nodes.new('ShaderNodeOutputWorld'); nwt.links.new(bgw.outputs[0], wow.inputs[0])
bgw.inputs['Color'].default_value = (*hexc('#101A48'), 1); bgw.inputs['Strength'].default_value = 0.25
