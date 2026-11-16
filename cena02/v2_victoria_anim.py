# Animacao da Victoria (ancora do telejornal, frames 1-103): SENTADA na cadeira atras da bancada, falando (mandibula), com gestos de jornalista
# (maos na bancada, mao direita enfatiza as manchetes, aponta para as imagens), acenos de cabeca e balanco do tronco.
# Uso: blender -b cena02_v2.blend -S SCN_Telejornal --python cena02/v2_victoria_anim.py
# (a cena ativa precisa ser SCN_Telejornal, senao o rig nao entra no depsgraph)
import bpy, math, re
from mathutils import Vector, Matrix

assert bpy.context.scene.name == "SCN_Telejornal", "rode com -S SCN_Telejornal"
rig = bpy.data.objects["RIG-Victoria"]
pb = rig.pose.bones
D = bpy.data
meshes = [o for o in D.objects if o.type == 'MESH' and o.name.startswith("GEO-victoria")]
_was = {o.name: o.hide_viewport for o in meshes}
for o in meshes: o.hide_viewport = True
upd = bpy.context.view_layer.update

# ---------------------------------------------------------------- sentada: raiz no chao com escala 1,25 (a Victoria e pequena; assim o busto aparece acima da bancada de 1,0 m)
root = D.objects["ROOT_Victoria"]
root.scale = (1.25, 1.25, 1.25); root.location = (500.1, 2.67, 0.0)
# cadeira: assento + haste mais alta (o encosto ja existia)
m_ch = D.materials.get("MAT_TJ_Cadeira")
if "TJ_Cadeira_Assento" not in D.objects:
    me = D.meshes.new("TJ_Cadeira_Assento"); import bmesh
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    seat = D.objects.new("TJ_Cadeira_Assento", me); D.objects["TJ_Cadeira_Encosto"].users_collection[0].objects.link(seat)
    seat.scale = (0.62, 0.58, 0.09); seat.location = (500.1, 2.74, 0.76)
    if m_ch: me.materials.append(m_ch)
    bv = seat.modifiers.new("Bevel", 'BEVEL'); bv.width = 0.03; bv.segments = 3
hs = D.objects["TJ_Cadeira_Haste"]; hs.location = (500.1, 2.74, 0.38); hs.scale = (1.0, 1.0, 1.45)
D.objects["TJ_Cadeira_Encosto"].location = (500.1, 3.04, 1.12)

if rig.animation_data and rig.animation_data.action:
    D.actions.remove(rig.animation_data.action)
for b in pb:
    b.location = (0, 0, 0); b.scale = (1, 1, 1); b.rotation_euler = (0, 0, 0); b.rotation_quaternion = (1, 0, 0, 0)
for n, k in (("PRP-UpperArm.L", "ik_left_arm"), ("PRP-UpperArm.R", "ik_right_arm"), ("PRP-Spine", "ik_spine")):
    pb[n][k] = 0.0
for n, k in (("PRP-Thigh.L", "ik_left_leg"), ("PRP-Thigh.R", "ik_right_leg")):
    pb[n][k] = 1.0
upd()

R3 = rig.matrix_world.to_3x3().normalized()
R3i = R3.inverted()
FWD = (R3 @ Vector((0, -1, 0))).normalized()   # frente nativa do rig (-Y local)
LEFT = (R3 @ Vector((1, 0, 0))).normalized()
UP = Vector((0, 0, 1))
_prev = {}

def W(side, out, fwd, up):
    return (LEFT * side * out + FWD * fwd + UP * up).normalized()

def aim(name, wdir, twist=0.0):
    """ABSOLUTO: zera a rotacao antes de apontar o eixo Y do osso para wdir (o twist nao se acumula entre chaves)."""
    b = pb[name]; b.rotation_euler = (0, 0, 0); upd()
    M = b.matrix.copy()
    tgt = (R3i @ wdir).normalized(); cur = M.to_3x3().col[1].normalized()
    m3 = cur.rotation_difference(tgt).to_matrix() @ M.to_3x3()
    if twist: m3 = Matrix.Rotation(math.radians(twist), 3, tgt) @ m3
    b.matrix = Matrix.Translation(M.translation) @ m3.to_4x4()
    upd()

def key(name, f):
    b = pb[name]; e = b.rotation_euler.copy()
    if name in _prev: e.make_compatible(_prev[name])
    b.rotation_euler = e; _prev[name] = e.copy()
    b.keyframe_insert("rotation_euler", frame=f)

# ---------------------------------------------------------------- pernas: sentada (coxas para a frente, canelas para baixo), pes em IK
upd()
for side, nm in ((1, "L"), (-1, "R")):
    hip = rig.matrix_world @ pb[f"FK-Thigh.{nm}"].head
    tgt = hip + FWD * 0.40 + LEFT * side * 0.02 - UP * 0.47
    b = pb[f"IK-Foot.{nm}"]; M = b.matrix.copy(); M.translation = rig.matrix_world.inverted() @ tgt; b.matrix = M; upd()
    b.keyframe_insert("location", frame=1); b.keyframe_insert("location", frame=103)
    b.keyframe_insert("rotation_euler", frame=1); b.keyframe_insert("rotation_euler", frame=103)

# ---------------------------------------------------------------- maos (poses prontas do Snow/Victoria: mesmos nomes de ossos de dedo)
def _fcs(a): return list(a.fcurves) if hasattr(a, "fcurves") else [fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
def pose_vals(name, flip=False):
    a = D.actions[name]; out = {}; f0 = a.frame_range[0]
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
def hand(f, side, shape):
    """shape: 'relax' | 'flat' | 'point' | 'spread'"""
    nm = {"relax": "Hand Relaxed", "flat": "Hand Flat", "point": "Hand Point", "spread": "Hand Spread"}[shape]
    k = (nm, side)
    if k not in _H: _H[k] = pose_vals(nm, flip=(side == "R"))
    touched = set()
    for (bone, prop, idx), v in _H[k].items():
        if bone in pb: getattr(pb[bone], prop)[idx] = v; touched.add((bone, prop))
    for bone, prop in touched: pb[bone].keyframe_insert(prop, frame=f)

# ---------------------------------------------------------------- poses de tronco/bracos
DESK  = dict(u=(0.20, 0.55, -0.80), f=(-0.10, 0.97, -0.10))     # antebracos apoiados na bancada
PAPER = dict(u=(0.30, 0.50, -0.80), f=(-0.30, 0.93, -0.12))     # mao esquerda sobre o papel (mais para o centro)
GEST  = dict(u=(0.50, 0.30, -0.82), f=(0.12, 0.85, 0.50))       # mao direita sobe, palma aberta (enfatiza)
GEST2 = dict(u=(0.42, 0.35, -0.84), f=(-0.05, 0.92, 0.22))      # gesto menor
POINT = dict(u=(0.55, 0.20, -0.80), f=(0.55, 0.78, 0.30))       # aponta para o lado (imagens do local)

def pose(f, L, Rr, spine=(0, 0), head=(0, 0, 0), hl="flat", hr="relax"):
    sp, sl = math.radians(spine[0]), math.radians(spine[1])
    aim("FK-Spine", (LEFT * math.sin(sl) + FWD * math.sin(sp) + UP * math.cos(sp)).normalized()); key("FK-Spine", f)
    hp, hs_ = math.radians(head[0]), math.radians(head[1])
    aim("FK-Head", (LEFT * math.sin(hs_) + FWD * math.sin(hp) + UP * math.cos(hp)).normalized(), head[2]); key("FK-Head", f)
    for side, nm, A in ((1, "L", L), (-1, "R", Rr)):
        aim(f"FK-UpperArm.{nm}", W(side, *A["u"])); key(f"FK-UpperArm.{nm}", f)
        aim(f"FK-Forearm.{nm}", W(side, *A["f"])); key(f"FK-Forearm.{nm}", f)
        aim(f"FK-Wrist.{nm}", W(side, *A["f"])); key(f"FK-Wrist.{nm}", f)
    hand(f, "L", hl); hand(f, "R", hr)

# apresentadora: postura ereta, olha a camera, olha o papel, enfatiza as manchetes com a mao direita
pose(1,   PAPER, DESK,  (2, 0),  (1, 0, 0),   "flat", "relax")
pose(8,   PAPER, DESK,  (3, 1),  (-2, 1, 0),  "flat", "relax")      # "Boa noite."
pose(14,  PAPER, DESK,  (4, 0),  (7, 0, 0),   "flat", "relax")      # olha o papel
pose(22,  PAPER, GEST2, (2, -1), (0, 0, 0),   "flat", "flat")       # volta para a camera
pose(30,  PAPER, GEST,  (1, -2), (-2, 2, 2),  "flat", "flat")       # "discussao por vaga de garagem" (enfatiza)
pose(38,  PAPER, GEST,  (2, -1), (2, -2, -2), "flat", "flat")
pose(46,  PAPER, DESK,  (3, 1),  (4, 0, 0),   "flat", "relax")      # baixa, consulta o papel
pose(54,  PAPER, GEST2, (1, 2),  (-1, 2, 2),  "flat", "flat")       # "a briga entre dois moradores"
pose(62,  PAPER, GEST,  (2, 0),  (1, -3, -3), "flat", "flat")
pose(70,  PAPER, DESK,  (3, 0),  (3, 0, 0),   "flat", "relax")
pose(78,  PAPER, POINT, (1, -2), (-1, -3, 0), "flat", "point")      # "imagens do local" (aponta para o telao)
pose(88,  PAPER, POINT, (1, -2), (-1, -3, 0), "flat", "point")
pose(96,  PAPER, DESK,  (2, 0),  (2, 0, 0),   "flat", "relax")
pose(103, PAPER, DESK,  (2, 0),  (1, 0, 0),   "flat", "relax")

# ---------------------------------------------------------------- fala: a mandibula abre e fecha no ritmo das silabas (pausas nas virgulas/pontos)
jaw = pb["Jaw"]
PAUSAS = (7, 21, 45, 53, 70, 77)       # pontuacao: boca fechada
def jaw_key(f, a): jaw.rotation_euler = (a, 0, 0); jaw.keyframe_insert("rotation_euler", frame=f)
jaw_key(1, 0.0); jaw_key(2, 0.0)
f = 3
import random
rnd = random.Random(7)
while f < 100:
    if any(abs(f - p) <= 1 for p in PAUSAS):
        jaw_key(f, 0.02); f += 3; continue
    amp = rnd.choice((0.10, 0.18, 0.24, 0.14, 0.20))
    jaw_key(f, amp); jaw_key(f + 1, amp * 0.35); f += 2
jaw_key(100, 0.02); jaw_key(103, 0.0)

# ---------------------------------------------------------------- interpolacao suave
act = rig.animation_data.action
n = 0
for fc in _fcs(act):
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'; n += 1
print("VIC_ANIM keys", n, "range", [round(x) for x in act.frame_range])
bpy.context.scene.frame_set(1); upd()
Wm = rig.matrix_world
print("VIC_CHECK pulso L/R z", round((Wm @ pb["DEF-Wrist.L"].head).z, 3), round((Wm @ pb["DEF-Wrist.R"].head).z, 3),
      "pe z", round((Wm @ pb["DEF-Foot.L"].head).z, 3), "quadril z", round((Wm @ pb["FK-Thigh.L"].head).z, 3),
      "ombro z", round((Wm @ pb["FK-UpperArm.L"].head).z, 3), "cabeca z", round((Wm @ pb["FK-Head"].head).z, 3), "(bancada = 1.03)")
for o in meshes: o.hide_viewport = _was[o.name]
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
