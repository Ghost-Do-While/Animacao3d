# build_snow.py - roda em Blender de FUNDO: prepara snow/snow_ready.blend a partir de snow/snow_v4.2.blend (CC-BY, Blender Studio)
#   blender -b --disable-autoexec snow/snow_v4.2.blend --python cena02/build_snow.py
import bpy, os, sys, traceback
D = bpy.data
try:
    for o in list(D.objects):
        if o.type in ('LIGHT', 'CAMERA'): D.objects.remove(o, do_unlink=True)
    rig = D.objects['RIG-Snow']
    P = rig.pose.bones['Properties']
    for k in ('ik_left_upperarm', 'ik_right_upperarm'): P[k] = 0.0         # braços em FK (a animação usa FK); pernas continuam em IK (pés plantados)
    meta = D.objects.get('META-Snow')
    if meta:
        for c in list(meta.users_collection): c.objects.unlink(meta)
        D.objects.remove(meta, do_unlink=True)
    out = os.path.join(os.path.dirname(bpy.data.filepath), 'snow_ready.blend')
    bpy.ops.wm.save_as_mainfile(filepath=out, relative_remap=True)
    print('SNOW_READY', out)
except Exception:
    print('SNOW_ERR', traceback.format_exc())
