"""Bandeja Círculo de Ritual – bandeja de dados redonda (Ø 160 mm) com um círculo de invocação em relevo no fundo:
dois anéis com runas inventadas, um selo central (olho dentro de um triângulo de pontas abertas) e cinco velinhas
derretidas na borda, com cera vermelha escorrendo para dentro.
Cores: c1 bandeja, c2 círculo e runas (últimas camadas), c3 velas, c4 cera. Deitada, sem suporte. Dica: feltro no fundo."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.3)
RB, HB, EF = 80.0, 16.0, 2.4
MN, MX = (-84, -84, 0), (84, 84, 34)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    rad = np.sqrt(X ** 2 + Y ** 2)
    ang = np.arctan2(Y, X)
    rr = ruido(g, 2.0, 61)
    band = np.maximum(rad - RB - 0.8 * np.sin(ang * 9), np.maximum(-Z, Z - HB)) + rr * 0.2
    band = smax(band, Z - HB, 2.0)
    band = menos(band, np.maximum(rad - RB + 8, EF - Z), 2.0)
    # círculo de invocação (relevo de 0,8 mm)
    desenho = np.minimum.reduce([np.abs(rad - 64) - 0.8, np.abs(rad - 54) - 0.6, np.abs(rad - 26) - 0.7])
    for k in range(18):                                     # runas entre os anéis
        a = k * 2 * np.pi / 18
        cu, sv = np.cos(a), np.sin(a)
        t = X * cu + Y * sv - 59
        s = -X * sv + Y * cu
        tr = np.maximum(np.abs(s) - 0.55, np.abs(t) - 3.2)
        tipo = k % 5
        if tipo == 0:
            tr = np.minimum(tr, np.maximum(np.abs(s - t * 0.8) - 0.55, np.abs(t - 1) - 2.2))
        elif tipo == 1:
            tr = np.minimum(tr, np.maximum(np.abs(t + 1.2) - 0.55, np.abs(s) - 2.4))
        elif tipo == 2:
            tr = np.minimum(tr, np.abs(np.sqrt((s - 1.8) ** 2 + (t - 1) ** 2) - 1.5) - 0.5)
        elif tipo == 3:
            tr = np.minimum(np.maximum(np.abs(s + t * 0.9) - 0.55, np.abs(t) - 3), np.maximum(np.abs(s - t * 0.9) - 0.55, np.abs(t) - 3))
        else:
            tr = np.minimum(tr, np.maximum(np.abs(t - 2.4) - 0.55, np.abs(s) - 2.4))
        desenho = np.minimum(desenho, tr)
    # estrela de 5 pontas aberta (linhas entre as velas) ligando o anel interno ao externo
    pts = [(54 * np.cos(np.pi / 2 + k * 2 * np.pi / 5), 54 * np.sin(np.pi / 2 + k * 2 * np.pi / 5)) for k in range(5)]
    for k in range(5):
        (x0, y0), (x1, y1) = pts[k], pts[(k + 2) % 5]
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        h = np.clip(((X - x0) * dx + (Y - y0) * dy) / L2, 0, 1)
        seg = np.sqrt((X - x0 - dx * h) ** 2 + (Y - y0 - dy * h) ** 2) - 0.6
        seg = np.maximum(seg, 26.5 - rad)                   # não entra no selo central
        desenho = np.minimum(desenho, seg)
    # selo central: triângulo de pontas abertas com um olho
    u, v = X, Y + 2
    tri = lambda r: np.maximum(-v - r * 0.5, v * 0.5 + np.abs(u) * 0.866 - r * 0.5)
    desenho = np.minimum(desenho, np.maximum(tri(20), -tri(17.6)))
    olho = np.maximum(np.sqrt(u ** 2 + (v + 7) ** 2) - 12, np.sqrt(u ** 2 + (v - 7) ** 2) - 12)   # lente do olho
    desenho = np.minimum(desenho, np.abs(olho) - 0.6)
    desenho = np.minimum(desenho, np.sqrt(u ** 2 + v ** 2) - 2.6)
    relevo = np.maximum(desenho, np.maximum(EF - Z, Z - EF - 0.8))
    # velas na borda e cera escorrendo para dentro
    velas = cera = None
    for k in range(5):
        a = np.pi / 2 + k * 2 * np.pi / 5
        cx, cy = (RB - 4) * np.cos(a), (RB - 4) * np.sin(a)
        h = HB + 8 + 4 * (k % 3)
        ve = np.maximum(np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) - 4.2, np.maximum(HB - 2 - Z, Z - h))
        ve = smax(ve, Z - h, 1.2)
        velas = ve if velas is None else np.minimum(velas, ve)
        c = np.maximum(np.abs(np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) - 3.6) - 1.4, np.abs(Z - h + 0.6) - 1.2)
        c = smin(c, capsula(g, (cx + 3.8 * np.cos(a + np.pi), cy + 3.8 * np.sin(a + np.pi), h - 1),
                            (cx + 9 * np.cos(a + np.pi), cy + 9 * np.sin(a + np.pi), HB - 3), 1.4, 1.9), 0.8)
        c = smin(c, capsula(g, (cx + 9 * np.cos(a + np.pi), cy + 9 * np.sin(a + np.pi), HB - 3),
                            (cx + 10.5 * np.cos(a + np.pi), cy + 10.5 * np.sin(a + np.pi), EF + 1), 1.8, 2.4), 0.8)
        cera = c if cera is None else np.minimum(cera, c)
    tudo = np.minimum.reduce([band, relevo, velas, cera])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c4": cera, "c3": velas, "c2": relevo}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "bandeja_ritual", IMP)).items():
        print(k, v)
