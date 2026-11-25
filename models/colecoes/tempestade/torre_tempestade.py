"""Torre da Tempestade Rubra – torre de dados redonda de pedra rachada, coroada por uma nuvem de tempestade vermelha
de onde descem raios pelas paredes. O dado entra pelo olho da nuvem, desce por três rampas e sai pelo portão para
a bandeja embutida, com o chão de lajes partidas. Uma peça só: 130 × 150 × 172 mm. Dado máximo: d20 de 26 mm.
Cores: c1 pedra, c2 rachaduras e portão, c3 raios, c4 nuvem. Em pé, sem suporte (nuvem com balanço de 45°)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.45)
RE, RI, HT = 33.0, 28.0, 138.0
g = Grade((-66, -100, 0), (66, 50, 176), passo)
X, Y, Z = g.x, g.y, g.z
rr = ruido(g, 2.0, 171)
rad = np.sqrt(X ** 2 + Y ** 2)
ang = np.arctan2(Y, X)
re_z = RE - 3 * np.clip(Z / HT, 0, 1)
corpo = np.maximum(rad - re_z, np.maximum(-Z, Z - HT)) + rr * 0.3
corpo = smin(corpo, np.maximum(rad - RE - 4, np.maximum(-Z, Z - 9)), 1.5)
# blocos de pedra
fila = np.floor(Z / 10)
du = np.mod(ang * RE + np.mod(fila, 2) * 9, 18)
dz = np.mod(Z, 10)
sul = np.minimum(np.minimum(dz, 10 - dz), np.minimum(du, 18 - du)) - 0.45
corpo = menos(corpo, np.maximum(-sul, np.maximum(-(rad - re_z + 0.8), np.maximum(10 - Z, Z - HT + 2))), 0.2)
# canal, rampas, piso
corpo = menos(corpo, np.maximum(rad - RI, -1 - Z))
for (z0, s) in [(120, 1), (92, -1), (64, 1)]:
    plano = np.abs((Z - z0) - 1.19 * s * Y) - 1.6
    corpo = np.minimum(corpo, np.maximum(plano, np.maximum(rad - RI - 0.5, -s * Y - 9)))
corpo = np.minimum(corpo, np.maximum((Z - 2) - 0.55 * (Y + RI), np.maximum(rad - RI - 0.5, -Z)))
# portão
W, ZT = 19.0, 26.0
arco = np.minimum(np.maximum(np.abs(X) - W, np.maximum(-1 - Z, Z - ZT)), np.maximum(np.sqrt(X ** 2 + (Z - ZT) ** 2) - W, ZT - Z))
corpo = menos(corpo, np.maximum(arco, Y + 10))
portao = np.maximum(np.maximum(arco - 2.4, -arco), np.maximum(np.abs(Y + RE + 0.3) - 1.4, -Z))
# bandeja embutida com lajes partidas
band = np.maximum(caixa(g, (0, -64, 8), (58, 34, 8), 8), -Z)
band = menos(band, caixa(g, (0, -64, 11), (53, 29, 8), 5))
band = menos(band, np.maximum(arco, np.maximum(Y + 40, -Y - 22)))
m1, m2 = np.mod(X + 4 + 3 * np.sin(Y * 0.2), 15), np.mod(Y + 6 * np.mod(np.floor(X / 15), 2) + 2 * np.sin(X * 0.3), 15)
lajes = np.minimum(np.minimum(m1, 15 - m1), np.minimum(m2, 15 - m2)) - 0.5
band = menos(band, np.maximum(lajes, np.maximum(caixa(g, (0, -64, 11), (53, 29, 8), 5) + 0.6, np.abs(Z - 3) - 0.6)), 0.2)
corpo = np.minimum(corpo, band)
# rachaduras nas paredes
rach = None
for (a0, z0, z1) in [(-100, 40, 90), (-60, 70, 125), (200, 30, 80), (20, 50, 110)]:
    pts = []
    for t in np.linspace(0, 1, 5):
        a = np.radians(a0 + 8 * np.sin(t * 9 + a0))
        z = z0 + (z1 - z0) * t
        rz = RE - 3 * z / HT
        pts.append((rz * np.cos(a), rz * np.sin(a), z))
    r_ = tubo(g, pts, [0.9, 0.8, 0.7, 0.6, 0.4])
    rach = r_ if rach is None else np.minimum(rach, r_)
corpo = menos(corpo, rach, 0.3)
escuro = np.minimum(rach - 0.6, portao)                  # fundo das rachaduras e moldura do portão
# nuvem no topo (bolas que saem para fora), com o olho por onde o dado entra
nuv = None
for k in range(11):
    a = k * 2 * np.pi / 11
    rr_ = 7.5 + 2 * np.sin(k * 1.7)
    b = esfera(g, ((RE - 1) * np.cos(a), (RE - 1) * np.sin(a), HT + 4 + 3 * np.sin(k * 2.3)), rr_ + 2)
    nuv = b if nuv is None else smin(nuv, b, 3)
for k in range(6):
    a = k * np.pi / 3 + 0.4
    nuv = smin(nuv, esfera(g, ((RE - 12) * np.cos(a), (RE - 12) * np.sin(a), HT + 10), 8.5), 3)
nuv = smin(nuv, elipsoide(g, (0, 0, HT + 4), (RE + 2, RE + 2, 6)), 4)
nuv = menos(nuv, np.maximum(rad - 17, HT - 6 - Z) , 2.0)                    # olho da nuvem (entrada)
nuv = np.maximum(nuv, HT - 6 - Z)
# raios descendo da nuvem pelas paredes
raios = None
for (a0, comp, w) in [(-80, 55, 2.0), (30, 40, 1.7), (160, 48, 1.8), (-150, 36, 1.5)]:
    pts = []
    for i, t in enumerate(np.linspace(0, 1, 6)):
        a = np.radians(a0 + (5 if i % 2 else -5))
        z = HT - comp * t
        rz = RE - 3 * z / HT + 0.6
        pts.append((rz * np.cos(a), rz * np.sin(a), z))
    rr2 = [w * (1 - 0.6 * t) for t in np.linspace(0, 1, 6)]
    r_ = tubo(g, pts, rr2)
    raios = r_ if raios is None else np.minimum(raios, r_)
tudo = np.minimum.reduce([corpo, nuv, raios, portao])
tudo = np.maximum(tudo, -Z)
partes = dividir(tudo, {"c3": raios, "c4": nuv, "c2": escuro})
for k, vv in exportar(g, partes, saida(__file__, "torre_tempestade", IMP), faces=None).items():
    print(k, vv)
