"""Placa do Clube – plaquinha de porta feita de tábuas pregadas, pintada à mão: "CLUBE SECRETO" e, embaixo,
"PROIBIDO ADULTOS", com um raio e pregos nos cantos. Dois furos para pendurar. 164 × 84 × 7 mm.
Cores: c1 tábuas, c2 letras, c3 pregos, c4 raio e faixa. Deitada, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.2)
MN, MX = (-84, -44, 0), (84, 44, 9)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    rr = ruido(g, 1.5, 191)
    tabuas = None
    for (y0, h, rot) in [(22, 19, 1.5), (0, 19, -1.0), (-22, 19, 0.8)]:
        v = Vista(g, (0, y0, 0), rot_z(rot))
        t = caixa(v, (0, y0, 2.6), (80 - abs(rot) * 2, h / 2, 2.6), 1.2) + rr * 0.15
        veio = 0.15 * np.sin(v.x * 0.7 + np.sin(v.y * 0.9) * 3)
        t = t + veio
        tabuas = t if tabuas is None else np.minimum(tabuas, t)
    # ripa vertical de trás segurando as tábuas
    tabuas = np.minimum(tabuas, caixa(g, (-60, 0, 1.3), (6, 36, 1.3), 1))
    tabuas = np.minimum(tabuas, caixa(g, (60, 0, 1.3), (6, 36, 1.3), 1))
    topo = 5.2
    letras = np.minimum(texto2d(X + 4, Y - 22, "CLUBE SECRETO", 9.5, "sans"), texto2d(X + 4, Y + 22, "PROIBIDO ADULTOS", 8, "sans"))
    letras = np.maximum(letras, np.maximum(topo - 0.4 - Z, Z - topo - 0.8))
    # raio e faixa vermelha
    pts = [(-72, 8), (-63, 1), (-69, -1), (-60, -8)]
    raio = None
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        dx, dy = x1 - x0, y1 - y0
        h = np.clip(((X - x0) * dx + (Y - y0) * dy) / (dx * dx + dy * dy), 0, 1)
        s = np.sqrt((X - x0 - dx * h) ** 2 + (Y - y0 - dy * h) ** 2) - 2.6 * (1 - 0.4 * (i + h) / 3)
        raio = s if raio is None else np.minimum(raio, s)
    faixa = np.maximum(np.abs(Y) - 1.6, np.abs(X + 2) - 52)
    c4 = np.maximum(np.minimum(raio, faixa), np.maximum(topo - 0.4 - Z, Z - topo - 0.6))
    # pregos
    pregos = None
    for x in (-60, 60):
        for y in (22, 0, -22):
            p = smin(cilindro(g, (x, y, topo - 0.5), 2.0, 1.4, 0.6), esfera(g, (x, y, topo + 0.6), 1.0), 0.4)
            pregos = p if pregos is None else np.minimum(pregos, p)
    # furos para pendurar
    for x in (-70, 70):
        tabuas = menos(tabuas, np.sqrt((X - x) ** 2 + (Y - 22) ** 2) - 2.2)
    tudo = np.minimum.reduce([tabuas, letras, c4, pregos])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c3": pregos, "c2": letras, "c4": c4}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "placa_clube", IMP)).items():
        print(k, v)
