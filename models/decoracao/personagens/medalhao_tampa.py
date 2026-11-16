#!/usr/bin/env python3
"""Medalhão da tampa (relicário 50 dados) com o símbolo enviado: base PRETA, aro e miolos VERMELHOS, símbolo BRANCO."""
import os, numpy as np, trimesh, manifold3d as mf
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
E = 1.6; R_MED, ASSENTO = 31 * E, 2.0 * E
Z_PLACA, Z_VERM, Z_BRANCO = ASSENTO + 0.8, ASSENTO + 1.6, ASSENTO + 2.6
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "simbolos")
m = np.asarray(Image.open(f"{S}/tampa_r12.png").convert("L")) < 128
ys, xs = np.nonzero(m); cyx = np.array([(ys.min() + ys.max()) / 2, (xs.min() + xs.max()) / 2])
rmax = np.sqrt(((np.c_[ys, xs] - cyx) ** 2).sum(1)).max()
PX = (R_MED - 4.5) / rmax                       # mm por pixel
furos = ndi.binary_fill_holes(m) & ~m
lab, n = ndi.label(furos); ar = ndi.sum(furos, lab, range(1, n + 1))
sl = ndi.find_objects(lab)
def redondo(i):
    h = sl[i][0].stop - sl[i][0].start; w = sl[i][1].stop - sl[i][1].start
    return 0.8 < h / w < 1.25 and 0.68 < ar[i] / (h * w) < 0.86 and ar[i] * PX * PX > 8
miolos = np.isin(lab, [i + 1 for i in range(n) if redondo(i)])   # só os miolos redondos dos círculos

def contorno(mask, folga=0.01):
    g = ndi.gaussian_filter(np.pad(mask, 2).astype(float), 1.2)
    polys = [np.c_[((c[:, 1] - 2) - cyx[1]) * PX, (cyx[0] - (c[:, 0] - 2)) * PX] for c in measure.find_contours(g, 0.5) if len(c) > 4]
    return mf.CrossSection(polys, mf.FillRule.EvenOdd).simplify(0.02).offset(folga, mf.JoinType.Round)

def tm(x):
    g = x.to_mesh(); return trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts), process=False)

disco = mf.CrossSection.circle(R_MED - 0.05, 200)
aro = mf.CrossSection.circle(R_MED - 0.05, 200) - mf.CrossSection.circle(R_MED - 2.2, 200)
branco2d = contorno(m) ^ disco.offset(-2.6, mf.JoinType.Round)
verm2d = (contorno(miolos) + aro) ^ disco
perfil = mf.CrossSection([np.array([(0, 0), (R_MED - ASSENTO, 0), (R_MED, ASSENTO), (R_MED, Z_PLACA), (0, Z_PLACA)])], mf.FillRule.EvenOdd)
base = perfil.revolve(200)
verm = verm2d.extrude(Z_VERM - Z_PLACA + 0.1).translate((0, 0, Z_PLACA - 0.1))
bran = branco2d.extrude(Z_BRANCO - Z_PLACA + 0.1).translate((0, 0, Z_PLACA - 0.1))
p1 = base
p3 = branco2d.extrude(Z_BRANCO - Z_PLACA).translate((0, 0, Z_PLACA))
p2 = (verm2d - branco2d.offset(0.02, mf.JoinType.Round)).extrude(Z_VERM - Z_PLACA).translate((0, 0, Z_PLACA))
os.makedirs("saida", exist_ok=True)
tm(base + verm + bran).export("saida/tampa_simbolo_medalhao.stl")
cena = trimesh.Scene()
for i, (p, c) in enumerate(((p1, "preto"), (p2, "vermelho"), (p3, "branco")), 1):
    t = tm(p); t.export(f"saida/tampa_simbolo_medalhao_cor{i}.stl"); cena.add_geometry(t, node_name=f"cor{i}_{c}", geom_name=f"cor{i}_{c}")
cena.export("saida/tampa_simbolo_medalhao_3cores.3mf")
for f in ("", "_cor1", "_cor2", "_cor3"):
    print(f or "inteiro", trimesh.load(f"saida/tampa_simbolo_medalhao{f}.stl").is_watertight)
