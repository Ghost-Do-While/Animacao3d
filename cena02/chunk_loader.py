# Etapa 4 - CHUNK LOADER: so renderiza o que a camera ativa enxerga (+ margem) ou o que esta perto dela.
#
# Chunks logicos = as colecoes do projeto (portaria/maquete, rua/entorno, apartamento, veiculos, personagens).
# A cada frame (render_pre / frame_change_post) cada objeto "culavel" e ligado/desligado em hide_render:
#   fica LIGADO se: esta a menos de RAIO da camera (garante sombras/reflexos proximos), ou algum canto da sua caixa
#   (bounding box) entra no quadro da camera ampliado pela MARGEM (evita "pop-in"), ou a caixa atravessa o quadro.
#   fica DESLIGADO caso contrario. Luzes, cameras, rigs e objetos ja escondidos no .blend nunca sao tocados.
# Parametros (Scene > Custom Properties, editaveis na interface; valores padrao criados por ensure_props()):
#   chunk_enabled (0/1), chunk_margin (fracao do quadro, padrao 0.35), chunk_radius_env (m, 14), chunk_radius_char (m, 18),
#   chunk_cull_chars (0/1)
# Uso em Blender de fundo:  --python cena02/render_setup.py   com a variavel de ambiente ANIM3D_CHUNK=1
# Uso na interface: Text Editor > abrir este arquivo > Run Script (instala os handlers), ou chunk_loader.install()
import bpy, time
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

DEFAULTS = {"chunk_enabled": 1, "chunk_margin": 0.35, "chunk_radius_env": 14.0, "chunk_radius_char": 18.0, "chunk_cull_chars": 1}
ENV_COLLS = ("MAQUETE_Condominio", "ENV_Rua_Entorno", "ENV_Apartamento", "VEHICLES_Animados")
CHAR_COLLS = ("CHAR_Vincent", "CHAR_Rex", "CHAR_Snow", "CHAR_Miguel", "CHAR_Marcos", "CHAR_Claudio")
CULL_TYPES = {'MESH', 'CURVE', 'FONT', 'SURFACE'}
last_stats = {}

def ensure_props(sc):
    for k, v in DEFAULTS.items():
        if k not in sc: sc[k] = v
    return sc

def camera_for_frame(sc, f):
    """camera ativa no frame f segundo os marcadores (nao depende de a cena ja ter trocado de camera)"""
    best = None
    for m in sc.timeline_markers:
        if m.camera and m.frame <= f and (best is None or m.frame >= best.frame): best = m
    return best.camera if best else sc.camera

def _kind_map():
    kind = {}
    for cn in ENV_COLLS:
        c = bpy.data.collections.get(cn)
        if c:
            for o in c.all_objects: kind[o] = 'env'
    for cn in CHAR_COLLS:
        c = bpy.data.collections.get(cn)
        if c:
            for o in c.all_objects: kind[o] = 'char'
    return kind

def restore(sc=None):
    n = 0
    for o in bpy.data.objects:
        if "_cl_base" in o:
            o.hide_render = bool(o["_cl_base"]); del o["_cl_base"]; n += 1
    return n

def apply(sc=None, frame=None):
    """liga/desliga os objetos para o frame atual. Retorna estatisticas."""
    global last_stats
    sc = sc or bpy.context.scene
    ensure_props(sc)
    if not sc["chunk_enabled"]:
        restore(sc); last_stats = {"enabled": False}; return last_stats
    f = sc.frame_current if frame is None else frame
    cam = camera_for_frame(sc, f)
    if cam is None: return {}
    t0 = time.time()
    cloc = cam.matrix_world.translation
    margin = float(sc["chunk_margin"]); r_env = float(sc["chunk_radius_env"]); r_chr = float(sc["chunk_radius_char"]); cull_chars = int(sc["chunk_cull_chars"])
    kind = _kind_map()
    total = culled = 0
    for o in sc.objects:
        k = kind.get(o)
        if k is None or o.type not in CULL_TYPES: continue
        if "_cl_base" not in o: o["_cl_base"] = 1 if o.hide_render else 0       # guarda o estado original uma unica vez
        if o["_cl_base"]: continue                                                  # ja escondido no arquivo: nao mexe
        if k == 'char' and not cull_chars:
            o.hide_render = False; continue
        total += 1
        mw = o.matrix_world
        corners = [mw @ Vector(c) for c in o.bound_box]
        center = sum(corners, Vector()) / 8.0
        keep = (center - cloc).length < (r_chr if k == 'char' else r_env)
        if not keep:
            vs = [world_to_camera_view(sc, cam, c) for c in corners]
            if any(v.z > 0 and -margin <= v.x <= 1 + margin and -margin <= v.y <= 1 + margin for v in vs): keep = True      # canto no quadro
            elif not (all(v.x < -margin for v in vs) or all(v.x > 1 + margin for v in vs) or all(v.y < -margin for v in vs)
                      or all(v.y > 1 + margin for v in vs) or all(v.z <= 0 for v in vs)): keep = True                          # atravessa o quadro
        o.hide_render = not keep
        if not keep: culled += 1
    last_stats = {"enabled": True, "frame": f, "camera": cam.name, "eligible": total, "culled": culled, "kept": total - culled,
                  "ms": round((time.time() - t0) * 1000)}
    return last_stats

def _handler(*args):
    sc = bpy.context.scene
    if sc and sc.name in ("Scene",): apply(sc)

def install():
    uninstall()
    bpy.app.handlers.render_pre.append(_handler)
    bpy.app.handlers.frame_change_post.append(_handler)

def uninstall():
    for lst in (bpy.app.handlers.render_pre, bpy.app.handlers.frame_change_post):
        for h in list(lst):
            if getattr(h, "__name__", "") == "_handler": lst.remove(h)

if __name__ == "__main__":
    install(); print("chunk_loader instalado:", apply())
