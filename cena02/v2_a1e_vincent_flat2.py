import bpy
for name, col in (("vincent_hair", (0.29, 0.09, 0.06, 1)), ("vincent_skin", (0.66, 0.42, 0.34, 1))):
    m = bpy.data.materials[name]; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    p = nt.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = col; p.inputs['Roughness'].default_value = 0.6
    nt.links.new(p.outputs[0], out.inputs['Surface'])
    print("FLAT2", name)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
