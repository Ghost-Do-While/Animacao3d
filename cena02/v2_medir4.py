import bpy
for m in bpy.data.materials:
    if 'eye' in m.name.lower() and 'snow' in m.name.lower() or m.name.lower().startswith('eyes') or m.name.lower()=='eye':
        print("MAT", m.name, m.use_nodes)
        if m.node_tree:
            for n in m.node_tree.nodes:
                ins = []
                for i in n.inputs:
                    if hasattr(i, 'default_value') and not i.is_linked and i.name in ('Emission Strength','Specular IOR Level','Roughness','Strength','Coat Weight','Emission Color','Base Color','Metallic','Fac','Factor'):
                        try: v = tuple(round(x,2) for x in i.default_value)
                        except TypeError: v = round(i.default_value,3)
                        ins.append((i.name, v))
                print("   ", n.type, n.name, n.label, ins)
for l in bpy.data.objects:
    if l.type == 'LIGHT' and (l.hide_render is False): print("LUZ", l.name, l.data.type, l.data.energy, round(l.location.x), round(l.location.y), round(l.location.z), [ (round(x,1)) for x in l.data.color])
