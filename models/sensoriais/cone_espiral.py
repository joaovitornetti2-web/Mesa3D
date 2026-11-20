#!/usr/bin/env python3
"""Cone espiral sensorial (impresso já montado): um cone cortado por uma lâmina helicoidal fina.
Vira uma fita em espiral contínua; empurrando a ponta, ela atravessa as voltas.

Uso: python3 cone_espiral.py saida.stl [--diametro 46] [--altura 50] [--passo 2.6] [--folga 0.5]
"""
import argparse

import numpy as np
import trimesh
from skimage import measure

ap = argparse.ArgumentParser()
ap.add_argument("saida")
ap.add_argument("--diametro", type=float, default=46)
ap.add_argument("--altura", type=float, default=50)
ap.add_argument("--passo", type=float, default=2.6, help="altura de cada volta da fita (mm)")
ap.add_argument("--folga", type=float, default=0.5, help="espessura do corte entre as voltas (mm)")
ap.add_argument("--voxel", type=float, default=0.12)
ap.add_argument("--faces", type=int, default=500000)
a = ap.parse_args()

R, H, P = a.diametro / 2, a.altura, a.voxel
xs = np.arange(-R - 1, R + 1, P)
zs = np.arange(0, H + 1, P)
X, Y = np.meshgrid(xs, xs, indexing="ij")
r = np.hypot(X, Y)
th = np.arctan2(Y, X)
S = np.zeros((len(xs), len(xs), len(zs)), bool)
ponta = 3.0                                                     # ponta arredondada
for k, z in enumerate(zs):
    rr = R * (1 - z / H)                                        # raio do cone nesta altura
    if z > H - ponta:                                           # arredonda a ponta
        rr = min(rr, np.sqrt(max(0.0, ponta ** 2 - (z - (H - ponta)) ** 2)))
    dentro = r <= rr
    if True:                                                    # corte em toda a altura: a ponta precisa atravessar até a base
        fase = np.mod(z / a.passo - th / (2 * np.pi), 1.0)
        dentro &= fase >= a.folga / a.passo
    S[:, :, k] = dentro
v, f, _, _ = measure.marching_cubes(np.pad(S, 1).astype(np.float32), 0.5)
v = (v - 1) * P + np.array([xs[0], xs[0], 0])
v[v[:, 2] < P, 2] = 0
m = trimesh.Trimesh(v, f)
m = trimesh.smoothing.filter_taubin(m, iterations=3)
if len(m.faces) > a.faces:
    m = m.simplify_quadric_decimation(face_count=a.faces)
m.fix_normals()
m.export(a.saida)
print(f"ok {a.saida}: {m.extents.round(1)} mm, {len(m.faces)} faces, corpos={m.body_count}")
