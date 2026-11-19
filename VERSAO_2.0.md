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

## Correcoes apos revisao do usuario (16/11/2026)
| Frame | Problema | Causa | Correcao |
|---|---|---|---|
| 233 (e 1-243) | pe do Snow aparecia embaixo do carro | pernas FK atravessavam o assoalho (tornozelo z=0,27; assoalho z=0,525) | `v2_fix_pernas_carro.py`: coxas sobem 15 graus, canelas 30 graus para baixo/frente; tornozelo ~0,63 no frame 233 |
| 399-492 | cabeca do Rex girando | `aim()` acumulava o twist a cada chave | `aim()` agora ABSOLUTO (zera a rotacao antes) em `v2_rex_anim.py` e `v2_vincent_anim.py`; animacoes refeitas |
| 499-521 | Snow andava de lado ate o sofa | yaw da raiz errado (virava para a TV antes de andar) | novas chaves de yaw em `v2_snow_apto.py`: anda de frente (produto frente.velocidade ~1) e so vira para a TV no fim |
| 508 | jogava a chave de costas | yaw 507 = +X (de costas para a mesa) | agora de frente para a mesa (-X) e braco para a frente |
| 610-720 | olhos brancos | cornea (Refraction no Eevee) renderiza como mancha branca; alvo do olhar tambem ficava abaixo | `v2_fix_olhos_cornea.py` esconde a cornea no render de 493 a 720; alvo do olhar em `TV_EYE` (628-720) |
| 299, 382 | mao do Vincent aberta/para fora | rolamento acumulado (corrigido pelo `aim()` absoluto) + dedos de descanso do BlenRig | rolamento corrigido + POSES DE MAO do Vincent (`v2_vincent_anim.py`, funcao `fingers()`): punho fechado, indicador esticado ao apontar, garra na cabeca, mao relaxada; curva as falanges `fing_<dedo>_2/3/4` (rotacao X), chaveadas em cada pose |

Diagnostico: `v2_medir*.py` (medicoes), `v2_teste_olhos.py`. Rodar na ordem: `v2_fix_pernas_carro`, `v2_rex_anim`, `v2_vincent_anim`, `v2_snow_apto`, `v2_fix_olhos_cornea` (todos com `-S Scene`).
Obs.: de 522 a 528 o Snow ainda recua ~1,2 m em 6 frames para sentar (rapido); ajuste futuro.

## Segunda rodada de correcoes (16/11/2026)
| Frame | Problema | Correcao |
|---|---|---|
| 91+ | olhos do Snow brancos / sem acompanhar a cabeca | `v2_fix_olhos_cornea.py`: cornea (Refraction) escondida em TODO o filme (viewport e render); iris e pupila aparecem |
| todo o filme | emocoes do Snow incoerentes | `v2_snow_emocoes.py`: linha do tempo de 58 emocoes (cansaco, impaciencia/raiva no carro, suspiro, surpresa na briga, exaustao, irritacao ao jogar a chave, alivio, surpresa/indignacao com o jornal, tristeza, sono) + piscadas. Rodar DEPOIS de `v2_snow_exit` e `v2_snow_apto` |
| 168 | carro "mole" | `v2_fix_carro_fisica.py`: suspensao recalculada nos 5 carros (cabeceio max 1,3 graus, amortecimento critico, 1 chave por frame) |
| 338 | mao do Vincent | revisada; poses de mao ja aplicadas (punho / indicador / garra); sem mudanca adicional |
| 518 | corpo esticado | `v2_snow_apto.py`: raiz 5-6 cm mais baixa (joelhos flexionados), cotovelos dobrados, tronco menos rigido |
| 542 | ancora em pe, sem animacao de jornalista | `v2_victoria_anim.py`: Victoria SENTADA (escala 1,25, assento `TJ_Cadeira_Assento`, pes em IK), fala com a mandibula, acena a cabeca, mao direita enfatiza manchetes e aponta as imagens |
| 568 | graficos do jornal entravam nos objetos | `v2_telejornal_overlays.py`: graficos numa cena propria (`SCN_Telejornal_Ovl`, camera fixa sem desfoque, fundo transparente) compostos POR CIMA com `telejornal_compor.py` |

**Pendente (render):** a TV do apartamento ainda usa os 103 PNG antigos (Victoria em pe, graficos 3D). Para atualizar:
1. `python cena02/render_telejornal.py` (estudio, ~2,4 min/frame, ~4 h) -> `render/telejornal_victoria/`
2. `blender -b cena02_v2.blend -S SCN_Telejornal_Ovl -s 1 -e 103 -a` (graficos, rapido) -> `render/telejornal_ovl/`
3. `python cena02/telejornal_compor.py` -> `render/telejornal_final/`; copiar para `render/telejornal/`.

## Estado do render do telejornal (parado em 16/11/2026, 16:50)
- Estudio (Victoria sentada): **65 de 103 frames** prontos em `render/telejornal_victoria/` (tv_0001 a tv_0065), ~1,8 min/frame; faltam 66-103.
- Para continuar: `bash cena02/render_telejornal_tudo.sh` (o `render_telejornal.py` retoma de onde parou, depois renderiza os graficos, compoe e copia para `render/telejornal/`).
- Enquanto os 103 frames compostos nao forem copiados, a TV do apartamento (`render/telejornal/`) ainda mostra os frames ANTIGOS (Victoria em pe, graficos 3D).
- Os graficos (`SCN_Telejornal_Ovl`) ainda nao foram renderizados: `blender -b cena02_v2.blend -S SCN_Telejornal_Ovl -s 1 -e 103 -a`.

## Atualizacao 19/11/2026 (11:20): render do telejornal CONCLUIDO
- Estudio 103/103, graficos 103/103, composicao 103/103; os 103 frames finais ja estao em `render/telejornal/` (a TV do apartamento passa a usar os frames novos).
- A composicao com `telejornal_compor.py` exige Pillow; sem ele use `blender -b --python cena02/telejornal_compor_blender.py` (roda da raiz do projeto).
- `cena02/vigia_travadas.ps1` mata o Blender travado (6 min sem frame novo) e o `render_telejornal.py` refaz o lote sozinho.
- Proximo: render da cena principal (`cena02_v2.blend`, `-S Scene`), Etapa 4 (benchmark do chunk loader) e Etapa 5 (cameras 9:16).
