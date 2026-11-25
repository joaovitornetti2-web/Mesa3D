"""Machado do Campeão – réplica de mesa (decoração): machado de duas lâminas em lua com runas gravadas, cabo
enrolado em couro e pomo de gema, em pé num suporte de pedra com um furo onde o cabo encaixa.
44 × 64 × 150 mm. Cores: c1 suporte, c2 lâmina, c3 runas e gema, c4 couro do cabo.
Impressão (--imprimir): machado deitado de lado (sem suporte) e o suporte em pé, lado a lado."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.25)
HC = 110.0                     # comprimento do cabo


def machado(g, z0):
    """machado em pé: cabo no eixo z a partir de z0, lâminas no plano xz (espessura em y)."""
    X, Y, Z = g.x, g.y, g.z
    zc = z0 + HC - 14
    cabo = capsula(g, (0, 0, z0), (0, 0, z0 + HC), 3.2)
    couro = np.maximum(np.abs(np.sqrt(X ** 2 + Y ** 2) - 3.4) - 0.7, np.abs(Z - z0 - 30) - 22)
    couro = couro + 0.3 * (np.abs(np.mod(Z - X * 0.6, 4) - 2) < 0.4)
    pomo = esfera(g, (0, 0, z0 - 2.5), 4.4)
    gema = np.maximum(np.abs(X) + np.abs(Y) * 0.8 + np.abs(Z - z0 - HC - 5) * 0.8 - 4.4, -(Z - z0 - HC))
    lam = None
    for s in (-1, 1):
        l = np.maximum(np.sqrt((X - s * 2) ** 2 + (Z - zc) ** 2) - 30, -s * X + 3)
        l = menos(l, np.sqrt((X - s * 40) ** 2 + (Z - zc) ** 2) - 20)            # recorte em lua
        t = np.clip(np.abs(X) / 30, 0, 1)
        l = np.maximum(l, np.abs(Y) - (3.2 - 2.2 * t))                          # afina até o fio
        lam = l if lam is None else np.minimum(lam, l)
    lam = np.minimum(lam, cilindro(g, (0, 0, zc - 9), 6.5, 18, 1.5))           # olho do machado
    # runas gravadas nas duas faces de cada lâmina
    runas = None
    for s in (-1, 1):
        for i, dz in enumerate((-8, 0, 8)):
            u, w = X - s * 15, Z - zc - dz
            tr = np.maximum(np.abs(u) - 0.6, np.abs(w) - 3)
            if i == 0:
                tr = np.minimum(tr, np.maximum(np.abs(u - w * 0.7) - 0.6, np.abs(w - 1) - 2))
            elif i == 1:
                tr = np.minimum(tr, np.maximum(np.abs(w) - 0.6, np.abs(u) - 2.4))
            else:
                tr = np.minimum(tr, np.abs(np.sqrt((u - 1.6) ** 2 + (w - 1) ** 2) - 1.4) - 0.5)
            runas = tr if runas is None else np.minimum(runas, tr)
    runas = np.maximum(runas, np.abs(np.abs(Y) - (3.2 - 2.2 * 0.5)) - 0.6)
    tudo = np.minimum.reduce([cabo, couro, pomo, gema, lam, runas])
    return tudo, lam, np.minimum(runas, gema), couro


def suporte(g, cx=0.0):
    X, Y, Z = g.x - cx, g.y, g.z
    s = caixa(Vista(g, (cx, 0, 0), np.eye(3)), (cx, 0, 8), (22, 32, 8), 3) + ruido(g, 2.0, 161) * 0.3
    s = smin(s, caixa(Vista(g, (cx, 0, 0), np.eye(3)), (cx, 0, 2), (25, 35, 2), 1.5), 1)
    s = menos(s, np.maximum(np.sqrt(X ** 2 + Y ** 2) - 3.6, 4 - Z))                     # furo do cabo (folga 0,4)
    return s


if IMP:
    g = Grade((-36, -40, 0), (36 + 160, 40, 18), passo)
    gv = Vista(g, (0, 0, 0), rot_x(90)); gv.z, gv.y = gv.z + 70, gv.y + 3.4     # machado deitado (eixo ao longo de y)
    tudo, lam, claro, couro = machado(gv, 0.0)
    tudo = np.maximum(tudo, -g.z)
    s = suporte(g, 140)
else:
    g = Grade((-36, -40, 0), (36, 40, 152), passo)
    # machado em pé, cabo encaixado no furo do suporte
    tudo, lam, claro, couro = machado(g, 4.5)
    s = suporte(g)
tudo = np.maximum(np.minimum(tudo, s), -g.z)
partes = dividir(tudo, {"c3": claro, "c4": couro, "c2": lam})
for k, vv in exportar(g, partes, saida(__file__, "machado", IMP), faces=None).items():
    print(k, vv)
