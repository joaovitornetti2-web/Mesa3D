"""Estandartes de Iniciativa – conjunto de 8 bandeirinhas numeradas (1 a 8) num mastro com base redonda de pedra
(Ø 25 mm, cabe num quadrado da grade). Ponha na frente da miniatura ou na mesa para marcar a ordem do turno.
Estandarte com rabo de andorinha e número em relevo dos dois lados. Cerca de 62 mm de altura.
Cores: c1 base e mastro, c2 estandarte, c3 número, c4 ponteira. Em pé, sem suporte.
Foto: 1 a 4 em fila. Impressão (--imprimir): os 8 lado a lado."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.2)
N = 8 if IMP else 4
DX = 30.0
g = Grade((-16, -16, 0), (16 + DX * (N - 1), 16, 66), passo)
X, Y, Z = g.x, g.y, g.z
rr = ruido(g, 0.8, 2)
tudo = band = num = pont = None
for i in range(N):
    cx = i * DX
    base = cilindro(g, (cx, 0, 0), 12.5, 3.6, 1.2) + rr * 0.15
    base = smin(base, cilindro(g, (cx, 0, 3.0), 5, 2.5, 1.0), 1.5)
    mastro = capsula(g, (cx - 9, 0, 3), (cx - 9, 0, 60), 1.7)
    mastro = smin(mastro, cilindro(g, (cx - 9, 0, 3), 3.4, 2.4, 0.8), 1.0)
    trav = capsula(g, (cx - 9, 0, 57), (cx + 13, 0, 57), 1.1)
    p = esfera(g, (cx - 9, 0, 62), 2.6)
    p = smin(p, capsula(g, (cx - 9, 0, 62), (cx - 9, 0, 65.5), 1.6, 0.3), 0.8)
    # estandarte: pendurado na travessa, ondulado, rabo de andorinha embaixo
    u, w = X - cx - 2, Z - 40
    onda = 1.2 * np.sin(u * 0.28 + 0.6)
    plano = np.abs(Y - onda) - 1.0
    contorno = np.maximum(np.maximum(np.abs(u) - 11, w - 15.5), 7 * (1 - np.abs(u) / 11) - (w + 15))   # rabo de andorinha
    ban = np.maximum(plano, contorno)
    # número em relevo dos dois lados
    t2 = texto2d(u, w + 1.5, str(i + 1), 14, "serif")
    n = np.maximum(t2, np.abs(Y - onda) - 1.6)
    n = np.maximum(n, -(np.abs(Y - onda) - 0.9))
    peca = np.minimum.reduce([base, mastro, trav, p, ban, n])
    tudo = peca if tudo is None else np.minimum(tudo, peca)
    band = ban if band is None else np.minimum(band, ban)
    num = n if num is None else np.minimum(num, n)
    pont = p if pont is None else np.minimum(pont, p)
tudo = np.maximum(tudo, -Z)
partes = dividir(tudo, {"c3": num, "c4": pont, "c2": band})
for k, v in exportar(g, partes, saida(__file__, "iniciativa", IMP), faces=None).items():
    print(k, v)
