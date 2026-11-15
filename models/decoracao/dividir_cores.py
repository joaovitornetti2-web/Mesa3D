#!/usr/bin/env python3
"""Corta o medalhão na altura da troca de cor e monta os 3MF (1 cor e 2 cores).
Uso: python3 dividir_cores.py medalhao.stl Z_COR prefixo_saida"""
import sys
import numpy as np
import trimesh
import manifold3d as mf

src, zc, pre = sys.argv[1], float(sys.argv[2]), sys.argv[3]
m = trimesh.load(src)
man = mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))


def tm(x):
    g = x.to_mesh()
    t = trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts), process=True)
    t.merge_vertices()
    return t


baixo = tm(man.trim_by_plane((0, 0, -1), -zc))   # z <= zc
cima = tm(man.trim_by_plane((0, 0, 1), zc))      # z >= zc
nome = pre.rsplit("/", 1)[-1]
cena = trimesh.Scene()
cena.add_geometry(baixo, node_name=f"{nome}_cor1", geom_name=f"{nome}_cor1")
cena.add_geometry(cima, node_name=f"{nome}_cor2_topo", geom_name=f"{nome}_cor2_topo")
cena.export(f"{pre}_2cores.3mf")
m.export(f"{pre}_1cor.3mf")
baixo.export(f"{pre}_cor1.stl")
cima.export(f"{pre}_cor2.stl")
print(f"  medalhão: cor1 {baixo.is_watertight}, cor2 {cima.is_watertight} (fechadas), troca de cor em z={zc} mm")
