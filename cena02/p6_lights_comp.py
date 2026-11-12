# Parte 6 - Iluminação cinematográfica de estúdio + compositor (grading quente/frio, glare, vinheta, grão) + sincronia da luz da TV
sc = bpy.context.scene
cL = col('LIGHTS')

def light(name, kind, energy, color, loc, rot=(0, 0, 0), size=None, size_y=None, radius=None, temp=None, spot=None):
    ld = D.lights.new(name, kind)
    ld.energy = energy; ld.color = color
    if temp: ld.use_temperature = True; ld.temperature = temp
    if kind == 'AREA': ld.shape = 'RECTANGLE'; ld.size = size; ld.size_y = size_y if size_y else size
    if radius is not None: ld.shadow_soft_size = radius
    if kind == 'SPOT' and spot: ld.spot_size = rad(spot[0]); ld.spot_blend = spot[1]
    o = D.objects.new(name, ld); link(o, cL)
    o.location = loc; o.rotation_euler = [rad(a) for a in rot]
    return o

def window_on(o, f0, f1, e):
    """Liga a luz só no intervalo do plano (energia keyada, constante)."""
    key(o.data, 'energy', 0.0, 1, 'CONSTANT')
    key(o.data, 'energy', 0.0, max(1, f0 - 1), 'CONSTANT'); key(o.data, 'energy', e, f0, 'CONSTANT')
    key(o.data, 'energy', e, f1, 'CONSTANT'); key(o.data, 'energy', 0.0, f1 + 1, 'CONSTANT')

# ---------------- Céu de "hora azul": laranja dourado no horizonte -> azul-violeta, nuvens leves
w = D.worlds.get('World') or D.worlds.new('World')
sc.world = w
wt = w.node_tree
for n in list(wt.nodes): wt.nodes.remove(n)
wo = wt.nodes.new('ShaderNodeOutputWorld'); bgn = wt.nodes.new('ShaderNodeBackground')
tc = wt.nodes.new('ShaderNodeTexCoord'); sp = wt.nodes.new('ShaderNodeSeparateXYZ')
rp = wt.nodes.new('ShaderNodeValToRGB'); cr = rp.color_ramp
cr.elements[0].position = 0.0; cr.elements[0].color = (*hexc('#FFB45A'), 1)
cr.elements[1].position = 0.34; cr.elements[1].color = (*hexc('#2C2F7A'), 1)
e_ = cr.elements.new(0.05); e_.color = (*hexc('#FF8A5C'), 1)
e_ = cr.elements.new(0.14); e_.color = (*hexc('#8A5AA8'), 1)
nz = wt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 2.5; nz.inputs['Detail'].default_value = 5
mx = wt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'SCREEN'
mr = wt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.52; mr.inputs['From Max'].default_value = 0.78; mr.inputs['To Max'].default_value = 0.35
wt.links.new(tc.outputs['Generated'], sp.inputs[0]); wt.links.new(sp.outputs['Z'], rp.inputs[0])
wt.links.new(tc.outputs['Generated'], nz.inputs['Vector']); wt.links.new(nz.outputs['Fac'], mr.inputs['Value'])
wt.links.new(mr.outputs[0], mx.inputs[0])
wt.links.new(rp.outputs['Color'], sock(mx.inputs, 'A'))
sock(mx.inputs, 'B').default_value = (*hexc('#E6A8C8'), 1)
wt.links.new(sock(mx.outputs, 'Result'), bgn.inputs['Color'])
bgn.inputs['Strength'].default_value = 0.85
wt.links.new(bgn.outputs[0], wo.inputs['Surface'])

# ---------------- Exterior: golden/blue hour, sombras longas e macias
sun = light('LGT_Sol_Entardecer', 'SUN', 3.2, (1, 1, 1), (0, -40, 20), (83, 0, 8), temp=2700)
sun.data.angle = rad(7)                                  # sombras macias (5-8°)
sky = light('LGT_Ceu_Preenchimento', 'SUN', 0.9, hexc('#8AA0FF'), (0, 0, 30), (28, 0, 160))   # luz azul-violeta da sombra
sky.data.angle = rad(40)
for nm, (px, py) in POSTES.items():                      # postes P1 e P2 da maquete (3000 K, 150 W)
    light(f'LGT_{nm[3:]}', 'POINT', 150, (1, 1, 1), (px, py, 3.9), radius=0.14, temp=3000)
light('LGT_Guarita_Interna', 'AREA', 60, hexc('#CFE6FF'), (gx_ := (GX0 + GX1) / 2, -10.2, 2.5), size=2.6, size_y=2.0)
for i, p_ in enumerate(STREET_LAMPS):                    # postes da rua: âmbar 2200 K
    light(f'LGT_Rua_Poste_{i}', 'POINT', 260, (1, 1, 1), p_, radius=0.25, temp=2200)
# estacionamento da briga: contraste dramático, luz dura verde-amarelada de poste vindo de cima + rim frio recortando as silhuetas
BX_, BY_ = (MIGUEL_POS[0] + CLAUDIO_POS[0]) / 2, (MIGUEL_POS[1] + CLAUDIO_POS[1]) / 2
bp = light('LGT_Briga_PosteVerde', 'SPOT', 1100, hexc('#E4F2A0'), (BX_, BY_, 6.2), (0, 0, 0), radius=0.1, spot=(75, 0.55))
look_at(bp, (BX_, BY_, 1.0)); window_on(bp, 253, 492, 1100)
brim = light('LGT_Briga_Rim', 'AREA', 500, hexc('#8FB4FF'), (BX_ - 2.4, BY_ + 3.6, 3.4), size=1.6, size_y=1.6)
look_at(brim, (BX_, BY_, 1.4)); window_on(brim, 253, 492, 500)
# névoa atmosférica leve só no exterior (Volume Scatter 0.003)
fog = box('ENV_Rua_Nevoa', (110, 80, 16), (0, -5, 7.4), None, col('ENV_Rua_Entorno'), bevel=0)
m_fog = new_mat('MAT_Nevoa', principled=False)
vs = m_fog.node_tree.nodes.new('ShaderNodeVolumeScatter'); vs.inputs['Density'].default_value = 0.003
vs.inputs['Color'].default_value = (*hexc('#C8D0F0'), 1)
m_fog.node_tree.links.new(vs.outputs[0], mat_out(m_fog).inputs['Volume'])
fog.data.materials.append(m_fog); fog.display_type = 'BOUNDS'
key_vis(fog, 1, True); key_vis(fog, 493, False)

# ---------------- Setup de 3 pontos nos closes: key quente e suave, fill frio, rim forte
def three_point(tag, f0, f1, target, toward, key_e=260, fill_e=70, rim_e=480, dist=2.4):
    """toward = vetor horizontal do sujeito em direção à câmera; o key vem de 40° à esquerda dessa direção."""
    t = Vector(target); d = Vector(toward).normalized(); lft = Vector((-d.y, d.x, 0))
    k = light(f'LGT_{tag}_Key', 'AREA', key_e, hexc('#FFC48A'), t + d * dist * 0.9 + lft * dist * 0.55 + Vector((0, 0, 1.2)), size=1.3, size_y=1.3)
    fl = light(f'LGT_{tag}_Fill', 'AREA', fill_e, hexc('#8CB0FF'), t + d * dist * 0.8 - lft * dist * 0.9 + Vector((0, 0, 0.3)), size=2.0, size_y=2.0)
    rm = light(f'LGT_{tag}_Rim', 'AREA', rim_e, hexc('#FFE2B8'), t - d * dist * 0.9 + lft * 0.8 + Vector((0, 0, 1.6)), size=0.7, size_y=1.4)
    for l_, e_ in ((k, key_e), (fl, fill_e), (rm, rim_e)):
        look_at(l_, t); window_on(l_, f0, f1, e_)
sc.frame_set(100)                       # o carro do Marcos anda durante o plano: as luzes ficam presas a ele
_t2 = rM.matrix_world @ Vector((0, 0, 1.55)) if False else carM.matrix_world.translation + Vector((0, 0, 1.15))
three_point('P02_Marcos', 73, 144, tuple(_t2), (-1, 0, 0), 140, 60, 260, 1.8)
for _l in [o for o in cL.objects if o.name.startswith('LGT_P02_Marcos')]:
    _l.parent = carM; _l.matrix_parent_inverse = carM.matrix_world.inverted()
three_point('P06_Miguel', 289, 396, (MIGUEL_POS[0], MIGUEL_POS[1], 1.5), (-1, -0.7, 0), 520, 120, 650, 2.6)
three_point('P07_Claudio', 397, 492, (CLAUDIO_POS[0], CLAUDIO_POS[1], 1.45), (1, 1.4, 0), 520, 120, 650, 2.6)
three_point('P10_Marcos', 601, 720, AZ(-12.05, 2.2, 1.15), (-1, 0, 0), 55, 25, 180, 1.8)

# ---------------- Apartamento: âmbar do abajur x azul da TV, bokeh pela janela
lamp = light('LGT_Apartamento_Abajur', 'POINT', 70, hexc('#FFB46B'), AZ(-11.9, 0.45, 1.25), radius=0.1, temp=2700)
key(lamp.data, 'energy', 70, 1); key(lamp.data, 'energy', 70, 613); key(lamp.data, 'energy', 28, 621)      # depois da TV: 40%
tvl = light('LGT_Apartamento_TV', 'AREA', 80, hexc('#8EC5FF'), AZ(-14.9, 2.2, 1.35), (0, -90, 0), size=0.7, size_y=1.2)
fillA = light('LGT_Apartamento_Preenchimento', 'AREA', 170, hexc('#FFB46B'), AZ(-12.4, 2.6, 2.7), size=3.5, size_y=3.5)
key(fillA.data, 'energy', 170, 613); key(fillA.data, 'energy', 68, 621)
light('LGT_Apartamento_RimJanela', 'AREA', 120, hexc('#7F9CFF'), AZ(-9.4, 2.5, 1.8), (0, 90, 0), size=2.5, size_y=1.6)
light('LGT_Apartamento_Corredor', 'POINT', 80, hexc('#FFE9C0'), AZ(-13.2, 7.0, 2.4), radius=0.2, temp=3500)
# luz da TV sincronizada com o vídeo do telejornal (cor e intensidade médias de cada ~3 frames)
news_avg = []
if news_files:
    try:
        for i in range(0, len(news_files), 3):
            im = D.images.load(os.path.join(NEWS_DIR, news_files[i])); im.scale(24, 14)
            px = list(im.pixels); n_ = len(px) // 4
            news_avg.append((sum(px[0::4]) / n_, sum(px[1::4]) / n_, sum(px[2::4]) / n_)); D.images.remove(im)
    except Exception as ex:
        news_avg = []
key(tvl.data, 'energy', 0, 1, 'CONSTANT'); key(tvl.data, 'energy', 0, 537, 'CONSTANT')
if news_avg:
    for i, (r_, g_, b_) in enumerate(news_avg):
        f = TV_F0 + 3 * i
        if f > 613: break
        mxv = max(r_, g_, b_, 1e-3); lum = 0.3 * r_ + 0.59 * g_ + 0.11 * b_
        tvl.data.color = (0.45 + 0.55 * r_ / mxv, 0.55 + 0.45 * g_ / mxv, 0.75 + 0.25 * b_ / mxv)
        tvl.data.keyframe_insert('color', frame=f); key(tvl.data, 'energy', 25 + 260 * lum, f, 'LINEAR')
else:
    key(tvl.data, 'energy', 80, 538, 'LINEAR'); key(tvl.data, 'energy', 80, 613); noise_mod(tvl.data, 'energy', 0, 40, 3.0, f0=540, f1=612)
key(tvl.data, 'energy', 0, 614, 'CONSTANT')       # a luz azul cai a zero em 3 frames
key(tvl.data, 'energy', 120, 613, 'CONSTANT') if False else None
em_node = next(n for n in D.materials['MAT_TV_Tela'].node_tree.nodes if n.type == 'EMISSION')
key(em_node.inputs['Strength'], 'default_value', 1.5, 537, 'CONSTANT')

# ---------------- Qualidade: Eevee Next com Raytracing + sombras suaves + AO/GI
ee = sc.eevee
try:
    ee.use_raytracing = True; ee.use_shadows = True
    ee.ray_tracing_options.resolution_scale = '1'
    ee.fast_gi_method = 'GLOBAL_ILLUMINATION'
except Exception: pass

# ---------------- Compositor: glare suave, lens distortion (briga), grading quente/frio, vinheta, grão
ng = D.node_groups.new('COMP_Cena02', 'CompositorNodeTree')
sc.compositing_node_group = ng
ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
N = ng.nodes; Lk = ng.links
rl = N.new('CompositorNodeRLayers'); rl.location = (-1000, 0)
gl = N.new('CompositorNodeGlare'); gl.location = (-780, 0)
try: gl.inputs['Type'].default_value = 'Fog Glow'
except Exception: pass
gl.inputs['Threshold'].default_value = 1.0
try: gl.inputs['Strength'].default_value = 0.7; gl.inputs['Size'].default_value = 0.5
except Exception: pass
ld_ = N.new('CompositorNodeLensdist'); ld_.location = (-560, 0)
for f, v in ((1, 0.0), (253, 0.01), (493, 0.0)):
    key(ld_.inputs['Dispersion'], 'default_value', v, f, 'CONSTANT'); key(ld_.inputs['Distortion'], 'default_value', -0.01 if v else 0.0, f, 'CONSTANT')
cb = N.new('CompositorNodeColorBalance'); cb.location = (-340, 0)
try:
    cb.inputs['Type'].default_value = 'Lift/Gamma/Gain'
    cb.inputs[4].default_value = (0.93, 0.97, 1.07, 1)      # lift azulado nas sombras
    cb.inputs[8].default_value = (1.10, 1.02, 0.90, 1)      # highlights dourados
except Exception: pass
el = N.new('CompositorNodeEllipseMask'); el.location = (-780, -350); el.inputs['Size'].default_value = (0.92, 0.82)
bl = N.new('CompositorNodeBlur'); bl.location = (-560, -350)
try: bl.inputs['Size'].default_value = (180, 180)
except Exception: pass
ma = N.new('ShaderNodeMath'); ma.operation = 'MULTIPLY_ADD'; ma.location = (-340, -350); ma.inputs[1].default_value = 0.38; ma.inputs[2].default_value = 0.62
mul = N.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.location = (-100, 0); mul.inputs['Factor'].default_value = 1.0
wn = N.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '4D'; wn.location = (-340, -600)
ic = N.new('CompositorNodeImageCoordinates'); ic.location = (-560, -600)
tm = N.new('CompositorNodeSceneTime'); tm.location = (-560, -750)
gr = N.new('ShaderNodeMix'); gr.data_type = 'RGBA'; gr.blend_type = 'OVERLAY'; gr.location = (120, 0); gr.inputs['Factor'].default_value = 0.035
out = N.new('NodeGroupOutput'); out.location = (360, 0)
Lk.new(rl.outputs['Image'], gl.inputs['Image']); Lk.new(gl.outputs[0], ld_.inputs['Image']); Lk.new(ld_.outputs[0], cb.inputs['Image'])
Lk.new(el.outputs[0], bl.inputs[0]); Lk.new(bl.outputs[0], ma.inputs[0])
Lk.new(cb.outputs[0], sock(mul.inputs, 'A')); Lk.new(ma.outputs[0], sock(mul.inputs, 'B'))
Lk.new(ic.outputs[0], wn.inputs['Vector']); Lk.new(tm.outputs[0], wn.inputs['W'])
Lk.new(sock(mul.outputs, 'Result'), sock(gr.inputs, 'A')); Lk.new(wn.outputs['Value'], sock(gr.inputs, 'B'))
Lk.new(sock(gr.outputs, 'Result'), out.inputs[0])

# ---------------- Fade to black (frames 708-720)
key(sc.view_settings, 'exposure', 0.7, 1, 'CONSTANT'); key(sc.view_settings, 'exposure', 0.7, 708); key(sc.view_settings, 'exposure', -9.3, 720)
sc.frame_set(1)
