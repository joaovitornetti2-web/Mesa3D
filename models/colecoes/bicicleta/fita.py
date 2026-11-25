"""Fita Cassete Porta-Dados – caixinha em forma de fita cassete gigante (e gordinha): etiqueta escrita
"MIXTAPE DA MESA – LADO A", janela com os dois carretéis, parafusinhos e os furos da cabeça de leitura embaixo.
A tampa (metade de cima) é maciça e tem um tampão que entra na boca da caixa (folga 0,25 mm). 104 × 66 × 34 mm.
Cores: c1 carcaça, c2 janela, carretéis e parafusos, c3 etiqueta, c4 faixa e letras da etiqueta.
Impressão (--imprimir): corpo e tampa em pé, lado a lado, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.25)
LX, LY, H, CORTE, F, TP = 52.0, 33.0, 34.0, 20.0, 0.25, 3.0
g = Grade((-56, -37, 0), (56 + (116 if IMP else 0), 37, 38), passo)


def fita(g):
    X, Y, Z = g.x, g.y, g.z
    casco = caixa(g, (0, 0, H / 2), (LX, LY, H / 2), 4)
    topo = H
    # etiqueta no topo
    etiq = np.maximum(caixa(g, (0, 6, topo), (44, 20, 0.8), 3), -(Z - topo + 0.3))
    faixa = np.maximum(np.maximum(np.abs(X) - 43.5, np.abs(Y - 19) - 3.5), np.abs(Z - topo - 0.6) - 0.6)
    letras = np.maximum(np.minimum(texto2d(X, Y - 19, "MIXTAPE DA MESA", 4.2, "mono"), texto2d(X + 30, Y + 6.5, "LADO A", 3.6, "mono")),
                        np.abs(Z - topo - 1.2) - 0.6)
    # janela com carretéis
    jan = caixa(g, (0, 3, topo), (22, 7.5, 1.6), 3.5)
    etiq = menos(etiq, jan + 0.0, 0.3)
    casco = menos(casco, np.maximum(jan, topo - 1.4 - Z), 0.3)
    janela = caixa(g, (0, 3, topo - 1.4), (22, 7.5, 0.6), 3.5)
    carr = None
    for xx in (-13, 13):
        rad = np.sqrt((X - xx) ** 2 + (Y - 3) ** 2)
        a = np.arctan2(Y - 3, X - xx)
        c = np.maximum(np.maximum(rad - 6.2, 3.2 - rad), np.abs(Z - topo + 0.6) - 0.6)
        dentes = np.maximum(np.maximum(rad - 3.3, 1.6 - rad), np.maximum(np.abs(np.mod(a * 6 / (2 * np.pi), 1) - 0.5) - 0.2, np.abs(Z - topo + 0.6) - 0.6))
        carr = np.minimum(c, dentes) if carr is None else np.minimum(carr, np.minimum(c, dentes))
    # parafusos nos cantos
    paraf = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = np.maximum(np.sqrt((X - sx * 46) ** 2 + (Y - sy * 27) ** 2) - 2.2, np.abs(Z - topo - 0.2) - 0.6)
            p = menos(p, np.maximum(np.maximum(np.abs(X - sx * 46) - 1.4, np.abs(Y - sy * 27) - 0.3), Z - topo - 2), 0)
            paraf = p if paraf is None else np.minimum(paraf, p)
    # furos da cabeça de leitura na frente embaixo
    for xx in (-24, -8, 8, 24):
        casco = menos(casco, caixa(g, (xx, -LY, 8), (3 if abs(xx) > 10 else 4.5, 2.5, 3.5), 1.0), 0.4)
    escuro = np.minimum.reduce([janela, carr, paraf, letras])
    c4 = faixa
    tudo = np.minimum.reduce([casco, etiq, escuro, c4])
    return tudo, escuro, etiq, c4


def partes_fita(g):
    tudo, escuro, etiq, c4 = fita(g)
    Z = g.z
    boca = caixa(g, (0, 0, H / 2 + 1), (LX - 2.6, LY - 2.6, H / 2 - 3.4), 2)
    corpo = menos(np.maximum(tudo, Z - CORTE), boca)
    tampao = np.maximum(caixa(g, (0, 0, CORTE - TP / 2), (LX - 2.6 - F, LY - 2.6 - F, TP / 2), 2 - F), Z - CORTE)
    tampa = np.minimum(np.maximum(tudo, CORTE + 0.3 - Z), tampao)
    return corpo, tampa, escuro, etiq, c4


corpo, tampa, escuro, etiq, c4 = partes_fita(g)
if IMP:
    gv = Vista(g, (0, 0, 0), np.eye(3))
    gv.x, gv.z = gv.x - 116, gv.z + CORTE - TP
    _, t2, e2, et2, c42 = partes_fita(gv)
    tampa = np.maximum(t2, CORTE - TP - gv.z)
    escuro, etiq, c4 = np.minimum(escuro, e2), np.minimum(etiq, et2), np.minimum(c4, c42)
tudo = np.maximum(np.minimum(corpo, tampa), -g.z)
partes = dividir(tudo, {"c4": c4, "c2": escuro, "c3": etiq})
for k, vv in exportar(g, partes, saida(__file__, "fita", IMP), faces=None).items():
    print(k, vv)
