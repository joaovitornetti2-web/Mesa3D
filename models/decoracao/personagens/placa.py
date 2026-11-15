#!/usr/bin/env python3
"""<nome>_niveis.png -> placa em arco com relevo de 3 cores (preto/vermelho/branco).
Saída: saida/<nome>_placa.stl, saida/<nome>_placa_3cores.3mf, saida/<nome>_placa_cor{1,2,3}.stl"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
import manifold3d as mf
import trimesh
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from triton import PX_MM, LARG_MM, ALT_MM

Z_BASE, Z_VERM, Z_BRANCO = 1.5, 2.1, 2.9   # base preta | +0.6 vermelho | +0.8 branco


def arco(w=LARG_MM, h=ALT_MM, n=48):
    r = 0.6 * w; off = r - w / 2; ha = np.sqrt(r * r - off * off)
    yb = h - ha
    # lado direito: arco centrado em (-off, yb) de x=w/2 até a ponta x=0
    a0 = np.arctan2(0, w / 2 + off); a1 = np.arctan2(ha, off)
    dir_ = [(-off + r * np.cos(a), yb + r * np.sin(a)) for a in np.linspace(a0, a1, n)]
    esq = [(-x, y) for x, y in reversed(dir_)]
    pts = [(-w / 2, 0), (w / 2, 0)] + dir_ + esq[1:]
    return mf.CrossSection([np.array(pts) + [w / 2, 0]], mf.FillRule.EvenOdd)


def contorno(mask, folga=0.01):
    m = np.pad(mask, 2).astype(float)
    m = ndi.zoom(m, 2, order=1)
    m = ndi.gaussian_filter(m, 0.9)
    cs = measure.find_contours(m, 0.5)
    H = m.shape[0]
    polys = []
    for c in cs:
        if len(c) < 4:
            continue
        x = (c[:, 1] / 2 - 2) * PX_MM
        y = ALT_MM - (c[:, 0] / 2 - 2) * PX_MM
        polys.append(np.c_[x, y])
    # +0.01 mm: regiões que só se encostam passam a se fundir (sem aresta não-manifold)
    return mf.CrossSection(polys, mf.FillRule.EvenOdd).simplify(0.02).offset(folga, mf.JoinType.Round)


def tm(man):
    g = man.to_mesh()
    # sem fundir vértices: ilhas que se tocam num ponto viram não-manifold se fundidas
    return trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts), process=False)


def placa(nome):
    niv = np.asarray(Image.open(f"{nome}_niveis.png"))
    a = arco()
    import os; os.makedirs("saida", exist_ok=True)
    # o STL (float32) pode criar arestas não-manifold; se acontecer, refaz com outra folga
    for folga in (0.010, 0.013, 0.017, 0.022, 0.03):
        a_in = a.offset(-0.05, mf.JoinType.Miter)   # relevo nunca encosta na borda da placa
        c1 = contorno(niv >= 1, folga) ^ a_in
        c2 = contorno(niv >= 2, folga) ^ c1.offset(-0.03, mf.JoinType.Miter)   # branco sempre dentro do vermelho
        p1 = a.extrude(Z_BASE)
        p2 = c1.extrude(Z_VERM - Z_BASE).translate((0, 0, Z_BASE))
        p3 = c2.extrude(Z_BRANCO - Z_VERM).translate((0, 0, Z_VERM))
        q2 = c1.extrude(Z_VERM - Z_BASE + 0.02).translate((0, 0, Z_BASE - 0.02))
        q3 = c2.extrude(Z_BRANCO - Z_VERM + 0.02).translate((0, 0, Z_VERM - 0.02))
        partes = [tm(p1), tm(p2), tm(p3)]
        tudo = tm(p1 + q2 + q3)
        tudo.export(f"saida/{nome}_placa.stl")
        ok = trimesh.load(f"saida/{nome}_placa.stl").is_watertight
        for i, p in enumerate(partes, 1):
            p.export(f"saida/{nome}_placa_cor{i}.stl")
            ok &= trimesh.load(f"saida/{nome}_placa_cor{i}.stl").is_watertight
        if ok:
            break
    cena = trimesh.Scene()
    for i, (p, cor) in enumerate(zip(partes, ["preto", "vermelho", "branco"]), 1):
        cena.add_geometry(p, node_name=f"{nome}_cor{i}_{cor}", geom_name=f"{nome}_cor{i}_{cor}")
    cena.export(f"saida/{nome}_placa_3cores.3mf")
    print(f"{nome}: {tudo.extents.round(1)} mm, STL fechado após recarregar={ok} (folga {folga} mm)")

if __name__ == "__main__":
    for n in sys.argv[1:]:
        placa(n)
