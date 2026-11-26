"""Prisão de Dados – cela de masmorra para "prender" o dado que rolou mal. Paredes de pedra talhada em blocos
irregulares, lascados e gastos, com ameias no alto; frente com grade de ferro rebitada em arco, dobradiças e cadeado;
tocha com pano enrolado e chama em labaredas na lateral; argola com corrente presa na parede de trás; piso de lajes;
uma caveira com dentes e mandíbula caída no canto. Aberta em cima: o dado entra por cima (cabe até 6 d20 de 22 mm).
70 × 58 × 59 mm. Cores: c1 pedra, c2 ferro, c3 caveira, c4 chama. Imprime em pé, sem suporte (tocha em balanço curto, 45°)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.13)
L, P, H, E = 70.0, 58.0, 52.0, 4.0
W, ZB, ZT = 17.0, 8.0, 36.0
MN, MX = (-48, -38, 0), (40, 37, 66)                       # vão da grade: meia largura, base, início do arco


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    lasca = desgaste(g, 1.0, 21)                                      # uma vez só: lascas da pedra
    # ---- pedra: caixa com blocos irregulares nas 4 faces
    fora = caixa(g, (0, 0, H / 2), (L / 2, P / 2, H / 2), 1.2)
    ladoX = np.abs(X) / (L / 2) > np.abs(Y) / (P / 2)
    u = np.where(ladoX, Y * np.sign(X) + 100 * np.sign(X), X * np.sign(-Y) + 300 * np.sign(Y))
    tex = tijolos(u, Z - 6.5, larg=11.0, alt=6.3, junta=0.6, prof=0.75, semente=7, irregular=0.35)
    perto = np.clip(1 - np.abs(fora) / 2.0, 0, 1)                     # só na casca
    na_parede = (Z > 6.5) & (Z < H)
    fora = fora + np.where(na_parede, tex, 0) * perto + lasca * 0.35 * perto + pele(g, 0.08)
    # ameias com pedra e lascas
    for i in range(-3, 4):
        for sy in (-1, 1):
            fora = np.minimum(fora, caixa(g, (i * 10, sy * (P / 2 - E / 2), H + 3.2), (3.3, E / 2 + 0.2, 3.6), 0.6) + lasca * 0.18)
    for j in (-1, 0, 1):
        for sx in (-1, 1):
            fora = np.minimum(fora, caixa(g, (sx * (L / 2 - E / 2), j * 18, H + 3.2), (E / 2 + 0.2, 3.3, 3.6), 0.6) + lasca * 0.18)
    # cornija sob as ameias e rodapé de lajes grandes
    fora = smin(fora, caixa(g, (0, 0, H - 1.2), (L / 2 + 1.0, P / 2 + 1.0, 1.2), 0.6) + lasca * 0.2, 0.5)
    rod = caixa(g, (0, 0, 3.2), (L / 2 + 1.8, P / 2 + 1.8, 3.2), 1.0)
    rod = rod + np.clip(1 - np.abs(rod) / 1.5, 0, 1) * tijolos(u * 0.6, Z + 0.0, larg=9, alt=6.4, junta=0.5, prof=0.5, semente=8)
    corpo = smin(fora, rod + lasca * 0.3, 0.6)
    # interior e piso de lajes
    corpo = menos(corpo, caixa(g, (0, 0, H / 2 + 3.2), (L / 2 - E, P / 2 - E, H / 2), 0.8))
    laje = tijolos(X, Y, larg=12, alt=10, junta=0.5, prof=0.5, semente=9, irregular=0.4)
    dentro = (np.abs(X) < L / 2 - E - 0.6) & (np.abs(Y) < P / 2 - E - 0.6)
    corpo = corpo + np.where(dentro, laje * np.clip(1 - np.abs(Z - 3.2) / 0.8, 0, 1), 0)
    # ---- vão em arco na frente
    vao = np.minimum(np.maximum(np.abs(X) - W, np.maximum(ZB - Z, Z - ZT)), np.maximum(np.sqrt(X ** 2 + (Z - ZT) ** 2) - W, ZT - Z))
    corpo = menos(corpo, np.maximum(vao, np.abs(Y + P / 2) - E - 1))
    # aduelas do arco (pedras em leque em volta do vão)
    ang = np.arctan2(Z - ZT, X)
    raio = np.sqrt(X ** 2 + (Z - ZT) ** 2)
    adu = np.maximum(np.maximum(raio - W - 4.5, W - raio), np.maximum(ZT - Z, np.abs(Y + P / 2 + 0.5) - 1.2))
    junta_ad = np.abs(np.mod(ang * 180 / np.pi + 9, 18) - 9) * raio * np.pi / 180 - 0.35
    adu = adu + 0.5 * np.clip(1 - junta_ad / 0.4, 0, 1)
    corpo = np.minimum(corpo, adu + lasca * 0.25)
    # ---- ferro: barras martelada, travessas rebitadas, moldura com cravos, dobradiças e cadeado
    martelo = 0.05 * ruido(g, 1.4, 70)
    barras = None
    for xx in np.arange(-13.5, 14, 4.5):
        topo = ZT + np.sqrt(max(W ** 2 - xx ** 2, 0)) + 1
        b = capsula(g, (xx, -P / 2 + E / 2, ZB - 1), (xx, -P / 2 + E / 2, topo), 1.05)
        barras = b if barras is None else np.minimum(barras, b)
    trav = None
    for zz in (17, 30):
        t = caixa(g, (0, -P / 2 + E / 2 - 0.3, zz), (W, 1.25, 1.1), 0.4)
        trav = t if trav is None else np.minimum(trav, t)
        trav = np.minimum(trav, rebites(g, [(xx, -P / 2 + E / 2 - 1.6, zz) for xx in np.arange(-13.5, 14, 4.5)], 0.75))
    barras = np.minimum(barras, trav)
    moldura = np.maximum(np.maximum(vao - 1.7, -vao + 0.2), np.abs(Y + P / 2 - 0.4) - 1.2)
    cravos = []
    for a in np.linspace(0.12, np.pi - 0.12, 9):
        cravos.append((np.cos(a) * (W + 0.85), -P / 2 - 0.9, ZT + np.sin(a) * (W + 0.85)))
    for zz in (11, 19, 27, 35):
        cravos += [(-W - 0.85, -P / 2 - 0.9, zz), (W + 0.85, -P / 2 - 0.9, zz)]
    moldura = np.minimum(moldura, rebites(g, cravos, 0.7))
    dobra = None
    for zz in (13, 30):
        d = np.minimum(caixa(g, (-W - 3.5, -P / 2 - 0.9, zz), (4.5, 0.6, 1.4), 0.4), cilindro(g, (-W - 0.6, -P / 2 - 1.2, zz - 2.2), 1.2, 4.4, 0.3))
        dobra = d if dobra is None else np.minimum(dobra, d)
    cad_c = (6.75, -P / 2 - 1.6, 21)
    cad = caixa(g, cad_c, (3.1, 1.5, 3.6), 1.2)
    cad = menos(cad, caixa(g, (6.75, -P / 2 - 3.2, 20.3), (0.5, 0.6, 1.3), 0.2))
    cad = np.minimum(cad, anel(g, (6.75, -P / 2 - 1.6, 25.2), 2.3, 0.65, "y"))
    ferro = np.minimum.reduce([np.maximum(barras, vao - 0.6) + martelo, moldura + martelo, dobra, cad])
    # argola com corrente na parede de trás (por dentro)
    elos = [anel(g, (-14, P / 2 - E - 1.0, 40), 2.4, 0.6, "y")]
    for k in range(5):
        zz = 36.5 - k * 3.6
        elos.append(anel(g, (-14 + 0.4 * k, P / 2 - E - 1.6, zz), 1.6, 0.5, "x" if k % 2 == 0 else "y"))
    ferro = np.minimum(ferro, np.minimum.reduce(elos))
    ferro = np.minimum(ferro, caixa(g, (-14, P / 2 - E - 0.4, 42.6), (1.6, 0.6, 1.6), 0.3))
    # ---- tocha
    tx, ty = -L / 2 - 1, -8
    sup = np.minimum.reduce([caixa(g, (tx, ty, 32), (1.0, 3.6, 6.5), 0.5),
                             capsula(g, (tx, ty, 29.5), (tx - 5.5, ty, 33.5), 1.15),
                             anel(g, (tx - 6.4, ty, 34.2), 2.6, 0.75, "z"),
                             rebites(g, [(tx - 1.1, ty, 27.3), (tx - 1.1, ty, 36.7)], 0.8)])
    cabo = capsula(g, (tx - 5, ty, 26), (tx - 8.2, ty, 41), 1.7, 2.4) + 0.15 * np.sin(Z * 4.0)
    pano = capsula(g, (tx - 7.5, ty, 38), (tx - 8.6, ty, 43.4), 3.1, 3.6)
    pano = pano + 0.35 * np.abs(np.sin((Z - 38) * 2.2 + np.arctan2(Y - ty, X - tx + 8) * 1.0))
    ch = Vista(g, (tx - 8.8, ty, 44), rot_y(-10))
    chama = elipsoide(ch, (tx - 8.8, ty, 46.8), (3.7, 3.7, 4.0))
    for (dx, dy, h, r, s) in [(0, 0, 11, 2.6, 0), (2.4, 1.8, 7.5, 1.6, 1), (-2.6, 1.2, 8.5, 1.7, 2), (0.9, -2.6, 7.0, 1.5, 3), (-1.4, -2.0, 9.5, 1.4, 4)]:
        tor = 0.9 * np.sin(s * 1.7)
        lab = tubo(ch, [(tx - 8.8 + dx * 0.5, ty + dy * 0.5, 47), (tx - 8.8 + dx + tor, ty + dy, 47 + h * 0.6), (tx - 8.8 + dx * 0.6 - tor, ty + dy * 0.6, 47 + h)], [r, r * 0.6, 0.25])
        chama = smin(chama, lab, 1.1)
    chama = chama + 0.08 * ruido(g, 1.5, 81)
    # ---- caveira com dentes e mandíbula caída
    cx, cy, cz = 15, 13, 4 + 6.2
    cv = Vista(g, (cx, cy, cz), rot_z(-25))
    cranio = smin(esfera(cv, (cx, cy + 0.6, cz + 1.2), 6.4), elipsoide(cv, (cx, cy - 3.2, cz - 2.2), (4.6, 3.4, 3.0)), 2.2)
    cranio = smin(cranio, np.minimum(esfera(cv, (cx - 4.6, cy - 2.0, cz - 1.2), 2.0), esfera(cv, (cx + 4.6, cy - 2.0, cz - 1.2), 2.0)), 1.2)   # maçãs
    nariz = np.maximum(poligono2d(cv.x - cx, cv.z - (cz - 2.4), [(-1.0, 0.8), (1.0, 0.8), (0, -1.2)]), np.abs(cv.y - cy + 6.0) - 1.6)
    furos = np.minimum.reduce([elipsoide(cv, (cx - 2.5, cy - 5.6, cz + 0.2), (1.9, 1.6, 2.1)),
                               elipsoide(cv, (cx + 2.5, cy - 5.6, cz + 0.2), (1.9, 1.6, 2.1)), nariz])
    cranio = menos(cranio, furos, 0.35)
    dentes = None
    for k in range(-3, 4):
        d = caixa(cv, (cx + k * 0.95, cy - 5.6, cz - 4.6), (0.38, 0.5, 0.75), 0.25)
        dentes = d if dentes is None else np.minimum(dentes, d)
    cranio = np.minimum(menos(cranio, caixa(cv, (cx, cy - 6.0, cz - 4.6), (3.6, 1.2, 0.85), 0.3)), dentes)
    mand = np.maximum(np.abs(np.sqrt((cv.x - cx) ** 2 + ((cv.y - cy + 1.5) * 1.2) ** 2) - 4.2) - 0.8, np.abs(cv.z - 4.9) - 0.9)
    mand = np.maximum(mand, cv.y - cy + 0.5)            # só a metade da frente (ferradura)
    cranio = np.minimum(cranio, mand)
    cranio = np.maximum(cranio, 4 - Z) + pele(g, 0.06, 90)
    # ---- junta tudo
    tudo = np.minimum.reduce([corpo, ferro, cabo, pano, sup, chama, cranio])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c4": chama, "c3": cranio, "c2": np.minimum(ferro, sup)}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "prisao", IMP)).items():
        print(k, v)
