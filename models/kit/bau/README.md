# Baú de ritual (esculpido)

Baú de dados com escultura gerada no Meshy (desenho original: pedra e ferro, círculo de runas, caveiras,
correntes, cantoneiras) e tornado funcional por `../bau_meshy.py`: corpo preenchido, cortado em base e
tampa, cavidade com parede de 5 mm e borda de encaixe de 4 mm na base, que entra num rebaixo da tampa
(folga 0.35 mm).

| Arquivo | Peça | Medidas |
|---|---|---|
| `bau_base.3mf` | base, espaço interno 83 × 57 × 54 mm | 104 × 80 × 67 mm |
| `bau_tampa.3mf` | tampa | 101 × 82 × 27 mm |

Imprimir (A1, PLA, 0.16–0.2 mm): base em pé, sem suporte. Tampa em pé (topo esculpido para cima), com suporte
em árvore só no rebaixo de baixo. As duas peças já estão na posição montada.

Refazer: `python3 ../bau_meshy.py meshy_op/bau.stl bau --largura 104` (escultura original fora do git).

**Ainda não testado na impressora:** encaixe da tampa.

**Preenchimento recomendado:** 8% gyroid, 2 paredes. Leve e resistente para peças de mesa (é o que os preços do site consideram).
