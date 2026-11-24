"""Chapéu de Mago Espiral – o cone espiral sensorial virou um chapéu de mago de aba larga, curvinho para dentro,
com estrelinhas e uma lua em relevo. Continua sendo uma fita em espiral só, impressa já montada:
empurre a ponta e ela atravessa as voltas. Mesmo corte do cone antigo (passo 2,6 mm, folga 0,5 mm). 1 cor."""
import os, sys
import numpy as np
import trimesh
from skimage import measure

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.12
H, RB, ABA = 56.0, 22.0, 31.0
PASSO_ESP, FOLGA = 2.6, 0.5
xs = np.arange(-ABA - 1.5, ABA + 1.5, passo)
zs = np.arange(0, H + 1, passo)
X, Y = np.meshgrid(xs, xs, indexing="ij")
r = np.hypot(X, Y); th = np.arctan2(Y, X)
# relevos: estrelinhas (domos) e lua no lado da frente
domos = [(-90, 12, 2.2), (-60, 22, 1.7), (-120, 28, 1.6), (-75, 36, 1.3), (-100, 43, 1.1), (60, 15, 2.0), (150, 24, 1.8), (20, 31, 1.4), (200, 9, 2.0), (110, 38, 1.2), (250, 30, 1.5)]
S = np.zeros((len(xs), len(xs), len(zs)), bool)
for k, z in enumerate(zs):
    t = z / H
    rr = RB * (1 - t) ** 1.25                              # cone curvinho para dentro
    if z > H - 2.5:
        rr = min(rr, np.sqrt(max(0.0, 2.5 ** 2 - (z - (H - 2.5)) ** 2)) + 0.4)
    R = np.full_like(r, rr)
    if z < 2.4:
        R[:] = ABA - 1.2 * (z / 2.4) ** 2                  # aba (uma volta da fita)
    elif z < 4.2:
        R[:] = rr + (ABA - rr) * max(0.0, 1 - (z - 2.4) / 1.8) ** 2.2
    # faixa do chapéu
    R += 1.2 * np.exp(-((z - 7.5) / 1.6) ** 4)
    for (ang, zc, rd) in domos:
        a = np.radians(ang)
        dang = np.angle(np.exp(1j * (th - a)))
        d2 = (dang * max(rr, 4)) ** 2 + (z - zc) ** 2
        R += np.where(d2 < rd ** 2, np.sqrt(np.maximum(rd ** 2 - d2, 0)) * 0.8, 0)
    # lua minguante em relevo na frente (-Y)
    dang = np.angle(np.exp(1j * (th + np.pi / 2)))
    lx, lz = dang * max(rr, 4), z - 20
    lua = (np.hypot(lx, lz) < 5.2) & (np.hypot(lx - 2.6, lz - 1.2) > 4.3)
    R += np.where(lua, 0.9, 0)
    dentro = r <= R
    fase = np.mod(z / PASSO_ESP - th / (2 * np.pi), 1.0)
    dentro &= fase >= FOLGA / PASSO_ESP
    S[:, :, k] = dentro
v, f, _, _ = measure.marching_cubes(np.pad(S, 1).astype(np.float32), 0.5)
v = (v - 1) * passo + np.array([xs[0], xs[0], 0])
m = trimesh.Trimesh(v, f[:, ::-1], process=True)
partes = [p for p in m.split(only_watertight=False) if p.area > 4]
m = trimesh.util.concatenate(partes)
trimesh.smoothing.filter_taubin(m, iterations=4)
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
os.makedirs(d, exist_ok=True)
m.export(os.path.join(d, "cone_c1.stl"))
print("cone", len(m.faces), len(partes), "pedaço(s)")
