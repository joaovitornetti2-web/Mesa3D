#!/usr/bin/env python3
"""Gera texturas.scad: sulcos do fundo do medalhão, um tema por elemento (baseado no livro):
Sangue = veias (o fluxo), Morte = espiral do tempo, Medo = fragmentos do impossível."""
import numpy as np
from scipy.spatial import Voronoi

R = 20.6   # raio do campo interno (mm)


def veias(seed=11):
    rng = np.random.default_rng(seed)
    linhas = []

    def ramo(p, ang, comp, prof):
        pts = [p]
        for _ in range(int(comp / 1.1)):
            ang += rng.normal(0, 0.28)
            p = p + 1.1 * np.array([np.cos(ang), np.sin(ang)])
            if np.hypot(*p) > R - 0.6:
                break
            pts.append(p)
            if prof < 3 and rng.uniform() < 0.16:
                ramo(p, ang + rng.choice([-1, 1]) * rng.uniform(0.5, 1.0), comp * 0.55, prof + 1)
        if len(pts) > 1:
            linhas.append(pts)

    for k in range(11):
        a = 2 * np.pi * k / 11 + rng.normal(0, 0.15)
        ramo(np.array([np.cos(a), np.sin(a)]) * (R - 0.8), a + np.pi + rng.normal(0, 0.35), 16, 0)
    return linhas


def espiral(passo=1.45):
    t = np.arange(0, R / passo * 2 * np.pi, 0.12)
    r = 1.2 + passo * t / (2 * np.pi)
    t, r = t[r < R - 0.6], r[r < R - 0.6]
    return [np.c_[r * np.cos(-t), r * np.sin(-t)]]


def fragmentos(seed=37, n=26, jit=0.5):
    rng = np.random.default_rng(seed)
    a = rng.uniform(0, 2 * np.pi, n * 3)
    r = R * 1.3 * np.sqrt(rng.uniform(0, 1, n * 3))
    vor = Voronoi(np.c_[r * np.cos(a), r * np.sin(a)])
    out = []
    for (i, j) in vor.ridge_vertices:
        if i < 0 or j < 0:
            continue
        p, q = vor.vertices[i], vor.vertices[j]
        if max(np.hypot(*p), np.hypot(*q)) > R - 0.8 or rng.uniform() < 0.15:
            continue
        out.append([p, p + (q - p) * 0.5 + rng.normal(0, jit, 2), q])
    return out


def raios(seed=53):
    """Raios fractais (figura de Lichtenberg) saindo do centro: o caos da Energia."""
    rng = np.random.default_rng(seed)
    linhas = []

    def ramo(p, ang, prof):
        pts = [p]
        for _ in range([20, 8, 4, 2][prof]):
            ang += rng.normal(0, 0.55)
            p = p + rng.uniform(0.8, 1.4) * np.array([np.cos(ang), np.sin(ang)])
            if np.hypot(*p) > R - 0.6:
                break
            pts.append(p)
            if prof < 3 and rng.uniform() < 0.22:
                ramo(p, ang + rng.choice([-1, 1]) * rng.uniform(0.4, 0.9), prof + 1)
        if len(pts) > 1:
            linhas.append(pts)

    for k in range(9):
        a = 2 * np.pi * k / 9 + rng.normal(0, 0.2)
        ramo(np.array([np.cos(a), np.sin(a)]) * 3.0, a, 0)
    return linhas


with open("texturas.scad", "w") as f:
    f.write("// Gerado por gerar_texturas.py – sulcos do fundo do medalhão\n")
    for nome, ls, w in [("SANGUE", veias(), 0.7), ("MORTE", espiral(), 0.6), ("MEDO", fragmentos(), 0.6), ("ENERGIA", raios(), 0.6)]:
        txt = ",\n  ".join("[" + ", ".join(f"[{x:.2f}, {y:.2f}]" for x, y in l) + "]" for l in ls)
        f.write(f"RACHAS_{nome} = [\n  {txt}\n];\nLARG_{nome} = {w};\n")
        print(nome, len(ls), "linhas,", sum(len(l) for l in ls), "pontos")
