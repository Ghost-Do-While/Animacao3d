# CORRECAO (frame 168): o carro parecia "mole": a carroceria cabeceava ate 4 graus numa mola pouco amortecida (periodo ~11 frames,
# amortecimento 0,45) com chaves a cada 2 frames. Aqui a suspensao e recalculada em TODOS os carros com amplitude menor (max 1,3 graus),
# amortecimento critico (sem balancar de volta) e uma chave por frame. Rodar com -S Scene.
import bpy, math
from mathutils import Vector

def chans(o):
    a = o.animation_data.action
    return list(a.fcurves) if hasattr(a, "fcurves") else [fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
def fc_of(o, path, idx):
    return next(fc for fc in chans(o) if fc.data_path == path and fc.array_index == idx)

GAIN, MAXP, W_, Z_ = 0.30, math.radians(1.3), 0.45, 1.0
n_cars = 0
for body in [o for o in bpy.data.objects if o.name.startswith("VEH_") and o.name.endswith("_Corpo") and o.animation_data and o.animation_data.action]:
    root = bpy.data.objects[body.name[:-len("_Corpo")]]
    if not (root.animation_data and root.animation_data.action): continue
    try: fx = fc_of(body, "rotation_euler", 0)
    except StopIteration: continue
    frames = sorted(round(kp.co[0]) for kp in fx.keyframe_points)
    segs, cur = [], [frames[0]]
    for f in frames[1:]:
        if f - cur[-1] > 12: segs.append((cur[0], cur[-1])); cur = []
        cur.append(f)
    segs.append((cur[0], cur[-1]))
    rx, ry, rz = fc_of(root, "location", 0), fc_of(root, "location", 1), fc_of(root, "rotation_euler", 2)
    def loc(f): return Vector((rx.evaluate(f), ry.evaluate(f), 0))
    def spd(f):
        yaw = rz.evaluate(f); d = loc(f) - loc(f - 1)
        return d.dot(Vector((-math.sin(yaw), math.cos(yaw), 0)))
    try: fz = fc_of(body, "location", 2)
    except StopIteration: fz = None
    for f0, f1 in segs:
        for fc in [fx] + ([fz] if fz else []):
            for kp in reversed(list(fc.keyframe_points)):
                if f0 <= kp.co[0] <= f1: fc.keyframe_points.remove(kp)
        p = v = 0.0
        for f in range(max(2, f0 - 4), f1 + 14):
            a = spd(f) - spd(f - 1)
            tgt = max(-MAXP, min(MAXP, -a * GAIN))
            acc = -W_ * W_ * (p - tgt) - 2 * Z_ * W_ * v
            v += acc; p += v
            body.rotation_euler[0] = p; body.keyframe_insert("rotation_euler", index=0, frame=f)
            body.location[2] = -abs(p) * 0.25; body.keyframe_insert("location", index=2, frame=f)
    for fc in chans(body):
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
    n_cars += 1; print("CARRO", body.name, segs)
print("CARROS", n_cars)
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
