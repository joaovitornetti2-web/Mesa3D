"""Minotauro Guerreiro – figura chibi (~62 mm): minotauro troncudo de chifres grandes e argola no focinho,
ombreira de metal, tanga de couro e um machado de duas lâminas apoiado no ombro. Base redonda de 32 mm com pedras.
Cores: c1 pelo, c2 metal (machado, ombreira, argola), c3 chifres, olhos e cascos, c4 tanga e faixa.
Em pé, suporte em árvore só sob a lâmina do machado."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.22)
g = Grade((-32, -24, 0), (32, 24, 68), passo)
X, Y, Z = g.x, g.y, g.z
rr = ruido(g, 0.9, 101)
base = cilindro(g, (0, 0, 0), 16, 3.2, 1.2) + ruido(g, 1.5, 102) * 0.25
corpo = elipsoide(g, (0, 1, 22), (13, 10.5, 12))                 # tronco
corpo = smin(corpo, elipsoide(g, (0, -1, 31), (14.5, 10, 7)), 4)   # peitoral largo
cab = elipsoide(g, (0, -2, 44), (10, 9, 9))
foc = elipsoide(g, (0, -10, 41), (6.4, 5, 4.6))
cab = smin(cab, foc, 3)
corpo = smin(corpo, cab, 4)
# pernas curtas com cascos
cascos = None
for sx in (-1, 1):
    corpo = smin(corpo, capsula(g, (sx * 6, 1, 14), (sx * 6.5, 0, 6), 5, 4.2), 2)
    c = cilindro(g, (sx * 6.5, -0.5, 3), 4.6, 3.2, 1.0)
    c = menos(c, np.maximum(np.abs(X - sx * 6.5) - 0.4, np.maximum(Y + 0.5, -Y - 6)), 0.2)
    cascos = c if cascos is None else np.minimum(cascos, c)
# braços: esquerdo segura o cabo do machado no ombro, direito com punho fechado
corpo = smin(corpo, capsula(g, (-13, 0, 31), (-16, -5, 22), 4.4, 3.8), 2)
corpo = smin(corpo, esfera(g, (-16.5, -6, 20.5), 4.2), 1.5)
corpo = smin(corpo, capsula(g, (13, 0, 31), (12, -8, 36), 4.4, 3.8), 2)
corpo = smin(corpo, esfera(g, (11.5, -9.5, 37.5), 4.0), 1.5)
corpo = corpo + rr * 0.12
# orelhas, chifres, olhos, narinas e argola
claro = None
for sx in (-1, 1):
    corpo = smin(corpo, elipsoide(Vista(g, (sx * 10.5, 0, 47), rot_y(sx * 50)), (sx * 10.5, 0, 47), (1.8, 3, 4.5)), 1)
    ch = tubo(g, [(sx * 6, -1, 50), (sx * 13, -1, 53), (sx * 18, -3, 59), (sx * 18.5, -6, 64)], [3.0, 2.5, 1.6, 0.5])
    claro = ch if claro is None else np.minimum(claro, ch)
    claro = np.minimum(claro, esfera(g, (sx * 4.2, -9.4, 46), 1.6))
    corpo = menos(corpo, esfera(g, (sx * 2.4, -15.2, 41.5), 1.1), 0.3)
olhos_p = np.minimum(esfera(g, (-4.1, -10.8, 46), 0.85), esfera(g, (4.1, -10.8, 46), 0.85))
argola = toro(Vista(g, (0, -14.6, 38.5), rot_x(10)), (0, -14.6, 38.5), 2.4, 0.6)
claro = np.minimum(claro, cascos)
# ombreira e machado (cabo do punho direito até atrás do ombro, lâminas atrás da cabeça)
ombreira = np.maximum(elipsoide(g, (12, 0, 33), (7, 7.5, 5.5)), -elipsoide(g, (12, 0, 31), (6, 6.5, 5)))
ombreira = np.minimum(ombreira, esfera(g, (12, 0, 38.4), 1.4))
p0, p1 = np.array([11.5, -12, 40.5]), np.array([12.5, 12, 56])
cabo = capsula(g, tuple(p0), tuple(p1), 1.4)
dirc = (p1 - p0) / np.linalg.norm(p1 - p0)
cl = p1 - dirc * 3
v = Vista(g, tuple(cl), mul(rot_x(-np.degrees(np.arctan2(dirc[2], dirc[1]))), np.eye(3)))
lam = None
for s in (-1, 1):
    l = np.maximum(np.sqrt((v.x - cl[0] - s * 3) ** 2 + (v.z - cl[2]) ** 2) - 9, -s * (v.x - cl[0]) + 1.2)
    l = np.maximum(l, np.abs(v.y - cl[1]) - 1.0)
    l = menos(l, np.sqrt((v.x - cl[0] - s * 13.5) ** 2 + (v.z - cl[2]) ** 2) - 6.5)
    lam = l if lam is None else np.minimum(lam, l)
metal = np.minimum.reduce([ombreira, cabo, lam, argola])
# tanga e faixa
tanga = np.maximum(np.abs(elipsoide(g, (0, 1, 16), (13.6, 11.2, 7))) - 0.9, np.abs(Z - 15) - 4)
tanga = np.minimum(tanga, np.maximum(caixa(g, (0, -10.5, 11), (4.5, 1.0, 5), 1), Z - 16))
faixa = np.maximum(np.abs(elipsoide(g, (0, 0.5, 28), (14.6, 11.2, 12.5))) - 0.7, np.abs((Z - 28) - 0.75 * X) - 2.2)
c4 = np.minimum(tanga, faixa)
tudo = np.minimum.reduce([smin(corpo, base, 1.5), claro, metal, c4, olhos_p])
tudo = np.maximum(tudo, -Z)
partes = dividir(tudo, {"c2": np.minimum(metal, olhos_p), "c3": claro, "c4": c4})
for k, vv in exportar(g, partes, saida(__file__, "minotauro", IMP), faces=None).items():
    print(k, vv)
