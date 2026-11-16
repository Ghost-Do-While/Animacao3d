# CORRECAO (frame 233 etc.): no carro as pernas do Snow atravessavam o assoalho (tornozelo em z=0,27; o assoalho do carro fica em z=0,525
# e o pe aparecia embaixo do carro). Aqui as coxas sobem um pouco e as canelas apontam para a frente/baixo, de modo que os pes
# repousem no assoalho (tornozelo ~0,60). Reaponta so coxa/joelho/pe nos frames ja chaveados de 1 a 243.
# Uso: blender -b cena02_v2.blend -S Scene --python cena02/v2_fix_pernas_carro.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snow_lib import *

THIGH_UP, SHIN_DOWN = math.radians(15), math.radians(30)
frames = sorted({round(kp.co[0]) for fc in fcurves() if fc.data_path == 'pose.bones["FK-Thigh.L"].rotation_euler' for kp in fc.keyframe_points if 1 <= kp.co[0] <= 243})
print("frames:", frames)
for f in frames:
    frame(f); _, F, L = axes()
    for side, nm in ((1, "L"), (-1, "R")):
        aim(f"FK-Thigh.{nm}", (L * side * 0.06 + F * math.cos(THIGH_UP) + UP * math.sin(THIGH_UP)).normalized()); key(f"FK-Thigh.{nm}", f)
        aim(f"FK-Knee.{nm}", (F * math.cos(SHIN_DOWN) - UP * math.sin(SHIN_DOWN)).normalized()); key(f"FK-Knee.{nm}", f)
        aim(f"FK-Foot.{nm}", (F * 0.97 - UP * 0.10).normalized()); key(f"FK-Foot.{nm}", f)
smooth_new()
for f in (1, 120, 233):
    frame(f); print("TORNOZELO", f, [round((rig.matrix_world @ pb[n].head).z, 3) for n in ("DEF-Foot.L", "DEF-Foot.R")])
finish()
