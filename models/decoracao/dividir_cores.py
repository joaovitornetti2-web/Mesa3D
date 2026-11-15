#!/usr/bin/env python3
"""Corta o medalhão nas alturas de troca de cor e monta os 3MF (1 cor e N cores).
Uso: python3 dividir_cores.py medalhao.stl Z1[,Z2,...] prefixo_saida"""
import sys
import numpy as np
import trimesh
import manifold3d as mf

src, zs, pre = sys.argv[1], [float(z) for z in sys.argv[2].split(",")], sys.argv[3]
m = trimesh.load(src)
man = mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))


def tm(x):
    g = x.to_mesh()
    t = trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts), process=True)
    t.merge_vertices()
    return t


cortes = [-1e9] + zs + [1e9]
partes = []
for a, b in zip(cortes[:-1], cortes[1:]):
    x = man
    if a > -1e8: x = x.trim_by_plane((0, 0, 1), a)     # z >= a
    if b < 1e8: x = x.trim_by_plane((0, 0, -1), -b)    # z <= b
    partes.append(tm(x))
nome = pre.rsplit("/", 1)[-1]
cena = trimesh.Scene()
for i, p in enumerate(partes, 1):
    cena.add_geometry(p, node_name=f"{nome}_cor{i}", geom_name=f"{nome}_cor{i}")
    p.export(f"{pre}_cor{i}.stl")
n = len(partes)
cena.export(f"{pre}_{n}cores.3mf")
m.export(f"{pre}_1cor.3mf")
print(f"  medalhão: " + ", ".join(f"cor{i} {'fechada' if p.is_watertight else 'ABERTA'}" for i, p in enumerate(partes, 1))
      + f"; trocas de cor em z = {', '.join(str(z) for z in zs)} mm")
