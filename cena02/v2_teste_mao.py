# Teste: rolamento (twist) das maos do Vincent na pose "maos na cabeca" (frame 360). Renderiza 4 variantes com camera de teste.
# Uso: blender -b cena02_v2.blend -S Scene --python cena02/v2_teste_mao.py -- OUTDIR
import bpy, sys, os, math
from mathutils import Matrix, Vector
out = sys.argv[sys.argv.index("--") + 1]
sc = bpy.context.scene; r = bpy.data.objects["RIG-Vincent"]; pb = r.pose.bones
sc.render.resolution_percentage = 50; sc.eevee.taa_render_samples = 16
for m in list(sc.timeline_markers): sc.timeline_markers.remove(m)
# cena de teste: camera lateral, na altura da cabeca do Vincent
cam = bpy.data.objects.new("TMPCAM", bpy.data.cameras.new("TMPCAM")); sc.collection.objects.link(cam)
cam.location = (12.2, 7.0, 2.0); cam.data.lens = 70
tgt = bpy.data.objects.new("TMPTGT", None); tgt.location = (10.0, 7.0, 1.85); sc.collection.objects.link(tgt)
tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
cam2 = bpy.data.objects.new("TMPCAM2", bpy.data.cameras.new("TMPCAM2")); sc.collection.objects.link(cam2)
cam2.location = (10.0, 3.2, 2.3); cam2.data.lens = 70
tc2 = cam2.constraints.new('TRACK_TO'); tc2.target = tgt; tc2.track_axis = 'TRACK_NEGATIVE_Z'; tc2.up_axis = 'UP_Y'
sc.frame_set(360)
for ang in (0, 60, -60, 110):
    sc.frame_set(360); bpy.context.view_layer.update()
    for side, nm in ((1, "L"), (-1, "R")):
        b = pb[f"hand_fk_{nm}"]; M = b.matrix.copy()
        b.matrix = M @ Matrix.Rotation(math.radians(ang * side), 4, 'Y'); bpy.context.view_layer.update()
    for ci, c in enumerate((cam, cam2)):
        sc.camera = c; sc.render.filepath = os.path.join(out, f"tw{ang:+04d}_c{ci}.png"); bpy.ops.render.render(write_still=True)
    print("TESTE", ang)
