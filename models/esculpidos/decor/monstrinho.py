"""Monstrinho Porta-Trecos – a boca é a abertura: come canetas, pincéis e dados.
Dentões em volta da boca, língua caída por cima do lábio, um olho desconfiado e outro arregalado,
chifrinhos tortos, bracinhos abraçando a barriga, pezinhos e verruguinhas.
c1 corpo · c2 pupilas · c3 branco dos olhos e dentes · c4 língua, bochechas e pintinhas."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.33
g = Grade((-52, -46, 0), (52, 44, 112), passo)
X, Y, Z = g.x, g.y, g.z
th = np.arctan2(Y, X)

# corpo de pote mole, mais gordinho embaixo
nucleo = elipsoide(g, (0, 0, 46), (38, 34, 50))
nucleo = smin(nucleo, elipsoide(g, (0, -1, 22), (41, 36, 22)), 10)
nucleo = smin(nucleo, np.maximum(elipsoide(g, (0, 0, 60), (31, 29, 60)), Z - 86), 10)
corpo = nucleo
# lábio enrolado da boca, inclinado para trás
BZ = 86.0
labio = toro(Vista(g, (0, 0, BZ), rot_x(6)), (0, 0, BZ), 29.5, 4.2, 1.0)
corpo = smin(corpo, labio, 4)
# chifrinhos tortos
for s, ang in ((-1, 24), (1, 34)):
    corpo = smin(corpo, tubo(g, [(s * 24, 4, BZ - 4), (s * 30, 6, BZ + 6), (s * 31, 8, BZ + 14), (s * 27, 9, BZ + 18)], [7, 5, 3, 1.2]), 3)
# bracinhos abraçando a barriga, com três dedos
for s in (-1, 1):
    corpo = smin(corpo, tubo(g, [(s * 36, -6, 50), (s * 34, -22, 40), (s * 20, -33, 38)], [6.5, 5.5, 5]), 4)
    for d in (-1, 0, 1):
        corpo = smin(corpo, capsula(g, (s * 20, -33, 38), (s * 14, -36, 38 + d * 3.6), 2.6, 2.0), 1.4)
# pezinhos
for s in (-1, 1):
    pe = elipsoide(g, (s * 17, -22, 4.5), (11, 13, 6))
    for d in (-1, 0, 1):
        pe = smin(pe, esfera(g, (s * 17 + d * 5.5, -33, 3.6), 3.4), 2)
    corpo = smin(corpo, pe, 4)
# verruguinhas
rng = np.random.default_rng(3)
pintas = []
for k in range(16):
    a, e = rng.uniform(0, 2 * np.pi), rng.uniform(-0.6, 0.55)
    if -2.1 < a < -1.0 and e > -0.1:
        continue
    c = (38.5 * np.cos(e) * np.cos(a), 34.5 * np.cos(e) * np.sin(a), 46 + 50 * np.sin(e) * 0.95)
    r = rng.uniform(1.6, 3.4)
    corpo = smin(corpo, esfera(g, c, r), 1.0)
    if k % 3 == 0:
        pintas.append(esfera(g, c, r + 0.2))
corpo = corpo + 0.08 * ruido(g, 2.5, 8)

# rosto
def fy(x, z):
    return -34 * np.sqrt(max(0, 1 - (x / 38) ** 2 - ((z - 46) / 50) ** 2)) + 1.0
olho_b, pup, brilho, palp = [], [], [], None
for s, rz, lid in ((-1, 10.5, False), (1, 8.5, True)):
    x0, z0 = s * 13, 58
    y0 = fy(x0, z0)
    e = elipsoide(g, (x0, y0, z0), (9, 5, rz))
    corpo = smin(corpo, e, 1.5)
    olho_b.append(elipsoide(g, (x0, y0, z0), (9, 12, rz)))
    pup.append(elipsoide(g, (x0 - s * 1.2, y0 - 4, z0 - 1.5), (4.2, 3, 5)))
    brilho.append(esfera(g, (x0 + 2.5, y0 - 4.3, z0 + 3.5), 1.6))
    if lid:   # pálpebra caída de desconfiado
        p = np.maximum(elipsoide(g, (x0, y0 + 0.6, z0 + 0.5), (10.2, 6.2, rz + 1.4)), -(Z - z0 - 1.5 + 0.25 * (X - x0)))
        palp = p
        corpo = smin(corpo, p, 1.0)
for s in (-1, 1):
    corpo = smin(corpo, capsula(g, (s * 6, fy(s * 6, 72) - 0.5, 72 - (3 if s > 0 else 0)), (s * 21, fy(s * 21, 70) - 0.5, 70 + (2 if s > 0 else 0)), 2.0), 1.5)
boch = [elipsoide(g, (s * 26, fy(s * 26, 46) + 0.3, 46), (5, 2.2, 3.2)) for s in (-1, 1)]
for b in boch:
    corpo = smin(corpo, b, 0.8)

# oco (espaço para canetas): paredes de ~2,6 mm e fundo de 3 mm
oco = np.maximum(nucleo + 2.6, 3.0 - Z)
oco = np.minimum(oco, np.maximum(cilindro(g, (0, 0, 60), 25.5, 60), 3.0 - Z))
corpo = menos(corpo, oco)
# corta o topo da boca (o lábio fica)
corpo = np.maximum(corpo, -np.maximum(np.sqrt(X * X + Y * Y) - 25.6, BZ - 0.5 - Z + 0.10 * Y))

# dentões em volta da boca, apontando para cima
dentes = []
for k in range(10):
    a = np.radians(k * 36 + 18)
    if -110 < np.degrees(a) - 360 < -70 or -110 < np.degrees(a) < -70:
        continue
    r0 = 27.0
    base = (r0 * np.cos(a), r0 * np.sin(a), BZ + 0.10 * r0 * np.sin(a) + 1)
    tip = ((r0 - 2.5) * np.cos(a), (r0 - 2.5) * np.sin(a), base[2] + (10 if k % 2 else 7))
    d = capsula(g, base, tip, 4.0 if k % 2 else 3.2, 0.7)
    dentes.append(d)
    corpo = smin(corpo, d, 0.8)
# língua caída pela frente
lingua = tubo(g, [(10, -17, BZ - 0.5), (13, -27, BZ + 1.6), (15, -33, BZ - 3), (15.5, -34.5, BZ - 9), (15, -33.8, BZ - 12.5)], [5.5, 6, 5.8, 5.2, 4.4])
lingua = np.maximum(lingua, -(oco))
corpo = smin(corpo, lingua, 1.2)
corpo = np.maximum(corpo, -Z)

branco = np.minimum.reduce(olho_b)
if palp is not None:
    branco = np.maximum(branco, -(palp - 0.05))
reg = {"c2": np.minimum.reduce(pup),
       "c3": np.minimum.reduce(brilho + dentes + [branco]),
       "c4": np.minimum.reduce([lingua - 0.4] + boch)}
for k, v in exportar(g, dividir(corpo, reg), os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "monstrinho"), faces=400000).items():
    print(k, v)
