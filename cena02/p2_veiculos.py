# Parte 2 - Carros clássicos da maquete (fixos) + carros animados (fila, Marcos, Claudio, Miguel)
cV = col('VEHICLES_Animados'); cCE = col('Carros_Estacionados')
m_tire = mat('MAT_Pneu', hexc('#151515'), 0.8)
m_hub = mat('MAT_Calota', hexc('#A9ADB0'), 0.3, 0.9)
m_bump = mat('MAT_ParaChoque', hexc('#2A2B2C'), 0.6)
m_cglass = mat('MAT_VidroCarro', hexc('#2A333B'), 0.03, alpha=0.28)
m_cglass_d = mat('MAT_VidroCarroEscuro', hexc('#1A2026'), 0.05, alpha=0.75)
m_seat = mat('MAT_Banco', hexc('#2C2D30'), 0.85)
m_dash = mat('MAT_Painel', hexc('#1E1F21'), 0.55)
m_plate = mat('MAT_Placa_Carro', hexc('#E8E8E0'), 0.5)
m_chrome = mat('MAT_Cromado', hexc('#D9DCDF'), 0.12, 1.0)
WHEEL_R = 0.33

def wheel_driver(wp, root, r):
    fc = wp.driver_add('rotation_euler', 0)
    drv = fc.driver; drv.type = 'SCRIPTED'
    v = drv.variables.new(); v.name = 'o'; v.type = 'SINGLE_PROP'
    v.targets[0].id = root; v.targets[0].data_path = '["odo"]'          # odômetro do carro (distância percorrida, keyada)
    drv.expression = f'-o/{r}'

# ---------------------------------------------------------------- carro moderno (frente = +Y local)
def build_car(name, color, interior=False, length=3.45, sedan=False, pickup=False, width=1.6, c=None):
    c = c or cV
    P = lambda n: f'VEH_{name}_{n}'
    root = empty(f'VEH_{name}', (0, 0, 0), c, 1.2, 'ARROWS'); root['odo'] = 0.0
    holder = empty(P('Escala'), (0, 0, 0), c, 0.5, parent=root)   # largura ajustada aqui
    holder.scale.x = width / 1.76
    body_e = empty(P('Corpo'), (0, 0, 0), c, 0.5, parent=holder)
    body = mat(f'MAT_Pintura_{name}', hexc(color), 0.3, 0.5, coat=1.0)
    brake = mat(f'MAT_Lanterna_{name}', hexc('#4A0806'), 0.3, emit=hexc('#FF1A0A'), emit_str=0.0)
    head = mat(f'MAT_Farol_{name}', hexc('#CFCFCF'), 0.1, emit=hexc('#FFF4E0'), emit_str=0.0)
    hl = length / 2
    parts = {'root': root, 'brake': brake, 'head': head, 'holder': holder, 'body': body_e}
    H = body_e
    if interior:
        box(P('Frente'), (1.76, hl - 0.75, 0.6), (0, (0.75 + hl) / 2, 0.62), body, c, bevel=0.08, parent=H)
        box(P('Traseira'), (1.76, hl - 0.55, 0.6), (0, (-hl - 0.55) / 2, 0.62), body, c, bevel=0.08, parent=H)
        box(P('Assoalho'), (1.7, 1.32, 0.1), (0, 0.1, 0.37), m_dash, c, parent=H)
        box(P('LadoDireito'), (0.06, 1.32, 0.56), (0.85, 0.1, 0.62), body, c, parent=H)
        dp = empty(P('Porta_Pivo'), (-0.86, 0.75, 0.62), c, 0.3, 'ARROWS', parent=H)
        box(P('Porta'), (0.06, 1.3, 0.56), (0, -0.65, 0), body, c, parent=dp, bevel=0.02)
        quad(P('Porta_Vidro'), [(0.07, 0.1, 0.3), (0.07, -1.3, 0.3), (0.15, -1.3, 0.91), (0.15, -0.6, 0.91)], m_cglass, c, parent=dp)
        parts['door'] = dp
        for sx, nm in ((-0.4, 'Motorista'), (0.4, 'Passageiro')):
            box(P(f'Banco{nm}_Assento'), (0.5, 0.5, 0.12), (sx, -0.15, 0.48), m_seat, c, bevel=0.04, parent=H)
            box(P(f'Banco{nm}_Encosto'), (0.5, 0.12, 0.65), (sx, -0.5, 0.86), m_seat, c, rot=(15, 0, 0), bevel=0.04, parent=H)
            box(P(f'Banco{nm}_Apoio'), (0.28, 0.1, 0.16), (sx, -0.6, 1.27), m_seat, c, rot=(15, 0, 0), bevel=0.03, parent=H)
        box(P('Painel'), (1.62, 0.36, 0.2), (0, 0.72, 0.9), m_dash, c, bevel=0.04, parent=H)
        box(P('Painel_Instrumentos'), (0.36, 0.05, 0.1), (-0.4, 0.55, 1.0), mat('MAT_Instrumentos', hexc('#0A0A0A'), 0.2, emit=hexc('#6FB7FF'), emit_str=0.6), c, parent=H)
        beam(P('Coluna_Direcao'), (-0.4, 0.62, 0.88), (-0.4, 0.43, 0.97), 0.05, m_dash, c, parent=H)
        torus(P('Volante'), 0.18, 0.022, (-0.4, 0.4, 0.98), m_dash, c, rot=(65, 0, 0), parent=H)
        cyl(P('Volante_Centro'), 0.06, 0.04, (-0.4, 0.41, 0.98), m_dash, c, rot=(65, 0, 0), parent=H)
        box(P('Retrovisor'), (0.25, 0.03, 0.07), (0, 0.27, 1.42), m_dash, c, bevel=0.01, parent=H)
        beam(P('Retrovisor_Haste'), (0, 0.27, 1.45), (0, 0.22, 1.52), 0.015, m_dash, c, parent=H)
    else:
        box(P('Carroceria'), (1.76, length, 0.6), (0, 0, 0.62), body, c, bevel=0.08, parent=H)
    gl = m_cglass if interior else m_cglass_d
    if pickup:
        cb, ct = (-0.45, -0.4)
    else:
        cb, ct = ((-hl + 0.9, -hl + 1.4) if sedan else (-hl + 0.2, -hl + 0.45))
    for sx in (-1, 1):
        s = 'L' if sx < 0 else 'R'
        beam(P(f'ColunaA_{s}'), (sx * 0.8, 0.85, 0.92), (sx * 0.71, 0.15, 1.53), 0.07, body, c, parent=H)
        if not pickup:
            beam(P(f'ColunaB_{s}'), (sx * 0.8, -0.5, 0.92), (sx * 0.72, -0.5, 1.53), 0.07, body, c, parent=H)
        beam(P(f'ColunaC_{s}'), (sx * 0.8, cb, 0.92), (sx * 0.71, ct, 1.53), 0.09, body, c, parent=H)
    box(P('Teto'), (1.5, 0.15 - ct + 0.04, 0.06), (0, (0.15 + ct) / 2, 1.55), body, c, bevel=0.02, parent=H)
    quad(P('ParaBrisa'), [(-0.8, 0.85, 0.92), (0.8, 0.85, 0.92), (0.71, 0.15, 1.53), (-0.71, 0.15, 1.53)], gl, c, parent=H)
    quad(P('VidroTraseiro'), [(-0.8, cb, 0.92), (0.8, cb, 0.92), (0.71, ct, 1.53), (-0.71, ct, 1.53)], gl, c, parent=H)
    quad(P('VidroLado_R'), [(0.79, 0.85, 0.92), (0.79, cb, 0.92), (0.71, ct, 1.53), (0.71, 0.15, 1.53)], gl, c, parent=H)
    if interior:
        quad(P('VidroLado_L_Tras'), [(-0.79, -0.55, 0.92), (-0.79, cb, 0.92), (-0.71, ct, 1.53), (-0.71, -0.55, 1.53)], gl, c, parent=H)
    else:
        quad(P('VidroLado_L'), [(-0.79, 0.85, 0.92), (-0.79, cb, 0.92), (-0.71, ct, 1.53), (-0.71, 0.15, 1.53)], gl, c, parent=H)
    if pickup:  # caçamba
        bl = hl + cb
        for sx in (-1, 1):
            box(P(f'Cacamba_Lado_{sx}'), (0.08, bl, 0.3), (sx * 0.84, (cb - hl) / 2, 1.07), body, c, parent=H)
        box(P('Cacamba_Tampa'), (1.76, 0.08, 0.3), (0, -hl + 0.04, 1.07), body, c, parent=H)
        box(P('Cacamba_Fundo'), (1.6, bl - 0.1, 0.02), (0, (cb - hl) / 2, 0.93), m_dash, c, parent=H)
        box(P('Cacamba_Carga'), (0.6, 0.5, 0.35), (0.3, -hl + 0.6, 1.1), mat('MAT_CaixaFerramentas', hexc('#B33A1E'), 0.5), c, parent=H)
    box(P('ParaChoque_F'), (1.82, 0.2, 0.22), (0, hl + 0.02, 0.42), m_bump, c, bevel=0.05, parent=H)
    box(P('ParaChoque_T'), (1.82, 0.2, 0.22), (0, -hl - 0.02, 0.42), m_bump, c, bevel=0.05, parent=H)
    for sx in (-1, 1):
        s = 'L' if sx < 0 else 'R'
        box(P(f'Farol_{s}'), (0.36, 0.06, 0.12), (sx * 0.58, hl + 0.01, 0.76), head, c, bevel=0.02, parent=H)
        box(P(f'Lanterna_{s}'), (0.3, 0.06, 0.13), (sx * 0.62, -hl - 0.01, 0.78), brake, c, bevel=0.02, parent=H)
    box(P('Placa_F'), (0.4, 0.02, 0.13), (0, hl + 0.13, 0.45), m_plate, c, parent=H)
    box(P('Placa_T'), (0.4, 0.02, 0.13), (0, -hl - 0.13, 0.45), m_plate, c, parent=H)
    wy = hl - 0.62
    for sx, sy, s in ((-1, 1, 'FL'), (1, 1, 'FR'), (-1, -1, 'RL'), (1, -1, 'RR')):
        wp = empty(P(f'Roda_{s}_Pivo'), (sx * 0.8, sy * wy, WHEEL_R), c, 0.2, 'CIRCLE', parent=holder)
        wp.rotation_mode = 'XYZ'
        cyl(P(f'Roda_{s}_Pneu'), WHEEL_R, 0.23, (0, 0, 0), m_tire, c, rot=(0, 90, 0), segs=20, parent=wp)
        cyl(P(f'Roda_{s}_Calota'), 0.19, 0.24, (0, 0, 0), m_hub, c, rot=(0, 90, 0), segs=5, parent=wp, smooth=False)
        wheel_driver(wp, root, WHEEL_R)
    return parts

# ---------------------------------------------------------------- clássico anos 30 (frente = +Y local)
def build_classic(name, body_hex, fender_hex, top_hex=None, hood_hex=None, convertible=True, L=3.4, Wd=1.25):
    c = cCE
    P = lambda n: f'{name}_{n}'
    root = empty(name, (0, 0, 0), c, 1.0, 'ARROWS')
    body = mat(f'MAT_{name}_Carroceria', hexc(body_hex), 0.25, 0.4, coat=1.0)
    fend = mat(f'MAT_{name}_Paralama', hexc(fender_hex), 0.25, 0.3, coat=1.0)
    hood = mat(f'MAT_{name}_Capo', hexc(hood_hex or body_hex), 0.25, 0.4, coat=1.0)
    creme = mat('MAT_Classico_BancoCreme', hexc('#F4DDAA'), 0.7)
    hl = L / 2; fy, ry = hl - 0.62, -hl + 0.62; fx = Wd / 2 - 0.13
    for sx in (-1, 1):
        for nm_, wy_ in (('F', fy), ('T', ry)):
            sphere(P(f'Paralama_{nm_}{sx}'), (0.2, 0.6, 0.3), (sx * fx, wy_, 0.42), fend, c, parent=root)
            wp = empty(P(f'Roda_{nm_}{sx}'), (sx * fx, wy_, 0.32), c, 0.15, parent=root)
            cyl(P(f'Roda_{nm_}{sx}_Pneu'), 0.32, 0.16, (0, 0, 0), m_tire, c, rot=(0, 90, 0), segs=20, parent=wp)
            cyl(P(f'Roda_{nm_}{sx}_Raios'), 0.22, 0.17, (0, 0, 0), m_chrome, c, rot=(0, 90, 0), segs=12, parent=wp, smooth=False)
        box(P(f'Estribo_{sx}'), (0.24, L - 2 * 0.62 - 0.3, 0.05), (sx * fx, 0, 0.3), fend, c, parent=root)
    box(P('Chassi'), (Wd - 0.5, L - 0.3, 0.2), (0, 0, 0.42), fend, c, parent=root)
    box(P('Capo'), (Wd * 0.62, 1.25, 0.42), (0, hl - 0.85, 0.74), hood, c, bevel=0.06, parent=root)
    box(P('Grade'), (Wd * 0.5, 0.07, 0.55), (0, hl - 0.2, 0.76), m_chrome, c, bevel=0.03, parent=root)
    box(P('Cabine'), (Wd * 0.88, 1.35, 0.5), (0, -0.2, 0.78), body, c, bevel=0.05, parent=root)
    box(P('PortaMalas'), (Wd * 0.8, 0.5, 0.48), (0, -hl + 0.42, 0.72), body, c, bevel=0.06, parent=root)
    cyl(P('Estepe'), 0.3, 0.14, (0, -hl + 0.12, 0.78), m_tire, c, rot=(90, 0, 0), segs=20, parent=root)
    cyl(P('Estepe_Aro'), 0.18, 0.15, (0, -hl + 0.12, 0.78), m_chrome, c, rot=(90, 0, 0), segs=16, parent=root)
    for sx in (-1, 1):
        cyl(P(f'Farol_{sx}'), 0.1, 0.12, (sx * 0.38, hl - 0.38, 1.0), m_chrome, c, rot=(90, 0, 0), segs=16, parent=root)
    box(P('ParaChoque_F'), (Wd * 0.95, 0.06, 0.06), (0, hl - 0.05, 0.42), m_chrome, c, parent=root)
    box(P('ParaChoque_T'), (Wd * 0.95, 0.06, 0.06), (0, -hl + 0.02, 0.42), m_chrome, c, parent=root)
    beam(P('ParaBrisa_Moldura'), (-Wd * 0.4, 0.5, 1.05), (Wd * 0.4, 0.5, 1.05), 0.03, m_chrome, c, parent=root)
    quad(P('ParaBrisa'), [(-Wd * 0.4, 0.5, 1.04), (Wd * 0.4, 0.5, 1.04), (Wd * 0.4, 0.42, 1.38), (-Wd * 0.4, 0.42, 1.38)], m_cglass, c, parent=root)
    if convertible:
        box(P('Banco_F'), (Wd * 0.75, 0.4, 0.2), (0, 0.05, 1.0), creme, c, bevel=0.04, parent=root)
        box(P('Banco_F_Encosto'), (Wd * 0.75, 0.12, 0.3), (0, -0.15, 1.15), creme, c, bevel=0.04, parent=root)
        box(P('Banco_T'), (Wd * 0.75, 0.4, 0.2), (0, -0.55, 1.0), creme, c, bevel=0.04, parent=root)
        box(P('CapotaRecolhida'), (Wd * 0.8, 0.3, 0.16), (0, -0.92, 1.08), mat(f'MAT_{name}_Capota', hexc(top_hex or '#1A1A1A'), 0.8), c, bevel=0.06, parent=root)
    else:
        m_top = mat(f'MAT_{name}_Capota', hexc(top_hex or '#1A1A1A'), 0.8)
        box(P('Capota'), (Wd * 0.86, 1.25, 0.45), (0, -0.3, 1.24), m_top, c, bevel=0.08, parent=root)
        for sx in (-1, 1):
            box(P(f'JanelaLateral_{sx}'), (0.02, 0.8, 0.26), (sx * Wd * 0.43, -0.2, 1.24), m_cglass_d, c, parent=root)
    return root

PARKED = {}   # os 4 clássicos foram removidos: as vagas V1, V2, V4 e V5 ficam livres para os carros da fila
for nm, cfg in PARKED.items():
    r_ = build_classic(nm, cfg['body'], cfg['fender'], cfg.get('top'), cfg.get('hood'), cfg['convertible'])
    r_.location = (cfg['pos'][0], cfg['pos'][1], 0)
    r_.rotation_euler.z = rad(cfg.get('rot', -90)); r_.scale = (1.32, 1.32, 1.32)   # ~4,5 m

# ---------------------------------------------------------------- carros animados (modernos estilizados, ~4,2 m x 1,8 m)
CARS = {}
CARS['Marcos'] = build_car('CarroMarcos', '#C4CCDA', interior=True, length=4.0, width=1.8)
CARS['Marcos']['body'].scale = (1, 1, 1.25)          # cabine mais alta: cabe a cabeça do Marcos
for i, (clr, sed) in enumerate([('#E8604A', True), ('#3A7BD8', False), ('#F2C23A', True), ('#58B08A', False)]):
    CARS[f'Fila{i+1}'] = build_car(f'Fila_{i+1}', clr, sedan=sed, length=4.4 if sed else 4.0, width=1.8)
CARS['Claudio'] = build_car('CarroClaudio', '#2C3C8E', sedan=True, length=4.2, width=1.75)
CARS['Miguel'] = build_car('PicapeMiguel', '#F4F0E6', pickup=True, length=4.4, width=1.8)
# Claudio estacionado na V3 (frente para +X, junto ao muro direito)
CARS['Claudio']['root'].location = (13.15, RIGHT_Y[2], 0); CARS['Claudio']['root'].rotation_euler.z = rad(-90)
# picape do Miguel parada no corredor, ligeiramente torta, porta aberta e pisca-alerta
CARS['Miguel']['root'].location = (PICKUP_POS[0], PICKUP_POS[1], 0); CARS['Miguel']['root'].rotation_euler.z = rad(96)
m_haz = mat('MAT_PiscaAlerta_Miguel', hexc('#7A4A08'), 0.3, emit=hexc('#FF9A1A'), emit_str=0.0)
Hm = CARS['Miguel']['body']
pdp = empty('VEH_PicapeMiguel_Porta_Pivo', (-0.86, 0.75, 0.62), cV, 0.3, 'ARROWS', parent=Hm)
box('VEH_PicapeMiguel_Porta', (0.06, 1.1, 0.56), (0, -0.55, 0), mat('MAT_Pintura_PicapeMiguel', (1, 1, 1)), cV, parent=pdp)
pdp.rotation_euler.z = rad(-32)
for sx in (-1, 1):
    for sy in (-1, 1):
        box(f'VEH_PicapeMiguel_Pisca_{sx}{sy}', (0.14, 0.09, 0.07), (sx * 0.88, sy * 2.1, 0.62), m_haz, cV, parent=Hm)