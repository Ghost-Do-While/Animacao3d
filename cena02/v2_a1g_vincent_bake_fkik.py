# Os drivers de influencia FK/IK/hinge do BlenRig (expressao "a - b") nao avaliam aqui e deixam a influencia em 1.0
# (o FK fica preso no IK). Congela o resultado: valor = prop(ik/hinge) - reproportion, remove o driver.
import bpy, re
rig = bpy.data.objects["RIG-Vincent"]
arm = rig.data
rep = arm.get("reproportion", 0.0)
pat = re.compile(r'pose\.bones\["([^"]+)"\]\.constraints\["([^"]+)"\]\.influence$')
done = skipped = 0
for d in list(rig.animation_data.drivers):
    m = pat.match(d.data_path)
    if not m: continue
    dr = d.driver
    if dr.expression.replace(" ", "") not in ("var1-var2", "var_1-var_2"): skipped += 1; continue
    vals = []
    ok = True
    for v in dr.variables:
        t = v.targets[0]
        try:
            if t.id is rig:
                p = t.data_path.replace('].["', ']["')
                vals.append(float(rig.path_resolve(p)))
            else:
                vals.append(float(t.id[t.data_path.strip('[]"\'')]))
        except Exception as e:
            ok = False; break
    if not ok or len(vals) != 2: skipped += 1; continue
    inf = max(0.0, min(1.0, vals[0] - vals[1]))
    bone, cname = m.group(1), m.group(2)
    c = rig.pose.bones[bone].constraints[cname]
    rig.animation_data.drivers.remove(d)
    c.influence = inf
    done += 1
print("BAKE done", done, "skipped", skipped)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
