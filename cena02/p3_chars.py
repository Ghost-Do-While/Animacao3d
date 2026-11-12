# Parte 3 - Personagens: anexa characters.blend (gerado por build_chars.py em Blender de fundo, com Rigify limpo)
# Cada personagem: CHAR_<nome> contendo RIG_<nome> (Rigify), MESH_<nome>_*_PLACEHOLDER, SLOT_<nome> e FACE_<nome> (controle de expressões).
CHARS_FILE = os.path.join(os.path.dirname(BASE), 'characters.blend')
if not os.path.exists(CHARS_FILE):
    raise RuntimeError('characters.blend não encontrado: rode build_chars.py (blender -b --factory-startup --python cena02/build_chars.py -- characters.blend)')
with D.libraries.load(CHARS_FILE, link=False) as (src, dst):
    dst.collections = [n for n in src.collections]
sc_ = bpy.context.scene
CHARS = {}
for c_ in dst.collections:
    if c_ is None: continue
    if c_.name.startswith('CHAR_'):
        sc_.collection.children.link(c_)
    else:
        c_.use_fake_user = True          # WGTS_* (formas dos controles do Rigify) ficam fora da cena
for N in ('Marcos', 'Miguel', 'Claudio'):
    CHARS[N] = dict(rig=D.objects[f'RIG_{N}'], face=D.objects[f'FACE_{N}'], mesh=D.objects[f'MESH_{N}_ROSTO_PLACEHOLDER'])
    rig = CHARS[N]['rig']; rig.rotation_mode = 'XYZ'
# prop de mão: chaves e controle ficam presos a osso de mão (hand_fk), nunca ao mesh -> criados em p4_anim

# Texto interno: como substituir os placeholders por modelos baixados da Blender Community
LEIA = D.texts.new('LEIA-ME_SUBSTITUIR')
LEIA.write('''LEIA-ME_SUBSTITUIR - trocar os personagens provisorios por modelos baixados (Blender Studio, BlenderKit, Mixamo-style rigs...)

ESTRUTURA (por personagem: Marcos, Miguel, Claudio)
  CHAR_<nome>/
    RIG_<nome>                 armature Rigify "Human" (ossos padrao: spine/torso, upper_arm, forearm, hand, f_*, thigh, shin, foot,
                               head, eyes (alvo do olhar), eye.L/R, jaw...), IK/FK por membro (propriedade IK_FK em
                               upper_arm_parent.L/R e thigh_parent.L/R: 0 = IK, 1 = FK; esta cena usa FK = 1)
    MESH_<nome>_CORPO_PLACEHOLDER, _ROUPA_, _CABELO_, _ROSTO_, _OLHO_L/R_, (_GRAVATA_ / _ABAS_JAQUETA_)
                               -> so parentados/skinados ao rig. PODEM SER APAGADOS sem perder a animacao.
    FACE_<nome>                empty de controle das expressoes. Propriedades (A E I O U MBP FV rest blink eyes_closed
                               brow_up brow_down brow_sad brow_angry brow_smug mouth_smile mouth_frown mouth_smirk mouth_shout
                               sigh nostril_flare vein_pop) -> acionam as shape keys do rosto por DRIVER. A animacao esta
                               keyada AQUI. Se o novo modelo tiver shape keys com os mesmos nomes, crie drivers lendo FACE_<nome>["nome"].
    SLOT_<nome>                empty onde o modelo novo deve ser importado (propriedade altura_alvo_m).

ALTURAS-ALVO: Marcos 1,75 m / Miguel 1,80 m / Claudio 1,72 m. Pe no chao em Z = 0, pose-base A estreita.

PASSO A PASSO
  1) Importe o modelo baixado (File > Import) e coloque dentro de CHAR_<nome>; mova-o para o empty SLOT_<nome>.
  2) Escale o modelo ate a altura-alvo (Dimensions Z) e aplique a escala (Ctrl+A > Scale). Pe em Z = 0.
  3) Se o modelo ja tiver rig humano: use o add-on "Animation Retargeting" (ou Rigify > "Generate" no novo modelo)
     para passar a animacao de RIG_<nome> para o rig novo (mapa: torso/hips/chest/neck/head, *_fk.L/R, f_*_master, eyes).
     Se NAO tiver rig: gere um Rigify Human sobre ele (Add > Armature > Human (Meta-Rig), ajuste ao corpo, Generate) e
     faca Parent With Automatic Weights.
  4) Confira as roupas, os dedos (apontar = indicador estendido) e o alinhamento dos olhos com 'eyes'.
  5) Apague os MESH_<nome>_*_PLACEHOLDER (a animacao fica no RIG e no FACE_<nome>).
  6) Props de mao (PRP_Chaves, PRP_ControleRemoto) estao presos ao osso hand_fk.L / hand_fk.R do rig (Child Of): se mudar o rig, mude o alvo.
  7) A movimentacao global (andar, sentar) esta na transformacao do objeto RIG_<nome> e nos controles do rig: o retarget leva tudo junto.
''')
