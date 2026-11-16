# Reanimacao do Claudio -> Rex (CloudRig). FK por DIRECAO, igual ao Vincent. Sem bracos cruzados:
# no trecho em que o Claudio cruzava os bracos (frames 292-392) o Rex so baixa os bracos, com ease in/out.
# Uso: blender -b cena02_v2.blend --python cena02/v2_rex_anim.py
import bpy, math
from mathutils import Vector, Matrix

rig = bpy.data.objects["RIG-rex"]
pb = rig.pose.bones
MIGUEL_HEAD = Vector((10.0, 7.0, 1.6))

meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith("GEO-rex")]
_was = {o.name: o.hide_viewport for o in meshes}
for o in meshes: o.hide_viewport = True
upd = bpy.context.view_layer.update

if rig.animation_data and rig.animation_data.action:
    bpy.data.actions.remove(rig.animation_data.action)
for b in pb:
    b.location = (0, 0, 0); b.scale = (1, 1, 1)
    b.rotation_euler = (0, 0, 0); b.rotation_quaternion = (1, 0, 0, 0)

# bracos e coluna em FK (o rig vem com IK ligado)
for n, k in (("PRP-UpperArm.L", "ik_left_arm"), ("PRP-UpperArm.R", "ik_right_arm"), ("PRP-Spine", "ik_spine")):
    pb[n][k] = 0.0
upd()

R3i = rig.matrix_world.to_3x3().inverted()
FWD = (rig.matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()   # frente do personagem (mundo)
LEFT = (rig.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()   # esquerda do personagem (mundo)
_prev = {}

def W(side, out, fwd, up):
    return (LEFT * side * out + FWD * fwd + Vector((0, 0, up))).normalized()

def aim(name, wdir, twist=0.0):
    b = pb[name]
    b.rotation_euler = (0, 0, 0); upd()      # ABSOLUTO: sem isso o twist da cabeca se acumulava de chave em chave (cabeca girando 399-492)
    M = b.matrix.copy()
    tgt = (R3i @ wdir).normalized()
    cur = M.to_3x3().col[1].normalized()
    m3 = cur.rotation_difference(tgt).to_matrix() @ M.to_3x3()
    if twist: m3 = Matrix.Rotation(math.radians(twist), 3, tgt) @ m3
    b.matrix = Matrix.Translation(M.translation) @ m3.to_4x4()
    upd()

def key(name, f):
    b = pb[name]
    e = b.rotation_euler.copy()
    if name in _prev: e.make_compatible(_prev[name])
    b.rotation_euler = e; _prev[name] = e.copy()
    b.keyframe_insert("rotation_euler", frame=f)

DEF = dict(u=(0.22, 0.30, -0.92), f=(0.10, 0.80, -0.55))     # maos na frente, cintura
PREP = dict(u=(0.28, 0.15, -0.95), f=(0.05, 0.60, 0.70))     # antebracos erguidos (arma o empurrao)
PUSH = dict(u=(0.15, 0.95, -0.25), f=(0.05, 0.98, -0.10))     # empurra o ar
SHRUG = dict(u=(0.45, 0.15, -0.85), f=(0.70, 0.55, 0.10))     # da de ombros, maos abertas
REL = dict(u=(0.15, 0.05, -0.99), f=(0.08, 0.25, -0.95))      # bracos baixos, relaxados

def pose(f, A, spine=(0, 0), head=(0, 0, 0)):
    sp, sl = math.radians(spine[0]), math.radians(spine[1])
    d = (LEFT * math.sin(sl) + FWD * math.sin(sp) + Vector((0, 0, math.cos(sp)))).normalized()
    aim("FK-Spine", d); key("FK-Spine", f)
    hp, hl = math.radians(head[0]), math.radians(head[1])
    aim("FK-Head", (LEFT * math.sin(hl) + FWD * math.sin(hp) + Vector((0, 0, math.cos(hp)))).normalized(), head[2])
    key("FK-Head", f)
    for side, nm in ((1, "L"), (-1, "R")):
        aim(f"FK-UpperArm.{nm}", W(side, *A["u"])); key(f"FK-UpperArm.{nm}", f)
        aim(f"FK-Forearm.{nm}", W(side, *A["f"])); key(f"FK-Forearm.{nm}", f)
        aim(f"FK-Wrist.{nm}", W(side, *A["f"])); key(f"FK-Wrist.{nm}", f)

def mix(a, b, t): return {k: tuple(x + (y - x) * t for x, y in zip(a[k], b[k])) for k in a}
BS = (-3, 0)

def K(f, A, sp=BS, hd=(0, 0, 0)): pose(f, A, sp, hd)

# Plano 04-05
K(1, DEF); K(253, DEF); K(259, DEF)
for f, A, sp in ((266, PUSH, (3, 0)), (272, PREP, (-8, 0)), (279, PUSH, (4, 0)), (286, DEF, BS)):
    K(f, A, sp, (0, 0, 6))
# Plano 06: em vez de cruzar os bracos, baixa os bracos com transicao suave (ease) ate pose relaxada
K(289, DEF)
K(300, mix(DEF, REL, 0.6), BS, (0, 0, 4))
K(312, REL, (-2, 0), (-4, 0, 8)); K(392, REL, (-2, 0), (-4, 0, 10))
# Plano 07: empurra o ar, da de ombros, deboche
K(397, mix(REL, DEF, 0.8)); K(401, PREP, (-10, 0))
for a, b in ((405, 408), (417, 420), (459, 463)):
    K(a, PUSH, (5, 0), (0, 0, 6)); K(b, PUSH, (5, 0), (0, 0, 6))
K(413, PREP, (-10, 0)); K(426, DEF, BS)
for a, b in ((431, 437), (475, 483)):
    K(a, SHRUG, (-8, 0), (-5, 0, 16)); K(b, SHRUG, (-8, 0), (-5, 0, 16))
K(444, SHRUG, (-8, 0), (-4, 0, -12)); K(450, DEF, BS); K(455, PREP, (-10, 0)); K(470, DEF, BS)
K(492, SHRUG, (-8, 0), (-6, 0, 18))
K(520, DEF); K(545, REL, (0, 0)); K(720, REL, (0, 0))

act = rig.animation_data.action
chans = act.fcurves if hasattr(act, "fcurves") else [fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
n = 0
for fc in chans:
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'; n += 1
print("REX_ANIM keys", n, "range", [round(x) for x in act.frame_range])
for o in meshes: o.hide_viewport = _was[o.name]
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
