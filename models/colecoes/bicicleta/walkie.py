"""Walkie-Talkie Porta-Celular – rádio comunicador dos anos 80 deitado para trás, que segura o celular: o
aparelho apoia no rebaixo da frente e encosta no corpo do rádio (cerca de 65°; capinha de até 13 mm). Antena,
grade do alto-falante, botão de falar, botões de canal e uma luzinha. 92 × 84 × 150 mm.
Cores: c1 carcaça, c2 grade, botões e antena, c3 etiqueta "CANAL 9", c4 luz e botão de falar.
Em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.3)
INC = 25.0                       # inclinação do rádio para trás (graus)
MN, MX = (-48, -50, 0), (48, 90, 150)


def campo(g):
    X, Y, Z = g.x, g.y, g.z


    def radio(g):
        """rádio em pé no próprio referencial: frente para −y, base em z = 0."""
        X, Y, Z = g.x, g.y, g.z
        corpo = caixa(g, (0, 0, 58), (24, 13, 58), 6)
        corpo = smin(corpo, caixa(g, (0, 0, 104), (20, 11, 10), 5), 2)                     # ombro mais estreito
        # grade do alto-falante (rasgos horizontais) na parte de baixo da frente
        fr = -13
        rasgos = np.maximum(np.abs(np.mod(Z - 20, 4.2) - 2.1) - 0.8, np.maximum(np.abs(X) - 16, np.maximum(np.abs(Z - 40) - 19, np.abs(Y - fr) - 1.6)))
        corpo = menos(corpo, rasgos, 0.3)
        grade = np.maximum(np.abs(np.maximum(np.abs(X) - 17.5, np.abs(Z - 40) - 20.5)) - 1.2, np.abs(Y - fr - 0.2) - 0.9)
        # etiqueta e luz
        etiq = caixa(g, (0, fr - 0.4, 78), (18, 1.0, 6), 1.5)
        letras = np.maximum(texto2d(X, Z - 78, "CANAL 9", 5.5, "mono"), np.abs(Y - fr + 1.6) - 0.5)
        luz = esfera(g, (13, fr - 0.6, 96), 2.2)
        # botões de canal no topo e botão de falar na lateral
        bot = None
        for xx in (-9, 0):
            b_ = cilindro(g, (xx, 0, 113), 3.2, 5, 1.0)
            bot = b_ if bot is None else np.minimum(bot, b_)
        falar = caixa(g, (-24.8, 0, 72), (2, 6, 14), 1.5)
        antena = smin(capsula(g, (11, 2, 112), (11, 2, 150), 2.4, 1.6), esfera(g, (11, 2, 150.5), 2.6), 1)
        antena = smin(antena, cilindro(g, (11, 2, 110), 4.2, 8, 1.2), 1)
        escuro = np.minimum.reduce([grade, bot, antena])
        tudo = np.minimum.reduce([corpo, etiq, letras, luz, escuro, falar])
        return tudo, escuro, etiq, letras, np.minimum(luz, falar)


    gv = Vista(g, (0, 20, 0), rot_x(-INC))
    tudo, escuro, etiq, letras, verm = radio(gv)
    # pé de apoio: base larga com o rebaixo do celular na frente
    base = caixa(g, (0, -8, 5), (40, 40, 5), 4)
    cel = (Y + 32) * np.cos(np.radians(INC)) - (Z - 10) * np.sin(np.radians(INC))   # plano das costas do celular
    canal = np.maximum(np.abs(cel + 7) - 7.0, np.maximum(np.abs(X) - 44, 6 - Z))
    labio = np.maximum(np.maximum(-(cel + 14), cel + 18), np.maximum(np.abs(X) - 30, np.maximum(-Z, Z - 14)))
    base = smin(base, labio, 2)
    tudo = np.minimum(tudo, base)
    tudo = menos(tudo, canal, 0.8)
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c4": verm, "c2": np.minimum(escuro, letras), "c3": etiq}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "walkie", IMP)).items():
        print(k, v)
