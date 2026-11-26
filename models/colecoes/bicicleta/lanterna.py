"""Lanterna da Investigação – porta-lápis em forma de lanterna de mão antiga, em pé com a cabeça para cima:
corpo com anéis de borracha, botão deslizante, alça de pulso e a cabeça larga com vidro e refletor; a boca da
lanterna é o copo dos lápis. Ø 64 × 118 mm.
Cores: c1 corpo, c2 anéis, botão e alça, c3 vidro/refletor, c4 faixa refletiva. Em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.13)
MN, MX = (-36, -36, 0), (36, 36, 122)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    rad = np.sqrt(X ** 2 + Y ** 2)
    ang = np.arctan2(Y, X)
    # perfil: base, cabo, gargalo cônico, cabeça
    r_perfil = np.where(Z < 6, 22, np.where(Z < 74, 19.5, np.where(Z < 90, 19.5 + (Z - 74) * 0.7, 30.6)))
    corpo = np.maximum(rad - r_perfil, np.maximum(-Z, Z - 118))
    corpo = smax(corpo, Z - 118, 2.0)
    corpo = menos(corpo, np.maximum(rad - 16.5, 10 - Z))                       # copo dos lápis
    # anéis de borracha (grip) no cabo
    aneis = None
    for zz in (16, 26, 36, 46, 56):
        a = np.maximum(np.abs(rad - 20.2) - 1.4, np.abs(Z - zz) - 2.4)
        aneis = a if aneis is None else np.minimum(aneis, a)
    # botão deslizante e trilho
    botao = np.maximum(caixa(g, (0, -20.6, 66), (4, 1.6, 5), 1.5), -(rad - 18))
    trilho = np.maximum(np.maximum(np.abs(X) - 2.2, np.abs(Z - 66) - 9), np.abs(rad - 19.5) - 0.8)
    corpo = menos(corpo, trilho, 0.3)
    # alça de pulso
    alca = toro(Vista(g, (20.5, 0, 12), rot_y(90)), (20.5, 0, 12), 6.5, 1.8)
    alca = np.maximum(alca, -(X - 20))
    # vidro (anel na boca) e refletor por dentro
    vidro = np.maximum(np.abs(rad - 23) - 7.4, np.abs(Z - 117) - 1.2)
    vidro = np.maximum(vidro, -(rad - 16.6))
    refletor = np.maximum(np.abs(rad - 17.4) - 0.9, np.abs(Z - 108) - 9)
    # faixa refletiva na cabeça
    faixa = np.maximum(np.abs(rad - 30.6 - 0.2) - 0.8, np.abs(Z - 100) - 3)
    escuro = np.minimum.reduce([aneis, botao, alca])
    claro = np.minimum(vidro, refletor)
    escuro = escuro + 0.15 * (np.abs(np.mod(np.arctan2(Y, X) * 48 / (2 * np.pi), 1) - 0.5) < 0.25) * np.clip(1 - np.abs(escuro) / 0.6, 0, 1)   # borracha estriada
    corpo = corpo + 0.03 * ruido(g, 0.3, 230)
    tudo = np.minimum.reduce([corpo, escuro, claro, faixa])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c3": claro, "c2": escuro, "c4": faixa}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "lanterna", IMP)).items():
        print(k, v)
