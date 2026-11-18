#!/usr/bin/env python3
"""Desenho em linha (PNG com as linhas no canal alfa) -> mini quadro em relevo de 2 cores.
Placa branca, desenho em preto 0,6 mm em relevo, moldura preta, furo de pendurar e suporte de mesa.

Uso: python3 quadro.py desenho.png [--girar -90] [--largura 140]
Saída (pasta saida/): quadro_branco.stl, quadro_preto.stl, quadro_2cores.3mf, suporte.stl, preview.png
"""
import argparse, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
import manifold3d as mf
import trimesh

ap = argparse.ArgumentParser()
ap.add_argument("desenho")
ap.add_argument("--girar", type=float, default=-90, help="graus (negativo = horário)")
ap.add_argument("--largura", type=float, default=140, help="largura da área do desenho (mm)")
ap.add_argument("--moldura", type=float, default=9, help="largura da moldura (mm)")
a = ap.parse_args()

PX = 0.1                       # mm por pixel na placa
Z_PLACA, Z_LINHA, Z_MOLD = 2.0, 2.6, 4.5
LINHA_MIN = 0.6                # linha mais fina que o bico 0,4 imprime bem
MARGEM = 4                     # respiro entre desenho e moldura (mm)

im = Image.open(a.desenho).convert("RGBA")
alfa = np.asarray(im)[..., 3]
lum = np.asarray(im.convert("L"))
linhas = alfa if alfa.min() < 250 else 255 - lum          # linhas no alfa (fundo transparente) ou escuras no branco
img = Image.fromarray(linhas).rotate(a.girar, expand=True, resample=Image.BICUBIC)
# recorta ao desenho
m0 = np.asarray(img) > 60
ys, xs = np.nonzero(m0)
img = img.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
W = int(round(a.largura / PX)); H = int(round(img.height * W / img.width))
m = np.asarray(img.resize((W, H), Image.LANCZOS)).astype(float) / 255
mask = m > 0.35
# engrossa as linhas até LINHA_MIN: dilata só onde a linha é mais fina que o mínimo
esp = ndi.distance_transform_edt(mask) * 2 * PX           # espessura local aproximada
fina = mask & (esp < LINHA_MIN)
r = int(np.ceil((LINHA_MIN / 2) / PX))
mask = mask | ndi.binary_dilation(fina, iterations=max(1, r - 1))
mask = ndi.gaussian_filter(mask.astype(float), 0.8) > 0.5
# tira sujeira: ilhas < 0,25 mm² e furinhos < 0,15 mm² (que não imprimem)
for alvo, amin in ((mask, 0.25), (~mask, 0.15)):
    lab, n = ndi.label(alvo)
    if n:
        ar = ndi.sum(alvo, lab, range(1, n + 1)) * PX * PX
        peq = np.isin(lab, 1 + np.nonzero(ar < amin)[0])
        mask = (mask & ~peq) if alvo is mask else (mask | peq)
art_w, art_h = W * PX, H * PX
LX = art_w + 2 * (MARGEM + a.moldura); LY = art_h + 2 * (MARGEM + a.moldura)
print(f"desenho {art_w:.0f}×{art_h:.0f} mm  quadro {LX:.0f}×{LY:.0f} mm")

def contorno(mk, folga=0.01):
    mm = ndi.gaussian_filter(ndi.zoom(np.pad(mk, 2).astype(float), 2, order=1), 0.9)
    polys = []
    for c in measure.find_contours(mm, 0.5):
        if len(c) >= 4:
            x = (c[:, 1] / 2 - 2) * PX + a.moldura + MARGEM
            y = LY - ((c[:, 0] / 2 - 2) * PX + a.moldura + MARGEM)
            polys.append(np.c_[x, y])
    return mf.CrossSection(polys, mf.FillRule.EvenOdd).simplify(0.02).offset(folga, mf.JoinType.Round)

def ret(x0, y0, x1, y1, r=0):
    c = mf.CrossSection.square((x1 - x0 - 2 * r, y1 - y0 - 2 * r)).translate((x0 + r, y0 + r))
    return c.offset(r, mf.JoinType.Round, circular_segments=48) if r else c

def tm(man):
    g = man.to_mesh()
    return trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts), process=False)

externo = ret(0, 0, LX, LY, 4)
interno = ret(a.moldura, a.moldura, LX - a.moldura, LY - a.moldura, 1.5)
linhas2d = contorno(mask) ^ interno.offset(-0.3, mf.JoinType.Miter)

# moldura preta com chanfro interno de 1 mm e furo de pendurar (fechadura) atrás, no topo
moldura = (externo - interno).extrude(Z_MOLD - 1) + (externo - interno.offset(1, mf.JoinType.Round)).extrude(1).translate((0, 0, Z_MOLD - 1))
fech = (mf.Manifold.cylinder(2.6, 4.2, circular_segments=32).translate((LX / 2, LY - a.moldura / 2 - 1.2, 0))
        + mf.Manifold.cube((4.2, 6, 2.6)).translate((LX / 2 - 2.1, LY - a.moldura / 2 - 1.2 - 6, 0))
        + mf.Manifold.cylinder(1.4, 7.6, circular_segments=32).translate((LX / 2, LY - a.moldura / 2 - 1.2 - 6, 0)))
moldura = moldura - fech
placa = interno.offset(0.0, mf.JoinType.Miter).extrude(Z_PLACA)
preto = moldura + linhas2d.extrude(Z_LINHA - Z_PLACA).translate((0, 0, Z_PLACA))   # desenho apoiado em cima da placa
branco = placa

# suporte de mesa: bloco com fenda inclinada 12° onde o quadro encaixa
EQ = Z_MOLD + 0.4
blk = mf.Manifold.cube((min(LX * 0.6, 110), 34, 12))
fenda = mf.Manifold.cube((min(LX * 0.6, 110) + 2, EQ, 30)).translate((-1, -EQ / 2, 0)).rotate((-12, 0, 0)).translate((0, 17, 3))
suporte = blk - fenda

os.makedirs("saida", exist_ok=True)
pb, pp = tm(branco), tm(preto)
pb.export("saida/quadro_branco.stl"); pp.export("saida/quadro_preto.stl"); tm(suporte).export("saida/suporte.stl")
cena = trimesh.Scene()
cena.add_geometry(pp, node_name="quadro_cor1_preto", geom_name="quadro_cor1_preto")
cena.add_geometry(pb, node_name="quadro_cor2_branco", geom_name="quadro_cor2_branco")
cena.export("saida/quadro_2cores.3mf")
prev = np.full((H, W, 3), 242, np.uint8); prev[mask] = 20
Image.fromarray(prev).save("saida/preview.png")
for n in ("quadro_branco", "quadro_preto", "suporte"):
    t = trimesh.load(f"saida/{n}.stl"); print(n, t.extents.round(1), "fechada", t.is_watertight)
