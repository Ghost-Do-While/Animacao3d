# Prévia rápida (50%, 16 amostras) como sequência PNG retomável. Uso:
#   blender -b cena02.blend --python cena02/render_preview.py
# Se travar/for interrompido, rode de novo: frames já prontos são pulados.
import bpy
s = bpy.context.scene
s.render.resolution_percentage = 50
s.eevee.taa_render_samples = 16
s.eevee.volumetric_tile_size = '16'  # névoa mais leve na prévia
im = s.render.image_settings
im.file_format = 'PNG'
im.color_depth = '8'
im.color_mode = 'RGB'
s.render.use_overwrite = False
s.render.use_placeholder = True
s.render.filepath = '//render/previa/f_'
bpy.ops.render.render(animation=True)
