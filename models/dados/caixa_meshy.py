#!/usr/bin/env python3
"""Caixa de dados elemental esculpida: escultura do Meshy + cavidade, tampa com encaixe e o emblema
de cada elemento embutido no medalhão liso da frente (lado -Y; segunda cor, 0,7 mm de profundidade).

Uso: python3 caixa_meshy.py escultura.stl pasta_saida [--largura 104] [--corte 0.62] [--emblema 30]
Saída: <pasta>/caixa_tampa.stl e, para cada elemento, <pasta>/base_<elemento>_cor1.stl e _cor2.stl,
tudo na posição montada. Os emblemas vêm de emblemas/<elemento>.stl (gerados de caixa_elementos.scad).
"""
import argparse
import os

import numpy as np
import trimesh
from scipy import ndimage
from skimage import measure

AQUI = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("entrada"); ap.add_argument("pasta")
ap.add_argument("--largura", type=float, default=104)
ap.add_argument("--corte", type=float, default=0.84, help="altura do corte da tampa (fração da altura)")
ap.add_argument("--emblema", type=float, default=28, help="diâmetro do emblema no medalhão da frente (mm)")
ap.add_argument("--passo", type=float, default=0.3)
ap.add_argument("--faces", type=int, default=300000)
ap.add_argument("--elementos", default="sangue,morte,conhecimento,energia,medo")
a = ap.parse_args()

PAREDE, FUNDO = 5.0, 4.0
LABIO_H, LABIO_W, FOLGA = 4.0, 1.8, 0.35
INLAY = 0.7

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
X = np.arange(sh[0]) * P + o[0]; Y = np.arange(sh[1]) * P + o[1]; Z = np.arange(sh[2]) * P + o[2]
zc = a.corte * H
kc = int(np.searchsorted(Z, zc))

area = S.sum((0, 1))
zcheio = Z[int(np.argmax(area >= 0.85 * area[:kc].max()))]
fundo = max(zcheio + FUNDO, zc - 34)   # cavidade de no máximo 34 mm de fundo (dá para pegar os dados)
cav = np.ones(sh[:2], bool)
for k in range(int(np.searchsorted(Z, fundo)), kc):
    cav &= ndimage.binary_erosion(S[:, :, k], structure=est, iterations=int(round(PAREDE / P)))
cav = ndimage.binary_opening(cav, structure=est, iterations=3)
lab, n = ndimage.label(cav)
cav = lab == (1 + int(np.argmax(ndimage.sum(cav, lab, range(1, n + 1)))))
ys, xs = np.where(cav.T)
print(f"cavidade: {(np.ptp(xs) + 1) * P:.0f} × {(np.ptp(ys) + 1) * P:.0f} mm, {zc - fundo:.0f} mm de fundo")

labio = ndimage.binary_dilation(cav, structure=est, iterations=int(round(LABIO_W / P))) & ~cav
rebaixo = ndimage.binary_dilation(cav | labio, structure=est, iterations=max(1, int(round(FOLGA / P))))
base = S.copy(); base[:, :, kc:] = False
for k in range(int(np.searchsorted(Z, fundo)), kc):
    base[:, :, k] &= ~cav
base[:, :, kc:int(np.searchsorted(Z, zc + LABIO_H))] |= labio[:, :, None]
tampa = S.copy(); tampa[:, :, :kc] = False
tampa[:, :, kc:int(np.searchsorted(Z, zc + LABIO_H + FOLGA))] &= ~rebaixo[:, :, None]

# frente (-Y): primeira coluna cheia vista de frente, para cada (x, z)
tem = base.any(1)
jfrente = np.where(tem, np.argmax(base, axis=1), sh[1])
cx = (X[tem.any(1)].min() + X[tem.any(1)].max()) / 2
# centro do medalhão: o disco mais plano da frente entre 30 % e 70 % da altura
r_px = int(a.emblema / 2 / P) + 2
xi = int(np.searchsorted(X, cx))
melhor, cz = 1e9, H / 2
for zz in np.arange(0.3 * H, 0.7 * H, 1.0):
    zi = int(np.searchsorted(Z, zz))
    bloco = jfrente[xi - r_px:xi + r_px, zi - r_px:zi + r_px].astype(float)
    if bloco.size and (bloco < sh[1]).all() and bloco.std() < melhor:
        melhor, cz = bloco.std(), zz
print(f"medalhão da frente em x={cx:.1f}, z={cz:.1f} mm (variação {melhor * P:.2f} mm)")


def salvar(V, nome):
    lab, n = ndimage.label(V)
    if n > 1:
        V = np.isin(lab, 1 + np.where(ndimage.sum(V, lab, range(1, n + 1)) > 50)[0])
    v, f, _, _ = measure.marching_cubes(np.pad(V, 1).astype(np.float32), 0.5)
    v = (v - 1) * P + o
    r = trimesh.Trimesh(v, f)
    r = trimesh.smoothing.filter_taubin(r, iterations=6)
    if len(r.faces) > a.faces:
        r = r.simplify_quadric_decimation(face_count=a.faces)
    r.fix_normals()
    caminho = os.path.join(a.pasta, nome)
    r.export(caminho)
    print(f"ok {caminho}: {r.extents.round(1)} mm, {len(r.faces)} faces")


def mascara(e):
    """Emblema rasterizado na grade XY, centrado no medalhão e com o diâmetro pedido."""
    em = trimesh.load(os.path.join(AQUI, "emblemas", f"{e}.stl"))
    em.apply_translation([-em.bounds.mean(0)[0], -em.bounds.mean(0)[1], 0])
    em.apply_scale([a.emblema / max(em.extents[:2]), a.emblema / max(em.extents[:2]), 1])
    XX, YY = np.meshgrid(X - cx, Z - cz, indexing="ij")   # plano da frente: x e altura
    pts2 = np.column_stack([XX.ravel(), YY.ravel(), np.full(XX.size, 0.5)])
    perto = (np.abs(pts2[:, 0]) <= a.emblema / 2 + 1) & (np.abs(pts2[:, 1]) <= a.emblema / 2 + 1)
    dentro = np.zeros(XX.size, bool)
    dentro[perto] = em.contains(pts2[perto])
    return dentro.reshape(XX.shape)


os.makedirs(a.pasta, exist_ok=True)
salvar(tampa, "caixa_tampa.stl")
prof = int(round(INLAY / P))
JJ = np.arange(sh[1])[None, :, None]
for e in a.elementos.split(","):
    mk = mascara(e) & tem                      # (x, z)
    cor2 = base & mk[:, None, :] & (JJ < (jfrente[:, None, :] + prof))
    salvar(base & ~cor2, f"base_{e}_cor1.stl")
    salvar(cor2, f"base_{e}_cor2.stl")
