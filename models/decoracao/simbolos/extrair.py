#!/usr/bin/env python3
"""Isola o traço de cada símbolo (remove fumaça, poeira, respingos) e salva <elemento>.png:
símbolo preto em fundo branco, pronto para trace_png.py. Uso: python3 -I extrair.py"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from pathlib import Path

D = Path(__file__).resolve().parent


def carregar(e):
    im = Image.open(D / "originais" / f"{e}.webp").convert("RGBA")
    fundo = Image.new("RGBA", im.size, (255, 255, 255, 255))
    rgb = np.array(Image.alpha_composite(fundo, im).convert("RGB")).astype(int)
    hsv = np.array(Image.fromarray(rgb.astype(np.uint8)).convert("HSV")).astype(int)
    return rgb, hsv


def limpar(m, min_area, abrir=1, fechar=2):
    if abrir: m = ndi.binary_opening(m, iterations=abrir)
    if fechar: m = ndi.binary_closing(m, iterations=fechar)
    lab, n = ndi.label(m)
    areas = ndi.sum(m, lab, range(1, n + 1))
    keep = np.isin(lab, [i + 1 for i, a in enumerate(areas) if a >= min_area])
    return ndi.binary_fill_holes(keep) if False else keep


def sangue():
    rgb, hsv = carregar("sangue")
    m = (hsv[..., 2] < 70) & ((hsv[..., 1] < 140) | (hsv[..., 2] < 40))
    return limpar(m, 4000, abrir=2, fechar=3)


def morte():
    rgb, hsv = carregar("morte")
    m = hsv[..., 2] < 38
    return limpar(m, 2500, abrir=2, fechar=2)


def medo():
    rgb, hsv = carregar("medo")
    v = hsv[..., 2]
    m = (v > 200) & (hsv[..., 1] < 40)
    lab, n = ndi.label(m)
    borda = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    m = m & ~np.isin(lab, list(borda))
    return limpar(m, 3000, abrir=1, fechar=2)


RAIO_MM = 19.5     # cabe dentro do anel interno do selo
TRACO_MM = 0.9     # menor traço que o bico 0.4 imprime bem


def disco(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def imprimivel(m, area_min_mm2=3.0):
    ys, xs = np.nonzero(m)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = m.shape
    yy, xx = np.nonzero(m)
    rmax = np.sqrt((xx - w / 2) ** 2 + (yy - h / 2) ** 2).max()
    s = RAIO_MM / rmax                       # mm por pixel no tamanho final
    r = max(1, int(round(TRACO_MM / 2 / s)))
    nucleo = ndi.binary_opening(m, structure=disco(r))
    fino = m & ~nucleo
    lab, n = ndi.label(fino)
    if n:
        a = ndi.sum(fino, lab, range(1, n + 1))
        fino = np.isin(lab, [i + 1 for i, x in enumerate(a) if x * s * s >= 0.4])
        fino = ndi.binary_dilation(fino, structure=disco(max(1, r // 2)))
    out = nucleo | fino
    lab, n = ndi.label(out)
    a = ndi.sum(out, lab, range(1, n + 1))
    caixas = ndi.find_objects(lab)
    out = np.isin(lab, [i + 1 for i, x in enumerate(a)
                        if x * s * s >= area_min_mm2 and max(caixas[i][0].stop - caixas[i][0].start,
                                                              caixas[i][1].stop - caixas[i][1].start) * s >= 5.0])
    return np.pad(out, 20), s


for e, f in [("sangue", sangue), ("morte", morte)]:
    m, s = imprimivel(f())
    Image.fromarray(np.where(m, 0, 255).astype(np.uint8)).save(D / f"{e}.png")
    print(f"{e}: {s * 1000:.1f} µm/px, traço mínimo {TRACO_MM} mm")
print("medo: redesenhado em vetor (medo_vetor.scad -> medo.svg)")
