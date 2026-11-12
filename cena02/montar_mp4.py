# Junta a sequência PNG em MP4 (H.264) pelo Video Sequencer. Uso:
#   blender -b cena02.blend --python cena02/montar_mp4.py
import bpy, os
d = bpy.path.abspath('//render/previa/')
files = sorted(f for f in os.listdir(d) if f.endswith('.png') and os.path.getsize(os.path.join(d, f)) > 0)
sc = bpy.data.scenes.new('MONTAGEM')
sc.render.fps = 24
sc.frame_start = 1
sc.frame_end = len(files)
sc.render.resolution_x = 960
sc.render.resolution_y = 540
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'Standard'  # PNGs já estão com AgX aplicado
se = sc.sequence_editor_create()
coll = se.strips if hasattr(se, 'strips') else se.sequences
st = coll.new_image(name='previa', filepath=os.path.join(d, files[0]), channel=1, frame_start=1)
for f in files[1:]:
    st.elements.append(f)
im = sc.render.image_settings
try:
    im.media_type = 'VIDEO'
except Exception:
    pass
im.file_format = 'FFMPEG'
ff = sc.render.ffmpeg
ff.format = 'MPEG4'
ff.codec = 'H264'
ff.constant_rate_factor = 'HIGH'
sc.render.use_sequencer = True
sc.render.filepath = '//render/cena02_previa.mp4'
sc.render.use_file_extension = False
bpy.ops.render.render(animation=True, scene=sc.name)
print('MP4 OK:', bpy.path.abspath(sc.render.filepath), len(files), 'frames')
