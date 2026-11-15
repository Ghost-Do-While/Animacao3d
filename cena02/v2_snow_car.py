# Snow (Marcos) NO CARRO, frames 1-243: sentado, maos no volante por IK (acompanham o volante com o carro andando),
# pernas em FK nos pedais, cabeca/tronco seguem o roteiro (olha a fila, revira os olhos, suspira, cabeca no encosto).
# Uso: blender -b cena02_v2.blend --python cena02/v2_snow_car.py
import bpy, math
from mathutils import Vector, Matrix

sc = bpy.context.scene
rig = bpy.data.objects["RIG-Snow"]
pb = rig.pose.bones
wheel = bpy.data.objects["VEH_CarroMarcos_Volante"]
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith("GEO-snow")]
_was = {o.name: o.hide_viewport for o in meshes}
for o in meshes: o.hide_viewport = True
upd = bpy.context.view_layer.update

if rig.animation_data and rig.animation_data.action:
    bpy.data.actions.remove(rig.animation_data.action)
for b in pb:
    b.location = (0, 0, 0); b.scale = (1, 1, 1); b.rotation_euler = (0, 0, 0); b.rotation_quaternion = (1, 0, 0, 0)
# bracos em IK (maos no volante); pernas e coluna em FK
P = pb["Properties"]
P["ik_left_upperarm"] = 1.0; P["ik_right_upperarm"] = 1.0
P["ik_left_thigh"] = 0.0; P["ik_right_thigh"] = 0.0; P["ik_spine"] = 0.0
off = bpy.data.objects["ROOT_Snow_Off"]
off.location = (0, -0.12, 0)          # um pouco para a frente (ombros mais perto do volante)

def need(*names):
    miss = [n for n in names if n not in pb]
    assert not miss, f"ossos ausentes: {miss}"
need("FK-Spine", "FK-Chest", "FK-Neck", "FK-Head", "FK-Thigh.L", "FK-Knee.L", "FK-Foot.L", "FK-Thigh.R", "FK-Knee.R", "FK-Foot.R",
    "IK-Wrist.L", "IK-Wrist.R", "DEF-Wrist.L", "DEF-Wrist.R")

_prev = {}
def frame(f): sc.frame_set(f); upd()
def axes():
    R3 = rig.matrix_world.to_3x3()
    F = (R3 @ Vector((0, -1, 0))).normalized(); L = (R3 @ Vector((1, 0, 0))).normalized()
    return R3.inverted(), F, L
def aim(name, wdir, twist=0.0):
    R3i, _, _ = axes()
    b = pb[name]; M = b.matrix.copy(); tgt = (R3i @ wdir).normalized(); cur = M.to_3x3().col[1].normalized()
    m3 = cur.rotation_difference(tgt).to_matrix() @ M.to_3x3()
    if twist: m3 = Matrix.Rotation(math.radians(twist), 3, tgt) @ m3
    b.matrix = Matrix.Translation(M.translation) @ m3.to_4x4(); upd()
def place(name, wpos, wdir=None):
    b = pb[name]; M = b.matrix.copy(); M.translation = rig.matrix_world.inverted() @ wpos; b.matrix = M; upd()
    if wdir is not None: aim(name, wdir)
def key(name, f, loc=False):
    b = pb[name]
    if b.rotation_mode == 'QUATERNION': b.keyframe_insert("rotation_quaternion", frame=f)
    else:
        e = b.rotation_euler.copy()
        if name in _prev: e.make_compatible(_prev[name])
        b.rotation_euler = e; _prev[name] = e.copy(); b.keyframe_insert("rotation_euler", frame=f)
    if loc: b.keyframe_insert("location", frame=f)

def sit(f, lean=-3, hpitch=0, htwist=0):
    frame(f)
    _, F, L = axes(); U = Vector((0, 0, 1))
    for side, nm in ((1, "L"), (-1, "R")):
        aim(f"FK-Thigh.{nm}", (L * side * 0.06 + F * 0.97 - U * 0.18).normalized()); key(f"FK-Thigh.{nm}", f)
        aim(f"FK-Knee.{nm}", (L * side * 0.0 - F * 0.10 - U * 1.0).normalized()); key(f"FK-Knee.{nm}", f)
        aim(f"FK-Foot.{nm}", (F * 0.95 - U * 0.25).normalized()); key(f"FK-Foot.{nm}", f)
    a = math.radians(lean)
    aim("FK-Spine", (F * math.sin(a) + U * math.cos(a)).normalized()); key("FK-Spine", f)
    aim("FK-Chest", (F * math.sin(a * 0.5) + U * math.cos(a * 0.5)).normalized()); key("FK-Chest", f)
    h = math.radians(hpitch)
    aim("FK-Head", (F * math.sin(h) + U * math.cos(h)).normalized(), htwist); key("FK-Head", f)
    # maos no volante (IK): aro em Volante +- 0.21 lateral
    C = wheel.matrix_world.translation.copy()
    for side, nm in ((1, "L"), (-1, "R")):
        g = C + L * side * 0.21 + U * 0.01
        place(f"IK-Wrist.{nm}", g, (F * 0.8 - L * side * 0.35 - U * 0.25).normalized()); key(f"IK-Wrist.{nm}", f, loc=True)

# roteiro (frames de p4_anim.py, planos 01-04): (frame, inclinacao do tronco, cabeca pitch, cabeca giro)
SCRIPT = {1: (-3, 0, 0), 60: (-3, 0, 0), 73: (-3, 0, 0), 88: (-3, 0, 0),
          96: (-3, 0, 12), 104: (-3, 3, 12), 110: (-3, 6, 4), 118: (-6, 4, -4),
          125: (-12, -2, 0), 134: (-12, 2, 0), 143: (-14, -10, 6), 150: (-3, 0, 0), 176: (-3, 0, 0),
          200: (-3, 0, 0), 222: (-3, 0, -6), 240: (-3, 0, 0)}
frames = sorted(set(SCRIPT) | set(range(1, 244, 12)) | {243})
prev = (-3, 0, 0)
for f in frames:
    v = SCRIPT.get(f)
    if v is None:   # interpola o ultimo valor roteirizado
        ks = [k for k in SCRIPT if k <= f]; v = SCRIPT[max(ks)]
    sit(f, *v)

# erro de alcance das maos (m) em alguns frames
for f in (1, 80, 200):
    frame(f)
    C = wheel.matrix_world.translation; _, F, L = axes()
    for side, nm in ((1, "L"), (-1, "R")):
        w = rig.matrix_world @ pb[f"DEF-Wrist.{nm}"].head
        print("SNOW_REACH", f, nm, round((w - (C + L * side * 0.21)).length, 3))

act = rig.animation_data.action
chans = act.fcurves if hasattr(act, "fcurves") else [fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
n = 0
for fc in chans:
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'; n += 1
print("SNOW_CAR keys", n)
for o in meshes: o.hide_viewport = _was[o.name]
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
