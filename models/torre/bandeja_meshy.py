#!/usr/bin/env python3
"""Bandeja esculpida da Torre do Ritual: borda do Meshy + fundo liso com moldura da torre e sigilo gravado.

Escala a escultura, preenche (voxels), corta o excesso de baixo, escava um fundo liso por dentro,
grava o sigilo com runas (0,8 mm) e sobe a moldura de encaixe da torre (1,6 mm).
As máscaras do fundo vêm de bandeja_mascaras.scad (ritual/mascaras/gravura.stl e moldura.stl).

Uso: python3 bandeja_meshy.py escultura.stl saida.stl [--largura 190] [--corte 14] [--interno 158x154]
"""
import argparse
import os

import numpy as np
import trimesh
from scipy import ndimage
from skimage import measure

AQUI = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("entrada"); ap.add_argument("saida")
ap.add_argument("--largura", type=float, default=190)
ap.add_argument("--corte", type=float, default=14, help="mm removidos de baixo (a escultura vem muito grossa)")
ap.add_argument("--interno", default="158x154", help="fundo liso interno, largura x profundidade (mm)")
ap.add_argument("--fundo", type=float, default=3.0, help="espessura do fundo (mm)")
ap.add_argument("--passo", type=float, default=0.25)
ap.add_argument("--fecha", type=float, default=1.0, help="fecha frestas até 2x este valor antes de preencher (mm); menor = mais detalhe")
ap.add_argument("--faces", type=int, default=700000)
a = ap.parse_args()
IX, IY = (float(v) for v in a.interno.split("x"))

m = trimesh.load(a.entrada, force="mesh")
m.merge_vertices()
m.apply_scale(a.largura / max(m.extents[:2]))
c = m.bounds.mean(0)
m.apply_translation([-c[0], -c[1], -m.bounds[0][2]])
print(f"escultura: {m.extents.round(1)} mm")

P = a.passo
pts, _ = trimesh.sample.sample_surface(m, int(m.area / (P * P) * 6))
o = m.bounds[0] - 3 * P
idx = np.floor((pts - o) / P).astype(int)
sh = idx.max(0) + 4
G = np.zeros(sh, bool)
G[idx[:, 0], idx[:, 1], idx[:, 2]] = True
G = ndimage.binary_closing(G, iterations=1)
S = ndimage.binary_fill_holes(G)
F = max(1, int(round(a.fecha / P)))
est = ndimage.generate_binary_structure(2, 1)
for k in range(S.shape[2]):
    fat = np.pad(S[:, :, k], F + 1)
    fat = ndimage.binary_erosion(ndimage.binary_fill_holes(ndimage.binary_dilation(fat, structure=est, iterations=F)), structure=est, iterations=F)
    S[:, :, k] |= fat[F + 1:-F - 1, F + 1:-F - 1]
S = ndimage.binary_fill_holes(S)

# corta o excesso de baixo e desce tudo
kcorte = int(round(a.corte / P))
S = S[:, :, kcorte:]
X = np.arange(sh[0]) * P + o[0]; Y = np.arange(sh[1]) * P + o[1]; Z = np.arange(S.shape[2]) * P
# centro da borda (pela silhueta logo acima do corte)
base2d = S[:, :, int(2 / P)]
cx = (X[base2d.any(1)].min() + X[base2d.any(1)].max()) / 2
cy = (Y[base2d.any(0)].min() + Y[base2d.any(0)].max()) / 2
XX, YY = np.meshgrid(X - cx, Y - cy, indexing="ij")
interno = (np.abs(XX) <= IX / 2) & (np.abs(YY) <= IY / 2)
kf = int(round(a.fundo / P))
S[:, :, :kf] |= base2d[:, :, None] | interno[:, :, None]   # fundo inteiro e cheio
S[:, :, kf:] &= ~interno[:, :, None]                         # fundo liso por dentro


from shapely import contains_xy


def mascara(nome):
    """Rasteriza uma máscara 2D (fatia de um STL extrudado) na grade XY, centrada no fundo."""
    em = trimesh.load(os.path.join(AQUI, "ritual", "mascaras", f"{nome}.stl"))
    sec = em.section(plane_origin=[0, 0, 0.5], plane_normal=[0, 0, 1])
    pts2 = np.column_stack([XX.ravel(), YY.ravel()])
    dentro = np.zeros(len(pts2), bool)
    for poly in sec.to_2D(to_2D=np.eye(4))[0].polygons_full:
        bx = poly.bounds
        perto = (pts2[:, 0] >= bx[0]) & (pts2[:, 0] <= bx[2]) & (pts2[:, 1] >= bx[1]) & (pts2[:, 1] <= bx[3])
        dentro[perto] |= contains_xy(poly, pts2[perto, 0], pts2[perto, 1])
    return dentro.reshape(XX.shape)


grav = mascara("gravura") & interno
mold = mascara("moldura")   # pode encostar na borda

kg = int(round(0.8 / P))
S[:, :, kf - kg:kf] &= ~grav[:, :, None]                         # gravura de 0,8 mm no fundo
S[:, :, kf:kf + int(round(1.6 / P))] |= mold[:, :, None]          # moldura de 1,6 mm

lab, n = ndimage.label(S)
if n > 1:
    S = lab == (1 + int(np.argmax(ndimage.sum(S, lab, range(1, n + 1)))))
v, f, _, _ = measure.marching_cubes(np.pad(S, 1).astype(np.float32), 0.5)
v = (v - 1) * P + np.array([o[0], o[1], 0])
v[v[:, 2] < P, 2] = 0
r = trimesh.Trimesh(v, f)
r = trimesh.smoothing.filter_taubin(r, iterations=2)
if len(r.faces) > a.faces:
    r = r.simplify_quadric_decimation(face_count=a.faces)
r.fix_normals()
r.apply_translation([-cx, -cy, 0])
r.export(a.saida)
print(f"ok {a.saida}: {r.extents.round(1)} mm, {len(r.faces)} faces; fundo em z={a.fundo} mm, centro do fundo na origem")
