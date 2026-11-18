#!/usr/bin/env python3
"""Prepara uma miniatura do Meshy na escala 28–32 mm, mantendo a malha original (todo o detalhe):
escala pela altura da figura (pés ao topo) e envolve a base do Meshy numa base lisa de 25 mm.
Saída: um STL com a figura + a base (o Bambu Studio une as duas ao fatiar).

Uso: python3 preparar_mini.py entrada.stl saida.stl --altura 31 [--base 25]
"""
import argparse
import numpy as np
import trimesh

ap = argparse.ArgumentParser()
ap.add_argument("entrada"); ap.add_argument("saida")
ap.add_argument("--altura", type=float, required=True, help="altura da figura dos pés ao ponto mais alto (mm)")
ap.add_argument("--base", type=float, default=25.0)
ap.add_argument("--triangulos", type=int, default=600000, help="reduz a malha para este nº de triângulos (0 = não reduz)")
a = ap.parse_args()

m = trimesh.load(a.entrada, force="mesh")
m.merge_vertices()
m.update_faces(m.nondegenerate_faces()); m.remove_unreferenced_vertices()
alt = int(np.argmax(m.extents))
if alt == 0:
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
elif alt == 1:
    m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
m.apply_translation([0, 0, -m.bounds[0][2]])
H = m.extents[2]
V = m.vertices
pe = V[V[:, 2] < H * 0.01]
c = (pe[:, :2].max(0) + pe[:, :2].min(0)) / 2
R0 = np.ptp(pe[:, :2], axis=0).max() / 2
rad = np.linalg.norm(V[:, :2] - c, axis=1)
# topo da base do Meshy = plano com mais vértices entre 2% e 15% da altura (a face de cima da base)
zz = V[:, 2][(V[:, 2] > H * 0.02) & (V[:, 2] < H * 0.15)]
cont, bordas = np.histogram(zz, bins=int(0.13 / 0.004))
zb = float(bordas[np.argmax(cont) + 1])
esc = a.altura / (H - zb)
m.apply_translation([-c[0], -c[1], 0])
m.apply_scale(esc)
zb *= esc
R0 *= esc
print(f"escala {esc:.5f}  base do Meshy: Ø{2 * R0:.1f} × {zb:.2f} mm  altura total {m.extents[2]:.1f} mm")

if a.triangulos and len(m.faces) > a.triangulos:   # 2 milhões de triângulos é demais para 3 cm; 600 mil guarda o detalhe
    m = m.simplify_quadric_decimation(face_count=a.triangulos)

# base lisa de 25 mm com chanfro, da altura da base do Meshy (que fica embutida nela)
hb = max(zb, 2.0)
perfil = [[0, 0], [a.base / 2, 0], [a.base / 2, hb - 0.6], [a.base / 2 - 0.6, hb], [0, hb]]
base = trimesh.creation.revolve(perfil, sections=128)
out = trimesh.util.concatenate([m, base])
out.export(a.saida)
print(f"ok {a.saida}: {np.round(out.extents, 1)} mm, figura {len(m.faces)} triângulos")
