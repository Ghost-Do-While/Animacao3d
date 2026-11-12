# Parte 2 - Veículos e props
cV = col('VEHICLES'); cPr = col('PROPS')
m_tire = mat('MAT_Pneu', hexc('#151515'), 0.8)
m_hub = mat('MAT_Calota', hexc('#A9ADB0'), 0.3, 0.9)
m_bump = mat('MAT_ParaChoque', hexc('#2A2B2C'), 0.6)
m_cglass = mat('MAT_VidroCarro', hexc('#2A333B'), 0.03, alpha=0.28)
m_cglass_d = mat('MAT_VidroCarroEscuro', hexc('#1A2026'), 0.05, alpha=0.75)
m_seat = mat('MAT_Banco', hexc('#2C2D30'), 0.85)
m_dash = mat('MAT_Painel', hexc('#1E1F21'), 0.55)
m_plate = mat('MAT_Placa_Carro', hexc('#E8E8E0'), 0.5)
WHEEL_R = 0.33

def build_car(name, color, interior=False, length=4.0, sedan=False, c=None):
    c = c or cV
    P = lambda n: f'VEH_{name}_{n}'
    root = empty(f'VEH_{name}', (0, 0, 0), c, 1.2, 'ARROWS')
    body = mat(f'MAT_Pintura_{name}', hexc(color), 0.3, 0.5, coat=1.0)
    brake = mat(f'MAT_Lanterna_{name}', hexc('#4A0806'), 0.3, emit=hexc('#FF1A0A'), emit_str=0.0)
    head = mat(f'MAT_Farol_{name}', hexc('#CFCFCF'), 0.1, emit=hexc('#FFF4E0'), emit_str=0.0)
    hl = length / 2
    parts = {'root': root, 'brake': brake, 'head': head}
    if interior:
        box(P('Frente'), (1.76, hl - 0.75, 0.6), (0, (0.75 + hl) / 2, 0.62), body, c, bevel=0.08, parent=root)
        box(P('Traseira'), (1.76, hl - 0.55, 0.6), (0, (-hl - 0.55) / 2, 0.62), body, c, bevel=0.08, parent=root)
        box(P('Assoalho'), (1.7, 1.32, 0.1), (0, 0.1, 0.37), m_dash, c, parent=root)
        box(P('LadoDireito'), (0.06, 1.32, 0.56), (0.85, 0.1, 0.62), body, c, parent=root)
        dp = empty(P('Porta_Pivo'), (-0.86, 0.75, 0.62), c, 0.3, 'ARROWS', parent=root)
        box(P('Porta'), (0.06, 1.3, 0.56), (0, -0.65, 0), body, c, parent=dp, bevel=0.02)
        quad(P('Porta_Vidro'), [(0.07, 0.1, 0.3), (0.07, -1.3, 0.3), (0.15, -1.3, 0.91), (0.15, -0.6, 0.91)], m_cglass, c, parent=dp)
        parts['door'] = dp
        # interior
        for sx, nm in ((-0.4, 'Motorista'), (0.4, 'Passageiro')):
            box(P(f'Banco{nm}_Assento'), (0.5, 0.5, 0.12), (sx, -0.15, 0.48), m_seat, c, bevel=0.04, parent=root)
            box(P(f'Banco{nm}_Encosto'), (0.5, 0.12, 0.65), (sx, -0.5, 0.86), m_seat, c, rot=(15, 0, 0), bevel=0.04, parent=root)
            box(P(f'Banco{nm}_Apoio'), (0.28, 0.1, 0.16), (sx, -0.6, 1.27), m_seat, c, rot=(15, 0, 0), bevel=0.03, parent=root)
        box(P('Painel'), (1.62, 0.36, 0.2), (0, 0.72, 0.9), m_dash, c, bevel=0.04, parent=root)
        box(P('Painel_Instrumentos'), (0.36, 0.05, 0.1), (-0.4, 0.55, 1.0), mat('MAT_Instrumentos', hexc('#0A0A0A'), 0.2, emit=hexc('#6FB7FF'), emit_str=0.6), c, parent=root)
        beam(P('Coluna_Direcao'), (-0.4, 0.62, 0.88), (-0.4, 0.43, 0.97), 0.05, m_dash, c, parent=root)
        torus(P('Volante'), 0.18, 0.022, (-0.4, 0.4, 0.98), m_dash, c, rot=(65, 0, 0), parent=root)
        cyl(P('Volante_Centro'), 0.06, 0.04, (-0.4, 0.41, 0.98), m_dash, c, rot=(65, 0, 0), parent=root)
        box(P('Retrovisor'), (0.25, 0.03, 0.07), (0, 0.27, 1.42), m_dash, c, bevel=0.01, parent=root)
        beam(P('Retrovisor_Haste'), (0, 0.27, 1.45), (0, 0.22, 1.52), 0.015, m_dash, c, parent=root)
    else:
        box(P('Carroceria'), (1.76, length, 0.6), (0, 0, 0.62), body, c, bevel=0.08, parent=root)
    # cabine (colunas + teto + vidros)
    gl = m_cglass if interior else m_cglass_d
    cb, ct = ((-hl + 0.9, -hl + 1.4) if sedan else (-hl + 0.2, -hl + 0.45))
    for sx in (-1, 1):
        s = 'L' if sx < 0 else 'R'
        beam(P(f'ColunaA_{s}'), (sx * 0.8, 0.85, 0.92), (sx * 0.71, 0.15, 1.53), 0.07, body, c, parent=root)
        beam(P(f'ColunaB_{s}'), (sx * 0.8, -0.5, 0.92), (sx * 0.72, -0.5, 1.53), 0.07, body, c, parent=root)
        beam(P(f'ColunaC_{s}'), (sx * 0.8, cb, 0.92), (sx * 0.71, ct, 1.53), 0.09, body, c, parent=root)
    box(P('Teto'), (1.5, 0.15 - ct + 0.04, 0.06), (0, (0.15 + ct) / 2, 1.55), body, c, bevel=0.02, parent=root)
    quad(P('ParaBrisa'), [(-0.8, 0.85, 0.92), (0.8, 0.85, 0.92), (0.71, 0.15, 1.53), (-0.71, 0.15, 1.53)], gl, c, parent=root)
    quad(P('VidroTraseiro'), [(-0.8, cb, 0.92), (0.8, cb, 0.92), (0.71, ct, 1.53), (-0.71, ct, 1.53)], gl, c, parent=root)
    quad(P('VidroLado_R'), [(0.79, 0.85, 0.92), (0.79, cb, 0.92), (0.71, ct, 1.53), (0.71, 0.15, 1.53)], gl, c, parent=root)
    if interior:
        quad(P('VidroLado_L_Tras'), [(-0.79, -0.55, 0.92), (-0.79, cb, 0.92), (-0.71, ct, 1.53), (-0.71, -0.55, 1.53)], gl, c, parent=root)
    else:
        quad(P('VidroLado_L'), [(-0.79, 0.85, 0.92), (-0.79, cb, 0.92), (-0.71, ct, 1.53), (-0.71, 0.15, 1.53)], gl, c, parent=root)
    # para-choques, faróis, lanternas, placas
    box(P('ParaChoque_F'), (1.82, 0.2, 0.22), (0, hl + 0.02, 0.42), m_bump, c, bevel=0.05, parent=root)
    box(P('ParaChoque_T'), (1.82, 0.2, 0.22), (0, -hl - 0.02, 0.42), m_bump, c, bevel=0.05, parent=root)
    for sx in (-1, 1):
        s = 'L' if sx < 0 else 'R'
        box(P(f'Farol_{s}'), (0.36, 0.06, 0.12), (sx * 0.58, hl + 0.01, 0.76), head, c, bevel=0.02, parent=root)
        box(P(f'Lanterna_{s}'), (0.3, 0.06, 0.13), (sx * 0.62, -hl - 0.01, 0.78), brake, c, bevel=0.02, parent=root)
    box(P('Placa_F'), (0.4, 0.02, 0.13), (0, hl + 0.13, 0.45), m_plate, c, parent=root)
    box(P('Placa_T'), (0.4, 0.02, 0.13), (0, -hl - 0.13, 0.45), m_plate, c, parent=root)
    # rodas com driver ligado ao deslocamento em Y
    wy = hl - 0.72
    for sx, sy, s in ((-1, 1, 'FL'), (1, 1, 'FR'), (-1, -1, 'RL'), (1, -1, 'RR')):
        wp = empty(P(f'Roda_{s}_Pivo'), (sx * 0.8, sy * wy, WHEEL_R), c, 0.2, 'CIRCLE', parent=root)
        wp.rotation_mode = 'XYZ'
        cyl(P(f'Roda_{s}_Pneu'), WHEEL_R, 0.23, (0, 0, 0), m_tire, c, rot=(0, 90, 0), segs=20, parent=wp)
        cyl(P(f'Roda_{s}_Calota'), 0.19, 0.24, (0, 0, 0), m_hub, c, rot=(0, 90, 0), segs=5, parent=wp, smooth=False)
        fc = wp.driver_add('rotation_euler', 0)
        drv = fc.driver; drv.type = 'SCRIPTED'
        v = drv.variables.new(); v.name = 'y'; v.type = 'TRANSFORMS'
        t = v.targets[0]; t.id = root; t.transform_type = 'LOC_Y'; t.transform_space = 'WORLD_SPACE'
        drv.expression = f'-y/{WHEEL_R}'
    return parts

CARS = {}
CARS['Marcos'] = build_car('CarroMarcos', '#B8BCC0', interior=True, length=3.9)
for i, (clr, sed) in enumerate([('#6B6E70', True), ('#2F3A44', False), ('#8C8577', True), ('#4C5A4E', False)]):
    CARS[f'Fila{i+1}'] = build_car(f'Fila_{i+1}', clr, sedan=sed, length=4.3 if sed else 3.9)
CARS['Claudio'] = build_car('CarroClaudio', '#6E2424', sedan=True, length=4.3)
CARS['Miguel'] = build_car('CarroMiguel', '#D9D9D2', length=4.0)

# Posições fixas: fila na portaria (frente para +Y, cancela em y=0)
FILA_Y = [-3.0, -8.0, -13.0, -18.0]
MARCOS_FILA_Y = -23.0
for i, y in enumerate(FILA_Y):
    CARS[f'Fila{i+1}']['root'].location = (0.0, y, 0.0)

# Garagem: carros estacionados bem colados
CARS['Claudio']['root'].location = G(-5.7, 2.6, 0); CARS['Claudio']['root'].rotation_euler.z = rad(90)
CARS['Miguel']['root'].location = G(1.4, 6.6, 0); CARS['Miguel']['root'].rotation_euler.z = rad(-162)
park_cols = ['#7A7E82', '#33363A', '#9C978C', '#5B6670', '#2E2E30', '#8A8F86', '#6C5F57', '#A8ACAF', '#3F4A55', '#585A5C']
pc = iter(park_cols)
for n, y in ((10, -7.8), (11, -5.2), (15, 5.2), (16, 7.8)):
    p_ = build_car(f'Garagem_Vaga{n}', next(pc), sedan=(n % 2 == 0), length=4.2 if n % 2 == 0 else 3.9)
    p_['root'].location = G(-5.75, y + random.uniform(-0.12, 0.12), 0); p_['root'].rotation_euler.z = rad(90 + random.uniform(-2, 2))
for n, y in ((20, -7.8), (21, -5.2), (22, -2.6), (24, 2.6), (25, 5.2), (26, 7.8)):
    p_ = build_car(f'Garagem_Vaga{n}', next(pc), sedan=(n % 2 == 1), length=4.2 if n % 2 == 1 else 3.9)
    p_['root'].location = G(5.75, y + random.uniform(-0.12, 0.12), 0); p_['root'].rotation_euler.z = rad(-90 + random.uniform(-2, 2))

# Pisca-alerta do carro do Miguel
m_haz = mat('MAT_PiscaAlerta_Miguel', hexc('#7A4A08'), 0.3, emit=hexc('#FF9A1A'), emit_str=0.0)
for sx in (-1, 1):
    for sy in (-1, 1):
        box(f'VEH_CarroMiguel_Pisca_{sx}{sy}', (0.12, 0.08, 0.06), (sx * 0.85, sy * 2.0, 0.62), m_haz, cV, parent=CARS['Miguel']['root'])

# ---------------------------------------------------------------- PROPS
m_key = mat('MAT_Chave', hexc('#C9C9C2'), 0.25, 1.0)
m_tag = mat('MAT_TagCondominio', hexc('#2F6FB0'), 0.4)
keys_ = empty('PRP_Chaves', A(3.6, 0.6, 1.0), cPr, 0.08, 'SPHERE')
torus('PRP_Chaves_Argola', 0.022, 0.003, (0, 0, 0), m_key, cPr, rot=(90, 0, 0), parent=keys_)
for i, ang_ in enumerate([-25, 0, 25]):
    k_ = box(f'PRP_Chaves_Chave_{i}', (0.012, 0.003, 0.055), (0, 0, -0.045), m_key, cPr, parent=keys_)
    k_.location = (math.sin(rad(ang_)) * 0.045, 0.002 * i, -0.04 * math.cos(rad(ang_)) - 0.02)
    k_.rotation_euler.y = rad(-ang_)
box('PRP_Chaves_Tag', (0.03, 0.006, 0.04), (0, -0.004, -0.04), m_tag, cPr, rot=(0, 40, 0), bevel=0.004, parent=keys_)

m_remote = mat('MAT_Controle', hexc('#121212'), 0.45)
m_red = mat('MAT_BotaoVermelho', hexc('#C8150F'), 0.3, emit=hexc('#FF2A1A'), emit_str=0.3)
m_btn = mat('MAT_BotaoCinza', hexc('#5A5A5A'), 0.5)
remote = box('PRP_ControleRemoto', (0.05, 0.19, 0.022), A(0.62, -1.75, 0.515), m_remote, cPr, bevel=0.008)
cyl('PRP_ControleRemoto_BotaoDesligar', 0.008, 0.006, (0, 0.07, 0.012), m_red, cPr, parent=remote, segs=12)
for i in range(6):
    box(f'PRP_ControleRemoto_Botao_{i}', (0.009, 0.009, 0.004), ((i % 2 - 0.5) * 0.018, 0.03 - (i // 2) * 0.022, 0.012), m_btn, cPr, parent=remote)

# Tela da TV com telejornal fake (geometria emissiva em frente à tela)
SY = 2.372; SZ = 1.15; SW, SH = 1.21, 0.68
m_scr = new_mat('MAT_TV_Tela', principled=False)
nt = m_scr.node_tree
em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.6
tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (*hexc('#0B1E3F'), 1); ramp.color_ramp.elements[1].color = (*hexc('#2D6FB8'), 1)
nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs[0])
nt.links.new(ramp.outputs['Color'], em.inputs['Color']); nt.links.new(em.outputs[0], mat_out(m_scr).inputs['Surface'])
tv = box('PRP_TV_Tela', (SW, 0.003, SH), A(0, SY, SZ), m_scr, cPr)

def emat(name, hx, s=2.0):
    m_ = new_mat(name, principled=False); nt_ = m_.node_tree
    e_ = nt_.nodes.new('ShaderNodeEmission'); e_.inputs['Color'].default_value = (*hexc(hx), 1)
    e_.inputs['Strength'].default_value = s
    nt_.links.new(e_.outputs[0], mat_out(m_).inputs['Surface'])
    return m_
e_white = emat('MAT_TV_Branco', '#F4F4F4', 2.2)
e_red = emat('MAT_TV_Tarja', '#C4161C', 2.2)
e_yel = emat('MAT_TV_Amarelo', '#F2C230', 2.2)
e_navy = emat('MAT_TV_Azul', '#0E2A55', 1.6)
e_skin = emat('MAT_TV_Pele', '#D9A27E', 1.6)
e_suit = emat('MAT_TV_Terno', '#20242C', 1.2)
e_hair = emat('MAT_TV_Cabelo', '#2A1C14', 1.2)
e_blue = emat('MAT_TV_Giroflex_Azul', '#2A6BFF', 6.0)
e_rd = emat('MAT_TV_Giroflex_Verm', '#FF2A2A', 6.0)
e_dark = emat('MAT_TV_Escuro', '#10141C', 1.0)
Yc = SY - 0.004
def tvp(name, size, x, z, m_, dy=0.0):
    return box(f'PRP_TV_{name}', (size[0], 0.002, size[1]), A(x, Yc - dy, SZ + z), m_, cPr)
tvp('LogoFundo', (0.36, 0.07), -0.4, 0.27, e_navy)
text('PRP_TV_Logo', 'JORNAL DA CIDADE', 0.032, A(-0.4, Yc - 0.003, SZ + 0.265), (90, 0, 0), e_white, cPr)
tvp('LogoFaixa', (0.36, 0.008), -0.4, 0.232, e_yel, 0.001)
tvp('AoVivo', (0.11, 0.045), 0.49, 0.28, e_red)
text('PRP_TV_AoVivoTxt', 'AO VIVO', 0.022, A(0.49, Yc - 0.003, SZ + 0.278), (90, 0, 0), e_white, cPr)
# âncora estilizada + mesa
sphere('PRP_TV_Ancora_Cabeca', (0.055, 0.002, 0.068), A(0.24, Yc - 0.002, SZ + 0.08), e_skin, cPr, segs=(24, 6))
sphere('PRP_TV_Ancora_Cabelo', (0.06, 0.002, 0.045), A(0.24, Yc - 0.001, SZ + 0.115), e_hair, cPr, segs=(24, 6))
sphere('PRP_TV_Ancora_Corpo', (0.15, 0.002, 0.12), A(0.24, Yc - 0.001, SZ - 0.07), e_suit, cPr, segs=(24, 6))
tvp('Ancora_Mesa', (0.5, 0.09), 0.24, -0.14, e_navy, 0.003)
# inserto com viatura
tvp('Inserto', (0.42, 0.25), -0.28, 0.02, e_dark)
tvp('Inserto_Borda', (0.44, 0.27), -0.28, 0.02, e_white, -0.0005)
tvp('Viatura_Corpo', (0.26, 0.05), -0.28, -0.03, e_white, 0.001)
tvp('Viatura_Cabine', (0.14, 0.04), -0.29, 0.015, e_white, 0.001)
tvp('Viatura_Faixa', (0.26, 0.012), -0.28, -0.03, e_navy, 0.002)
tvp('Viatura_GiroAzul', (0.03, 0.015), -0.31, 0.043, e_blue, 0.002)
tvp('Viatura_GiroVerm', (0.03, 0.015), -0.27, 0.043, e_rd, 0.002)
# tarja inferior (origem na borda esquerda para entrar da esquerda)
tarja = box('PRP_TV_Tarja', (SW, 0.002, 0.11), (0, 0, 0), e_red, cPr)
for v in tarja.data.vertices: v.co.x += SW / 2
tarja.location = A(-SW / 2, Yc - 0.004, SZ - 0.255)
tag_u = box('PRP_TV_Urgente', (0.17, 0.002, 0.04), A(-0.5, Yc - 0.005, SZ - 0.18), e_yel, cPr)
text('PRP_TV_UrgenteTxt', 'URGENTE', 0.024, A(-0.5, Yc - 0.006, SZ - 0.181), (90, 0, 0), e_red, cPr)
manchete = text('PRP_TV_Manchete', 'Discussão por vaga de garagem termina na delegacia', 0.037,
                A(-0.585, Yc - 0.006, SZ - 0.258), (90, 0, 0), e_white, cPr, align='LEFT')
# TV desligada (preto brilhante) e flash branco de 1 frame
m_off = mat('MAT_TV_Desligada', hexc('#050506'), 0.12)
tv_off = box('PRP_TV_Desligada', (SW, 0.002, SH), A(0, SY - 0.011, SZ), m_off, cPr)
tv_flash = box('PRP_TV_Flash', (SW, 0.002, SH), A(0, SY - 0.013, SZ), emat('MAT_TV_Flash', '#FFFFFF', 25.0), cPr)
