#!/usr/bin/env python3
"""Estima filamento, tempo e preço de venda de cada produto do site a partir das malhas.

Uso: python3 site/precos.py      (lê as malhas de models/ e site/.cache/; rode antes site/gerar_imagens.py)

Como o preço é calculado (ajuste as constantes abaixo):
  gramas    = (cascas de 0,8 mm + 8 % de preenchimento no miolo) × 1,24 g/cm³ × perdas
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
PREENCHIMENTO = 0.08         # 8 %: leve e resistente para peças de mesa
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
    "caixa": ([os.path.join(M, "dados", "runica", "base_sangue_cor1.stl"), os.path.join(M, "dados", "runica", "caixa_tampa.stl")], 2, 8.0, 1),
    "relicario": ([c("relicario_sangue_c1.stl"), c("relicario_sangue_c2.stl")], 2, 6.0, 1),
    "agentes": ([os.path.join(M, "kit", "meshy_op", "combatente_pronto.stl")], 1, 1.5, 1),
    "mini-agente": ([os.path.join(M, "kit", "meshy_op", "chibi_agente_pronto.stl")], 1, 3.0, 1),
    "mini-criatura": ([os.path.join(M, "kit", "meshy_op", "chibi_criatura_pronto.stl")], 1, 3.0, 1),
}

# Valores do fatiador (PrusaSlicer com site/a1_pla_8.ini: A1, PLA, camada 0,2, 2 paredes, 8 % gyroid).
# gramas, horas, purga extra do AMS (g) estimada para peças de 2 cores. Atualize com o Bambu Studio quando fatiar lá.
FATIADO = {
    "torre": (223.0 + 125.6, 11.29 + 4.51, 0),           # torre + bandeja esculpida (cores em peças separadas: sem purga)
    "bau": (68.8 + 35.1, 2.74 + 1.43, 0),                # base + tampa
    "caixa": (87.9 + 22.1, 3.28 + 0.72, 60),             # base + tampa; emblema na frente troca de cor ~140 camadas
    "relicario": (58.8 + 0.9, 2.08 + 0.09, 3),           # corpo/tampa + topo do medalhão
    "aneis": ((5.62 + 0.25) * 2, (0.20 + 0.05) * 2, 5),  # 8 anéis; texto nas 3 últimas camadas
    "agentes": (3.7, 0.5, 0),                            # miniatura com suporte orgânico
    "mini-agente": (10.8, 0.97, 0),
    "mini-criatura": (9.5, 0.78, 0),
}

if __name__ == "__main__":
    print("== pelo fatiador ==")
    print(f"{'produto':<14}{'gramas':>8}{'horas':>7}{'custo':>10}{'preço':>10}")
    for pid, (g, h, purga) in FATIADO.items():
        custo, p = preco(g + purga, h)
        print(f"{pid:<14}{g + purga:>8.0f}{h:>7.1f}{custo:>10.2f}{p:>10.2f}")
    print("== estimativa pelo volume (antiga) ==")
    print(f"{'produto':<14}{'gramas':>8}{'horas':>7}{'custo':>10}{'preço':>10}")
    for pid, (malhas, cores, horas, copias) in PRODUTOS.items():
        g = gramas(malhas, cores) * copias if cores == 1 else (gramas(malhas, 1) * copias + (cores - 1) * 12)
        horas = max(horas, g / 25)           # a A1 imprime uns 25 g/h em peça grande
        custo, p = preco(g, horas)
        print(f"{pid:<14}{g:>8.0f}{horas:>7.1f}{custo:>10.2f}{p:>10.2f}")
