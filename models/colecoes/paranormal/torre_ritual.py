"""Torre da Ordo Realitas – torre de dados em forma de obelisco de pedra negra com Marcas de Sangue gravadas, correntes atravessadas,
um olho entalhado no alto e quatro velas derretidas nos cantos do topo. O dado entra pela boca no topo, desce
por três rampas e sai pelo portal em arco para a bandeja embutida na frente, com um círculo de ritual no fundo.
Uma peça só: 120 × 150 × 170 mm (cabe na mesa da A1). Dado máximo: d20 de 26 mm.
Cores: c1 pedra, c2 runas, olho e correntes, c3 velas, c4 cera e chamas. Em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.2)
A, AI, HT = 32.0, 27.0, 150.0           # meia largura externa na base, canal (meia largura), altura do corpo
MN, MX = (-62, -96, 0), (62, 40, 186)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    rr = ruido(g, 2.0, 91)
    afina = 1 - 0.18 * np.clip(Z / HT, 0, 1)        # obelisco afina para cima
    corpo = np.maximum(np.maximum(np.abs(X), np.abs(Y)) - A * afina, np.maximum(-Z, Z - HT)) + rr * 0.3
    corpo = smin(corpo, np.maximum(np.maximum(np.abs(X), np.abs(Y)) - A - 4, np.maximum(-Z, Z - 10)), 1.5)    # degrau da base
    corpo = smin(corpo, np.maximum(np.maximum(np.abs(X), np.abs(Y)) - A * 0.82 - 3, np.abs(Z - HT + 2) - 3), 1.0)   # cornija
    # canal interno e rampas
    canal = np.maximum(np.maximum(np.abs(X), np.abs(Y)) - AI * afina, -1 - Z)
    corpo = menos(corpo, canal)
    for (z0, s) in [(128, 1), (100, -1), (72, 1)]:
        plano = np.abs((Z - z0) - 1.19 * s * Y) - 1.6
        corpo = np.minimum(corpo, np.maximum(plano, np.maximum(np.maximum(np.abs(X), np.abs(Y)) - AI * afina - 0.5, -s * Y - 9)))
    corpo = np.minimum(corpo, np.maximum((Z - 2) - 0.55 * (Y + AI), np.maximum(np.maximum(np.abs(X), np.abs(Y)) - AI - 0.5, -Z)))
    # portal na frente (y negativo)
    W, ZT = 19.0, 26.0
    arco = np.minimum(np.maximum(np.abs(X) - W, np.maximum(-1 - Z, Z - ZT)), np.maximum(np.sqrt(X ** 2 + (Z - ZT) ** 2) - W, ZT - Z))
    corpo = menos(corpo, np.maximum(arco, Y + 10))
    # bandeja embutida na frente
    band = np.maximum(caixa(g, (0, -62, 7), (56, 32, 7), 6), -Z)
    band = menos(band, caixa(g, (0, -62, 10), (51, 27, 8), 4))
    band = menos(band, np.maximum(arco, np.maximum(Y + 40, -Y - 24)))   # passagem do dado na parede de trás
    bx, by = X, Y + 62
    rb = np.sqrt(bx ** 2 + by ** 2)
    circ = np.maximum(np.minimum(np.abs(rb - 20) - 0.7, np.abs(rb - 15) - 0.5), np.abs(Z - 2.4) - 0.6)
    for k in range(8):
        a = k * np.pi / 4
        circ = np.minimum(circ, np.maximum(np.maximum(np.abs(-bx * np.sin(a) + by * np.cos(a)) - 0.5, np.abs(bx * np.cos(a) + by * np.sin(a) - 17.5) - 2), np.abs(Z - 2.4) - 0.6))
    corpo = np.minimum(corpo, band)
    perto = np.clip(1 - np.abs(corpo) / 1.5, 0, 1)
    corpo = corpo + perto * desgaste(g, 0.3, 92) * np.where(Z > 12, 1.0, 0.4)      # lascas na pedra (bem leves na bandeja)
    # runas gravadas nas 4 faces (colunas de traços) e olho no alto da frente
    runas = None
    for face in range(4):
        a = face * np.pi / 2
        n_x, n_y = -np.sin(a), -np.cos(a)            # normal da face (frente = −y)
        u = X * np.cos(a) - Y * np.sin(a)
        prof = (X * n_x + Y * n_y) - A * afina
        for i, zz in enumerate(range(48, 120, 12)):
            tr = sigilo_sangue(u, -(Z - zz), 9.0, 1.4) if (i + face) % 2 == 0 else np.minimum(np.sqrt(u ** 2 + (Z - zz) ** 2) - 1.4, np.abs(np.sqrt(u ** 2 + (Z - zz) ** 2) - 3.4) - 0.5)
            tr = np.maximum(tr, np.abs(prof + 0.3) - 0.9)
            if face == 0 and zz < 60:
                continue
            runas = tr if runas is None else np.minimum(runas, tr)
    olho_l = np.maximum(np.sqrt(X ** 2 + (Z - 134 + 6) ** 2) - 10, np.sqrt(X ** 2 + (Z - 134 - 6) ** 2) - 10)
    prof0 = -Y - A * (1 - 0.18 * 134 / HT)
    olho = np.maximum(np.minimum(np.abs(olho_l) - 0.7, np.sqrt(X ** 2 + (Z - 134) ** 2) - 2.6), np.abs(prof0 + 0.3) - 0.9)
    runas = np.minimum(runas, olho)
    # correntes atravessadas na frente (elos)
    elos = None
    for i in range(9):
        t = i / 8
        cx, cz = -A + 2 * A * t, 62 + 34 * t
        ang = np.degrees(np.arctan2(34, 2 * A))
        v = Vista(g, (cx, -A * (1 - 0.18 * cz / HT) - 2.2, cz), mul(rot_y(-ang), rot_x(90 if i % 2 else 0)))
        e = toro(v, (cx, -A * (1 - 0.18 * cz / HT) - 2.2, cz), 3.4, 1.1, 1.0)
        elos = e if elos is None else np.minimum(elos, e)
    # velas nos cantos do topo
    velas = cera = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy, h = sx * (A * 0.82 - 3), sy * (A * 0.82 - 3), 14 + 4 * ((sx + sy * 2) % 3)
            ve = np.maximum(np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) - 3.6, np.maximum(HT - 1 - Z, Z - HT - h))
            velas = ve if velas is None else np.minimum(velas, ve)
            c = np.maximum(np.abs(np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) - 3.4) - 1.2, np.abs(Z - HT - h + 0.5) - 1.0)
            c = smin(c, capsula(g, (cx + 3.4 * sx, cy, HT + h - 1), (cx + 3.6 * sx, cy, HT + 2), 1.0, 1.5), 0.6)
            c = np.minimum(c, smin(elipsoide(g, (cx, cy, HT + h + 2.6), (1.6, 1.6, 2.6)), capsula(g, (cx, cy, HT + h + 3), (cx, cy, HT + h + 6.5), 1.0, 0.2), 0.5))
            cera = c if cera is None else np.minimum(cera, c)
    escuro = np.minimum.reduce([runas, circ, elos])
    tudo = np.minimum.reduce([corpo, escuro, velas, cera])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c4": cera, "c3": velas, "c2": escuro}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "torre_ritual", IMP)).items():
        print(k, v)
