"""Goblin Engenhoqueiro – figura chibi (~55 mm): goblin de orelhas enormes, nariz pontudo e sorriso de dentinhos,
óculos de proteção na testa, avental de couro, uma chave inglesa gigante na mão e uma mochila de engrenagens com
chaminé soltando fumaça. Base redonda de 32 mm.
Cores: c1 pele, c2 metal (chave, engrenagens, óculos), c3 olhos, dentes e lentes, c4 avental e fumaça.
Em pé; suporte em árvore só sob a chave inglesa (a fumaça encosta na chaminé)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.12)
MN, MX = (-30, -22, 0), (36, 26, 64)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    base = cilindro(g, (0, 0, 0), 16, 3.2, 1.2)
    corpo = elipsoide(g, (0, 1, 15), (8.5, 7.5, 9))
    cab = elipsoide(g, (0, -1, 31), (10, 8.6, 8.6))
    corpo = smin(corpo, cab, 4)
    corpo = smin(corpo, capsula(g, (0, -8, 31), (0, -15, 29.5), 2.4, 0.9), 1.2)           # nariz
    for sx in (-1, 1):
        orelha = elipsoide(Vista(g, (sx * 15, 0, 33), mul(rot_z(sx * -10), rot_y(sx * -18))), (sx * 15, 0, 33), (8.5, 1.8, 4))
        corpo = smin(corpo, orelha, 2)
        corpo = menos(corpo, elipsoide(Vista(g, (sx * 15.5, -1.4, 33), rot_y(sx * -18)), (sx * 15.5, -1.4, 33), (6, 1.0, 2.4)), 0.5)
        corpo = smin(corpo, capsula(g, (sx * 4, 1, 4), (sx * 4.5, 0, 9), 2.6, 2.6), 1.5)       # pernas
        corpo = smin(corpo, elipsoide(g, (sx * 4.6, -2.5, 3.6), (3.2, 4.8, 2.4)), 1.2)         # pés
    # braços: direito segura a chave inglesa, esquerdo acena
    corpo = smin(corpo, capsula(g, (7, 0, 20), (12, -5, 13), 2.4, 2.2), 1.5)
    corpo = smin(corpo, esfera(g, (12.5, -6, 12), 2.8), 1)
    corpo = smin(corpo, capsula(g, (-7, 0, 20), (-13, -3, 27), 2.4, 2.2), 1.5)
    corpo = smin(corpo, esfera(g, (-14, -3.5, 28.5), 2.6), 1)
    # olhos grandes, sorriso com dentinhos
    claro = pup = None
    for sx in (-1, 1):
        o = esfera(g, (sx * 4.2, -7.2, 32.5), 2.8)
        p = esfera(g, (sx * 4.0, -9.4, 32.3), 1.5)
        claro = o if claro is None else np.minimum(claro, o)
        pup = p if pup is None else np.minimum(pup, p)
    boca = np.maximum(toro(Vista(g, (0, -7.8, 27), rot_x(90)), (0, -7.8, 27), 4.2, 0.9), Z - 26.4)
    corpo = menos(corpo, boca, 0.4)
    for sx in (-1, 1):
        claro = np.minimum(claro, caixa(g, (sx * 1.8, -8.6, 25.6), (0.8, 0.8, 1.0), 0.3))
    # óculos de proteção na testa (tira + 2 lentes)
    tira = np.maximum(np.abs(elipsoide(g, (0, -1, 31), (10.3, 8.9, 8.9))) - 0.6, np.abs(Z - 37.5) - 1.3)
    metal = tira
    for sx in (-1, 1):
        a = np.maximum(np.sqrt((X - sx * 3.8) ** 2 + (Z - 37.8) ** 2) - 2.9, np.abs(Y + 9.3) - 1.6)
        metal = np.minimum(metal, menos(a, np.maximum(np.sqrt((X - sx * 3.8) ** 2 + (Z - 37.8) ** 2) - 2.0, -(Y + 9.6) - 3)))
        claro = np.minimum(claro, np.maximum(np.sqrt((X - sx * 3.8) ** 2 + (Z - 37.8) ** 2) - 2.1, np.abs(Y + 9.5) - 0.8))
    # chave inglesa
    haste = capsula(g, (12.5, -6.5, 12), (25.5, -9.5, 9.5), 1.4)                     # cabo, da mão para a direita
    cabeca = np.maximum(np.sqrt((X - 29) ** 2 + (Z - 9) ** 2) - 4.8, np.abs(Y + 10) - 1.5)
    cabeca = menos(cabeca, caixa(g, (32.5, -10, 9), (3, 3, 1.7), 0.3))              # boca da chave
    metal = np.minimum.reduce([metal, haste, cabeca])
    # mochila de engrenagens com chaminé e fumaça
    moch = caixa(g, (0, 9.5, 17), (6.5, 3.5, 7), 2)
    eng = None
    for (x, z, r) in [(-3, 21, 4.0), (3.5, 14, 3.2)]:
        rr_ = np.sqrt((X - x) ** 2 + (Z - z) ** 2)
        a = np.arctan2(Z - z, X - x)
        dentes = r + 0.9 * (np.cos(a * 8) > 0.2)
        e = np.maximum(rr_ - dentes, np.abs(Y - 13.6) - 1.0)
        e = menos(e, np.maximum(rr_ - 1.2, np.abs(Y - 13.6) - 2))
        eng = e if eng is None else np.minimum(eng, e)
    chamine = np.maximum(np.sqrt((X - 4) ** 2 + (Y - 9.5) ** 2) - 1.8, np.maximum(22 - Z, Z - 33))
    fumaca = smin(smin(esfera(g, (4.5, 10, 35.5), 3.2), esfera(g, (6.5, 11, 40.5), 3.8), 1.5), esfera(g, (4, 12, 46), 4.5), 1.5)
    metal = np.minimum.reduce([metal, eng, chamine])
    # avental
    avental = np.maximum(np.abs(elipsoide(g, (0, 1, 15), (8.9, 7.9, 9.4))) - 0.6, np.maximum(Y + 0.5, np.abs(Z - 14) - 7))
    c4 = np.minimum(avental, fumaca)
    # pele enrugada com verrugas, couro do avental com costura, metal riscado
    corpo = corpo + 0.06 * ruido(g, 0.4, 111) + 0.25 * np.clip(ruido_cel(g, 1.6, 112) - 1.3, 0, None) * np.clip(1 - np.abs(corpo) / 1.0, 0, 1)
    c4 = c4 + 0.07 * ruido(g, 0.5, 113)
    metal = metal + 0.04 * ruido(g, 0.4, 114)
    base = base + desgaste(g, 0.35, 115)
    tudo = np.minimum.reduce([smin(corpo, base, 1.5), moch, claro, pup, metal, c4])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c2": np.minimum(metal, pup), "c3": claro, "c4": c4}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "goblin", IMP)).items():
        print(k, v)
