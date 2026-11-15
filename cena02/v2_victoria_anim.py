# Animacao da Victoria (ancora do telejornal, frames 1-103), FK por DIRECAO como Vincent/Rex.
# Uso: blender -b cena02_v2.blend -S SCN_Telejornal --python cena02/v2_victoria_anim.py
# (a cena ativa precisa ser SCN_Telejornal, senao o rig nao entra no depsgraph)
import bpy, math
from mathutils import Vector, Matrix

assert bpy.context.scene.name == "SCN_Telejornal", "rode com -S SCN_Telejornal"
rig = bpy.data.objects["RIG-Victoria"]
pb = rig.pose.bones
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith("GEO-victoria")]
_was = {o.name: o.hide_viewport for o in meshes}
for o in meshes: o.hide_viewport = True
upd = bpy.context.view_layer.update

if rig.animation_data and rig.animation_data.action:
    bpy.data.actions.remove(rig.animation_data.action)
for b in pb:
    b.location = (0, 0, 0); b.scale = (1, 1, 1); b.rotation_euler = (0, 0, 0); b.rotation_quaternion = (1, 0, 0, 0)
for n, k in (("PRP-UpperArm.L", "ik_left_arm"), ("PRP-UpperArm.R", "ik_right_arm"), ("PRP-Spine", "ik_spine")):
    pb[n][k] = 0.0
upd()

R3 = rig.matrix_world.to_3x3()
R3i = R3.inverted()
FWD = (R3 @ Vector((0, -1, 0))).normalized()   # frente nativa do rig (-Y local)
LEFT = (R3 @ Vector((1, 0, 0))).normalized()
_prev = {}

def W(side, out, fwd, up):
    return (LEFT * side * out + FWD * fwd + Vector((0, 0, up))).normalized()

def aim(name, wdir, twist=0.0):
    b = pb[name]; M = b.matrix.copy()
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

DESK = dict(u=(0.20, 0.15, -0.96), f=(-0.10, 0.88, -0.45))     # antebracos apoiados a frente, maos separadas
GEST = dict(u=(0.40, 0.25, -0.88), f=(0.15, 0.80, 0.25))       # mao direita sobe, palma aberta
GEST2 = dict(u=(0.35, 0.35, -0.85), f=(-0.05, 0.90, 0.10))

def pose(f, L, Rr, spine=(0, 0), head=(0, 0, 0)):
    sp, sl = math.radians(spine[0]), math.radians(spine[1])
    aim("FK-Spine", (LEFT * math.sin(sl) + FWD * math.sin(sp) + Vector((0, 0, math.cos(sp)))).normalized()); key("FK-Spine", f)
    hp, hl = math.radians(head[0]), math.radians(head[1])
    aim("FK-Head", (LEFT * math.sin(hl) + FWD * math.sin(hp) + Vector((0, 0, math.cos(hp)))).normalized(), head[2]); key("FK-Head", f)
    for side, nm, A in ((1, "L", L), (-1, "R", Rr)):
        aim(f"FK-UpperArm.{nm}", W(side, *A["u"])); key(f"FK-UpperArm.{nm}", f)
        aim(f"FK-Forearm.{nm}", W(side, *A["f"])); key(f"FK-Forearm.{nm}", f)
        aim(f"FK-Wrist.{nm}", W(side, *A["f"])); key(f"FK-Wrist.{nm}", f)

# postura de apresentadora: tronco ereto, olhar na camera, gesto sutil
pose(1, DESK, DESK, (1, 0), (0, 0, 0))
pose(14, DESK, DESK, (2, 0), (-4, 0, 0))            # olha o texto
pose(24, DESK, DESK, (1, 0), (0, 0, 0))             # volta para a camera
pose(36, DESK, GEST, (2, 0), (1, 0, 0))             # gesto na manchete
pose(52, DESK, GEST2, (2, 0), (0, 2, 0))
pose(66, DESK, DESK, (1, 0), (-3, 0, 0))
pose(84, DESK, GEST2, (2, 0), (1, 0, 0))
pose(103, DESK, DESK, (1, 0), (0, 0, 0))

act = rig.animation_data.action
chans = act.fcurves if hasattr(act, "fcurves") else [fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
n = 0
for fc in chans:
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'; n += 1
print("VIC_ANIM keys", n, "range", [round(x) for x in act.frame_range])
for o in meshes: o.hide_viewport = _was[o.name]
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
