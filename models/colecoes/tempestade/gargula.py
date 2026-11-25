"""Dragão de Pedra – gárgula de dragão agachada sobre um pedestal de pedra, asas meio abertas, chifres para trás,
garras agarradas na borda, rabo enrolado na lateral e olhos acesos. Decoração de estante ou guardião da mesa.
78 × 72 × 104 mm. Cores: c1 pedra, c2 pedestal (blocos), c3 chifres e garras, c4 olhos.
Em pé, suporte em árvore só sob as pontas das asas e o queixo."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.25)
g = Grade((-44, -40, 0), (44, 40, 106), passo)
X, Y, Z = g.x, g.y, g.z
rr = ruido(g, 1.2, 151)
# pedestal
ped = caixa(g, (0, 2, 14), (26, 22, 14), 1.5) + ruido(g, 2.0, 152) * 0.25
ped = smin(ped, caixa(g, (0, 2, 2.5), (30, 26, 2.5), 1.2), 1)
ped = smin(ped, caixa(g, (0, 2, 27), (28, 24, 2), 1.2), 1)
m = np.mod(Z - 5, 7)
ped = menos(ped, np.maximum(np.minimum(m, 7 - m) - 0.4, np.maximum(np.maximum(np.abs(X) - 26.2, np.abs(Y - 2) - 22.2) * -1 - 0.6, np.maximum(5 - Z, Z - 25))), 0.2)
# corpo agachado
Z0 = 29.0
corpo = elipsoide(g, (0, 6, Z0 + 15), (12, 13, 15))
peito = elipsoide(g, (0, -4, Z0 + 22), (10.5, 9, 12))
corpo = smin(corpo, peito, 4)
cab = elipsoide(g, (0, -10, Z0 + 40), (8.5, 9, 7.5))
foc = elipsoide(g, (0, -19, Z0 + 37.5), (5.2, 7, 4.2))
cab = smin(cab, foc, 3)
corpo = smin(corpo, capsula(g, (0, -2, Z0 + 30), (0, -8, Z0 + 37), 6, 5), 3)
corpo = smin(corpo, cab, 3)
boca = np.maximum(elipsoide(g, (0, -22, Z0 + 35.6), (3.6, 5, 1.2)), -(Y + 17))
corpo = menos(corpo, boca, 0.4)
# pernas dobradas com garras agarradas na borda da frente
garras = None
for sx in (-1, 1):
    corpo = smin(corpo, elipsoide(g, (sx * 10, 6, Z0 + 8), (6, 10, 8)), 3)             # coxa
    corpo = smin(corpo, capsula(g, (sx * 10, -2, Z0 + 4), (sx * 9, -14, Z0 + 2), 3.4, 3), 2)
    corpo = smin(corpo, capsula(g, (sx * 7, -6, Z0 + 20), (sx * 8, -16, Z0 + 3), 3.0, 2.6), 2)   # braços apoiados
    for k in (-1, 0, 1):
        for (yy, zz) in [(-14, Z0 + 2), (-16, Z0 + 3)]:
            gr = capsula(g, (sx * 9 + k * 2.2, yy - 1, zz), (sx * 9 + k * 2.4, -21.5, Z0 - 3), 1.1, 0.35)
            garras = gr if garras is None else np.minimum(garras, gr)
# rabo enrolado na lateral do pedestal
rabo = tubo(g, [(0, 18, Z0 + 6), (14, 24, Z0 + 1), (27, 14, Z0 - 6), (27, -4, Z0 - 12), (24, -14, Z0 - 8)], [5, 4, 3, 2, 1.2])
corpo = smin(corpo, rabo, 2)
# asas meio abertas
for sx in (-1, 1):
    v = Vista(g, (sx * 9, 12, Z0 + 26), mul(rot_z(sx * -20), rot_y(sx * -35)))
    mem = np.maximum(np.abs(v.y - 12) - 1.2, np.maximum(np.sqrt((v.x - sx * 20) ** 2 + (v.z - Z0 - 26) ** 2) - 18,
                                                      -(np.sqrt((v.x - sx * 26) ** 2 + (v.z - Z0 - 8) ** 2) - 14)))
    mem = np.maximum(mem, -(sx * (v.x - sx * 6)))
    osso = tubo(v, [(sx * 6, 12, Z0 + 26), (sx * 18, 12, Z0 + 42), (sx * 36, 12, Z0 + 34)], [2.6, 1.8, 0.8])
    corpo = smin(corpo, np.minimum(mem, osso), 1.5)
corpo = corpo + rr * 0.15
# chifres e olhos
chif = None
for sx in (-1, 1):
    c = tubo(g, [(sx * 4.5, -6, Z0 + 45), (sx * 7, 2, Z0 + 50), (sx * 7.5, 10, Z0 + 52)], [2.4, 1.6, 0.4])
    chif = c if chif is None else np.minimum(chif, c)
    chif = np.minimum(chif, capsula(g, (sx * 6, -4, Z0 + 43), (sx * 11, 0, Z0 + 42), 1.4, 0.4))
olhos = np.minimum(elipsoide(g, (-4.4, -16.6, Z0 + 42), (1.8, 1.2, 1.1)), elipsoide(g, (4.4, -16.6, Z0 + 42), (1.8, 1.2, 1.1)))
corpo = menos(corpo, np.minimum(elipsoide(g, (-4.4, -16.8, Z0 + 42), (2.3, 1.6, 1.6)), elipsoide(g, (4.4, -16.8, Z0 + 42), (2.3, 1.6, 1.6))), 0.3)
claro = np.minimum(chif, garras)
tudo = np.minimum.reduce([ped, corpo, claro, olhos])
tudo = np.maximum(tudo, -Z)
partes = dividir(tudo, {"c4": olhos, "c3": claro, "c2": ped})
for k, vv in exportar(g, partes, saida(__file__, "gargula", IMP), faces=None).items():
    print(k, vv)
