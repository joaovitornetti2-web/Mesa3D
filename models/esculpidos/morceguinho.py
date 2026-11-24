"""Morceguinho – notívago de gorro de dormir, acordadíssimo, de pé numa lua minguante.
c1 corpo/asas · c2 olhos/boca · c3 brilho, presinha e pompom · c4 gorro, orelha por dentro, bochechas e lua."""
import sys
from sdf import *
from rosto import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.2
g = Grade((-36, -24, 0), (36, 22, 56), passo)
X, Y, Z = g.x, g.y, g.z
MZ, MR = 23.0, 13.5

corpo = elipsoide(g, (0, 0, MZ), (MR, MR * 0.92, MR * 1.02))
# orelhonas com a parte de dentro cavada
orelha_in = None
for s in (-1, 1):
    c = (s * 7.2, 0.5, MZ + 13)
    v = Vista(g, c, mul(rot_y(s * 22), rot_x(-6)))
    o = capsula(v, (c[0], c[1], c[2] - 6), (c[0], c[1], c[2] + 6), 5.0, 0.9)
    o = np.maximum(o, np.abs(v.y - c[1]) - 2.2)
    corpo = smin(corpo, o, 2.5)
    oi = capsula(v, (c[0], c[1] - 2.6, c[2] - 3.5), (c[0], c[1] - 2.6, c[2] + 4.5), 2.8, 0.5)
    orelha_in = oi if orelha_in is None else np.minimum(orelha_in, oi)
corpo = menos(corpo, orelha_in, 0.4)
orelha_cor = np.maximum(orelha_in - 0.9, -corpo - 0.7)
# asas abertas para um abraço
for s in (-1, 1):
    c = (s * 11, 3, MZ + 2)
    v = Vista(g, c, mul(rot_z(s * -25), rot_y(s * 10)))
    lx = (v.x - c[0]) * s
    memb = elipsoide(v, (c[0] + s * 11, c[1], c[2] + 1.5), (12, 6, 9))
    memb = np.maximum(np.maximum(memb, np.abs(v.y - c[1]) - 0.9), -lx + 0.4)
    for k in range(3):
        memb = menos(memb, esfera(v, (c[0] + s * (8 + k * 6), c[1], c[2] - 8.6 + k * 2.4), 3.8), 0.4)
    ossos = None
    for (bx, bz) in ((19, 7.5), (19.5, 0.5)):
        o = capsula(v, (c[0], c[1], c[2] + 3), (c[0] + s * bx, c[1], c[2] + bz), 1.5, 0.6)
        ossos = o if ossos is None else np.minimum(ossos, o)
    corpo = smin(corpo, smin(memb, ossos, 0.6), 1.6)
    corpo = smin(corpo, tubo(g, [(s * 4.5, 0, MZ - 10), (s * 5, -0.5, 7.5), (s * 5.2, -2, 5.6)], [2.4, 1.8, 1.7]), 1.6)   # pezinhos

corpo = corpo + 0.03 * ruido(g, 1.5, 6)

# rosto animado
f = Rosto(g, MZ, MR, 0.92)
f.olho(-5.2, MZ + 2.4, 3.6, 4.4, (0.2, 0.2))
f.olho(5.2, MZ + 2.4, 3.6, 4.4, (0.2, 0.2))
f.boca(0, MZ - 4.2, 3.0, 2.2)
f.presa(-1.8, MZ - 4.6, 2.0, 0.8)
f.bochecha(-9.3, MZ - 2.2, 2.2, 1.4)
f.bochecha(9.3, MZ - 2.2, 2.2, 1.4)
corpo = f.aplicar(corpo)

# gorro de dormir caído para o lado, com aba e pompom
HC = (0, 1.5, MZ + 9.5)
v = Vista(g, HC, mul(rot_y(18), rot_x(8)))
gorro = tubo(v, [(0, 1.5, MZ + 9.6), (0.6, 2, MZ + 14), (2.5, 2.8, MZ + 18), (7, 3, MZ + 20.5), (12, 2, MZ + 19), (15, 0.5, MZ + 15.5)],
             [7.0, 6.0, 4.6, 3.2, 2.2, 1.4])
gorro = gorro + 0.25 * np.sin(1.6 * v.z + 2.5 * v.x * 0.2)
aba = toro(v, (0, 1.5, MZ + 9.8), 6.6, 1.8, 1.0)
gorro = smin(gorro, aba, 0.8)
pompom = esfera(g, (12.5, 0.8, MZ + 14.6), 3.0) + 0.25 * ruido(g, 0.5, 13)
gorro = menos(gorro, orelha_in - 0.5) if False else gorro
corpo = smin(corpo, gorro, 1.0)
corpo = smin(corpo, pompom, 0.6)

# lua minguante como base
lua = np.maximum(cilindro(g, (0, -1, 0), 15, 4.2, 1.4), -cilindro(g, (3.5, 9.5, -1), 10.5, 7, 1.0))
corpo = smin(corpo, lua, 1.2)
corpo = np.maximum(corpo, -Z)

reg = {"c3": juntar(f.c3 + [pompom - 0.3]), "c4": juntar(f.c4 + [gorro - 0.6, orelha_cor, lua - 0.5]), "c2": juntar(f.c2)}
for k, v_ in exportar(g, dividir(corpo, reg), "stl/morceguinho", faces=300000).items():
    print(k, v_)
