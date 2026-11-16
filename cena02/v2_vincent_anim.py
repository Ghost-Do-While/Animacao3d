# Reanimacao do Miguel -> Vincent (planos 01-10), FK por DIRECAO (independente dos eixos locais do rig BlenRig).
# Uso: blender -b cena02_v2.blend --python cena02/v2_vincent_anim.py
# Tempos e gestos vem de cena02/p4_anim.py (secao BRIGA). Sem bracos cruzados.
import bpy, math
from mathutils import Vector, Matrix, Euler

rig = bpy.data.objects["RIG-Vincent"]
pb = rig.pose.bones
CLAUDIO_HEAD = Vector((10.0, 5.90, 1.55))   # alvo do olhar (Claudio fica em y=5.84)

# --- durante a autoria as malhas ficam fora do depsgraph (rig de 2263 ossos + malhas pesadas)
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith("GEO-vincent")]
_was = {o.name: o.hide_viewport for o in meshes}
for o in meshes: o.hide_viewport = True
upd = bpy.context.view_layer.update

# --- remove animacao anterior do Vincent (se rodar de novo)
if rig.animation_data and rig.animation_data.action:
    bpy.data.actions.remove(rig.animation_data.action)
for b in pb:
    b.location = (0, 0, 0); b.scale = (1, 1, 1)
    b.rotation_euler = (0, 0, 0); b.rotation_quaternion = (1, 0, 0, 0)
upd()

R3 = rig.matrix_world.to_3x3()
R3i = R3.inverted()
_prev = {}

def W(side, out, fwd, up):
    """direcao no mundo; personagem olha para -Y; esquerda = +X (side=+1 L, -1 R)."""
    return Vector((side * out, -fwd, up)).normalized()

def aim(name, wdir, twist=0.0):
    """aponta o eixo Y do osso para wdir (mundo). twist = graus em torno do proprio eixo."""
    b = pb[name]
    if b.rotation_mode == 'QUATERNION': b.rotation_quaternion = (1, 0, 0, 0)
    else: b.rotation_euler = (0, 0, 0)
    upd()      # ABSOLUTO: o twist da cabeca e o rolamento das maos nao se acumulam entre chaves
    M = b.matrix.copy()
    tgt = (R3i @ wdir).normalized()
    cur = M.to_3x3().col[1].normalized()
    q = cur.rotation_difference(tgt)
    m3 = q.to_matrix() @ M.to_3x3()
    if twist:
        m3 = Matrix.Rotation(math.radians(twist), 3, tgt) @ m3
    b.matrix = Matrix.Translation(M.translation) @ m3.to_4x4()
    upd()

def key(name, f, loc=False):
    b = pb[name]
    path = "rotation_quaternion" if b.rotation_mode == 'QUATERNION' else "rotation_euler"
    if b.rotation_mode != 'QUATERNION':
        e = b.rotation_euler.copy()
        if name in _prev: e.make_compatible(_prev[name])
        b.rotation_euler = e; _prev[name] = e.copy()
    b.keyframe_insert(path, frame=f)
    if loc: b.keyframe_insert("location", frame=f)

# --------------------------------------------------------------- poses (out, fwd, up) por braco
REST = dict(u=(0.12, 0.0, -1.0), f=(0.10, 0.15, -1.0))
ANG  = dict(u=(0.45, 0.10, -0.88), f=(0.22, 0.75, -0.55))     # punhos fechados na frente, tenso
AT   = dict(u=(0.25, 0.90, -0.30), f=(0.15, 0.97, -0.20))      # aponta para o Claudio
FLR  = dict(u=(0.30, 0.60, -0.75), f=(0.22, 0.55, -0.80))      # aponta para o chao (vaga V3)
HEAD = dict(u=(0.80, -0.05, 0.35), f=(-0.55, 0.10, 0.85))      # maos na cabeca ("Pelo amor de Deus!")

def pose(f, L, Rr, spine=(0, 0), head=(0, 0, 0), gaze=True):
    """spine=(inclinacao p/ frente, lado) graus; head=(pitch, lado, giro) graus."""
    sp, sl = math.radians(spine[0]), math.radians(spine[1])
    aim("torso_fk_ctrl", Vector((math.sin(sl) * 1.0, -math.sin(sp), math.cos(sp))).normalized(), 0)
    key("torso_fk_ctrl", f)
    hp, hl = math.radians(head[0]), math.radians(head[1])
    aim("head_ik_ctrl", Vector((math.sin(hl), -math.sin(hp), math.cos(hp))).normalized(), head[2])
    key("head_ik_ctrl", f)
    for side, P, nm in ((1, L, "L"), (-1, Rr, "R")):
        u, fo = W(side, *P["u"]), W(side, *P["f"])
        aim(f"arm_fk_{nm}", u);      key(f"arm_fk_{nm}", f)
        aim(f"forearm_fk_{nm}", fo); key(f"forearm_fk_{nm}", f)
        aim(f"hand_fk_{nm}", fo);    key(f"hand_fk_{nm}", f)
    if gaze:
        b = pb["look_head"]
        M = b.matrix.copy(); M.translation = rig.matrix_world.inverted() @ CLAUDIO_HEAD
        b.matrix = M; upd(); key("look_head", f, loc=True)

def mix(a, b, t):
    return {k: tuple(x + (y - x) * t for x, y in zip(a[k], b[k])) for k in a}

# --------------------------------------------------------------- roteiro (frames de p4_anim.py, planos 04-07)
BASE_SP = (8, 0); BASE_HD = (-6, 0, 0)
def K(f, L, Rr, spine=BASE_SP, head=BASE_HD): pose(f, L, Rr, spine, head)

K(1,   ANG, ANG); K(253, ANG, ANG)
# Plano 05: discute com o Claudio (arma o braco direito para ele)
for f, Rp, sp in ((259, AT, (10, 0)), (266, ANG, BASE_SP), (272, AT, (10, 0)), (279, ANG, BASE_SP), (286, ANG, BASE_SP)):
    K(f, ANG, Rp, sp)
# Plano 06: aponta o chao, aponta Claudio, maos na cabeca
K(289, ANG, ANG)
K(293, ANG, mix(ANG, REST, 0.5), (4, 0), (0, 0, 0))
FL_SP = (18, 0); FL_HD = (16, 0, 0)
K(297, ANG, FLR, FL_SP, FL_HD); K(300, ANG, FLR, FL_SP, FL_HD)
for i, f in enumerate(range(303, 318, 4)):
    K(f, ANG, mix(FLR, AT, 0.0 if i % 2 == 0 else 0.25), (18 + 3 * (i % 2), 0), FL_HD)   # estocadas para o chao
K(319, ANG, FLR, FL_SP, FL_HD)
AT_SP = (10, 6); AT_HD = (-8, -6, 0)
K(321, ANG, AT, AT_SP, AT_HD); K(324, ANG, AT, AT_SP, AT_HD); K(328, ANG, AT, AT_SP, AT_HD)
for i, f in enumerate(range(332, 347, 4)):
    K(f, ANG, mix(AT, ANG, 0.0 if i % 2 == 0 else 0.2), (12 if i % 2 == 0 else 7, 6), AT_HD)
K(349, ANG, AT, AT_SP, AT_HD)
K(352, ANG, ANG, (16, 0), (0, 0, 0))
HD_SP = (-6, 0)
K(357, HEAD, HEAD, HD_SP, (-16, 0, 0)); K(360, HEAD, HEAD, HD_SP, (-16, 0, 0))
for i, f in enumerate(range(364, 396, 4)):
    K(f, HEAD, HEAD, (-6 - (i % 2) * 3, 5 if i % 2 else -5), (-16, 0, 12 if i % 2 == 0 else -12))
# Plano 07: Miguel reage a fala do Claudio (apontando / tenso), sem cruzar os bracos
for i, f in enumerate(range(397, 493, 7)):
    K(f, ANG, AT if i % 2 == 0 else ANG, (8 + (i % 3) * 3, 0), (-6, 0, 8 * (-1) ** i))
# depois da briga: baixa os bracos com transicao suave ate pose relaxada
K(505, ANG, ANG); K(530, REST, REST, (2, 0), (0, 0, 0)); K(720, REST, REST, (2, 0), (0, 0, 0))

# interpolacao suave
act = rig.animation_data.action
n = 0
for fc in act.fcurves if hasattr(act, "fcurves") else [fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]:
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'; n += 1
print("VINCENT_ANIM keys", n, "range", [round(x) for x in act.frame_range])

for o in meshes: o.hide_viewport = _was[o.name]
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
