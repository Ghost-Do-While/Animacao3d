# Versao 2.0 - personagens novos do Blender Studio

Branch `Versao-2.0`. Parte da `main` (Cena 02 com personagens placeholder). Arquivo de trabalho: **`cena02_v2.blend`** (o `cena02.blend` da main e o `cena02_backup.blend` ficam intactos).

## O que mudou
| Personagem | Antes | Agora | Estado |
|---|---|---|---|
| Miguel | Rigify placeholder | **Vincent** (BlenRig) | animado nos frames 1-530 (briga, sem bracos cruzados) |
| Claudio | Rigify placeholder | **Rex** (CloudRig) | animado nos frames 1-720 (empurra o ar, ombros, bracos baixos no lugar de cruzar) |
| Ancora do telejornal | formas simples | **Victoria** (CloudRig) | animada (frames 1-103); 103 PNG novos em `render/telejornal/` |
| Marcos | Rigify placeholder | **Snow** (CloudRig) | **so no carro (frames 1-243)**: maos no volante por IK, tamborilar, rosto, olhar |

Os personagens antigos ficam escondidos (nao apagados). O `RIG_Marcos` antigo continua na cena so para carregar o movimento de raiz (carro, caminhada, sofa); o `ROOT_Snow` o segue.

## Falta fazer
- Snow fora do carro: sair do carro, porta, caminhada, apartamento (porta, chave na mesa, sofa, controle, TV, dormir). `PRP_Chaves` e `PRP_ControleRemoto` ainda estao presos ao rig antigo.
- Dedos (apontar) e lip-sync do Vincent e do Rex; olhos do Vincent (vinculo quebrado no log).
- Chunk loader (so carregar o que a camera ve), cameras 16:9 e 9:16.
- Render final dos frames 243-720 (os 1-242 estao ~46% feitos).

## Scripts (`cena02/v2_*.py`) - ordem de montagem a partir do `cena02.blend`
Sempre rodar com `-S Scene` (cena principal); so os da Victoria usam `-S SCN_Telejornal`.
1. Vincent: `v2_a1_vincent_append` -> `a1b..a1h` (materiais Eevee, gaiolas, drivers) -> `v2_vincent_anim`
2. Rex: `v2_b1_rex_append` -> `v2_rex_anim`
3. Limite de GPU: `v2_c1_render_limits` (Subsurf render <= 1), `v2_c2_snow_textures` (texturas 1024 px em `snow_tex/`)
4. Victoria: `v2_d1_victoria_append` -> `v2_victoria_anim` (`-S SCN_Telejornal`)
5. Snow: `v2_e1_snow_append` -> `v2_e2_fix_snow_scene` -> `v2_f1_snow_poselib` -> `v2_snow_car` -> `v2_snow_car_face`
6. Render: `render_telejornal.py` e `render_cena.py` (Blender de fundo, retomaveis); testes: `v2_render_frames.py`, `v2_render_temp_cam.py`

Exemplo: `blender -b cena02_v2.blend -S Scene --python cena02/v2_snow_car.py`

## Notas tecnicas (Radeon integrada / Blender 5.2)
- Frame preto ou queda do Blender = limite da GPU integrada: Subsurf de render <= 1, texturas reduzidas, **um frame por processo** (`-b`). Aviso "tempo limite do driver (TDR)" da AMD aparece em alguns frames; `render_cena.py` tem vigia de 15 min por frame e refaz os que falham.
- Os rigs CloudRig vem com bracos/coluna em IK; as animacoes ligam FK pelas propriedades (`PRP-UpperArm.L/R`, `Properties`). Controle de IK do pulso no Snow: `IK-Wrist.L/R`.
- Drivers FK/IK do BlenRig (Vincent) tinham caminho incompativel com o Blender 5.x: corrigido em `v2_a1g/a1h`.
- Render do telejornal: ~2,4 min/frame (1280x720). Cena principal: ~4 min/frame (1920x1080) nesta maquina.
- Os 112 frames ja renderizados da cena principal (`render/cena02_frames/`, ~870 MB) NAO estao no Git.

Creditos dos modelos em `CREDITS.txt`.
