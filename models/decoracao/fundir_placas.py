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

corpo = man(trimesh.load(f"{OUT}/energia_corpo_placas.stl"))
tudo, preto, branco = corpo, corpo, None
for n, ang in ORDEM.items():
    M = matriz(ang)
    p = trimesh.load(f"relevo/saida/{n}_relevo.stl"); p.apply_transform(M)
    b = trimesh.load(f"relevo/saida/{n}_relevo_cor2.stl"); b.apply_transform(M)
    k = trimesh.load(f"relevo/saida/{n}_relevo_cor1.stl"); k.apply_transform(M)
    tudo = tudo + man(p)
    preto = preto + man(k)
    branco = man(b) if branco is None else branco + man(b)
for nome, x in [("energia_corpo_com_personagens", tudo), ("energia_corpo_com_personagens_cor1_preto", preto), ("energia_corpo_com_personagens_cor2_branco", branco)]:
    tm(x).export(f"{OUT}/{nome}.stl")
    print(nome, trimesh.load(f"{OUT}/{nome}.stl").is_watertight)
