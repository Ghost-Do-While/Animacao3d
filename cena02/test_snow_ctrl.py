import bpy, sys, json, traceback, math
from mathutils import Vector, Euler, Matrix
out = {}
try:
    D = bpy.data
    rig = D.objects['RIG-Snow']
    for o in D.objects:
        if o.type == 'MESH': o.hide_viewport = True
    pbs = rig.pose.bones
    P = pbs['Properties']
    out['props_before'] = {k: P[k] for k in P.keys() if k.startswith(('ik_left_up', 'ik_right_up', 'ik_spine', 'ik_left_thigh', 'ik_left_finger_index1', 'fk_hinge_head', 'fk_hinge_neck'))}
    for k in ('ik_left_upperarm', 'ik_right_upperarm'): P[k] = 0.0
    bpy.context.view_layer.update()
    def pos(n, tail=False):
        pb = pbs[n]; m = pb.matrix
        return [round(x, 3) for x in (m @ Vector((0, pb.length, 0)) if tail else m.translation)]
    def rot(n, e):
        pb = pbs[n]; pb.rotation_mode = 'XYZ'
        R = pb.bone.matrix_local.to_3x3()
        pb.rotation_euler = (R.inverted() @ Euler(tuple(math.radians(a) for a in e), 'XYZ').to_matrix() @ R).to_euler('XYZ')
        bpy.context.view_layer.update()
    def reset(n):
        pbs[n].rotation_euler = (0, 0, 0); pbs[n].rotation_quaternion = (1, 0, 0, 0); bpy.context.view_layer.update()
    tests = {
        'FK-UpperArm.L Y+60 -> DEF-UpperArm_2.L tail / Wrist': ('FK-UpperArm.L', (0, 60, 0), ['DEF-UpperArm_2.L', 'DEF-Forearm_2.L'] ),
        'FK-OS-Spine X+25 -> DEF-Head': ('FK-OS-Spine', (25, 0, 0), ['DEF-Head', 'DEF-Chest']),
        'FK-Spine X+25 -> DEF-Head': ('FK-Spine', (25, 0, 0), ['DEF-Head']),
        'FK-OS-Chest X+25 -> DEF-Head': ('FK-OS-Chest', (25, 0, 0), ['DEF-Head']),
        'FK-Chest X+25 -> DEF-Head': ('FK-Chest', (25, 0, 0), ['DEF-Head']),
        'FK-Head X+25 -> DEF-Head tail': ('FK-Head', (25, 0, 0), ['DEF-Head']),
        'Head X+25 -> DEF-Head tail': ('Head', (25, 0, 0), ['DEF-Head']),
        'FK-Neck X+25': ('FK-Neck', (25, 0, 0), ['DEF-Head']),
        'Neck X+25': ('Neck', (25, 0, 0), ['DEF-Head']),
        'TORSO-Spine X+25': ('TORSO-Spine', (25, 0, 0), ['DEF-Head', 'DEF-Thigh_1.L']),
        'HIP-Spine X+25': ('HIP-Spine', (25, 0, 0), ['DEF-Head', 'DEF-Thigh_1.L']),
        'FK-Finger_Index1.L Y+60': ('FK-Finger_Index1.L', (0, 60, 0), ['DEF-Finger_Index3.L']),
    }
    base = {}
    names = ['DEF-UpperArm_2.L', 'DEF-Forearm_2.L', 'DEF-Head', 'DEF-Chest', 'DEF-Thigh_1.L', 'DEF-Finger_Index3.L']
    for n in names:
        if n in pbs: base[n] = Vector(pos(n, True))
        else: out.setdefault('missing', []).append(n)
    res = {}
    for k, (b, e, watch) in tests.items():
        if b not in pbs: res[k] = 'sem osso'; continue
        rot(b, e)
        res[k] = {w: [round(x, 3) for x in (Vector(pos(w, True)) - base[w])] for w in watch if w in base}
        reset(b)
    out['res'] = res
    out['def_names'] = [n for n in pbs.keys() if n.startswith('DEF-') and any(t in n for t in ('Forearm', 'Wrist', 'Hand', 'Chest', 'Spine', 'RibCage', 'Neck', 'Shoulder'))][:40]
    out['arm_dir_tail'] = {n: pos(n, True) for n in ('FK-UpperArm.L', 'FK-Forearm.L', 'FK-Wrist.L')}
    out['front'] = {'toes_tail_y': pos('FK-Toes.L', True), 'head_y': pos('DEF-Head', True)}
except Exception:
    out['err'] = traceback.format_exc()[-1800:]
json.dump(out, open(sys.argv[-1], 'w'), indent=1, default=str)
