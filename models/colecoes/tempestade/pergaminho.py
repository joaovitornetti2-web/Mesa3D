"""Pergaminho do Aventureiro – porta-lápis e porta-fichas deitado: um pergaminho enrolado com as pontas abertas
em espiral, amarrado por uma fita com selo de cera; em cima, uma canaleta para lápis e borracha e uma fenda para
fichas de personagem dobradas (até 6 mm). 140 × 48 × 42 mm.
Cores: c1 papel, c2 tinta (mapa/letras na lateral), c3 fita, c4 selo de cera. Deitado, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.3)
L, R = 64.0, 19.0
MN, MX = (-72, -26, 0), (72, 26, 46)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    rr = ruido(g, 2.5, 131)
    rad = np.sqrt(Y ** 2 + (Z - R) ** 2)
    ang = np.arctan2(Z - R, Y)
    # rolo com leve abaulado e as pontas em espiral (sulcos de espiral nas faces)
    corpo = np.maximum(rad - R - 0.6 * np.cos(X / L * np.pi / 2), np.abs(X) - L) + rr * 0.15
    esp = np.mod(rad - ang / (2 * np.pi) * 2.4, 2.4)
    espiral = np.maximum(np.minimum(esp, 2.4 - esp) - 0.35, np.abs(np.abs(X) - L) - 1.2)
    corpo = menos(corpo, np.maximum(espiral, rad - R + 1.5), 0.2)
    # folha solta desenrolando na frente (aba curva)
    aba = np.maximum(np.abs(np.sqrt((Y + 4) ** 2 + (Z - R + 2) ** 2) - R - 2.5) - 0.8, np.maximum(np.abs(X) - L + 6, np.maximum(Z - R + 6, -Y - R - 10)))
    aba = np.maximum(aba, -Z)
    corpo = smin(corpo, aba, 1.0)
    corpo = np.maximum(corpo, -Z)
    # canaleta dos lápis e fenda das fichas
    corpo = menos(corpo, capsula(g, (-L + 8, -6, 2 * R + 3), (L - 8, -6, 2 * R + 3), 6.0), 1.0)
    corpo = menos(corpo, caixa(g, (0, 8, 2 * R), (L - 10, 3.0, 14), 1.0), 0.6)
    # fita amarrada com laço e selo de cera
    fita = np.maximum(np.abs(rad - R - 0.8) - 0.8, np.abs(X - 22) - 4)
    laco = None
    for s in (-1, 1):
        lc = toro(Vista(g, (22 + s * 5, -R - 1.5, R - 2), mul(rot_x(90), rot_y(s * 30))), (22 + s * 5, -R - 1.5, R - 2), 4.0, 1.2)
        laco = lc if laco is None else np.minimum(laco, lc)
    pontas = np.minimum(capsula(g, (22, -R - 1.5, R - 5), (19, -R - 2, R - 14), 1.3), capsula(g, (22, -R - 1.5, R - 5), (26, -R - 2, R - 13), 1.3))
    fita = np.minimum.reduce([fita, laco, pontas])
    selo = np.maximum(np.sqrt((X - 22) ** 2 + (Z - R + 1) ** 2) - 5.2 - 0.5 * np.sin(np.arctan2(Z - R + 1, X - 22) * 7), np.abs(Y + R + 3.2) - 1.6)
    selo = menos(selo, np.maximum(np.abs(np.sqrt((X - 22) ** 2 + (Z - R + 1) ** 2) - 2.6) - 0.5, -(Y + R + 4.0)), 0.2)
    # tinta: rosa dos ventos e linhas de texto na lateral da frente (relevo baixo)
    u, v = X + 30, Z - R
    rosa = np.minimum(np.abs(u) * 3 + np.abs(v) - 9, np.abs(u) + np.abs(v) * 3 - 9)
    rosa = np.minimum(rosa, np.abs(np.sqrt(u ** 2 + v ** 2) - 6) - 0.4)
    linhas = np.maximum(np.abs(np.mod(Z - R + 1, 3.6) - 1.8) - 0.4, np.maximum(np.abs(X - 2) - 10, np.abs(Z - R) - 7))
    tinta = np.maximum(np.minimum(rosa, linhas), np.abs(rad - R - 0.4) - 0.5)
    tinta = np.maximum(tinta, Y + 4)
    tudo = np.minimum.reduce([corpo, fita, selo, tinta])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c4": selo, "c3": fita, "c2": tinta}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "pergaminho", IMP)).items():
        print(k, v)
