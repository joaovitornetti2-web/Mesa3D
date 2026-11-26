"""Elmo Guarda-Dados – elmo de guerreiro com chifres curvos, viseira em T, rebites e crista de pelos, que cobre
os dados como uma redoma: levante o elmo pela crista e os dados estão na base (prato com rebaixo onde o elmo
assenta, folga 0,3 mm). 112 × 84 × 98 mm.
Cores: c1 elmo, c2 rebites, viseira e faixa, c3 chifres, c4 crista e base.
Impressão (--imprimir): elmo em pé (boca para baixo, cúpula autoportante) e base deitada, lado a lado."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.14)
RB, ZB, E, F = 38.0, 6.0, 2.4, 0.3            # raio da boca do elmo, altura onde assenta, parede, folga


def elmo(g):
    X, Y, Z = g.x, g.y, g.z
    rr = ruido(g, 2.0, 121)
    cup = elipsoide(g, (0, 0, ZB), (RB, RB * 0.92, 62)) + rr * 0.15
    cup = np.maximum(cup, ZB - Z)
    cup = smin(cup, np.maximum(np.abs(elipsoide(g, (0, 0, ZB), (RB + 1.6, RB * 0.92 + 1.6, 62))) - 1.6, np.abs(Z - ZB - 4) - 4), 0.8)   # aba
    cup = menos(cup, np.maximum(elipsoide(g, (0, 0, ZB), (RB - E, RB * 0.92 - E, 62 - E)), ZB - 1 - Z))
    # viseira em T (vazada) na frente
    fr = -RB * 0.92
    tv = np.minimum(np.maximum(np.abs(X) - 17, np.abs(Z - 40) - 3.6), np.maximum(np.abs(X) - 3.6, np.abs(Z - 26) - 13))
    cup = menos(cup, np.maximum(tv, Y - fr * 0.4), 0.6)
    moldura = np.maximum(np.maximum(tv - 2.0, -tv), np.abs(elipsoide(g, (0, 0, ZB), (RB + 0.6, RB * 0.92 + 0.6, 62.6))) - 1.2)
    moldura = np.maximum(moldura, Y)
    faixa = np.maximum(np.abs(X) - 4.5, np.maximum(np.abs(elipsoide(g, (0, 0, ZB), (RB + 0.6, RB * 0.92 + 0.6, 62.6))) - 1.0, Z - 66))
    faixa = np.maximum(faixa, 45 - Z)
    reb = None
    for k in range(12):
        a = np.radians(k * 30 + 15)
        r_ = esfera(g, ((RB + 1.8) * np.cos(a), (RB * 0.92 + 1.8) * np.sin(a), ZB + 4), 1.5)
        reb = r_ if reb is None else np.minimum(reb, r_)
    metal = np.minimum.reduce([moldura, faixa, reb])
    # chifres
    chif = None
    for sx in (-1, 1):
        c = tubo(g, [(sx * 30, 4, 46), (sx * 44, 4, 52), (sx * 52, 0, 66), (sx * 50, -4, 80), (sx * 45, -6, 87)], [7.0, 5.6, 4.2, 2.6, 0.8])
        chif = c if chif is None else np.minimum(chif, c)
        cup = smin(cup, cilindro(Vista(g, (sx * 31, 4, 46), rot_y(sx * 75)), (sx * 31, 4, 44), 8.5, 4, 1.5), 1.5)   # base do chifre
    # crista (pelos) no topo, também serve de pegador
    crista = None
    for i in range(9):
        t = i / 8
        y = -18 + 40 * t
        h = 63 + 10 * np.sin(np.pi * t) + ZB
        cr = capsula(g, (0, y, h - 8), (0, y + 3, h + 2), 3.4, 1.4)
        crista = cr if crista is None else smin(crista, cr, 1.5)
    # metal martelado, chifres com anéis de crescimento, crina em mechas
    cup = cup + 0.05 * ruido(g, 0.5, 141) + 0.12 * np.clip(ruido(g, 1.4, 142) - 1.1, 0, None)
    chif = chif + 0.18 * np.abs(np.sin(np.hypot(g.x, g.z - 60) * 1.6)) * np.clip(1 - np.abs(chif) / 1.0, 0, 1)
    crista = crista + pelo(g, 3.0, 0.55, 0.22, 143)
    tudo = np.minimum.reduce([cup, metal, chif, crista])
    return tudo, metal, chif, crista


def base(g):
    X, Y, Z = g.x, g.y, g.z
    rad = np.sqrt(X ** 2 + (Y / 0.92) ** 2)
    b = np.maximum(rad - RB - 6, np.maximum(-Z, Z - ZB)) + ruido(g, 2.0, 122) * 0.1
    b = smax(b, Z - ZB, 1.5)
    b = menos(b, np.maximum(np.abs(rad - RB + E / 2) - E / 2 - F, ZB - 3.5 - Z))      # sulco onde o elmo assenta
    b = menos(b, np.maximum(rad - RB + E + 3, ZB - 2.2 - Z), 1.5)                    # prato dos dados
    return b


MN, MX = ((-58, -46, 0), (158, 46, 96)) if IMP else ((-58, -46, 0), (58, 46, 92))


def campo(g):
    if IMP:
        gv = Vista(g, (0, 0, 0), np.eye(3))
        gv.z = gv.z + ZB                                           # elmo com a boca na mesa
        tudo, metal, chif, crista = elmo(gv)
        tudo = np.maximum(tudo, -g.z)
        gb = Vista(g, (0, 0, 0), np.eye(3))
        gb.x = gb.x - 100
        b = base(gb)
    else:
        tudo, metal, chif, crista = elmo(g)
        b = base(g)
    c4 = np.minimum(crista, b)
    tudo = np.maximum(np.minimum(tudo, b), -g.z)
    return tudo, {"c3": chif, "c2": metal, "c4": c4}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "elmo", IMP)).items():
        print(k, v)
