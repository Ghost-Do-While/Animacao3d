# Contexto do projeto — Cena 02 "A Fila, a Vaga e o Cansaço" (Blender 5.2)

> Cole este arquivo numa conversa nova (ou envie junto com o `cena02.blend`) para continuar de onde paramos.
> Idioma de trabalho: português (Brasil). O usuário quer respostas diretas e curtas, sem render/MP4 final até pedir.

## 1. O que é
Animação 3D de 30 s (720 frames, 24 fps, 1920×1080) para um vídeo de projeto escolar de um sistema de controle de entrada de condomínio.
Roteiro: Marcos (de azul-claro, 35 anos) está numa fila lenta para entrar no condomínio; estaciona e vê Miguel (polo laranja) brigando com Claudio (jaqueta jeans azul) por uma vaga;
em casa joga as chaves, senta no sofá e vê um telejornal sobre a briga; desliga a TV e adormece ("Não dá mais... Tinha que existir um sistema...").
10 planos (CAM_01..CAM_10, ligados a markers): P01 1–72, P02 73–144, P03 145–204, P04 205–252, P05 253–288, P06 289–396, P07 397–492, P08 493–540, P09 541–600, P10 601–720.
Falas de Miguel/Claudio e a locução do Marcos estão no roteiro (lip-sync nos FACE_<nome>).

## 2. Regras do usuário (decididas, não rediscutir)
- Condomínio = réplica da MAQUETE física (fotos), mas AMPLIADO: lote 32×26 m (X −16..16, Y −13..13), prédio 7×13 m / 4 andares de 3 m no canto fundo-esquerdo,
  guarita CENTRALIZADA na frente, SAÍDA à esquerda e ENTRADA à direita (5 m cada), 6 vagas (4 no muro direito V1..V4, 2 centrais V5/V6) 2,6×5,2 m com as linhas encostando nos muros/gradil,
  2 cancelas, 2 sensores ultrassônicos (encostados nas laterais, fora do caminho), gradis brancos, 2 postes, muros de cobogó. SEM as 2 caixas pretas da maquete. SEM pilar sob a marquise da guarita.
- Estilo: animação de estúdio (Pixar/Illumination), formas arredondadas, cores saturadas, golden/blue hour, bokeh, luz de 3 pontos nos closes.
- Os 4 carros clássicos foram REMOVIDOS. Os 4 carros da fila (Fila1..4) entram de verdade e estacionam em V4, V5, V2, V1; Claudio já está na V3; Marcos estaciona na V6.
- A cancela da ENTRADA funciona em ciclos: abre, UM carro passa, fecha, abre para o próximo... O 1º ciclo (plano 1) e o do Marcos (plano 3) são lentos de propósito (sensação de demora/cansaço);
  ciclos 2–4 são curtos e acontecem durante o plano 2 (interior do carro).
- Carro do Marcos fica PARADO durante todo o "estresse" do plano 2 (frames 86–144): tamborila, olha, suspira, cabeça no encosto, sempre com as mãos no volante. Só anda 73–86 e depois de 145.
- Telejornal: estúdio 3D completo (cena `SCN_Telejornal`, objetos em X=500), câmera `CAM_TV_Jornal`, 103 frames pré-renderizados em `render/telejornal/tv_0001..0103.png`,
  usados como textura (Image Sequence) na tela da TV do apartamento (frame 538 = 1º frame do jornal). A âncora é uma jornalista formal (blazer rosa).
- NÃO renderizar o vídeo final nem exportar MP4 ainda (o usuário pediu para aguardar). Áudio: não há.
- Este PC só tem CPU (sem GPU para Cycles) → Eevee. O Blender da interface trava se rodar tarefas pesadas: prefira processos em segundo plano (`blender -b`).

## 3. Personagens
Marcos, Miguel, Claudio: rig Rigify (metarig humano), malhas `MESH_<nome>_*_PLACEHOLDER` separadas, `SLOT_<nome>`, `FACE_<nome>` (propriedades A E I O U MBP FV rest blink brow_* mouth_* ... com drivers nas shape keys),
texto interno `LEIA-ME_SUBSTITUIR` ensina a trocar por modelos baixados (retarget). Braços/pernas em FK (propriedade IK_FK = 1).
A animação usa FK por "nomes lógicos" (spine/chest/neck/head/upper_arm.L/...) traduzidos em `p4_anim.py` (função `xlate`).

## 4. Arquivos (pasta do projeto)
- `cena02.blend` — cena montada (última versão boa, SEM Snow). `cena02_v2_maquete_1-32.blend` — versão antiga (layout 19×16 m).
- `characters.blend` — personagens gerados por `cena02/build_chars.py` (Blender de fundo com Rigify).
- `render/telejornal/` — 103 PNG do telejornal (necessários para a tela da TV; sem eles a TV fica rosa).
- `cena02/` — scripts que reconstroem TUDO do zero: `lib.py, layout.py, p0_setup.py, p1_maquete.py, p1b_rua.py, p1c_apto.py, p2_veiculos.py, p3_chars.py, p4_anim.py, p5_cams.py, p6_lights_comp.py, p7_telejornal.py`;
  `run.py` (função `build()`), `preview_sheet.py` (folha de contato de frames), `render_preview.py`/`montar_mp4.py` (prévia), `build_chars.py`, `p4b_snow.py` + `build_snow.py` (experimento Snow, FORA da cadeia).
- `snow/` e `snow_src/` — conteúdo do `Snow_v4.2.zip` (Blender Studio, CC-BY) extraído; `snow_experimento/` — cache do retarget (descartável).
Reconstruir a cena: abrir o Blender, rodar `run.py` (ou executar as partes na ordem acima em um mesmo namespace com `BASE` = pasta `cena02`). Montar tudo leva alguns segundos.
Render do telejornal (se faltarem os PNG): `blender -b cena02.blend -S SCN_Telejornal -a`.

## 5. Estado e pendências
- Estado final entregue: tudo acima funcionando; colisão de carros verificada (zero); 10 planos conferidos em frames de teste.
- Ideia em andamento (CANCELADA por tempo do usuário): trocar o Claudio (pessoa de azul) pelo modelo **Snow** (Blender Studio, rig CloudRig, 1494 ossos, 50 shape keys no rosto, CC-BY — dar crédito
  "Snow Rig (CC) Blender Foundation | studio.blender.org"). Estudo feito: braços em T no repouso; controles FK úteis: FK-Spine/RibCage/Chest/Neck/Head, FK-Shoulder/UpperArm/Forearm/Wrist.L/R,
  FK-Finger_*; olhar = `TGT-Eyes`; rosto por poses 1-frame (ações `Mouth *` e `Eyemask *`); braços ficam em IK por padrão → pôr `Properties["ik_left_upperarm"]=0` (e right). Plano: retarget por orientação
  no espaço do armature a partir do rig Rigify do Claudio (script `p4b_snow.py`). O bake travou o Blender da interface (rig pesado): se retomar, fazer o bake em Blender de FUNDO e salvar um `.blend` pronto.
  O usuário aceita personagens de alturas/estilos diferentes; só a jornalista precisa ser formal.
- Outros pontos mencionados pelo usuário ("vamos discutir mais algumas coisas"): melhorar os bonecos; ainda não decididos.

## 6. Dicas técnicas aprendidas (Blender 5.2)
- Materiais novos precisam de árvore de nós explícita (`new_mat`); nós Mix têm sockets duplicados → usar `sock()`.
- Keyframes: interpolação padrão BEZIER; usar `key()`/`set_interp()` de `lib.py`. Rigify só habilita limpo em Blender de fundo (`bpy.ops.preferences.addon_enable('rigify')` com `--factory-startup`).
- `bpy.ops.render.render(scene=...)` não respeita `frame_current` de outra cena; para renderizar frames do telejornal use linha de comando.
- Edições de arquivo por script: cuidado com PowerShell `foreach` sobre arrays de um só par (achata o array e troca letras) — usar Python com `assert old in text`.
