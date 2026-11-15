# Verificacao automatica do projeto v2 (nao altera o arquivo). Uso: blender -b cena02_v2.blend -S Scene --python cena02/v2_verify.py
# Imprime linhas "CHK <OK|AVISO|ERRO> <area> <mensagem>" e grava render/verificacao_v2.txt
import bpy, os, math, re
from mathutils import Vector

sc = bpy.context.scene
assert sc.name == "Scene"
ROOT = os.path.dirname(os.path.dirname(bpy.data.filepath)) if False else os.path.dirname(bpy.data.filepath)
OUT = []
def R(level, area, msg):
    line = f"CHK {level} {area} {msg}"; print(line); OUT.append(line)

# ------------------------------------------------------------------ A. arquivos e caminhos
miss = []
big = 0
for im in bpy.data.images:
    if im.source in ('FILE', 'SEQUENCE', 'TILED') and not im.packed_file and im.filepath:
        p = bpy.path.abspath(im.filepath)
        if im.source == 'TILED':
            ok = all(os.path.exists(p.replace("<UDIM>", str(t.number))) for t in im.tiles)
        elif im.source == 'SEQUENCE':
            ok = os.path.exists(p)
        else:
            ok = os.path.exists(p)
        if not ok: miss.append(im.name)
    if im.size[0] * im.size[1]: big += im.size[0] * im.size[1] * 4
R("OK" if not miss else "ERRO", "arquivos", "texturas/imagens com arquivo faltando: %s" % (miss if miss else "nenhuma"))
R("OK" if big / 1048576 < 400 else "AVISO", "gpu", "memoria total de imagens carregadas: %.0f MB (Radeon integrada: 512 MB dedicados)" % (big / 1048576))
tvd = os.path.join(os.path.dirname(bpy.data.filepath), "render", "telejornal")
tv = [n for n in range(1, 104) if os.path.exists(os.path.join(tvd, "tv_%04d.png" % n))]
R("OK" if len(tv) == 103 else "ERRO", "telejornal", "PNG da TV do apartamento: %d/103 em render/telejornal" % len(tv))
bad_paths = []
for attr in ("images", "libraries", "texts", "sounds", "fonts", "movieclips"):
    for idb in getattr(bpy.data, attr):
        for prop in ("filepath", "filepath_raw"):
            v = getattr(idb, prop, None)
            if isinstance(v, str) and ("Joao" in v or re.match(r"^[A-Za-z]:\\Users\\", v)): bad_paths.append((attr, idb.name, v[:60]))
wk = sum(1 for i in bpy.data.user_map().keys() if getattr(i, "library_weak_reference", None) is not None and i.library_weak_reference.filepath and "Joao" in i.library_weak_reference.filepath)
R("OK" if not bad_paths and wk == 0 else "ERRO", "privacidade", "caminhos com o nome do usuario no .blend: %d (+%d referencias internas)" % (len(bad_paths), wk))

# ------------------------------------------------------------------ B. timeline, render, cameras
R("OK" if (sc.render.fps, sc.frame_start, sc.frame_end) == (24, 1, 720) else "ERRO", "timeline", f"fps={sc.render.fps}, frames {sc.frame_start}-{sc.frame_end}, {sc.render.resolution_x}x{sc.render.resolution_y}@{sc.render.resolution_percentage}%, motor {sc.render.engine}, amostras {sc.eevee.taa_render_samples}")
mk = sorted((m.frame, m.camera.name if m.camera else None) for m in sc.timeline_markers)
exp = [1, 73, 145, 205, 253, 289, 397, 493, 541, 601]
R("OK" if [m[0] for m in mk] == exp and all(m[1] for m in mk) else "ERRO", "cameras", "marcadores de camera: %s" % mk)
R("AVISO", "cameras", "enquadramento multi-formato 16:9 + 9:16 (Etapa 5) ainda NAO feito: cameras so em 1920x1080")

# ------------------------------------------------------------------ C. personagens e animacao
def chans(a): return list(a.fcurves) if hasattr(a, "fcurves") else [fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
for nm in ("RIG-Vincent", "RIG-rex", "RIG-Snow"):
    o = bpy.data.objects[nm]; a = o.animation_data.action if o.animation_data else None
    if not a: R("ERRO", nm, "sem animacao"); continue
    fr = a.frame_range; n = sum(len(fc.keyframe_points) for fc in chans(a))
    R("OK" if n > 500 else "ERRO", nm, f"acao '{a.name}': {n} chaves, frames {fr[0]:.0f}-{fr[1]:.0f}")
vic = bpy.data.objects["RIG-Victoria"]; a = vic.animation_data.action
R("OK", "RIG-Victoria", f"acao '{a.name}': frames {a.frame_range[0]:.0f}-{a.frame_range[1]:.0f} (telejornal, cena SCN_Telejornal)")
for cn in ("CHAR_Miguel", "CHAR_Claudio"):
    c = bpy.data.collections[cn]; R("OK" if c.hide_render else "ERRO", cn, "personagem antigo escondido no render" if c.hide_render else "ainda visivel no render!")
vis_old = [o.name for o in bpy.data.collections["CHAR_Marcos"].objects if o.type == 'MESH' and not o.hide_render]
R("OK" if not vis_old else "ERRO", "CHAR_Marcos", "malhas do Marcos antigo visiveis no render: %s" % (vis_old or "nenhuma"))
hi = [(o.name, m.render_levels) for o in bpy.data.objects if o.name.startswith(("GEO-snow", "GEO-rex", "GEO-vincent", "GEO-victoria")) for m in o.modifiers if m.type == 'SUBSURF' and m.render_levels > 1]
R("OK" if not hi else "AVISO", "gpu", "Subsurf de render > 1 nos personagens novos: %s" % (hi[:3] or "nenhum"))
R("OK" if all(abs(v) < 1e5 and v == v for o in bpy.data.objects for v in o.location) else "ERRO", "objetos", "sem posicoes invalidas (NaN/infinito)")

# ------------------------------------------------------------------ D. bracos cruzados (regra do usuario) em amostras de 6 em 6 frames
def axes(rig):
    R3 = rig.matrix_world.to_3x3(); return (R3 @ Vector((0, -1, 0))).normalized(), (R3 @ Vector((1, 0, 0))).normalized()
WR = {"RIG-Snow": ("DEF-Wrist.L", "DEF-Wrist.R"), "RIG-rex": ("DEF-Wrist.L", "DEF-Wrist.R"), "RIG-Vincent": ("hand_def_L", "hand_def_R")}
cross = {k: [] for k in WR}
samples = list(range(1, 721, 6))
foot_log = {}
PEL = {"RIG-Snow": "FK-Spine", "RIG-rex": "FK-Spine", "RIG-Vincent": "spine_1_fk"}
wrist_pos = {}
for f in samples:
    sc.frame_set(f); bpy.context.view_layer.update()
    for rn, (wl, wr) in WR.items():
        rig = bpy.data.objects[rn]; pb = rig.pose.bones
        if wl not in pb or wr not in pb or PEL[rn] not in pb: continue
        F, L = axes(rig); mw = rig.matrix_world
        mid = mw @ pb[PEL[rn]].head
        xl = ((mw @ pb[wl].head) - mid).dot(L); xr = ((mw @ pb[wr].head) - mid).dot(L)
        if xl < -0.03 or xr > 0.03: cross[rn].append((f, round(xl, 2), round(xr, 2)))
for rn, lst in cross.items():
    R("OK" if not lst else "AVISO", "bracos", f"{rn}: maos cruzam a linha do corpo em {len(lst)} de {len(samples)} amostras {lst[:6]}")

# ------------------------------------------------------------------ E. Snow: pes (deslize/flutuacao), porta, chave, controle
snow = bpy.data.objects["RIG-Snow"]; pbs = snow.pose.bones
def footpos(f, nm):
    sc.frame_set(f); bpy.context.view_layer.update(); return snow.matrix_world @ pbs[nm].head
GROUND = {247: 0.0, 493: 6.2}
for lo, hi_, gz, label in ((253, 260, 0.0, "caminhada plano 05"), (493, 497, 6.2, "entrada no apartamento"), (510, 521, 6.2, "caminhada ate o sofa"), (524, 531, 6.2, "sentar no sofa")):
    drag = []; zmin = 9; zmax = -9; swing = 0.0
    prev = {nm: footpos(lo, nm) for nm in ("DEF-Foot.L", "DEF-Foot.R")}
    for f in range(lo + 1, hi_ + 1):
        for nm in ("DEF-Foot.L", "DEF-Foot.R"):
            p = footpos(f, nm); z = p.z - gz; zmin = min(zmin, z); zmax = max(zmax, z)
            v = math.hypot(p.x - prev[nm].x, p.y - prev[nm].y)
            if prev[nm].z - gz < 0.105 and z < 0.105:      # pe no chao nos dois frames
                if 0.02 < v < 0.30: drag.append((f, nm[-1], round(v, 2)))     # arrasto lento = deslize de verdade (passo rapido e > 0.30)
            swing = max(swing, v); prev[nm] = p
    R("OK" if not drag else "AVISO", "pes", f"{label} (frames {lo}-{hi_}): frames com deslize lento no chao: {len(drag)} {drag[:4]}; passo mais rapido {swing:.2f} m/frame; altura do tornozelo {zmin:.2f}..{zmax:.2f} m")
# porta do apartamento: mao esquerda na macaneta
h = bpy.data.objects["ENV_Apartamento_Porta_Macaneta"]
dd = []
for f in (493, 494, 495, 500, 502, 504, 505):
    sc.frame_set(f); bpy.context.view_layer.update()
    dd.append((f, round((snow.matrix_world @ pbs["DEF-Wrist.L"].head - h.matrix_world.translation).length, 2)))
R("OK" if max(d for _, d in dd) < 0.12 else "AVISO", "porta", "distancia mao esquerda-macaneta (m) abrindo/fechando: %s" % dd)
pv = bpy.data.objects["ENV_Apartamento_Porta_Pivo"]
sc.frame_set(492); a0 = pv.rotation_euler.z; sc.frame_set(498); a1 = pv.rotation_euler.z; sc.frame_set(506); a2 = pv.rotation_euler.z
R("OK" if abs(a0) < 0.01 and a1 < -1.2 and abs(a2) < 0.01 else "ERRO", "porta", f"porta fechada(492)={math.degrees(a0):.0f} aberta(498)={math.degrees(a1):.0f} fechada(506)={math.degrees(a2):.0f} graus")
# chave e controle: sem pulo na troca mao -> mundo
def wpos(o, f): sc.frame_set(f); bpy.context.view_layer.update(); return o.matrix_world.translation.copy()
ch = bpy.data.objects["PRP_Chaves"]; rc = bpy.data.objects["PRP_ControleRemoto"]
for obj, fa, fb, label in ((ch, 509, 510, "chave (solta da mao)"), (rc, 534, 535, "controle (pego)"), (rc, 626, 627, "controle (solto)")):
    d = (wpos(obj, fa) - wpos(obj, fb)).length
    R("OK" if d < 0.25 else "AVISO", "props", f"{label}: salto entre frames {fa}->{fb} = {d:.2f} m")
k517 = wpos(ch, 517); R("OK" if (k517 - Vector((-15.15, 5.4, 7.005))).length < 0.05 else "ERRO", "props", f"chave pousa na mesa lateral (517): {[round(x, 2) for x in k517]}")
hand535 = snow.matrix_world @ pbs["DEF-Wrist.R"].head; sc.frame_set(535); bpy.context.view_layer.update()
dd = (snow.matrix_world @ pbs["DEF-Wrist.R"].head - rc.matrix_world.translation).length
R("OK" if dd < 0.2 else "AVISO", "props", f"controle junto da mao direita no frame 535: {dd:.2f} m")
sc.frame_set(1)

with open(os.path.join(os.path.dirname(bpy.data.filepath), "render", "verificacao_v2.txt"), "w", encoding="utf8") as fh: fh.write("\n".join(OUT) + "\n")
print("CHK FIM", sum(1 for l in OUT if " OK " in l), "ok;", sum(1 for l in OUT if " AVISO " in l), "avisos;", sum(1 for l in OUT if " ERRO " in l), "erros")
