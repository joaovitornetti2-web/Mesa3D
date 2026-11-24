#!/usr/bin/env python3
"""Transforma uma escultura de torre do Meshy numa torre de dados funcional.

Escala a escultura, preenche por dentro (voxels), garante paredes mínimas, escava o canal dos dados
(aberto em cima), a porta de saída na frente e duas rampas a 50° (sem suporte), e o piso inclinado
para a porta. A frente da torre é o lado -Y.

Uso: python3 torre_meshy.py entrada.stl saida.stl [--largura 86] [--girar 0] [--passo 0.4]
"""
import argparse

import numpy as np
import trimesh
from scipy import ndimage
from skimage import measure

ap = argparse.ArgumentParser()
ap.add_argument("entrada"); ap.add_argument("saida")
ap.add_argument("--largura", type=float, default=86, help="maior lado da base (mm)")
ap.add_argument("--girar", type=float, default=0, help="giro em Z (graus) para escolher a face da frente")
ap.add_argument("--passo", type=float, default=0.4, help="tamanho do voxel (mm)")
ap.add_argument("--faces", type=int, default=400000)
ap.add_argument("--suavizar", type=int, default=6, help="passadas de suavização (menos = mais detalhe)")
a = ap.parse_args()

CANAL = 50.0        # canal interno (mm); d20 de 26 mm passa folgado
PAREDE = 4.0        # parede mínima garantida em volta do canal
PORTA_W, PORTA_H = 40.0, 38.0
FUNDO = 2.0
ANG = np.radians(50)

m = trimesh.load(a.entrada, force="mesh")
m.merge_vertices()
# o STL do Meshy já vem com Z para cima
if a.girar:
    m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(a.girar), [0, 0, 1]))
m.apply_scale(a.largura / max(m.extents[:2]))
c = m.bounds.mean(0)
m.apply_translation([-c[0], -c[1], -m.bounds[0][2]])
# o corpo (fatias do meio, sem enfeites da base) precisa caber canal + paredes: senão aumenta a escala
prof = min(m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1]).extents[1] for z in np.linspace(0.3, 0.9, 7) * m.extents[2])
minimo = CANAL + 2 * PAREDE + 2
if prof < minimo:
    m.apply_scale(minimo / prof)
    c = m.bounds.mean(0)
    m.apply_translation([-c[0], -c[1], -m.bounds[0][2]])
    print(f"corpo com {prof:.1f} mm de fundo: escala aumentada {minimo / prof:.2f}x")
H = m.extents[2]
print(f"escultura: {m.extents.round(1)} mm")

# ---- voxeliza e preenche ----
P = a.passo
pts, _ = trimesh.sample.sample_surface(m, int(m.area / (P * P) * 6))
o = m.bounds[0] - 3 * P
idx = np.floor((pts - o) / P).astype(int)
sh = idx.max(0) + 4
G = np.zeros(sh, bool)
G[idx[:, 0], idx[:, 1], idx[:, 2]] = True
G = ndimage.binary_closing(G, iterations=1)
S = ndimage.binary_fill_holes(G)
FECHA = int(round(3.0 / P))   # fecha frestas de até ~6 mm antes de preencher cada fatia
est = ndimage.generate_binary_structure(2, 1)
for k in range(S.shape[2]):   # escultura oca ou com janelas: preenche fatia a fatia
    fat = np.pad(S[:, :, k], FECHA + 1)
    fat = ndimage.binary_closing(fat, structure=est, iterations=FECHA)[FECHA + 1:-FECHA - 1, FECHA + 1:-FECHA - 1]
    S[:, :, k] |= ndimage.binary_fill_holes(fat)
X = np.arange(sh[0]) * P + o[0]; Y = np.arange(sh[1]) * P + o[1]; Z = np.arange(sh[2]) * P + o[2]
XX, YY, ZZ = np.meshgrid(X, Y, Z, indexing="ij")

# altura útil: até onde a escultura ainda cobre o quadrado do canal com parede
cobre = [(S[:, :, k][(np.abs(X) <= CANAL / 2 + PAREDE)[:, None] & (np.abs(Y) <= CANAL / 2 + PAREDE)[None, :]]).mean() for k in range(sh[2])]
topo = max(z for z, f in zip(Z, cobre) if f > 0.97)
print(f"altura total {H:.1f} mm, corpo cheio até {topo:.1f} mm")

meio = CANAL / 2
casca = (np.abs(XX) <= meio + PAREDE) & (np.abs(YY) <= meio + PAREDE) & (ZZ <= topo)
canal = (np.abs(XX) < meio) & (np.abs(YY) < meio) & (ZZ > FUNDO)
S |= casca
S &= ~canal
# porta de saída na frente (-Y), em arco
xa = np.clip(np.abs(XX) / (PORTA_W / 2), 0, 1)
arco = FUNDO + PORTA_H - PORTA_W / 2 + np.sqrt(1 - xa ** 2) * PORTA_W / 2
porta = (np.abs(XX) < PORTA_W / 2) & (YY < 0) & (ZZ > FUNDO) & (ZZ < arco)
S &= ~porta

# rampas (iguais à torre paramétrica, escaladas pela altura útil)
k = topo / 130.0
E = 3.6 / np.cos(ANG)
T = np.tan(ANG)
dentro_x = np.abs(XX) <= meio + 1
zA = 100 * k - (YY + meio) * T            # sai da frente, desce para trás
rA = dentro_x & (YY >= -meio - 1) & (YY <= -meio + 26) & (ZZ <= zA) & (ZZ >= zA - E)
zB = 76 * k - (meio - YY) * T             # sai de trás, desce para a frente
rB = dentro_x & (YY <= meio + 1) & (YY >= meio - 26) & (ZZ <= zB) & (ZZ >= zB - E)
zP = FUNDO + 1.5 + (YY + meio) / CANAL * 38 * k   # piso inclinado para a porta
piso = dentro_x & (np.abs(YY) <= meio + 1) & (ZZ <= zP)
S |= rA | rB | piso
S[:, :, Z < 0] = False
S = ndimage.binary_fill_holes(S)   # bolhas fechadas por dentro viram maciço
lab, n = ndimage.label(S)   # descarta farelos soltos da voxelização
if n > 1:
    S = lab == (1 + int(np.argmax(ndimage.sum(S, lab, range(1, n + 1)))))

v, f, _, _ = measure.marching_cubes(np.pad(S, 1).astype(np.float32), 0.5)
v = (v - 1) * P + o
v[v[:, 2] < P, 2] = 0
r = trimesh.Trimesh(v, f)
r = trimesh.smoothing.filter_taubin(r, iterations=a.suavizar)
if a.faces and len(r.faces) > a.faces:
    r = r.simplify_quadric_decimation(face_count=a.faces)
r.fix_normals()
r.export(a.saida)
print(f"ok {a.saida}: {r.extents.round(1)} mm, {len(r.faces)} faces, estanque={r.is_watertight}, corpos={r.body_count}")
