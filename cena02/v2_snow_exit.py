# Snow (Marcos) frames 243-492: sai do carro, FECHA a porta do carro com a mao (249-251), anda ate o ponto da briga (253-260)
# e fica em pe assistindo (olha o Miguel e o Claudio). Pes em IK sem deslizar. Sem bracos cruzados.
# Uso: blender -b cena02_v2.blend -S Scene --python cena02/v2_snow_exit.py   (depois de v2_snow_car.py e v2_snow_car_face.py)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snow_lib import *

door = bpy.data.objects["VEH_CarroMarcos_Porta"]; pivo = bpy.data.objects["VEH_CarroMarcos_Porta_Pivo"]
MIGUEL = Vector((10.0, 7.04, 1.6)); CLAUDIO = Vector((10.0, 5.84, 1.6))
E0 = {"Sad": 0.3}; M0 = {"Compressed": 0.3}

# ---------------------------------------------------------------- raiz (RIG_Marcos): em vez de deslizar 5,6 m entre 249 e 253, ele fica
# junto a porta (249-252) e se aproxima dela ao fechar; o corte para o plano 05 (frame 253) leva ao novo lugar.
def rkey(f, loc, yaw, interp=None):
    rm.location = loc; rm.rotation_euler = (0, 0, yaw)
    rm.keyframe_insert("location", frame=f); rm.keyframe_insert("rotation_euler", frame=f)
    if interp:
        a = rm.animation_data.action
        ch = list(a.fcurves) if hasattr(a, "fcurves") else [fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
        for fc in ch:
            if fc.data_path in ("location", "rotation_euler"):
                for kp in fc.keyframe_points:
                    if round(kp.co[0]) == f: kp.interpolation = interp
rkey(249, Vector((-3.03, 10.24, 0.0)), math.pi, 'CONSTANT')
rkey(250, Vector((-2.95, 10.33, 0.0)), math.pi, 'LINEAR')
rkey(251, Vector((-2.85, 10.45, 0.0)), math.pi, 'LINEAR')
rkey(252, Vector((-2.85, 10.45, 0.0)), math.pi, 'CONSTANT')

# o Marcos antigo tinha a chave do frame 260 em Bezier: a raiz derivava ate o apartamento (493) -> trava em 260
_a = rm.animation_data.action
for fc in (list(_a.fcurves) if hasattr(_a, "fcurves") else [fc for l in _a.layers for s_ in l.strips for cb in s_.channelbags for fc in cb.fcurves]):
    if fc.data_path in ("location", "rotation_euler", "scale"):
        for kp in fc.keyframe_points:
            if round(kp.co[0]) in (260,): kp.interpolation = 'CONSTANT'

# ---------------------------------------------------------------- no carro 244-246: vira para a porta, tira as pernas
frame(243)
ik_legs(False, 243); ik_arms(True, 243)
frame(245); torso(245, lean=6, hpitch=0, htwist=-25)
_, F, L = axes()
for side, nm in ((1, "L"), (-1, "R")):                                   # joelhos para o lado da porta (esquerda)
    aim(f"FK-Thigh.{nm}", (L * 0.85 + F * 0.5 - UP * 0.15).normalized()); key(f"FK-Thigh.{nm}", 246)
    aim(f"FK-Knee.{nm}", (L * 0.2 - UP * 0.95).normalized()); key(f"FK-Knee.{nm}", 246)
frame(246); torso(246, lean=10, hpitch=0, htwist=-30)

# ---------------------------------------------------------------- fora do carro (247): pes e raiz no chao, braços em FK
GZ = 0.0
ik_legs(True, 247); ik_arms(False, 247)
def pe_porta(f):
    """ponto na porta do carro (perto da extremidade livre), segue a porta fechando"""
    c = door.matrix_world.translation; pv = pivo.matrix_world.translation
    d = Vector((c.x - pv.x, c.y - pv.y, 0)).normalized()
    return c + d * 0.10 + UP * 0.25
frame(247); stand_feet(247, GZ)
hand(246, 0.65, 0.65); hand(247, 0.0, 0.0)          # solta o volante: maos relaxadas
torso(247, lean=26, hpitch=14, htwist=10)
arms(247, dict(u=(0.2, 0.25, -0.9), f=(0.0, 0.7, -0.7)))
face(247, {"Sad": 0.6}, {"Compressed": 0.5})
frame(248); stand_feet(248, GZ); torso(248, lean=20, hpitch=10, htwist=5)
arms(248, dict(u=(0.2, 0.2, -0.95), f=(0.05, 0.6, -0.8)))
ik_arms(False, 248)
# 249-251: mao direita no topo da porta, empurra ate fechar; passo curto (a raiz se aproxima da porta)
keyprop("Properties", "ik_right_upperarm", 0.0, 248); keyprop("Properties", "ik_right_upperarm", 1.0, 249)
walk(249, 252, GZ, step=0.3, swing_arms=False)
for f in (249, 250, 251, 252):
    frame(f)
    torso(f, lean=14 - (f - 249) * 2, hpitch=8, htwist=0)
    P = pe_porta(f)
    place("IK-Wrist.R", P, (P - root_world()).normalized()); key("IK-Wrist.R", f, loc=True)
    arms(f, REL, REL, key_it=False)
    for b in ("UpperArm", "Forearm", "Wrist"): key(f"FK-{b}.L", f)
    face(f, {"Sad": 0.6}, {"Compressed": 0.5})
keyprop("Properties", "ik_right_upperarm", 0.0, 253)

# ---------------------------------------------------------------- plano 05-07: anda e fica em pe assistindo a briga
walk(253, 260, GZ, step=0.55)
frame(260)
for f in range(261, 493, 12):
    frame(f)
    cl = (f // 24) % 2 == 1
    tw = look_at(f, CLAUDIO if cl else MIGUEL, head_share=0.5)
    torso(f, lean=9 + (2 if cl else -1), hpitch=6, htwist=tw)
    arms(f, REL)
frame(260); look_at(260, MIGUEL); torso(260, lean=8, hpitch=4, htwist=0); arms(260, REL)
# pes plantados ate o fim do trecho (mantem a ultima posicao da caminhada)
frame(492)
for nm in ("L", "R"): key(f"IK-Foot.{nm}", 492, loc=True)
# rosto: cansado -> surpreso quando a briga comeca (frames do roteiro 253-288)
face(253, {"Sad": 0.7}, M0); face(262, E0, M0)
face(268, {"Scared": 0.55}, {"Oo": 0.4}); face(288, {"Scared": 0.45}, {"Oo": 0.2}); face(300, E0, M0)
blink(278, {"Scared": 0.45}, {"Oo": 0.2}, 8)
blink(330, E0, M0); blink(400, E0, M0); blink(450, E0, M0)
face(492, E0, M0)
smooth_new()
print("SNOWEXIT ok; chaves:", sum(len(fc.keyframe_points) for fc in fcurves()))
finish()
