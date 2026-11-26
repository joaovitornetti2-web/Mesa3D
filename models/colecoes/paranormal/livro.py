"""Livro Proibido – caixa porta-dados em forma de grimório: capa de couro gasto com cantoneiras de metal, tira
com fivela, um olho aberto no meio da capa (pálpebra e veias em relevo) e bordas de páginas nas laterais.
A tampa (capa + 1 cm de páginas) é maciça, com um tampão embaixo que entra na boca da caixa (folga 0,25 mm).
86 × 112 × 42 mm. Cores: c1 couro, c2 metal e pupila, c3 páginas e branco do olho, c4 íris.
Impressão (--imprimir): corpo e tampa em pé, lado a lado (tampão da tampa na mesa), sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.13)
LX, LY, H, CAPA = 43.0, 56.0, 42.0, 3.6
CORTE, F, TP = 30.0, 0.25, 3.0          # altura do corte, folga, altura do tampão
MN, MX = (-48, -60, 0), (48 + (100 if IMP else 0), 60, 50)


def campo(g):


    def livro(g):
        X, Y, Z = g.x, g.y, g.z
        rr = ruido(g, 2.5, 31)
        capas = np.minimum(caixa(g, (0, 0, CAPA / 2), (LX, LY, CAPA / 2), 1.2), caixa(g, (0, 0, H - CAPA / 2), (LX, LY, CAPA / 2), 1.2))
        lombada = np.maximum(caixa(g, (-LX + 5, 0, H / 2), (5, LY, H / 2), 4.5), -X - LX)
        couro = np.minimum(capas, lombada) + rr * 0.25
        couro = couro + 0.08 * ruido(g, 0.4, 32) + 0.18 * np.clip(np.abs(ruido(g, 3.0, 33)) - 0.9, 0, None)   # poros e vincos do couro
        for zz in (11, 21, 31):                                   # nervuras da lombada
            couro = smin(couro, capsula(g, (-LX - 0.3, -LY + 1, zz), (-LX - 0.3, LY - 1, zz), 1.3), 0.6)
        moldura = np.maximum(np.abs(np.maximum(np.abs(X - 3) - 32, np.abs(Y) - 46)) - 0.5, np.abs(Z - H) - 0.6)
        couro = menos(couro, moldura, 0.2)
        for sy in (-1, 1):                                        # filete pontilhado gravado
            for k in range(-9, 10):
                couro = menos(couro, esfera(g, (3 + k * 3.4, sy * 49, H + 0.3), 0.55), 0.1)
        # Marca de Sangue em relevo na lombada, dentro de um losango
        sl = np.maximum(np.minimum(sigilo_sangue(Y, Z - H / 2, 18, 1.4), np.abs(np.abs(Y) + np.abs(Z - H / 2) - 12) - 0.7), np.abs(X + LX + 0.4) - 0.9)
        couro = smin(couro, sl, 0.3)
        paginas = caixa(g, (2.2, 0, H / 2), (LX - 2.6, LY - 2.6, H / 2 - CAPA + 0.2), 0.6)
        paginas = paginas + (0.22 * np.sin(Z * 6.0) + 0.06 * np.sin(Z * 17)) * (paginas > -1.2) + 0.05 * ruido(g, 2, 34)   # folhas nas bordas
        # cantoneiras de metal
        metal = None
        for sy in (-1, 1):
            for zc in (CAPA / 2, H - CAPA / 2):
                tri = np.maximum(np.maximum(-(X - LX + 11), -(sy * Y - LY + 11)), (X - LX + 11) + (sy * Y - LY + 11) - 13)
                c = np.maximum(caixa(g, (LX - 5.4, sy * (LY - 5.4), zc), (6.2, 6.2, CAPA / 2 + 0.6), 1.0), tri)
                metal = c if metal is None else np.minimum(metal, c)
        # tira por cima da capa descendo pela frente, com fivela
        tira = np.maximum(np.abs(Y) - 6, np.maximum(np.abs(np.maximum(X - LX, Z - H)) - 1.1, np.maximum(18 - X, 12 - Z)))
        fivela = np.maximum(caixa(g, (LX + 1.6, 0, 22), (1.2, 8.5, 6.5), 1.0), -caixa(g, (LX + 1.6, 0, 22), (3, 6.5, 4.5), 0.6))
        metal = np.minimum(metal, fivela)
        metal = np.minimum(metal, rebites(g, [(LX - 2.2, sy * (LY - 8.5), zc) for sy in (-1, 1) for zc in (CAPA / 2, H - CAPA / 2)] +
                                          [(LX - 8.5, sy * (LY - 2.2), zc) for sy in (-1, 1) for zc in (CAPA / 2, H - CAPA / 2)], 0.8))
        metal = metal + 0.05 * ruido(g, 1.0, 35)
        # olho: amêndoa aberta na capa, globo, íris e pupila de gato; pálpebra e veias em relevo
        ox, oy = -2.0, 0.0
        amendoa = np.maximum(np.sqrt((Y - oy) ** 2 + (X - ox + 20) ** 2) - 28, np.sqrt((Y - oy) ** 2 + (X - ox - 20) ** 2) - 28)
        palpebra = np.maximum(amendoa - 3.2, np.abs(Z - H - 1.0) - 1.6)
        couro = smin(couro, palpebra, 1.2)
        couro = menos(couro, np.maximum(amendoa + 0.2, H - 10.4 - Z), 0.5)
        globo = np.maximum(esfera(g, (ox, oy, H - 9), 14.2), amendoa)
        iris = np.maximum(np.sqrt((X - ox) ** 2 + (Y - oy - 2) ** 2) - 6.8, -globo - 0.8)
        pupila = np.maximum(np.sqrt(((X - ox) / 0.45) ** 2 + (Y - oy - 2) ** 2) - 3.0, -globo - 0.9)
        veias = None
        for a in (20, 70, 160, 210, 300, 340):
            r = np.radians(a)
            vv = tubo(g, [(ox + 15 * np.cos(r), oy + 20 * np.sin(r), H + 0.4), (ox + 22 * np.cos(r + 0.2), oy + 30 * np.sin(r + 0.25), H + 0.3),
                          (ox + 27 * np.cos(r + 0.05), oy + 38 * np.sin(r + 0.1), H + 0.2)], [0.7, 0.55, 0.35])
            veias = vv if veias is None else np.minimum(veias, vv)
        couro = smin(couro, veias, 0.4)
        tudo = np.minimum.reduce([couro, paginas, metal, tira, globo])
        return tudo, metal, np.minimum(paginas, globo), iris, pupila


    def partes_livro(g):
        tudo, metal, claro, iris, pupila = livro(g)
        Z = g.z
        boca = caixa(g, (2, 0, H / 2 + 1), (LX - 9, LY - 9, H / 2 - CAPA - 2), 2)
        corpo = menos(np.maximum(tudo, Z - CORTE), boca)
        tampao = np.maximum(caixa(g, (2, 0, CORTE - TP / 2), (LX - 9 - F, LY - 9 - F, TP / 2), 2 - F), Z - CORTE)
        tampa = np.minimum(np.maximum(tudo, CORTE + 0.3 - Z), tampao)
        return corpo, tampa, metal, claro, iris, pupila


    corpo, tampa, metal, claro, iris, pupila = partes_livro(g)
    if IMP:
        gv = Vista(g, (0, 0, 0), np.eye(3))
        gv.x, gv.z = gv.x - 100, gv.z + CORTE - TP          # tampa ao lado, tampão na mesa
        _, t2, m2, c2, i2, p2 = partes_livro(gv)
        tampa = np.maximum(t2, CORTE - TP - gv.z)
        metal, claro, iris, pupila = np.minimum(metal, m2), np.minimum(claro, c2), np.minimum(iris, i2), np.minimum(pupila, p2)
    tudo = np.maximum(np.minimum(corpo, tampa), -g.z)
    return tudo, {"c2": np.minimum(metal, pupila), "c4": iris, "c3": claro}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "livro", IMP)).items():
        print(k, v)
