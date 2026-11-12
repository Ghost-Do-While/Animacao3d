# Parte 4b - SNOW (Blender Studio, CC-BY: "Snow Rig (CC) Blender Foundation | studio.blender.org") substitui o Claudio.
# O rig Rigify do Claudio continua no arquivo, escondido, como FONTE da animação; a pose dele é transferida (retarget por orientação
# no espaço do armature, com offset de pose de repouso) para os controles FK do Snow, mais olhar, visemas e expressões do rosto.
SNOW_FILE = os.path.join(os.path.dirname(BASE), 'snow', 'snow_ready.blend')
SNOW_DIR = os.path.dirname(SNOW_FILE)
if not os.path.exists(SNOW_FILE):
    raise RuntimeError('snow/snow_ready.blend não encontrado (rode cena02/build_snow.py)')
with D.libraries.load(SNOW_FILE, link=False) as (src_, dst_):
    dst_.collections = [n for n in src_.collections]
    dst_.actions = [n for n in src_.actions if n.startswith(('Mouth ', 'Eyemask ', 'Hand '))]     # bibliotecas de poses do rosto e das mãos
for a_ in dst_.actions:
    if a_ is not None: a_.use_fake_user = True
for c_ in dst_.collections:
    if c_ is not None and c_.name == 'CH-snow':
        sc_.collection.children.link(c_)
    elif c_ is not None:
        c_.use_fake_user = True
# texturas: apontam para snow/textures (relativo ao projeto)
for im_ in D.images:
    if im_.name.startswith(('eyes_', 'hair_', 'pants_', 'shirt_', 'shoes_', 'skin_')) and im_.source in ('FILE', 'TILED'):
        fn_ = os.path.basename(bpy.path.abspath(im_.filepath, library=im_.library)) if im_.filepath else im_.name
        im_.filepath = os.path.join(SNOW_DIR, 'textures', fn_)
rigS = D.objects['RIG-Snow']; rigS.rotation_mode = 'XYZ'
rigS.location = (CLAUDIO_POS[0], CLAUDIO_POS[1], 0); rigS.rotation_euler = (0, 0, rad(180))
rigC = CHARS['Claudio']['rig']; fC_ctrl = CHARS['Claudio']['face']
for pn_ in ('ik_left_upperarm', 'ik_right_upperarm'): rigS.pose.bones['Properties'][pn_] = 0.0       # braços em FK

# ---------------------------------------------------------------- mapa de ossos (fonte Rigify -> controle FK do Snow), pai antes do filho
PAIRS = [('FK-Spine', 'DEF-spine.001'), ('FK-RibCage', 'DEF-spine.002'), ('FK-Chest', 'DEF-spine.003'),
         ('FK-Neck', 'DEF-spine.005'), ('FK-Head', 'DEF-spine.006')]
ARM_BONES = []
for s_ in 'LR':
    PAIRS += [(f'FK-Shoulder.{s_}', f'DEF-shoulder.{s_}'), (f'FK-UpperArm.{s_}', f'DEF-upper_arm.{s_}'),
              (f'FK-Forearm.{s_}', f'DEF-forearm.{s_}'), (f'FK-Wrist.{s_}', f'DEF-hand.{s_}')]
    ARM_BONES += [f'FK-UpperArm.{s_}', f'FK-Forearm.{s_}', f'FK-Wrist.{s_}']
    for fs_, fd_ in (('f_index', 'Index'), ('f_middle', 'Middle'), ('f_ring', 'Ring'), ('f_pinky', 'Pinky'), ('thumb', 'Thumb')):
        for i_ in (1, 2, 3):
            PAIRS.append((f'FK-Finger_{fd_}{i_}.{s_}', f'DEF-{fs_}.0{i_}.{s_}')); ARM_BONES.append(f'FK-Finger_{fd_}{i_}.{s_}')
def restR(rig, b): return rig.data.bones[b].matrix_local.to_3x3().to_quaternion().to_matrix()
Q_ = {}
for s_ in 'LR':   # braços do Snow em T -> pendurados como no rig fonte (swing mínimo em torno do ombro)
    d_dst = restR(rigS, f'FK-UpperArm.{s_}') @ Vector((0, 1, 0)); d_src = restR(rigC, f'DEF-upper_arm.{s_}') @ Vector((0, 1, 0))
    Q_[s_] = d_dst.rotation_difference(d_src).to_matrix()
REF = {}
for dn, sn in PAIRS:
    side = dn[-1]
    REF[dn] = (Q_[side] @ restR(rigS, dn)) if dn in ARM_BONES else restR(rigS, dn)
REST_SRC = {sn: restR(rigC, sn) for _d, sn in PAIRS}

# ---------------------------------------------------------------- poses do rosto (biblioteca do Snow: ações de pose de 1 frame)
def read_pose(act):
    res = {}
    for layer in act.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    if fc.data_path.startswith('pose.bones["'):
                        bn = fc.data_path.split('"')[1]; prop = fc.data_path.rsplit('.', 1)[1]
                        if prop in ('location', 'rotation_euler', 'scale'):
                            kp = fc.keyframe_points
                            res.setdefault(bn, {})[(prop, fc.array_index)] = fc.evaluate(kp[0].co.x) if len(kp) else 0.0
    return res
POSES = {n: read_pose(D.actions[n]) for n in D.actions.keys() if n.startswith(('Mouth ', 'Eyemask '))}
BASE_FACE = {}
for dn_ in ('Mouth Default', 'Eyemask Default'):
    for bn, ch in POSES[dn_].items():
        for k, v in ch.items(): BASE_FACE[(bn,) + k] = v
MOUTH_MAP = {'A': [('Mouth Opensmile', 0.5), ('Mouth Openfrown', 0.5)], 'E': [('Mouth Teethsmile', 0.8)], 'I': [('Mouth Teethsmile', 0.6)],
             'O': [('Mouth Oo', 1.0)], 'U': [('Mouth Uu', 1.0)], 'MBP': [('Mouth Compressed', 1.0)], 'FV': [('Mouth Ff', 1.0)],
             'mouth_shout': [('Mouth Openfrown', 1.0)], 'mouth_smirk': [('Mouth Teethsmile', 0.45)], 'mouth_frown': [('Mouth Teethfrown', 0.6)],
             'mouth_smile': [('Mouth Opensmile', 0.7)]}
EYE_MAP = {'blink': [('Eyemask Closed', 1.0)], 'eyes_closed': [('Eyemask Closed', 1.0)], 'brow_angry': [('Eyemask Angry', 1.0)],
           'brow_smug': [('Eyemask Cocky', 1.0)], 'brow_sad': [('Eyemask Sad', 1.0)], 'brow_up': [('Eyemask Scared', 0.7)], 'brow_down': [('Eyemask Compressed', 0.8)]}
def face_values():
    w = {}
    for mp in (MOUTH_MAP, EYE_MAP):
        for prop, lst in mp.items():
            v = float(fC_ctrl.get(prop, 0.0))
            if abs(v) < 1e-4: continue
            for pn, sc in lst: w[pn] = min(1.0, w.get(pn, 0.0) + v * sc)
    vals = dict(BASE_FACE)
    for pn, wt in w.items():
        for bn, ch in POSES[pn].items():
            for k, v in ch.items():
                key_ = (bn,) + k
                vals[key_] = vals.get(key_, v) + wt * (v - BASE_FACE.get(key_, v))
    return vals
FACE_BONES = sorted({k[0] for k in BASE_FACE} | {bn for P_ in POSES.values() for bn in P_})

# ---------------------------------------------------------------- bake: percorre os frames animados do Claudio e transfere para o Snow
# (resultado guardado em snow/snow_bake_cache.json: só refaz se a animação do Claudio mudar)
import json, hashlib
CACHE = os.path.join(SNOW_DIR, 'snow_bake_cache.json')
def _sig():
    h = hashlib.md5()
    for ob in (rigC, fC_ctrl):
        for fc in sorted(fcurves(ob), key=lambda x: (x.data_path, x.array_index)):
            h.update(fc.data_path.encode()); h.update(str(fc.array_index).encode())
            for kp in fc.keyframe_points: h.update(('%.4f,%.4f;' % (kp.co.x, kp.co.y)).encode())
    h.update(str(sorted(PAIRS)).encode()); h.update(str(len(POSES)).encode()); h.update(b'v2')
    return h.hexdigest()
SIG = _sig()
orig_hide = {o.name: o.hide_viewport for o in D.objects if o.type == 'MESH'}
for o in D.objects:
    if o.type == 'MESH' and (o.name.startswith('GEO-snow') or o.name.startswith('MESH_Claudio') or o.name.startswith('MESH_Miguel') or o.name.startswith('MESH_Marcos')):
        o.hide_viewport = True
upd = bpy.context.view_layer.update
pbsS = rigS.pose.bones
tgt_eyes = pbsS['TGT-Eyes']
FR_SNOW = [1] + list(range(250, 495, 2)) + [720]
cache = None
if os.path.exists(CACHE):
    try:
        cache = json.load(open(CACHE))
        if cache.get('sig') != SIG: cache = None
    except Exception: cache = None
if cache:                                              # aplica o resultado já calculado (rápido)
    for f_s, chans in cache['frames'].items():
        f = int(f_s)
        for ck, vals in chans.items():
            bn, prop = ck.split('|'); pb = pbsS[bn]
            if prop == 'rotation_euler': pb.rotation_mode = 'XYZ'
            setattr(pb, prop, vals); pb.keyframe_insert(prop, frame=f); set_interp(pb, prop, f, 'LINEAR')
else:
    rec = {}
    for f in FR_SNOW:
        sc_.frame_set(f)
        cur = {sn: rigC.pose.bones[sn].matrix.to_3x3().to_quaternion().to_matrix() for _d, sn in PAIRS}
        for dn, sn in PAIRS:
            Rt = (cur[sn] @ REST_SRC[sn].inverted()) @ REF[dn]
            pb = pbsS[dn]; pb.rotation_mode = 'XYZ'; pb.rotation_euler = (0, 0, 0); upd()
            R0 = pb.matrix.to_3x3().to_quaternion().to_matrix()
            pb.rotation_euler = (R0.inverted() @ Rt).to_euler('XYZ'); upd()
        rf = rec.setdefault(str(f), {})
        for dn, _sn in PAIRS:
            pbsS[dn].keyframe_insert('rotation_euler', frame=f); set_interp(pbsS[dn], 'rotation_euler', f, 'LINEAR')
            rf[dn + '|rotation_euler'] = list(pbsS[dn].rotation_euler)
        # olhar: o alvo dos olhos do Snow vai para o mesmo ponto do mundo que o do Claudio
        Pw = rigC.matrix_world @ rigC.pose.bones['eyes'].matrix.translation
        Pa = rigS.matrix_world.inverted() @ Pw
        tgt_eyes.location = (0, 0, 0); upd()
        d_ = Pa - tgt_eyes.matrix.translation
        tgt_eyes.location = tgt_eyes.bone.matrix_local.to_3x3().inverted() @ d_; upd()
        tgt_eyes.keyframe_insert('location', frame=f); set_interp(tgt_eyes, 'location', f, 'LINEAR')
        rf['TGT-Eyes|location'] = list(tgt_eyes.location)
        # rosto: visemas e expressões do Claudio (FACE_Claudio) -> poses do Snow
        vals = face_values()
        for (bn, prop, idx), v in vals.items():
            pb = pbsS.get(bn)
            if pb is None: continue
            if prop == 'rotation_euler': pb.rotation_mode = 'XYZ'
            getattr(pb, prop)[idx] = v
        for bn in FACE_BONES:
            pb = pbsS.get(bn)
            if pb is None: continue
            for prop in ('location', 'rotation_euler', 'scale'):
                if any(k[0] == bn and k[1] == prop for k in vals):
                    pb.keyframe_insert(prop, frame=f); set_interp(pb, prop, f, 'LINEAR')
                    rf[bn + '|' + prop] = list(getattr(pb, prop))
    json.dump({'sig': SIG, 'frames': rec}, open(CACHE, 'w'))
for o in D.objects:
    if o.name in orig_hide: o.hide_viewport = orig_hide[o.name]
# o Claudio (Rigify) sai de cena: continua no arquivo, escondido, como fonte de animação
for c_ in (D.collections.get('CHAR_Claudio'),):
    if c_ is not None:
        c_.hide_render = True; c_.hide_viewport = True
        for o in c_.all_objects: o.hide_render = True
rS = rigS
sc_.frame_set(1)
