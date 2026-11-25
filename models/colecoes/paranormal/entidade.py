"""Entidade das Sombras – figura de mesa (escala heroica, ~62 mm): vulto encapuzado de manto esfarrapado que
flutua sobre uma névoa, rosto vazio com dois olhos acesos, mãos compridas com garras saindo das mangas e fiapos
de sombra subindo. Base redonda de 32 mm. Cores: c1 manto, c2 vazio do capuz, c3 garras e máscara de osso, c4 olhos.
Em pé, suporte em árvore só sob as mãos."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.22)
g = Grade((-30, -26, 0), (30, 26, 68), passo)
X, Y, Z = g.x, g.y, g.z
rr = ruido(g, 1.4, 71)
rad = np.sqrt(X ** 2 + Y ** 2)
ang = np.arctan2(Y, X)
# névoa na base (onde o manto some)
nevoa = smin(cilindro(g, (0, 0, 0), 16, 3.0, 1.2), elipsoide(g, (0, 0, 4), (15, 13, 4.5)) + rr * 1.2, 2)
# manto: cone que alarga para baixo, barra esfarrapada (pontas)
t = np.clip((Z - 6) / 46, 0, 1)
r_manto = 15.5 - 7.5 * t ** 0.8
manto = np.maximum(np.sqrt((X / 1.0) ** 2 + ((Y - 1) / 0.85) ** 2) - r_manto, np.maximum(6 - Z, Z - 52))
barra = 6 + 5 * (0.5 + 0.5 * np.sin(ang * 7)) + 2.5 * np.sin(ang * 13 + 1)
manto = np.maximum(manto, barra - Z - 0.0)
manto = np.minimum(manto, np.maximum(np.sqrt((X / 1.0) ** 2 + ((Y - 1) / 0.85) ** 2) - r_manto, np.maximum(-Z, Z - 9)) + 3)   # liga na névoa
dobras = 0.7 * np.sin(ang * 9 + Z * 0.05)
manto = manto + dobras * (Z < 46) + rr * 0.15
# capuz
capuz = elipsoide(g, (0, 1, 52), (9.5, 9.5, 10.5))
capuz = smin(capuz, tubo(g, [(0, 3, 59), (0, 9, 61), (0, 15, 57), (0, 17, 51)], [4.5, 3.4, 2.2, 1.0]), 2.5)          # ponta do capuz caída para trás
manto = smin(manto, capuz, 4)
abertura = elipsoide(g, (0, -8, 51), (6.2, 6, 7.6))
manto = menos(manto, abertura, 1.0)
vazio = np.maximum(elipsoide(g, (0, -3.5, 51), (6.4, 5.5, 7.8)), -(Y + 9.5))
olhos = np.minimum(elipsoide(g, (-2.6, -8.6, 52), (1.3, 0.9, 0.8)), elipsoide(g, (2.6, -8.6, 52), (1.3, 0.9, 0.8)))
# braços: mangas largas e mãos compridas com garras
garras = None
for sx in (-1, 1):
    manga = capsula(g, (sx * 7, -1, 42), (sx * 13, -7, 31), 4.0, 5.2)
    manto = smin(manto, manga, 2.5)
    manto = menos(manto, elipsoide(g, (sx * 13.5, -7.8, 30.2), (3.6, 3.6, 2.0)), 0.8)
    mao = capsula(g, (sx * 13.5, -8, 31), (sx * 15, -11, 25), 2.0, 1.6)
    for k in (-1, 0, 1):
        d = tubo(g, [(sx * (15 + k * 1.2), -11, 25), (sx * (15.6 + k * 1.8), -12.5, 20), (sx * (15.2 + k * 2.1), -14.8, 16.5)], [0.9, 0.7, 0.3])
        mao = np.minimum(mao, d)
    garras = mao if garras is None else np.minimum(garras, mao)
# fiapos de sombra subindo nas costas
for (a, h) in [(100, 30), (80, 38), (130, 24)]:
    r = np.radians(a)
    p0 = (10 * np.cos(r), 10 * np.sin(r) + 1, h)
    manto = smin(manto, tubo(g, [p0, (13 * np.cos(r), 13 * np.sin(r) + 3, h + 9), (12 * np.cos(r + 0.3), 15 * np.sin(r + 0.3) + 4, h + 18)], [2.2, 1.4, 0.4]), 1.5)
tudo = np.minimum.reduce([nevoa, manto, vazio, olhos, garras])
tudo = np.maximum(tudo, -Z)
partes = dividir(tudo, {"c4": olhos, "c2": vazio, "c3": garras})
for k, v in exportar(g, partes, saida(__file__, "entidade", IMP), faces=None).items():
    print(k, v)
