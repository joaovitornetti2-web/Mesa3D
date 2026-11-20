# Torre do Ritual (esculpida)

Torre de dados com escultura gerada no Meshy (desenho original: pedra rachada, sigilo entalhado, correntes,
sangue escorrendo, caveiras na base) e tornada funcional por `../torre_meshy.py`: corpo preenchido,
canal de 50 mm aberto em cima, duas rampas a 50° sem suporte, piso inclinado e porta de 40 × 38 mm na frente.

| Arquivo | Peça | Medidas |
|---|---|---|
| `torre_ritual.3mf` | torre | 100 × 79 × 180 mm |
| `bandeja_ritual.3mf` | bandeja com sigilo e anel de runas gravados e moldura de encaixe da torre | 160 × 178 × 16 mm |

Imprimir (A1, PLA): torre em pé, camada 0.16–0.2 mm, sem suporte (as rampas são a 50°; se o fatiador pedir,
use suporte em árvore só na porta). Bandeja: 0.2 mm, sem suporte. Dado máximo: d20 de 26 mm.

Refazer a bandeja: `openscad -o bandeja.stl ../torre_ritual.scad`.
Refazer a torre a partir da escultura: `python3 ../torre_meshy.py <escultura>.stl torre_ritual.stl --largura 86`
(a escultura original fica em `models/kit/meshy_op/torre_ritual.stl`, fora do git; o Meshy guarda a tarefa).

**Ainda não testado na impressora:** queda dos dados pelas rampas e encaixe da torre na moldura (folga 0.3 mm).

**Preenchimento recomendado:** 8% gyroid, 2 paredes. Leve e resistente para peças de mesa (é o que os preços do site consideram).
