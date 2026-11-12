import bpy, sys, json, traceback
from mathutils import Vector
out = {}
try:
    D = bpy.data
    rig = D.objects['RIG-Snow']
    ab = rig.data
    # ossos de controle principais (nao deform, nao mecanismo) por coleção
    colmap = {}
    for bc in ab.collections_all:
        colmap[bc.name] = [b.name for b in bc.bones][:80]
    out['col_main'] = colmap.get('Main Controls')
    for nm in ('Left Arm FK', 'Right Arm FK', 'Left Leg FK', 'Spine FK', 'Left Arm IK', 'Left Leg IK', 'Spine IK', 'Fingers FK', 'Left Index FK', 'Left Thumb FK', 'Face Main', 'Misc', 'Torso Tweak'):
        out['col_' + nm] = colmap.get(nm)
    # padrões de nomes
    names = [b.name for b in ab.bones]
    out['n'] = len(names)
    out['fk'] = [n for n in names if n.startswith('FK-')][:120]
    out['ik'] = [n for n in names if n.startswith('IK-')][:60]
    out['ctrl_other'] = [n for n in names if not n.startswith(('DEF-', 'MCH-', 'STR-', 'ORG-', 'TWK-', 'FK-', 'IK-', 'P-', 'DSP-', 'LTC', 'LAT', 'Cheek', 'Jaw', 'Lip', 'Nose', 'Eye', 'Brow', 'Forehead', 'Teeth', 'Tongue'))][:250]
    # propriedades de IK/FK
    props = {}
    for pb in rig.pose.bones:
        ks = [k for k in pb.keys() if not k.startswith('_') and k not in ('cloudrig_component', 'rigify_type')]
        if ks and (pb.name.startswith(('Properties', 'PROP', 'Prop')) or 'ik_fk' in ' '.join(ks).lower() or 'ik' in ' '.join(ks).lower()[:20]):
            props[pb.name] = {k: (pb[k] if isinstance(pb[k], (int, float)) else str(pb[k])[:30]) for k in ks[:20]}
    out['props'] = dict(list(props.items())[:40])
    # shape keys da cabeça e seus drivers
    head = D.objects['GEO-snow-head']
    sk = head.data.shape_keys
    out['head_keys'] = [kb.name for kb in sk.key_blocks]
    drv = {}
    for fc in (sk.animation_data.drivers if sk.animation_data else []):
        try:
            tg = [(v.name, [(t.id.name if t.id else None, t.data_path or t.bone_target) for t in v.targets][0]) for v in fc.driver.variables][:1]
        except Exception:
            tg = None
        drv[fc.data_path] = (fc.driver.type, fc.driver.expression[:40], tg)
    out['head_drivers_n'] = len(drv)
    out['head_drivers_sample'] = dict(list(drv.items())[:12])
    # ações (poses)
    acts = {}
    for a in D.actions:
        info = dict(frames=[round(a.frame_range[0]), round(a.frame_range[1])], markers=[(m.name, m.frame) for m in a.pose_markers][:70])
        acts[a.name] = info
    out['actions'] = acts
    # posição de repouso: direção dos ossos de braço (T-pose?)
    def d(n):
        b = ab.bones.get(n)
        return None if b is None else [[round(x, 2) for x in b.head_local], [round(x, 2) for x in b.tail_local]]
    out['rest_hint'] = {n: d(n) for n in [x for x in names if x.startswith('DEF-') and any(k in x for k in ('Arm', 'Hand', 'Leg', 'Thigh', 'Shin', 'Spine', 'Neck', 'Head'))][:40]}
    out['texts'] = {t.name: t.as_string()[:1500] for t in D.texts if t.name in ('ReadMe.txt',)}
    out['text_post'] = D.texts['snow_post_generation.py'].as_string()[:1500]
except Exception:
    out['err'] = traceback.format_exc()[-1500:]
json.dump(out, open(sys.argv[-1], 'w'), indent=1, default=str)
