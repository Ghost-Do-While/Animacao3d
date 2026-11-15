# Torna os materiais do Vincent compativeis com Eevee: troca Anisotropic BSDF (so Cycles) por Principled.
import bpy
n_rep = 0
for m in bpy.data.materials:
    if not m.name.startswith("vincent") or not m.use_nodes:
        continue
    trees = [m.node_tree] + [n.node_tree for n in m.node_tree.nodes if n.type == 'GROUP' and n.node_tree]
    for nt in trees:
        for n in list(nt.nodes):
            if n.bl_idname != 'ShaderNodeBsdfAnisotropic':
                continue
            p = nt.nodes.new('ShaderNodeBsdfPrincipled')
            p.location = n.location
            for src, dst in (("Color", "Base Color"), ("Roughness", "Roughness"), ("Normal", "Normal")):
                if src in n.inputs and dst in p.inputs:
                    p.inputs[dst].default_value = n.inputs[src].default_value if hasattr(n.inputs[src], "default_value") and dst != "Normal" else p.inputs[dst].default_value
                    for l in list(n.inputs[src].links):
                        nt.links.new(l.from_socket, p.inputs[dst])
            if "Metallic" in n.inputs:
                p.inputs["Metallic"].default_value = n.inputs["Metallic"].default_value if hasattr(n.inputs["Metallic"], "default_value") else 0.0
            for l in list(n.outputs[0].links):
                nt.links.new(p.outputs[0], l.to_socket)
            nt.nodes.remove(n); n_rep += 1
print("EEVEE_FIX replaced", n_rep)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
