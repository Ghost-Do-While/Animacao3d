# Parte 1 - MAQUETE_Condominio AMPLIADO (32 x 26 m): mesma disposição da maquete, com folgas generosas. Estilo de estúdio.
exec(compile(open(os.path.join(BASE, 'layout.py'), encoding='utf-8').read(), 'layout.py', 'exec'))
cPred, cGua, cCan, cSen = col('Predio'), col('Guarita'), col('Cancelas'), col('Sensores')
cMur, cGP, cVag = col('Muros'), col('Gradis_Postes'), col('Vagas')

# ---- paleta saturada e harmônica (quente do pôr do sol x azul-violeta da sombra)
m_piso = mat('MAT_MQ_Piso', hexc('#2C3042'), 0.55, bump=0.25)
m_muro = mat('MAT_MQ_MuroCinza', hexc('#C3CCDA'), 0.75, bump=0.3)
m_branco = mat('MAT_MQ_Branco', hexc('#FFF3DF'), 0.55)
m_creme = mat('MAT_MQ_Creme', hexc('#F5E2BE'), 0.7, bump=0.25)
m_chumbo = mat('MAT_MQ_CinzaAzulado', hexc('#7F93B2'), 0.65)
m_choc = mat('MAT_MQ_Terracota_Guarita', hexc('#9A4A32'), 0.7, bump=0.3)
m_vidro = mat('MAT_MQ_VidroEscuro', hexc('#16213A'), 0.04, alpha=0.4)
m_preto = mat('MAT_MQ_PretoImpressao', hexc('#262330'), 0.5)
m_metal = mat('MAT_MQ_Metal', hexc('#9FA9B8'), 0.28, 0.9)
m_faixa = mat('MAT_MQ_FaixaVaga', hexc('#FFF6E6'), 0.55)
m_interno = mat('MAT_MQ_Interior', hexc('#3A3550'), 0.9)
m_janela_acesa = mat('MAT_MQ_JanelaAcesa', hexc('#5A3A1C'), 0.7, emit=hexc('#FFC070'), emit_str=3.5)

def math_builder(nt):
    def M(op, a, b=None):
        n = nt.nodes.new('ShaderNodeMath'); n.operation = op
        for idx, v in ((0, a), (1, b)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[idx].default_value = v
            else: nt.links.new(v, n.inputs[idx])
        return n.outputs[0]
    return M

def cobogo_mat():
    """Módulos de 0,4 m com triângulos vazados em cata-vento (alfa procedural), terracota rico."""
    m = new_mat('MAT_MQ_Cobogo'); nt = m.node_tree; b = bsdf(m)
    b.inputs['Base Color'].default_value = (*hexc('#C9663C'), 1)
    b.inputs['Roughness'].default_value = 0.7
    tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sp.inputs[0])
    M = math_builder(nt)
    u = M('FRACT', M('DIVIDE', sp.outputs['X'], 0.4)); v = M('FRACT', M('DIVIDE', sp.outputs['Z'], 0.4))
    a = M('SUBTRACT', u, 0.5); bb = M('SUBTRACT', v, 0.5)
    A_ = M('ABSOLUTE', a); B_ = M('ABSOLUTE', bb)
    inner = M('MULTIPLY', M('LESS_THAN', A_, 0.41), M('LESS_THAN', B_, 0.41))
    sgn = M('GREATER_THAN', M('MULTIPLY', a, bb), 0.0)
    c1 = M('GREATER_THAN', A_, B_)
    cond = M('ADD', M('MULTIPLY', sgn, c1), M('MULTIPLY', M('SUBTRACT', 1.0, sgn), M('SUBTRACT', 1.0, c1)))
    gap = M('GREATER_THAN', M('ABSOLUTE', M('SUBTRACT', A_, B_)), 0.05)
    hole = M('MULTIPLY', M('MULTIPLY', inner, cond), gap)
    nt.links.new(M('SUBTRACT', 1.0, hole), b.inputs['Alpha'])
    m.surface_render_method = 'DITHERED'
    return m
m_cob = cobogo_mat()

def wall_seg(name, p0, p1, h, thick, m_, c, z0=0.0, bevel=None):
    p0 = Vector((p0[0], p0[1], 0)); p1 = Vector((p1[0], p1[1], 0)); d = p1 - p0
    o = box(name, (d.length, thick, h), ((p0 + p1) / 2).to_tuple()[:2] + (z0 + h / 2,), m_, c, bevel=bevel)
    o.rotation_euler.z = math.atan2(d.y, d.x)
    return o

# ------------------------------------------------ piso e muros (cinza-azulado claro, bevel generoso)
box('MQ_Piso', (2 * LX, 2 * LY, 0.1), (0, 0, -0.05), m_piso, cMur, bevel=0)
wall_seg('MQ_Muro_Esq', (-LX - 0.1, -LY), (-LX - 0.1, LY + 0.2), WALL_H, 0.2, m_muro, cMur)
wall_seg('MQ_Muro_Fundo', (-LX - 0.2, LY + 0.1), (LX + 0.2, LY + 0.1), WALL_H, 0.2, m_muro, cMur)
wall_seg('MQ_Muro_Dir', (LX + 0.1, -LY), (LX + 0.1, LY + 0.2), WALL_H, 0.2, m_muro, cMur)
# capeamento dos muros (acabamento branco quente)
for nm, p0, p1 in (('Esq', (-LX - 0.1, -LY), (-LX - 0.1, LY + 0.2)), ('Fundo', (-LX - 0.25, LY + 0.1), (LX + 0.25, LY + 0.1)), ('Dir', (LX + 0.1, -LY), (LX + 0.1, LY + 0.2))):
    wall_seg(f'MQ_Muro_{nm}_Capa', p0, p1, 0.1, 0.32, m_branco, cMur, z0=WALL_H)
# cobogó
def cob(nm, p0, p1): wall_seg(nm, p0, p1, COB_H, 0.18, m_cob, cMur, bevel=0.01)
cob('MQ_Cobogo_Centro', (COBC_X[0], -LY), (COBC_X[1], -LY))
cob('MQ_Cobogo_Centro_RetornoEsq', (COBC_X[0], -LY), (COBC_X[0], -8.2))
cob('MQ_Cobogo_Centro_RetornoDir', (COBC_X[1], -LY), (COBC_X[1], -8.2))
cob('MQ_Cobogo_Esq', (COBL_X[0], -LY), (COBL_X[1], -LY))
cob('MQ_Cobogo_Dir', (COBR_X[0], -LY), (COBR_X[1], -LY))
for nm, x0, x1 in (('Centro', COBC_X[0], COBC_X[1]), ('Esq', COBL_X[0], COBL_X[1]), ('Dir', COBR_X[0], COBR_X[1])):
    box(f'MQ_Cobogo_{nm}_Capa', (x1 - x0 + 0.1, 0.3, 0.12), ((x0 + x1) / 2, -LY, COB_H + 0.06), m_branco, cMur)
# placa "CONDOMÍNIO RESIDENCIAL" com letras metálicas
m_letra = mat('MAT_MQ_LetraMetal', hexc('#E2E6EC'), 0.22, 1.0)
box('MQ_Placa_Fundo', (4.6, 0.06, 0.56), (0.0, -LY - 0.12, 0.74), mat('MAT_MQ_PlacaFundo', hexc('#2E3550'), 0.5), cMur)
text('MQ_Placa_Texto', 'CONDOMÍNIO RESIDENCIAL', 0.27, (0.0, -LY - 0.17, 0.72), (90, 0, 0), m_letra, cMur, extrude=0.014)

# ------------------------------------------------ gradis (barras a cada 0,1 m) e postes
def gradil(name, p0, p1, h, c):
    p0 = Vector(p0); p1 = Vector(p1); d = p1 - p0; L = d.length
    n = max(2, int(L / 0.12))
    bm = bmesh.new()
    def addbox(cx, cz, sx, sy, sz):
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r['verts']: v.co = Vector((cx + v.co.x * sx, v.co.y * sy, cz + v.co.z * sz))
    for i in range(n + 1): addbox(i * L / n - L / 2, h / 2, 0.03, 0.03, h)
    addbox(0, h - 0.04, L, 0.06, 0.06); addbox(0, 0.15, L, 0.05, 0.05); addbox(0, 0.55, L, 0.04, 0.04)
    o = bm_obj(name, bm, c, m_branco)
    o.location = ((p0.x + p1.x) / 2, (p0.y + p1.y) / 2, 0)
    o.rotation_euler.z = math.atan2(d.y, d.x)
    md = o.modifiers.new('Bevel', 'BEVEL'); md.width = 0.006; md.segments = 2
    return o
gradil('MQ_Gradil_01', GR1[0], GR1[1], 1.1, cGP)
gradil('MQ_Gradil_02', GR2[0], GR2[1], 1.1, cGP)

m_lanterna = mat('MAT_MQ_LanternaVidro', hexc('#FFE2A8'), 0.15, emit=hexc('#FFB860'), emit_str=9.0)
POSTES = {'MQ_Poste_01': P1, 'MQ_Poste_02': P2}
for nm, (px, py) in POSTES.items():
    cyl(f'{nm}_Base', 0.2, 0.5, (px, py, 0.25), m_preto, cGP, segs=10, r2=0.15)
    cyl(f'{nm}_Haste', 0.07, 3.2, (px, py, 2.0), m_preto, cGP, segs=14)
    cyl(f'{nm}_Anel', 0.12, 0.1, (px, py, 3.55), m_preto, cGP, segs=14)
    cyl(f'{nm}_Lanterna_Base', 0.18, 0.1, (px, py, 3.65), m_preto, cGP, segs=4, rot=(0, 0, 45), smooth=False)
    cyl(f'{nm}_Lanterna_Vidro', 0.2, 0.46, (px, py, 3.93), m_lanterna, cGP, r2=0.25, segs=4, rot=(0, 0, 45), smooth=False)
    cyl(f'{nm}_Lanterna_Teto', 0.34, 0.22, (px, py, 4.27), m_preto, cGP, r2=0.03, segs=4, rot=(0, 0, 45), smooth=False)
    sphere(f'{nm}_Ponteira', 0.05, (px, py, 4.42), m_preto, cGP, segs=(10, 8))

# ------------------------------------------------ guarita 4 x 5 m (terracota) + laje branca em "T"
gx, gy = (GX0 + GX1) / 2, (GY0 + GY1) / 2
box('MQ_Guarita_ParedeFundo', (GX1 - GX0, 0.2, GH), (gx, GY1 - 0.1, GH / 2), m_choc, cGua)
box('MQ_Guarita_ParedeEsq', (0.2, GY1 - GY0, GH), (GX0 + 0.1, gy, GH / 2), m_choc, cGua)
box('MQ_Guarita_ParedeDir', (0.2, GY1 - GY0, GH), (GX1 - 0.1, gy, GH / 2), m_choc, cGua)
box('MQ_Guarita_Frente_Baixo', (GX1 - GX0, 0.2, 1.0), (gx, GY0 + 0.1, 0.5), m_choc, cGua)
box('MQ_Guarita_Frente_Cima', (GX1 - GX0, 0.2, 0.5), (gx, GY0 + 0.1, GH - 0.25), m_choc, cGua)
box('MQ_Guarita_Frente_PilarEsq', (0.7, 0.2, 1.3), (GX0 + 0.35, GY0 + 0.1, 1.65), m_choc, cGua)
box('MQ_Guarita_Frente_PilarDir', (0.7, 0.2, 1.3), (GX1 - 0.35, GY0 + 0.1, 1.65), m_choc, cGua)
box('MQ_Guarita_Janela', (GX1 - GX0 - 1.4, 0.04, 1.3), (gx, GY0 + 0.1, 1.65), m_vidro, cGua, bevel=0)
box('MQ_Guarita_Janela_Moldura', (GX1 - GX0 - 1.3, 0.06, 1.4), (gx, GY0 + 0.07, 1.65), m_branco, cGua)
box('MQ_Guarita_Porta', (0.06, 1.0, 2.2), (GX1 + 0.02, -9.4, 1.1), mat('MAT_MQ_PortaGuarita', hexc('#5A2E22'), 0.55), cGua)
box('MQ_Guarita', (GX1 - GX0 + 1.0, GY1 - GY0 + 0.3, 0.3), (gx, gy, GH + 0.15), m_branco, cGua)            # laje do "T"
box('MQ_Guarita_Marquise', (2.8, 4.0, 0.3), (gx, GY1 + 2.0, GH + 0.15), m_branco, cGua)   # marquise em balanço: SEM pilar de apoio
box('MQ_Guarita_Piso', (GX1 - GX0, GY1 - GY0, 0.06), (gx, gy, 0.03), mat('MAT_MQ_PisoGuarita', hexc('#8A7A6A'), 0.7), cGua, bevel=0)
box('MQ_Guarita_Bancada', (3.0, 0.6, 0.1), (gx, GY0 + 0.6, 1.0), m_branco, cGua)
m_sil = mat('MAT_MQ_Porteiro', hexc('#0F1018'), 0.9)
sphere('MQ_Guarita_Porteiro_Cabeca', (0.15, 0.16, 0.19), (gx - 0.4, -11.3, 1.78), m_sil, cGua)
sphere('MQ_Guarita_Porteiro_Corpo', (0.3, 0.22, 0.4), (gx - 0.4, -11.2, 1.26), m_sil, cGua)
porteiro_braco = sphere('MQ_Guarita_Porteiro_Braco', (0.06, 0.26, 0.06), (gx - 0.1, -11.55, 1.3), m_sil, cGua)
box('MQ_Guarita_Botao', (0.1, 0.1, 0.05), (gx + 0.15, -12.0, 1.06), mat('MAT_MQ_BotaoGuarita', hexc('#2A8A3A'), 0.4, emit=hexc('#3AFF5A'), emit_str=1.8), cGua)

# ------------------------------------------------ cancelas (base preta + braço com faixas)
m_refl_r = mat('MAT_MQ_RefletivoVerm', hexc('#E03A28'), 0.3, emit=hexc('#E03A28'), emit_str=0.2)
m_refl_b = mat('MAT_MQ_RefletivoBranco', hexc('#FFF6E6'), 0.3, emit=hexc('#FFFFFF'), emit_str=0.15)
cab_cols = [mat('MAT_MQ_CaboMarrom', hexc('#7A4A28'), 0.5), mat('MAT_MQ_CaboVermelho', hexc('#D02A22'), 0.5), mat('MAT_MQ_CaboLaranja', hexc('#F08A22'), 0.5)]
def cancela(nm, base, pivot, arm_len, direction):
    box(f'{nm}_Base', (0.5, 0.45, 1.1), (base[0], base[1], 0.55), m_preto, cCan)
    cyl(f'{nm}_Dobradica', 0.09, 0.16, (pivot[0], pivot[1] - 0.2, 0.95), m_metal, cCan, rot=(90, 0, 0), segs=14)
    pv = empty(nm, (pivot[0], pivot[1], 0.95), cCan, 0.4, 'ARROWS'); pv.rotation_mode = 'XYZ'
    box(f'{nm}_Braco', (arm_len, 0.08, 0.1), (direction * arm_len / 2, 0, 0), m_preto, cCan, parent=pv)
    n = int(arm_len / 0.5)
    for i in range(n):
        box(f'{nm}_Faixa_{i}', (0.25, 0.085, 0.104), (direction * (0.45 + i * 0.5), 0, 0), m_refl_r if i % 2 == 0 else m_refl_b, cCan, parent=pv)
    for i, mm in enumerate(cab_cols):
        a = Vector((base[0] - 0.14 + i * 0.05, base[1] + 0.23, 0.35)); b = Vector((a.x - 0.1, a.y + 0.9, 0.016))
        beam(f'{nm}_Cabo_{i}', a, b, 0.02, mm, cCan)
    return pv
C1 = cancela('MQ_Cancela_C1', C1_BASE, C1_PIV, ARM_LEN, 1)
C2 = cancela('MQ_Cancela_C2', C2_BASE, C2_PIV, ARM_LEN, -1)

# ------------------------------------------------ sensores ultrassônicos (LED apagado)
m_pcb = mat('MAT_MQ_PlacaAzul', hexc('#2563D6'), 0.35)
m_prata = mat('MAT_MQ_Prata', hexc('#D8DCE2'), 0.18, 1.0)
m_led = mat('MAT_MQ_LED', hexc('#3A0A0A'), 0.3, emit=hexc('#FF2020'), emit_str=0.0)
def sensor(nm, pos, rz):
    root_ = empty(nm, (pos[0], pos[1], 0), cSen, 0.4)
    box(f'{nm}_Pedestal', (0.2, 0.2, 0.9), (0, 0, 0.45), m_preto, cSen, parent=root_)
    box(f'{nm}_Placa', (0.7, 0.05, 0.34), (0, -0.05, 1.07), m_pcb, cSen, parent=root_)
    for sx in (-1, 1):
        cyl(f'{nm}_Olho_{sx}', 0.12, 0.16, (sx * 0.2, -0.14, 1.07), m_prata, cSen, rot=(90, 0, 0), segs=24, parent=root_)
        cyl(f'{nm}_OlhoTela_{sx}', 0.095, 0.162, (sx * 0.2, -0.14, 1.07), m_preto, cSen, rot=(90, 0, 0), segs=20, parent=root_)
    sphere(f'{nm}_LED', 0.02, (0, -0.08, 1.2), m_led, cSen, segs=(8, 6), parent=root_)
    root_.rotation_euler.z = rad(rz)
    return root_
sensor('MQ_Sensor_S1', S1_POS, 90)
sensor('MQ_Sensor_S2', S2_POS, -90)

# ------------------------------------------------ vagas 2,6 x 5,2 m (faixa branca de 0,12 m)
for i, y in enumerate([CENT_Y['V6'] + 1.3, CENT_Y['V6'] - 1.3, CENT_Y['V5'] - 1.3]):
    box(f'MQ_Vaga_Central_Faixa_{i}', (SLOT_D, 0.12, 0.012), ((CENT_X0 + CENT_X1) / 2, y, 0.006), m_faixa, cVag, bevel=0)
for i, y in enumerate([RIGHT_Y[0] + 1.3, RIGHT_Y[1] + 1.3, RIGHT_Y[2] + 1.3, RIGHT_Y[3] + 1.3, RIGHT_Y[3] - 1.3]):
    box(f'MQ_Vaga_Dir_Faixa_{i}', (SLOT_D, 0.12, 0.012), ((RIGHT_X0 + RIGHT_X1) / 2, y, 0.006), m_faixa, cVag, bevel=0)
for nm, (vx, vy) in {'MQ_Vaga_V1': ((RIGHT_X0 + RIGHT_X1) / 2, RIGHT_Y[0]), 'MQ_Vaga_V2': ((RIGHT_X0 + RIGHT_X1) / 2, RIGHT_Y[1]), 'MQ_Vaga_V3': ((RIGHT_X0 + RIGHT_X1) / 2, RIGHT_Y[2]),
                     'MQ_Vaga_V4': ((RIGHT_X0 + RIGHT_X1) / 2, RIGHT_Y[3]), 'MQ_Vaga_V5': ((CENT_X0 + CENT_X1) / 2, CENT_Y['V5']), 'MQ_Vaga_V6': ((CENT_X0 + CENT_X1) / 2, CENT_Y['V6'])}.items():
    e_ = empty(nm, (vx, vy, 0), cVag, 0.5, 'CUBE'); e_.scale = (SLOT_D / 2, SLOT_W / 2, 0.03)

# ------------------------------------------------ prédio 7 x 13 m, 4 pavimentos de 3 m
PH = FLOOR_H; NF = FLOORS; TOP = PH * NF
XA, XB, XW = BX1, BX1 - B_RECUO, BX0       # fachada A (frente), fachada B (recuada) e parede oeste
Y0, YM, Y1 = BY0, BYM, BY1
m_teto = mat('MAT_MQ_CoberturaPreta', hexc('#2E2A3A'), 0.9, bump=0.7)
random.seed(5)
box('MQ_Predio', (0.25, Y1 - Y0, TOP), (XW + 0.125, (Y0 + Y1) / 2, TOP / 2), m_creme, cPred)                  # oeste
box('MQ_Predio_ParedeSul', (XA - XW, 0.25, TOP), ((XW + XA) / 2, Y0 + 0.125, TOP / 2), m_creme, cPred)
box('MQ_Predio_ParedeNorte', (XB - XW, 0.25, TOP), ((XW + XB) / 2, Y1 - 0.125, TOP / 2), m_creme, cPred)
box('MQ_Predio_Degrau', (XA - XB, 0.25, TOP), ((XA + XB) / 2, YM + 0.125, TOP / 2), m_chumbo, cPred)
for k_ in range(NF):
    z0 = k_ * PH
    F = lambda s: f'MQ_Predio_P{k_}_{s}'
    # lajes (piso/teto de cada pavimento) + faixa branca saliente
    box(F('LajeA'), (XA - XW, YM - Y0, 0.2), ((XW + XA) / 2, (Y0 + YM) / 2, z0 + 0.1), m_branco, cPred, bevel=0)
    box(F('LajeB'), (XB - XW, Y1 - YM, 0.2), ((XW + XB) / 2, (YM + Y1) / 2, z0 + 0.1), m_branco, cPred, bevel=0)
    box(F('FaixaA'), (XA - XW + 0.4, YM - Y0 + 0.4, 0.22), ((XW + XA) / 2 + 0.2, (Y0 + YM) / 2, z0 + PH - 0.11), m_branco, cPred)
    box(F('FaixaB'), (XB - XW + 0.4, Y1 - YM + 0.4, 0.22), ((XW + XB) / 2 + 0.2, (YM + Y1) / 2, z0 + PH - 0.11), m_branco, cPred)
    # ---- Bloco A: pilar sul, janela grande 3x2, painel cobogó, parede norte, sacada
    xa = XA - 0.125
    box(F('A_PilarSul'), (0.25, 1.0, PH), (xa, Y0 + 0.5, z0 + PH / 2), m_creme, cPred)
    box(F('A_Peitoril'), (0.25, 4.0, 0.7), (xa, 2.7, z0 + 0.55), m_creme, cPred)
    box(F('A_Verga'), (0.25, 4.0, 0.45), (xa, 2.7, z0 + PH - 0.225 - 0.1), m_creme, cPred)
    box(F('A_ParedeNorte'), (0.25, 0.5, PH), (xa, YM - 0.25, z0 + PH / 2), m_creme, cPred)
    box(F('A_ParedeCobogo'), (0.25, 1.0, PH), (xa, 5.2, z0 + PH / 2), m_creme, cPred)
    box(F('A_Vidro'), (0.04, 4.0, 1.75), (XA - 0.06, 2.7, z0 + 1.575), m_vidro, cPred, bevel=0)
    for i, yy in enumerate([1.367, 2.033, 2.7, 3.367, 4.033, 4.7 - 1.334 + 1.334]):
        pass
    for i, yy in enumerate([0.7 + 4.0 / 3, 0.7 + 8.0 / 3, 0.7, 4.7]):
        box(F(f'A_Caixilho_V{i}'), (0.07, 0.07, 1.8), (XA - 0.04, yy, z0 + 1.575), m_branco, cPred, bevel=0.01)
    for i, zz in enumerate([0.7, 1.575, 2.45]):
        box(F(f'A_Caixilho_H{i}'), (0.07, 4.0, 0.07), (XA - 0.04, 2.7, z0 + zz), m_branco, cPred, bevel=0.01)
    cb = box(F('A_Cobogo'), (0.9, 0.08, 2.5), (XA + 0.02, 5.2, z0 + 1.45), m_cob, cPred, bevel=0)
    cb.rotation_euler.z = rad(90)
    box(F('A_Sacada'), (0.9, 4.4, 0.16), (XA + 0.4, 2.7, z0 + 0.08), m_branco, cPred)
    box(F('A_SacadaGuarda'), (0.05, 4.4, 0.35), (XA + 0.82, 2.7, z0 + 0.34), m_branco, cPred)
    if k_ != APT_FLOOR:
        box(F('A_Fundo'), (0.04, 4.0, 1.75), (XA - 0.9, 2.7, z0 + 1.575), m_janela_acesa if random.random() < 0.5 else m_interno, cPred, bevel=0)
    # ---- Bloco B (recuado): coluna cinza-azulada, cobogó, janela 2x2, sacada
    xb = XB - 0.125
    box(F('B_ColunaChumbo'), (0.4, 0.8, PH), (XB + 0.0, YM + 0.4, z0 + PH / 2), m_chumbo, cPred)
    box(F('B_ParedeEsq'), (0.25, 1.1, PH), (xb, 7.55, z0 + PH / 2), m_creme, cPred)
    box(F('B_Peitoril'), (0.25, 3.2, 0.8), (xb, 9.8, z0 + 0.6), m_creme, cPred)
    box(F('B_Verga'), (0.25, 3.2, 0.6), (xb, 9.8, z0 + PH - 0.4), m_creme, cPred)
    box(F('B_ParedeDir'), (0.25, 1.3, PH), (xb, 12.05, z0 + PH / 2), m_creme, cPred)
    box(F('B_Vidro'), (0.04, 3.2, 1.55), (XB - 0.06, 9.8, z0 + 1.575), m_vidro, cPred, bevel=0)
    for i, yy in enumerate([8.2, 9.8, 11.4]):
        box(F(f'B_Caixilho_V{i}'), (0.07, 0.07, 1.6), (XB - 0.04, yy, z0 + 1.575), m_branco, cPred, bevel=0.01)
    for i, zz in enumerate([0.8, 1.575, 2.35]):
        box(F(f'B_Caixilho_H{i}'), (0.07, 3.2, 0.07), (XB - 0.04, 9.8, z0 + zz), m_branco, cPred, bevel=0.01)
    cb = box(F('B_Cobogo'), (1.0, 0.08, 2.5), (XB + 0.02, 7.55, z0 + 1.45), m_cob, cPred, bevel=0)
    cb.rotation_euler.z = rad(90)
    box(F('B_Sacada'), (0.9, 3.6, 0.16), (XB + 0.4, 9.8, z0 + 0.08), m_branco, cPred)
    box(F('B_SacadaGuarda'), (0.05, 3.6, 0.35), (XB + 0.82, 9.8, z0 + 0.34), m_branco, cPred)
    box(F('B_Fundo'), (0.04, 3.2, 1.55), (XB - 0.9, 9.8, z0 + 1.575), m_janela_acesa if random.random() < 0.45 else m_interno, cPred, bevel=0)
    # ---- lateral para a rua (-Y): 2 janelinhas quadradas por andar
    for i, xx in enumerate([-13.6, -10.9]):
        box(F(f'Lateral_Janela_{i}'), (0.9, 0.04, 0.9), (xx, Y0 - 0.0, z0 + 1.6), m_vidro, cPred, bevel=0)
        box(F(f'Lateral_Moldura_{i}'), (1.1, 0.06, 1.1), (xx, Y0 + 0.02, z0 + 1.6), m_branco, cPred)
        box(F(f'Lateral_Luz_{i}'), (0.9, 0.04, 0.9), (xx, Y0 + 0.2, z0 + 1.6), m_janela_acesa if random.random() < 0.4 else m_interno, cPred, bevel=0)
# cobertura preta rugosa, escalonada
box('MQ_Predio_Cobertura_A', (XA - XW + 0.4, YM - Y0 + 0.3, 0.45), ((XW + XA) / 2 + 0.1, (Y0 + YM) / 2, TOP + 0.22), m_teto, cPred, bevel=0.06)
box('MQ_Predio_Cobertura_B', (XB - XW + 0.4, Y1 - YM + 0.3, 0.45), ((XW + XB) / 2 + 0.1, (YM + Y1) / 2, TOP + 0.22), m_teto, cPred, bevel=0.06)
box('MQ_Predio_Entrada_Calcada', (4.0, 3.0, 0.1), (-11.2, -1.8, 0.05), mat('MAT_MQ_CalcadaPredio', hexc('#C8C0B4'), 0.8), cPred, bevel=0)
