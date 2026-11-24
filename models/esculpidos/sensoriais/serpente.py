"""Sibila, a serpente – a mecânica (12 segmentos com pinos, impressa já montada) vem de models/sensoriais/sensoriais.scad
(DECOR=false); aqui cada segmento ganha uma cúpula de escamas por cima (sem tocar nas juntas) e a cabeça vira uma cabeça de
verdade: focinho, olhões com brilho, sobrancelhas de quem está tramando algo e linguinha bifurcada.
c1 segmentos pares · c2 segmentos ímpares · c3 branco dos olhos · c4 língua (pupilas na cor da cabeça)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, trimesh
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.18
N, W, H, L = 12, 16, 9, 18
ang = lambda i: 28 * np.sin(np.radians(i * 55))
dirv = lambda t: np.array([np.cos(np.radians(t)), np.sin(np.radians(t))])
sgl, c = [], np.array([0.0, 0.0])
for i in range(N):
    t = ang(i); j = c - L / 2 * dirv(t)
    sgl.append((c.copy(), t)); c = j - L / 2 * dirv(ang(i + 1))
xs = [p[0][0] for p in sgl]; ys = [p[0][1] for p in sgl]
g = Grade((min(xs) - 10, min(ys) - 10, 8.0), (max(xs) + 18, max(ys) + 10, 17), passo)
X, Y, Z = g.x, g.y, g.z
domos = {0: [], 1: []}
olhos_b, pupilas, lingua = [], [], None
for i, (cc, t) in enumerate(sgl):
    d = dirv(t); n = np.array([-d[1], d[0]])
    u = (X - cc[0]) * d[0] + (Y - cc[1]) * d[1]
    v = (X - cc[0]) * n[0] + (Y - cc[1]) * n[1]
    if i == 0:   # cabeça
        cab = elipsoide(g, (cc[0] + 1.0 * d[0], cc[1] + 1.0 * d[1], 8.6), (7.6, 7.4, 4.6))
        foc = elipsoide(g, (cc[0] + 4.5 * d[0], cc[1] + 4.5 * d[1], 8.6), (4.2, 5.6, 3.0))
        dom = smin(cab, foc, 2.0)
        for s in (-1, 1):
            o = cc + 1.8 * d + s * 3.6 * n
            dom = smin(dom, esfera(g, (o[0], o[1], 12.3), 2.7), 1.0)
            olhos_b.append(esfera(g, (o[0], o[1], 12.3), 2.75))
            p = o + 1.0 * d + s * 0.2 * n
            pupilas.append(elipsoide(g, (p[0], p[1], 14.3), (1.3, 0.9, 1.1)))
            # sobrancelha de quem trama algo
            b1 = cc + 0.2 * d + s * 2.2 * n; b2 = cc + 0.6 * d + s * 6.2 * n
            dom = smin(dom, capsula(g, (b1[0], b1[1], 15.3), (b2[0], b2[1], 14.4), 0.8), 0.6)
            nar = cc + 7.4 * d + s * 1.6 * n
            dom = menos(dom, esfera(g, (nar[0], nar[1], 11.0), 0.7), 0.2)
        dom = np.maximum(dom, np.sqrt(u ** 2 + v ** 2) - 7.6)
    else:
        r0 = 7.6
        dom = elipsoide(g, (cc[0], cc[1], 8.8), (r0, r0, 3.0 if i < N - 1 else 2.6))
        # escamas: losangos levantadinhos
        su = (u + 30) % 3.4 - 1.7; sv = (v + 30 + ((np.floor((u + 30) / 3.4)) % 2) * 1.7) % 3.4 - 1.7
        esc = np.abs(su) + np.abs(sv) - 1.25
        dom = dom - 0.35 * np.clip(-esc, 0, 1)
        dom = np.maximum(dom, np.sqrt(u ** 2 + v ** 2) - r0)
    dom = np.maximum(dom, 8.95 - Z)
    domos[i % 2].append(dom)
d0 = dirv(sgl[0][1]); n0 = np.array([-d0[1], d0[0]])
c0 = sgl[0][0]
p1 = c0 + 6.5 * d0; p2 = c0 + 12 * d0
lingua = capsula(g, (p1[0], p1[1], 9.6), (p2[0], p2[1], 9.6), 0.8)
for s in (-1, 1):
    p3 = p2 + 2.8 * d0 + s * 1.6 * n0
    lingua = np.minimum(lingua, capsula(g, (p2[0], p2[1], 9.6), (p3[0], p3[1], 9.6), 0.7, 0.45))
lingua = np.maximum(lingua, 8.95 - Z)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
olho = np.minimum.reduce(olhos_b); pup = np.minimum.reduce(pupilas)
cab_total = np.minimum.reduce(domos[0])
partes = {"c1": np.maximum(np.maximum(cab_total, -(olho)), -lingua), "c2": np.minimum.reduce(domos[1]),
          "c3": np.maximum(olho, -pup), "c4": lingua}
partes["c1"] = np.minimum(partes["c1"], np.maximum(pup, -olho - 1.2))   # pupilas na cor da cabeça (AMS tem 4 entradas)
partes["c1"] = np.minimum(partes["c1"], np.maximum(lingua, 1e9))
feitos = exportar(g, partes, os.path.join(out, "serpente_dec"), faces=None)
# junta decoração + mecânica (pares = c1, ímpares = c2)
for cor, mec in (("c1", "par"), ("c2", "impar")):
    a = trimesh.load(os.path.join(out, f"serpente_mec_{mec}.stl"))
    b = trimesh.load(os.path.join(out, f"serpente_dec_{cor}.stl"))
    try:
        u_ = trimesh.boolean.union([a, b], engine="manifold")
    except Exception as e:
        print("união falhou, juntando sem fundir:", e); u_ = trimesh.util.concatenate([a, b])
    u_.export(os.path.join(out, f"serpente_{cor}.stl"))
    print(cor, len(u_.faces), u_.is_watertight)
for cor in ("c3", "c4"):
    os.replace(os.path.join(out, f"serpente_dec_{cor}.stl"), os.path.join(out, f"serpente_{cor}.stl"))
