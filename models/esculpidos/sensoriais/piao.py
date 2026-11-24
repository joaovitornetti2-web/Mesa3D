"""Pião Abóbora – abobrinha de 44 mm com gomos, carinha de lanterna de Halloween, cabinho torcido (é por ele que se gira)
e gavinha enrolada. Uma peça só, impressa em pé na ponta com suporte em árvore só embaixo.
c1 abóbora · c2 carinha · c4 cabinho e gavinha."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.15
g = Grade((-25, -25, 0), (25, 25, 60), passo)
X, Y, Z = g.x, g.y, g.z
rho = np.sqrt(X * X + Y * Y); th = np.arctan2(Y, X)
# corpo: ponta em cone + abóbora de 8 gomos
lob = 1 - 0.07 * (1 - np.abs(np.cos(4 * th))) ** 1.5
ab = elipsoide(g, (0, 0, 30), (22, 22, 12.5))
ab = (np.sqrt((X / lob) ** 2 + (Y / lob) ** 2 + 0 * Z) - 22 * np.sqrt(np.clip(1 - ((Z - 30) / 12.5) ** 2, 0, 1))) * 0.8
ab = np.maximum(ab, np.abs(Z - 30) - 12.5)
cone = capsula(g, (0, 0, 1.4), (0, 0, 24), 1.4, 18.5)
corpo = smin(ab, cone, 6)
corpo = menos(corpo, elipsoide(g, (0, 0, 43.5), (7, 7, 3.2)), 2)          # topo afundado
# carinha de lanterna (cavada, cor 2)
def fy(x, z):
    return -22 * np.sqrt(max(0, 1 - ((z - 30) / 12.5) ** 2)) * 0.97 * np.sqrt(max(0.0, 1 - (x / 22) ** 2))
olho = lambda x0, z0, s: np.maximum(np.maximum(-(Z - z0 + 2.2), (Z - z0) + 1.9 * np.abs(X - x0) / 1.0 * 0.9 - 2.2), np.abs(Y - fy(x0, z0)) - 2.5)
olhos = np.minimum(olho(-6, 33, 1), olho(6, 33, 1))
bz = 26.0
boca_x = np.abs(X)
dente = 0.9 * np.abs(((X + 20) % 4.0) - 2.0)
boca = np.maximum.reduce([boca_x - 9.0 + 0 * Z, -(Z - (bz - 2.2 + 0.03 * X * X)), Z - (bz + 1.6 + 0.02 * X * X) + dente * 0.0])
boca = np.maximum(np.maximum(boca_x - 9, np.maximum(-(Z - (bz - 2.4 + 0.035 * X ** 2) - dente), Z - (bz + 1.2 + 0.035 * X ** 2) + (1.8 - dente))), Y + 12)
boca = np.maximum(boca, -(Y + 26))
cara = np.minimum(olhos, boca)
corpo = menos(corpo, np.maximum(cara, -(Y + 19.5)), 0.3)
cara_cor = np.maximum(cara - 0.8, -corpo - 0.8)
# cabinho torcido e gavinha
tw = th - Z * 0.12
cab = np.maximum(rho - (3.4 + 0.45 * np.cos(6 * tw)), np.maximum(41 - Z, Z - 56))
cab = smin(cab, esfera(g, (0, 0, 55.5), 3.6), 1)
cab = smin(cab, cilindro(g, (0, 0, 40), 5.2, 3.5, 1.2), 1.5)
gav = tubo(g, [(4.8 * np.cos(t), 4.8 * np.sin(t), 43.2 + 0.25 * t) for t in np.linspace(0, 2 * np.pi * 1.25, 18)], list(np.linspace(1.1, 0.6, 18)))
corpo = smin(corpo, cab, 1.2)
corpo = smin(corpo, gav, 0.4)
corpo = np.maximum(corpo, -Z)
reg = {"c2": cara_cor, "c4": np.minimum(cab - 0.3, gav - 0.1)}
for k, v_ in exportar(g, dividir(corpo, reg), os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "piao"), faces=None).items():
    print(k, v_)
