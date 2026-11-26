"""Porta-copos Brasão – 4 porta-copos redondos (Ø 92 mm) com borda de corda e um brasão em relevo cada:
d20, coroa, torre e espadas cruzadas. Guardados de pé num suporte em forma de muralha com ameias.
Cores: c1 porta-copo e muralha, c2 brasão (só nas últimas camadas), c3 borda de corda.
Impressão (--imprimir): porta-copos deitados, um por arquivo de cor; muralha em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.15)
RC, HC = 46.0, 5.0


def brasao(u, v, tipo):
    """campo 2D (u, v em mm, centro 0) do desenho de cada brasão."""
    if tipo == "d20":
        a = np.arctan2(v, u); sec = np.round(a / (np.pi / 3)) * (np.pi / 3)
        hexa = u * np.cos(sec) + v * np.sin(sec) - 20
        tri = np.maximum(-v - 6.5, v * 0.5 + np.abs(u) * 0.866 - 8)
        return menos(hexa, np.maximum(-tri - 1.8, tri))
    if tipo == "coroa":
        faixa = np.maximum(np.abs(u) - 20, np.abs(v + 10) - 4)
        pontas = np.maximum(np.abs(u) - 20, np.maximum(-(v + 6), v - 14 + 2.4 * np.abs(np.mod(u + 20, 10) - 5)))
        bolas = None
        for x in (-20, -10, 0, 10, 20):
            b = np.sqrt((u - x) ** 2 + (v - 15) ** 2) - 3
            bolas = b if bolas is None else np.minimum(bolas, b)
        return np.minimum(np.minimum(faixa, pontas), bolas)
    if tipo == "torre":
        corpo = np.maximum(np.abs(u) - 11, np.abs(v + 4) - 18)
        topo = np.maximum(np.abs(u) - 15, np.abs(v - 15) - 4)
        ameias = np.maximum(np.maximum(np.abs(u) - 15, np.abs(v - 21) - 3), 1.8 - np.abs(np.mod(u + 15, 10) - 5))
        porta = np.minimum(np.maximum(np.abs(u) - 5, np.abs(v + 15) - 7), np.sqrt(u ** 2 + (v + 8) ** 2) - 5)
        return menos(np.minimum.reduce([corpo, topo, ameias]), porta)
    # espadas cruzadas
    d = None
    for s in (-1, 1):
        c, sn = float(np.cos(np.radians(s * 40))), float(np.sin(np.radians(s * 40)))
        x, y = c * u + sn * v, -sn * u + c * v
        lam = np.maximum(np.abs(x) - 2.6, np.abs(y - 4) - 20)
        ponta = np.maximum(np.abs(x) - 2.6 * np.clip((30 - y) / 6, 0, 1), np.maximum(y - 30, 24 - y))
        guarda = np.maximum(np.abs(x) - 9, np.abs(y + 17) - 1.8)
        cabo = np.maximum(np.abs(x) - 2, np.abs(y + 23) - 5)
        pomo = np.sqrt(x ** 2 + (y + 29.5) ** 2) - 3.2
        e = np.minimum.reduce([lam, ponta, guarda, cabo, pomo])
        d = e if d is None else np.minimum(d, e)
    return d


def porta_copo(g, c, tipo, rot=None):
    gv = Vista(g, c, rot) if rot is not None else g
    x, y, z = gv.x - c[0], gv.y - c[1], gv.z - c[2]
    rad = np.sqrt(x ** 2 + y ** 2)
    corpo = np.maximum(rad - RC + 3.5, np.maximum(-z, z - HC))
    # corda: toro torcido na borda
    ang = np.arctan2(y, x)
    tor = np.sqrt((rad - RC + 3) ** 2 + (z - HC / 2) ** 2) - 3.0 + 0.6 * np.cos(ang * 46 + (z - HC / 2) * 1.3)
    corda = np.maximum(tor, np.maximum(-z, z - HC - 0.6))
    # fundo rebaixado e brasão em relevo
    corpo = menos(corpo, np.maximum(rad - RC + 9, HC - 1.2 - z), 0.6)
    corpo = corpo + 0.08 * ruido(gv, 0.6, 3)                                         # couro batido no fundo
    anel_ = np.maximum(np.abs(rad - RC + 11.5) - 0.45, np.maximum(HC - 1.4 - z, z - HC + 0.6))   # filete com pontinhos
    for a in np.linspace(0, 2 * np.pi, 37)[:-1]:
        anel_ = np.minimum(anel_, np.sqrt((x - (RC - 13.8) * np.cos(a)) ** 2 + (y - (RC - 13.8) * np.sin(a)) ** 2 + (z - HC + 1.2) ** 2) - 0.7)
    d2 = brasao(x, y, tipo)
    br = np.maximum(d2, np.maximum(HC - 1.4 - z, z - HC + 0.3 * np.clip(1 + d2, 0, 1)))   # relevo com bisel nas bordas
    br = np.minimum(br, anel_)
    return np.minimum.reduce([corpo, corda, br]), br, corda


TIPOS = ["d20", "coroa", "torre", "espadas"]
MN, MX = ((-50, -50, 0), (400, 50, 8)) if IMP else ((-62, -110, 0), (62, 40, 108))


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    tudo = br = corda = None
    if IMP:
        for i, t in enumerate(TIPOS):
            a, b, c = porta_copo(g, (i * 100, 0, 0), t)
            tudo = a if tudo is None else np.minimum(tudo, a)
            br = b if br is None else np.minimum(br, b)
            corda = c if corda is None else np.minimum(corda, c)
        return np.maximum(tudo, -Z), {"c2": br, "c3": corda}
    # muralha: caixa de pedra aberta em cima com ameias, 4 porta-copos de pé dentro
    mur = caixa(g, (0, 0, 26), (52, 15, 26), 2.0)
    u = np.where(np.abs(X) / 52 > np.abs(Y) / 15, Y * np.sign(X) + 200, X)
    mur = mur + np.clip(1 - np.abs(mur) / 1.5, 0, 1) * (tijolos(u, Z, larg=10, alt=6, junta=0.5, prof=0.6, semente=4) * (Z < 51) + desgaste(g, 0.3, 5))
    for i in range(-5, 6):
        for sy in (-1, 1):
            mur = np.minimum(mur, caixa(g, (i * 9.4, sy * 13, 55), (2.8, 2.0, 3.2), 0.6) + desgaste(g, 0.2, 6))
    mur = menos(mur, caixa(g, (0, 0, 32), (49, 12, 28), 1.0))
    tudo = mur
    for i, t in enumerate(TIPOS[1:]):
        a, b, c = porta_copo(g, (0, -6 + i * 6, 47), t, rot_x(90))
        tudo = np.minimum(tudo, a)
        br = b if br is None else np.minimum(br, b)
        corda = c if corda is None else np.minimum(corda, c)
    a, b, c = porta_copo(g, (0, -64, 0), "d20")
    tudo = np.minimum(tudo, a)
    return np.maximum(tudo, -Z), {"c2": np.minimum(br, b), "c3": np.minimum(corda, c)}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "porta_copos", IMP)).items():
        print(k, v)
