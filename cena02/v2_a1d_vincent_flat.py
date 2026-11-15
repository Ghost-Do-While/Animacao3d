# Eevee: materiais do Vincent simples (Principled com a cor base original) - os shaders originais sao feitos para Cycles.
import bpy
SKIP = ("vincent_cornea", "vincent_glasses_glass", "vincent_eyeball", "vincent_iris", "vincent_pupil", "vincent_teeth")
def fix(m):
    if not m.name.startswith("vincent") or not m.use_nodes or m.name.startswith(SKIP): return
    nt = m.node_tree
    dif = [n for n in nt.nodes if n.type == 'BSDF_DIFFUSE']
    col = tuple(dif[0].inputs['Color'].default_value) if dif else (0.5, 0.5, 0.5, 1)
    tex = None
    if dif and dif[0].inputs['Color'].links and dif[0].inputs['Color'].links[0].from_node.type == 'TEX_IMAGE':
        tex = dif[0].inputs['Color'].links[0].from_node
    for n in list(nt.nodes):
        if n is not tex and n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    p = nt.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = col
    p.inputs['Roughness'].default_value = 0.6
    if tex and m.name == "vincent_hair": nt.links.new(tex.outputs['Color'], p.inputs['Base Color'])
    elif tex: nt.nodes.remove(tex)
    nt.links.new(p.outputs[0], out.inputs['Surface'])
    print("FLAT", m.name, [round(x, 2) for x in col])
for m in list(bpy.data.materials):
    try: fix(m)
    except Exception as e: print('FLAT_ERR', m.name, repr(e))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
