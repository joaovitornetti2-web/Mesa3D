"""Caixa de Evidências – caixa de arquivo da investigação para guardar dados, cartas e fichas: aparência de papelão
com abas, etiqueta "EVIDÊNCIA / CASO Nº 13" e uma fita de isolamento "NÃO ULTRAPASSE" atravessada.
Tampa maciça com tampão que entra na boca (folga 0,25 mm). 100 × 76 × 62 mm.
Cores: c1 caixa, c2 letras, c3 etiqueta, c4 fita. Impressão (--imprimir): corpo e tampa em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.25)
LX, LY, H, CORTE, F, TP = 50.0, 38.0, 62.0, 50.0, 0.25, 3.0
g = Grade((-54, -42, 0), (54 + (112 if IMP else 0), 42, 66), passo)


def caixa_ev(g):
    X, Y, Z = g.x, g.y, g.z
    rr = ruido(g, 3.0, 51)
    cx = caixa(g, (0, 0, H / 2), (LX, LY, H / 2), 1.6) + rr * 0.12
    # tampa com borda que desce (aba) – sulco marcando a aba
    cx = menos(cx, np.maximum(np.abs(Z - CORTE + 0.6) - 0.5, -(np.maximum(np.abs(X) - LX + 0.6, np.abs(Y) - LY + 0.6))), 0.2)
    cx = smin(cx, caixa(g, (0, 0, CORTE + (H - CORTE) / 2), (LX + 0.8, LY + 0.8, (H - CORTE) / 2), 1.8), 0.6)
    # alça recortada nas laterais
    for sx in (-1, 1):
        cx = menos(cx, caixa(g, (sx * LX, 0, 38), (3, 11, 3.6), 3.4), 0.4)
    # etiqueta na frente
    u, w = X + 8, Z - 30
    etiq = np.maximum(caixa(g, (-8, -LY - 0.4, 30), (28, 1.0, 14), 2), Y + LY - 0.2)
    t1 = texto2d(u, w - 5.5, "EVIDÊNCIA", 7, "serif")
    t2 = texto2d(u, w + 6.0, "CASO Nº 13", 5.5, "mono")
    letras = np.maximum(np.minimum(t1, t2), np.abs(Y + LY + 1.45) - 0.45)
    # fita de isolamento: diagonal na frente, contorna a lateral direita e passa por cima
    d = (Z - 11) - (X - 10) * 0.42
    fita_f = np.maximum(np.abs(d) - 5.0, np.maximum(np.abs(Y + LY + 0.5) - 0.7, X - LX - 0.7))
    fita_l = np.maximum(np.abs((Z - 11) - 40 * 0.42 - (Y + LY) * 0.05) - 5.0, np.maximum(np.abs(X - LX - 0.5) - 0.7, np.abs(Y) - LY - 0.7))
    fita = np.minimum(fita_f, fita_l)
    fita = np.maximum(fita, -cx - 1.5)
    # texto da fita (inclinado): coordenadas ao longo da fita
    ang = np.arctan(0.42)
    s = (X - 10) * np.cos(ang) + (Z - 11) * np.sin(ang)
    tt = -(X - 10) * np.sin(ang) + (Z - 11) * np.cos(ang)
    txt = texto2d(s - 8, tt, "NÃO ULTRAPASSE", 4.2, "mono")
    txt = np.maximum(txt, np.maximum(np.abs(Y + LY + 1.55) - 0.4, X - LX))
    letras = np.minimum(letras, txt)
    tudo = np.minimum.reduce([cx, etiq, fita, letras])
    return tudo, letras, etiq, fita


def partes_caixa(g):
    tudo, letras, etiq, fita = caixa_ev(g)
    Z = g.z
    boca = caixa(g, (0, 0, H / 2 + 1), (LX - 2.6, LY - 2.6, H / 2 - 2.6), 1.5)
    corpo = menos(np.maximum(tudo, Z - CORTE), boca)
    tampao = np.maximum(caixa(g, (0, 0, CORTE - TP / 2), (LX - 2.6 - F, LY - 2.6 - F, TP / 2), 1.5 - F), Z - CORTE)
    tampa = np.minimum(np.maximum(tudo, CORTE + 0.3 - Z), tampao)
    return corpo, tampa, letras, etiq, fita


corpo, tampa, letras, etiq, fita = partes_caixa(g)
if IMP:
    gv = Vista(g, (0, 0, 0), np.eye(3))
    gv.x, gv.z = gv.x - 112, gv.z + CORTE - TP
    _, t2, l2, e2, f2 = partes_caixa(gv)
    tampa = np.maximum(t2, CORTE - TP - gv.z)
    letras, etiq, fita = np.minimum(letras, l2), np.minimum(etiq, e2), np.minimum(fita, f2)
tudo = np.maximum(np.minimum(corpo, tampa), -g.z)
partes = dividir(tudo, {"c2": letras, "c3": etiq, "c4": fita})
for k, v in exportar(g, partes, saida(__file__, "evidencias", IMP), faces=None).items():
    print(k, v)
