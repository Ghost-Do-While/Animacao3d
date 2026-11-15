# Render de teste com camera temporaria (nao salva). Uso: blender -b arq.blend -S Scene --python v2_render_temp_cam.py -- OUT PCT frame cx cy cz tx ty tz lens
import bpy, sys, os
a = sys.argv[sys.argv.index("--")+1:]
out, pct, fr = a[0], int(a[1]), int(a[2]); c = [float(x) for x in a[3:6]]; t = [float(x) for x in a[6:9]]; lens = float(a[9])
sc = bpy.context.scene; sc.render.resolution_percentage = pct; sc.eevee.taa_render_samples = 16
# coordenadas RELATIVAS ao volante do carro do Marcos naquele frame
sc.frame_set(fr); bpy.context.view_layer.update()
wp = bpy.data.objects["VEH_CarroMarcos_Volante"].matrix_world.translation
c = [wp.x + c[0], wp.y + c[1], wp.z + c[2]]; t = [wp.x + t[0], wp.y + t[1], wp.z + t[2]]
cam = bpy.data.objects.new("TMPCAM", bpy.data.cameras.new("TMPCAM")); sc.collection.objects.link(cam)
cam.location = c; cam.data.lens = lens
tgt = bpy.data.objects.new("TMPTGT", None); tgt.location = t; sc.collection.objects.link(tgt)
tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
for m in list(sc.timeline_markers): sc.timeline_markers.remove(m)   # marcadores trocam a camera sozinhos
sc.frame_set(fr); sc.camera = cam
sc.render.filepath = os.path.join(out, f"tmp_f{fr:04d}.png"); bpy.ops.render.render(write_still=True); print("RENDERED", sc.render.filepath)
