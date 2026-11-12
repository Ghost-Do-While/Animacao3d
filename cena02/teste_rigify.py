import bpy, json, sys, traceback, math
from mathutils import Vector, Matrix
out = {}
try:
    bpy.ops.preferences.addon_enable(module='rigify')
    bpy.ops.object.armature_human_metarig_add()
    meta = bpy.context.active_object
    ms = {}
    for b in meta.data.bones:
        if b.name.startswith(('spine', 'pelvis', 'thigh', 'shin', 'foot', 'toe', 'shoulder', 'upper_arm', 'forearm', 'hand', 'face', 'eye', 'jaw', 'palm', 'f_index', 'breast')) and not b.name.startswith(('face.',)) or b.name in ('face', 'eye.L'):
            ms[b.name] = [[round(x, 3) for x in b.head_local], [round(x, 3) for x in b.tail_local], b.parent.name if b.parent else None]
    out['meta'] = ms
    out['eye_names'] = [b.name for b in meta.data.bones if 'eye' in b.name]
    out['rig_params'] = {n: {k: (v if isinstance(v, (int, float, str, bool)) else str(v)) for k, v in meta.pose.bones[n].rigify_parameters.items()} for n in ('upper_arm.L', 'spine', 'thigh.L')}
    out['rig_type'] = {n: meta.pose.bones[n].rigify_type for n in ('upper_arm.L', 'spine', 'thigh.L', 'eye.L', 'face', 'spine.004')}
except Exception:
    out['err'] = traceback.format_exc()[-1500:]
json.dump(out, open(sys.argv[-1], 'w'), indent=1)
