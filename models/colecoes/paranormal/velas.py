"""Velas de Ritual – trio de velas derretidas (porta-velas de LED tipo réchaud, Ø 38 mm) num prato com círculo
de runas gravado. Cada vela tem um encaixe de 39,5 × 16 mm no topo para a velinha de LED; a cera vermelha escorre
por cima da branca. Prato Ø 116 mm; velas de 42, 58 e 74 mm.
Cores: c1 prato, c2 runas (incrustadas), c3 velas, c4 cera escorrida (c5: chama da velinha de LED, só na foto). Em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.15)
MN, MX = (-60, -60, 0), (60, 60, 88)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    rad = np.sqrt(X ** 2 + Y ** 2)
    ang = np.arctan2(Y, X)
    # prato com borda alta
    prato = np.maximum(rad - 58, np.maximum(-Z, Z - 7))
    prato = smax(prato, Z - 7, 1.5)
    prato = menos(prato, np.maximum(rad - 52, 3.4 - Z), 1.0)
    # círculo de runas no fundo: dois anéis e traços (runas inventadas) entre eles
    aneis = np.minimum(np.abs(rad - 46) - 0.6, np.abs(rad - 36) - 0.6)
    runas = None
    for k in range(14):
        a = k * 2 * np.pi / 14
        cu, sv = np.cos(a), np.sin(a)
        # coordenadas locais: t radial, s tangencial
        t = X * cu + Y * sv - 41
        s = -X * sv + Y * cu
        tr = sigilo_sangue(s, t, 7.0, 1.0) if k % 2 == 0 else np.sqrt(s ** 2 + t ** 2) - 1.0     # Marcas de Sangue e pontos
        runas = tr if runas is None else np.minimum(runas, tr)
    desenho = np.minimum(aneis, runas)
    inlay = np.maximum(desenho, np.abs(Z - 3.4) - 0.6)
    prato = menos(prato, inlay)
    # velas
    velas = cera = chamas = None
    for (x, y, h, r, sem) in [(-14, 10, 74, 22, 1), (20, 14, 58, 21, 2), (2, -22, 42, 21.5, 3)]:
        rr = ruido(g, 1.6, sem)
        v = np.maximum(np.sqrt((X - x) ** 2 + (Y - y) ** 2) - r - 0.6 * np.sin(np.arctan2(Y - y, X - x) * 5 + sem), np.maximum(3.0 - Z, Z - h)) + rr * 0.25
        topo = h - 2.2 + 2.2 * np.sin(np.arctan2(Y - y, X - x) * 3 + sem)
        v = smax(v, Z - topo, 2.5)
        # borda derretida irregular no topo
        v = menos(v, np.maximum(np.sqrt((X - x) ** 2 + (Y - y) ** 2) - 19.75, h - 16 - Z))      # encaixe da vela de LED
        velas = v if velas is None else np.minimum(velas, v)
        # cera vermelha escorrendo: poça no topo da borda + filetes
        c = np.maximum(np.abs(np.sqrt((X - x) ** 2 + (Y - y) ** 2) - r + 0.9) - 2.2, np.abs(Z - h + 0.8) - 1.6)
        for k in range(6):
            a = k * 1.05 + sem
            comp = 10 + 14 * ((k * 7 + sem * 3) % 5) / 4
            p0 = (x + (r + 0.3) * np.cos(a), y + (r + 0.3) * np.sin(a), h - 1.5)
            c = smin(c, capsula(g, p0, (p0[0] + 0.6 * np.cos(a), p0[1] + 0.6 * np.sin(a), h - comp), 1.6, 2.3), 0.8)
        c = c + 0.06 * ruido(g, 0.6, 50 + sem)
        cera = c if cera is None else np.minimum(cera, c)
        if not IMP:   # só na foto: a velinha de LED no encaixe, com a chama
            led = np.maximum(cilindro(g, (x, y, h - 16), 19.0, 15.0, 1.0), -cilindro(g, (x, y, h - 2), 15, 4, 0.5))
            ch = smin(elipsoide(g, (x, y, h + 2.5), (3.2, 3.2, 5)), capsula(g, (x, y, h + 4), (x, y, h + 11), 2.0, 0.3), 1.2)
            velas = np.minimum(velas, led)
            chamas = ch if chamas is None else np.minimum(chamas, ch)
    # poça de cera no prato
    cera = smin(cera, np.maximum(elipsoide(g, (-2, 2, 3.4), (24, 18, 1.6)), 3.4 - Z), 1)
    tudo = np.minimum.reduce([prato, inlay, velas, cera] + ([chamas] if chamas is not None else []))
    tudo = np.maximum(tudo, -Z)
    return tudo, {**({"c5": chamas} if chamas is not None else {}), "c4": cera, "c2": inlay, "c3": velas}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "velas", IMP)).items():
        print(k, v)
