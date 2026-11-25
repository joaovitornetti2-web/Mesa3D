"""Moedas do Reino – fichas de moeda para a mesa em três valores: coroa (Ø 32 mm, valor 10), espada (Ø 27 mm,
valor 5) e torre (Ø 22 mm, valor 1). Borda serrilhada, símbolo de um lado e o número do outro, em relevo.
Conjunto de 30 (10 de cada). Cores: c1 moeda, c2 símbolo e número (últimas camadas).
Foto: três pilhas e uma moeda de cada na frente. Impressão (--imprimir): uma moeda de cada, deitadas (duplique no fatiador)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.15)
ESP = 3.2


def simbolo(u, v, tipo, r):
    s = r / 16.0
    u, v = u / s, v / s
    if tipo == "coroa":
        faixa = np.maximum(np.abs(u) - 9, np.abs(v + 5) - 2.2)
        pontas = np.maximum(np.abs(u) - 9, np.maximum(-(v + 3), v - 7 + 1.6 * np.abs(np.mod(u + 6, 6) - 3)))
        bolas = None
        for x in (-9, -3, 3, 9):
            b = np.sqrt((u - x) ** 2 + (v - 7.6) ** 2) - 1.6
            bolas = b if bolas is None else np.minimum(bolas, b)
        d = np.minimum.reduce([faixa, pontas, bolas])
    elif tipo == "espada":
        lam = np.maximum(np.abs(u) - 1.5 * np.clip((11 - v) / 3, 0, 1), np.maximum(v - 11, -v - 3))
        guarda = np.maximum(np.abs(u) - 6, np.abs(v + 4) - 1.1)
        cabo = np.maximum(np.abs(u) - 1.1, np.abs(v + 7.5) - 2.6)
        pomo = np.sqrt(u ** 2 + (v + 11) ** 2) - 1.7
        d = np.minimum.reduce([lam, guarda, cabo, pomo])
    else:
        corpo = np.maximum(np.abs(u) - 4.5, np.abs(v + 1) - 8)
        topo = np.maximum(np.abs(u) - 6.5, np.abs(v - 7) - 2)
        ame = np.maximum(np.maximum(np.abs(u) - 6.5, np.abs(v - 10) - 1.6), 0.9 - np.abs(np.mod(u + 6.5, 4.33) - 2.165))
        porta = np.minimum(np.maximum(np.abs(u) - 2, np.abs(v + 6) - 3), np.sqrt(u ** 2 + (v + 3) ** 2) - 2)
        d = menos(np.minimum.reduce([corpo, topo, ame]), porta)
    return d * s


def moeda(g, c, r, tipo, valor, rot=None):
    gv = Vista(g, c, rot) if rot is not None else g
    x, y, z = gv.x - c[0], gv.y - c[1], gv.z - c[2]
    rad = np.sqrt(x ** 2 + y ** 2)
    ang = np.arctan2(y, x)
    serr = 0.35 * (np.cos(ang * round(r * 3)) > 0)
    corpo = np.maximum(rad - r + serr, np.abs(z - ESP / 2) - ESP / 2)
    corpo = smax(corpo, np.abs(z - ESP / 2) - ESP / 2, 0.5)
    for zz in (ESP, 0.0):                                          # rebaixo das faces deixando uma borda
        corpo = menos(corpo, np.maximum(rad - r + 2.2, np.abs(z - zz) - 0.6), 0.3)
    frente = np.maximum(simbolo(x, y, tipo, r), np.maximum(ESP - 0.6 - z, z - ESP))
    verso = np.maximum(texto2d(-x, y, valor, r * 0.75, "serif"), np.maximum(z - 0.6, -z))
    relevo = np.minimum(frente, verso)
    return np.minimum(corpo, relevo), relevo


TIPOS = [("coroa", 16.0, "10"), ("espada", 13.5, "5"), ("torre", 11.0, "1")]
tudo = relevo = None
if IMP:
    g = Grade((-18, -18, 0), (78, 18, ESP + 0.4), passo)
    for i, (t, r, v) in enumerate(TIPOS):
        a, b = moeda(g, (i * 34, 0, 0), r, t, v)
        tudo = a if tudo is None else np.minimum(tudo, a)
        relevo = b if relevo is None else np.minimum(relevo, b)
else:
    g = Grade((-46, -30, 0), (46, 30, 22), 0.2 if passo < 0.2 else passo)
    for i, (t, r, v) in enumerate(TIPOS):
        cx = -26 + i * 26
        for k in range(6 - i * 2):                               # pilhas
            ox, oy = 0.6 * np.sin(k * 2.3), 0.6 * np.cos(k * 1.7)
            a, b = moeda(g, (cx + ox, 10 + oy, k * ESP), r, t, v)
            tudo = a if tudo is None else np.minimum(tudo, a)
            relevo = b if relevo is None else np.minimum(relevo, b)
        a, b = moeda(g, ((-29, 2, 30)[i], -16, 0), r, t, v, rot_z(15 * i))  # moeda deitada na frente
        tudo = np.minimum(tudo, a)
        relevo = np.minimum(relevo, b)
tudo = np.maximum(tudo, -g.z)
partes = dividir(tudo, {"c2": relevo})
for k, vv in exportar(g, partes, saida(__file__, "moedas", IMP), faces=None).items():
    print(k, vv)
