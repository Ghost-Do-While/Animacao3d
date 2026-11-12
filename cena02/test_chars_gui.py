# Teste visual dos personagens (rodar no Blender GUI via exec). Variáveis: SP (pasta de saída), MODE
import bpy, os, math
from mathutils import Vector, Matrix, Euler
D = bpy.data
BASE = r'C:\Users\43604859808\AppData\Local\Claude-Data\claude_pzs8sxrjxfjjc\scratch-workspaces\85c3f8da-be6c-4596-b90f-1b28f6a9c594\9111420e-37ae-4933-80d4-97f67ffc73cc\scratch-2026-11-09-b51ac8'
bpy.ops.wm.open_mainfile(filepath=os.path.join(BASE, 'characters.blend'))
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
cam = D.objects.new('TCAM', D.cameras.new('TCAM')); sc.collection.objects.link(cam)
sun = D.objects.new('TSUN', D.lights.new('TSUN', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 3; sun.rotation_euler = (math.radians(50), 0, math.radians(20))
w = D.worlds.new('W'); sc.world = w; w.use_nodes = True
nt = w.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
bg = nt.nodes.new('ShaderNodeBackground'); wo = nt.nodes.new('ShaderNodeOutputWorld'); nt.links.new(bg.outputs[0], wo.inputs[0]); bg.inputs[1].default_value = 0.9
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 60
sc.eevee.taa_render_samples = 16
for n, x in (('Marcos', 0), ('Miguel', 1.3), ('Claudio', -1.3)):
    D.objects[f'RIG_{n}'].location = (x, 0, 0)
sc.camera = cam
def shot(name, loc, tgt, lens=50):
    cam.location = loc; cam.data.lens = lens
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(SP, name); bpy.ops.render.render(write_still=True)
