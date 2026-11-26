"""Bandeja da Tormenta – bandeja de dados com a borda feita de nuvens de tempestade fofas e, no fundo, raios em
relevo cruzando um céu rachado. 168 × 124 × 22 mm.
Cores: c1 bandeja, c2 rachaduras do céu, c3 raios, c4 nuvens da borda (vermelhas). Deitada, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.15)
AX, AY, EF = 76.0, 54.0, 2.4
MN, MX = (-86, -64, 0), (86, 64, 26)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    # fundo arredondado
    fundo = np.maximum(caixa(g, (0, 0, EF / 2), (AX, AY, EF / 2), 20), -Z)
    # pontos espaçados por igual no contorno de um retângulo de cantos arredondados
    RC = 22.0
    lados = [2 * (AX - RC), np.pi * RC / 2, 2 * (AY - RC), np.pi * RC / 2] * 2
    per = sum(lados)
    def contorno(d):
        d = d % per
        cantos = [(-(AX - RC), AY - RC), (-(AX - RC), -(AY - RC)), (AX - RC, -(AY - RC)), (AX - RC, AY - RC)]
        segs = [((AX - RC, AY), (-(AX - RC), AY)), None, ((-AX, AY - RC), (-AX, -(AY - RC))), None,
                ((-(AX - RC), -AY), (AX - RC, -AY)), None, ((AX, -(AY - RC)), (AX, AY - RC)), None]
        for i, Lg in enumerate(lados):
            if d <= Lg:
                if segs[i] is not None:
                    (x0, y0), (x1, y1) = segs[i]; t = d / Lg
                    return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                cx, cy = cantos[i // 2]
                a = [np.pi / 2, np.pi, 3 * np.pi / 2, 0][i // 2] + d / RC
                return cx + RC * np.cos(a), cy + RC * np.sin(a)
            d -= Lg
    nuv = None
    N = 46
    for k in range(N):
        px, py = contorno(k / N * per)
        r = 9.5 + 2.5 * np.sin(k * 2.7)
        b = esfera(g, (px, py, 9 + 3 * np.sin(k * 1.9)), r)
        nuv = b if nuv is None else smin(nuv, b, 3)
    nuv = np.maximum(nuv, -Z)
    dentro = caixa(g, (0, 0, 12), (AX - 9, AY - 9, 12), 14)
    nuv = menos(nuv, np.maximum(dentro, EF - Z), 2)
    # céu rachado (sulcos rasos) e raios em relevo
    rach = None
    for (pts, rs) in [([(-50, 20), (-30, 8), (-10, 14), (12, 0)], 0.6), ([(30, -30), (18, -12), (34, 4), (52, 10)], 0.6), ([(-40, -28), (-22, -20)], 0.5)]:
        t3 = [(x, y, EF) for x, y in pts]
        r_ = tubo(g, t3, [rs] * len(t3))
        rach = r_ if rach is None else np.minimum(rach, r_)
    rach = np.maximum(rach, np.abs(Z - EF) - 0.5)
    raios = None
    for (pts, w) in [([(-46, 34), (-30, 12), (-38, 10), (-18, -14), (-28, -14), (-8, -38)], 2.4), ([(40, 38), (30, 18), (38, 16), (22, -8)], 2.0)]:
        for i in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            dx, dy = x1 - x0, y1 - y0
            h = np.clip(((X - x0) * dx + (Y - y0) * dy) / (dx * dx + dy * dy), 0, 1)
            seg = np.sqrt((X - x0 - dx * h) ** 2 + (Y - y0 - dy * h) ** 2) - w * (1 - 0.5 * (i + h) / (len(pts) - 1))
            raios = seg if raios is None else np.minimum(raios, seg)
    raios = np.maximum(raios, np.maximum(EF - Z, Z - EF - 0.8))
    nuv = nuv - 0.8 * np.clip(fbm(g, 4.5, 181, 3), 0, None) * np.clip(1 - np.abs(nuv) / 3, 0, 1)      # volutas
    fundo = fundo + 0.05 * ruido(g, 0.5, 182)
    tudo = np.minimum.reduce([fundo, nuv, rach, raios])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c3": raios, "c2": rach, "c4": nuv}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "bandeja_nuvem", IMP)).items():
        print(k, v)
