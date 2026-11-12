import bpy, sys, json, traceback
from mathutils import Vector
from bpy_extras import anim_utils
out = {}
try:
    D = bpy.data
    rig = D.objects['RIG-Snow']; ab = rig.data
    colmap = {bc.name: [b.name for b in bc.bones] for bc in ab.collections_all}
    for nm in ('Face Main', 'Face Secondary', 'Face', 'Teeth', 'Tongue', 'Hair'):
        out['col_' + nm] = colmap.get(nm, [])[:70]
    names = [b.name for b in ab.bones]
    out['eye_like'] = [n for n in names if 'ye' in n and not n.startswith(('DEF-', 'MCH-'))][:60]
    out['jaw_like'] = [n for n in names if 'Jaw' in n and not n.startswith(('DEF-', 'MCH-'))][:30]
    out['brow_like'] = [n for n in names if 'brow' in n.lower() and not n.startswith(('DEF-', 'MCH-'))][:30]
    out['hips_leg'] = [n for n in names if n in ('HIP-Spine', 'TORSO-Spine', 'IK-W-Foot.L', 'IK-Foot.L', 'FK-W-Foot.L', 'IK-Foot_Roll.L')] + [n for n in names if n.startswith(('IK-W', 'IK-Foot', 'POLE-Thigh', 'IK-Ankle'))][:10]
    # conteúdo das ações de pose (bone -> canais) para algumas
    def action_pose(a):
        res = {}
        slots = list(a.slots) if hasattr(a, 'slots') else []
        for fc in a.fcurves if hasattr(a, 'fcurves') else []:
            pass
        try:
            for layer in a.layers:
                for strip in layer.strips:
                    for cb in strip.channelbags:
                        for fc in cb.fcurves:
                            if fc.data_path.startswith('pose.bones['):
                                bn = fc.data_path.split('"')[1]; ch = fc.data_path.split('.')[-1]
                                v = fc.evaluate(fc.keyframe_points[0].co.x if len(fc.keyframe_points) else 0)
                                res.setdefault(bn, {})[f'{ch}[{fc.array_index}]'] = round(v, 4)
        except Exception as e:
            res['_err'] = str(e)
        return res
    sel = ['Mouth Default', 'Mouth Oo', 'Mouth Uu', 'Mouth Ff', 'Mouth Opensmile', 'Mouth Teethsmile', 'Mouth Compressed', 'Eyemask Closed', 'Eyemask Angry', 'Eyemask Cocky', 'Eyemask Default', 'Hand Point', 'Hand Fist']
    out['act'] = {n: action_pose(D.actions[n]) for n in sel}
    out['act_sizes'] = {n: len(out['act'][n]) for n in sel}
    out['rest_dir'] = {}
    for n in ('FK-Shoulder.L', 'FK-UpperArm.L', 'FK-Forearm.L', 'FK-Wrist.L', 'FK-Spine', 'FK-RibCage', 'FK-Chest', 'FK-Neck', 'FK-Head', 'FK-Thigh.L', 'FK-Finger_Index1.L', 'FK-Finger_Thumb1.L', 'DEF-Spine', 'HIP-Spine', 'TORSO-Spine'):
        b = ab.bones.get(n)
        out['rest_dir'][n] = None if b is None else dict(head=[round(x, 2) for x in b.head_local], tail=[round(x, 2) for x in b.tail_local], parent=b.parent.name if b.parent else None, ctr=[c.type for c in rig.pose.bones[n].constraints][:4])
    out['eye_target_props'] = {n: [k for k in rig.pose.bones[n].keys()][:10] for n in out['eye_like'][:8]}
except Exception:
    out['err'] = traceback.format_exc()[-1800:]
json.dump(out, open(sys.argv[-1], 'w'), indent=1, default=str)
