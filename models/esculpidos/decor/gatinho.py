"""Gatinho Suporte de Celular – gatinho deitado (em "pãozinho") com uma fenda nas costas: o celular fica em pé atrás
da cabeça, inclinado para trás, e o rosto continua à mostra. Rabo enrolado do lado, patinhas para fora e canal para o cabo.
c1 pelo · c2 olhos/nariz/boca · c3 brilho dos olhos · c4 orelha por dentro, bochechas, almofadinhas e listras."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.33
g = Grade((-48, -58, 0), (54, 62, 80), passo)
X, Y, Z = g.x, g.y, g.z
INC = 16          # inclinação do celular
FENDA = 13.0      # celulares de até ~12 mm com capinha

# corpo em pãozinho
corpo = elipsoide(g, (0, 14, 21), (36, 44, 22))
corpo = smin(corpo, caixa(g, (0, 14, 6), (34, 42, 6), 6), 8)
CY, CZ = -26, 38
corpo = smin(corpo, elipsoide(g, (0, CY, CZ), (27, 22, 22)), 9)
for s in (-1, 1):
    corpo = smin(corpo, elipsoide(g, (s * 17, CY - 6, CZ - 9), (11, 10, 8.5)), 5)       # bochechas de pelo
# orelhas
orelha_in = []
for s in (-1, 1):
    c = (s * 15.5, CY + 3, CZ + 19)
    v = Vista(g, c, mul(rot_y(s * -20), rot_x(-10)))
    o = np.maximum(capsula(v, (c[0], c[1], c[2] - 6), (c[0], c[1], c[2] + 8), 8.5, 1.1), np.abs(v.y - c[1]) - 3.4)
    corpo = smin(corpo, o, 3)
    orelha_in.append(capsula(v, (c[0], c[1] - 3.4, c[2] - 3), (c[0], c[1] - 3.4, c[2] + 5.5), 5.0, 0.8))
for oi in orelha_in:
    corpo = menos(corpo, oi, 0.5)
orelha_cor = np.maximum(np.minimum.reduce(orelha_in) - 0.8, -corpo - 0.6)
# patinhas da frente aparecendo embaixo do queixo
almof = []
for s in (-1, 1):
    pata = elipsoide(g, (s * 12, CY - 16, 5.5), (8, 11, 5.5))
    for d in (-1, 0, 1):
        pata = smin(pata, esfera(g, (s * 12 + d * 3.9, CY - 25.5, 4.6), 2.6), 1.5)
    corpo = smin(corpo, pata, 3)
    for d in (-1, 0, 1):
        almof.append(esfera(g, (s * 12 + d * 3.9, CY - 27.2, 5.4), 1.3))
# rabo enrolado do lado direito, ponta levantadinha
corpo = smin(corpo, tubo(g, [(20, 54, 6), (36, 46, 5.5), (43, 26, 5), (42, 4, 5), (36, -10, 7), (35, -16, 12)], [5.6, 5.4, 5.0, 4.6, 4.2, 3.6]), 3)
corpo = corpo + 0.06 * ruido(g, 2.0, 21)
# listras de gatinho nas costas (cor 4, levemente em relevo)
listras = []
for k, yy in enumerate((24, 36, 48)):
    faixa = np.abs(Y - yy - 0.12 * (Z - 30)) - (2.4 - 0.3 * k)
    listras.append(np.maximum(np.maximum(faixa, 21 - Z), -(corpo + 1.2)))

# rosto
def fy(x, z):
    return CY - 22 * np.sqrt(max(0, 1 - (x / 27) ** 2 - ((z - CZ) / 22) ** 2))
olhos, brilho, boch = [], [], []
for s in (-1, 1):
    x0, z0 = s * 9.5, CZ + 2.5
    y0 = fy(x0, z0) + 0.9
    corpo = smin(corpo, elipsoide(g, (x0, y0, z0), (5.0, 2.4, 6.2)), 1)
    olhos.append(elipsoide(g, (x0, y0, z0), (5.0, 8, 6.2)))
    brilho.append(esfera(g, (x0 + 1.6, y0 - 2.2, z0 + 2.4), 1.5))
    brilho.append(esfera(g, (x0 - 1.4, y0 - 2.0, z0 - 2.4), 0.75))
    boch.append(elipsoide(g, (s * 18, fy(s * 18, CZ - 7) + 0.4, CZ - 7), (4.4, 2.4, 2.8)))
    corpo = smin(corpo, boch[-1], 0.8)
fz = CZ - 6.5
corpo = smin(corpo, np.minimum(elipsoide(g, (-2.9, fy(0, fz) + 0.8, fz), (4, 2.8, 3.1)), elipsoide(g, (2.9, fy(0, fz) + 0.8, fz), (4, 2.8, 3.1))), 1.5)
nariz = np.maximum(elipsoide(g, (0, fy(0, fz + 2.8) - 0.8, fz + 2.8), (2.4, 2.0, 1.7)), -(Z - fz - 1.2))
corpo = smin(corpo, nariz, 0.5)
boca = None
for s in (-1, 1):
    b = tubo(g, [(0, fy(0, fz + 0.8) - 1.6, fz + 0.8), (s * 1.7, fy(s * 1.7, fz - 1.6) - 2.3, fz - 1.8), (s * 3.7, fy(s * 3.7, fz - 0.6) - 2.0, fz - 0.4)], [0.5, 0.5, 0.42])
    boca = b if boca is None else np.minimum(boca, b)
corpo = menos(corpo, boca, 0.2)
boca_cor = np.maximum(boca - 0.7, -corpo - 0.8)
bigodes = None
for s in (-1, 1):
    for k in (-1, 1):
        b = capsula(g, (s * 6.5, fy(s * 6.5, fz) - 1.5, fz + k * 1.2), (s * 14.5, fy(s * 14.5, fz) - 1.0, fz + 0.6 + k * 2.8), 0.5, 0.38)
        bigodes = b if bigodes is None else np.minimum(bigodes, b)
corpo = menos(corpo, bigodes, 0.2)

# fenda do celular (inclinada para trás) e canal do cabo saindo por trás
F0 = (0, 4, 8)
v = Vista(g, F0, rot_x(-INC))
fenda = caixa(v, (0, 4 + FENDA / 2, 60), (60, FENDA / 2, 52), 1.0)
corpo = menos(corpo, fenda, 0.8)
cabo = np.minimum(caixa(g, (0, 30, 4.5), (5.5, 30, 4.5), 2.0), caixa(g, (0, 8, 4.5), (5.5, 5, 8), 2.0))
corpo = menos(corpo, cabo, 0.8)
corpo = np.maximum(corpo, -Z)

reg = {"c3": np.minimum.reduce(brilho),
       "c2": np.minimum.reduce([np.maximum(np.minimum.reduce(olhos), -np.minimum.reduce(brilho)), nariz - 0.2, boca_cor]),
       "c4": np.minimum.reduce(boch + almof + listras + [orelha_cor])}
for k, v_ in exportar(g, dividir(corpo, reg), os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "gatinho"), faces=400000).items():
    print(k, v_)
