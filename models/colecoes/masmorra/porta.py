"""Porta da Masmorra – peça de cenário (escala 28–32 mm) e decoração: portal de pedra em arco com porta de tábuas,
dobradiças de ferro, argola de caveira e tochas dos dois lados, sobre uma base de 2 × 1 quadrados (50,8 × 25,4 mm).
Cerca de 76 mm de altura. Cores: c1 pedra, c2 ferro, c3 caveira, c4 chamas, c5 madeira.
Em pé, sem suporte (chamas com balanço curto)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.22)
g = Grade((-34, -16, 0), (34, 16, 82), passo)
X, Y, Z = g.x, g.y, g.z
rr = ruido(g, 1.2, 9)
base = caixa(g, (0, 0, 2), (25.4, 12.7, 2), 1.0) + rr * 0.2
# lajes da base
m = np.mod(X + 25.4, 12.7)
base = menos(base, np.maximum(np.minimum(m, 12.7 - m) - 0.4, np.abs(Z - 4) - 0.6), 0.2)
W, ZT, Z0 = 13.0, 44.0, 4.0
arco = lambda w: np.minimum(np.maximum(np.abs(X) - w, np.maximum(Z0 - Z, Z - ZT)), np.maximum(np.sqrt(X ** 2 + (Z - ZT) ** 2) - w, ZT - Z))
# portal: blocos em volta do arco (aduelas) e pilares
portal = np.maximum(arco(W + 9), np.abs(Y) - 6) + rr * 0.25
portal = smin(portal, np.maximum(np.maximum(np.abs(X) - 24, np.abs(Y) - 7), np.maximum(Z0 - Z, Z - 14)), 0.6)
ang = np.arctan2(Z - ZT, X)
aduela = np.minimum(np.mod(ang, np.pi / 9), np.pi / 9 - np.mod(ang, np.pi / 9)) * np.sqrt(X ** 2 + (Z - ZT) ** 2) - 0.45
fila = np.minimum(np.mod(Z - Z0, 8), 8 - np.mod(Z - Z0, 8)) - 0.45
sulco = np.where(Z > ZT, aduela, fila)
portal = menos(portal, np.maximum(sulco, np.maximum(-(np.abs(Y) - 5.3), -arco(W + 0.5))), 0.2)
portal = menos(portal, arco(W))
# porta de tábuas (recuada)
porta = np.maximum(arco(W + 0.3), np.abs(Y - 1) - 2.2)
mt = np.mod(X + W, 26 / 5)
porta = menos(porta, np.maximum(np.minimum(mt, 26 / 5 - mt) - 0.4, -(np.abs(Y - 1) - 1.6)), 0.2)
porta = porta + ruido(g, 0.5, 4) * 0.12
# dobradiças e argola
ferro = None
for zz in (14, 34):
    f = np.maximum(caixa(g, (-4, -1.6, zz), (10, 0.7, 1.6), 0.4), Y + 0)
    f = smin(f, esfera(g, (5.5, -1.4, zz), 1.6), 0.5)
    ferro = f if ferro is None else np.minimum(ferro, f)
for zz in (12, 22, 32, 42, 50):
    for xx in (-9, -2):
        ferro = np.minimum(ferro, esfera(g, (xx, -1.3, zz), 0.8))
argola = toro(Vista(g, (7, -2.4, 22), rot_x(90)), (7, -2.4, 22), 3.6, 0.8)
ferro = np.minimum(ferro, argola)
# caveira da argola
cav = smin(esfera(g, (7, -2.8, 28.2), 3.0), elipsoide(g, (7, -4.0, 26.2), (2.0, 1.8, 1.6)), 1.0)
cav = menos(cav, np.minimum.reduce([esfera(g, (5.9, -5.4, 28), 0.9), esfera(g, (8.1, -5.4, 28), 0.9)]), 0.2)
# tochas nos pilares
chamas = None
for sx in (-1, 1):
    sup = capsula(g, (sx * 19, -6, 26), (sx * 19, -10, 30), 1.0)
    taca = np.maximum(esfera(g, (sx * 19, -10.5, 31), 2.6), Z - 32)
    ferro = np.minimum(ferro, np.minimum(sup, np.minimum(taca, caixa(g, (sx * 19, -6.5, 27), (2, 0.6, 3), 0.4))))
    ch = smin(elipsoide(g, (sx * 19, -10.5, 34), (2.6, 2.6, 3.6)), capsula(g, (sx * 19, -10.5, 35), (sx * 19.5, -10.8, 40), 1.6, 0.3), 1)
    chamas = ch if chamas is None else np.minimum(chamas, ch)
tudo = np.minimum.reduce([base, portal, porta, ferro, cav, chamas])
tudo = np.maximum(tudo, -Z)
partes = dividir(tudo, {"c4": chamas, "c3": cav, "c2": ferro, "c5": porta})
for k, v in exportar(g, partes, saida(__file__, "porta", IMP), faces=None).items():
    print(k, v)
