#!/usr/bin/env python3
"""Placa em arco (mesmo formato dos pôsteres) com sigilo do livro: sigilo BRANCO, anel e runas VERMELHOS, fundo PRETO."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from triton import PX_MM, LARG_MM, ALT_MM, MOLDURA, arco_dist
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "simbolos")
NOMES = {"sangue": "SANGUE", "morte": "MORTE", "energia": "ENERGIA", "conhecimento": "CONHECIMENTO"}

def mascara(nome, diam_px):
    m = np.asarray(Image.open(f"{S}/{nome}.png").convert("L")) < 128
    if nome == "conhecimento":   # só o miolo: glifos maiores e legíveis
        h, w = m.shape; yy, xx = np.mgrid[:h, :w]
        m = m & (np.hypot(yy - h / 2, xx - w / 2) < h * 0.31)
    ys, xs = np.nonzero(m); m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = m.shape; k = diam_px / max(h, w)
    return np.asarray(Image.fromarray(m.astype(np.uint8) * 255).resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)) > 127

def placa(nome):
    W, H = int(LARG_MM / PX_MM), int(ALT_MM / PX_MM)
    niv = np.zeros((H, W), np.uint8)
    cx, cy = W / 2, H * 0.43
    R = W * 0.43
    yy, xx = np.mgrid[:H, :W]; d = np.hypot(xx - cx, yy - cy)
    niv[(d < R) & (d > R - 1.1 / PX_MM)] = 1                       # anel externo vermelho
    niv[(d < R - 2.2 / PX_MM) & (d > R - 2.9 / PX_MM)] = 1         # anel interno
    for k in range(12):                                            # losangos entre os anéis
        a = k * np.pi / 6; px, py = cx + (R - 1.65 / PX_MM) * np.cos(a), cy + (R - 1.65 / PX_MM) * np.sin(a)
        niv[(np.abs(xx - px) + np.abs(yy - py)) < 0.55 / PX_MM] = 1
    s = mascara(nome, 2 * (R - 3.6 / PX_MM) * (0.98 if nome == "conhecimento" else 0.9))
    oy, ox = int(cy - s.shape[0] / 2), int(cx - s.shape[1] / 2)
    grosso = {"sangue": 0, "morte": 0.45, "energia": 0.5, "conhecimento": 0.25}[nome]
    if grosso: s = ndi.binary_dilation(s, iterations=max(1, round(grosso / PX_MM / 2)))
    pad = 6; s2 = np.zeros((s.shape[0] + 2 * pad, s.shape[1] + 2 * pad), bool); s2[pad:-pad, pad:-pad] = s; s = s2
    oy, ox = int(cy - s.shape[0] / 2), int(cx - s.shape[1] / 2)
    niv[oy:oy + s.shape[0], ox:ox + s.shape[1]][s] = 2               # sigilo branco
    # nome do elemento em vermelho embaixo
    img = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(img)
    f = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", int((3.6 if len(NOMES[nome]) > 8 else 4.6) / PX_MM))
    dr.text((W / 2, H * 0.86), NOMES[nome], fill=255, font=f, anchor="mm")
    niv[np.asarray(img) > 127] = 1
    # traços mínimos imprimíveis
    for k in (1, 2):
        m = ndi.binary_closing(ndi.binary_opening(niv >= k, iterations=1), iterations=1)
        niv = np.where(m, np.maximum(niv, k), np.minimum(niv, k - 1)).astype(np.uint8)
    dist = arco_dist(W, H); f0, f1, f2 = (v / PX_MM for v in MOLDURA)
    niv[dist < f2] = 0; niv[(dist >= f0) & (dist < f1)] = 2
    Image.fromarray(niv).save(f"sigilo_{nome}_niveis.png")
    cores = np.array([[21, 21, 21], [192, 20, 28], [240, 240, 240]], np.uint8)
    Image.fromarray(cores[niv]).save(f"sigilo_{nome}_preview.png")

for n in sys.argv[1:]: placa(n)
