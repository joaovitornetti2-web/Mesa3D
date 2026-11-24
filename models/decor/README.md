# Plaquinhas e decoração

Desenho próprio. Fonte Fredoka (licença SIL OFL, em `fontes/`). Fonte: `plaquinhas.scad` e `decor.scad`.

## Plaquinhas (160 × 60 × 5 mm, 2 cores)
Base (cor 1) e texto/moldura/ícone em relevo (cor 2). A troca de cor é só no topo, então quase não há purga.
Furos escareados para prego/parafuso, ou use fita dupla face.
- Estilo do Ateliê: `placa_nao_perturbe.3mf`, `placa_covil.3mf`, `placa_criaturas.3mf`
- Dia a dia: `placa_bem_vindos.3mf`, `placa_home_office.3mf`, `placa_nome.3mf` (troque `NOME` em `plaquinhas.scad`
  e gere: `openscad -o nome_c1.stl -D 'PARTE="nome_c1"' -D 'NOME="Quarto do João"' plaquinhas.scad`, idem `_c2`)

Fatiado: ~21–25 g, ~35–40 min cada.

## Decoração
| Arquivo | Peça | Estilo | Fatiado (8 %) |
|---|---|---|---|
| `lanterna.3mf` | Lanterna Rúnica, para vela de LED de até 38 mm (janelas em forma de runa) | Ateliê | ~66 g, ~3 h |
| `monstrinho.3mf` | Monstrinho porta-trecos (3 cores: corpo, pupilas/boca, olhos/dentes) | Ateliê | ~60 g, ~1h45 |
| `porta_chaves_runa.3mf` | Porta-chaves de parede, 4 ganchos em garra (2 cores) | Ateliê | ~37 g, ~1h20 |
| `vaso.3mf` | Vaso torcido de 8 pontas (flores secas/artificiais ou capa de vaso) | Dia a dia | ~120 g, ~4 h |
| `porta_copos.3mf` | Porta-copos (o arquivo tem 3; imprima 4), flor e ondas em 2 cores | Dia a dia | ~18 g cada |
| `gatinho.3mf` | Gatinho suporte de celular (4 cores), canal para o cabo | Dia a dia | ~46 g, ~1h30 |

Imprimir sem suporte, exceto: ganchos do porta-chaves (imprimir a placa deitada; os ganchos sobem em pé),
orelhas e rabinho do gatinho (suporte em árvore se o fatiador pedir). Vaso e lanterna não são à prova d'água.

**Ainda não testado na impressora.**
