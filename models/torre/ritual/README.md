# Torre do Ritual (Torre Rúnica no site)

Torre e bandeja esculpidas no Meshy (desenho original: pedra rachada, sigilo entalhado, correntes, sangue escorrendo,
caveiras) e tornadas funcionais:

- **Torre** (`../torre_meshy.py`, voxel 0,25 mm): corpo preenchido, canal de 50 mm aberto em cima, duas rampas a 50°
  sem suporte, piso inclinado e porta de 40 × 38 mm na frente.
- **Bandeja** (`../bandeja_meshy.py`): borda esculpida com caveiras e correntes, fundo liso de 158 × 154 mm (3 mm),
  sigilo com anel de runas gravado (0,8 mm) e moldura de encaixe da torre (1,6 mm). Máscaras do fundo em
  `../bandeja_mascaras.scad` → `mascaras/`.

| Arquivo | Peça | Medidas | Fatiado (8 %) |
|---|---|---|---|
| `torre_ritual.3mf` | torre | 100 × 79 × 180 mm | ~223 g, ~11h20 |
| `bandeja_esculpida.3mf` | bandeja | 193 × 188 × 41 mm | ~126 g, ~4h30 |

Imprimir (A1, PLA, camada 0.2, 2 paredes, **8 % gyroid**): torre em pé, sem suporte (se o fatiador pedir, suporte em
árvore só na porta). Bandeja deitada, sem suporte (as correntes externas podem pedir suporte em árvore).
Dado máximo: d20 de 26 mm.

Refazer: `python3 ../torre_meshy.py <torre>.stl torre_ritual.stl --largura 86 --passo 0.25 --suavizar 2 --faces 900000`
e `python3 ../bandeja_meshy.py <bandeja>.stl bandeja_esculpida.stl --faces 900000` (esculturas em
`models/kit/meshy_op/`, fora do git; o Meshy guarda as tarefas).

**Ainda não testado na impressora:** queda dos dados pelas rampas e encaixe da torre na moldura (folga 0,3 mm).
