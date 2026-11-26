"""Dragãozinho do Crítico – filhote de dragão sentado em cima de um d20 gigante, abraçando o dado como tesouro.
Chifrinhos, asinhas abertas, barriga listrada e rabo enrolado em volta do dado. Cerca de 60 mm.
Cores: c1 dragão, c2 d20 e pupilas, c3 barriga, chifres e olhos, c4 membrana das asas. Em pé, suporte em árvore só sob as asas."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.12)
MN, MX = (-34, -30, 0), (34, 32, 66)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    # d20 apoiado numa face (rot alinha uma face para baixo)
    R0 = np.array(mul(rot_x(-20.9), rot_z(0)))
    n0 = np.array([0, 1 / PHI, PHI]); n0 = n0 / np.linalg.norm(n0)   # normal de uma face
    alvo = np.array([0, 0, 1.0]); ax = np.cross(n0, alvo); sa = np.linalg.norm(ax); ca = n0 @ alvo
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]]) / sa
    RF = np.eye(3) + sa * K + (1 - ca) * K @ K       # leva essa face para cima (e a oposta para a mesa)
    dado = d20(g, (0, 2, 15.2), 15.2, 1.2, rot=RF)
    dado = menos(dado, numeros_d20(g, (0, 2, 15.2), 15.2, RF, altura=5.6, prof=0.7), 0.15)
    dado = np.maximum(dado, -Z)
    # número 20 em baixo relevo na face da frente (aproximação: dois traços estilizados)
    corpo = elipsoide(g, (0, 0, 39), (9.5, 8.5, 10.5))
    cab = elipsoide(g, (0, -3, 54), (9.5, 8.5, 7.8))
    foc = elipsoide(g, (0, -10.5, 51.5), (5.6, 5, 4.2))
    cab = smin(cab, foc, 3)
    dr = smin(corpo, cab, 4)
    # patas abraçando o dado
    for sx in (-1, 1):
        dr = smin(dr, capsula(g, (sx * 7, -4, 40), (sx * 9, -11, 32), 3.0, 2.6), 2)
        dr = smin(dr, capsula(g, (sx * 7, 2, 31), (sx * 10, -6, 28), 3.6, 3.0), 2)
    # rabo enrolado em volta do dado
    pts = [(0, 8, 32), (10, 12, 27), (17, 6, 22), (17, -6, 18), (9, -15, 15)]
    dr = smin(dr, tubo(g, pts, [4.2, 3.6, 3.0, 2.4, 1.6]), 2)
    ponta = elipsoide(Vista(g, (6, -18, 14.5), rot_z(-40)), (6, -18, 14.5), (3.4, 1.2, 2.6))
    dr = smin(dr, ponta, 1)
    # espinhos nas costas
    for i, (y, z) in enumerate([(6.5, 60), (8.5, 52), (9.4, 44), (9.0, 36)]):
        dr = smin(dr, capsula(g, (0, y - 1.5, z), (0, y + 2.8, z + 1.2), 1.8, 0.4), 0.8)
    # chifres e orelhinhas
    claro = None
    for sx in (-1, 1):
        ch = tubo(g, [(sx * 4.5, -1, 60), (sx * 6.5, 2, 64.5), (sx * 7, 5.5, 65.5)], [1.9, 1.2, 0.5])
        claro = ch if claro is None else np.minimum(claro, ch)
        dr = smin(dr, elipsoide(Vista(g, (sx * 9, 0, 57), rot_y(sx * 40)), (sx * 9, 0, 57), (1.4, 2.6, 4)), 1)
    # barriga listrada
    barriga = elipsoide(g, (0, -6.2, 38), (6.2, 3.2, 8.5))
    barriga = np.maximum(barriga, -(dr + 0.0) - 2.2)
    listras = np.abs(np.mod(Z - 30, 3.2) - 1.6) - 0.35
    barriga = menos(barriga, np.maximum(listras, -(barriga + 0.6)), 0.2)
    claro = np.minimum(claro, barriga)
    # olhos e narinas
    olhos, pupilas = None, None
    for sx in (-1, 1):
        o = esfera(g, (sx * 4.3, -9.5, 55.5), 2.8)
        p = esfera(g, (sx * 4.0, -11.6, 55.4), 1.6)
        olhos = o if olhos is None else np.minimum(olhos, o)
        pupilas = p if pupilas is None else np.minimum(pupilas, p)
        dr = menos(dr, esfera(g, (sx * 1.8, -15.4, 52.5), 0.7), 0.2)
    dr = menos(dr, np.maximum(np.abs(X) - 3.4, np.maximum(np.abs(Z - 49.6) - 0.35, np.abs(Y + 14.8) - 1.5)), 0.3)  # sorriso
    claro = np.minimum(claro, menos(olhos, pupilas))
    # asas abertas (osso + membrana)
    membrana = None
    for sx in (-1, 1):
        v = Vista(g, (sx * 7, 7, 46), mul(rot_z(sx * -25), rot_y(sx * -18)))
        osso = tubo(v, [(sx * 7, 10.5, 46), (sx * 14, 10.5, 57.5), (sx * 25, 10.5, 52)], [1.8, 1.4, 0.8])
        mem = np.maximum(np.abs(v.y - 10.5) - 0.9, np.maximum(np.sqrt((v.x - sx * 16) ** 2 + (v.z - 48) ** 2) - 10.5,
                                                              -(np.sqrt((v.x - sx * 20) ** 2 + (v.z - 38) ** 2) - 8)))
        mem = np.maximum(mem, -(sx * (v.x - sx * 7)))
        dr = smin(dr, osso, 1)
        membrana = mem if membrana is None else np.minimum(membrana, mem)
    # escamas no dragão (menos na barriga), garrinhas, dentinhos, brilho nos olhos, veias nas asas
    perto = np.clip(1 - np.abs(dr) / 1.2, 0, 1)
    ang = np.arctan2(X, -(Y - 0.5))
    dr = dr + perto * escamas(ang * 9.5, Z, r=1.05, prof=0.3) * np.clip((np.abs(ang) - 0.55) / 0.3, 0, 1)
    dr = dr + pele(g, 0.05, 41)
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            claro = np.minimum(claro, capsula(g, (sx * (9 + k * 1.3), -12.6, 31.4), (sx * (9.2 + k * 1.5), -14.0, 29.6), 0.55, 0.15))
            claro = np.minimum(claro, capsula(g, (sx * (10 + k * 1.4), -7.4, 27.0), (sx * (10.3 + k * 1.6), -9.2, 25.6), 0.6, 0.15))
        claro = np.minimum(claro, capsula(g, (sx * 2.4, -14.8, 49.7), (sx * 2.6, -15.2, 48.4), 0.45, 0.1))     # dentinhos
        pupilas = menos(pupilas, esfera(g, (sx * 4.8, -12.6, 56.4), 0.5))
        v = Vista(g, (sx * 7, 7, 46), mul(rot_z(sx * -25), rot_y(sx * -18)))
        for (px, pz) in [(18, 44), (21, 48), (12, 41)]:
            membrana = np.minimum(membrana, np.maximum(capsula(v, (sx * 14, 10.5, 57), (sx * px, 10.5, pz), 0.7, 0.3), membrana - 0.6))
    escuro = np.minimum(dado, np.maximum(pupilas, olhos))
    tudo = np.minimum.reduce([dado, dr, claro, membrana])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c3": claro, "c2": escuro, "c4": membrana}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "dragaozinho", IMP)).items():
        print(k, v)
