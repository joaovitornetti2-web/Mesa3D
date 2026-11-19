# Caixa de dados elemental (esculpida)

Escultura gerada no Meshy (desenho original: pedra rúnica, caveiras, cantoneiras, medalhão de runas) e tornada
caixa por `../caixa_meshy.py`: corpo preenchido, cavidade de 70 × 56 × 34 mm, tampa cortada no topo com encaixe
(borda de 4 mm na base, folga 0.35 mm) e o emblema do elemento embutido 0,7 mm no medalhão da frente.

| Arquivo | Peça |
|---|---|
| `base_<elemento>_2cores.3mf` | base com 2 objetos: corpo (cor 1) e emblema (cor 2). No Bambu Studio, atribua um filamento a cada objeto |
| `caixa_tampa.3mf` | tampa (igual para todos os elementos) |

Fechada: 104 × 88 × 92 mm. Imprimir (A1, PLA, 0.16–0.2 mm): base em pé, sem suporte; tampa em pé, com suporte em
árvore só no rebaixo de baixo. Elementos: sangue, morte, conhecimento, energia, medo.

Refazer: `python3 ../caixa_meshy.py <escultura>.stl runica` (escultura em `models/kit/meshy_op/caixa_runica.stl`, fora do git).

**Ainda não testado na impressora:** encaixe da tampa e o emblema de 2 cores na frente (troca de cor em várias camadas:
gasta mais filamento na purga do AMS).
