#!/usr/bin/env python3
"""Converte um PNG (símbolo escuro em fundo claro, ou com transparência) em SVG para o OpenSCAD.
Uso: python3 -I trace_png.py entrada.png saida.svg"""
import sys
import numpy as np
from PIL import Image
import potrace

img = Image.open(sys.argv[1])
if img.mode in ("RGBA", "LA") or "transparency" in img.info:
    a = np.array(img.convert("RGBA"))[:, :, 3]
    mask = a > 128
else:
    g = np.array(img.convert("L"))
    mask = g < 128
    if mask.mean() > 0.5:          # símbolo claro em fundo escuro
        mask = ~mask
bm = potrace.Bitmap(~mask)   # potracer preenche os pixels "False"
plist = bm.trace(turdsize=10, opttolerance=0.4)
h, w = mask.shape
parts = []
for curve in plist:
    sx, sy = curve.start_point.x, curve.start_point.y
    d = [f"M{sx:.2f},{sy:.2f}"]
    for seg in curve.segments:
        if seg.is_corner:
            d.append(f"L{seg.c.x:.2f},{seg.c.y:.2f}L{seg.end_point.x:.2f},{seg.end_point.y:.2f}")
        else:
            d.append(f"C{seg.c1.x:.2f},{seg.c1.y:.2f} {seg.c2.x:.2f},{seg.c2.y:.2f} {seg.end_point.x:.2f},{seg.end_point.y:.2f}")
    parts.append("".join(d) + "Z")
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
       f'<path fill-rule="evenodd" d="{" ".join(parts)}"/></svg>')
open(sys.argv[2], "w").write(svg)
print(f"{len(plist)} contornos -> {sys.argv[2]}")
