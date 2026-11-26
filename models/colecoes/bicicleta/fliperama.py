"""Torre Fliperama – torre de dados em forma de máquina de fliperama dos anos 80: o dado entra pela boca do letreiro
no topo, desce por três rampas dentro do gabinete e sai pela portinhola da ficha, caindo na bandeja embutida na
frente. Tela com uma caveirinha pixelada, painel com manche e botões, entrada de ficha e adesivos laterais em raio.
Uma peça só: 96 × 150 × 166 mm. Dado máximo: d20 de 26 mm.
Cores: c1 gabinete, c2 tela, painel e moldura, c3 pixels e letreiro, c4 botões, manche e raio. Em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.45)
LX, LY = 34.0, 32.0             # meia largura e meia profundidade do gabinete
MN, MX = (-48, -104, 0), (48, 40, 170)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    # perfil lateral do gabinete (y, z): costas retas, frente com recorte do painel e da tela inclinada
    def perfil(y, z):
        fora = np.maximum(y - LY, np.maximum(-z, z - 160))
        frente = np.where(z < 70, -y - LY, np.where(z < 84, -y - LY + (z - 70) * 0.9, np.where(z < 132, -y - LY + 12.6 + (z - 84) * 0.12, -y - LY + 5)))
        return np.maximum(fora, frente)
    gab = np.maximum(perfil(Y, Z), np.abs(X) - LX)
    gab = smax(gab, np.abs(X) - LX, 2.0)
    # canal interno e rampas
    AI = 26.0
    canal = np.maximum(np.maximum(np.abs(X) - AI, np.abs(Y - 6) - 20), -1 - Z)
    canal = np.maximum(canal, Z - 150)
    gab = menos(gab, canal)
    for (z0, s) in [(128, 1), (100, -1), (72, 1)]:
        plano = np.abs((Z - z0) - 1.19 * s * (Y - 6)) - 1.6
        gab = np.minimum(gab, np.maximum(plano, np.maximum(np.maximum(np.abs(X) - AI - 0.5, np.abs(Y - 6) - 20.5), -s * (Y - 6) - 9)))
    gab = np.minimum(gab, np.maximum((Z - 2) - 0.55 * (Y - 6 + 20), np.maximum(np.maximum(np.abs(X) - AI - 0.5, np.abs(Y - 6) - 20.5), -Z)))
    # boca no topo (letreiro) e portinhola da ficha embaixo
    gab = menos(gab, np.maximum(np.maximum(np.abs(X) - 20, np.abs(Y - 6) - 14), 148 - Z))
    porta = np.maximum(np.maximum(np.abs(X) - 20, np.abs(Z - 18) - 16), Y + 10)
    gab = menos(gab, porta)
    # tela (inclinada) com mostro pixelado
    zt = 108.0
    tela = np.maximum(np.maximum(np.abs(X) - 24, np.abs(Z - zt) - 20), np.abs(-Y - LY + 12.6 + (Z - 84) * 0.12 + 0.6) - 1.0)
    mold = np.maximum(np.maximum(np.maximum(np.abs(X) - 27, np.abs(Z - zt) - 23), -np.maximum(np.abs(X) - 24, np.abs(Z - zt) - 20)),
                      np.abs(-Y - LY + 12.6 + (Z - 84) * 0.12) - 1.2)
    px, pz = np.floor((X + 14) / 3.2), np.floor((zt + 12 - Z) / 3.2)
    mostro = ["...XXXXX...", "..XXXXXXX..", ".XXXXXXXXX.", ".XX..X..XX.", ".XX..X..XX.", ".XXXX.XXXX.", "..XXXXXXX..", "..X.X.X.X.."]   # caveirinha original
    mask = np.zeros(np.broadcast(px, pz).shape, bool)
    for r, linha in enumerate(mostro):
        for c, ch in enumerate(linha):
            if ch == "X":
                mask |= (px == c - 2) & (pz == r)
    pix = np.where(mask, -1.0, 1.0).astype(np.float32)
    pix = np.maximum(pix, np.abs(-Y - LY + 12.6 + (Z - 84) * 0.12 - 0.8) - 0.6)   # salientes à frente da tela (E > 0 é fora)
    pix = np.maximum(pix, np.maximum(np.abs(X) - 22, np.abs(Z - zt) - 18))
    # letreiro com texto
    letreiro = np.maximum(np.maximum(np.abs(X) - 30, np.abs(Z - 146) - 9), np.abs(Y + LY - 5 - 0.6) - 1.0)
    txt = np.maximum(texto2d(X, Z - 146, "ARCADE", 8, "redonda"), np.abs(Y + LY - 5 - 0.6 + 1.0) - 0.5)
    # painel com manche e botões
    pz0 = 77.0
    manche = smin(capsula(g, (-14, -LY - 6, pz0), (-14, -LY - 8, pz0 + 9), 1.4), esfera(g, (-14, -LY - 8, pz0 + 10.5), 3.2), 0.5)
    botoes = None
    for (bx, bz) in [(4, 0), (12, 1.5), (20, 3)]:
        b = np.maximum(np.sqrt((X - bx) ** 2 + (Y + LY + 6) ** 2) - 3.2, np.abs(Z - pz0 - 1.5) - 1.8)
        botoes = b if botoes is None else np.minimum(botoes, b)
    ficha = caixa(g, (0, -LY - 0.6, 52), (8, 1.4, 6), 1.5)
    gab = menos(gab, caixa(g, (0, -LY - 1.5, 52), (1.0, 2.0, 3.6), 0.4))
    # raio adesivo nas laterais
    raio = None
    for sx in (-1, 1):
        pts = [(28, 140), (8, 112), (16, 108), (-6, 80), (2, 76), (-16, 46)]
        for i in range(len(pts) - 1):
            (y0, z0_), (y1, z1) = pts[i], pts[i + 1]
            dy, dz = y1 - y0, z1 - z0_
            h = np.clip(((Y - y0) * dy + (Z - z0_) * dz) / (dy * dy + dz * dz), 0, 1)
            seg = np.sqrt((Y - y0 - dy * h) ** 2 + (Z - z0_ - dz * h) ** 2) - 3.0 * (1 - 0.5 * (i + h) / 5)
            seg = np.maximum(seg, np.abs(X - sx * (LX + 0.3)) - 0.7)
            raio = seg if raio is None else np.minimum(raio, seg)
    # bandeja embutida na frente
    band = np.maximum(caixa(g, (0, -68, 7), (44, 34, 7), 6), -Z)
    band = menos(band, caixa(g, (0, -68, 10), (39, 29, 8), 4))
    band = menos(band, np.maximum(porta, np.maximum(Y + 40, -Y - 24)))
    gab = np.minimum(gab, band)
    escuro = np.minimum.reduce([tela, mold, ficha])
    claro = np.minimum(pix, letreiro)
    c4 = np.minimum.reduce([manche, botoes, raio])
    tudo = np.minimum.reduce([gab, escuro, claro, txt, c4])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c4": c4, "c3": menos(claro, txt), "c2": np.minimum(escuro, txt)}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "fliperama", IMP)).items():
        print(k, v)
