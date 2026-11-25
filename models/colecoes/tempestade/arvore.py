"""Árvore dos Sussurros – porta-joias e decoração: árvore retorcida e sem folhas, com um rosto sonolento entalhado
no tronco, galhos para pendurar anéis, colares e chaveiros, raízes num prato de musgo e um corvinho num galho.
Ø 100 × 118 mm. Cores: c1 tronco, c2 olhos/boca e corvo, c3 cogumelos, c4 musgo do prato.
Em pé, suporte em árvore só sob as pontas dos galhos mais abertos."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.3)
g = Grade((-56, -56, 0), (56, 56, 122), passo)
X, Y, Z = g.x, g.y, g.z
rr = ruido(g, 1.4, 141)
rad = np.sqrt(X ** 2 + Y ** 2)
ang = np.arctan2(Y, X)
# prato com musgo
prato = np.maximum(rad - 48 - 1.5 * np.sin(ang * 7), np.maximum(-Z, Z - 5)) + rr * 0.3
musgo = np.maximum(elipsoide(g, (0, 0, 4), (44, 44, 4)) + ruido(g, 2.0, 142) * 1.2, -Z + 4)
# tronco retorcido: raio diminui e o eixo gira
tw = ang - Z * 0.035
r_tronco = 13 - Z * 0.07 + 1.6 * np.sin(tw * 5)
cx_, cy_ = 3 * np.sin(Z * 0.04), 2 * np.cos(Z * 0.05)
tronco = np.maximum(np.sqrt((X - cx_) ** 2 + (Y - cy_) ** 2) - r_tronco, np.maximum(-Z, Z - 78)) + rr * 0.25
# raízes
for k in range(6):
    a = k * np.pi / 3 + 0.3
    tronco = smin(tronco, tubo(g, [(8 * np.cos(a), 8 * np.sin(a), 14), (20 * np.cos(a + 0.2), 20 * np.sin(a + 0.2), 6), (33 * np.cos(a + 0.3), 33 * np.sin(a + 0.3), 4)], [5, 3.2, 1.2]), 3)
# galhos (com pontas erguidas para segurar anéis)
gal = [((0, 0, 70), (24, -6, 86), (40, -2, 92), (44, 0, 98)), ((0, 0, 74), (-22, 8, 92), (-38, 6, 100), (-42, 4, 106)),
       ((0, 0, 60), (16, 22, 72), (24, 36, 78), (26, 40, 84)), ((0, 0, 64), (-14, -24, 78), (-20, -38, 84), (-21, -42, 90)),
       ((0, 0, 76), (4, 6, 98), (2, 10, 112), (-1, 12, 117))]
for p in gal:
    tronco = smin(tronco, tubo(g, list(p), [6.5, 3.6, 2.2, 1.4]), 3)
    # galhinho lateral
    m = np.array(p[2])
    tronco = smin(tronco, tubo(g, [tuple(m), tuple(m + np.array([0, 0, 9]) + np.array([4, 4, 0]) * np.sign(m[0] + 0.1))], [1.8, 1.0]), 1)
# rosto no tronco (frente, −y): olhos fechados (arcos), boca em O
face = None
for sx in (-1, 1):
    o = np.maximum(np.abs(np.sqrt((X - sx * 5) ** 2 + (Z - 46) ** 2) - 3.2) - 0.7, Z - 46)
    face = o if face is None else np.minimum(face, o)
boca = np.sqrt(X ** 2 + (Z - 37) ** 2 * 1.3) - 2.8
prof = Y + np.sqrt(np.maximum(r_tronco ** 2 - X ** 2, 0)) - cy_
tronco = menos(tronco, np.maximum(np.minimum(face, boca), np.abs(prof) - 2.4), 0.3)
escuro = np.maximum(np.minimum(face, boca) - 0.4, np.abs(prof + 1.6) - 1.2)
# corvinho no galho direito
cv = (40, -2, 95.5)
corvo = smin(elipsoide(g, cv, (4.5, 3, 3.2)), esfera(g, (cv[0] - 3.6, cv[1] - 0.5, cv[2] + 3.2), 2.6), 1.2)
corvo = smin(corvo, capsula(g, (cv[0] - 6, cv[1] - 0.6, cv[2] + 3.4), (cv[0] - 8.8, cv[1] - 0.6, cv[2] + 2.8), 0.9, 0.3), 0.4)
corvo = smin(corvo, capsula(g, (cv[0] + 3, cv[1], cv[2]), (cv[0] + 7.5, cv[1], cv[2] + 2), 1.6, 0.6), 0.6)
olho_c = esfera(g, (cv[0] - 4.6, cv[1] - 2.4, cv[2] + 3.8), 0.8)
corvo = menos(corvo, olho_c)
escuro = np.minimum(escuro, corvo)
# cogumelos nas raízes
cog = None
for (x, y, h) in [(18, -16, 7), (-20, -12, 9), (6, 26, 6)]:
    c = smin(capsula(g, (x, y, 4), (x, y, 4 + h), 1.6), np.maximum(elipsoide(g, (x, y, 4 + h), (4.2, 4.2, 2.8)), 4 + h - 0.4 - Z), 0.8)
    cog = c if cog is None else np.minimum(cog, c)
tudo = np.minimum.reduce([prato, musgo, tronco, corvo, cog])
tudo = np.maximum(tudo, -Z)
partes = dividir(tudo, {"c3": cog, "c2": escuro, "c4": musgo})
for k, vv in exportar(g, partes, saida(__file__, "arvore", IMP), faces=None).items():
    print(k, vv)
