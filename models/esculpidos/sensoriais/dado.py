"""Dado Sensorial – cubo de 32 mm com cantos bem macios e uma textura diferente em cada face:
escamas de dragão, plástico-bolha, ondas zen, carinha sorrindo, espiral para seguir com o dedo e covinhas.
1 cor (c1) + carinha (c2) opcional."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.12
L = 16.0
g = Grade((-L - 2, -L - 2, 0), (L + 2, L + 2, 2 * L + 2), passo)
X, Y, Z = g.x, g.y, g.z - L                     # centro no meio do cubo
cubo = caixa(g, (0, 0, L), (L, L, L), 4.5)

def face(n):
    """coordenadas (u, v, profundidade) na face n: 0 +Z, 1 -Z, 2 +X, 3 -X, 4 +Y, 5 -Y."""
    return [(X, Y, Z), (X, -Y, -Z), (Y, Z, X), (-Y, Z, -X), (-X, Z, Y), (X, Z, -Y)][n]

relevo, corte, cor2 = [], [], []
# 0 (+Z, em cima): espiral cavada
u, v, w = face(0)
r = np.sqrt(u * u + v * v); th = np.arctan2(v, u)
esp = np.abs(((r - 1.6 * th / np.pi) % 3.2) - 1.6) - 0.55
corte.append(np.maximum(np.maximum(esp, r - 11.5), L - 0.9 - w))
# 1 (-Z, embaixo, apoio): covinhas rasas
u, v, w = face(1)
cov = np.sqrt(((u + 20) % 6.5 - 3.25) ** 2 + ((v + 20) % 6.5 - 3.25) ** 2 + (w - L - 1.3) ** 2) - 2.2
corte.append(np.maximum(cov, np.maximum(np.abs(u) - 11, np.abs(v) - 11)))
# 2 (+X): escamas de dragão
u, v, w = face(2)
lin = np.floor((v + 30) / 4.0)
uu = u + (lin % 2) * 2.5
cu = (uu + 30) % 5.0 - 2.5
cv = (v + 30) % 4.0 - 0.6
esc = np.sqrt(cu ** 2 + (cv * 1.15) ** 2 + (w - L + 1.2) ** 2) - 2.6
relevo.append(np.maximum(esc, np.maximum(np.abs(u) - 11.5, np.abs(v) - 11.5)))
# 3 (-X): plástico-bolha (domos)
u, v, w = face(3)
bol = np.sqrt(((u + 10.5) % 7 - 3.5) ** 2 + ((v + 10.5) % 7 - 3.5) ** 2 + (w - L + 1.0) ** 2) - 2.9
relevo.append(np.maximum(bol, np.maximum(np.abs(u) - 10.5, np.abs(v) - 10.5)))
# 4 (+Y): ondas zen
u, v, w = face(4)
ond = np.abs(((v + 1.2 * np.sin(u * 0.55)) + 30) % 3.4 - 1.7) - 0.6
corte.append(np.maximum(np.maximum(ond, np.maximum(np.abs(u) - 12, np.abs(v) - 12)), L - 0.8 - w))
# 5 (-Y, frente): carinha sorridente (olhos e boca em relevo, cor 2)
u, v, w = face(5)
olhos = np.minimum(np.sqrt((u + 5) ** 2 + ((v - 2.5) / 1.25) ** 2) - 2.2, np.sqrt((u - 5) ** 2 + ((v - 2.5) / 1.25) ** 2) - 2.2)
boca = np.maximum(np.abs(np.sqrt(u ** 2 + (v + 0.5) ** 2) - 6.0) - 0.9, v + 2.5)
boch = np.minimum(np.sqrt((u + 9) ** 2 + (v + 2.5) ** 2) - 1.8, np.sqrt((u - 9) ** 2 + (v + 2.5) ** 2) - 1.8)
cara = np.minimum.reduce([olhos, boca, boch])
cara3 = np.maximum(cara, np.maximum(w - L - 0.8, L - 1.0 - w))
relevo.append(cara3)

corpo = cubo
for r_ in relevo:
    corpo = smin(corpo, np.maximum(r_, -cubo - 0.0) if False else r_, 0.4)
for c_ in corte:
    corpo = menos(corpo, c_, 0.3)
corpo = np.maximum(corpo, -(g.z))
reg = {"c2": np.maximum(cara, -(face(5)[2] - L + 1.5))}
for k, v_ in exportar(g, dividir(corpo, reg), os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "dado"), faces=None).items():
    print(k, v_)
