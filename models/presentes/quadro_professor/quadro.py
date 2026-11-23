#!/usr/bin/env python3
"""Desenho em linha (PNG com as linhas no canal alfa) -> mini quadro em relevo de 2 cores.
Placa branca, desenho em preto 0,6 mm em relevo, moldura preta e suporte de mesa (tudo sem suporte de impressão).

Uso: python3 quadro.py desenho.png [--girar -90] [--largura 140]
Saída (--saida, --nome): <nome>_branco.stl, <nome>_preto_com_suporte.stl, <nome>_2cores_com_suporte.3mf, <nome>_preview.png
PDF: --pagina N --sem-recorte --girar 0 usa a página inteira na medida original.
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
ap.add_argument("--margem", type=float, default=4, help="respiro entre desenho e moldura (mm)")
ap.add_argument("--fresta", type=float, default=0.45, help="menor vão branco que o engrossamento pode deixar (mm)")
ap.add_argument("--sem-recorte", action="store_true", help="usa a página inteira (não recorta ao desenho)")
ap.add_argument("--pagina", type=int, default=1, help="página do PDF")
ap.add_argument("--saida", default="saida", help="pasta de saída")
ap.add_argument("--nome", default="quadro", help="prefixo dos arquivos")
a = ap.parse_args()

PX = 0.1                       # mm por pixel na placa
Z_PLACA, Z_LINHA, Z_MOLD = 2.0, 2.6, 4.5
LINHA_MIN = 0.6                # linha mais fina que o bico 0,4 imprime bem

if a.desenho.lower().endswith(".pdf"):      # PDF: rasteriza a página a 0,05 mm/px
    import subprocess, tempfile
    tmp = tempfile.mkdtemp()
    subprocess.run(["pdftoppm", "-r", "508", "-png", "-f", str(a.pagina), "-l", str(a.pagina), "-singlefile", a.desenho, tmp + "/p"], check=True)
    a.desenho = tmp + "/p.png"
im = Image.open(a.desenho).convert("RGBA")
alfa = np.asarray(im)[..., 3]
lum = np.asarray(im.convert("L"))
linhas = alfa if alfa.min() < 250 else 255 - lum          # linhas no alfa (fundo transparente) ou escuras no branco
img = Image.fromarray(linhas).rotate(a.girar, expand=True, resample=Image.BICUBIC)
# recorta ao desenho
m0 = np.asarray(img) > 60
if not a.sem_recorte:
    ys, xs = np.nonzero(m0)
    img = img.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
W = int(round(a.largura / PX)); H = int(round(img.height * W / img.width))
m = np.asarray(img.resize((W, H), Image.LANCZOS)).astype(float) / 255
mask = m > 0.35
original = mask.copy()
cruz = ndi.generate_binary_structure(2, 1)
rb = max(1, int(round(a.fresta / 2 / PX)))
def protege_vaos(mk):
    """o engrossamento não pode fechar vãos (miolo das letras, olhos, entre linhas): onde o branco
    ficou mais estreito que --fresta e era branco no desenho, devolve o branco"""
    estreito = ~mk & ~ndi.binary_opening(~mk, structure=cruz, iterations=rb)
    return mk & ~(mk & ~original & ndi.binary_dilation(estreito, structure=cruz, iterations=rb + 1))
# engrossa só o que é fino: some numa abertura de raio LINHA_MIN/2 (letras em negrito e áreas cheias ficam como estão)
rt = max(1, int(round(LINHA_MIN / 2 / PX)))
fina = mask & ~ndi.binary_opening(mask, structure=cruz, iterations=rt)
cresce = max(1, int(round((LINHA_MIN - 2 * rt * PX * 0.66) / 2 / PX)))
mask = mask | ndi.binary_dilation(fina, structure=cruz, iterations=cresce)
mask = protege_vaos(mask)
mask = ndi.gaussian_filter(mask.astype(float), 0.7) > 0.5      # contorno liso
mask = protege_vaos(mask)
# tira sujeira: ilhas < 0,25 mm² e furinhos < 0,15 mm² (que não imprimem)
for alvo, amin in ((mask, 0.25), (~mask, 0.15)):
    lab, n = ndi.label(alvo)
    if n:
        ar = ndi.sum(alvo, lab, range(1, n + 1)) * PX * PX
        peq = np.isin(lab, 1 + np.nonzero(ar < amin)[0])
        mask = (mask & ~peq) if alvo is mask else (mask | peq)
art_w, art_h = W * PX, H * PX
LX = art_w + 2 * (a.margem + a.moldura); LY = art_h + 2 * (a.margem + a.moldura)
print(f"desenho {art_w:.0f}×{art_h:.0f} mm  quadro {LX:.0f}×{LY:.0f} mm")

def contorno(mk, folga=0.01):
    mm = ndi.gaussian_filter(ndi.zoom(np.pad(mk, 2).astype(float), 2, order=1), 0.9)
    polys = []
    for c in measure.find_contours(mm, 0.5):
        if len(c) >= 4:
            x = (c[:, 1] / 2 - 2) * PX + a.moldura + a.margem
            y = LY - ((c[:, 0] / 2 - 2) * PX + a.moldura + a.margem)
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

# moldura preta com chanfro interno de 1 mm (sem furos nem pontes: imprime sem suporte)
moldura = (externo - interno).extrude(Z_MOLD - 1) + (externo - interno.offset(1, mf.JoinType.Round)).extrude(1).translate((0, 0, Z_MOLD - 1))
placa = interno.offset(0.0, mf.JoinType.Miter).extrude(Z_PLACA)
preto = moldura + linhas2d.extrude(Z_LINHA - Z_PLACA).translate((0, 0, Z_PLACA))   # desenho apoiado em cima da placa
branco = placa

# suporte de mesa: bloco com fenda inclinada 12° onde o quadro encaixa
EQ = Z_MOLD + 0.4
blk = mf.Manifold.cube((min(LX * 0.6, 110), 34, 12))
fenda = mf.Manifold.cube((min(LX * 0.6, 110) + 2, EQ, 30)).translate((-1, -EQ / 2, 0)).rotate((-12, 0, 0)).translate((0, 17, 3))
suporte = blk - fenda

# suporte junto, deitado ao lado do quadro na mesma mesa de impressão (cabe na A1: ~206 × 202 mm)
SW = min(LX * 0.6, 110)
suporte_lado = suporte.rotate((0, 0, 90)).translate((LX + 6 + 34, (LY - SW) / 2, 0))
O = a.saida; N = a.nome
os.makedirs(O, exist_ok=True)
pb, pp, ps = tm(branco), tm(preto), tm(suporte_lado)
pb.export(f"{O}/{N}_branco.stl")
trimesh.util.concatenate([pp, ps]).export(f"{O}/{N}_preto_com_suporte.stl")
cena = trimesh.Scene()
cena.add_geometry(pp, node_name=f"{N}_cor1_preto", geom_name=f"{N}_cor1_preto")
cena.add_geometry(pb, node_name=f"{N}_cor2_branco", geom_name=f"{N}_cor2_branco")
cena.add_geometry(ps, node_name=f"{N}_suporte_preto", geom_name=f"{N}_suporte_preto")
cena.export(f"{O}/{N}_2cores_com_suporte.3mf")
prev = np.full((H, W, 3), 242, np.uint8); prev[mask] = 20
Image.fromarray(prev).save(f"{O}/{N}_preview.png")
for n in (f"{N}_branco", f"{N}_preto_com_suporte"):
    t = trimesh.load(f"{O}/{n}.stl"); print(n, t.extents.round(1), "fechada", t.is_watertight, "corpos", t.body_count)
