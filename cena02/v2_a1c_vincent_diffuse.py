# Eevee: liga a saida do material direto ao Diffuse BSDF (cor base) dos materiais vincent_* que sao mix Diffuse+Anisotropic.
import bpy
for m in bpy.data.materials:
    if not m.name.startswith("vincent") or not m.use_nodes: continue
    nt = m.node_tree
    out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output), None)
    dif = [n for n in nt.nodes if n.type == 'BSDF_DIFFUSE']
    if not out or not dif or m.name.startswith(("vincent_cornea","vincent_glasses_glass","vincent_eyeball")): continue
    d = dif[0]
    nt.links.new(d.outputs[0], out.inputs['Surface'])
    print("DIFF", m.name, [round(x,2) for x in d.inputs['Color'].default_value], [l.from_node.bl_idname for l in d.inputs['Color'].links])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
