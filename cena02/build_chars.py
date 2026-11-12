# build_chars.py - roda em Blender de FUNDO (Rigify limpo):
#   blender -b --factory-startup --python cena02/build_chars.py -- characters.blend
# Cria 3 personagens: Rigify (metarig humano) + malhas PLACEHOLDER separadas + rosto com shape keys + SLOT_ + FACE_ (controle).
import bpy, bmesh, math, sys, os, traceback, json
from mathutils import Vector, Matrix, Euler
BASE = os.path.dirname(os.path.abspath(__file__))
exec(compile(open(os.path.join(BASE, 'lib.py'), encoding='utf-8').read(), 'lib.py', 'exec'))
bpy.ops.preferences.addon_enable(module='rigify')
OUT = sys.argv[-1]

for o in list(D.objects): D.objects.remove(o, do_unlink=True)

# ------------------------------------------------------------------ geometria
def _unit_sphere(u, v):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    vs = [vv.co.copy() for vv in bm.verts]; fs = [[vv.index for vv in f.verts] for f in bm.faces]
    bm.free()
    return vs, fs
US_BIG = _unit_sphere(32, 16)
US_SMALL = _unit_sphere(16, 10)

def add_capsule(bm, a, b, ra, rb, mi, segs=16, rings=10):
    a = Vector(a); b = Vector(b); d = b - a; L = d.length
    q = Vector((0, 0, 1)).rotation_difference(d)
    res = bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    faces = set()
    for v in res['verts']:
        x, y, z = v.co
        if z < -1e-6: loc = Vector((x * ra, y * ra, z * ra))
        else: loc = Vector((x * rb, y * rb, L + z * rb))
        v.co = a + q @ loc
        faces.update(v.link_faces)
    for f in faces: f.material_index = mi; f.smooth = True

def add_ellipsoid(bm, c, r, mi, rot=None, segs=(20, 12)):
    res = bmesh.ops.create_uvsphere(bm, u_segments=segs[0], v_segments=segs[1], radius=1.0)
    Rm = rot.to_matrix() if rot is not None else Matrix.Identity(3)
    faces = set()
    for v in res['verts']:
        p = Vector((v.co.x * r[0], v.co.y * r[1], v.co.z * r[2]))
        v.co = Vector(c) + Rm @ p
        faces.update(v.link_faces)
    for f in faces: f.material_index = mi; f.smooth = True

def add_box(bm, c, size, mi, rot=None, bev=0.02):
    res = bmesh.ops.create_cube(bm, size=1.0)
    Rm = rot.to_matrix() if rot is not None else Matrix.Identity(3)
    for v in res['verts']:
        v.co = Vector(c) + Rm @ Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    faces = set(f for v in res['verts'] for f in v.link_faces)
    for f in faces: f.material_index = mi
    return res

def add_torus(bm, c, R, r, mi, axis_rot=None, seg=24, rseg=8):
    vs = []; fs = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for j in range(rseg):
            b = 2 * math.pi * j / rseg
            vs.append(Vector(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b))))
    Rm = axis_rot.to_matrix() if axis_rot is not None else Matrix.Identity(3)
    bvs = [bm.verts.new(Vector(c) + Rm @ p) for p in vs]
    for i in range(seg):
        for j in range(rseg):
            i2 = (i + 1) % seg; j2 = (j + 1) % rseg
            f = bm.faces.new([bvs[i * rseg + j], bvs[i2 * rseg + j], bvs[i2 * rseg + j2], bvs[i * rseg + j2]])
            f.material_index = mi; f.smooth = True

def seg_dist(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length

def weight_object(obj, bones, rig, sigma=0.03, fixed=None):
    """Pesos por proximidade (suaviza as juntas). fixed = {bone: 1.0} para peso rígido."""
    me = obj.data
    if fixed:
        for bn, w in fixed.items():
            vg = obj.vertex_groups.new(name=bn); vg.add(list(range(len(me.vertices))), w, 'REPLACE')
        return
    segs = {}
    for bn in bones:
        b = rig.data.bones.get(bn)
        if b: segs[bn] = (b.head_local.copy(), b.tail_local.copy())
    groups = {bn: obj.vertex_groups.new(name=bn) for bn in segs}
    acc = {bn: ([], []) for bn in segs}
    for v in me.vertices:
        p = v.co.copy()
        ds = {bn: seg_dist(p, a, b) for bn, (a, b) in segs.items()}
        dm = min(ds.values())
        ws = {bn: math.exp(-(d - dm) / sigma) for bn, d in ds.items()}
        tot = sum(ws.values())
        for bn, w in ws.items():
            w /= tot
            if w > 0.02: acc[bn][0].append(v.index); acc[bn][1].append(w)
    for bn, (idx, ww) in acc.items():
        for i, w in zip(idx, ww): groups[bn].add([i], w, 'REPLACE')

# ------------------------------------------------------------------ rosto
def _M(c, r, rot=(0, 0, 0)):
    return (Matrix.Translation(Vector(c)) @ Euler([math.radians(a) for a in rot], 'XYZ').to_matrix().to_4x4() @ Matrix.Diagonal((r[0], r[1], r[2], 1)))

def make_face(name, parts, keys, mats, c, loc):
    verts, faces, mids, ranges = [], [], [], {}
    for (pn, pc, pr, prot, mi, big) in parts:
        uv, uf = US_BIG if big else US_SMALL
        off = len(verts); M = _M(pc, pr, prot)
        verts += [M @ u for u in uv]; faces += [[i + off for i in f] for f in uf]; mids += [mi] * len(uf)
        ranges[pn] = (off, len(uv), big)
    me = D.meshes.new(name); me.from_pydata(verts, [], faces)
    for m_ in mats: me.materials.append(m_)
    for p_, mi in zip(me.polygons, mids): p_.material_index = mi
    me.shade_smooth()
    o = D.objects.new(name, me); link(o, c); o.location = loc
    o.shape_key_add(name='Basis', from_mix=False)
    for kname, over in keys.items():
        kb = o.shape_key_add(name=kname, from_mix=False); kb.value = 0.0; kb.slider_min = -1.0
        for pn, (kc, kr, krot) in over.items():
            if pn not in ranges: continue
            off, n, big = ranges[pn]
            uv = (US_BIG if big else US_SMALL)[0]; M = _M(kc, kr, krot)
            for i in range(n): kb.data[off + i].co = M @ uv[i]
    return o

SPEC = {
    'Marcos': dict(H=1.75, skin='#F0B791', hair='#5A3420', shirt='#7CB7F0', pants='#3C4A63', shoe='#4A2E22', tie='#C23B3B',
                   collar=True, rolled=True, stubble=True, bags='#A87888', lid=(0.017, 0.02), hair_style='curto', W=1.0, head=1.0),
    'Miguel': dict(H=1.80, skin='#EE9A70', hair='#3A2A20', shirt='#FF7A1A', pants='#46506A', shoe='#4A3220', boots=True, stain=True,
                   collar=True, mustache=True, vein=True, lid=(0.03, 0.012), hair_style='calvo', W=1.22, belly=0.07, head=1.04, brow_tilt=-6, shortsleeve=True),
    'Claudio': dict(H=1.72, skin='#D9A07C', hair='#1A1512', hair_rough=0.15, shirt='#F2EEE4', jacket='#3E78C8', pants='#2A2F3C', shoe='#F4F4F0',
                    lid=(0.028, 0.013), hair_style='gel', W=0.9, head=0.98, hem=True),
}

def build_character(N, cfg):
    H = cfg['H']; k = H / 2.1; W = cfg.get('W', 1.0); belly = cfg.get('belly', 0.0)
    c = D.collections.new('CHAR_' + N); bpy.context.scene.collection.children.link(c)
    lc = bpy.context.view_layer.layer_collection.children[c.name]
    bpy.context.view_layer.active_layer_collection = lc
    S = 1.09 * cfg.get('head', 1.0)
    center = Vector((0, -0.005, 1.781 * k + 0.08 * S))
    # --- metarig escalado para a altura-alvo e com os braços para baixo (pose A estreita)
    bpy.ops.object.armature_human_metarig_add()
    meta = bpy.context.active_object; meta.name = f'META_{N}'
    meta.scale = (k, k, k)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = meta.data.edit_bones
    for s, sg in (('L', 1), ('R', -1)):
        up = eb[f'upper_arm.{s}']
        chain = [up] + list(up.children_recursive)
        conn = {b.name: b.use_connect for b in chain}
        for b in chain: b.use_connect = False
        d0 = (up.tail - up.head).normalized(); d1 = Vector((0.12 * sg, 0.03, -1)).normalized()
        Mx = Matrix.Translation(up.head.copy()) @ d0.rotation_difference(d1).to_matrix().to_4x4() @ Matrix.Translation(-up.head.copy())
        for b in chain: b.transform(Mx)
        for b in chain: b.use_connect = conn[b.name]
    for s, sg in (('L', 1), ('R', -1)):   # olhos do rig alinhados ao rosto estilizado (cabeça grande)
        e = eb[f'eye.{s}']; e.head = Vector((sg * 0.055 * S, center.y - 0.12 * S, center.z + 0.025 * S)); e.tail = e.head + Vector((0, -0.025, 0))
    bpy.ops.object.mode_set(mode='OBJECT')
    meta.data.rigify_rig_basename = f'RIG_{N}' if hasattr(meta.data, 'rigify_rig_basename') else ''
    bpy.ops.pose.rigify_generate()
    rig = bpy.context.active_object
    rig.name = f'RIG_{N}'; rig.data.name = f'RIG_{N}_Data'
    for pbn in ('thigh_parent', 'upper_arm_parent'):
        for s in 'LR': rig.pose.bones[f'{pbn}.{s}']['IK_FK'] = 1.0        # braços e pernas em FK (IK disponível pela propriedade IK_FK)
    # --- ossos extras de movimento secundário (gravata / aba da jaqueta)
    extra = []
    bpy.ops.object.mode_set(mode='EDIT')
    eb = rig.data.edit_bones
    def ebone(nm, h, t, par):
        b = eb.new(nm); b.head = h; b.tail = t; b.parent = eb[par]; b.use_deform = True; b.use_connect = False; return b
    if cfg.get('tie'):
        ebone('tie.001', Vector((0, -0.125 * k * 1.15, 1.50 * k)), Vector((0, -0.14 * k, 1.33 * k)), 'DEF-spine.003')
        ebone('tie.002', Vector((0, -0.14 * k, 1.33 * k)), Vector((0, -0.145 * k, 1.17 * k)), 'tie.001'); extra += ['tie.001', 'tie.002']
        eb['tie.002'].use_connect = True
    if cfg.get('hem'):
        for s, sg in (('L', 1), ('R', -1)):
            ebone(f'hem.{s}', Vector((sg * 0.14 * k, -0.02, 1.12 * k)), Vector((sg * 0.16 * k, -0.02, 0.86 * k)), 'DEF-spine.001'); extra.append(f'hem.{s}')
    bpy.ops.object.mode_set(mode='OBJECT')
    Bn = lambda n: (rig.data.bones[n].head_local.copy(), rig.data.bones[n].tail_local.copy())
    BH = lambda n: Bn(n)[0]; BT = lambda n: Bn(n)[1]

    # --- materiais
    skin = mat(f'MAT_{N}_Pele', hexc(cfg['skin']), 0.5)
    b = bsdf(skin)
    for nm_, v_ in (('Subsurface Weight', 0.18), ('Subsurface Radius', None)):
        if v_ is not None and nm_ in b.inputs: b.inputs[nm_].default_value = v_
    if 'Subsurface Radius' in b.inputs: b.inputs['Subsurface Radius'].default_value = (0.9, 0.35, 0.2)
    if cfg.get('stubble'):
        nt = skin.node_tree
        tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ')
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -0.035; mr.inputs['From Max'].default_value = -0.065
        mr2 = nt.nodes.new('ShaderNodeMapRange'); mr2.inputs['From Min'].default_value = -0.02; mr2.inputs['From Max'].default_value = -0.07
        mul_ = nt.nodes.new('ShaderNodeMath'); mul_.operation = 'MULTIPLY'
        nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 900
        mul2 = nt.nodes.new('ShaderNodeMath'); mul2.operation = 'MULTIPLY'
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
        sock(mx.inputs, 'A').default_value = (*hexc(cfg['skin']), 1); sock(mx.inputs, 'B').default_value = (*hexc('#6B5A52'), 1)
        nt.links.new(tc.outputs['Object'], sp.inputs[0]); nt.links.new(sp.outputs['Z'], mr.inputs['Value']); nt.links.new(sp.outputs['Y'], mr2.inputs['Value'])
        nt.links.new(mr.outputs[0], mul_.inputs[0]); nt.links.new(mr2.outputs[0], mul_.inputs[1])
        nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
        nt.links.new(mul_.outputs[0], mul2.inputs[0]); nt.links.new(nz.outputs['Fac'], mul2.inputs[1])
        nt.links.new(mul2.outputs[0], sock(mx.inputs, 'Factor') if False else mx.inputs[0])
        nt.links.new(sock(mx.outputs, 'Result'), bsdf(skin).inputs['Base Color'])
    hair = mat(f'MAT_{N}_Cabelo', hexc(cfg['hair']), cfg.get('hair_rough', 0.55))
    shirt = mat(f'MAT_{N}_Camisa', hexc(cfg['shirt']), 0.7)
    pants = mat(f'MAT_{N}_Calca', hexc(cfg['pants']), 0.7)
    shoe = mat(f'MAT_{N}_Sapato', hexc(cfg['shoe']), 0.45)
    jacket = mat(f'MAT_{N}_Jaqueta', hexc(cfg.get('jacket', cfg['shirt'])), 0.75)
    tie = mat(f'MAT_{N}_Gravata', hexc(cfg.get('tie', '#B33A3A')), 0.5)
    tee = mat(f'MAT_{N}_Camiseta', hexc('#F2EFE6'), 0.8)
    graxa = mat('MAT_Graxa', hexc('#3A3128'), 0.6)
    eyew = mat('MAT_Olho', hexc('#FAF7EF'), 0.12); pupil = mat('MAT_Pupila', hexc('#1E140D'), 0.1)
    iris = mat(f'MAT_{N}_Iris', hexc('#4E8F5E' if N != 'Miguel' else '#8A5A32'), 0.15)
    m_mouth = mat('MAT_Boca', hexc('#5A1E1B'), 0.5); bags = mat(f'MAT_{N}_Olheira', hexc(cfg.get('bags', cfg['skin'])), 0.7)
    vein = mat('MAT_Veia', hexc('#B0384A'), 0.5)

    # --- CORPO (pele): pescoço, mãos grandes, antebraços descobertos
    bm = bmesh.new()
    add_capsule(bm, BH('DEF-spine.004') + Vector((0, 0.01, -0.02 * k)), BT('DEF-spine.005'), 0.056 * k * (1 + (W - 1) * 0.8), 0.05 * k, 0)
    hs = 1.3
    for s, sg in (('L', 1), ('R', -1)):
        hh = BH(f'DEF-hand.{s}'); fi = BH(f'DEF-f_index.01.{s}'); ft = BT(f'DEF-f_middle.03.{s}')
        ax = (ft - hh); axn = ax.normalized()
        rotq = Vector((0, 0, 1)).rotation_difference(axn)
        add_ellipsoid(bm, hh + ax * 0.33, (0.043 * hs * k * 1.1, 0.026 * hs * k * 1.1, 0.075 * hs * k * 1.1), 0, rot=rotq)
        for fn, rr in (('f_index', 0.0125), ('f_middle', 0.0135), ('f_ring', 0.0125), ('f_pinky', 0.011)):
            add_capsule(bm, BH(f'DEF-{fn}.01.{s}'), BT(f'DEF-{fn}.03.{s}'), rr * hs * k * 1.05, rr * hs * k * 0.9, 0, segs=10, rings=8)
        add_capsule(bm, BH(f'DEF-thumb.01.{s}'), BT(f'DEF-thumb.03.{s}'), 0.0155 * hs * k, 0.013 * hs * k, 0, segs=10, rings=8)
        if cfg.get('rolled') or cfg.get('shortsleeve'):  # antebraço nu
            e = BH(f'DEF-forearm.{s}'); w = BH(f'DEF-hand.{s}')
            add_capsule(bm, e + (w - e) * 0.08, w, 0.052 * k * (1 + (W - 1) * 0.5), 0.04 * k, 0)
    corpo = bm_obj(f'MESH_{N}_CORPO_PLACEHOLDER', bm, c, [skin])
    corpo.data.shade_smooth()
    # --- ROUPA
    bm = bmesh.new()
    cs = 0.178 * k
    smi = 3 if cfg.get('jacket') else 0
    add_ellipsoid(bm, (0, 0.0, 1.47 * k), (0.2 * W * k, 0.13 * k, 0.185 * k), 0)
    add_ellipsoid(bm, (0, -belly * 0.5, 1.22 * k), (0.162 * W * k, (0.115 + belly) * k, 0.17 * k), 0)
    add_ellipsoid(bm, (0, 0.0, 1.04 * k), (0.178 * W * k, 0.122 * k, 0.12 * k), 1)
    for s, sg in (('L', 1), ('R', -1)):
        sh = BH(f'DEF-upper_arm.{s}')
        add_ellipsoid(bm, sh + Vector((0, 0, 0.0)), (0.066 * W * k, 0.064 * k, 0.066 * k), smi)
        e = BH(f'DEF-forearm.{s}'); w = BH(f'DEF-hand.{s}')
        rs = 0.058 * k * (1 + (W - 1) * 0.7)
        if cfg.get('shortsleeve'):
            add_capsule(bm, sh, sh + (e - sh) * 0.62, rs * 1.15, rs * 1.08, smi)
        else:
            add_capsule(bm, sh, e, rs * 1.05, rs * 0.95, smi)
            if cfg.get('rolled'):
                add_torus(bm, e + (w - e) * 0.03, 0.05 * k, 0.017 * k, 0, axis_rot=Vector((0, 0, 1)).rotation_difference((w - e).normalized()))
            else:
                add_capsule(bm, e, w + (e - w) * 0.1, rs * 0.95, rs * 0.78, smi)
        hip = BH(f'DEF-thigh.{s}'); kn = BH(f'DEF-shin.{s}'); an = BH(f'DEF-foot.{s}')
        rt = 0.085 * k * (1 + (W - 1) * 0.6)
        add_capsule(bm, hip + Vector((0, 0, 0.02)), kn, rt, rt * 0.82, 1)
        add_capsule(bm, kn, an + Vector((0, 0, 0.03)), rt * 0.82, 0.062 * k, 1)
        ft = BT(f'DEF-foot.{s}'); tt = BT(f'DEF-toe.{s}')
        bh_ = 0.13 if cfg.get('boots') else 0.07
        add_ellipsoid(bm, Vector((an.x, (an.y + tt.y) / 2 - 0.01, bh_ * 0.32 * k + 0.025)), (0.058 * k, 0.15 * k, bh_ * k * 0.9 + 0.01), 2)
        if cfg.get('boots'):
            add_capsule(bm, Vector((an.x, an.y, 0.035)), Vector((an.x, an.y, 0.20 * k)), 0.07 * k, 0.07 * k, 2)
    if cfg.get('collar'):
        add_torus(bm, BH('DEF-spine.004') + Vector((0, 0.0, 0.0)), 0.07 * k, 0.022 * k, 0, axis_rot=Euler((math.radians(-10), 0, 0)))
    if cfg.get('jacket'):
        add_ellipsoid(bm, (0, 0.006, 1.47 * k), (0.215 * W * k * 1.2, 0.138 * k * 1.2, 0.185 * k * 1.25), 3)
        add_ellipsoid(bm, (0, 0.006, 1.2 * k), (0.18 * W * k * 1.15, 0.128 * k * 1.12, 0.17 * k * 1.2), 3)
        add_box(bm, (0, -0.128 * k * 1.2, 1.26 * k), (0.11 * k, 0.025 * k, 0.34 * k), 4)
        for s, sg in (('L', 1), ('R', -1)):
            e = BH(f'DEF-forearm.{s}'); w = BH(f'DEF-hand.{s}'); sh = BH(f'DEF-upper_arm.{s}')
            add_capsule(bm, e, w + (e - w) * 0.08, 0.06 * k, 0.05 * k, smi)
    if cfg.get('stain'):
        add_ellipsoid(bm, (0.085 * k, -0.13 * k * 1.15 - belly * 0.5, 1.2 * k), (0.045 * k, 0.012 * k, 0.035 * k), 5)
    roupa = bm_obj(f'MESH_{N}_ROUPA_PLACEHOLDER', bm, c, [shirt if not cfg.get('jacket') else tee, pants, shoe, jacket, tee, graxa])
    roupa.data.shade_smooth()
    # --- gravata / abas (movimento secundário)
    extras_objs = []
    if cfg.get('tie'):
        bm = bmesh.new()
        add_ellipsoid(bm, (0.0, -0.148 * k * 1.1, 1.505 * k), (0.026 * k, 0.02 * k, 0.026 * k), 0)
        add_box(bm, (0.0, -0.152 * k * 1.1, 1.36 * k), (0.07 * k, 0.014 * k, 0.28 * k), 0)
        gr = bm_obj(f'MESH_{N}_GRAVATA_PLACEHOLDER', bm, c, [tie]); gr.data.shade_smooth()
        weight_object(gr, ['tie.001', 'tie.002', 'DEF-spine.003'], rig, sigma=0.03); extras_objs.append(gr)
    if cfg.get('hem'):
        bm = bmesh.new()
        for s, sg in (('L', 1), ('R', -1)):
            add_ellipsoid(bm, (sg * 0.15 * k, 0.0, 0.98 * k), (0.065 * k, 0.13 * k, 0.15 * k), 0)
        hm = bm_obj(f'MESH_{N}_ABAS_JAQUETA_PLACEHOLDER', bm, c, [jacket]); hm.data.shade_smooth()
        weight_object(hm, ['hem.L', 'hem.R', 'DEF-spine.001', 'DEF-pelvis.L', 'DEF-pelvis.R'], rig, sigma=0.05); extras_objs.append(hm)
    # --- pesos
    arm_b = [f'DEF-{n}.{s}' for s in 'LR' for n in ('shoulder', 'upper_arm', 'upper_arm', 'forearm', 'hand')] + \
            [f'DEF-{n}.{s}{x}' for s in 'LR' for n in ('upper_arm', 'forearm') for x in ('.001',)]
    body_b = ['DEF-spine', 'DEF-spine.001', 'DEF-spine.002', 'DEF-spine.003', 'DEF-spine.004', 'DEF-spine.005', 'DEF-pelvis.L', 'DEF-pelvis.R'] + \
             [f'DEF-{n}.{s}{x}' for s in 'LR' for n in ('thigh', 'shin') for x in ('', '.001')] + [f'DEF-foot.{s}' for s in 'LR'] + [f'DEF-toe.{s}' for s in 'LR']
    fing_b = [f'DEF-{n}.{x}.{s}' for s in 'LR' for n in ('f_index', 'f_middle', 'f_ring', 'f_pinky', 'thumb') for x in ('01', '02', '03')] + [f'DEF-palm.0{i}.{s}' for s in 'LR' for i in range(1, 5)]
    weight_object(corpo, arm_b + fing_b + ['DEF-spine.003', 'DEF-spine.004', 'DEF-spine.005', 'DEF-spine.006'], rig, sigma=0.022)
    weight_object(roupa, arm_b + body_b + extra, rig, sigma=0.03)
    # --- rosto + cabelo + olhos
    eyeL = Vector((0.055 * S, center.y - 0.12 * S, center.z + 0.025 * S)); eyeR = Vector((-0.055 * S, center.y - 0.12 * S, center.z + 0.025 * S))
    E = 0.055
    lid_dz, lid_h = cfg['lid']
    h = lambda v: tuple(x * S for x in v)
    parts = [
        ('cranio', (0, 0, 0), h((0.14, 0.145, 0.165)), (0, 0, 0), 0, True),
        ('bochecha_L', h((0.075, -0.1, -0.05)), h((0.05, 0.04, 0.04)), (0, 0, 0), 0, False),
        ('bochecha_R', h((-0.075, -0.1, -0.05)), h((0.05, 0.04, 0.04)), (0, 0, 0), 0, False),
        ('orelha_L', h((0.14, 0.0, 0.0)), h((0.022, 0.035, 0.045)), (0, 0, 0), 0, False),
        ('orelha_R', h((-0.14, 0.0, 0.0)), h((0.022, 0.035, 0.045)), (0, 0, 0), 0, False),
        ('nariz', h((0, -0.15, -0.01)), h((0.024, 0.03, 0.034)), (0, 0, 0), 0, False),
        ('palpebra_L', h((E, -0.121, 0.025 + lid_dz)), h((0.037, 0.036, lid_h)), (0, 0, 0), 0, False),
        ('palpebra_R', h((-E, -0.121, 0.025 + lid_dz)), h((0.037, 0.036, lid_h)), (0, 0, 0), 0, False),
        ('olheira_L', h((E, -0.143, -0.011)), h((0.028, 0.009, 0.011)), (0, 0, 0), 2, False),
        ('olheira_R', h((-E, -0.143, -0.011)), h((0.028, 0.009, 0.011)), (0, 0, 0), 2, False),
        ('sobrancelha_L', h((E, -0.142, 0.075)), h((0.032, 0.01, 0.008)), (0, cfg.get('brow_tilt', 0), 0), 1, False),
        ('sobrancelha_R', h((-E, -0.142, 0.075)), h((0.032, 0.01, 0.008)), (0, -cfg.get('brow_tilt', 0), 0), 1, False),
        ('boca', h((0, -0.132, -0.07)), h((0.032, 0.012, 0.005)), (0, 0, 0), 3, False),
        ('canto_L', h((0.032, -0.13, -0.07)), h((0.008, 0.008, 0.008)), (0, 0, 0), 3, False),
        ('canto_R', h((-0.032, -0.13, -0.07)), h((0.008, 0.008, 0.008)), (0, 0, 0), 3, False),
    ]
    if cfg.get('mustache'): parts.append(('bigode', h((0, -0.148, -0.046)), h((0.045, 0.013, 0.012)), (0, 0, 0), 1, False))
    if cfg.get('vein'): parts.append(('veia', h((0.04, -0.095, 0.1)), h((0.001, 0.001, 0.003)), (0, 0, 0), 4, False))
    pd = {p[0]: p for p in parts}
    def ov(pn, dc=(0, 0, 0), sr=(1, 1, 1), rot=None):
        p = pd[pn]
        return (tuple(p[1][i] + dc[i] * S for i in range(3)), tuple(p[2][i] * sr[i] for i in range(3)), rot if rot is not None else p[3])
    def mouth(sx_, sz_, dz=0.0, dy=0.0, cdz=0.0, cdx=0.0):
        w = pd['boca'][2][0] * sx_
        d = {'boca': ov('boca', (0, dy, dz), (sx_, 1.0, sz_))}
        d['canto_L'] = ((w + cdx * S, pd['canto_L'][1][1] + dy * S, pd['canto_L'][1][2] + (dz + cdz) * S), pd['canto_L'][2], (0, 0, 0))
        d['canto_R'] = ((-(w + cdx * S), pd['canto_R'][1][1] + dy * S, pd['canto_R'][1][2] + (dz + cdz) * S), pd['canto_R'][2], (0, 0, 0))
        return d
    def lids(closed=1.0):
        d = {}
        for s in ('L', 'R'):
            p = pd[f'palpebra_{s}']
            ez = 0.025 * S
            cz = p[1][2] + (ez - p[1][2]) * closed; rz = p[2][2] + (0.039 * S - p[2][2]) * closed
            d[f'palpebra_{s}'] = ((p[1][0], p[1][1] - 0.006 * S * closed, cz), (p[2][0] * 1.02, p[2][1] * (1.05 + 0.3 * closed), rz), (0, 0, 0))
        return d
    tilt = cfg.get('brow_tilt', 0)
    keys = {
        'blink': lids(1.0), 'eyes_closed': lids(1.0),
        'brow_down': {'sobrancelha_L': ov('sobrancelha_L', (0, 0.002, -0.012)), 'sobrancelha_R': ov('sobrancelha_R', (0, 0.002, -0.012))},
        'brow_up': {'sobrancelha_L': ov('sobrancelha_L', (0, 0.002, 0.018), rot=(0, -6, 0)), 'sobrancelha_R': ov('sobrancelha_R', (0, 0.002, 0.018), rot=(0, 6, 0)), **lids(-0.6)},
        'brow_sad': {'sobrancelha_L': ov('sobrancelha_L', (0, 0, 0.004), rot=(0, tilt + 22, 0)), 'sobrancelha_R': ov('sobrancelha_R', (0, 0, 0.004), rot=(0, -tilt - 22, 0))},
        'brow_angry': {'sobrancelha_L': ov('sobrancelha_L', (0, 0.0, -0.01), rot=(0, -28, 0)), 'sobrancelha_R': ov('sobrancelha_R', (0, 0.0, -0.01), rot=(0, 28, 0))},
        'brow_smug': {'sobrancelha_L': ov('sobrancelha_L', (0, 0.002, 0.02), rot=(0, -10, 0)), 'sobrancelha_R': ov('sobrancelha_R', (0, 0.0, -0.006), rot=(0, 15, 0))},
        'mouth_frown': mouth(0.95, 0.8, 0, 0, -0.013, -0.002),
        'mouth_smile': mouth(1.35, 1.1, -0.002, 0, 0.012, 0.004),
        'mouth_smirk': {'canto_L': ov('canto_L', (0.006, 0, 0.012)), 'boca': ov('boca', (0.006, 0, 0.003), (1.05, 1, 1), rot=(0, -12, 0))},
        'mouth_shout': mouth(1.6, 9.0, -0.022, -0.004, 0.0, 0.006),
        'sigh': {'bochecha_L': ov('bochecha_L', (0.012, -0.012, 0), (1.45, 1.45, 1.35)), 'bochecha_R': ov('bochecha_R', (-0.012, -0.012, 0), (1.45, 1.45, 1.35)), **mouth(0.55, 0.6, 0, -0.008)},
        'nostril_flare': {'nariz': ov('nariz', (0, 0, 0), (1.45, 1.0, 1.05))},
        'A': mouth(1.1, 5.5, -0.012), 'E': mouth(1.35, 3.0, -0.006), 'I': mouth(1.3, 1.6, -0.002),
        'O': mouth(0.75, 4.5, -0.01, -0.004), 'U': mouth(0.5, 3.0, -0.006, -0.008), 'MBP': mouth(1.0, 0.25, 0, 0.0),
        'FV': mouth(0.95, 1.2, 0.002), 'rest': mouth(0.9, 0.6),
    }
    if cfg.get('vein'): keys['vein_pop'] = {'veia': (h((0.04, -0.112, 0.1)), h((0.006, 0.006, 0.03)), (0, 0, 14))}
    face = make_face(f'MESH_{N}_ROSTO_PLACEHOLDER', parts, keys, [skin, hair, bags, m_mouth, vein], c, center)
    weight_object(face, [], rig, fixed={'DEF-spine.006': 1.0})
    # cabelo (malha separada)
    bm = bmesh.new(); hs_ = cfg['hair_style']
    if hs_ == 'curto':
        add_ellipsoid(bm, center + Vector((0, 0.015, 0.035)) * 0 + Vector((0, 0.015 * S, 0.035 * S)), (0.147 * S, 0.153 * S, 0.147 * S), 0)
        add_ellipsoid(bm, center + Vector((0, -0.09 * S, 0.12 * S)), (0.1 * S, 0.06 * S, 0.04 * S), 0, rot=Euler((math.radians(-20), 0, 0)))
    elif hs_ == 'calvo':
        add_ellipsoid(bm, center + Vector((0, 0.035 * S, -0.015 * S)), (0.147 * S, 0.13 * S, 0.128 * S), 0)
    elif hs_ == 'gel':
        add_ellipsoid(bm, center + Vector((0, 0.012 * S, 0.04 * S)), (0.147 * S, 0.153 * S, 0.147 * S), 0)
        add_ellipsoid(bm, center + Vector((0, -0.09 * S, 0.14 * S)), (0.07 * S, 0.06 * S, 0.04 * S), 0, rot=Euler((math.radians(-25), 0, 0)))
        add_ellipsoid(bm, center + Vector((0, -0.04 * S, 0.19 * S)), (0.09 * S, 0.09 * S, 0.05 * S), 0)
    hairm = bm_obj(f'MESH_{N}_CABELO_PLACEHOLDER', bm, c, [hair]); hairm.data.shade_smooth()
    weight_object(hairm, [], rig, fixed={'DEF-spine.006': 1.0})
    # olhos: esfera + íris/pupila, presos aos ossos de olhar do Rigify
    eye_objs = []
    for s, ep in (('L', eyeL), ('R', eyeR)):
        bm = bmesh.new()
        add_ellipsoid(bm, (0, 0, 0), (0.032 * S,) * 3, 0, segs=(24, 14))
        add_ellipsoid(bm, (0, -0.026 * S, 0), (0.0205 * S, 0.0095 * S, 0.0205 * S), 1, segs=(20, 10))
        add_ellipsoid(bm, (0, -0.0335 * S, 0), (0.011 * S, 0.0052 * S, 0.011 * S), 2, segs=(16, 8))
        eo = bm_obj(f'MESH_{N}_OLHO_{s}_PLACEHOLDER', bm, c, [eyew, iris, pupil]); eo.data.shade_smooth()
        eo.location = ep
        eye_objs.append(eo)
    # --- hierarquia / organização
    for o_ in [corpo, roupa, face, hairm] + extras_objs:
        o_.parent = rig; o_.matrix_parent_inverse = Matrix.Identity(4)
        md = o_.modifiers.new('Armature', 'ARMATURE'); md.object = rig
    for eo, s in zip(eye_objs, 'LR'):
        for bn in (f'ORG-eye.{s}', f'eye.{s}'):
            if bn in rig.data.bones: break
        wm_t = eo.location.copy()
        eo.parent = rig; eo.parent_type = 'BONE'; eo.parent_bone = f'ORG-eye.{s}' if f'ORG-eye.{s}' in rig.data.bones else bn
        pb = rig.data.bones[eo.parent_bone]
        eo.matrix_parent_inverse = (rig.matrix_world @ pb.matrix_local @ Matrix.Translation((0, pb.length, 0))).inverted()
        eo.matrix_basis = Matrix.Translation(wm_t)
    slot = empty(f'SLOT_{N}', (0, 0, 0), c, 0.5, 'ARROWS')
    slot['altura_alvo_m'] = H; slot['nota'] = 'Importe o novo modelo aqui, escale para altura_alvo_m e retarget a animacao de RIG_' + N
    ctrl = empty(f'FACE_{N}', (0.5, 0.5, 2.1 * k), c, 0.12, 'SPHERE', parent=rig)
    for kb in face.data.shape_keys.key_blocks[1:]:
        ctrl[kb.name] = 0.0
        try: ctrl.id_properties_ui(kb.name).update(min=-1.0, max=1.0)
        except Exception: pass
        fc = kb.driver_add('value'); dr = fc.driver; dr.type = 'AVERAGE'
        v = dr.variables.new(); v.name = 'v'; v.type = 'SINGLE_PROP'
        v.targets[0].id = ctrl; v.targets[0].data_path = f'["{kb.name}"]'
    # coleção: tudo dentro de CHAR_N; metarig oculto
    for o_ in D.objects:
        if o_.name == f'META_{N}':
            for cc in list(o_.users_collection): cc.objects.unlink(o_)
            c.objects.link(o_); o_.hide_set(True); o_.hide_viewport = True
    rig['altura_alvo_m'] = H
    return dict(rig=rig, face=face)

try:
    info = {}
    for N, cfg in SPEC.items():
        r = build_character(N, cfg); info[N] = [r['rig'].name, r['face'].name]
    # coleções de widgets do Rigify: mantê-las no arquivo, fora da cena
    for c_ in D.collections:
        if c_.name.startswith('WGTS'):
            for p in list(D.collections):
                if c_.name in [x.name for x in p.children]: p.children.unlink(c_)
            if c_.name in [x.name for x in bpy.context.scene.collection.children]: bpy.context.scene.collection.children.unlink(c_)
            c_.use_fake_user = True
    info['colecoes'] = [c_.name for c_ in D.collections]
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    json.dump(info, open(OUT + '.json', 'w'), indent=1)
except Exception:
    open(OUT + '.err', 'w').write(traceback.format_exc())
