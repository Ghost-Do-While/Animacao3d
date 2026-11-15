# Snow (Marcos) no APARTAMENTO, frames 493-720:
#  493-505  abre a porta com a mao esquerda na macaneta, entra, VIRA e FECHA a porta puxando a macaneta
#  505-510  vira, a chave (mao direita) e jogada na mesa lateral (soltura no frame da mao)
#  510-527  caminha ate o sofa e senta (pes em IK, sem deslizar)
#  528-627  pega o controle (mao direita), aponta para a TV e a desliga; deixa o controle no sofa
#  628-720  fecha os olhos, suspira e dorme
# Uso: blender -b cena02_v2.blend -S Scene --python cena02/v2_snow_apto.py   (depois de v2_snow_exit.py)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snow_lib import *

piv = bpy.data.objects["ENV_Apartamento_Porta_Pivo"]; handle = bpy.data.objects["ENV_Apartamento_Porta_Macaneta"]
keys_ = bpy.data.objects["PRP_Chaves"]; remote = bpy.data.objects["PRP_ControleRemoto"]
FL = 6.2                      # piso do apartamento
TABLE = Vector((-15.05, 5.3, 6.96))
TV = Vector((-15.38, 2.2, 7.55))

def chans(obj):
    a = obj.animation_data.action
    return list(a.fcurves) if hasattr(a, "fcurves") else [fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
def drop_keys(obj, paths, lo, hi):
    for fc in chans(obj):
        if fc.data_path in paths:
            for kp in reversed(list(fc.keyframe_points)):
                if lo <= kp.co[0] <= hi: fc.keyframe_points.remove(kp)
def set_interp(obj, paths, frames, interp):
    for fc in chans(obj):
        if fc.data_path in paths:
            for kp in fc.keyframe_points:
                if round(kp.co[0]) in frames: kp.interpolation = interp

# ============================================================== 1) raiz (RIG_Marcos): nova trajetoria com a porta
drop_keys(rm, ("location", "rotation_euler", "scale"), 493, 540)
Y0 = -6.283185307
ROOT = [  # frame, (x, y, z), yaw  (yaw continuo: vira para a porta e depois desvira para a mesa/sofa)
    (493, (-13.15, 6.30, FL), 0.0), (495, (-13.20, 5.80, FL), 0.0), (497, (-13.10, 5.20, FL), 0.0),
    (499, (-13.05, 5.15, FL), -1.571), (500, (-13.00, 5.10, FL), -1.571), (505, (-12.90, 5.55, FL), -3.14159),
    (507, (-13.20, 5.00, FL), -4.712), (510, (-13.45, 4.60, FL), Y0), (514, (-13.50, 4.00, FL), Y0 - 1.2),
    (518, (-13.60, 3.30, FL), Y0 - 2.034), (521, (-13.30, 2.40, FL), Y0 - 1.571), (524, (-12.85, 2.30, 6.18), Y0 - 1.571),
    (527, (-12.10, 2.20, 5.87), Y0 - 1.571), (531, (-12.05, 2.20, 5.92), Y0 - 1.571), (536, (-12.05, 2.20, 5.91), Y0 - 1.571)]
for f, loc, yaw in ROOT:
    rm.location = Vector(loc); rm.rotation_euler = (0, 0, yaw)
    rm.keyframe_insert("location", frame=f); rm.keyframe_insert("rotation_euler", frame=f)
set_interp(rm, ("location", "rotation_euler"), {493}, 'CONSTANT')      # corte: aparece na porta do apartamento

# ============================================================== 2) porta do apartamento: abre (493-497), segura, FECHA (500-505)
drop_keys(piv, ("rotation_euler",), 1, 720)
for f, a in ((1, 0.0), (492, 0.0), (497, -1.431), (500, -1.431), (505, 0.0), (720, 0.0)):
    piv.rotation_euler[2] = a; piv.keyframe_insert("rotation_euler", index=2, frame=f)

# ============================================================== 3) ajuda: alvos de mao relativos ao corpo
def R_of(): _, F, L = axes(); return -L
def body_pt(fwd, right, h):
    r = root_world(); _, F, L = axes(); return r + F * fwd + (-L) * right + UP * h
def wrist(nm, f, P, d=None):
    place(f"IK-Wrist.{nm}", P, d); key(f"IK-Wrist.{nm}", f, loc=True)
def hang(nm, f, extra_fwd=0.05, h=0.72):
    side = 1 if nm == "L" else -1; _, F, L = axes()
    P = body_pt(extra_fwd, -side * 0.27, h)
    wrist(nm, f, P, (F * 0.15 - UP).normalized())
def seated_h(): return 0.72 - 0.0

# --- todos os bracos em IK a partir do apartamento (sem trocas de FK/IK no meio -> sem saltos)
ik_arms(True, 493)
ik_legs(True, 493)

# ---- 493-499: mao esquerda na macaneta empurra a porta (493-495); mao direita leva a chave
frame(493)
for f in (493, 494, 495):
    frame(f)
    P = handle.matrix_world.translation.copy()
    wrist("L", f, P, (P - root_world()).normalized())
    wrist("R", f, body_pt(0.20, 0.22, 0.95), R_of() * 0.0 + axes()[1])
    torso(f, lean=4, hpitch=0, htwist=0)
hand(493, 0.55, 0.45); hand(495, 0.55, 0.45); hand(496, 0.0, 0.45)
frame(496); hang("L", 496)
walk(493, 497, FL, step=0.45, swing_arms=False)
for f in (496, 497):
    frame(f); hang("L", f); wrist("R", f, body_pt(0.20, 0.22, 0.95), axes()[1]); torso(f, lean=3, hpitch=0, htwist=-10)

# ---- 497-505: vira para a porta e a FECHA puxando a macaneta com a mao esquerda
walk(497, 506, FL, step=0.25, swing_arms=False)
for f in (499, 500, 501, 502, 503, 504, 505):
    frame(f)
    P = handle.matrix_world.translation.copy()
    wrist("L", f, P, (P - root_world()).normalized())
    wrist("R", f, body_pt(0.20, 0.22, 0.95), axes()[1])
    torso(f, lean=6 if f < 503 else 10, hpitch=4, htwist=0)
hand(498, 0.0, 0.45); hand(499, 0.7, 0.45); hand(505, 0.7, 0.45); hand(506, 0.0, 0.45)

# ---- 506-510: solta a porta, vira, chave: mao direita vai para tras e SOLTA (510) em direcao a mesa
walk(506, 510, FL, step=0.3, swing_arms=False)
frame(506); hang("L", 506); wrist("R", 506, body_pt(0.20, 0.22, 0.95), axes()[1])
frame(508); hang("L", 508); wrist("R", 508, body_pt(-0.10, 0.50, 1.15), (-axes()[2]))
frame(510); hang("L", 510); wrist("R", 510, body_pt(-0.25, 0.60, 1.18), (-axes()[2]))
for f in (506, 508, 510):
    frame(f); torso(f, lean=4, hpitch=0, htwist=look_at(f, TABLE, 0.6))
frame(510); P_rel = (rig.matrix_world @ pb["DEF-Wrist.R"].head).copy()     # onde a mao esta ao soltar
hand(508, 0.0, 0.5); hand(510, 0.0, 0.0); hand(512, 0.0, 0.0)

# chave: presa ao pulso direito do Snow ate o frame 510 e depois voa ate a mesa (chegada no 517)
for c in list(keys_.constraints): keys_.constraints.remove(c)
kc = keys_.constraints.new('CHILD_OF'); kc.name = 'NaMao'; kc.target = rig; kc.subtarget = 'DEF-Wrist.R'
kc.inverse_matrix = Matrix.Identity(4); kc.set_inverse_pending = False
drop_keys(keys_, ("location", "rotation_euler", 'constraints["NaMao"].influence'), 1, 720)
def kinf(f, v):
    kc.influence = v; keys_.keyframe_insert('constraints["NaMao"].influence', frame=f)
kinf(1, 0.0); kinf(492, 0.0); kinf(493, 1.0); kinf(509, 1.0); kinf(510, 0.0)
set_interp(keys_, ('constraints["NaMao"].influence',), {1, 492, 493, 509, 510}, 'CONSTANT')
def kloc(f, loc, rot, interp='BEZIER'):
    keys_.location = loc; keys_.rotation_euler = rot
    keys_.keyframe_insert("location", frame=f); keys_.keyframe_insert("rotation_euler", frame=f)
kloc(1, (0, 0, -100), (0, 0, 0)); kloc(492, (0, 0, -100), (0, 0, 0))
kloc(493, (0, 0.1, 0), (0, 0, 0)); kloc(509, (0, 0.1, 0), (0, 0, 0))                # local ao pulso enquanto na mao
kloc(510, Vector(P_rel), (0, 0, 0)); kloc(512, (-14.7, 5.2, 7.38), (0, 0, 0))
kloc(514, (-15.0, 5.3, 7.03), (math.radians(200), math.radians(40), math.radians(90)))
kloc(515, (-15.1, 5.35, 7.1), (math.radians(230), math.radians(30), math.radians(100)))
kloc(517, (-15.15, 5.4, 7.005), (math.radians(270), math.radians(10), math.radians(110)))

# ---- 510-524: anda ate o sofa
walk(510, 521, FL, step=0.5, swing_arms=False)
for f in (512, 514, 516, 518, 520):
    frame(f); hang("L", f); hang("R", f); torso(f, lean=8, hpitch=6, htwist=look_at(f, TV, 0.4))
hand(514, 0.0, 0.0)
walk(521, 524, FL, step=0.25, swing_arms=False)
frame(524); hang("L", 524); hang("R", 524); torso(524, lean=10, hpitch=4, htwist=look_at(524, TV, 0.4))

# ---- 524-536: senta (raiz desce); pes em IK a frente do sofa
frame(527)
r = root_world(); _, F, L = axes()
for side in (1, -1): foot(side, 527, Vector((r.x, r.y, FL + 0.08)) + F * 0.42 + L * side * 0.14, F)
frame(531)
for side in (1, -1): foot(side, 531, Vector((r.x, r.y, FL + 0.08)) + F * 0.42 + L * side * 0.14, F)
SEAT_L, SEAT_R = (0.28, 0.20), (0.28, 0.20)
for f in (527, 531, 536):
    frame(f)
    wrist("L", f, body_pt(0.30, -0.18, 0.62), F * 0.6 - UP * 0.4); wrist("R", f, body_pt(0.30, 0.18, 0.62), F * 0.6 - UP * 0.4)
    torso(f, lean=-12 if f > 527 else -4, hpitch=2, htwist=look_at(f, TV, 0.4))

# ---- controle remoto: pega no sofa (535), aponta e desliga a TV (610-614), deixa de lado (627)
remote.location = Vector((-11.90, 2.65, 6.715)); remote.keyframe_insert("location", frame=1)     # mais perto do alcance do Snow
rcc = [c for c in remote.constraints]
for c in rcc: remote.constraints.remove(c)
rc = remote.constraints.new('CHILD_OF'); rc.name = 'NaMao'; rc.target = rig; rc.subtarget = 'DEF-Wrist.R'
rc.inverse_matrix = Matrix.Identity(4); rc.set_inverse_pending = False
drop_keys(remote, ('constraints["NaMao"].influence', "location", "rotation_euler"), 2, 720)
def rinf(f, v):
    rc.influence = v; remote.keyframe_insert('constraints["NaMao"].influence', frame=f)
rinf(1, 0.0); rinf(534, 0.0); rinf(535, 1.0); rinf(626, 1.0); rinf(627, 0.0)
set_interp(remote, ('constraints["NaMao"].influence',), {1, 534, 535, 626, 627}, 'CONSTANT')
def rloc(f, loc, rot):
    remote.location = loc; remote.rotation_euler = rot
    remote.keyframe_insert("location", frame=f); remote.keyframe_insert("rotation_euler", frame=f)
rloc(1, Vector((-11.90, 2.65, 6.715)), (0, 0, 0)); rloc(534, Vector((-11.90, 2.65, 6.715)), (0, 0, 0))
rloc(535, (0, 0.08, 0), (0, 0, 0)); rloc(626, (0, 0.08, 0), (0, 0, 0))

frame(534); P = remote.matrix_world.translation.copy()
wrist("R", 534, body_pt(0.30, 0.18, 0.62), axes()[1]); torso(534, lean=-10, hpitch=8, htwist=look_at(534, P, 0.3))
frame(535); P = Vector((-11.90, 2.65, 6.80)); wrist("R", 535, P, axes()[1]); torso(535, lean=-6, hpitch=12, htwist=0)
hand(534, 0.0, 0.0); hand(535, 0.0, 0.8)
POINT = lambda: body_pt(0.55, 0.20, 1.38)
LAP = lambda: body_pt(0.30, 0.20, 0.82)
for f, fn, hp, ls in ((538, POINT, 6, -10), (541, POINT, 6, -10), (553, LAP, 12, -12), (600, LAP, 12, -14), (604, LAP, 12, -14),
                      (610, POINT, 6, -14), (614, POINT, 6, -14), (620, POINT, 6, -14), (624, LAP, 12, -14)):
    frame(f); wrist("R", f, fn(), axes()[1]); wrist("L", f, body_pt(0.30, -0.18, 0.62), axes()[1] * 0.6 - UP * 0.4)
    torso(f, lean=ls, hpitch=hp, htwist=look_at(f, TV if fn is POINT else body_pt(0.4, 0.2, 0.7), 0.4))
# solta o controle no sofa ao lado: a mao pousa e o controle fica ali
frame(627); wrist("R", 627, body_pt(0.12, 0.42, 0.62), axes()[1])
Prem = (rig.matrix_world @ pb["DEF-Wrist.R"].head).copy()
rloc(627, Prem, (0, 0, math.radians(25))); rloc(720, Prem, (0, 0, math.radians(25)))
wrist("L", 627, body_pt(0.30, -0.18, 0.62), axes()[1] * 0.6 - UP * 0.4); torso(627, lean=-14, hpitch=12, htwist=0)
hand(538, 0.0, 0.8); hand(541, 0.0, 0.8); hand(553, 0.0, 0.8); hand(600, 0.0, 0.8); hand(610, 0.0, 0.8); hand(626, 0.0, 0.8); hand(628, 0.0, 0.0)

# ---- 628-720: fecha os olhos, suspira e dorme (cabeca cai para frente e para o lado)
for f, ls, hp, tw in ((640, -16, 12, 0), (668, -18, 6, 0), (684, -15, 14, 0), (702, -12, 28, 12), (720, -12, 30, 14)):
    frame(f)
    wrist("R", f, body_pt(0.12, 0.42, 0.62), axes()[1]); wrist("L", f, body_pt(0.30, -0.18, 0.62), axes()[1] * 0.6 - UP * 0.4)
    torso(f, lean=ls, hpitch=hp, htwist=tw)

# ---- pes no fim e rosto
frame(720)
for side in (1, -1): foot(side, 720, Vector((r.x, r.y, FL + 0.08)) + F * 0.42 + L * side * 0.14, F)
E0 = {"Sad": 0.5}; M0 = {"Compressed": 0.5}
face(493, E0, M0); face(505, E0, M0); blink(499, E0, M0, 6)
face(527, E0, M0); face(536, {"Sad": 0.4}, {"Compressed": 0.3}); blink(532, {"Sad": 0.4}, {"Compressed": 0.3}, 8)
face(600, {"Sad": 0.4}, {"Compressed": 0.3}); blink(567, {"Sad": 0.4}, {"Compressed": 0.3}, 10); blink(591, {"Sad": 0.4}, {"Compressed": 0.3}, 10)
face(628, {"Sad": 0.7}, {"Compressed": 0.6}); face(640, {"Sad": 0.7}, {"Compressed": 0.6})
face(660, {"Sad": 0.7, "Closed": 1.0}, {"Compressed": 0.6})
face(670, {"Sad": 0.7, "Closed": 1.0}, {"Openfrown": 0.6}); face(674, {"Sad": 0.7, "Closed": 1.0}, {"Openfrown": 0.6})
face(684, {"Sad": 0.3, "Closed": 1.0}, {"Compressed": 0.2}); face(720, {"Sad": 0.3, "Closed": 1.0}, {"Compressed": 0.2})

smooth_new()
print("SNOWAPTO ok; chaves:", sum(len(fc.keyframe_points) for fc in fcurves()))
finish()
