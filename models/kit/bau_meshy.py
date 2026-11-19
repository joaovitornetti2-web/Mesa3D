#!/usr/bin/env python3
"""Transforma uma escultura de baú do Meshy num baú de dados de verdade: base oca + tampa com encaixe.

Escala, preenche por dentro (voxels), corta na altura da tampa, escava a cavidade da base com parede
mínima, sobe uma borda de encaixe na base e abre na tampa o rebaixo onde essa borda entra.

Uso: python3 bau_meshy.py entrada.stl pasta_saida [--largura 104] [--corte 0.70] [--passo 0.35]
Saída: <pasta>/bau_base.stl, <pasta>/bau_tampa.stl (na posição montada; a tampa imprime de pé,
com suporte só no rebaixo de baixo).
"""
import argparse
import os

import numpy as np
import trimesh
from scipy import ndimage
from skimage import measure

ap = argparse.ArgumentParser()
ap.add_argument("entrada"); ap.add_argument("pasta")
ap.add_argument("--largura", type=float, default=104, help="maior lado (mm)")
ap.add_argument("--corte", type=float, default=0.70, help="altura do corte da tampa (fração da altura)")
ap.add_argument("--passo", type=float, default=0.35)
ap.add_argument("--faces", type=int, default=300000)
a = ap.parse_args()

PAREDE, FUNDO = 5.0, 4.0
LABIO_H, LABIO_W, FOLGA = 4.0, 1.8, 0.35

m = trimesh.load(a.entrada, force="mesh")
m.merge_vertices()
m.apply_scale(a.largura / max(m.extents[:2]))
c = m.bounds.mean(0)
m.apply_translation([-c[0], -c[1], -m.bounds[0][2]])
H = m.extents[2]
print(f"escultura: {m.extents.round(1)} mm")

P = a.passo
pts, _ = trimesh.sample.sample_surface(m, int(m.area / (P * P) * 6))
o = m.bounds[0] - 3 * P
idx = np.floor((pts - o) / P).astype(int)
sh = idx.max(0) + 4 + np.array([0, 0, int(LABIO_H / P) + 2])
G = np.zeros(sh, bool)
G[idx[:, 0], idx[:, 1], idx[:, 2]] = True
G = ndimage.binary_closing(G, iterations=1)
S = ndimage.binary_fill_holes(G)
F = int(round(3.0 / P))
est = ndimage.generate_binary_structure(2, 1)
for k in range(S.shape[2]):
    fat = np.pad(S[:, :, k], F + 1)
    fat = ndimage.binary_erosion(ndimage.binary_fill_holes(ndimage.binary_dilation(fat, structure=est, iterations=F)), structure=est, iterations=F)
    S[:, :, k] |= fat[F + 1:-F - 1, F + 1:-F - 1]
S = ndimage.binary_fill_holes(S)
Z = np.arange(sh[2]) * P + o[2]
zc = a.corte * H
kc = int(np.searchsorted(Z, zc))

# fundo: a partir da primeira fatia "cheia" (o baú pode ter pés nos cantos)
area = S.sum((0, 1))
zcheio = Z[int(np.argmax(area >= 0.85 * area[:kc].max()))]
FUNDO = zcheio + FUNDO
print(f"corpo cheio a partir de {zcheio:.1f} mm")
# cavidade: o que sobra de TODAS as fatias entre o fundo e o corte depois de tirar a parede
cav = np.ones(sh[:2], bool)
for k in range(int(np.searchsorted(Z, FUNDO)), kc):
    cav &= ndimage.binary_erosion(S[:, :, k], structure=est, iterations=int(round(PAREDE / P)))
cav = ndimage.binary_opening(cav, structure=est, iterations=3)
lab, n = ndimage.label(cav)
cav = lab == (1 + int(np.argmax(ndimage.sum(cav, lab, range(1, n + 1)))))
ys, xs = np.where(cav.T)
print(f"cavidade: {(np.ptp(xs) + 1) * P:.0f} × {(np.ptp(ys) + 1) * P:.0f} mm, {zc - FUNDO:.0f} mm de fundo")

labio = ndimage.binary_dilation(cav, structure=est, iterations=int(round(LABIO_W / P))) & ~cav
rebaixo = ndimage.binary_dilation(cav | labio, structure=est, iterations=max(1, int(round(FOLGA / P))))

base = S.copy(); base[:, :, kc:] = False
for k in range(int(np.searchsorted(Z, FUNDO)), kc):
    base[:, :, k] &= ~cav
kl = int(np.searchsorted(Z, zc + LABIO_H))
base[:, :, kc:kl] |= labio[:, :, None]

tampa = S.copy(); tampa[:, :, :kc] = False
kr = int(np.searchsorted(Z, zc + LABIO_H + FOLGA))
tampa[:, :, kc:kr] &= ~rebaixo[:, :, None]


def salvar(V, nome):
    lab, n = ndimage.label(V)
    if n > 1:
        V = lab == (1 + int(np.argmax(ndimage.sum(V, lab, range(1, n + 1)))))
    v, f, _, _ = measure.marching_cubes(np.pad(V, 1).astype(np.float32), 0.5)
    v = (v - 1) * P + o
    r = trimesh.Trimesh(v, f)
    r = trimesh.smoothing.filter_taubin(r, iterations=6)
    if len(r.faces) > a.faces:
        r = r.simplify_quadric_decimation(face_count=a.faces)
    r.fix_normals()
    caminho = os.path.join(a.pasta, nome)
    r.export(caminho)
    print(f"ok {caminho}: {r.extents.round(1)} mm, {len(r.faces)} faces, corpos={r.body_count}")


os.makedirs(a.pasta, exist_ok=True)
salvar(base, "bau_base.stl")
salvar(tampa, "bau_tampa.stl")
