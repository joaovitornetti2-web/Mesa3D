# Brinquedos sensoriais (desenho próprio)

Fidgets do Ateliê do Mestre no estilo rúnico, sem depender de licença de terceiros.
Fonte: `sensoriais.scad` (PARTE = `s_…`) e `cone_espiral.py`. Fotos do site: `site/gerar_imagens.py` (produtos `sens_*`).

| Arquivo | Peça | Como imprimir (A1, PLA, 0.2 mm, 8 % gyroid) | Fatiado |
|---|---|---|---|
| `spinner_corpo.3mf` + 2× `spinner_tampinha.3mf` | Spinner Rúnico; **precisa de 1 rolamento 608** (22 × 8 × 7 mm) prensado no centro | deitado, sem suporte; tampinhas com o pino para cima | ~12 g, ~30 min |
| `cone_espiral.3mf` | Cone Espiral, impresso já montado | em pé, sem suporte; depois de imprimir, gire e empurre a ponta para soltar as voltas | ~27 g, ~1 h |
| `serpente_articulada.3mf` | Serpente de 12 segmentos, já montada (pinos verticais, folga 0,4 mm) | deitada, sem suporte; dobre cada junta com cuidado para soltar | ~15 g, ~50 min |
| `dado_sensorial.3mf` | Dado com 6 texturas | apoiado na face dos 6 pontos, sem suporte | ~8 g, ~22 min |
| `anel_P_17mm.3mf`, `anel_M_19mm.3mf`, `anel_G_21mm.3mf` | Anel giratório, já montado (canal em V, folga 0,35 mm) | deitado, sem suporte; gire a faixa para soltar | ~4 g, ~8 min |
| `pedra_runas.3mf` | Pedra de apertar | base reta na mesa, sem suporte | ~8 g, ~17 min |
| `piao_corpo.3mf` + `piao_haste.3mf` | Pião (a haste encaixa no furo de cima; cole se ficar folgada) | corpo com a face de cima na mesa (ponta para cima); haste em pé | ~7 g, ~28 min |
| `chaveiro_d20.3mf` | d20 de 23 mm com argola | deitado na lateral com suporte em árvore, ou em pé com suporte só na argola | ~3 g, ~15 min |

Anel em 2 cores: o aro de dentro e a faixa de fora são corpos separados no arquivo, então dá para dar um filamento a cada um.
Serpente em 2 cores: os segmentos são corpos separados; alterne os filamentos no Bambu Studio.

**Ainda não testado na impressora:** folgas das peças já montadas (serpente, anel, cone) e o aperto do rolamento
(furo de 22,15 mm). Se o rolamento entrar solto ou apertado demais, ajuste `SP_FURO` em `sensoriais.scad`.
