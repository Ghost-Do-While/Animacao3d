# Animacao3d - Cena 02 "A Fila, a Vaga e o Cansaco"

Animacao 3D (Blender 5.2, 30 s, 720 frames, 24 fps) de um condominio com sistema de controle de entrada, para um projeto escolar.
Marcos espera numa fila lenta, estaciona, ve a briga por uma vaga, volta para casa e dorme na frente do telejornal.

## O que tem aqui
| Caminho | Conteudo |
|---|---|
| `cena02.blend` | Cena montada: condominio (maquete ampliada 32x26 m), rua, apartamento, carros, 3 personagens com rig Rigify, 10 cameras ligadas a markers, luzes, compositor e a cena `SCN_Telejornal` |
| `characters.blend` | Personagens gerados por `cena02/build_chars.py` (Marcos, Miguel, Claudio) |
| `render/telejornal/` | 103 PNG do telejornal 3D, usados como textura animada na TV do apartamento (sem eles a TV fica rosa) |
| `cena02/` | Scripts Python que reconstroem a cena do zero (`run.py`, `p0_setup.py` ... `p7_telejornal.py`) |
| `versoes/` | Versao antiga (maquete 19x16 m) |
| `CONTEXTO_PROJETO.md` | Resumo completo do projeto, regras ja decididas e pendencias (use para continuar em outra conversa) |

## Como abrir
Abra `cena02.blend` no Blender 5.2. Mantenha `render/telejornal` ao lado do arquivo.

## Como reconstruir tudo pelos scripts
1. `blender -b --factory-startup --python cena02/build_chars.py -- characters.blend` (precisa do add-on Rigify; gera os personagens)
2. Abra o Blender e rode `cena02/run.py` (funcao `build()`), que executa as partes na ordem e salva `cena02.blend`.
3. Telejornal (se faltarem os PNG): `blender -b cena02.blend -S SCN_Telejornal -a`.

## Estado
Sem render final e sem MP4 por enquanto (pedido do usuario). Sem audio. Eevee (a maquina so tem CPU).
O experimento de trocar o Claudio pelo modelo Snow (Blender Studio, CC-BY) foi cancelado; os scripts `p4b_snow.py` e `build_snow.py` ficam fora da cadeia de montagem e os arquivos do Snow nao estao neste repositorio.
