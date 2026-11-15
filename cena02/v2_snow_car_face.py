# Refino do Snow no carro (frames 1-243): mao em torno do aro, tamborilar (90-106), rosto (cansaco, suspiro, piscadas) e olhar.
# Usa as poses prontas do Snow (Hand *, Mouth *, Eyemask *) misturadas por peso. Rodar DEPOIS de v2_snow_car.py, com -S Scene.
import bpy, re, math
from mathutils import Vector

rig = bpy.data.objects["RIG-Snow"]
pb = rig.pose.bones
sc = bpy.context.scene
assert sc.name == "Scene" and rig.animation_data and rig.animation_data.action, "rode v2_snow_car.py antes, com -S Scene"
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith("GEO-snow")]
_was = {o.name: o.hide_viewport for o in meshes}
for o in meshes: o.hide_viewport = True

def fcs(a): return list(a.fcurves) if hasattr(a, "fcurves") else [fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
def pose_vals(name, flip=False):
    """{(bone, prop, idx): valor} da pose pronta (um unico quadro)."""
    a = bpy.data.actions[name]; out = {}
    f0 = a.frame_range[0]
    for fc in fcs(a):
        m = re.match(r'pose\.bones\["([^"]+)"\]\.(\w+)', fc.data_path)
        if not m: continue
        bone, prop = m.group(1), m.group(2)
        if prop not in ('location', 'rotation_euler', 'scale'): continue
        v = fc.evaluate(f0)
        if flip:
            bone = bone.replace(".L", ".R") if bone.endswith(".L") else (bone.replace(".R", ".L") if bone.endswith(".R") else bone)
            if prop == "location" and fc.array_index == 0: v = -v
            if prop == "rotation_euler" and fc.array_index in (1, 2): v = -v
        out[(bone, prop, fc.array_index)] = v
    return out
REST = lambda prop: 1.0 if prop == "scale" else 0.0
def blend(base, poses):
    """base + soma(peso * (pose - base)); poses = [(vals, peso)]"""
    res = dict(base)
    for vals, w in poses:
        for k, v in vals.items():
            b = base.get(k, REST(k[1]))
            res[k] = res.get(k, b) + w * (v - b)
    return res
def write_key(vals, f, only=None):
    touched = set()
    for (bone, prop, idx), v in vals.items():
        if bone not in pb or (only and not only(bone)): continue
        getattr(pb[bone], prop)[idx] = v; touched.add((bone, prop))
    for bone, prop in touched: pb[bone].keyframe_insert(prop, frame=f)

# ---------------------------------------------------------------- maos: relaxada -> punho (aro)
FING = ("Thumb", "Index", "Middle", "Ring", "Pinky")
relL, fistL = pose_vals("Hand Relaxed"), pose_vals("Hand Fist")
relR, fistR = pose_vals("Hand Relaxed", True), pose_vals("Hand Fist", True)
def hand(side, w):
    """w: peso do punho por dedo (dict nome->0..1) ou numero unico."""
    rel, fist = (relL, fistL) if side == "L" else (relR, fistR)
    wd = {n: (w if not isinstance(w, dict) else w.get(n, 0.0)) for n in FING}
    vals = {}
    for k, v in rel.items():
        fname = next((n for n in FING if f"Finger_{n}" in k[0]), None)
        wf = wd[fname] if fname else (sum(wd.values()) / len(wd))
        fv = fist.get(k, v)
        vals[k] = v + wf * (fv - v)
    return vals
GRIP = 0.65
for f in (1, 243):
    write_key(hand("L", GRIP), f); write_key(hand("R", GRIP), f)
# tamborila (4 frames por dedo) com a mao direita, carro parado (frames 90-106): indicador, medio, anelar, minimo
write_key(hand("R", GRIP), 89)
for i, n in enumerate(("Index", "Middle", "Ring", "Pinky")):
    fi = 90 + i * 4
    base = {x: GRIP for x in FING}
    up = dict(base); up[n] = 0.05
    write_key(hand("R", base), fi, only=lambda b: f"Finger_{n}" in b)
    write_key(hand("R", up), fi + 2, only=lambda b: f"Finger_{n}" in b)
    write_key(hand("R", base), fi + 4, only=lambda b: f"Finger_{n}" in b)
write_key(hand("R", GRIP), 107)

# ---------------------------------------------------------------- rosto
eyeD = pose_vals("Eyemask Default"); mouD = pose_vals("Mouth Default")
EYE = {n: pose_vals(f"Eyemask {n}") for n in ("Sad", "Closed", "Relaxed", "Angry", "Scared")}
MOU = {n: pose_vals(f"Mouth {n}") for n in ("Compressed", "Openfrown", "Teethfrown", "Narrow")}
def face(f, eye, mouth):
    write_key(blend(eyeD, [(EYE[k], w) for k, w in eye.items()]), f)
    write_key(blend(mouD, [(MOU[k], w) for k, w in mouth.items()]), f)
def blink(f, dur=8, base=None, mouth=None):
    base = base or {}
    face(f, base, mouth or {}); face(f + 3, {**base, "Closed": 1.0}, mouth or {}); face(f + dur, base, mouth or {})
E0 = {"Sad": 0.35}; M0 = {"Compressed": 0.35}
face(1, E0, M0)
blink(20, 8, E0, M0)
face(88, E0, M0); blink(98, 10, E0, M0)
face(104, {"Sad": 0.25}, M0)
face(116, {"Sad": 0.9}, {"Compressed": 0.6})
face(122, {"Sad": 0.9}, {"Compressed": 0.6})
face(125, {"Sad": 0.9}, {"Openfrown": 1.0}); face(128, {"Sad": 0.9}, {"Openfrown": 1.0})   # suspira
face(136, {"Sad": 0.6}, {"Compressed": 0.5})
face(142, {"Sad": 0.6, "Closed": 0.6}, {"Compressed": 0.5})                                # pesado, cabeca no encosto
face(150, E0, M0); face(243, E0, M0)

# ---------------------------------------------------------------- olhar (alvo dos olhos), se o rig tiver o controle
cand = [n for n in ("TGT-Eyes", "Eyes", "EYES", "Eye_Target", "TGT-Eye") if n in pb]
print("SNOWFACE eye target:", cand, [n for n in pb.keys() if n.startswith(("TGT", "Eyes", "LOOK"))][:10])
if cand:
    eb = cand[0]
    def look(f, x, y, z):
        sc.frame_set(f); bpy.context.view_layer.update()
        R3 = rig.matrix_world.to_3x3(); F = (R3 @ Vector((0, -1, 0))).normalized(); Lf = (R3 @ Vector((1, 0, 0))).normalized(); U = Vector((0, 0, 1))
        eye = rig.matrix_world @ (pb["FK-Head"].head + Vector((0, 0, 0.12)))
        tgt = eye + F * (1.0 + y) + (-Lf) * x + U * z          # x>0 = direita do personagem (lado da fila)
        b = pb[eb]; M = b.matrix.copy(); M.translation = rig.matrix_world.inverted() @ tgt; b.matrix = M
        bpy.context.view_layer.update(); b.keyframe_insert("location", frame=f)
    for f, v in ((1, (0, 0.2, 0)), (88, (0, 0.2, 0)), (96, (0.7, 0.2, 0.05)), (104, (0.7, 0.2, 0.05)), (108, (0.0, 0.3, 0.55)),
                 (112, (-0.6, 0.3, 0.45)), (116, (-0.6, 0.3, 0.45)), (122, (0, 0.2, 0)), (134, (0, 0.2, 0)), (143, (0, 0.3, -0.25)), (150, (0, 0.2, 0)), (243, (0, 0.2, 0))):
        look(f, *v)

for fc in fcs(rig.animation_data.action):
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
print("SNOWFACE keys", sum(len(fc.keyframe_points) for fc in fcs(rig.animation_data.action)))
for o in meshes: o.hide_viewport = _was[o.name]
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
