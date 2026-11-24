# Brinquedos sensoriais esculpidos

Versão esculpida (campos de distância, `../sdf.py`) dos fidgets do Ateliê do Mestre. As peças com mecanismo
(serpente e anel) usam a mecânica de `../../sensoriais/sensoriais.scad` com `DECOR=false` e recebem a decoração por cima,
sem tocar nas juntas nem nas folgas. O chapéu espiral usa o mesmo corte do cone antigo (passo 2,6 mm, folga 0,5 mm).

Gerar tudo: `./gerar_todos.sh` (STL em `stl/`, ignorado no git; 3MF aqui).

| Arquivo | Peça | Como imprimir (A1, PLA, 0,2 mm, 8 % gyroid) | Fatiado (sem purga) |
|---|---|---|---|
| `spinner_gatinhos.3mf` + 2× `spinner_tampinha.3mf` | Spinner Ciranda dos Gatinhos; **rolamento 608** prensado no centro (furo 22,15 mm) | deitado, sem suporte; carinhas só nas últimas camadas; tampinhas com o pino para cima | ~8 g + 2 × 0,8 g, ~25 min |
| `chapeu_espiral.3mf` | Chapéu de Mago Espiral, já montado | em pé, sem suporte; depois gire e empurre a ponta para soltar as voltas | ~29 g, ~1 h 10 |
| `serpente_sibila.3mf` | Sibila, 12 segmentos já articulados (4 cores: pares, ímpares, olhos, língua) | deitada, sem suporte; dobre cada junta com cuidado para soltar | ~17 g, ~1 h |
| `dado_sensorial.3mf` | Dado com 6 texturas e carinha (2 cores) | apoiado na face das covinhas, sem suporte | ~10 g, ~28 min |
| `anel_P_17mm.3mf`, `anel_M_19mm.3mf`, `anel_G_21mm.3mf` | Anel giratório com ciranda de fantasminhas (aro e faixa em corpos separados) | deitado, sem suporte; gire a faixa para soltar | ~4 g, ~13 min |
| `pedrinha_sonolenta.3mf` | Pedrinha Sonolenta (4 cores) | base reta na mesa, sem suporte | ~9 g, ~23 min |
| `piao_abobora.3mf` | Pião Abóbora, uma peça só (3 cores) | em pé na ponta, **suporte em árvore** só embaixo | ~11 g, ~38 min |
| `chaveiro_d20.3mf` | Chaveiro d20 Criaturinha (4 cores) | em pé, **suporte em árvore** embaixo e sob as asinhas | ~4 g, ~25 min |

**Ainda não testado na impressora:** folgas do anel, da serpente e do chapéu espiral (mesmos valores das versões antigas)
e o pino das tampinhas do spinner (7,8 mm no furo de 8 mm do rolamento).
