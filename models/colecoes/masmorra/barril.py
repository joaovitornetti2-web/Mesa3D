"""Barril da Taverna – porta-lápis e porta-dados em forma de barril de taverna: aduelas de madeira, três cintas
de ferro, torneirinha na frente e uma caneca de espuma transbordando grudada ao lado (também oca, para dados).
Barril de 62 mm de diâmetro e 90 mm de altura. Cores: c1 madeira, c2 cintas e torneira, c3 espuma, c4 caneca.
Em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.13)
H, R0, R1, E = 90.0, 27.0, 31.0, 2.4
MN, MX = (-36, -44, 0), (70, 36, 96)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    rr = ruido(g, 1.2, 5)
    # perfil abaulado do barril
    t = (Z - H / 2) / (H / 2)
    raio = R0 + (R1 - R0) * (1 - t ** 2)
    rad = np.sqrt(X ** 2 + Y ** 2)
    corpo = np.maximum(rad - raio, np.maximum(-Z, Z - H))
    # aduelas: sulcos verticais
    ang = np.arctan2(Y, X)
    n = 18
    fase = np.mod(ang * n / (2 * np.pi), 1.0)
    sulco = np.minimum(fase, 1 - fase) * (2 * np.pi * R1 / n) - 0.45
    corpo = menos(corpo, np.maximum(sulco, np.maximum(-(rad - raio + 0.7), np.maximum(3 - Z, Z - H + 3))), 0.2)
    perto = np.clip(1 - np.abs(corpo) / 1.5, 0, 1)
    corpo = corpo + perto * (madeira(Z, ang * R1, tabua=2 * np.pi * R1 / n, fenda=0.01, prof=0.0, veio=0.14, semente=7) + desgaste(g, 0.25, 8)) + rr * 0.05
    # marca a ferro "XXX" na lateral
    lado = np.arctan2(Y, -X) * R1                        # arco medido a partir do lado esquerdo (-x)
    corpo = menos(corpo, np.maximum(texto2d(lado, Z - 62, "XXX", 7, "serif"), np.abs(rad - raio) - 0.55), 0.1)
    # oco por dentro
    oco = np.maximum(rad - (raio - E - 0.6), 3 - Z)
    corpo = menos(corpo, oco)
    # cintas de ferro
    cintas = None
    for zc in (10, H / 2, H - 10):
        tc = (zc - H / 2) / (H / 2)
        rc = R0 + (R1 - R0) * (1 - tc ** 2)
        c = np.maximum(np.abs(rad - rc - 0.4) - 1.0, np.abs(Z - zc) - 2.4)
        c = np.maximum(c, -(rad - rc + 0.6))
        c = np.minimum(c, rebites(g, [((rc + 1.3) * np.cos(a), (rc + 1.3) * np.sin(a), zc) for a in np.linspace(0, 2 * np.pi, 13)[:-1]], 0.7))
        cintas = c if cintas is None else np.minimum(cintas, c)
    # torneira na frente (y negativo)
    torn = np.minimum(capsula(g, (0, -R1 + 1, 30), (0, -R1 - 7, 30), 2.4), capsula(g, (0, -R1 - 7, 30), (0, -R1 - 7, 24), 2.0, 1.6))
    torn = np.minimum(torn, capsula(g, (-3.5, -R1 - 5, 34), (3.5, -R1 - 5, 34), 1.2))
    torn = np.minimum(torn, capsula(g, (0, -R1 - 5, 31), (0, -R1 - 5, 34), 1.0))
    # caneca ao lado (x positivo), com alça e espuma
    cx, cy, cr, ch = 36.0, -24.0, 13.5, 46.0
    radc = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    caneca = np.maximum(radc - cr, np.maximum(-Z, Z - ch))
    caneca = smin(caneca, np.maximum(np.abs(radc - cr) - 1.0, np.abs(Z - 4) - 3) - 0.6, 0.6)
    caneca = smin(caneca, np.maximum(np.abs(radc - cr) - 1.0, np.abs(Z - ch + 4) - 2) - 0.6, 0.6)
    alca = toro(Vista(g, (cx + cr + 2, cy, ch / 2), rot_x(90)), (cx + cr + 2, cy, ch / 2), 9, 2.6)
    alca = np.maximum(alca, -(X - cx - cr + 1))
    caneca = smin(caneca, alca, 1)
    caneca = menos(caneca, np.maximum(radc - cr + E, 3 - Z))
    # espuma: anel fofo na borda + escorrido pela lateral
    esp = None
    for k in range(9):
        a = k * 2 * np.pi / 9
        b = esfera(g, (cx + (cr - 1.5) * np.cos(a), cy + (cr - 1.5) * np.sin(a), ch + 1.5 + (k % 2)), 4.6)
        esp = b if esp is None else smin(esp, b, 1.6)
    esp = smin(esp, capsula(g, (cx - 6, cy - cr + 0.8, ch), (cx - 7, cy - cr - 0.6, ch - 12), 3.2, 2.4), 1.5)
    esp = menos(esp, np.maximum(radc - cr + E + 0.5, ch - 2 - Z), 1.0)
    rng = np.random.default_rng(3)
    for k in range(26):                                   # bolhas de espuma estouradas
        a, h = rng.uniform(0, 2 * np.pi), rng.uniform(-1, 4)
        p = (cx + (cr + 0.5) * np.cos(a) * 0.8, cy + (cr + 0.5) * np.sin(a) * 0.8, ch + 3 + h)
        esp = menos(esp, esfera(g, p, rng.uniform(0.5, 1.1)), 0.2)
    cintas = cintas + 0.05 * ruido(g, 1.2, 9)
    tudo = np.minimum.reduce([corpo, cintas, torn, caneca, esp])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c3": esp, "c2": np.minimum(cintas, torn), "c4": caneca}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "barril", IMP)).items():
        print(k, v)
