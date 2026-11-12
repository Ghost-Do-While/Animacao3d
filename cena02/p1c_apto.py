# Parte 1c - ENV_Apartamento: sala aconchegante dentro do prédio (Bloco A, 3º andar) + props + TV com o telejornal pré-renderizado
cA = col('ENV_Apartamento')
Z0 = APT_Z
def R(x, y, z=0.0): return (x, y, Z0 + z)

m_wood = mat('MAT_Apto_PisoMadeira', hexc('#9A6238'), 0.4, bump=0.2)
m_aw = mat('MAT_Apto_Parede', hexc('#E8B98A'), 0.8, bump=0.2)
m_aw2 = mat('MAT_Apto_ParedeDestaque', hexc('#C8785A'), 0.8, bump=0.2)
m_sofa = mat('MAT_Apto_Sofa', hexc('#5B6F8F'), 0.75, bump=0.3, sss=0.1)
m_pill = mat('MAT_Apto_Almofada', hexc('#F0A24A'), 0.85)
m_pill2 = mat('MAT_Apto_Almofada2', hexc('#4FB8A8'), 0.85)
m_rug = mat('MAT_Apto_Tapete', hexc('#B85A4A'), 1.0, bump=0.4)
m_rack = mat('MAT_Apto_Rack', hexc('#6A3F2A'), 0.45)
m_tvb = mat('MAT_Apto_TV_Moldura', hexc('#14121A'), 0.25)
m_door = mat('MAT_Apto_Porta', hexc('#A86A3E'), 0.45)
m_shade = mat('MAT_Apto_Cupula', hexc('#FFD9A0'), 0.8, emit=hexc('#FFB46B'), emit_str=3.0)
m_brass = mat('MAT_Apto_Latao', hexc('#D9A63C'), 0.25, 0.9)
m_tbl = mat('MAT_Apto_Mesinha', hexc('#7A4A30'), 0.4)
m_plant = mat('MAT_Apto_Planta', hexc('#3FA64F'), 0.7)

# piso, paredes pintadas (acabamento interno) e divisória com a porta
box('ENV_Apartamento_Piso', (APT_X1 - APT_X0, APT_Y1 - APT_Y0, 0.04), R((APT_X0 + APT_X1) / 2, (APT_Y0 + APT_Y1) / 2, 0.02), m_wood, cA, bevel=0)
box('ENV_Apartamento_Parede_Oeste', (0.04, APT_Y1 - APT_Y0 + 0.2, 2.8), R(APT_X0 + 0.0, (APT_Y0 + APT_Y1) / 2, 1.4), m_aw2, cA, bevel=0)
box('ENV_Apartamento_Parede_Sul', (APT_X1 - APT_X0, 0.04, 2.8), R((APT_X0 + APT_X1) / 2, APT_Y0 - 0.04, 1.4), m_aw, cA, bevel=0)
DOOR_X0, DOOR_X1 = -13.7, -12.7
DY = 6.05
box('ENV_Apartamento_Divisoria_A', (DOOR_X0 - APT_X0, 0.2, 2.8), R((APT_X0 + DOOR_X0) / 2, DY, 1.4), m_aw, cA)
box('ENV_Apartamento_Divisoria_B', (APT_X1 - DOOR_X1, 0.2, 2.8), R((DOOR_X1 + APT_X1) / 2, DY, 1.4), m_aw, cA)
box('ENV_Apartamento_Divisoria_Verga', (DOOR_X1 - DOOR_X0, 0.2, 0.7), R((DOOR_X0 + DOOR_X1) / 2, DY, 2.45), m_aw, cA)
box('ENV_Apartamento_Batente_L', (0.08, 0.26, 2.1), R(DOOR_X0 - 0.04, DY, 1.05), m_branco, cA)
box('ENV_Apartamento_Batente_R', (0.08, 0.26, 2.1), R(DOOR_X1 + 0.04, DY, 1.05), m_branco, cA)
box('ENV_Apartamento_Batente_T', (DOOR_X1 - DOOR_X0 + 0.16, 0.26, 0.08), R((DOOR_X0 + DOOR_X1) / 2, DY, 2.14), m_branco, cA)
# corredor iluminado do lado de fora da porta
box('ENV_Apartamento_Corredor_Parede', (6.0, 0.2, 2.8), R(-12.4, 8.3, 1.4), mat('MAT_Apto_CorredorParede', hexc('#7F6BA8'), 0.8), cA)
box('ENV_Apartamento_Corredor_Luz', (1.6, 0.5, 0.08), R(-13.2, 7.2, 2.74), mat('MAT_Apto_CorredorLuz', hexc('#FFF2D8'), 0.4, emit=hexc('#FFE9C0'), emit_str=6.0), cA, bevel=0.01)
dpiv = empty('ENV_Apartamento_Porta_Pivo', R(DOOR_X0, DY, 0), cA, 0.3, 'ARROWS')
box('ENV_Apartamento_Porta', (1.0, 0.06, 2.1), (0.5, 0, 1.05), m_door, cA, parent=dpiv)
sphere('ENV_Apartamento_Porta_Macaneta', 0.04, (0.88, -0.06, 1.0), m_brass, cA, parent=dpiv)

# Sofá 3 lugares, de costas para a janela, virado para a TV (-X)
SOFA = (-11.9, 2.2)
sofa = empty('ENV_Apartamento_Sofa', R(SOFA[0], SOFA[1], 0), cA, 0.5, 'ARROWS'); sofa.rotation_euler.z = rad(90)
box('ENV_Apartamento_Sofa_Base', (2.4, 1.0, 0.3), (0, 0, 0.2), m_sofa, cA, parent=sofa)
box('ENV_Apartamento_Sofa_Encosto', (2.4, 0.26, 0.6), (0, -0.42, 0.65), m_sofa, cA, bevel=0.07, parent=sofa)
for sx in (-1, 1):
    box(f'ENV_Apartamento_Sofa_Braco_{"L" if sx < 0 else "R"}', (0.24, 1.0, 0.64), (sx * 1.32, 0, 0.32), m_sofa, cA, bevel=0.08, parent=sofa)
for i, cx in enumerate([-0.76, 0.0, 0.76]):
    c_ = box(f'ENV_Apartamento_Sofa_Assento_{i}', (0.75, 0.78, 0.14), (cx, 0.07, 0.36), m_sofa, cA, bevel=0.06, parent=sofa)
    for v in c_.data.vertices: v.co.z += 0.07
    box(f'ENV_Apartamento_Sofa_Costas_{i}', (0.75, 0.2, 0.48), (cx, -0.24, 0.74), m_sofa, cA, bevel=0.08, parent=sofa)
box('ENV_Apartamento_Almofada_L', (0.44, 0.15, 0.42), (-0.98, -0.1, 0.7), m_pill, cA, rot=(-12, 0, 18), bevel=0.08, parent=sofa)
box('ENV_Apartamento_Almofada_R', (0.44, 0.15, 0.42), (0.98, -0.1, 0.7), m_pill2, cA, rot=(-12, 0, -15), bevel=0.08, parent=sofa)
box('ENV_Apartamento_Tapete', (2.6, 3.0, 0.03), R(-13.4, 2.2, 0.05), m_rug, cA, bevel=0.01)

# Rack + TV 55" na parede oeste
box('ENV_Apartamento_Rack', (0.46, 2.0, 0.5), R(-15.2, 2.2, 0.25), m_rack, cA)
tvroot = empty('PRP_TV', R(-15.38, 2.2, 1.35), cA, 0.4, 'ARROWS'); tvroot.rotation_euler.z = rad(90)   # tela olha para +X
box('ENV_Apartamento_TV_Moldura', (1.32, 0.06, 0.8), (0, 0.032, 0), m_tvb, cA, parent=tvroot)
box('ENV_Apartamento_TV_Pe', (0.4, 0.2, 0.04), (0, 0.04, -0.42), m_tvb, cA, parent=tvroot)
# Abajur ao lado do sofá (mesa na ponta sul)
box('ENV_Apartamento_MesaAbajur', (0.5, 0.5, 0.58), R(-11.9, 0.45, 0.29), m_tbl, cA)
cyl('ENV_Apartamento_Abajur_Base', 0.1, 0.06, R(-11.9, 0.45, 0.61), m_brass, cA)
cyl('ENV_Apartamento_Abajur_Haste', 0.018, 0.5, R(-11.9, 0.45, 0.88), m_brass, cA, segs=8)
cyl('ENV_Apartamento_Abajur_Cupula', 0.23, 0.3, R(-11.9, 0.45, 1.25), m_shade, cA, r2=0.15, segs=24)
# Mesinha lateral junto à porta (oeste da porta) + fruteira
box('ENV_Apartamento_MesaLateral_Tampo', (0.5, 1.0, 0.05), R(-15.05, 5.3, 0.76), m_tbl, cA)
for i, (lx, ly) in enumerate([(-0.2, -0.42), (0.2, -0.42), (-0.2, 0.42), (0.2, 0.42)]):
    box(f'ENV_Apartamento_MesaLateral_Pe_{i}', (0.05, 0.05, 0.75), R(-15.05 + lx, 5.3 + ly, 0.375), m_tbl, cA)
sphere('ENV_Apartamento_Fruteira', (0.18, 0.18, 0.08), R(-15.05, 5.0, 0.84), mat('MAT_Apto_Ceramica', hexc('#F4EAD6'), 0.3), cA)
for i, (fx, fy, fc_) in enumerate([(0.0, 0.0, '#E03A2A'), (0.08, 0.05, '#FFC93A'), (-0.07, 0.06, '#8CC43A'), (0.02, -0.08, '#F58A22')]):
    sphere(f'ENV_Apartamento_Fruta_{i}', 0.05, R(-15.05 + fx, 5.0 + fy, 0.92), mat(f'MAT_Apto_Fruta_{i}', hexc(fc_), 0.35), cA, segs=(14, 10))
# planta e quadro (vida)
cyl('ENV_Apartamento_Vaso', 0.2, 0.4, R(-9.4, 0.5, 0.2), mat('MAT_Apto_Vaso', hexc('#D2603A'), 0.6), cA, r2=0.15, segs=16)
for i in range(7):
    a_ = i * 51
    sphere(f'ENV_Apartamento_Folha_{i}', (0.09, 0.03, 0.3), R(-9.4 + 0.16 * math.cos(rad(a_)), 0.5 + 0.16 * math.sin(rad(a_)), 0.62), m_plant, cA, rot=(25 * math.cos(rad(a_)), -25 * math.sin(rad(a_)), a_), segs=(10, 8))
box('ENV_Apartamento_Quadro_Moldura', (0.04, 1.2, 0.8), R(-15.43, 4.2, 1.65), m_branco, cA)
box('ENV_Apartamento_Quadro_Arte', (0.02, 1.05, 0.65), R(-15.41, 4.2, 1.65), mat('MAT_Apto_Arte', hexc('#F2A441'), 0.6, emit=hexc('#F2A441'), emit_str=0.15), cA, bevel=0)

# ---------------------------------------------------------------- PROPS
m_key = mat('MAT_Chave', hexc('#E4E4DC'), 0.22, 1.0)
m_tag = mat('MAT_TagCondominio', hexc('#2F8AE0'), 0.4)
keys_ = empty('PRP_Chaves', (0, 0, 0), cA, 0.08, 'SPHERE')
torus('PRP_Chaves_Argola', 0.025, 0.004, (0, 0, 0), m_key, cA, rot=(90, 0, 0), parent=keys_)
for i, ang_ in enumerate([-25, 0, 25]):
    k_ = box(f'PRP_Chaves_Chave_{i}', (0.014, 0.004, 0.06), (0, 0, -0.045), m_key, cA, parent=keys_)
    k_.location = (math.sin(rad(ang_)) * 0.05, 0.002 * i, -0.045 * math.cos(rad(ang_)) - 0.02); k_.rotation_euler.y = rad(-ang_)
box('PRP_Chaves_Tag', (0.035, 0.007, 0.045), (0, -0.004, -0.045), m_tag, cA, rot=(0, 40, 0), parent=keys_)
m_remote = mat('MAT_Controle', hexc('#1A1822'), 0.4)
m_red = mat('MAT_BotaoVermelho', hexc('#E8201A'), 0.3, emit=hexc('#FF2A1A'), emit_str=0.4)
m_btn = mat('MAT_BotaoCinza', hexc('#6A6A80'), 0.5)
REMOTE_SEAT = R(-11.75, 3.05, 0.515)
remote = box('PRP_ControleRemoto', (0.055, 0.2, 0.024), REMOTE_SEAT, m_remote, cA)
cyl('PRP_ControleRemoto_BotaoDesligar', 0.009, 0.006, (0, 0.075, 0.014), m_red, cA, parent=remote, segs=12)
for i in range(6):
    box(f'PRP_ControleRemoto_Botao_{i}', (0.01, 0.01, 0.005), ((i % 2 - 0.5) * 0.02, 0.03 - (i // 2) * 0.024, 0.013), m_btn, cA, parent=remote)

# ---------------------------------------------------------------- TV: tela = vídeo do telejornal pré-renderizado (SET_Telejornal -> CAM_TV_Jornal)
SW, SH = 1.21, 0.68
TV_F0, TV_F1 = 538, 640            # frames em que a tela mostra o jornal (liga em 538, desliga em 614; sobra de margem)
NEWS_DIR = os.path.join(os.path.dirname(BASE), 'render', 'telejornal')
news_files = sorted(f for f in os.listdir(NEWS_DIR) if f.lower().endswith('.png')) if os.path.isdir(NEWS_DIR) else []
m_scr = new_mat('MAT_TV_Tela', principled=False)
nt = m_scr.node_tree
em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.5
tc = nt.nodes.new('ShaderNodeTexCoord'); sepn = nt.nodes.new('ShaderNodeSeparateXYZ'); cmb = nt.nodes.new('ShaderNodeCombineXYZ')
nt.links.new(tc.outputs['Generated'], sepn.inputs[0]); nt.links.new(sepn.outputs['X'], cmb.inputs['X']); nt.links.new(sepn.outputs['Z'], cmb.inputs['Y'])
if news_files:
    img = D.images.load(os.path.join(NEWS_DIR, news_files[0]))
    img.source = 'SEQUENCE'
    img.colorspace_settings.name = 'sRGB'
    it = nt.nodes.new('ShaderNodeTexImage'); it.image = img
    it.image_user.frame_start = TV_F0; it.image_user.frame_duration = len(news_files)
    it.image_user.frame_offset = 0                  # sincroniza: frame 538 da cena = primeiro frame do jornal
    it.image_user.use_auto_refresh = True; it.image_user.use_cyclic = False
    it.extension = 'EXTEND'; it.interpolation = 'Linear'
    nt.links.new(cmb.outputs[0], it.inputs['Vector'])
    col_out = it.outputs['Color']
else:
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (*hexc('#0B1E3F'), 1); ramp.color_ramp.elements[1].color = (*hexc('#2D6FB8'), 1)
    nt.links.new(sepn.outputs['Z'], ramp.inputs[0]); col_out = ramp.outputs['Color']
# vinheta + scanlines sutis (parece TV de verdade) e brilho de borda
vg = nt.nodes.new('ShaderNodeTexGradient'); vg.gradient_type = 'QUADRATIC_SPHERE'
nrm = nt.nodes.new('ShaderNodeMapping'); nrm.inputs['Location'].default_value = (-0.5, -0.5, 0)
nt.links.new(tc.outputs['Generated'], nrm.inputs['Vector'])
sp2 = nt.nodes.new('ShaderNodeSeparateXYZ'); cb2 = nt.nodes.new('ShaderNodeCombineXYZ')
nt.links.new(nrm.outputs[0], sp2.inputs[0]); nt.links.new(sp2.outputs['X'], cb2.inputs['X']); nt.links.new(sp2.outputs['Z'], cb2.inputs['Y'])
nt.links.new(cb2.outputs[0], vg.inputs['Vector'])
vr = nt.nodes.new('ShaderNodeMapRange'); vr.inputs['From Min'].default_value = 0.0; vr.inputs['From Max'].default_value = 0.5
vr.inputs['To Min'].default_value = 1.0; vr.inputs['To Max'].default_value = 0.55
nt.links.new(vg.outputs['Fac'], vr.inputs['Value'])
scan = nt.nodes.new('ShaderNodeMath'); scan.operation = 'SINE'
smul = nt.nodes.new('ShaderNodeMath'); smul.operation = 'MULTIPLY'; smul.inputs[1].default_value = 3.14159 * 2 * 240
nt.links.new(sepn.outputs['Z'], smul.inputs[0]); nt.links.new(smul.outputs[0], scan.inputs[0])
sm2 = nt.nodes.new('ShaderNodeMath'); sm2.operation = 'MULTIPLY_ADD'; sm2.inputs[1].default_value = 0.04; sm2.inputs[2].default_value = 0.96
nt.links.new(scan.outputs[0], sm2.inputs[0])
fm = nt.nodes.new('ShaderNodeMath'); fm.operation = 'MULTIPLY'
nt.links.new(vr.outputs[0], fm.inputs[0]); nt.links.new(sm2.outputs[0], fm.inputs[1])
mixc = nt.nodes.new('ShaderNodeMix'); mixc.data_type = 'RGBA'; mixc.blend_type = 'MULTIPLY'; sock(mixc.inputs, 'Factor').default_value = 1.0
nt.links.new(col_out, sock(mixc.inputs, 'A')); nt.links.new(fm.outputs[0], sock(mixc.inputs, 'B'))
nt.links.new(sock(mixc.outputs, 'Result'), em.inputs['Color']); nt.links.new(em.outputs[0], mat_out(m_scr).inputs['Surface'])
tv = box('PRP_TV_Tela', (SW, 0.004, SH), (0, 0, 0), m_scr, cA, parent=tvroot, bevel=0)
# vidro com reflexo suave da sala
m_tvglass = mat('MAT_TV_Vidro', (0.02, 0.02, 0.03), 0.04, alpha=0.12)
box('PRP_TV_Vidro', (SW + 0.01, 0.003, SH + 0.01), (0, -0.0045, 0), m_tvglass, cA, parent=tvroot, bevel=0)
m_off = mat('MAT_TV_Desligada', hexc('#07070B'), 0.08)
tv_off = box('PRP_TV_Desligada', (SW, 0.003, SH), (0, -0.003, 0), m_off, cA, parent=tvroot, bevel=0)
tv_flash = box('PRP_TV_Flash', (SW, 0.003, SH), (0, -0.0035, 0), mat('MAT_TV_Flash', hexc('#FFFFFF'), 0.3, emit=hexc('#FFFFFF'), emit_str=25.0), cA, parent=tvroot, bevel=0)
tarja = manchete = None   # (a tarja e a manchete agora vivem no vídeo do telejornal)
