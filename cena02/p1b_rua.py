# Parte 1b - ENV_Rua_Entorno ampliado: calçadas de 3 m, rua de 2 faixas de 3,5 m, vizinhança (tudo FORA do lote)
cR = col('ENV_Rua_Entorno')
m_calc = mat('MAT_Rua_Calcada', hexc('#D5CFC4'), 0.75, bump=0.25)
m_junta = mat('MAT_Rua_Junta', hexc('#9E968A'), 0.9)
m_meiofio = mat('MAT_Rua_MeioFio', hexc('#EDE6D8'), 0.7)
m_asf = mat('MAT_Rua_AsfaltoUmido', hexc('#363B50'), 0.4, bump=0.2)
m_amar = mat('MAT_Rua_FaixaAmarela', hexc('#FFC62B'), 0.5)
m_brc = mat('MAT_Rua_FaixaBranca', hexc('#FFF6E6'), 0.5)
m_grelha = mat('MAT_Rua_Bueiro', hexc('#25222E'), 0.45, 0.8)
m_terra = mat('MAT_Rua_Canteiro', hexc('#5A3F2C'), 1.0)
m_copa = mat('MAT_Rua_Copa', hexc('#4FA65A'), 0.8)
m_ipe = mat('MAT_Rua_CopaIpe', hexc('#FFC93A'), 0.8)
m_tronco = mat('MAT_Rua_Tronco', hexc('#6B4A38'), 0.85)
m_poste = mat('MAT_Rua_Poste', hexc('#5C6678'), 0.35, 0.7)
m_lamp = mat('MAT_Rua_LampadaAmbar', hexc('#FFB868'), 0.3, emit=hexc('#FF9C3A'), emit_str=14.0)
m_lixo = mat('MAT_Rua_Lixeira', hexc('#2FA85A'), 0.45)
m_telha = mat('MAT_Rua_Telhado', hexc('#D2603A'), 0.75)
m_fach = [mat(f'MAT_Rua_Fachada_{i}', hexc(c_), 0.75, bump=0.2) for i, c_ in enumerate(['#F2D9A8', '#9DC1D8', '#F4B9A0', '#C9B8E0', '#B9DCB4', '#F7E6C4'])]
m_jan_on = mat('MAT_Rua_JanelaAcesa', hexc('#5A3A1C'), 0.7, emit=hexc('#FFC070'), emit_str=5.0)
m_jan_off = mat('MAT_Rua_JanelaApagada', hexc('#2A3350'), 0.1)
m_neon = mat('MAT_Rua_Letreiro', hexc('#FFFFFF'), 0.4, emit=hexc('#FF6A4A'), emit_str=12.0)
RX0, RX1 = -80.0, 80.0
W_ = RX1 - RX0
Ym = (SW_Y[0] + SW_Y[1]) / 2

# calçada da frente (3 m) com juntas, meio-fio e rampas de acesso nas aberturas
box('ENV_Rua_Calcada_Frente', (W_, 3.0, 0.2), (0, Ym, -0.1), m_calc, cR, bevel=0)
for x in range(int(RX0), int(RX1), 3):
    box(f'ENV_Rua_Junta_{x}', (0.03, 3.0, 0.005), (x, Ym, 0.003), m_junta, cR, bevel=0)
box('ENV_Rua_MeioFio', (W_, 0.2, 0.22), (0, SW_Y[0] - 0.1, -0.04), m_meiofio, cR)
for nm, xc, w in (('Saida', EXIT_CX, 5.0), ('Entrada', ENTR_CX, 5.0)):
    r_ = box(f'ENV_Rua_Rampa_{nm}', (w, 1.4, 0.06), (xc, SW_Y[0] + 0.6, -0.07), m_calc, cR, bevel=0.01)
    r_.rotation_euler.x = rad(6)
# rua: 2 faixas de 3,5 m
box('ENV_Rua_Asfalto', (W_, 7.0, 0.2), (0, (ROAD_Y[0] + ROAD_Y[1]) / 2, -0.28), m_asf, cR, bevel=0)
yc = (ROAD_Y[0] + ROAD_Y[1]) / 2
for i, x in enumerate(range(int(RX0), int(RX1), 5)):
    box(f'ENV_Rua_LinhaCentral_{i:02d}', (2.5, 0.14, 0.012), (x + 1.2, yc, -0.175), m_amar, cR, bevel=0)
for i in range(9):  # faixa de pedestres perto da entrada
    box(f'ENV_Rua_Zebra_{i}', (0.55, 6.0, 0.012), (9.5 + i * 1.0, yc, -0.175), m_brc, cR, bevel=0)
for i, x in enumerate([-24, -9.0, 14.0, 30]):
    box(f'ENV_Rua_Bueiro_{i}', (1.1, 0.5, 0.03), (x, ROAD_Y[1] - 0.45, -0.17), m_grelha, cR, bevel=0)
# calçada do outro lado (3 m): canteiros, ipês, postes âmbar, lixeiras
box('ENV_Rua_Calcada_Oposta', (W_, 3.0, 0.2), (0, (SW2_Y[0] + SW2_Y[1]) / 2, -0.1), m_calc, cR, bevel=0)
box('ENV_Rua_MeioFio_Oposto', (W_, 0.2, 0.22), (0, SW2_Y[1] + 0.1, -0.04), m_meiofio, cR)
STREET_LAMPS = []
for i, x in enumerate([-40, -28, -16, -4, 8, 20, 32, 44]):
    box(f'ENV_Rua_Canteiro_{i}', (1.6, 1.6, 0.08), (x + 4.5, -24.6, 0.04), m_terra, cR)
    cyl(f'ENV_Rua_Arvore_{i}_Tronco', 0.2, 3.6, (x + 4.5, -24.6, 1.8), m_tronco, cR, segs=10)
    sphere(f'ENV_Rua_Arvore_{i}_Copa', (2.3, 2.3, 1.9), (x + 4.5, -24.6, 4.8), m_ipe if i % 2 else m_copa, cR, segs=(12, 8))
    cyl(f'ENV_Rua_Poste_{i}', 0.11, 8.0, (x, -23.6, 4.0), m_poste, cR, segs=12)
    beam(f'ENV_Rua_Poste_{i}_Braco', (x, -23.6, 7.9), (x, -21.4, 8.1), 0.1, m_poste, cR)
    box(f'ENV_Rua_Poste_{i}_Luminaria', (0.45, 0.8, 0.16), (x, -21.3, 8.0), m_lamp, cR)
    STREET_LAMPS.append((x, -21.3, 7.8))
    if i % 2 == 0:
        cyl(f'ENV_Rua_Lixeira_{i}', 0.28, 0.9, (x + 1.5, -23.8, 0.45), m_lixo, cR, segs=14)
# vizinhança em frente (prédios de 3-8 andares, casas, comércio com letreiro aceso) - low-poly arredondado
random.seed(11)
x = -78.0; i = 0
VY0 = SW2_Y[0] - 0.5
while x < 78:
    w = random.uniform(8, 14); floors = random.choice([1, 2, 3, 4, 5, 6, 8]); h = floors * 3.0; d = random.uniform(10, 14)
    if x + w > -23.5 and x < -12.0:
        x = -12.0; continue
    yb = VY0 - d / 2
    box(f'ENV_Rua_Vizinho_{i:02d}', (w, d, h), (x + w / 2, yb, h / 2), random.choice(m_fach), cR, bevel=0.2)
    if floors <= 2:
        box(f'ENV_Rua_Vizinho_{i:02d}_Telhado', (w + 0.8, d + 0.8, 1.0), (x + w / 2, yb, h + 0.4), m_telha, cR, bevel=0.25)
    for f in range(floors):
        for j in range(max(1, int(w / 2.8))):
            jx = x + 1.4 + j * 2.8
            if jx > x + w - 0.8: break
            box(f'ENV_Rua_Vizinho_{i:02d}_J{f}_{j}', (1.3, 0.06, 1.6), (jx, VY0 + 0.02, f * 3.0 + 1.8), m_jan_on if random.random() < 0.5 else m_jan_off, cR, bevel=0.03)
    i += 1; x += w + random.uniform(0.6, 2.0)
box('ENV_Rua_Comercio', (11.0, 8.0, 4.0), (-17.5, VY0 - 4.0, 2.0), m_fach[2], cR, bevel=0.2)
box('ENV_Rua_Comercio_Vitrine', (8.0, 0.06, 2.4), (-17.5, VY0 + 0.02, 1.5), m_jan_on, cR, bevel=0.03)
box('ENV_Rua_Comercio_Placa', (8.5, 0.2, 0.9), (-17.5, VY0 + 0.1, 3.4), mat('MAT_Rua_PlacaFundo', hexc('#231E30'), 0.5), cR)
text('ENV_Rua_Comercio_Letreiro', 'PADARIA PÃO QUENTE', 0.58, (-17.5, VY0 + 0.25, 3.37), (90, 0, 0), m_neon, cR)
# entorno atrás dos muros: copas, casas e prédios
for i, (tx, ty, r_) in enumerate([(-21, -4, 3.0), (-23, 5, 3.4), (-21, 13, 3.0), (-8, 19, 3.2), (6, 19, 3.6), (18, 20, 3.0), (22, 6, 3.2), (21, -5, 3.0), (26, 15, 3.6), (-30, 18, 3.8), (-24, -12, 2.8), (24, -12, 3.0)]):
    cyl(f'ENV_Rua_ArvoreFundo_{i}_Tronco', 0.22, 4.2, (tx, ty, 2.1), m_tronco, cR, segs=10)
    sphere(f'ENV_Rua_ArvoreFundo_{i}_Copa', (r_, r_, r_ * 0.85), (tx, ty, 4.2 + r_ * 0.6), m_copa, cR, segs=(12, 8))
for i, (hx, hy, w, d) in enumerate([(-27, 0, 9, 11), (27, 2, 10, 12), (0, 24, 16, 9), (-22, 24, 11, 10), (23, 24, 10, 10)]):
    box(f'ENV_Rua_CasaFundo_{i}', (w, d, 4.0), (hx, hy, 2.0), random.choice(m_fach), cR, bevel=0.2)
    box(f'ENV_Rua_CasaFundo_{i}_Telhado', (w + 0.8, d + 0.8, 1.4), (hx, hy, 4.5), m_telha, cR, bevel=0.3)
for i, (hx, hy, f) in enumerate([(-36, 10, 6), (36, 12, 7), (10, 40, 8), (-16, 42, 5), (50, 30, 6), (-50, 28, 7)]):
    box(f'ENV_Rua_PredioFundo_{i}', (12, 12, f * 3), (hx, hy, f * 1.5), random.choice(m_fach), cR, bevel=0.25)
    for fl in range(f):
        for j in range(4):
            mj = m_jan_on if random.random() < 0.5 else m_jan_off
            sx_ = 1 if hx < 0 else -1
            box(f'ENV_Rua_PredioFundo_{i}_JX{fl}_{j}', (0.06, 1.3, 1.6), (hx + sx_ * 6.02, hy - 4.2 + j * 2.8, fl * 3 + 1.8), mj, cR, bevel=0.03)
            box(f'ENV_Rua_PredioFundo_{i}_JY{fl}_{j}', (1.3, 0.06, 1.6), (hx - 4.2 + j * 2.8, hy - 6.02, fl * 3 + 1.8), mj, cR, bevel=0.03)
box('ENV_Rua_ChaoEntorno', (260, 260, 0.1), (0, 40, -0.5), mat('MAT_Rua_Chao', hexc('#4A4540'), 0.95), cR, bevel=0)
# vida: pombos e folhas
m_pombo = mat('MAT_Rua_Pombo', hexc('#8A8FA3'), 0.8)
for i, (px, py, rz) in enumerate([(-9.0, -14.0, 30), (-8.2, -14.6, 160), (3.0, -24.0, 80)]):
    sphere(f'ENV_Rua_Pombo_{i}_Corpo', (0.12, 0.2, 0.1), (px, py, 0.1), m_pombo, cR, rot=(0, 0, rz), segs=(12, 8))
    sphere(f'ENV_Rua_Pombo_{i}_Cabeca', 0.06, (px + 0.16 * math.sin(rad(-rz)), py + 0.16 * math.cos(rad(rz)), 0.2), m_pombo, cR, segs=(10, 8))
m_folha = mat('MAT_Rua_Folha', hexc('#E28A2E'), 0.8)
for i in range(40):
    fx = random.uniform(-26, 26); fy = random.choice([random.uniform(-15.8, -13.3), random.uniform(-25.8, -23.3)])
    sphere(f'ENV_Rua_Folha_{i:02d}', (0.08, 0.05, 0.006), (fx, fy, 0.006), m_folha, cR, rot=(0, 0, random.uniform(0, 180)), segs=(6, 4))
