# Reconstrói a Cena 02 inteira do zero (apaga tudo da cena atual!) e salva cena02.blend.
# Pré-requisito: characters.blend (blender -b --factory-startup --python cena02/build_chars.py -- characters.blend)
# Uso (no Blender, Text Editor, Alt+P) com o .blend dentro da pasta do projeto:
#   exec(open(r'<pasta>/cena02/run.py', encoding='utf-8').read())
import os, bpy
BASE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else globals().get('BASE')
PARTS = ['lib.py', 'p0_setup.py', 'p1_maquete.py', 'p1b_rua.py', 'p1c_apto.py', 'p2_veiculos.py', 'p3_chars.py',
         'p4_anim.py', 'p5_cams.py', 'p6_lights_comp.py', 'p7_telejornal.py']
def build(only=None, save=True):
    g = {'__name__': 'cena02', 'BASE': BASE}
    for p in PARTS:
        if only and p not in only: continue
        fp = os.path.join(BASE, p)
        exec(compile(open(fp, encoding='utf-8').read(), fp, 'exec'), g)
    if save:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(BASE), 'cena02.blend'))
    return g
