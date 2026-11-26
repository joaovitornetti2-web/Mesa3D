"""Boombox Porta-Trecos – rádio-gravador de dois alto-falantes dos anos 80, aberto em cima para guardar dados,
lápis e miniaturas. Alça cromada, dois cones de alto-falante, deck de fita no meio, botões e um equalizador.
128 × 50 × 92 mm. Cores: c1 carcaça, c2 alto-falantes, deck e alça, c3 cones e fita, c4 botões e luzes.
Em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.3)
LX, LY, H = 62.0, 22.0, 62.0
MN, MX = (-66, -26, 0), (66, 26, 104)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    corpo = caixa(g, (0, 0, H / 2), (LX, LY, H / 2), 7)
    corpo = menos(corpo, caixa(g, (0, 2, H / 2 + 6), (LX - 3, LY - 5, H / 2), 4))             # aberto em cima
    fr = -LY
    # alto-falantes (aro, grade e cone)
    alto = cones = None
    for sx in (-1, 1):
        cx, cz = sx * 38, 30
        rad = np.sqrt((X - cx) ** 2 + (Z - cz) ** 2)
        aro = np.maximum(np.abs(rad - 19) - 2.0, np.abs(Y - fr) - 1.4)
        fundo = np.maximum(rad - 17.5, np.abs(Y - fr - 0.4) - 0.8)
        cone = np.maximum(np.maximum(rad - 11, -(Y - fr) - 0.6 - (11 - rad) * 0.25), Y - fr - 0.4)
        cone = np.minimum(cone, np.maximum(rad - 4, np.abs(Y - fr + 2.6) - 1.0))
        a = np.minimum(aro, fundo)
        alto = a if alto is None else np.minimum(alto, a)
        cones = cone if cones is None else np.minimum(cones, cone)
    # deck de fita no meio
    deck = caixa(g, (0, fr - 0.4, 32), (15, 1.2, 12), 2)
    fita = caixa(g, (0, fr - 1.4, 32), (11, 0.8, 7), 1.2)
    for xx in (-5, 5):
        fita = menos(fita, np.maximum(np.sqrt((X - xx) ** 2 + (Z - 32) ** 2) - 2.2, np.abs(Y - fr + 1.4) - 2), 0.2)
    # botões em cima da frente e equalizador
    bot = None
    for i, xx in enumerate(np.arange(-12, 13, 6)):
        b = caixa(g, (xx, fr - 0.8, 50), (2.2, 1.6, 2.2), 0.6)
        bot = b if bot is None else np.minimum(bot, b)
    for i, xx in enumerate(np.arange(-12, 13, 4)):
        h = 2 + 3 * abs(np.sin(i * 1.7))
        bot = np.minimum(bot, caixa(g, (xx, fr - 0.6, 12 + h / 2), (1.2, 1.0, h / 2), 0.4))
    # alça cromada
    alca = toro(Vista(g, (0, 0, H - 10), rot_x(90)), (0, 0, H - 10), 44, 3.0, 1.0)
    alca = np.maximum(alca, -(Z - H + 1))
    alca = smin(alca, np.minimum(caixa(g, (-42, 0, H), (5, 5, 3), 1.5), caixa(g, (42, 0, H), (5, 5, 3), 1.5)), 1.5)
    alca = menos(alca, caixa(g, (0, 2, H / 2 + 6), (LX - 3, LY - 5, H / 2), 4))
    escuro = np.minimum.reduce([alto, deck, alca])
    tudo = np.minimum.reduce([corpo, escuro, cones, fita, bot])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c4": bot, "c3": np.minimum(cones, fita), "c2": escuro}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "boombox", IMP)).items():
        print(k, v)
