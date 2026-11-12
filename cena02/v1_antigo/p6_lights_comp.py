# Parte 6 - Iluminação por ambiente + compositor + estados da TV
sc = bpy.context.scene
cL = col('LIGHTS')

def light(name, kind, energy, color, loc, rot=(0, 0, 0), size=None, size_y=None, radius=None, temp=None):
    ld = D.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if temp:
        ld.use_temperature = True; ld.temperature = temp
    if kind == 'AREA':
        ld.shape = 'RECTANGLE'; ld.size = size; ld.size_y = size_y
    if radius is not None:
        ld.shadow_soft_size = radius
    o = D.objects.new(name, ld); link(o, cL)
    o.location = loc; o.rotation_euler = [rad(a) for a in rot]
    return o

# ---------------- Portaria: Sun 1.5, 5500 K, ângulo 15°
sun = light('LGT_Portaria_Sol', 'SUN', 1.5, (1, 1, 1), (0, 0, 30), (52, 0, -38), temp=5500)
sun.data.angle = rad(15)
key(sun.data, 'energy', 1.5, 1, 'CONSTANT'); key(sun.data, 'energy', 0.0, 205, 'CONSTANT')

# ---------------- Garagem: 6 áreas 1.2 x 0.1 m, 150 W, #E8F5E0; uma pisca
gcol = hexc('#E8F5E0')
for i, (tx, ty) in enumerate(TUBES):
    l_ = light(f'LGT_Garagem_Tubo_{i}', 'AREA', 150, gcol, G(tx, ty, 2.26), size=0.1, size_y=1.2)
    if i == FLICKER:
        key(l_.data, 'energy', 150, 1)
        fc = find_fc(l_.data, 'energy', 0)
        nm = fc.modifiers.new('NOISE'); nm.strength = 260; nm.scale = 2.2; nm.phase = 7.0
        st = fc.modifiers.new('STEPPED'); st.frame_step = 2
        lm = fc.modifiers.new('LIMITS'); lm.use_min_y = True; lm.min_y = 12; lm.use_max_y = True; lm.max_y = 170
        # emissão do tubo segue a luz
        inp = bsdf(D.materials['MAT_Fluorescente_Pisca']).inputs['Emission Strength']
        dfc = inp.driver_add('default_value')
        v = dfc.driver.variables.new(); v.name = 'e'; v.type = 'SINGLE_PROP'
        v.targets[0].id_type = 'LIGHT'; v.targets[0].id = l_.data; v.targets[0].data_path = 'energy'
        dfc.driver.expression = 'e/150*6'
light('LGT_Garagem_FillFrio', 'AREA', 1500, hexc('#9FB7D9'), G(0, 0, 2.2), size=10, size_y=24)

fb_ = light('LGT_Garagem_FillBriga', 'AREA', 90, hexc('#BFD3E8'), G(-1.3, 0.2, 1.9), size=1.5, size_y=1.0)
look_at(fb_, G(-1.3, 2.6, 1.4))

# ---------------- Apartamento
lamp = light('LGT_Apartamento_Abajur', 'POINT', 60, hexc('#FFB46B'), A(-1.65, -2.0, 1.1), radius=0.08)
key(lamp.data, 'energy', 60, 1); key(lamp.data, 'energy', 60, 613); key(lamp.data, 'energy', 24, 621)
tvl = light('LGT_Apartamento_TV', 'AREA', 80, hexc('#8EC5FF'), A(0, 2.2, 1.15), (-90, 0, 0), size=1.2, size_y=0.7)
key(tvl.data, 'energy', 0, 1, 'CONSTANT'); key(tvl.data, 'energy', 80, 538); key(tvl.data, 'energy', 80, 614, 'LINEAR')
key(tvl.data, 'energy', 0, 617)
noise_mod(tvl.data, 'energy', 0, 45, 3.0, f0=540, f1=612)
light('LGT_Apartamento_RimJanela', 'AREA', 20, hexc('#7F9CC8'), A(0, -2.45, 1.6), (90, 0, 0), size=2.0, size_y=1.2)
fillA = light('LGT_Apartamento_Preenchimento', 'AREA', 90, hexc('#FFB46B'), A(0, 0, 2.6), size=4, size_y=3)
key(fillA.data, 'energy', 90, 613); key(fillA.data, 'energy', 40, 621)
# rebatimento quente do abajur no rosto (acompanha a queda para 40%)
kr = light('LGT_Apartamento_RebateRosto', 'AREA', 30, hexc('#FFB46B'), A(-1.0, -0.6, 1.55), size=0.8, size_y=0.8)
look_at(kr, A(0, -1.9, 1.15))
key(kr.data, 'energy', 30, 613); key(kr.data, 'energy', 12, 621)
# brilho emissivo da tela acompanha a luz da TV
em_node = next(n for n in D.materials['MAT_TV_Tela'].node_tree.nodes if n.type == 'EMISSION')
key(em_node.inputs['Strength'], 'default_value', 1.6, 538)

# ---------------- Compositor (Blender 5: node group de composição)
ng = D.node_groups.new('COMP_Cena02', 'CompositorNodeTree')
sc.compositing_node_group = ng
ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
N = ng.nodes; Lk = ng.links
rl = N.new('CompositorNodeRLayers'); rl.location = (-900, 0)
gl = N.new('CompositorNodeGlare'); gl.location = (-650, 0)
for val in ('Fog Glow', 'FOG_GLOW'):
    try: gl.inputs['Type'].default_value = val; break
    except Exception: pass
gl.inputs['Threshold'].default_value = 1.2
try: gl.inputs['Strength'].default_value = 0.6
except Exception: pass
ld_ = N.new('CompositorNodeLensdist'); ld_.location = (-420, 0)
disp = ld_.inputs['Dispersion']; dist = ld_.inputs['Distortion']
for f, v in ((1, 0.0), (253, 0.01), (493, 0.0)):
    key(disp, 'default_value', v, f, 'CONSTANT')
    key(dist, 'default_value', -0.01 if v else 0.0, f, 'CONSTANT')
el = N.new('CompositorNodeEllipseMask'); el.location = (-650, -350)
el.inputs['Size'].default_value = (0.92, 0.82)
bl = N.new('CompositorNodeBlur'); bl.location = (-420, -350)
try: bl.inputs['Size'].default_value = (180, 180)
except Exception: pass
ma = N.new('ShaderNodeMath'); ma.operation = 'MULTIPLY_ADD'; ma.location = (-200, -350)
ma.inputs[1].default_value = 0.45; ma.inputs[2].default_value = 0.55
mul = N.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.location = (0, 0)
mul.inputs['Factor'].default_value = 1.0
wn = N.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '4D'; wn.location = (-200, -600)
ic = N.new('CompositorNodeImageCoordinates'); ic.location = (-420, -600)
tm = N.new('CompositorNodeSceneTime'); tm.location = (-420, -750)
gr = N.new('ShaderNodeMix'); gr.data_type = 'RGBA'; gr.blend_type = 'OVERLAY'; gr.location = (220, 0)
gr.inputs['Factor'].default_value = 0.06
out = N.new('NodeGroupOutput'); out.location = (450, 0)
Lk.new(rl.outputs['Image'], gl.inputs['Image'])
Lk.new(gl.outputs[0], ld_.inputs['Image'])
Lk.new(el.outputs[0], bl.inputs[0])
Lk.new(bl.outputs[0], ma.inputs[0])
Lk.new(ld_.outputs[0], sock(mul.inputs, 'A'))
Lk.new(ma.outputs[0], sock(mul.inputs, 'B'))
Lk.new(ic.outputs[0], wn.inputs['Vector'])
Lk.new(tm.outputs[0], wn.inputs['W'])
Lk.new(sock(mul.outputs, 'Result'), sock(gr.inputs, 'A'))
Lk.new(wn.outputs['Value'], sock(gr.inputs, 'B'))
Lk.new(sock(gr.outputs, 'Result'), out.inputs[0])

# ---------------- Fade to black (frames 708-720)
key(sc.view_settings, 'exposure', 0.0, 708)
key(sc.view_settings, 'exposure', -10.0, 720)
sc.frame_set(1)
