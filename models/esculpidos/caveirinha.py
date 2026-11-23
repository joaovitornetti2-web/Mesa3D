"""Caveirinha – macabra e fofa: coroa de florzinhas, rachadinha remendada e sentada em ossinhos cruzados.
c1 osso · c2 órbitas e nariz · c3 brilho nos olhos e miolo das flores · c4 pétalas."""
import sys
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.2
g = Grade((-26, -24, 0), (26, 24, 40), passo)
X, Y, Z = g.x, g.y, g.z
CZ = 17.8

# crânio + maçãs do rosto + maxilar arredondado
cranio = elipsoide(g, (0, 1, CZ), (14.5, 14, 13.5))
for s in (-1, 1):
    cranio = smin(cranio, elipsoide(g, (s * 8.2, -7.5, CZ - 6), (4.6, 4.5, 3.6)), 2.4)
maxilar = caixa(g, (0, -5.5, CZ - 11), (7.6, 6.0, 3.6), 3.2)
cranio = smin(cranio, maxilar, 3.0)
# têmporas afundadas
for s in (-1, 1):
    cranio = menos(cranio, esfera(g, (s * 16.5, -1, CZ - 3), 4.0), 2.5)

def fy(x, z):
    return -0.94 * 14 * np.sqrt(max(0, 1 - (x / 14.5) ** 2 - ((z - CZ) / 13.5) ** 2)) + 1

# órbitas fundas (expressão: uma redonda, outra arqueada)
orb = None
for s, rz in ((-1, 4.9), (1, 4.3)):
    x0, z0 = s * 5.6, CZ - 0.5
    o = elipsoide(g, (x0, fy(x0, z0) + 0.6, z0), (4.4, 4.0, rz))
    orb = o if orb is None else np.minimum(orb, o)
cranio = menos(cranio, orb, 0.8)
orb_cor = np.maximum(np.minimum(elipsoide(g, (-5.6, fy(-5.6, CZ) + 0.6, CZ - 0.5), (5.3, 5.0, 5.8)),
                                elipsoide(g, (5.6, fy(5.6, CZ) + 0.6, CZ - 0.5), (5.3, 5.0, 5.2))), -cranio - 1.0)
brilho = np.minimum(esfera(g, (-4.6, fy(-4.6, CZ) + 1.6, CZ + 1.0), 1.25), esfera(g, (6.4, fy(6.4, CZ) + 1.6, CZ + 0.8), 1.05))
# nariz em coraçãozinho invertido
nariz = np.minimum(elipsoide(g, (-0.9, -12.2, CZ - 6.8), (1.2, 2.2, 1.6)), elipsoide(g, (0.9, -12.2, CZ - 6.8), (1.2, 2.2, 1.6)))
nariz = smin(nariz, esfera(g, (0, -12.0, CZ - 8.4), 0.9), 0.8)
cranio = menos(cranio, nariz, 0.3)
nariz_cor = np.maximum(smin(nariz, nariz, 1) - 0.8, -cranio - 0.8)
# dentes: sulcos verticais no maxilar e linha da mordida
for i in range(-3, 4):
    cranio = menos(cranio, caixa(g, (i * 2.4 + 1.2, -11.6, CZ - 12.6), (0.28, 1.5, 2.0), 0.2), 0.15)
cranio = menos(cranio, caixa(g, (0, -11.6, CZ - 12.6), (8, 1.5, 0.28), 0.2), 0.15)
# rachadinha em zigue-zague com pontos de costura
rach = tubo(g, [(6, -6, CZ + 12.2), (8, -4, CZ + 10.6), (7.2, -5.5, CZ + 8.6), (9.4, -6.5, CZ + 6.8)], [0.5, 0.45, 0.4, 0.3])
cranio = menos(cranio, rach, 0.2)
for (px, pz) in ((5.6, CZ + 10.6), (9.0, CZ + 9.4), (7.0, CZ + 7.4)):
    cranio = smin(cranio, capsula(g, (px - 1.2, -8, pz), (px + 1.2, -8, pz + 0.4), 0.38), 0.2) if False else cranio

# ossinhos cruzados embaixo (base)
ossos = None
for a in (35, -35):
    r = np.radians(a)
    d = np.array([np.cos(r), np.sin(r)])
    p1, p2 = -16 * d, 16 * d
    o = capsula(g, (p1[0], p1[1], 2.4), (p2[0], p2[1], 2.4), 2.2)
    for p in (p1, p2):
        perp = np.array([-d[1], d[0]])
        for s in (-1, 1):
            q = p + perp * s * 1.8 + d * np.sign(p @ d) * 0.6
            o = smin(o, esfera(g, (q[0], q[1], 2.6), 2.4), 1.0)
    ossos = o if ossos is None else smin(ossos, o, 1.0)
ossos = smin(ossos, cilindro(g, (0, 0, 0), 8, 4, 1.5), 2)
corpo = smin(cranio, ossos, 2.0)

# coroa de florzinhas
flores_p, flores_m, folhas = None, None, None
for (fx, fy_, fz, r, inc) in ((-9.0, -5.5, CZ + 10.0, 3.3, -30), (-2.0, -2.8, CZ + 13.4, 2.6, -10), (4.8, -1.5, CZ + 13.2, 2.2, 15)):
    v = Vista(g, (fx, fy_, fz), mul(rot_y(inc), rot_x(28)))
    m = esfera(v, (fx, fy_, fz + 0.9), r * 0.45)
    p = None
    for k in range(5):
        a = np.radians(k * 72 + 10)
        e = elipsoide(v, (fx + r * 0.75 * np.cos(a), fy_ + r * 0.75 * np.sin(a), fz + 0.2), (r * 0.62, r * 0.62, r * 0.32))
        p = e if p is None else np.minimum(p, e)
    flores_p = p if flores_p is None else np.minimum(flores_p, p)
    flores_m = m if flores_m is None else np.minimum(flores_m, m)
    corpo = smin(corpo, np.minimum(p, m), 0.6)
for (a, b) in (((-12.5, -3, CZ + 7.5), (-15.5, -2, CZ + 4.5)), ((7.5, 0, CZ + 12.6), (11.5, 0.5, CZ + 11.0))):
    corpo = smin(corpo, capsula(g, a, b, 1.2, 0.3), 0.6)

corpo = corpo + 0.03 * ruido(g, 1.5, 9)
corpo = np.maximum(corpo, -Z)
reg = {"c3": np.minimum(brilho, flores_m - 0.05), "c4": flores_p - 0.1, "c2": np.minimum(orb_cor, nariz_cor)}
for k, v_ in exportar(g, dividir(corpo, reg), "stl/caveirinha", faces=300000).items():
    print(k, v_)
