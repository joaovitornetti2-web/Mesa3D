"""Estandartes de Iniciativa – conjunto de 8 bandeirinhas numeradas (1 a 8) num mastro com base redonda de pedra
(Ø 25 mm, cabe num quadrado da grade). Ponha na frente da miniatura ou na mesa para marcar a ordem do turno.
Estandarte com rabo de andorinha e número em relevo dos dois lados. Cerca de 62 mm de altura.
Cores: c1 base e mastro, c2 estandarte, c3 número, c4 ponteira. Em pé, sem suporte.
Foto: 1 a 4 em fila. Impressão (--imprimir): os 8 lado a lado."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.12)
N = 8 if IMP else 4
DX = 30.0
MN, MX = (-16, -16, 0), (16 + DX * (N - 1), 16, 66)


def campo(g):
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
        lanca = np.maximum(poligono2d(X - cx + 9, Z - 63, [(-2.4, 0), (0, 5.5), (2.4, 0), (0, -1.0)]), np.abs(Y) - 0.9 + 0.25 * np.abs(X - cx + 9))
        p = smin(esfera(g, (cx - 9, 0, 61.2), 2.1), lanca, 0.5)
        # estandarte: pendurado na travessa, ondulado, rabo de andorinha embaixo
        u, w = X - cx - 2, Z - 40
        onda = 1.2 * np.sin(u * 0.28 + 0.6) + 0.35 * np.sin(u * 0.9 + w * 0.25 + i) * np.clip((15 - w) / 10, 0, 1)   # dobras do pano
        plano = np.abs(Y - onda) - 1.0
        contorno = np.maximum(np.maximum(np.abs(u) - 11, w - 15.5), 7 * (1 - np.abs(u) / 11) - (w + 15))   # rabo de andorinha
        ban = np.maximum(plano, contorno)
        bord = np.maximum(np.maximum(np.abs(contorno + 1.4) - 0.35, np.abs(Y - onda) - 1.35), contorno)      # bainha bordada
        ban = np.minimum(ban, bord)
        for k in range(7):                                                             # laços que prendem o pano na travessa
            ban = np.minimum(ban, capsula(g, (cx - 8 + k * 3.33, 0, 57.0), (cx - 8 + k * 3.33, 0, 54.0), 0.45, 0.3))
        base = base + desgaste(g, 0.3, 10 + i) + 0.4 * np.clip(1 - np.abs(Z - 3.6) / 0.6, 0, 1) * (np.abs(np.mod(np.degrees(np.arctan2(Y, X - cx)), 45) - 22.5) < 0.8)
        mastro = mastro + 0.1 * np.sin(np.arctan2(Y, X - cx + 9) * 3 + Z * 1.4)       # cabo torneado
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
    return tudo, {"c3": num, "c4": pont, "c2": band}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "iniciativa", IMP)).items():
        print(k, v)
