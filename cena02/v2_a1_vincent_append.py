# Etapa 1 (Vincent): anexa o Vincent (Blender Studio, CC) ao cena02_v2.blend no lugar do Miguel.
# Uso: blender -b cena02_v2.blend --python cena02/v2_a1_vincent_append.py
# Nao apaga o Miguel antigo: so esconde (CHAR_Miguel fica na cena para backup).
import bpy, os, math

import os
_MODELOS = os.environ.get("ANIM3D_MODELOS", os.path.join(os.path.expanduser("~"), "Downloads"))   # pasta dos .blend baixados do Blender Studio
VINCENT = os.path.join(_MODELOS, *"vincent.blend".split("/"))
OUT = bpy.data.filepath
MIGUEL_POS = (10.0, 7.04, 0.0)

if "CHAR_Vincent" in bpy.data.collections:
    raise SystemExit("Vincent ja foi anexado; abortando para nao duplicar.")

with bpy.data.libraries.load(VINCENT, link=False) as (src, dst):
    dst.collections = [c for c in ("CH-Vincent.high", "Rig Extra Objects") if c in src.collections]

sc = bpy.context.scene
holder = bpy.data.collections.new("CHAR_Vincent")
sc.collection.children.link(holder)
for c in dst.collections:
    holder.children.link(c)

# raiz unica: move o personagem inteiro (malhas nao sao filhas do rig)
root = bpy.data.objects.new("ROOT_Vincent", None)
root.empty_display_type = 'ARROWS'
root.empty_display_size = 0.5
holder.objects.link(root)

allobjs = set()
for c in dst.collections:
    for o in c.all_objects:
        allobjs.add(o)
for o in allobjs:
    if o.parent is None or o.parent not in allobjs:
        o.parent = root
        o.matrix_parent_inverse.identity()
    if o.type == 'LATTICE':
        o.hide_set(True)

root.location = MIGUEL_POS
root.rotation_euler = (0, 0, 0)   # Miguel antigo: rot 0, de frente para -Y (Claudio)

# esconde o Miguel antigo (backup mantido)
old = bpy.data.collections.get("CHAR_Miguel")
if old:
    old.hide_viewport = True
    old.hide_render = True

rig = bpy.data.objects["RIG-Vincent"]
print("OK", rig.name, len(rig.data.bones), "objs", len(allobjs))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
