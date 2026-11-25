"""Barra de Vida – marcador de pontos de vida no estilo videogame dos anos 80: régua com 10 encaixes de coração
pixelado e a palavra "VIDA"; os corações são peças soltas que entram nos encaixes (folga 0,2 mm). Tirou dano, tira um
coração. Régua 176 × 34 × 7 mm; corações 13 × 12 × 4 mm. Conjunto com 10 corações.
Cores: c1 régua, c2 moldura pixelada e letras, c3 brilho dos corações, c4 corações.
Foto: 7 corações no lugar. Impressão (--imprimir): régua e os 10 corações deitados."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.15)
PX = 1.45                             # tamanho do "pixel"
CORACAO = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]
BRILHO = [(1, 1)]                     # (linha, coluna) do pixel de brilho


def coracao2d(u, v, folga=0.0):
    """campo 2D de um coração pixelado centrado em (0, 0)."""
    d = None
    for r, linha in enumerate(CORACAO):
        for c, ch in enumerate(linha):
            if ch == "X":
                cx, cy = (c - 3) * PX, (2.5 - r) * PX
                q = np.maximum(np.abs(u - cx), np.abs(v - cy)) - PX / 2 - folga
                d = q if d is None else np.minimum(d, q)
    return d


def brilho2d(u, v):
    d = None
    for (r, c) in BRILHO:
        cx, cy = (c - 3) * PX, (2.5 - r) * PX
        q = np.maximum(np.abs(u - cx), np.abs(v - cy)) - PX / 2 + 0.05
        d = q if d is None else np.minimum(d, q)
    return d


L, W, H = 88.0, 17.0, 7.0
XS = [-58 + i * 13.5 for i in range(10)]
HC = 4.0


def regua(g):
    X, Y, Z = g.x, g.y, g.z
    r = caixa(g, (0, 0, H / 2), (L, W, H / 2), 2)
    # moldura pixelada (degraus) em relevo e "VIDA"
    mold = np.maximum(np.abs(np.maximum(np.abs(X) - L + 2.5, np.abs(Y) - W + 2.5)) - 0.9, np.abs(Z - H - 0.4) - 0.6)
    letras = np.maximum(texto2d(X + 73, Y, "VIDA", 5, "mono"), np.abs(Z - H - 0.4) - 0.6)
    for x in XS:
        r = menos(r, np.maximum(coracao2d(X - x, Y + 0.4, 0.2), H - HC + 0.4 - Z))          # encaixes
    return np.minimum.reduce([r, mold, letras]), np.minimum(mold, letras)


def coracoes(g, centros, z0):
    X, Y, Z = g.x, g.y, g.z
    cor = bri = None
    for (x, y) in centros:
        c = np.maximum(coracao2d(X - x, Y - y), np.maximum(z0 - Z, Z - z0 - HC))
        b = np.maximum(brilho2d(X - x, Y - y), np.abs(Z - z0 - HC + 0.3) - 0.4)
        cor = c if cor is None else np.minimum(cor, c)
        bri = b if bri is None else np.minimum(bri, b)
    return cor, bri


if IMP:
    g = Grade((-92, -21, 0), (92, 21 + 26, H + 1.5), passo)
    tudo, escuro = regua(g)
    cor, bri = coracoes(g, [(-60 + i * 13.5, 34) for i in range(10)], 0.0)
else:
    g = Grade((-92, -21, 0), (92, 21, H + 2.5), passo)
    tudo, escuro = regua(g)
    cor, bri = coracoes(g, [(x, -0.4) for x in XS[:7]], H - HC + 0.4)
tudo = np.maximum(np.minimum.reduce([tudo, cor, bri]), -g.z)
partes = dividir(tudo, {"c3": bri, "c4": cor, "c2": escuro})
for k, vv in exportar(g, partes, saida(__file__, "barra_vida", IMP), faces=None).items():
    print(k, vv)
