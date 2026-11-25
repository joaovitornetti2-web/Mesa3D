"""Mão do Além – suporte de celular: uma mão magra sai de um monte de terra de cemitério e segura o celular
inclinado (cerca de 65°). O celular apoia na canaleta da frente (cabe capinha de até 13 mm) e encosta nos dedos.
Lapidezinha torta e ossinhos na terra. 96 × 84 × 92 mm.
Cores: c1 terra, c2 mão, c3 lápide e ossos, c4 unhas e manga rasgada. Em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.3)
g = Grade((-50, -44, 0), (50, 44, 96), passo)
X, Y, Z = g.x, g.y, g.z
rr = ruido(g, 2.0, 41)
terra = elipsoide(g, (0, 2, 0), (46, 40, 16)) + rr * 0.9
terra = np.maximum(terra, -Z)
# canaleta para o celular: rampa inclinada na frente
INC = np.radians(25)                       # inclinação do celular a partir da vertical
d = (Y + 22) * np.cos(INC) - (Z - 8) * np.sin(INC)        # distância ao plano das costas do celular
canal = np.maximum(np.abs(d + 7) - 7.0, np.maximum(np.abs(X) - 44, 7 - Z))
lab = np.maximum(np.maximum(-(d + 14) , d + 18), np.maximum(np.abs(X) - 30, np.maximum(-Z, Z - 12)))   # lábio da frente
terra = menos(terra, canal, 1.0)
terra = smin(terra, lab + rr * 0.3, 2)
# mão: antebraço saindo da terra atrás, palma inclinada com os dedos para cima
mao = capsula(g, (1, 2, 4), (0, 5, 34), 8.5, 6.8)
palma = elipsoide(Vista(g, (0, 7, 46), rot_x(25)), (0, 7, 46), (11.5, 4.6, 12))
mao = smin(mao, palma, 4)
unhas = None
dedos = [(-8.4, 0.92, 26), (-2.8, 1.0, 31), (2.8, 0.98, 29), (8.2, 0.88, 23)]
for (x, s, L) in dedos:
    # dedo sobe inclinado e curva levemente para a frente (por cima do celular)
    p0 = np.array([x, 6.0, 56.0])
    p1 = p0 + np.array([x * 0.08, L * 0.55 * np.tan(INC), L * 0.55])
    p2 = p1 + np.array([x * 0.04, L * 0.32 * np.tan(INC), L * 0.32])
    p3 = p2 + np.array([0, -3.0, L * 0.12])
    dd = tubo(g, [tuple(p0), tuple(p1), tuple(p2), tuple(p3)], [3.0 * s, 2.7 * s, 2.4 * s, 2.0 * s])
    for p in (p1, p2):
        dd = smin(dd, esfera(g, tuple(p), 3.2 * s), 0.8)          # nós dos dedos
    mao = smin(mao, dd, 1.6)
    un = np.maximum(esfera(g, tuple(p3 + np.array([0, -0.8, 1.0])), 2.0 * s), -(Z - p3[2]))
    unhas = un if unhas is None else np.minimum(unhas, un)
polegar = tubo(g, [(-11, 6, 44), (-17, 4, 52), (-19, 1, 58)], [3.6, 3.0, 2.4])
mao = smin(mao, polegar, 1.5)
unhas = np.minimum(unhas, esfera(g, (-19.4, -0.6, 59), 2.0))
mao = mao + ruido(g, 0.8, 42) * 0.12
# manga rasgada no pulso
manga = np.maximum(np.abs(np.sqrt((X - 1) ** 2 + ((Y - 2.5) * 0.9) ** 2) - 9.2) - 1.4, np.abs(Z - 14 - 2 * np.sin(np.arctan2(Y - 2.5, X) * 5)) - 5)
manga = np.maximum(manga, -Z + 4)
# lápide e ossos
v = Vista(g, (-30, 22, 8), mul(rot_z(15), rot_y(-10)))
lap = np.minimum(caixa(v, (-30, 22, 18), (9, 3, 10), 1.5), np.maximum(np.sqrt((v.x + 30) ** 2 + (v.z - 28) ** 2) - 9, np.abs(v.y - 22) - 3))
lap = menos(lap, np.maximum(np.maximum(np.abs(v.x + 30) - 5.5, np.abs(v.z - 24) - 0.8), -(v.y - 22 + 2.4)), 0.2)
lap = menos(lap, np.maximum(np.maximum(np.abs(v.x + 30) - 0.8, np.abs(v.z - 24) - 5.5), -(v.y - 22 + 2.4)), 0.2)
osso = np.minimum(capsula(g, (24, -6, 6), (36, -12, 7), 1.6), np.minimum.reduce([esfera(g, (24, -6, 6), 2.4), esfera(g, (36, -12, 7), 2.4)]))
claro = np.minimum(lap, osso)
tudo = np.minimum.reduce([terra, mao, manga, lap, osso, unhas])
tudo = np.maximum(tudo, -Z)
partes = dividir(tudo, {"c4": np.minimum(unhas, manga), "c3": claro, "c2": mao})
for k, v in exportar(g, partes, saida(__file__, "mao", IMP), faces=None).items():
    print(k, v)
