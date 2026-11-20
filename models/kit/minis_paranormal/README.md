# Miniaturas e brinquedinhos paranormais (Meshy)

Desenhos originais gerados no Meshy (texto → 3D, sem textura), inspirados no horror paranormal de mesa,
sem personagens nem símbolos oficiais de nenhum jogo.

| Arquivo | Peça | Tamanho |
|---|---|---|
| `ocultista.3mf` | agente ocultista com grimório, adaga e velas no círculo de ritual | base 40 mm, 38 mm de altura |
| `combatente.3mf` | agente com colete tático, facão e espingarda | base 25 mm, 34 mm |
| `especialista.3mf` | investigador de sobretudo com lanterna e câmera | base 25 mm, 33 mm |
| `criatura.3mf` | criatura de sangue | base 25 mm, 32 mm |
| `chibi_agente.3mf` | brinquedinho: mini agente com lanterna | base 32 mm, 53 mm |
| `chibi_criatura.3mf` | brinquedinho: mini criatura de sangue | base 32 mm, 52 mm |

Como imprimir (A1, PLA): camada 0.08–0.12 mm, bico 0.4 (0.2 se tiver), suporte em árvore só onde o
Bambu Studio pedir (facão, braços e velas), brim desligado. A figura e a base são corpos separados no
arquivo; o Bambu Studio une os dois ao fatiar (se avisar de malha aberta, aceite o reparo automático).

**Ainda não testado na impressora:** partes finas (facão do combatente, velas da ocultista, garras da
criatura) podem precisar de 0.08 mm e suporte; confira na pré-visualização do fatiador.

Licença: confira se o seu plano do Meshy permite uso comercial antes de vender (no plano gratuito,
normalmente não permite).

Os STL originais e os prontos ficam em `models/kit/meshy_op/` (fora do git). Para refazer:
`python3 ../preparar_mini.py <nome>.stl <nome>_pronto.stl --altura 31` (brinquedinhos: `--altura 50 --base 32`).

**Preenchimento recomendado:** 8% gyroid, 2 paredes. Leve e resistente para peças de mesa (é o que os preços do site consideram).
