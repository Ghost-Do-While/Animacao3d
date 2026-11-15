# Anexa o Snow (Blender Studio, CC-BY) no lugar do Marcos. O RIG_Marcos antigo continua na cena (sem malhas visiveis)
# porque carrega o movimento de raiz (Child Of no carro, caminhada, sofa); o Snow segue essa raiz via ROOT_Snow.
import bpy, math
import os
_MODELOS = os.environ.get("ANIM3D_MODELOS", os.path.join(os.path.expanduser("~"), "Downloads"))   # pasta dos .blend baixados do Blender Studio
SNOW = os.path.join(_MODELOS, *"Snow_v4.2/Snow/snow_v4.2.blend".split("/"))
if "CHAR_Snow" in bpy.data.collections: raise SystemExit("Snow ja anexado")
with bpy.data.libraries.load(SNOW, link=False) as (src, dst):
    dst.collections = ["CH-snow"]
sc = bpy.context.scene
holder = bpy.data.collections.new("CHAR_Snow"); sc.collection.children.link(holder)
for c in dst.collections: holder.children.link(c)
rm = bpy.data.objects["RIG_Marcos"]
root = bpy.data.objects.new("ROOT_Snow", None); root.empty_display_type = 'ARROWS'; root.empty_display_size = 0.5
holder.objects.link(root)
cl = root.constraints.new('COPY_LOCATION'); cl.target = rm
cr = root.constraints.new('COPY_ROTATION'); cr.target = rm
off = bpy.data.objects.new("ROOT_Snow_Off", None); off.empty_display_type = 'PLAIN_AXES'; off.empty_display_size = 0.2
holder.objects.link(off); off.parent = root
allobjs = set()
for c in dst.collections: allobjs.update(c.all_objects)
for o in allobjs:
    if o.parent is None or o.parent not in allobjs:
        o.parent = off; o.matrix_parent_inverse.identity()
# esconde as malhas do Marcos antigo (o rig e o movimento de raiz ficam)
for o in bpy.data.collections["CHAR_Marcos"].objects:
    if o.type == 'MESH': o.hide_render = True; o.hide_viewport = True
# limites de GPU e Eevee
for o in allobjs:
    for m in o.modifiers:
        if m.type == 'SUBSURF': m.render_levels = min(m.render_levels, 1)
n = 0
for m in bpy.data.materials:
    if m.name.lower().startswith("snow") and m.use_nodes:
        nt = m.node_tree
        for nd in list(nt.nodes):
            if nd.bl_idname == 'ShaderNodeBsdfAnisotropic':
                p = nt.nodes.new('ShaderNodeBsdfPrincipled'); p.location = nd.location
                for s, d in (("Color", "Base Color"), ("Roughness", "Roughness")):
                    if s in nd.inputs:
                        p.inputs[d].default_value = nd.inputs[s].default_value
                        for l in list(nd.inputs[s].links): nt.links.new(l.from_socket, p.inputs[d])
                for l in list(nd.outputs[0].links): nt.links.new(p.outputs[0], l.to_socket)
                nt.nodes.remove(nd); n += 1
print("SNOW_OK objs", len(allobjs), "aniso", n)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
