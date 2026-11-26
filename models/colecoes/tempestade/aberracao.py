"""Aberração da Tempestade – criatura chibi (~58 mm) nascida da tempestade rubra: corpo de inseto com placas de
carapaça, seis olhos, mandíbulas, quatro patas finas e cristais vermelhos brotando das costas. Base redonda de
42 mm com chão rachado. Cores: c1 carapaça, c2 juntas e mandíbulas, c3 olhos, c4 cristais e rachaduras.
Em pé, sem suporte (patas apoiadas na base)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.12)
MN, MX = (-30, -26, 0), (30, 26, 62)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    base = cilindro(g, (0, 0, 0), 21, 3.2, 1.2)
    rach = None
    for (a, L) in [(20, 13), (140, 11), (250, 14), (320, 9)]:
        r = np.radians(a)
        t = tubo(g, [(0, 0, 3.2), (L * 0.5 * np.cos(r + 0.3), L * 0.5 * np.sin(r + 0.3), 3.2), (L * np.cos(r), L * np.sin(r), 3.2)], [0.9, 0.7, 0.4])
        rach = t if rach is None else np.minimum(rach, t)
    rach = np.maximum(rach, np.abs(Z - 3.0) - 0.5)
    abd = elipsoide(g, (0, 7, 18), (10, 11, 9))                     # abdome atrás
    tor = elipsoide(g, (0, -2, 26), (9, 8, 9))
    cab = elipsoide(g, (0, -8, 36), (9.5, 8, 8))
    corpo = smin(smin(abd, tor, 3), cab, 3)
    # placas de carapaça: sulcos em anéis no abdome e no tórax
    an = np.abs(np.mod(Y - 2, 4.5) - 2.25) - 0.4
    corpo = menos(corpo, np.maximum(an, np.maximum(-(corpo + 0.8), -(Y - 1))), 0.2)
    # patas (4) com juntas
    juntas = None
    for sx in (-1, 1):
        for (yb, ang) in [(-3, -35), (5, 30)]:
            a = np.radians(ang)
            p0 = (sx * 7, yb, 22)
            p1 = (sx * 16, yb + 9 * np.sin(a), 24)
            p2 = (sx * 17, yb + 12 * np.sin(a), 3.6)
            corpo = smin(corpo, tubo(g, [p0, p1, p2], [2.2, 1.6, 1.0]), 1.2)
            j = esfera(g, p1, 2.3)
            juntas = j if juntas is None else np.minimum(juntas, j)
    # bracinhos com garras na frente
    for sx in (-1, 1):
        corpo = smin(corpo, tubo(g, [(sx * 6, -7, 28), (sx * 11, -13, 25), (sx * 9, -17, 21)], [1.8, 1.4, 0.5]), 1)
    # mandíbulas
    mand = None
    for sx in (-1, 1):
        m = tubo(g, [(sx * 3, -14, 32), (sx * 5.5, -18, 30.5), (sx * 2.2, -20.5, 29)], [1.6, 1.2, 0.4])
        mand = m if mand is None else np.minimum(mand, m)
    # seis olhos
    olhos = None
    for (x, z, r) in [(-3.8, 39.5, 2.2), (3.8, 39.5, 2.2), (-6.5, 36.5, 1.6), (6.5, 36.5, 1.6), (-2.2, 35.3, 1.3), (2.2, 35.3, 1.3)]:
        o = esfera(g, (x, -14.2 + abs(x) * 0.35, z), r)
        olhos = o if olhos is None else np.minimum(olhos, o)
    # cristais vermelhos nas costas
    crist = None
    for (x, y, z, ax, ay, h) in [(0, 10, 26, -25, 0, 14), (-6, 8, 24, -20, -30, 10), (6, 9, 23, -15, 30, 11), (0, 1, 33, -10, 0, 9), (-3, 14, 18, -45, -15, 8)]:
        v = Vista(g, (x, y, z), mul(rot_x(ax), rot_y(ay)))
        ang6 = np.arctan2(v.y - y, v.x - x)
        sec = np.round(ang6 / (np.pi / 3)) * (np.pi / 3)
        hexr = (v.x - x) * np.cos(sec) + (v.y - y) * np.sin(sec)
        t = np.clip((v.z - z) / h, 0, 1)
        c = np.maximum(hexr - 2.4 * (1 - t ** 1.6) - 0.2, np.maximum(z - 4 - v.z, v.z - z - h))
        crist = c if crist is None else np.minimum(crist, c)
    # carapaça em segmentos com sulcos e poros; chão gasto
    perto = np.clip(1 - np.abs(corpo) / 1.2, 0, 1)
    corpo = corpo + perto * (0.3 * np.clip(1 - np.abs(np.mod(Z * 0.9 + 0.3 * np.sin(X * 0.4), 3.0) - 1.5) / 0.35, 0, 1) + 0.12 * np.clip(ruido_cel(g, 0.7, 121) - 0.8, 0, None))
    base = base + desgaste(g, 0.4, 122)
    tudo = np.minimum.reduce([smin(corpo, base, 1.5), juntas, mand, olhos, crist, rach])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c4": np.minimum(crist, rach), "c3": olhos, "c2": np.minimum(juntas, mand)}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "aberracao", IMP)).items():
        print(k, v)
