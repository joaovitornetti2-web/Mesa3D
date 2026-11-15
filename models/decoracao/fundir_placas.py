#!/usr/bin/env python3
"""Funde as placas em relevo no corpo (STL único com os personagens) + versão 2 cores."""
import numpy as np, trimesh, manifold3d as mf, os
ESC = 1.6
R_FUNDO = (38 - 0.8) * ESC
Z0 = 8.5 * ESC + 0.2
ORDEM = {"joui": 270, "labirinto": 225, "dante": 315, "rubens": 180, "balu": 0, "guizo": 135, "chico": 45, "bran": 90}
OUT = "saida_pessoal/50_dados_energia_personagens"

def man(t):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))
def tm(x):
    g = x.to_mesh(); return trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts), process=False)
def matriz(ang):
    a = np.radians(ang); Rz = np.array([[np.cos(a), -np.sin(a), 0, 0], [np.sin(a), np.cos(a), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    T = np.eye(4); T[:3, 3] = (R_FUNDO, 0, Z0)
    B = np.array([[0, 0, 1, 0], [1, 0, 0, -17.4], [0, 1, 0, 0], [0, 0, 0, 1]], float)
    return Rz @ T @ B

import sys
POSTER = "--poster" in sys.argv
corpo = man(trimesh.load(f"{OUT}/energia_corpo_placas.stl"))
tudo, preto, branco, verm = corpo, corpo, None, None
for n, ang in ORDEM.items():
    M = matriz(ang)
    if POSTER:   # pôster 3 cores: cor1 preto, cor2 vermelho, cor3 branco
        f = lambda k: f"personagens/saida/{n}_placa{k}.stl"
        p, k, r, b = (trimesh.load(f(x)) for x in ("", "_cor1", "_cor2", "_cor3"))
    else:
        f = lambda k: f"relevo/saida/{n}_relevo{k}.stl"
        p, k, b = (trimesh.load(f(x)) for x in ("", "_cor1", "_cor2")); r = None
    for t in (p, k, r, b):
        if t is not None: t.apply_transform(M)
    tudo = tudo + man(p); preto = preto + man(k)
    branco = man(b) if branco is None else branco + man(b)
    if r is not None: verm = man(r) if verm is None else verm + man(r)
suf = "_poster" if POSTER else ""
saidas = [(f"energia_corpo_com_personagens{suf}", tudo), (f"energia_corpo_com_personagens{suf}_cor1_preto", preto)]
if verm is not None: saidas.append((f"energia_corpo_com_personagens{suf}_cor2_vermelho", verm))
saidas.append((f"energia_corpo_com_personagens{suf}_cor{3 if verm is not None else 2}_branco", branco))
for nome, x in saidas:
    tm(x).export(f"{OUT}/{nome}.stl")
    print(nome, trimesh.load(f"{OUT}/{nome}.stl").is_watertight)
