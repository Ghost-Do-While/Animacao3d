# Versao 2.0 - personagens novos do Blender Studio

Branch `Versao-2.0`. Parte da `main` (Cena 02 com personagens placeholder). Arquivo de trabalho: **`cena02_v2.blend`** (o `cena02.blend` da main e o `cena02_backup.blend` ficam intactos).

## O que mudou
| Personagem | Antes | Agora | Estado |
|---|---|---|---|
| Miguel | Rigify placeholder | **Vincent** (BlenRig) | animado nos frames 1-530 (briga, sem bracos cruzados) |
| Claudio | Rigify placeholder | **Rex** (CloudRig) | animado nos frames 1-720 (empurra o ar, ombros, bracos baixos no lugar de cruzar) |
| Ancora do telejornal | formas simples | **Victoria** (CloudRig) | animada (frames 1-103); 103 PNG novos em `render/telejornal/` |
| Marcos | Rigify placeholder | **Snow** (CloudRig) | frames 1-720: carro (maos no volante por IK, tamborilar, rosto), saida do carro com a mao na porta, caminhada com pes em IK, em pe na briga, apartamento (abre e FECHA a porta com a mao na macaneta, chave jogada na mesa, sofa, controle, TV, dormindo) |

Os personagens antigos ficam escondidos (nao apagados). O `RIG_Marcos` antigo continua na cena so para carregar o movimento de raiz (carro, caminhada, sofa); o `ROOT_Snow` o segue.

## Falta fazer
- Conferir a mao do Snow na porta do carro (frame 250): a camera de teste ficou escondida atras dos carros.
- Dedos (apontar) e lip-sync do Vincent e do Rex; olhos do Vincent (vinculo quebrado no log).
- Chunk loader (so carregar o que a camera ve), cameras 16:9 e 9:16.
- Render final de TODOS os frames (os 1-242 estao ~46% feitos em `render/cena02_frames`, fora do Git; frames 243-720 ainda nao).

## Conferencia geral (14-15/11/2026)
Verificacao automatica `cena02/v2_verify.py` (resultado em `render/verificacao_v2.txt`): **23 OK, 7 avisos, 0 erros**. Folha de contato em `render/folha_contato/folha_1..3.png` (25 frames do filme inteiro).
- OK: nenhuma textura faltando (158 MB de imagens), 103/103 PNG da TV, nenhum caminho local no `.blend`, 24 fps, frames 1-720, 10 marcadores de camera, os 3 personagens animados, antigos escondidos, porta do apartamento abre (82 graus) e FECHA com a mao na macaneta (0 cm), chave pousa na mesa lateral, controle junto da mao.
- Bracos: Rex e Vincent 0 de 120 amostras cruzam o corpo; Snow 1 (frame 505, mao esquerda puxando a macaneta, 8 cm).
- Pes: sem deslize relevante (2-6 cm em 1-4 frames por caminhada). O ritmo do apartamento (493-540, so 2 s para porta, chave, caminhada, sentar e controle) obriga passos rapidos (ate ~1 m/frame): vem do roteiro original.
- Corrigido na conferencia: raiz do apartamento andava em degraus (interpolacao constante herdada); sentar arrastava os pes (agora da um passo); cabeca/olhos do Snow; Vincent claro demais; Snow virava silhueta no apartamento (luz `LGT_Apto_Fill_Snow`, frames 493-540).
- Frame 720 e preto de proposito (a tela escurece entre 708 e 714).
- Avisos que ficam: Subsurf de render = 2 em `GEO-rex_polo_shirt(_collar)` e `GEO-victoria_dress` (controlado por driver "Quality" do rig; renderizam sem problema), enquadramento 16:9 + 9:16 (Etapa 5) e chunk loader (Etapa 4) AINDA NAO feitos.

## Scripts (`cena02/v2_*.py`) - ordem de montagem a partir do `cena02.blend`
Sempre rodar com `-S Scene` (cena principal); so os da Victoria usam `-S SCN_Telejornal`.
1. Vincent: `v2_a1_vincent_append` -> `a1b..a1h` (materiais Eevee, gaiolas, drivers) -> `v2_vincent_anim`
2. Rex: `v2_b1_rex_append` -> `v2_rex_anim`
3. Limite de GPU: `v2_c1_render_limits` (Subsurf render <= 1), `v2_c2_snow_textures` (texturas 1024 px em `snow_tex/`)
4. Victoria: `v2_d1_victoria_append` -> `v2_victoria_anim` (`-S SCN_Telejornal`)
5. Snow: `v2_e1_snow_append` -> `v2_e2_fix_snow_scene` -> `v2_f1_snow_poselib` -> `v2_snow_car` -> `v2_snow_car_face` -> `v2_snow_exit` -> `v2_snow_apto` -> `v2_snow_eyes` (usam `snow_lib.py`); acabamento: `v2_polish`; conferencia: `v2_verify`, `contact_sheet.py`
6. Render: `render_telejornal.py` e `render_cena.py` (Blender de fundo, retomaveis); testes: `v2_render_frames.py`, `v2_render_temp_cam.py`

Exemplo: `blender -b cena02_v2.blend -S Scene --python cena02/v2_snow_car.py`

## Notas tecnicas (Radeon integrada / Blender 5.2)
- Frame preto ou queda do Blender = limite da GPU integrada: Subsurf de render <= 1, texturas reduzidas, **um frame por processo** (`-b`). Aviso "tempo limite do driver (TDR)" da AMD aparece em alguns frames; `render_cena.py` tem vigia de 15 min por frame e refaz os que falham.
- Giro da cabeca (`twist`) em `snow_lib.torso()` e ABSOLUTO (zera antes de apontar); o alvo dos olhos (`TGT-Eyes`) e filho da cabeca e so e posicionado depois da pose final dela.
- Os rigs CloudRig vem com bracos/coluna em IK; as animacoes ligam FK pelas propriedades (`PRP-UpperArm.L/R`, `Properties`). Controle de IK do pulso no Snow: `IK-Wrist.L/R`.
- Drivers FK/IK do BlenRig (Vincent) tinham caminho incompativel com o Blender 5.x: corrigido em `v2_a1g/a1h`.
- Render do telejornal: ~2,4 min/frame (1280x720). Cena principal: ~4 min/frame (1920x1080) nesta maquina.
- Os 112 frames ja renderizados da cena principal (`render/cena02_frames/`, ~870 MB) NAO estao no Git.

Creditos dos modelos em `CREDITS.txt`.
