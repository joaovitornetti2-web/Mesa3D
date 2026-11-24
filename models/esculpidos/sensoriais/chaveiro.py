"""Chaveiro d20 Criaturinha – um d20 de 24 mm que ganhou vida: carinha marota numa das faces,
asinhas de morcego dos lados, dois chifrinhos e a argola em cima.
c1 dado · c2 carinha · c4 asinhas e chifrinhos."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.1
g = Grade((-26, -14, 0), (26, 14, 40), passo)
X, Y, Z = g.x, g.y, g.z
C = (0, 0, 13.5)
# gira o icosaedro para uma face olhar para a frente (-Y)
n = np.array([0, 1 / PHI, PHI]); n /= np.linalg.norm(n)
alvo = np.array([0, -1.0, 0])
v = np.cross(n, alvo); s_ = np.linalg.norm(v); c_ = n @ alvo
K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
R = np.eye(3) + K + K @ K * ((1 - c_) / s_ ** 2)
dado = d20(g, C, 10.2, 0.9, rot=R)
corpo = dado
# carinha na face da frente
yf = -10.2 - 0.0
olhos = np.minimum(elipsoide(g, (-3.4, yf, 16.2), (1.5, 0.9, 2.0)), elipsoide(g, (3.4, yf, 16.2), (1.5, 0.9, 2.0)))
boca = np.maximum(np.abs(np.sqrt(X ** 2 + (Z - 13.0) ** 2) - 2.0) - 0.45, Z - 12.6)
boca = np.maximum(boca, np.abs(Y - yf) - 0.9)
presa = capsula(g, (1.1, yf + 0.1, 11.3), (1.1, yf - 0.3, 10.1), 0.55, 0.2)
corpo = smin(corpo, olhos, 0.2)
corpo = menos(corpo, boca, 0.15)
corpo = smin(corpo, presa, 0.15)
# asinhas e chifrinhos
asas = None
for s in (-1, 1):
    c = (s * 9.5, 1.5, 15)
    w = elipsoide(g, (s * 16, 1.5, 17), (8, 1.0, 6))
    for k in range(3):
        w = menos(w, esfera(g, (s * (11 + k * 4.5), 1.5, 11.2 + k * 1.0), 2.6), 0.3)
    w = np.maximum(w, -(s * X - 8))
    w = smin(w, capsula(g, (s * 8, 1.5, 17), (s * 23, 1.5, 21), 0.9, 0.5), 0.4)
    asas = w if asas is None else np.minimum(asas, w)
chif = np.minimum(tubo(g, [(-4.5, 0, 22), (-6.5, 0.5, 26), (-5.5, 1, 28.5)], [1.8, 1.1, 0.4]),
                  tubo(g, [(4.5, 0, 22), (6.5, 0.5, 26), (5.5, 1, 28.5)], [1.8, 1.1, 0.4]))
corpo = smin(corpo, asas, 0.8)
corpo = smin(corpo, chif, 0.6)
# argola
arg = toro(Vista(g, (0, 0, 29), rot_x(90)), (0, 0, 29), 4.2, 1.5)
arg = np.maximum(arg, 23.5 - Z)
corpo = smin(corpo, arg, 0.6)
corpo = np.maximum(corpo, -Z)
reg = {"c2": np.minimum(olhos - 0.05, np.maximum(boca - 0.5, -corpo - 0.6)), "c4": np.minimum(asas - 0.15, chif - 0.15)}
reg = {"c3": presa - 0.05, **reg}
for k, v_ in exportar(g, dividir(corpo, reg), os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "chaveiro"), faces=None).items():
    print(k, v_)
