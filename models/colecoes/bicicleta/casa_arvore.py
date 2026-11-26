"""Casa na Árvore – decoração e porta-dados: a sede secreta da turma, uma casinha de tábuas num tronco grosso,
com telhado torto, janela redonda, plaquinha "NÃO ENTRE", escada de cordas pendurada e uma bicicleta encostada
no tronco. O telhado sai (encaixe com tampão) e a casinha guarda dados. Ø 110 × 140 mm.
Cores: c1 tronco e galhos, c2 casa (tábuas), c3 telhado, c4 placa, escada e bicicletinha.
Impressão (--imprimir): árvore com a casa em pé e o telhado ao lado; suporte em árvore só sob o piso da casa."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.18)
ZC, LX, LY, HC = 62.0, 26.0, 22.0, 34.0      # piso da casa, meia largura, meia profundidade, altura das paredes
ZT = ZC + HC                                  # onde o telhado assenta
F = 0.25
MN, MX = (-58, -58, 0), (58 + (110 if IMP else 0), 58, 144)


def campo(g):


    def arvore_casa(g):
        X, Y, Z = g.x, g.y, g.z
        rr = ruido(g, 1.6, 211)
        rad = np.sqrt(X ** 2 + Y ** 2)
        ang = np.arctan2(Y, X)
        tronco = np.maximum(rad - (13 - Z * 0.03) - 1.2 * np.sin(ang * 6 + Z * 0.05), np.maximum(-Z, Z - ZC - 4)) + rr * 0.3
        for k in range(5):
            a = k * 2 * np.pi / 5 + 0.4
            tronco = smin(tronco, tubo(g, [(8 * np.cos(a), 8 * np.sin(a), 12), (20 * np.cos(a + 0.2), 20 * np.sin(a + 0.2), 4), (30 * np.cos(a + 0.3), 30 * np.sin(a + 0.3), 2)], [5, 3, 1.2]), 3)
        # galhos sustentando o piso
        for a in (0.6, 2.5, 4.3):
            tronco = smin(tronco, tubo(g, [(0, 0, ZC - 18), (18 * np.cos(a), 18 * np.sin(a), ZC - 4), (24 * np.cos(a), 24 * np.sin(a), ZC - 1)], [4.5, 3, 2]), 2)
        tronco = tronco + np.clip(1 - np.abs(tronco) / 1.5, 0, 1) * (0.35 * np.abs(np.sin(ang * 16 + Z * 0.06 + ruido(g, 2, 231))) + desgaste(g, 0.2, 232))   # casca
        base = np.maximum(rad - 40 - 2 * np.sin(ang * 5), np.maximum(-Z, Z - 3)) + rr * 0.3
        tronco = smin(tronco, base, 2)
        # casa: piso, paredes de tábuas, janela redonda, porta
        casa = caixa(g, (0, 0, ZC + HC / 2), (LX, LY, HC / 2), 1.5) + rr * 0.15
        casa = smin(casa, caixa(g, (0, 0, ZC + 1.5), (LX + 4, LY + 4, 1.5), 1), 0.6)          # piso com beiral
        tab = np.minimum(np.mod(Z - ZC, 6.0), 6.0 - np.mod(Z - ZC, 6.0)) - 0.4
        casa = menos(casa, np.maximum(tab, np.maximum(-(np.maximum(np.abs(X) - LX + 0.6, np.abs(Y) - LY + 0.6)), np.maximum(ZC + 3 - Z, Z - ZT + 1))), 0.2)
        u = np.where(np.abs(X) / LX > np.abs(Y) / LY, Y, X)
        casa = casa + np.clip(1 - np.abs(casa) / 1.2, 0, 1) * (madeira(u, Z - ZC, tabua=6, fenda=0.01, prof=0.0, veio=0.12, semente=233) + desgaste(g, 0.2, 234))
        casa = menos(casa, np.maximum(caixa(g, (0, 0, ZC + HC / 2 + 2), (LX - 2.6, LY - 2.6, HC / 2), 1), ZC + 3 - Z))   # oca
        casa = menos(casa, np.maximum(np.sqrt((X - 12) ** 2 + (Z - ZC - 20) ** 2) - 6, Y + 10))                         # janela
        casa = menos(casa, caixa(g, (-12, -LY, ZC + 12), (6, 4, 10), 2))                                  # porta
        # placa "NÃO ENTRE" pregada na frente
        placa = caixa(Vista(g, (-12, -LY - 1.2, ZC + 28), rot_y(-6)), (-12, -LY - 1.2, ZC + 28), (12.5, 0.9, 4), 1)
        letras = np.maximum(texto2d(X + 12, Z - ZC - 28, "NÃO ENTRE", 3.0, "sans"), np.abs(Y + LY + 2.4) - 0.5)
        # escada de corda pendurada da porta
        escada = None
        for sx in (-1, 1):
            e = capsula(g, (-12 + sx * 5, -LY - 3, ZC), (-12 + sx * 5.5, -LY - 8, 6), 0.9)
            escada = e if escada is None else np.minimum(escada, e)
        for k in range(6):
            zz = ZC - 8 - k * 9
            yy = -LY - 3 - (ZC - zz) / (ZC - 6) * 5
            escada = np.minimum(escada, caixa(g, (-12, yy, zz), (5.8, 1.2, 1.0), 0.5))
        # bicicletinha encostada no tronco (perfil simples)
        bx, by = 22, -14
        rodas = None
        for dx in (-9, 9):
            r = np.maximum(np.abs(np.sqrt((X - bx - dx) ** 2 + (Z - 7.5) ** 2) - 6) - 1.0, np.abs(Y - by) - 1.2)
            rodas = r if rodas is None else np.minimum(rodas, r)
        quadro = np.minimum.reduce([capsula(g, (bx - 9, by, 7.5), (bx, by, 8), 0.9), capsula(g, (bx, by, 8), (bx + 6, by, 16), 0.9),
                                    capsula(g, (bx - 9, by, 7.5), (bx - 3, by, 15), 0.9), capsula(g, (bx - 3, by, 15), (bx + 6, by, 16), 0.9),
                                    capsula(g, (bx + 6, by, 16), (bx + 9, by, 7.5), 0.9), capsula(g, (bx + 6, by, 16), (bx + 5, by, 20), 0.9)])
        bici = np.minimum(rodas, quadro)
        c4 = np.minimum.reduce([placa, escada, bici])
        return np.minimum.reduce([tronco, casa, c4, letras]), casa, c4, letras


    def telhado(g):
        X, Y, Z = g.x, g.y, g.z
        v = Vista(g, (0, 0, ZT), rot_z(4))                                     # um pouco torto
        t = np.maximum(np.maximum(np.abs(v.x) - LX - 6, np.abs(v.y) - LY - 6), np.maximum(ZT - v.z, (v.z - ZT) - 22 + np.abs(v.x) * 0.8))
        t = smax(t, ZT - v.z, 1)
        telhas = np.minimum(np.mod(v.z - ZT, 4.5), 4.5 - np.mod(v.z - ZT, 4.5)) - 0.4
        t = menos(t, np.maximum(telhas, -(t + 0.7)), 0.2)
        tampao = np.maximum(caixa(g, (0, 0, ZT - 1.5), (LX - 2.6 - F, LY - 2.6 - F, 1.5), 1 - F), Z - ZT)
        chamine = caixa(g, (14, 8, ZT + 18), (3.5, 3.5, 7), 1)
        return np.minimum.reduce([t, tampao, chamine])


    tudo, casa, c4, letras = arvore_casa(g)
    tudo = np.maximum(tudo, g.z - ZT)
    if IMP:
        gv = Vista(g, (0, 0, 0), np.eye(3)); gv.x, gv.z = gv.x - 110, gv.z + ZT - 3.0
        tel = np.maximum(telhado(gv), -g.z)
    else:
        tel = telhado(g)
    tudo = np.maximum(np.minimum(tudo, tel), -g.z)
    return tudo, {"c4": c4, "c3": tel, "c2": casa}          # letras da placa ficam na cor do tronco (c1)


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "casa_arvore", IMP)).items():
        print(k, v)
