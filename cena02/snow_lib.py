# Biblioteca comum para a animacao do Snow (Marcos) fora do carro e no apartamento. Importada por v2_snow_exit.py / v2_snow_apto.py.
# Rodar sempre com:  blender -b cena02_v2.blend -S Scene --python cena02/v2_snow_<parte>.py
import bpy, re, math
from mathutils import Vector, Matrix

sc = bpy.context.scene
assert sc.name == "Scene", "rode com -S Scene"
rig = bpy.data.objects["RIG-Snow"]
rm = bpy.data.objects["RIG_Marcos"]          # rig antigo: carrega o movimento de raiz (ROOT_Snow copia local/rotacao dele)
pb = rig.pose.bones
assert rig.animation_data and rig.animation_data.action, "rode v2_snow_car.py e v2_snow_car_face.py antes"
UP = Vector((0, 0, 1))
_meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith("GEO-snow")]
_was = {o.name: o.hide_viewport for o in _meshes}
for o in _meshes: o.hide_viewport = True      # autoria sem as malhas (rig de 1494 ossos)
upd = bpy.context.view_layer.update
_prev = {}

def finish():
    for o in _meshes: o.hide_viewport = _was[o.name]
    sc.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

def fcurves():
    a = rig.animation_data.action
    return list(a.fcurves) if hasattr(a, "fcurves") else [fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]

def smooth_new(skip_const=True):
    for fc in fcurves():
        if skip_const and any(kp.interpolation == 'CONSTANT' for kp in fc.keyframe_points): continue
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'

# --------------------------------------------------------------- geometria
def frame(f): sc.frame_set(f); upd()
def axes():
    R3 = rig.matrix_world.to_3x3()
    return R3.inverted(), (R3 @ Vector((0, -1, 0))).normalized(), (R3 @ Vector((1, 0, 0))).normalized()   # R3^-1, frente, esquerda
def root_world():
    m = rig.matrix_world; return m.translation.copy()
def aim(name, wdir, twist=0.0):
    R3i, _, _ = axes()
    b = pb[name]; M = b.matrix.copy(); tgt = (R3i @ wdir).normalized(); cur = M.to_3x3().col[1].normalized()
    m3 = cur.rotation_difference(tgt).to_matrix() @ M.to_3x3()
    if twist: m3 = Matrix.Rotation(math.radians(twist), 3, tgt) @ m3
    b.matrix = Matrix.Translation(M.translation) @ m3.to_4x4(); upd()
def place(name, wpos, wdir=None, twist=0.0):
    b = pb[name]; M = b.matrix.copy(); M.translation = rig.matrix_world.inverted() @ wpos; b.matrix = M; upd()
    if wdir is not None: aim(name, wdir, twist)
def key(name, f, loc=False, interp=None):
    b = pb[name]
    if b.rotation_mode == 'QUATERNION': b.keyframe_insert("rotation_quaternion", frame=f)
    else:
        e = b.rotation_euler.copy()
        if name in _prev: e.make_compatible(_prev[name])
        b.rotation_euler = e; _prev[name] = e.copy(); b.keyframe_insert("rotation_euler", frame=f)
    if loc: b.keyframe_insert("location", frame=f)
    if interp:
        for fc in fcurves():
            if fc.data_path.startswith(f'pose.bones["{name}"]'):
                for kp in fc.keyframe_points:
                    if round(kp.co[0]) == f: kp.interpolation = interp
def keyprop(bone, prop, value, f, interp='CONSTANT'):
    pb[bone][prop] = value; pb[bone].keyframe_insert(f'["{prop}"]', frame=f)
    for fc in fcurves():
        if fc.data_path == f'pose.bones["{bone}"]["{prop}"]':
            for kp in fc.keyframe_points:
                if round(kp.co[0]) == f: kp.interpolation = interp

# --------------------------------------------------------------- poses de corpo por direcao (out, fwd, up) ; side=+1 esquerda, -1 direita
def W(side, out, fwd, up):
    _, F, L = axes(); return (L * side * out + F * fwd + UP * up).normalized()
REL = dict(u=(0.15, 0.05, -0.99), f=(0.08, 0.25, -0.95))          # bracos baixos, relaxados
def arms(f, A, B=None, key_it=True):
    """A para os dois bracos, ou A (esq) e B (dir)"""
    B = B or A
    for side, nm, P in ((1, "L", A), (-1, "R", B)):
        aim(f"FK-UpperArm.{nm}", W(side, *P["u"])); aim(f"FK-Forearm.{nm}", W(side, *P["f"])); aim(f"FK-Wrist.{nm}", W(side, *P["f"]))
        if key_it:
            for b in ("UpperArm", "Forearm", "Wrist"): key(f"FK-{b}.{nm}", f)
def torso(f, lean=0, side=0, hpitch=0, hside=0, htwist=0):
    _, F, L = axes(); a, s = math.radians(lean), math.radians(side)
    aim("FK-Spine", (F * math.sin(a) + L * math.sin(s) + UP * math.cos(a)).normalized()); key("FK-Spine", f)
    aim("FK-Chest", (F * math.sin(a * 0.5) + L * math.sin(s * 0.5) + UP * math.cos(a * 0.5)).normalized()); key("FK-Chest", f)
    h, hs = math.radians(hpitch), math.radians(hside)
    aim("FK-Head", (F * math.sin(h) + L * math.sin(hs) + UP * math.cos(h)).normalized(), htwist); key("FK-Head", f)
def look_at(f, pt, head_share=0.5, pitch=0):
    """olhos (TGT-Eyes) no ponto do mundo; cabeca acompanha em head_share do giro horizontal"""
    _, F, L = axes()
    eye = rig.matrix_world @ (pb["FK-Head"].head + Vector((0, 0, 0.12)))
    d = (pt - eye); dh = Vector((d.x, d.y, 0)).normalized()
    th = math.degrees(math.atan2(F.cross(dh).z, F.dot(dh)))
    b = pb["TGT-Eyes"]; M = b.matrix.copy(); M.translation = rig.matrix_world.inverted() @ pt; b.matrix = M; upd(); b.keyframe_insert("location", frame=f)
    return max(-45, min(45, th * head_share))

# --------------------------------------------------------------- pes em IK
def ik_legs(on, f):
    for n in ("ik_left_thigh", "ik_right_thigh"): keyprop("Properties", n, 1.0 if on else 0.0, f)
def ik_arms(on, f):
    for n in ("ik_left_upperarm", "ik_right_upperarm"): keyprop("Properties", n, 1.0 if on else 0.0, f)
def foot(side, f, pos, fdir, lift=0.0, interp=None):
    nm = "L" if side > 0 else "R"
    place(f"IK-Foot.{nm}", pos + UP * lift, fdir); key(f"IK-Foot.{nm}", f, loc=True, interp=interp)

def stand_feet(f, ground_z, spread=0.11, interp=None):
    """pes plantados ao lado da raiz (no frame f), no chao"""
    frame(f); r = root_world(); _, F, L = axes()
    for side in (1, -1):
        p = Vector((r.x, r.y, ground_z + 0.08)) + L * side * spread
        foot(side, f, p, F, interp=interp)
    return r

def sample_root(f0, f1):
    out = {}
    for f in range(f0, f1 + 1):
        frame(f); r = root_world(); _, F, L = axes(); out[f] = (r, F.copy(), L.copy())
    return out

def walk(f0, f1, ground_z, step=0.5, spread=0.11, lift=0.12, swing=22, swing_arms=True):
    """caminhada com os pes em IK sem deslizar: cada passo pousa 1 passo a frente; bracos balancam em contrafase.
    Usa a trajetoria de RIG_Marcos nos frames f0..f1. Retorna a distancia andada."""
    S = sample_root(f0, f1)
    fr = list(range(f0, f1 + 1))
    dist = {f0: 0.0}
    for a, b in zip(fr[:-1], fr[1:]): dist[b] = dist[a] + (S[b][0] - S[a][0]).length
    total = dist[f1]
    def at_dist(d):                       # raiz/frente/esq na distancia d (extrapola para alem do fim com a ultima direcao)
        d = max(0.0, d)
        if d >= total:
            r, F, L = S[f1]; return r + F * (d - total), F, L
        for a, b in zip(fr[:-1], fr[1:]):
            if dist[a] <= d <= dist[b]:
                t = 0 if dist[b] == dist[a] else (d - dist[a]) / (dist[b] - dist[a])
                return S[a][0].lerp(S[b][0], t), S[a][1].lerp(S[b][1], t).normalized(), S[a][2].lerp(S[b][2], t).normalized()
        return S[f0]
    n = max(1, int(math.ceil(total / step)))
    # passo j: pe (esq se j par) decola em d=j*step e pousa em d=(j+1)*step + step*0.5 a frente do tronco naquele instante
    land = []
    for j in range(n + 2):
        r, F, L = at_dist((j + 1) * step)
        side = 1 if j % 2 == 0 else -1
        p = Vector((r.x, r.y, ground_z + 0.08)) + F * (step * 0.5) + L * side * spread
        land.append((side, j * step, (j + 1) * step, p, F))
    def foot_at(side, d):
        steps = [s for s in land if s[0] == side]
        r0, F0, L0 = S[f0]
        prev = (Vector((r0.x, r0.y, ground_z + 0.08)) + L0 * side * spread, F0)
        for (sd, d0, d1, p, F) in steps:
            if d < d0: break
            if d < d1:
                t = (d - d0) / (d1 - d0); t = t * t * (3 - 2 * t)
                return prev[0].lerp(p, t) + UP * (lift * math.sin(math.pi * t)), prev[1].lerp(F, t)
            prev = (p, F)
        return prev[0], prev[1]
    for f in fr:
        frame(f)
        for side in (1, -1):
            p, F = foot_at(side, dist[f]); foot(side, f, p, F)
        if not swing_arms: continue
        # bracos balancam em contrafase com os passos
        ph = (dist[f] / step) * math.pi
        for side, nm in ((1, "L"), (-1, "R")):
            a = math.sin(ph + (0 if side > 0 else math.pi)) * math.radians(swing)
            _, F, L = axes()
            u = (UP * -math.cos(a) + F * math.sin(a) + L * side * 0.12).normalized()
            aim(f"FK-UpperArm.{nm}", u); aim(f"FK-Forearm.{nm}", (u + F * 0.25).normalized()); aim(f"FK-Wrist.{nm}", (u + F * 0.25).normalized())
            for b in ("UpperArm", "Forearm", "Wrist"): key(f"FK-{b}.{nm}", f)
    return total

# --------------------------------------------------------------- rosto (poses prontas, mistura por peso)
def _fcs(a): return list(a.fcurves) if hasattr(a, "fcurves") else [fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
def pose_vals(name, flip=False):
    a = bpy.data.actions[name]; out = {}; f0 = a.frame_range[0]
    for fc in _fcs(a):
        m = re.match(r'pose\.bones\["([^"]+)"\]\.(\w+)', fc.data_path)
        if not (m and m.group(2) in ('location', 'rotation_euler', 'scale')): continue
        bone, prop, v = m.group(1), m.group(2), fc.evaluate(f0)
        if flip:
            bone = bone.replace(".L", ".R") if bone.endswith(".L") else (bone.replace(".R", ".L") if bone.endswith(".R") else bone)
            if prop == "location" and fc.array_index == 0: v = -v
            if prop == "rotation_euler" and fc.array_index in (1, 2): v = -v
        out[(bone, prop, fc.array_index)] = v
    return out
_H = {}
def hand(f, w_left=0.0, w_right=0.0):
    """maos: 0 = relaxada, 1 = punho (poses prontas do Snow; direita = espelho da esquerda)"""
    if not _H:
        _H["relL"], _H["fistL"] = pose_vals("Hand Relaxed"), pose_vals("Hand Fist")
        _H["relR"], _H["fistR"] = pose_vals("Hand Relaxed", True), pose_vals("Hand Fist", True)
    for side, w in (("L", w_left), ("R", w_right)):
        rel, fist = _H["rel" + side], _H["fist" + side]
        _write({k: v + w * (fist.get(k, v) - v) for k, v in rel.items()}, f)
_REST = lambda prop: 1.0 if prop == "scale" else 0.0
def _blend(base, poses):
    res = dict(base)
    for vals, w in poses:
        for k, v in vals.items():
            b = base.get(k, _REST(k[1])); res[k] = res.get(k, b) + w * (v - b)
    return res
def _write(vals, f):
    touched = set()
    for (bone, prop, idx), v in vals.items():
        if bone in pb: getattr(pb[bone], prop)[idx] = v; touched.add((bone, prop))
    for bone, prop in touched: pb[bone].keyframe_insert(prop, frame=f)
_eyeD = _mouD = _EYE = _MOU = None
def face(f, eye, mouth):
    global _eyeD, _mouD, _EYE, _MOU
    if _eyeD is None:
        _eyeD = pose_vals("Eyemask Default"); _mouD = pose_vals("Mouth Default")
        _EYE = {n: pose_vals(f"Eyemask {n}") for n in ("Sad", "Closed", "Relaxed", "Angry", "Scared", "Cocky", "Compressed")}
        _MOU = {n: pose_vals(f"Mouth {n}") for n in ("Compressed", "Openfrown", "Teethfrown", "Narrow", "Opensmile", "Default", "Oo", "Uu")}
    _write(_blend(_eyeD, [(_EYE[k], w) for k, w in eye.items()]), f)
    _write(_blend(_mouD, [(_MOU[k], w) for k, w in mouth.items()]), f)
def blink(f, eye, mouth, dur=8):
    face(f, eye, mouth); face(f + 3, {**eye, "Closed": 1.0}, mouth); face(f + dur, eye, mouth)
