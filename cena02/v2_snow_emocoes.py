# Emocoes do Snow (Marcos) coerentes com a historia, frames 1-720. Substitui TODAS as chaves de rosto (Eyemask*/Mouth*) por uma linha do tempo:
# cansaco na fila -> impaciencia/raiva no carro -> suspiro -> cansaco -> surpresa e preocupacao na briga -> exaustao em casa -> irritacao ao arremessar a chave
# -> alivio ao sentar -> surpresa e indignacao com o jornal -> tristeza -> dorme.  Rodar com -S Scene.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snow_lib import *

# 1) apaga as chaves antigas de rosto
face_bones = {b for (b, _, _) in list(pose_vals("Eyemask Default")) + list(pose_vals("Mouth Default"))}
for n in ("Sad", "Closed", "Relaxed", "Angry", "Scared", "Cocky", "Compressed"): face_bones |= {b for (b, _, _) in pose_vals(f"Eyemask {n}")}
for n in ("Compressed", "Openfrown", "Teethfrown", "Narrow", "Opensmile", "Default", "Oo", "Uu"): face_bones |= {b for (b, _, _) in pose_vals(f"Mouth {n}")}
act = rig.animation_data.action
removed = 0
for fc in list(fcurves()):
    m = re.match(r'pose\.bones\["([^"]+)"\]\.(\w+)', fc.data_path)
    if m and m.group(1) in face_bones and m.group(2) in ("location", "rotation_euler", "scale"):
        if hasattr(act, "fcurves"): act.fcurves.remove(fc)
        else:
            for l in act.layers:
                for s in l.strips:
                    for cb in s.channelbags:
                        if fc in list(cb.fcurves): cb.fcurves.remove(fc)
        removed += 1
print("rosto: curvas removidas", removed)

# 2) linha do tempo de emocoes: (frame, olhos, boca)
def E(**k): return k
T = [
 (1, E(Sad=.40), E(Compressed=.30)), (40, E(Sad=.50), E(Compressed=.35)), (60, E(Sad=.45, Angry=.15), E(Compressed=.40)),
 (73, E(Sad=.40), E(Compressed=.30)),
 (88, E(Angry=.35, Sad=.15), E(Compressed=.50)), (104, E(Angry=.30), E(Compressed=.50)),
 (108, E(Cocky=.45), E(Narrow=.30)), (113, E(Cocky=.45), E(Narrow=.30)),
 (116, E(Angry=.55, Sad=.20), E(Teethfrown=.50)), (122, E(Angry=.55, Sad=.20), E(Teethfrown=.50)),
 (125, E(Sad=.80), E(Openfrown=1.0)), (129, E(Sad=.80), E(Openfrown=1.0)),
 (136, E(Sad=.70), E(Compressed=.50)), (142, E(Sad=.70, Closed=.60), E(Compressed=.50)),
 (150, E(Sad=.50), E(Compressed=.35)), (190, E(Sad=.45), E(Compressed=.35)),
 (205, E(Angry=.30, Sad=.20), E(Compressed=.45)), (225, E(Angry=.25, Sad=.20), E(Compressed=.45)), (243, E(Sad=.50), E(Compressed=.40)),
 (247, E(Sad=.60), E(Compressed=.50)), (252, E(Sad=.60), E(Compressed=.50)),
 (253, E(Sad=.70), E(Compressed=.30)), (262, E(Sad=.30), E(Compressed=.30)),
 (268, E(Scared=.55), E(Oo=.40)), (288, E(Scared=.45), E(Oo=.20)),
 (300, E(Scared=.30, Sad=.20), E(Compressed=.40)),
 (321, E(Scared=.35), E(Openfrown=.30)), (349, E(Scared=.35), E(Openfrown=.30)),
 (357, E(Scared=.50, Sad=.20), E(Openfrown=.50)), (396, E(Scared=.50, Sad=.20), E(Openfrown=.50)),
 (410, E(Sad=.55, Angry=.10), E(Compressed=.50)), (440, E(Sad=.60), E(Compressed=.55)), (475, E(Sad=.60, Angry=.10), E(Compressed=.50)),
 (492, E(Sad=.50), E(Compressed=.30)),
 (493, E(Sad=.70), E(Compressed=.50)), (503, E(Sad=.70), E(Compressed=.50)),
 (506, E(Sad=.40, Angry=.35), E(Teethfrown=.35)), (510, E(Sad=.40, Angry=.35), E(Teethfrown=.35)),
 (516, E(Sad=.60), E(Compressed=.40)), (524, E(Sad=.60), E(Compressed=.40)),
 (528, E(Sad=.70), E(Openfrown=.60)), (534, E(Sad=.70), E(Openfrown=.60)),
 (540, E(Relaxed=.30), E(Default=1.0)), (560, E(Relaxed=.20), E(Default=1.0)),
 (566, E(Scared=.50), E(Oo=.30)), (576, E(Scared=.50), E(Oo=.30)),
 (582, E(Angry=.45, Scared=.20), E(Teethfrown=.40)), (600, E(Angry=.45, Scared=.20), E(Teethfrown=.40)),
 (606, E(Angry=.40), E(Compressed=.50)), (614, E(Angry=.40), E(Compressed=.50)),
 (620, E(Sad=.60), E(Compressed=.50)), (628, E(Sad=.70), E(Compressed=.60)), (640, E(Sad=.75), E(Openfrown=.40)),
 (660, E(Sad=.70, Closed=1.0), E(Compressed=.50)),
 (670, E(Sad=.70, Closed=1.0), E(Openfrown=.60)), (676, E(Sad=.70, Closed=1.0), E(Openfrown=.60)),
 (684, E(Sad=.30, Closed=1.0), E(Compressed=.20)), (720, E(Sad=.30, Closed=1.0), E(Compressed=.20)),
]
for f, e, m in T: face(f, e, m)
# piscadas (so quando os olhos estao abertos)
for f in (30, 98, 158, 200, 278, 330, 404, 450, 545, 560, 592, 636):
    seg = [t for t in T if t[0] <= f][-1]
    blink(f, seg[1], seg[2], 7)
smooth_new()
print("EMOCOES ok; marcos:", len(T))
finish()
