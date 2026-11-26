"""Mochila da Aventura – porta-lápis em forma de mochila escolar dos anos 80, aberta em cima: bolso da frente com
zíper, alças, broches (um raio, uma estrela e um d20) e uma lanterna presa na lateral.
76 × 56 × 104 mm. Cores: c1 mochila, c2 zíperes, fivelas e lanterna, c3 broches, c4 bolso e alças.
Em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.13)
MN, MX = (-42, -32, 0), (42, 32, 116)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    rr = ruido(g, 2.0, 201)
    corpo = caixa(g, (0, 4, 46), (30, 17, 46), 12) + rr * 0.25
    corpo = smin(corpo, elipsoide(g, (0, 4, 90), (30, 17, 14)), 6)                   # topo arredondado
    corpo = menos(corpo, np.maximum(caixa(g, (0, 4, 60), (26, 13, 60), 9), 14 - Z))  # aberta em cima (copo)
    corpo = np.maximum(corpo, Z - 100)
    # bolso da frente com zíper e aba
    bolso = caixa(g, (0, -14, 28), (24, 6, 20), 7) + rr * 0.2
    zip_ = np.maximum(np.abs(np.maximum(np.abs(X) - 21, np.abs(Z - 30) - 16)) - 0.8, np.abs(Y + 19.6) - 0.8)
    zip_ = np.maximum(zip_, -(Z - 30) - 8)
    puxa = caixa(g, (14, -21, 46), (1.4, 1.0, 3.2), 0.6)
    # alças nas costas e alça de mão no topo
    alcas = None
    for sx in (-1, 1):
        a = tubo(g, [(sx * 16, 21, 92), (sx * 20, 26, 60), (sx * 18, 23, 14)], [3.5, 3.0, 3.0])
        alcas = a if alcas is None else np.minimum(alcas, a)
    alca_top = np.maximum(toro(Vista(g, (0, 4, 100), rot_x(90)), (0, 4, 100), 9, 2.2), 99 - Z)
    alcas = np.minimum(alcas, alca_top)
    fivelas = np.minimum(caixa(g, (-17, 24, 40), (4, 1.6, 2.4), 0.6), caixa(g, (17, 24, 40), (4, 1.6, 2.4), 0.6))
    # broches na parte de cima da frente
    br = simb = None
    for (x, z, tipo) in [(-14, 70, 0), (0, 74, 1), (14, 70, 2)]:
        u, w = X - x, Z - z
        if tipo == 0:
            d = np.maximum(np.abs(u - w * 0.45) - 1.5, np.abs(w) - 5)
        elif tipo == 1:
            a = np.arctan2(w, u) - np.pi / 2
            rr2 = np.sqrt(u ** 2 + w ** 2)
            k = np.cos(np.pi / 5) / np.cos(np.mod(a, 2 * np.pi / 5) - np.pi / 5)
            d = rr2 - 5.2 * (0.45 + 0.55 * np.clip((k - np.cos(np.pi / 5)) / (1 - np.cos(np.pi / 5)), 0, 1) ** 2)
        else:
            a = np.arctan2(w, u); sec = np.round(a / (np.pi / 3)) * (np.pi / 3)
            d = u * np.cos(sec) + w * np.sin(sec) - 4.8
        b = np.maximum(np.sqrt(u ** 2 + w ** 2) - 6.4, np.abs(Y + 13.4) - 1.0)
        sym = np.maximum(d, np.abs(Y + 14.6) - 0.6)
        br = b if br is None else np.minimum(br, b)
        simb = sym if simb is None else np.minimum(simb, sym)
    # lanterna presa na lateral
    lant = np.minimum(capsula(g, (31, 4, 40), (31, 4, 66), 4.2), cilindro(g, (31, 4, 64), 6, 7, 1.5))
    lant = np.minimum(lant, caixa(g, (30, 4, 52), (2.4, 5.4, 1.4), 0.5))
    escuro = np.minimum.reduce([zip_, puxa, fivelas, lant, simb])
    c4 = np.minimum(bolso, alcas)
    # trama do tecido (lona) e costuras pespontadas nas bordas do bolso
    trama = 0.06 * (np.sin(X * 6.5) * np.sin(Z * 6.5))
    corpo = corpo + trama * np.clip(1 - np.abs(corpo) / 0.8, 0, 1)
    c4 = c4 + trama * np.clip(1 - np.abs(c4) / 0.8, 0, 1)
    pesp = np.maximum(np.abs(np.maximum(np.abs(X) - 21.5, np.abs(Z - 28) - 18.5)) - 0.3, np.abs(Y + 20.2) - 0.4)
    c4 = menos(c4, np.maximum(pesp, np.abs(np.mod(X + Z, 2.4) - 1.2) - 0.55), 0.05)
    tudo = np.minimum.reduce([corpo, c4, escuro, br])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c2": escuro, "c3": br, "c4": c4}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "mochila", IMP)).items():
        print(k, v)
