# Reduz o brilho (reflexo) dos olhos do Snow: com a luz forte da TV a corea refletia branco e escondia a iris. Rodar com -S Scene.
import bpy
rig = bpy.data.objects["RIG-Snow"]
p = rig.pose.bones["Properties_Character_Snow"]
before = p["Eye Highlight Strength"]
p["Eye Highlight Strength"] = 0.25
print("SNOWEYES", before, "->", p["Eye Highlight Strength"])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
