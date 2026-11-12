# Cena 02 - helpers compartilhados (executado antes de cada parte)
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix, Euler, Quaternion
from bpy_extras import anim_utils

D = bpy.data
rad = math.radians
PI = math.pi

# Offsets de cada ambiente no mundo
OX_GAR = 100.0
OX_APT = 200.0
def G(x, y, z=0.0): return (x + OX_GAR, y, z)
def A(x, y, z=0.0): return (x + OX_APT, y, z)

def col(name):
    return D.collections[name]

# ---------------------------------------------------------------- cores
def srgb(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def hexc(h):
    h = h.lstrip('#')
    return tuple(srgb(int(h[i:i+2], 16) / 255) for i in (0, 2, 4))

# ---------------------------------------------------------------- materiais
def mat(name, color, rough=0.5, metal=0.0, emit=None, emit_str=0.0, alpha=1.0, coat=0.0, bump=0.0, sss=0.0):
    m = D.materials.get(name) or new_mat(name)
    b = bsdf(m)
    if sss and 'Subsurface Weight' in b.inputs: b.inputs['Subsurface Weight'].default_value = sss
    if bump and not m.get('_bump'):
        nt = m.node_tree; nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 9; nz.inputs['Detail'].default_value = 3
        bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.02
        nt.links.new(nz.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal']); m['_bump'] = 1
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if coat:
        b.inputs['Coat Weight'].default_value = coat
    if emit is not None:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = emit_str
    if alpha < 1.0:
        b.inputs['Alpha'].default_value = alpha
        m.surface_render_method = 'BLENDED'
    m.diffuse_color = (*color, 1)
    return m

def bsdf(m):
    return m.node_tree.nodes.get('Principled BSDF')

def sock(coll, name):
    # socket habilitado com esse nome (Mix tem vários 'A'/'B'/'Result')
    return next(s for s in coll if s.name == name and getattr(s, 'enabled', True))

def mat_out(m):
    return next(n for n in m.node_tree.nodes if n.type == 'OUTPUT_MATERIAL')

def new_mat(name, principled=True):
    """Material com árvore de nós garantida (Blender 5 pode criar vazia)."""
    m = D.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree
    out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if out is None:
        out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (300, 0)
    if principled and bsdf(m) is None:
        b = nt.nodes.new('ShaderNodeBsdfPrincipled'); b.name = 'Principled BSDF'
        nt.links.new(b.outputs[0], out.inputs['Surface'])
    if not principled:
        for n in list(nt.nodes):
            if n.type == 'BSDF_PRINCIPLED': nt.nodes.remove(n)
    return m

# ---------------------------------------------------------------- objetos
def link(o, c):
    c.objects.link(o)
    return o

def set_parent(child, parent):
    child.parent = parent
    child.matrix_parent_inverse = Matrix.Identity(4)

def empty(name, loc, c, size=0.3, kind='PLAIN_AXES', parent=None):
    o = D.objects.new(name, None)
    o.empty_display_type = kind
    o.empty_display_size = size
    link(o, c)
    o.location = loc
    if parent: set_parent(o, parent)
    return o

def bm_obj(name, bm, c, m=None, smooth=False):
    me = D.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.shade_smooth()
    o = D.objects.new(name, me)
    link(o, c)
    if m:
        if isinstance(m, (list, tuple)):
            for mm in m: me.materials.append(mm)
        else:
            me.materials.append(m)
    return o

def _place(o, loc, rot, parent):
    o.location = loc
    o.rotation_euler = [rad(a) for a in rot]
    if parent: set_parent(o, parent)
    return o

def box(name, size, loc, m, c, rot=(0, 0, 0), bevel=None, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    o = bm_obj(name, bm, c, m)
    if bevel is None:   # automático: ~10% da menor dimensão, entre 3 mm e 12 cm
        bevel = max(0.003, min(0.12, 0.10 * min(size)))
    if bevel:
        md = o.modifiers.new('Bevel', 'BEVEL')
        md.width = bevel; md.segments = 3; md.limit_method = 'ANGLE'; md.harden_normals = False
    return _place(o, loc, rot, parent)

def sphere(name, r, loc, m, c, rot=(0, 0, 0), segs=(24, 12), parent=None):
    if not isinstance(r, (tuple, list)): r = (r, r, r)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs[0], v_segments=segs[1], radius=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * r[0], v.co.y * r[1], v.co.z * r[2]))
    o = bm_obj(name, bm, c, m, smooth=True)
    return _place(o, loc, rot, parent)

def cyl(name, r, h, loc, m, c, rot=(0, 0, 0), segs=24, r2=None, parent=None, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r,
                          radius2=(r if r2 is None else r2), depth=h)
    o = bm_obj(name, bm, c, m, smooth=smooth)
    if smooth:
        md = o.modifiers.new('Smooth', 'EDGE_SPLIT') if False else None
    return _place(o, loc, rot, parent)

def beam(name, a, b, t, m, c, parent=None):
    a = Vector(a); b = Vector(b); d = b - a
    o = box(name, (t, t, d.length), (a + b) / 2, m, c, parent=None)
    o.rotation_euler = Vector((0, 0, 1)).rotation_difference(d).to_euler()
    if parent: set_parent(o, parent)
    return o

def quad(name, pts, m, c, parent=None):
    me = D.meshes.new(name)
    me.from_pydata([Vector(p) for p in pts], [], [list(range(len(pts)))])
    o = D.objects.new(name, me); link(o, c)
    me.materials.append(m)
    if parent: set_parent(o, parent)
    return o

def torus(name, R, r, loc, m, c, rot=(0, 0, 0), seg=32, rseg=10, parent=None):
    verts, faces = [], []
    for i in range(seg):
        a = 2 * PI * i / seg
        for j in range(rseg):
            b = 2 * PI * j / rseg
            verts.append(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
    for i in range(seg):
        for j in range(rseg):
            i2 = (i + 1) % seg; j2 = (j + 1) % rseg
            faces.append([i * rseg + j, i2 * rseg + j, i2 * rseg + j2, i * rseg + j2])
    me = D.meshes.new(name); me.from_pydata(verts, [], faces); me.shade_smooth()
    o = D.objects.new(name, me); link(o, c); me.materials.append(m)
    return _place(o, loc, rot, parent)

def text(name, body, size, loc, rot, m, c, extrude=0.0, align='CENTER', parent=None):
    cu = D.curves.new(name, 'FONT')
    cu.body = body; cu.size = size; cu.align_x = align; cu.align_y = 'CENTER'
    cu.extrude = extrude
    o = D.objects.new(name, cu); link(o, c)
    cu.materials.append(m)
    return _place(o, loc, rot, parent)

def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

# ---------------------------------------------------------------- animação
def fcurves(idb):
    adt = idb.animation_data
    if not adt or not adt.action: return []
    cb = anim_utils.animdata_get_channelbag_for_assigned_slot(adt)
    return list(cb.fcurves) if cb else []

def find_fc(idb, path, index=0):
    for fc in fcurves(idb):
        if fc.data_path == path and fc.array_index == index:
            return fc
    return None

def set_interp(owner, prop, frame, interp, easing=None):
    idb = owner.id_data
    path = owner.path_from_id(prop)
    for fc in fcurves(idb):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                if abs(kp.co.x - frame) < 0.01:
                    kp.interpolation = interp
                    if easing: kp.easing = easing

def key(owner, prop, value, frame, interp=None, easing=None):
    """Define valor e insere keyframe. interp: 'CONSTANT','LINEAR','BEZIER','BACK','BOUNCE'..."""
    if value is not None:
        setattr(owner, prop, value)
    owner.keyframe_insert(prop, frame=frame)
    set_interp(owner, prop, frame, interp or 'BEZIER', easing)

def key_vis(o, frame, visible):
    """Liga/desliga objeto no render e viewport (constante)."""
    key(o, 'hide_render', not visible, frame, 'CONSTANT')
    key(o, 'hide_viewport', not visible, frame, 'CONSTANT')

def noise_mod(idb, path, index, strength, scale, phase=None, f0=None, f1=None):
    fc = find_fc(idb, path, index)
    if fc is None: return None
    m = fc.modifiers.new('NOISE')
    m.strength = strength; m.scale = scale
    m.phase = phase if phase is not None else random.uniform(0, 100)
    if f0 is not None:
        m.use_restricted_range = True
        m.frame_start = f0; m.frame_end = f1
        m.blend_in = 2; m.blend_out = 2
    return m

# ---------------------------------------------------------------- poses (rig)
def pose(rig, p, frame=None, interp=None):
    """p = {bone: (x,y,z)} em graus, eixos do armature em repouso."""
    for bname, e in p.items():
        pb = rig.pose.bones.get(bname)
        if pb is None: continue
        R = pb.bone.matrix_local.to_3x3()
        Dm = Euler((rad(e[0]), rad(e[1]), rad(e[2])), 'XYZ').to_matrix()
        basis = R.inverted() @ Dm @ R
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = basis.to_euler('XYZ', pb.rotation_euler)
        if frame is not None:
            pb.keyframe_insert('rotation_euler', frame=frame)
            set_interp(pb, 'rotation_euler', frame, interp or 'BEZIER')

def merge(*ps):
    out = {}
    for p in ps: out.update(p)
    return out

def mirror(p):
    """Espelha pose L<->R (inverte Y e Z)."""
    out = {}
    for k, (x, y, z) in p.items():
        if k.endswith('.L'): k2 = k[:-2] + '.R'
        elif k.endswith('.R'): k2 = k[:-2] + '.L'
        else: k2 = k
        out[k2] = (x, -y, -z)
    return out

def root(rig, loc, rz_deg, frame, interp=None, scale=None):
    key(rig, 'location', loc, frame, interp)
    key(rig, 'rotation_euler', (0, 0, rad(rz_deg)), frame, interp)
    if scale is not None:
        key(rig, 'scale', scale, frame, interp)

def sk(ctrl, name, value, frame, interp=None):
    """Key de expressão facial: propriedade custom do empty FACE_<nome> (que aciona as shape keys por driver)."""
    ctrl[name] = float(value)
    ctrl.keyframe_insert('["%s"]' % name, frame=frame)
    for fc in fcurves(ctrl):
        if fc.data_path == '["%s"]' % name:
            for kp in fc.keyframe_points:
                if abs(kp.co.x - frame) < 0.01: kp.interpolation = interp or 'BEZIER'

def yaw(dx, dy):
    """Rotação Z (graus) para um personagem (que olha para -Y em repouso) olhar na direção (dx,dy)."""
    return math.degrees(math.atan2(dx, -dy))

def ploc(rig, bname, delta, frame=None, interp=None):
    """Posição de um osso (ex.: alvo do olhar 'eyes') como deslocamento no espaço do rig."""
    pb = rig.pose.bones[bname]
    R = pb.bone.matrix_local.to_3x3()
    pb.location = R.inverted() @ Vector(delta)
    if frame is not None:
        pb.keyframe_insert('location', frame=frame)
        set_interp(pb, 'location', frame, interp or 'BEZIER')

VISEMES = ['A', 'E', 'I', 'O', 'U', 'MBP', 'FV', 'rest']
_VMAP = {'a': 'A', 'á': 'A', 'ã': 'A', 'â': 'A', 'à': 'A', 'e': 'E', 'é': 'E', 'ê': 'E',
         'i': 'I', 'í': 'I', 'o': 'O', 'ó': 'O', 'õ': 'O', 'ô': 'O', 'u': 'U', 'ú': 'U',
         'm': 'MBP', 'b': 'MBP', 'p': 'MBP', 'f': 'FV', 'v': 'FV'}

def lipsync(face, txt, f0, f1, amp=1.0):
    seq = []
    for ch in txt.lower():
        v = _VMAP.get(ch)
        if v is None and ch in ' ,.!?…': v = 'rest'
        if v and (not seq or seq[-1] != v): seq.append(v)
    n = len(seq)
    max_n = max(2, int((f1 - f0) / 2))
    if n > max_n:
        seq = [seq[int(i * n / max_n)] for i in range(max_n)]; n = max_n
    step = (f1 - f0) / n
    for i, v in enumerate(seq):
        f = round(f0 + i * step)
        for vv in VISEMES:
            sk(face, vv, (amp if vv == v else 0.0), f)
    for vv in VISEMES:
        sk(face, vv, 0.0, f0 - 2)
        sk(face, vv, 0.0, f1 + 2)
