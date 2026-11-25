"""Bandeja de Dados Escudo – bandeja em forma de escudo de cavaleiro (heráldico), com borda de metal rebitada,
fundo de tábuas e um brasão em relevo baixo no centro: duas espadas cruzadas atrás de um d20.
136 × 154 × 14 mm. Cores: c1 escudo, c2 borda de metal, c3 rebites, c4 brasão (só nas últimas camadas).
Deitada, sem suporte. Dica: cole feltro no fundo para o dado rolar sem barulho."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.3)
W, H1, HT, EF = 68.0, 60.0, 14.0, 2.4
R = 1.45 * W
g = Grade((-72, -98, 0), (72, 64, 18), passo)
X, Y, Z = g.x, g.y, g.z


def escudo(off=0.0):
    return np.maximum(Y - H1 + off, np.sqrt((np.abs(X) + R - W) ** 2 + np.minimum(Y, 0) ** 2) - R + off)


fora = escudo(0)
corpo = np.maximum(fora, np.maximum(-Z, Z - HT))
corpo = smax(corpo, Z - HT + 0.0, 1.0)
dentro = escudo(7.0)
corpo = menos(corpo, np.maximum(dentro, EF - Z), 1.2)
# tábuas no fundo
m = np.mod(X + 4, 17)
tab = np.minimum(m, 17 - m) - 0.45
corpo = menos(corpo, np.maximum(tab, np.maximum(dentro + 0.6, np.abs(Z - EF - 0.25) - 0.75)), 0.2)
# borda de metal (topo e faces da borda)
borda = np.maximum(np.maximum(fora - 0.6, -(dentro - 0.6)), np.maximum(HT - 3.5 - Z, Z - HT - 0.6))
metal = borda
# rebites na borda
reb = None
pts = []
for ang in np.linspace(-np.pi, np.pi, 40, endpoint=False):
    # busca radial do ponto no meio da borda
    for rr_ in np.linspace(20, 110, 400):
        x, y = rr_ * np.cos(ang), rr_ * np.sin(ang) + 0
        d = max(y - H1, np.sqrt((abs(x) + R - W) ** 2 + min(y, 0) ** 2) - R)
        if d > -3.5:
            pts.append((x, y))
            break
for (x, y) in pts:
    r_ = esfera(g, (x, y, HT + 0.2), 1.5)
    reb = r_ if reb is None else np.minimum(reb, r_)
# brasão no fundo: espadas cruzadas + d20 (relevo 1 mm)
cz = EF
br = None
for s in (-1, 1):
    v = Vista(g, (0, -8, cz), rot_z(s * 38))
    guarda = np.maximum(np.abs(v.x) - 9, np.abs(v.y + 8 + 26) - 1.6)
    cabo = np.maximum(np.abs(v.x) - 1.8, np.abs(v.y + 8 + 32) - 5)
    pomo = np.sqrt(v.x ** 2 + (v.y + 8 + 38.5) ** 2) - 3
    esp = np.minimum.reduce([np.maximum(np.abs(v.x) - 2.4, np.abs(v.y + 8) - 26), guarda, cabo, pomo])
    ponta = np.maximum(np.abs(v.x) - 2.6 * np.clip((v.y + 8 - 32) / -6, 0, 1), np.maximum(v.y + 8 - 32, 26 - (v.y + 8)))
    esp = np.minimum(esp, ponta)
    esp = np.maximum(esp, np.abs(v.z - cz - 0.5) - 0.5)
    br = esp if br is None else np.minimum(br, esp)
# d20 em silhueta hexagonal com triângulo
ang6 = np.arctan2(Y + 8, X)
sec = np.round(ang6 / (np.pi / 3)) * (np.pi / 3)
hexa = (X * np.cos(sec) + (Y + 8) * np.sin(sec)) - 13
dd = np.maximum(hexa, np.abs(Z - cz - 0.6) - 0.6)
tri = np.maximum(-(Y + 8) - 4.0, (Y + 8) * 0.5 + np.abs(X) * 0.866 - 5.0)
dd = menos(dd, np.maximum(np.maximum(-tri - 1.0, tri), np.abs(Z - cz - 1.2) - 0.7), 0)
br = np.minimum(menos(br, np.maximum(hexa - 1.2, np.abs(Z - cz) - 3)), dd)
tudo = np.minimum.reduce([corpo, metal, reb, br])
tudo = np.maximum(tudo, -Z)
partes = dividir(tudo, {"c3": reb, "c2": metal, "c4": br})
for k, v in exportar(g, partes, saida(__file__, "bandeja_escudo", IMP), faces=None).items():
    print(k, v)
