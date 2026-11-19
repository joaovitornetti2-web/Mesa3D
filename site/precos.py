#!/usr/bin/env python3
"""Estima filamento, tempo e preço de venda de cada produto do site a partir das malhas.

Uso: python3 site/precos.py      (lê as malhas de models/ e site/.cache/; rode antes site/gerar_imagens.py)

Como o preço é calculado (ajuste as constantes abaixo):
  gramas    = (cascas de 0,8 mm + 15 % de preenchimento no miolo) × 1,24 g/cm³ × perdas
              (perdas: 5 % em peça de 1 cor; 2 cores no AMS gastam filamento na purga: +12 g por troca de cor por camada, estimado)
  filamento = gramas × R$ 149 / 1000 g
  máquina   = horas × R$ 1,50 (energia e desgaste); horas = estimativa da peça, no mínimo gramas / 25 g/h
  preço     = (filamento + máquina) × 3 (mão de obra, falhas, embalagem e lucro), arredondado para R$ x9,90
  O preço nunca fica abaixo de R$ 19,90.
"""
import math
import os

import trimesh

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(RAIZ, "models")
CACHE = os.path.join(RAIZ, "site", ".cache")

FILAMENTO_KG = 149.0
DENSIDADE = 1.24          # g/cm³ (PLA)
CASCA_MM = 0.8            # 2 paredes de 0,4 mm
PREENCHIMENTO = 0.15
MAQUINA_HORA = 1.50
MULTIPLICADOR = 3.0
MINIMO = 19.90


def gramas(caminhos, cores=1, perda=1.05, purga_g=12):
    vol = 0.0
    for c in caminhos:
        m = trimesh.load(c, force="mesh")
        v = abs(m.volume) / 1000            # cm³
        casca = m.area * CASCA_MM / 1000     # cm³
        vol += min(v, casca + max(0, v - casca) * PREENCHIMENTO)
    return vol * DENSIDADE * perda + (cores - 1) * purga_g


def preco(g, horas):
    custo = g * FILAMENTO_KG / 1000 + horas * MAQUINA_HORA
    p = custo * MULTIPLICADOR
    p = max(MINIMO, math.ceil((p + 0.1) / 10) * 10 - 0.10)   # termina em 9,90
    return custo, p


c = lambda n: os.path.join(CACHE, n)
PRODUTOS = {
    # id do site: (malhas, cores, horas estimadas, quantidade de cópias da malha)
    "torre": ([os.path.join(M, "torre", "ritual", "torre_ritual.stl"), os.path.join(M, "torre", "ritual", "bandeja.stl")], 1, 14.0, 1),
    "bau": ([os.path.join(M, "kit", "bau", "bau_base.stl"), os.path.join(M, "kit", "bau", "bau_tampa.stl")], 1, 9.0, 1),
    "aneis": ([c("aneis_c1.stl"), c("aneis_c2.stl")], 2, 3.0, 2),          # malha tem 4 anéis; o conjunto tem 8
    "caixa": ([c("caixa_sangue_c1.stl"), c("caixa_sangue_c2.stl")], 2, 3.5, 1),
    "relicario": ([c("relicario_sangue_c1.stl"), c("relicario_sangue_c2.stl")], 2, 6.0, 1),
    "agentes": ([os.path.join(M, "kit", "meshy_op", "combatente_pronto.stl")], 1, 1.5, 1),
    "mini-agente": ([os.path.join(M, "kit", "meshy_op", "chibi_agente_pronto.stl")], 1, 3.0, 1),
    "mini-criatura": ([os.path.join(M, "kit", "meshy_op", "chibi_criatura_pronto.stl")], 1, 3.0, 1),
}

if __name__ == "__main__":
    print(f"{'produto':<14}{'gramas':>8}{'horas':>7}{'custo':>10}{'preço':>10}")
    for pid, (malhas, cores, horas, copias) in PRODUTOS.items():
        g = gramas(malhas, cores) * copias if cores == 1 else (gramas(malhas, 1) * copias + (cores - 1) * 12)
        horas = max(horas, g / 25)           # a A1 imprime uns 25 g/h em peça grande
        custo, p = preco(g, horas)
        print(f"{pid:<14}{g:>8.0f}{horas:>7.1f}{custo:>10.2f}{p:>10.2f}")
