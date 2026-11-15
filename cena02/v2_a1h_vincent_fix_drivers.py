# Corrige caminhos de drivers do BlenRig incompativeis com o Blender 5.x: 'pose.bones["x"].["prop"]' -> 'pose.bones["x"]["prop"]'.
# Sem isso os drivers de influencia FK/IK/hinge nao avaliam e o FK dos bracos fica preso no IK.
import bpy
rig = bpy.data.objects["RIG-Vincent"]
n = 0
for d in rig.animation_data.drivers:
    for v in d.driver.variables:
        for t in v.targets:
            if t.data_path and '].["' in t.data_path:
                t.data_path = t.data_path.replace('].["', ']["'); n += 1
print("FIXDRV patched", n)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
