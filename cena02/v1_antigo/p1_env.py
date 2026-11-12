# Parte 1 - Ambientes: Portaria, Garagem, Apartamento
# ======================================================== PORTARIA
cP = col('ENV_Portaria')
m_asph = mat('MAT_Asfalto', hexc('#4A4C4F'), 0.85)
m_side = mat('MAT_Calcada', hexc('#8A8A86'), 0.9)
m_conc = mat('MAT_Concreto', hexc('#9A9A96'), 0.9)
m_conc_d = mat('MAT_Concreto_Escuro', hexc('#6E6F70'), 0.9)
m_wallP = mat('MAT_Muro', hexc('#B7B2A6'), 0.95)
m_smoke = mat('MAT_VidroFume', hexc('#20262B'), 0.05, alpha=0.55)
m_sil = mat('MAT_Silhueta', hexc('#111214'), 0.9)
m_line = mat('MAT_Faixa', hexc('#D9D4C2'), 0.7)
m_sign = mat('MAT_Placa', hexc('#7F8C86'), 0.8)
m_signtxt = mat('MAT_PlacaTexto', hexc('#C9C2A8'), 0.9)
m_dark = mat('MAT_Tunel', hexc('#08090A'), 1.0)
m_build = mat('MAT_Predio', hexc('#A3A39D'), 0.9)
m_win = mat('MAT_JanelaPredio', hexc('#3B4650'), 0.2)
m_tree = mat('MAT_Arvore', hexc('#4F5E4A'), 0.9)
m_trunk = mat('MAT_Tronco', hexc('#4A3D33'), 0.9)
m_metal = mat('MAT_MetalCinza', hexc('#5F6366'), 0.4, 0.8)

# Chão com abertura para a rampa (x -3.5..3.5, y 6..24)
box('ENV_Portaria_Chao_Sul', (200, 106, 0.2), (0, -47, -0.1), m_asph, cP)
box('ENV_Portaria_Chao_Norte', (200, 80, 0.2), (0, 64, -0.1), m_side, cP)
box('ENV_Portaria_Chao_L', (96.5, 18, 0.2), (-51.75, 15, -0.1), m_side, cP)
box('ENV_Portaria_Chao_R', (96.5, 18, 0.2), (51.75, 15, -0.1), m_side, cP)
box('ENV_Portaria_Pista', (7, 6, 0.21), (0, 3, -0.1), m_asph, cP)
# calçadas da rua de acesso
box('ENV_Portaria_Calcada_L', (3, 60, 0.15), (-5.0, -30, 0.075), m_side, cP)
box('ENV_Portaria_Calcada_R', (3, 60, 0.15), (5.0, -30, 0.075), m_side, cP)
for i in range(10):
    box(f'ENV_Portaria_Faixa_{i:02d}', (0.15, 2.0, 0.01), (0, -6 - i * 5, 0.005), m_line, cP)
box('ENV_Portaria_FaixaPare', (7, 0.35, 0.01), (0, -1.6, 0.006), m_line, cP)

# Rampa de descida (12°) para a garagem
L_r = 14.0; drop = 3.0
ang = math.atan2(drop, L_r)
rp = box('ENV_Portaria_Rampa', (7, math.hypot(L_r, drop), 0.3), (0, 6 + L_r / 2, -drop / 2 - 0.15), m_conc_d, cP)
rp.rotation_euler = (-ang, 0, 0)
box('ENV_Portaria_RampaFundo', (7, 12, 0.3), (0, 26, -3.15), m_conc_d, cP)
for sx in (-1, 1):
    box(f'ENV_Portaria_RampaMuro_{"L" if sx < 0 else "R"}', (0.3, 24, 4.0), (sx * 3.65, 18, -1.2), m_conc, cP)
box('ENV_Portaria_TunelTeto', (7.6, 10, 0.4), (0, 25, 0.2), m_conc, cP)
box('ENV_Portaria_TunelBoca', (7.0, 0.2, 2.6), (0, 30, -1.8), m_dark, cP)
box('ENV_Portaria_TunelVerga', (7.0, 0.3, 0.9), (0, 20.1, -0.25), m_conc, cP)
text('ENV_Portaria_TxtGaragem', 'GARAGEM', 0.45, (0, 19.93, -0.25), (90, 0, 0), m_signtxt, cP)

# Muro do condomínio + placa desbotada
box('ENV_Portaria_Muro_L', (24, 0.35, 2.6), (-19, 1.2, 1.3), m_wallP, cP, bevel=0.02)
box('ENV_Portaria_Muro_R', (24, 0.35, 2.6), (16.5, 1.2, 1.3), m_wallP, cP, bevel=0.02)
box('ENV_Portaria_Placa', (5.2, 0.06, 0.7), (9.5, 1.0, 1.75), m_sign, cP, bevel=0.01)
text('ENV_Portaria_PlacaTexto', 'CONDOMÍNIO RESIDENCIAL', 0.34, (9.5, 0.96, 1.72), (90, 0, 0), m_signtxt, cP)

# Guarita: concreto + vidro fumê + porteiro em silhueta
gx, gy = -5.6, -1.2
box('ENV_Portaria_Guarita_Base', (3.0, 3.0, 1.0), (gx, gy, 0.5), m_conc, cP, bevel=0.03)
box('ENV_Portaria_Guarita_Fundo', (3.0, 0.2, 1.6), (gx, gy + 1.4, 1.8), m_conc, cP)
box('ENV_Portaria_Guarita_LadoL', (0.2, 3.0, 1.6), (gx - 1.4, gy, 1.8), m_conc, cP)
for i, (px, py) in enumerate([(gx + 1.4, gy - 1.4), (gx - 1.4, gy - 1.4), (gx + 1.4, gy + 1.4)]):
    box(f'ENV_Portaria_Guarita_Pilar_{i}', (0.2, 0.2, 1.6), (px, py, 1.8), m_conc, cP)
box('ENV_Portaria_Guarita_VidroFrente', (2.6, 0.04, 1.5), (gx, gy - 1.42, 1.8), m_smoke, cP)
box('ENV_Portaria_Guarita_VidroLado', (0.04, 2.6, 1.5), (gx + 1.42, gy, 1.8), m_smoke, cP)
box('ENV_Portaria_Guarita_Teto', (3.6, 3.6, 0.25), (gx, gy, 2.72), m_conc, cP, bevel=0.03)
sphere('ENV_Portaria_Porteiro_Cabeca', (0.13, 0.14, 0.16), (gx + 0.3, gy, 1.72), m_sil, cP)
sphere('ENV_Portaria_Porteiro_Corpo', (0.28, 0.2, 0.38), (gx + 0.3, gy, 1.25), m_sil, cP)

# Cancela: pivô na ponta (empty) -> braço listrado
m_canc = mat('MAT_Cancela', (1, 1, 1), 0.5)
nt = m_canc.node_tree
tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
mth = nt.nodes.new('ShaderNodeMath'); mth.operation = 'MULTIPLY'; mth.inputs[1].default_value = 1.0 / 0.6
frc = nt.nodes.new('ShaderNodeMath'); frc.operation = 'FRACT'
ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation = 'CONSTANT'
ramp.color_ramp.elements[0].color = (*hexc('#B3261E'), 1)
ramp.color_ramp.elements[1].position = 0.5
ramp.color_ramp.elements[1].color = (*hexc('#E8E6E0'), 1)
nt.links.new(tc.outputs['Object'], sep.inputs[0]); nt.links.new(sep.outputs['X'], mth.inputs[0])
nt.links.new(mth.outputs[0], frc.inputs[0]); nt.links.new(frc.outputs[0], ramp.inputs[0])
nt.links.new(ramp.outputs['Color'], bsdf(m_canc).inputs['Base Color'])
box('ENV_Portaria_Cancela_Poste', (0.35, 0.35, 1.05), (-3.75, -0.2, 0.52), m_metal, cP, bevel=0.02)
piv = empty('ENV_Portaria_Cancela_Pivo', (-3.6, -0.2, 1.0), cP, 0.4, 'ARROWS')
arm_ = box('ENV_Portaria_Cancela_Braco', (6.9, 0.09, 0.09), (3.55, 0, 0), m_canc, cP, parent=piv)
cyl('ENV_Portaria_Cancela_Apoio', 0.05, 0.9, (3.35, -0.2, 0.45), m_metal, cP)

# Prédios ao fundo, árvores e postes
for i, (bx, by, w_, d_, h_) in enumerate([(-22, 40, 14, 12, 34), (-4, 52, 16, 12, 44), (18, 42, 13, 12, 30),
                                          (34, 60, 14, 14, 38), (-38, 58, 12, 12, 26)]):
    b_ = box(f'ENV_Portaria_Predio_{i}', (w_, d_, h_), (bx, by, h_ / 2), m_build, cP)
    for fl in range(3, int(h_), 3):
        box(f'ENV_Portaria_Predio_{i}_Janelas_{fl:02d}', (w_ * 0.9, 0.05, 1.1), (bx, by - d_ / 2 - 0.02, fl), m_win, cP)
for i, (tx, ty) in enumerate([(-9, -6), (-9, -16), (-9, -26), (9, -8), (9, -20), (12, 6), (-14, 6)]):
    cyl(f'ENV_Portaria_Arvore_{i}_Tronco', 0.15, 2.4, (tx, ty, 1.2), m_trunk, cP, segs=8)
    sphere(f'ENV_Portaria_Arvore_{i}_Copa', (1.4, 1.4, 1.7), (tx, ty, 3.6), m_tree, cP, segs=(10, 6))
for i, py in enumerate([-8, -22, -36]):
    cyl(f'ENV_Portaria_Poste_{i}', 0.08, 6, (-6.8, py, 3), m_metal, cP, segs=8)

# Névoa leve (só na portaria): cubo de volume com Volume Scatter 0.005
fog = box('ENV_Portaria_Nevoa', (140, 140, 40), (0, 10, 19.5), None, cP)
m_fog = new_mat('MAT_Nevoa', principled=False)
nt = m_fog.node_tree
vs = nt.nodes.new('ShaderNodeVolumeScatter'); vs.inputs['Density'].default_value = 0.005
vs.inputs['Color'].default_value = (*hexc('#C9CFD6'), 1)
nt.links.new(vs.outputs[0], mat_out(m_fog).inputs['Volume'])
fog.data.materials.append(m_fog)
fog.display_type = 'BOUNDS'

# ======================================================== GARAGEM (subsolo)
cG = col('ENV_Garagem')
m_gfloor = mat('MAT_PisoGaragem', hexc('#5E5F5C'), 0.75)
m_gceil = mat('MAT_TetoGaragem', hexc('#7A7B78'), 0.95)
m_gwall = mat('MAT_ParedeGaragem', hexc('#8C8C86'), 0.95)
m_white = mat('MAT_FaixaVaga', hexc('#E2E2DA'), 0.6)
m_num = mat('MAT_NumeroVaga', hexc('#F0EFE6'), 0.6)
m_oil = mat('MAT_Oleo', hexc('#0E0F10'), 0.12, coat=0.6)
m_pipe = mat('MAT_Cano', hexc('#8F9497'), 0.35, 0.7)
m_pipe_r = mat('MAT_CanoVermelho', hexc('#9C2A22'), 0.4)
m_ext = mat('MAT_Extintor', hexc('#C0201A'), 0.3)
m_black = mat('MAT_PretoFosco', hexc('#141414'), 0.6)
m_tube = mat('MAT_Fluorescente', hexc('#E8F5E0'), 0.3, emit=hexc('#E8F5E0'), emit_str=6.0)
m_tube_f = mat('MAT_Fluorescente_Pisca', hexc('#E8F5E0'), 0.3, emit=hexc('#E8F5E0'), emit_str=6.0)

# listras amarelo/preto em diagonal para pilares
m_stripe = mat('MAT_PilarListrado', (1, 1, 1), 0.7)
nt = m_stripe.node_tree
tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
add = nt.nodes.new('ShaderNodeMath'); add.operation = 'ADD'
mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 5.0
frc = nt.nodes.new('ShaderNodeMath'); frc.operation = 'FRACT'
ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation = 'CONSTANT'
ramp.color_ramp.elements[0].color = (*hexc('#E3B21B'), 1)
ramp.color_ramp.elements[1].position = 0.5
ramp.color_ramp.elements[1].color = (*hexc('#151515'), 1)
low = nt.nodes.new('ShaderNodeMath'); low.operation = 'GREATER_THAN'; low.inputs[1].default_value = 1.1
mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
sock(mix.inputs, 'B').default_value = (*hexc('#8C8C86'), 1)
nt.links.new(tc.outputs['Object'], sep.inputs[0])
nt.links.new(sep.outputs['Z'], add.inputs[0]); nt.links.new(sep.outputs['X'], add.inputs[1])
nt.links.new(add.outputs[0], mul.inputs[0]); nt.links.new(mul.outputs[0], frc.inputs[0])
nt.links.new(frc.outputs[0], ramp.inputs[0])
# objeto com origem no chão: acima de 1.1 m vira concreto
nt.links.new(sep.outputs['Z'], low.inputs[0])
nt.links.new(low.outputs[0], mix.inputs['Factor'])
nt.links.new(ramp.outputs['Color'], sock(mix.inputs, 'A'))
nt.links.new(sock(mix.outputs, 'Result'), bsdf(m_stripe).inputs['Base Color'])

H = 2.4
box('ENV_Garagem_Piso', (18, 28, 0.2), G(0, 0, -0.1), m_gfloor, cG)
box('ENV_Garagem_Teto', (18, 28, 0.25), G(0, 0, H + 0.125), m_gceil, cG)
box('ENV_Garagem_Parede_Oeste', (0.3, 28, H), G(-9.15, 0, H / 2), m_gwall, cG)
box('ENV_Garagem_Parede_Leste', (0.3, 28, H), G(9.15, 0, H / 2), m_gwall, cG)
box('ENV_Garagem_Parede_Norte', (18, 0.3, H), G(0, 14.15, H / 2), m_gwall, cG)
box('ENV_Garagem_Parede_Sul_L', (7.5, 0.3, H), G(-5.25, -14.15, H / 2), m_gwall, cG)
box('ENV_Garagem_Parede_Sul_R', (6.0, 0.3, H), G(6.0, -14.15, H / 2), m_gwall, cG)
box('ENV_Garagem_Rampa_Entrada', (4.5, 8, 0.2), G(0.75, -18, 0.6), m_gfloor, cG, rot=(-8, 0, 0))
box('ENV_Garagem_Rampa_Teto', (4.5, 8, 0.2), G(0.75, -18, 3.3), m_gceil, cG)
box('ENV_Garagem_Rampa_ParedeL', (0.2, 8, 3.5), G(-1.6, -18, 1.6), m_gwall, cG)
box('ENV_Garagem_Rampa_ParedeR', (0.2, 8, 3.5), G(3.1, -18, 1.6), m_gwall, cG)
box('ENV_Garagem_Rampa_Fundo', (4.5, 0.2, 3.5), G(0.75, -22, 1.6), m_dark, cG)

# Vagas: fileira oeste 10..16 (x -8..-3), fileira leste 20..26 (x 3..8)
SLOT_W = 2.6
slot_y = {n: (n - 13) * SLOT_W for n in range(10, 17)}
for side, x0, x1, nums in (('W', -8.6, -3.0, range(10, 17)), ('E', 3.0, 8.6, range(20, 27))):
    for i, n in enumerate(nums):
        yc = (i - 3) * SLOT_W
        for edge in (-1, 1):
            box(f'ENV_Garagem_Linha_{n}_{edge}', (x1 - x0, 0.1, 0.01), G((x0 + x1) / 2, yc + edge * SLOT_W / 2, 0.006), m_white, cG)
        fx = x1 - 0.9 if side == 'W' else x0 + 0.9
        rz = 90 if side == 'W' else -90
        sz = 0.75 if n in (12, 13, 14) else 0.55
        text(f'ENV_Garagem_Num_{n}', str(n), sz, G(fx, yc, 0.012), (0, 0, rz), m_num, cG)
        wx = -8.98 if side == 'W' else 8.98
        text(f'ENV_Garagem_NumParede_{n}', str(n), 0.45, G(wx, yc, 1.55), (90, 0, 90 if side == 'W' else -90), m_num, cG)

# Destaque da vaga 14 (pintura mais nova + placa no pilar)
box('ENV_Garagem_Vaga14_Destaque', (0.9, 1.6, 0.008), G(-3.9, slot_y[14], 0.004), mat('MAT_Vaga14Fundo', hexc('#2F5D8A'), 0.6), cG)

# Pilares com faixas (origem no chão)
pil_y = [-7.8 - 1.3, -2.6 - 1.3, 2.6 + 1.3, 7.8 + 1.3]
for i, py in enumerate(pil_y):
    for sx in (-1, 1):
        p_ = box(f'ENV_Garagem_Pilar_{i}_{"W" if sx < 0 else "E"}', (0.45, 0.45, H), G(sx * 3.15, py, 0), m_stripe, cG)
        for v in p_.data.vertices: v.co.z += H / 2

# Canos no teto
for i, (px, m_) in enumerate([(-2.2, m_pipe), (-1.8, m_pipe_r), (2.6, m_pipe)]):
    cyl(f'ENV_Garagem_Cano_{i}', 0.07 if m_ is m_pipe else 0.05, 28, G(px, 0, 2.18), m_, cG, rot=(90, 0, 0), segs=12)
for i, py in enumerate([-10, -3, 4, 11]):
    cyl(f'ENV_Garagem_CanoX_{i}', 0.05, 18, G(0, py, 2.28), m_pipe, cG, rot=(0, 90, 0), segs=12)

# Manchas de óleo
for i in range(14):
    ox = random.choice([random.uniform(-7, -3.6), random.uniform(-2.5, 2.5), random.uniform(3.6, 7)])
    oy = random.uniform(-12, 12)
    r_ = random.uniform(0.2, 0.6)
    cyl(f'ENV_Garagem_Oleo_{i:02d}', r_, 0.004, G(ox, oy, 0.004), m_oil, cG,
        rot=(0, 0, random.uniform(0, 90)), segs=16).scale = (1, random.uniform(0.5, 1), 1)

# Extintor no pilar perto da vaga 14
ex_p = G(-2.86, 3.9, 0)
cyl('ENV_Garagem_Extintor', 0.09, 0.5, (ex_p[0], ex_p[1], 0.75), m_ext, cG, segs=16)
sphere('ENV_Garagem_Extintor_Topo', 0.09, (ex_p[0], ex_p[1], 1.0), m_ext, cG, segs=(16, 8))
box('ENV_Garagem_Extintor_Valvula', (0.05, 0.12, 0.06), (ex_p[0], ex_p[1], 1.1), m_black, cG)
box('ENV_Garagem_Extintor_Placa', (0.02, 0.3, 0.3), (ex_p[0] - 0.05, ex_p[1], 1.45), m_ext, cG)

# Luminárias tubulares (6) - a luz fica em LIGHTS
TUBES = [(-1.7, -9.0), (-1.7, -3.0), (-1.2, 4.6), (1.8, -6.0), (1.8, 0.0), (1.8, 7.0)]
FLICKER = 2  # luminária perto da vaga 14 (pisca)
for i, (tx, ty) in enumerate(TUBES):
    m_ = m_tube_f if i == FLICKER else m_tube
    box(f'ENV_Garagem_Luminaria_{i}_Calha', (0.18, 1.3, 0.05), G(tx, ty, H - 0.03), m_metal, cG)
    cyl(f'ENV_Garagem_Luminaria_{i}_Tubo', 0.025, 1.2, G(tx, ty, H - 0.09), m_, cG, rot=(90, 0, 0), segs=10)

# ======================================================== APARTAMENTO (sala, noite)
cA = col('ENV_Apartamento')
m_wood = mat('MAT_PisoMadeira', hexc('#5B4636'), 0.45)
m_aw = mat('MAT_ParedeSala', hexc('#B9A992'), 0.9)
m_ceilA = mat('MAT_TetoSala', hexc('#C9C1B4'), 0.9)
m_sofa = mat('MAT_Sofa', hexc('#3E4144'), 0.85)
m_pill = mat('MAT_Almofada', hexc('#7A5A45'), 0.9)
m_pill2 = mat('MAT_Almofada2', hexc('#4E6170'), 0.9)
m_rug = mat('MAT_Tapete', hexc('#6B6157'), 1.0)
m_rack = mat('MAT_Rack', hexc('#3A2E25'), 0.5)
m_tvb = mat('MAT_TV_Moldura', hexc('#0B0B0C'), 0.3)
m_door = mat('MAT_Porta', hexc('#6A5240'), 0.5)
m_frame = mat('MAT_Batente', hexc('#DCD3C4'), 0.6)
m_glass = mat('MAT_VidroJanela', hexc('#1B2430'), 0.02, alpha=0.18)
m_shade = mat('MAT_Cupula', hexc('#E9D3B0'), 0.8, emit=hexc('#FFB46B'), emit_str=1.5)
m_brass = mat('MAT_Latao', hexc('#9C7A3C'), 0.3, 0.9)
m_tbl = mat('MAT_Mesinha', hexc('#4A3A2E'), 0.4)

W_, Dp, HA = 6.0, 5.0, 2.7
box('ENV_Apartamento_Piso', (W_, Dp, 0.1), A(0, 0, -0.05), m_wood, cA)
box('ENV_Apartamento_Teto', (W_, Dp, 0.1), A(0, 0, HA + 0.05), m_ceilA, cA)
box('ENV_Apartamento_Parede_TV', (W_, 0.15, HA), A(0, 2.575, HA / 2), m_aw, cA)
box('ENV_Apartamento_Parede_Oeste', (0.15, Dp, HA), A(-3.075, 0, HA / 2), m_aw, cA)
# parede leste com vão de porta (y 0.15..1.05, z 0..2.1)
box('ENV_Apartamento_Parede_Leste_A', (0.15, 2.65, HA), A(3.075, -1.175, HA / 2), m_aw, cA)
box('ENV_Apartamento_Parede_Leste_B', (0.15, 1.45, HA), A(3.075, 1.775, HA / 2), m_aw, cA)
box('ENV_Apartamento_Parede_Leste_C', (0.15, 0.9, 0.6), A(3.075, 0.6, 2.4), m_aw, cA)
box('ENV_Apartamento_Corredor', (1.5, 2.0, 0.1), A(3.9, 0.6, -0.05), m_conc_d, cA)
box('ENV_Apartamento_Corredor_Fundo', (0.1, 2.0, HA), A(4.6, 0.6, HA / 2), mat('MAT_Corredor', hexc('#4F4A43'), 0.9), cA)
for n_, (bx_, by_, sx_, sy_, sz_) in {'Top': (3.0, 0.6, 0.18, 1.02, 0.08), 'L': (3.0, 0.12, 0.18, 0.06, 2.12),
                                     'R': (3.0, 1.08, 0.18, 0.06, 2.12)}.items():
    box(f'ENV_Apartamento_Batente_{n_}', (sx_, sy_, sz_), A(bx_, by_, 2.14 if n_ == 'Top' else 1.06), m_frame, cA)
# Porta (pivô na dobradiça)
dpiv = empty('ENV_Apartamento_Porta_Pivo', A(2.99, 0.16, 0), cA, 0.3, 'ARROWS')
box('ENV_Apartamento_Porta', (0.05, 0.88, 2.08), (0, 0.44, 1.04), m_door, cA, parent=dpiv)
sphere('ENV_Apartamento_Porta_Macaneta', 0.035, (-0.05, 0.8, 1.0), m_brass, cA, parent=dpiv)

# parede sul com janela (x -1.1..1.1, z 0.95..2.25)
box('ENV_Apartamento_Parede_Sul_L', (1.9, 0.15, HA), A(-2.05, -2.575, HA / 2), m_aw, cA)
box('ENV_Apartamento_Parede_Sul_R', (1.9, 0.15, HA), A(2.05, -2.575, HA / 2), m_aw, cA)
box('ENV_Apartamento_Parede_Sul_Baixo', (2.2, 0.15, 0.95), A(0, -2.575, 0.475), m_aw, cA)
box('ENV_Apartamento_Parede_Sul_Cima', (2.2, 0.15, 0.45), A(0, -2.575, 2.475), m_aw, cA)
box('ENV_Apartamento_Janela_Vidro', (2.2, 0.02, 1.3), A(0, -2.6, 1.6), m_glass, cA)
box('ENV_Apartamento_Janela_Caixilho', (0.05, 0.06, 1.3), A(0, -2.6, 1.6), m_frame, cA)
# cidade lá fora (luzes que viram bokeh)
m_night = mat('MAT_CeuNoite', hexc('#0A0E18'), 1.0, emit=hexc('#141C2E'), emit_str=0.6)
box('ENV_Apartamento_Cidade_Fundo', (60, 0.2, 30), A(0, -30, 6), m_night, cA)
m_bld = mat('MAT_PredioNoite', hexc('#05070B'), 1.0)
cl_cols = [hexc('#FFD39A'), hexc('#FFC27A'), hexc('#CFE3FF'), hexc('#FFE7BF')]
cl_mats = [mat(f'MAT_LuzCidade_{i}', c_, 0.5, emit=c_, emit_str=8.0) for i, c_ in enumerate(cl_cols)]
for i in range(8):
    bx_ = -14 + i * 4 + random.uniform(-1, 1); hh = random.uniform(6, 16)
    box(f'ENV_Apartamento_PredioNoite_{i}', (3.2, 2.0, hh), A(bx_, -20 - random.uniform(0, 4), hh / 2 - 3), m_bld, cA)
for i in range(160):
    lx = random.uniform(-16, 16); lz = random.uniform(-2, 11)
    box(f'ENV_Apartamento_LuzCidade_{i:03d}', (0.35, 0.05, 0.25), A(lx, -18.5 - random.uniform(0, 2), lz),
        random.choice(cl_mats), cA)

# Sofá 3 lugares (assento topo z=0.45)
box('ENV_Apartamento_Sofa_Base', (2.3, 0.95, 0.3), A(0, -1.95, 0.2), m_sofa, cA, bevel=0.04)
box('ENV_Apartamento_Sofa_Encosto', (2.3, 0.25, 0.55), A(0, -2.35, 0.65), m_sofa, cA, bevel=0.06)
for sx in (-1, 1):
    box(f'ENV_Apartamento_Sofa_Braco_{"L" if sx < 0 else "R"}', (0.22, 0.95, 0.62), A(sx * 1.26, -1.95, 0.31), m_sofa, cA, bevel=0.06)
for i, cx in enumerate([-0.72, 0.0, 0.72]):
    c_ = box(f'ENV_Apartamento_Sofa_Assento_{i}', (0.71, 0.75, 0.14), A(cx, -1.88, 0.0), m_sofa, cA, bevel=0.05)
    for v in c_.data.vertices: v.co.z += 0.07
    c_.location.z = 0.36
    b_ = box(f'ENV_Apartamento_Sofa_Costas_{i}', (0.71, 0.18, 0.45), A(cx, -2.18, 0.72), m_sofa, cA, bevel=0.07)
box('ENV_Apartamento_Almofada_L', (0.42, 0.14, 0.4), A(-0.95, -2.02, 0.68), m_pill, cA, rot=(-12, 0, 18), bevel=0.08)
box('ENV_Apartamento_Almofada_R', (0.42, 0.14, 0.4), A(0.95, -2.02, 0.68), m_pill2, cA, rot=(-12, 0, -15), bevel=0.08)
box('ENV_Apartamento_Tapete', (2.6, 1.8, 0.02), A(0, -0.4, 0.01), m_rug, cA)

# Rack + TV 55" (1.22 x 0.69)
box('ENV_Apartamento_Rack', (1.9, 0.42, 0.45), A(0, 2.25, 0.225), m_rack, cA, bevel=0.01)
box('ENV_Apartamento_TV_Moldura', (1.26, 0.05, 0.73), A(0, 2.4, 1.15), m_tvb, cA, bevel=0.005)
box('ENV_Apartamento_TV_Pe', (0.3, 0.2, 0.02), A(0, 2.3, 0.46), m_tvb, cA)

# Abajur ao lado do sofá
box('ENV_Apartamento_MesaAbajur', (0.45, 0.45, 0.55), A(-1.65, -2.0, 0.275), m_tbl, cA)
cyl('ENV_Apartamento_Abajur_Base', 0.09, 0.05, A(-1.65, -2.0, 0.575), m_brass, cA)
cyl('ENV_Apartamento_Abajur_Haste', 0.015, 0.45, A(-1.65, -2.0, 0.8), m_brass, cA, segs=8)
cyl('ENV_Apartamento_Abajur_Cupula', 0.2, 0.28, A(-1.65, -2.0, 1.12), m_shade, cA, r2=0.13, segs=24)

# Mesinha lateral perto da porta + fruteira
box('ENV_Apartamento_MesaLateral_Tampo', (0.45, 0.9, 0.04), A(2.72, -0.55, 0.76), m_tbl, cA)
for i, (lx, ly) in enumerate([(-0.18, -0.4), (0.18, -0.4), (-0.18, 0.4), (0.18, 0.4)]):
    box(f'ENV_Apartamento_MesaLateral_Pe_{i}', (0.04, 0.04, 0.74), A(2.72 + lx, -0.55 + ly, 0.37), m_tbl, cA)
fb = sphere('ENV_Apartamento_Fruteira', (0.16, 0.16, 0.07), A(2.72, -0.8, 0.83), mat('MAT_Ceramica', hexc('#D8D2C4'), 0.3), cA)
for i, (fx, fy, fc_) in enumerate([(0.0, 0.0, '#C0392B'), (0.07, 0.04, '#E6B83A'), (-0.06, 0.05, '#7FA43A'), (0.02, -0.07, '#D9822B')]):
    sphere(f'ENV_Apartamento_Fruta_{i}', 0.045, A(2.72 + fx, -0.8 + fy, 0.89), mat(f'MAT_Fruta_{i}', hexc(fc_), 0.4), cA, segs=(12, 8))
