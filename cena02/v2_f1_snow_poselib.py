# Traz as poses prontas do Snow (maos, boca, mascara dos olhos) para a v2. Rodar com -S Scene.
import bpy, re
import os
_MODELOS = os.environ.get("ANIM3D_MODELOS", os.path.join(os.path.expanduser("~"), "Downloads"))   # pasta dos .blend baixados do Blender Studio
SNOW = os.path.join(_MODELOS, *"Snow_v4.2/Snow/snow_v4.2.blend".split("/"))
want = ["Hand Crawl", "Hand Fist", "Hand Flat", "Hand Folded", "Hand Point", "Hand Relaxed", "Hand Spread", "Hand Spread2"] + \
       [n for n in ("Mouth Compressed", "Mouth Default", "Mouth Ff", "Mouth Narrow", "Mouth Oo", "Mouth Openfrown", "Mouth Opensmile", "Mouth Teethfrown", "Mouth Teethsmile", "Mouth Uu")] + \
       [f"Eyemask {n}" for n in ("Angry", "Closed", "Cocky", "Compressed", "Default", "Relaxed", "Sad", "Scared")]
with bpy.data.libraries.load(SNOW, link=False) as (src, dst):
    dst.actions = [a for a in want if a in src.actions]
def fcs(a): return list(a.fcurves) if hasattr(a, "fcurves") else [fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
for a in dst.actions:
    a.use_fake_user = True
    f = fcs(a); bones = sorted({re.findall(r'pose.bones\["([^"]+)"\]', x.data_path)[0] for x in f if 'pose.bones' in x.data_path})
    print("POSE", a.name, "fcs", len(f), "bones", len(bones), "range", [round(v) for v in a.frame_range], bones[:3], "L" if any(b.endswith('.L') for b in bones) else "-", "R" if any(b.endswith('.R') for b in bones) else "-")
print("POSELIB loaded", len(dst.actions))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
